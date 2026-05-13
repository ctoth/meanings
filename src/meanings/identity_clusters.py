"""Identity-cluster (IC) merge procedure for spelling variants.

This module replaces the old hand-coded 7-pair whitelist with a real merge
*procedure* over the OEWN lemma set:

1. **Candidate detection** -- a battery of standard English orthographic-variant
   transformations (``-or``/``-our``, ``-er``/``-re``, ``-ize``/``-ise``,
   ``-yze``/``-yse``, ``-og``/``-ogue``, doubled-consonant ``-ll-``/``-l-``,
   dropped-``e``, ``ae``/``e`` and ``oe``/``e``, ``-ce``/``-se``,
   ``-mme``/``-m``, plus assorted lexical pairs and a generic small
   edit-distance pass) over the lexicon lemma set. Both members of a candidate
   pair must be present in the lexicon.

2. **Gloss-similarity gate** -- a candidate pair ``(f1, f2)`` is only merged
   when some sense of ``f1`` and some sense of ``f2`` of the same POS have
   glosses whose token-Jaccard similarity clears a threshold. This rejects
   look-alikes (``defer``/``differ``, ``colon``/``colour``) that an
   edit-distance pass would otherwise flag.

3. **The merge** -- per merge we emit a :class:`MergeRecord` (contributing
   forms, merged sense ids, the orthographic rule that fired, the gloss
   similarity score, provenance). ICs are built from these records: each IC is a
   set of forms + their merged senses + the merge records that built it +
   aliases. **Every form is kept** -- this is merge, not canonicalization.

The runtime interface ``identity_cluster_for_form(form)`` used by
``wordnet_pipeline`` is preserved; it returns an :class:`IdentityClusterMerge`
view (``ic_id`` + ``forms`` + ``rationale`` + ``evidence``) for any form that
participates in a merge, else ``None``.

The IC table is computed by :func:`build_identity_clusters` over a ``wn``
lexicon. A precomputed table is shipped at ``reports/ic-merge-method.json`` and
loaded lazily so that the per-sense ``identity_cluster_for_form`` lookups in the
pipeline stay O(1) and do not re-iterate the lexicon. Pass ``rebuild=True`` (or
delete the JSON) to recompute from the live lexicon.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from meanings.normalize import basic_tokens, normalize_lemma

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IC_TABLE_JSON = _REPO_ROOT / "reports" / "ic-merge-method.json"

# Tokens that carry no discriminative weight inside a short dictionary gloss; a
# generous list so that the Jaccard gate compares *content*.
_GLOSS_STOP = frozenset(
    {
        "a",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "being",
        "by",
        "for",
        "from",
        "had",
        "has",
        "have",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "other",
        "that",
        "the",
        "their",
        "this",
        "to",
        "used",
        "use",
        "using",
        "was",
        "which",
        "with",
        "without",
        "you",
        "your",
        "especially",
        "typically",
        "usually",
        "often",
        "sometimes",
        "etc",
    }
)


# ---------------------------------------------------------------------------
# Edit distance (hand-rolled; no deps)
# ---------------------------------------------------------------------------


def levenshtein(a: str, b: str, *, cap: int | None = None) -> int:
    """Levenshtein edit distance. ``cap`` stops early once the distance exceeds it."""

    if a == b:
        return 0
    if cap is not None and abs(len(a) - len(b)) > cap:
        return cap + 1
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        best = i
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            val = min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + cost,
            )
            current.append(val)
            if val < best:
                best = val
        previous = current
        if cap is not None and best > cap:
            return cap + 1
    return previous[-1]


# ---------------------------------------------------------------------------
# Orthographic-variant rules
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrthographicRule:
    """A reversible orthographic-variant transformation.

    ``apply`` takes a normalized lemma and yields the lemma(s) obtained by
    flipping the orthographic feature this rule encodes (e.g. ``color`` ->
    ``colour``). It may return zero, one, or several candidates.
    """

    rule_id: str
    description: str
    apply: object  # Callable[[str], Iterable[str]]

    def variants(self, lemma: str) -> set[str]:
        out: set[str] = set()
        for cand in self.apply(lemma):  # type: ignore[operator]
            cand = cand.strip()
            if cand and cand != lemma:
                out.add(cand)
        return out


def _suffix_swap(suffixes: Sequence[tuple[str, str]]):
    """Build an apply-fn that swaps any of ``(left, right)`` suffix pairs both ways."""

    def fn(lemma: str) -> Iterable[str]:
        for left, right in suffixes:
            if left and lemma.endswith(left) and len(lemma) > len(left):
                yield lemma[: -len(left)] + right
            if right and lemma.endswith(right) and len(lemma) > len(right):
                yield lemma[: -len(right)] + left

    return fn


def _infix_swap(pairs: Sequence[tuple[str, str]]):
    """Apply-fn that swaps an internal substring both ways at every occurrence."""

    def fn(lemma: str) -> Iterable[str]:
        for a, b in pairs:
            start = 0
            while (idx := lemma.find(a, start)) != -1:
                yield lemma[:idx] + b + lemma[idx + len(a) :]
                start = idx + 1
            start = 0
            while (idx := lemma.find(b, start)) != -1:
                yield lemma[:idx] + a + lemma[idx + len(b) :]
                start = idx + 1

    return fn


_DOUBLE_C = "bcdfghklmnprstvz"


def _doubled_consonant_before_suffix(lemma: str) -> Iterable[str]:
    # traveled <-> travelled, modeling <-> modelling, focused <-> focussed
    for m in re.finditer(r"([bcdfghklmnprstvz])\1", lemma):
        i = m.start()
        yield lemma[:i] + lemma[i + 1 :]
    for suf in ("ing", "ed", "er", "or", "y"):
        if lemma.endswith(suf) and len(lemma) > len(suf):
            stem = lemma[: -len(suf)]
            if stem and stem[-1] in _DOUBLE_C and (len(stem) < 2 or stem[-2] in "aeiou"):
                yield stem + stem[-1] + suf


def _dropped_e(lemma: str) -> Iterable[str]:
    # judgment <-> judgement, aging <-> ageing, acknowledgment <-> acknowledgement
    for suf in ("ment", "ing", "able"):
        if lemma.endswith(suf) and len(lemma) > len(suf):
            stem = lemma[: -len(suf)]
            if stem and stem[-1] != "e":
                yield stem + "e" + suf
            elif stem and stem[-1] == "e":
                yield stem[:-1] + suf


_RULES: tuple[OrthographicRule, ...] = (
    OrthographicRule(
        "spelling.or_our",
        "color/colour, honor/honour, behavior/behaviour: -or <-> -our",
        _suffix_swap([("or", "our")]),
    ),
    OrthographicRule(
        "spelling.er_re",
        "center/centre, theater/theatre, fiber/fibre: -er <-> -re",
        _suffix_swap([("er", "re")]),
    ),
    OrthographicRule(
        "spelling.ize_ise",
        "organize/organise: -ize <-> -ise, -ization <-> -isation",
        _suffix_swap(
            [("ize", "ise"), ("ization", "isation"), ("izer", "iser"), ("izing", "ising")]
        ),
    ),
    OrthographicRule(
        "spelling.yze_yse",
        "analyze/analyse, paralyze/paralyse: -yze <-> -yse",
        _suffix_swap([("yze", "yse"), ("yzer", "yser"), ("yzing", "ysing")]),
    ),
    OrthographicRule(
        "spelling.og_ogue",
        "catalog/catalogue, dialog/dialogue, analog/analogue: -og <-> -ogue",
        _suffix_swap([("og", "ogue"), ("ogs", "ogues")]),
    ),
    OrthographicRule(
        "spelling.ce_se",
        "defence/defense, licence/license, practise/practice: -ce <-> -se",
        _suffix_swap([("ce", "se"), ("nce", "nse")]),
    ),
    OrthographicRule(
        "spelling.mme_m",
        "programme/program, gramme/gram: -mme <-> -m",
        _suffix_swap([("mme", "m")]),
    ),
    OrthographicRule(
        "spelling.ae_e",
        "encyclopaedia/encyclopedia, anaemia/anemia, paediatric/pediatric: ae <-> e",
        _infix_swap([("ae", "e")]),
    ),
    OrthographicRule(
        "spelling.oe_e",
        "foetus/fetus, oesophagus/esophagus, diarrhoea/diarrhea: oe <-> e",
        _infix_swap([("oe", "e"), ("oea", "ea")]),
    ),
    OrthographicRule(
        "spelling.doubled_consonant",
        "traveled/travelled, modeling/modelling, focused/focussed: -CC- <-> -C-",
        _doubled_consonant_before_suffix,
    ),
    OrthographicRule(
        "spelling.dropped_e",
        "judgment/judgement, aging/ageing, acknowledgment/acknowledgement: stem-e elision",
        _dropped_e,
    ),
)
# rule_ids that come from a transformation rule (used for the merge-record tag)
_RULE_IDS = frozenset(r.rule_id for r in _RULES) | {"spelling.lexical_pairs", "edit-distance"}

# Hand-listed irregular variant pairs that no transformation rule captures
# cleanly (vowel/consonant swaps, whole-word alternants). Both members still
# have to be in the lexicon and still have to pass the gloss gate.
_LEXICAL_VARIANT_PAIRS: tuple[tuple[str, str], ...] = (
    ("grey", "gray"),
    ("ax", "axe"),
    ("plough", "plow"),
    ("mould", "mold"),
    ("smoulder", "smolder"),
    ("doughnut", "donut"),
    ("sulphur", "sulfur"),
    ("sceptic", "skeptic"),
    ("cheque", "check"),
    ("tyre", "tire"),
    ("kerb", "curb"),
    ("pyjamas", "pajamas"),
    ("aluminium", "aluminum"),
    ("aeroplane", "airplane"),
    ("draught", "draft"),
    ("gaol", "jail"),
    ("storey", "story"),
    ("manoeuvre", "maneuver"),
    ("mum", "mom"),
    ("artefact", "artifact"),
    ("disc", "disk"),
    ("enquiry", "inquiry"),
    ("jewellery", "jewelry"),
    ("woollen", "woolen"),
    ("kilometre", "kilometer"),
    ("metre", "meter"),
    ("litre", "liter"),
)


_ROMAN_RE = re.compile(r"^[ivxlcdm]{2,}$")
_IEC_UNIT_RE = re.compile(r"^[a-z]i(bit|byte)$")  # kibit, mibyte, gibit, ...
_NO_VOWEL_RE = re.compile(r"^[^aeiouy]+$")


def _is_code_like(lemma: str) -> bool:
    """Reject obvious symbol/code lemmas before they enter the candidate pass.

    Roman numerals (``lxviii``, ``clxxv``) and IEC binary-unit prefixes
    (``kibit``, ``mibyte``) cluster densely under edit-distance-1 and have
    near-identical glosses ("the cardinal number that is X"), so the gloss gate
    cannot separate them; they are ``symbol-code``s, not spelling variants.
    """

    return bool(_ROMAN_RE.match(lemma) or _IEC_UNIT_RE.match(lemma) or _NO_VOWEL_RE.match(lemma))


def _pairs(items: Sequence[str]):
    """Yield all unordered pairs from ``items``."""

    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            yield items[i], items[j]


@dataclass(frozen=True)
class RuleHit:
    rule_id: str
    other: str


def candidate_variants(lemma: str) -> list[RuleHit]:
    """All orthographic-rule-derived candidate spelling variants of ``lemma``."""

    hits: list[RuleHit] = []
    seen: set[tuple[str, str]] = set()
    for rule in _RULES:
        for other in rule.variants(lemma):
            key = (rule.rule_id, other)
            if key not in seen:
                seen.add(key)
                hits.append(RuleHit(rule.rule_id, other))
    for a, b in _LEXICAL_VARIANT_PAIRS:
        if lemma == a:
            hits.append(RuleHit("spelling.lexical_pairs", b))
        elif lemma == b:
            hits.append(RuleHit("spelling.lexical_pairs", a))
    return hits


def candidate_pairs(
    lemma_set: set[str], *, edit_distance_cap: int = 1
) -> dict[frozenset[str], list[str]]:
    """Return ``{frozenset({f1, f2}): [rule_id, ...]}`` for every candidate pair.

    Both members are guaranteed to be in ``lemma_set``. Single-token lemmas only
    (no underscores -- multi-word forms are handled by the construction layer).
    A generic Levenshtein <= ``edit_distance_cap`` pass over near-equal-length
    lemmas of length >= 5 catches alternants the rules miss; those are tagged
    ``edit-distance``. Pairs found by both a rule and the edit-distance pass keep
    only the rule tag.
    """

    out: dict[frozenset[str], set[str]] = defaultdict(set)
    single = [
        w
        for w in lemma_set
        if "_" not in w and w.isalpha() and len(w) >= 2 and not _is_code_like(w)
    ]
    single_set = set(single)

    # 1. rule-driven
    for lemma in single:
        for hit in candidate_variants(lemma):
            if hit.other in single_set:
                out[frozenset({lemma, hit.other})].add(hit.rule_id)

    # 2. generic edit-distance pass (Levenshtein <= 1: one substitution,
    #    insertion, or deletion). Only lemmas of length >= 5 participate.
    #
    # Brute O(n^2) over ~150k lemmas is infeasible, so we index by highly
    # selective keys instead of comparing every pair:
    #   * substitution-1 pairs: same length L, all chars equal except position i
    #     -> key = (L, i, word with position i blanked). Two words collide on
    #     such a key iff they differ in exactly that one position.
    #   * insertion/deletion-1 pairs: lengths L and L+1, the longer with one char
    #     removed equals the shorter -> key = (min length, the shorter string)
    #     where the shorter comes either from being length L itself or from a
    #     single deletion of a length-(L+1) word. We verify the survivors with a
    #     bounded Levenshtein, and hard-cap bucket fan-out so a pathological key
    #     cannot blow up the run.
    #   * a small transposition pass (adjacent swaps) over sorted-letter buckets,
    #     hard-capped, catches things like ``calibre``/``caliber`` (distance 2).
    if edit_distance_cap >= 1:
        long_lemmas = [w for w in single if len(w) >= 5]
        _BUCKET_CAP = 64

        # substitutions
        sub_index: dict[tuple[int, int, str], list[str]] = defaultdict(list)
        for lemma in long_lemmas:
            n = len(lemma)
            for i in range(n):
                sub_index[(n, i, lemma[:i] + "\0" + lemma[i + 1 :])].append(lemma)
        for items in sub_index.values():
            if len(items) < 2 or len(items) > _BUCKET_CAP:
                continue
            for a, b in _pairs(items):
                key = frozenset({a, b})
                if key not in out:
                    out[key].add("edit-distance")

        # insertions / deletions: bucket every length-L word and every
        # single-deletion of a length-(L+1) word under (L, shorter_string)
        indel_index: dict[str, list[str]] = defaultdict(list)
        for lemma in long_lemmas:
            indel_index[lemma].append(lemma)  # the shorter itself
            for i in range(len(lemma)):
                short = lemma[:i] + lemma[i + 1 :]
                if len(short) >= 4:  # don't generate noise from tiny fragments
                    indel_index[short].append(lemma)
        for items in indel_index.values():
            uniq = sorted(set(items))
            if len(uniq) < 2 or len(uniq) > _BUCKET_CAP:
                continue
            for a, b in _pairs(uniq):
                if abs(len(a) - len(b)) > edit_distance_cap:
                    continue
                if levenshtein(a, b, cap=edit_distance_cap) <= edit_distance_cap:
                    key = frozenset({a, b})
                    if key not in out:
                        out[key].add("edit-distance")

        # transpositions (adjacent swaps): sorted-letter buckets, hard-capped
        anagram_buckets: dict[str, list[str]] = defaultdict(list)
        for lemma in long_lemmas:
            anagram_buckets["".join(sorted(lemma))].append(lemma)
        for items in anagram_buckets.values():
            if not 2 <= len(items) <= 8:
                continue
            for a, b in _pairs(items):
                if levenshtein(a, b, cap=2) <= 2:
                    key = frozenset({a, b})
                    if key not in out:
                        out[key].add("edit-distance")

    # rule tags win over the generic edit-distance tag
    result: dict[frozenset[str], list[str]] = {}
    for k, tags in out.items():
        rule_tags = sorted(t for t in tags if t != "edit-distance")
        result[k] = rule_tags or ["edit-distance"]
    return result


# ---------------------------------------------------------------------------
# Gloss-similarity gate
# ---------------------------------------------------------------------------


def _gloss_tokens(text: str) -> set[str]:
    return {t for t in basic_tokens(text) if t not in _GLOSS_STOP and len(t) > 1}


def gloss_similarity(g1: str, g2: str) -> float:
    """Token-Jaccard similarity between two glosses (after stop-stripping).

    Jaccard rather than per-pair TF-IDF: the inputs are short dictionary glosses
    where presence/absence of content words is the signal, and TF weighting over
    a two-document corpus is degenerate. A corpus-wide TF-IDF cosine is offered
    separately (:func:`gloss_cosine_corpus`) for analysis, but the gate uses
    Jaccard.
    """

    a, b = _gloss_tokens(g1), _gloss_tokens(g2)
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def gloss_cosine_corpus(glosses: Sequence[str]) -> object:
    """TF-IDF cosine matrix over a list of glosses (sklearn). Provided for analysis."""

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vec = TfidfVectorizer(token_pattern=r"[A-Za-z]{2,}", stop_words=list(_GLOSS_STOP))
    mat = vec.fit_transform(list(glosses))
    return cosine_similarity(mat)


# Gate threshold. Spot-checked: real US/UK pairs share the bulk of their gloss
# content words (color/colour glosses are near-identical -> Jaccard ~0.5-1.0),
# whereas edit-distance look-alikes (defer/differ, colon/colour, cloud/clout)
# share essentially nothing (~0.0-0.1). 0.34 sits in the gap and still admits
# pairs where one gloss is a touch longer/shorter than the other.
GLOSS_GATE_THRESHOLD: float = 0.34


@dataclass
class _FormSenses:
    """Senses of one form, grouped by POS: pos -> [(sense_id, gloss), ...]."""

    by_pos: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))


# ---------------------------------------------------------------------------
# MergeRecord + IdentityCluster
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MergeRecord:
    """One belief-set-style merge that brought two forms' senses into an IC.

    ``rule_id`` is the orthographic rule that fired (or ``edit-distance``);
    ``gloss_score`` is the Jaccard similarity of the best matched gloss pair;
    ``matched_sense_pair`` is that gloss pair's sense ids; ``provenance`` records
    the build procedure version.
    """

    merge_id: str
    contributing_forms: frozenset[str]
    merged_sense_ids: frozenset[str]
    rule_id: str
    gloss_score: float
    matched_sense_pair: tuple[str, str]
    pos: str
    provenance: str = "identity_clusters.build_identity_clusters/v2"

    def to_json(self) -> dict[str, object]:
        return {
            "merge_id": self.merge_id,
            "contributing_forms": sorted(self.contributing_forms),
            "merged_sense_ids": sorted(self.merged_sense_ids),
            "rule_id": self.rule_id,
            "gloss_score": round(self.gloss_score, 4),
            "matched_sense_pair": list(self.matched_sense_pair),
            "pos": self.pos,
            "provenance": self.provenance,
        }


@dataclass
class IdentityCluster:
    """A merged referential unit: a set of forms + their senses + the merge records."""

    ic_id: str
    forms: set[str] = field(default_factory=set)
    sense_ids: set[str] = field(default_factory=set)
    merge_records: list[MergeRecord] = field(default_factory=list)

    @property
    def aliases(self) -> set[str]:
        return set(self.forms)

    def to_json(self) -> dict[str, object]:
        return {
            "ic_id": self.ic_id,
            "forms": sorted(self.forms),
            "sense_ids": sorted(self.sense_ids),
            "aliases": sorted(self.forms),
            "merge_records": [m.to_json() for m in self.merge_records],
        }


# Backwards-compatible lightweight view used by ``wordnet_pipeline`` and the
# existing tests. ``forms`` is the IC's form set; ``evidence`` is the tuple of
# rule ids that built it.
@dataclass(frozen=True, slots=True)
class IdentityClusterMerge:
    ic_id: str
    forms: frozenset[str]
    rationale: str
    evidence: tuple[str, ...]


# ---------------------------------------------------------------------------
# Build procedure
# ---------------------------------------------------------------------------


def _ic_id_for_forms(forms: Iterable[str]) -> str:
    return "ic:" + sorted(forms)[0]


def _iter_form_pos_sense_def(lexicon: object):
    """Yield ``(normalized_lemma, synset_pos, sense_id, definition)`` for every sense.

    Fast path: read the ``wn`` SQLite store directly (one query, ~2s for OEWN).
    The per-object ``wn`` navigation API (``word.lemma()``, ``sense.synset()``,
    ``synset.definition()``) costs ~1ms per call -> ~6 min over OEWN, so we only
    fall back to it if the DB path is unavailable.
    """

    lexicon_id: str | None = None
    try:
        lexs = lexicon.lexicons()  # type: ignore[attr-defined]
        if lexs:
            lexicon_id = lexs[0].id
    except Exception:  # pragma: no cover - defensive
        lexicon_id = None

    if lexicon_id is not None:
        try:
            import os
            import sqlite3

            import wn as _wn

            db_path = os.path.join(_wn.config.data_directory, "wn.db")
            if os.path.exists(db_path):
                con = sqlite3.connect(db_path)
                try:
                    row = con.execute(
                        "SELECT rowid FROM lexicons WHERE id = ? LIMIT 1", (lexicon_id,)
                    ).fetchone()
                    if row is not None:
                        lex_rowid = row[0]
                        query = """
                            SELECT f.form, sy.pos, s.id, d.definition
                            FROM senses s
                            JOIN entries e ON e.rowid = s.entry_rowid
                            JOIN forms f ON f.entry_rowid = e.rowid AND f.rank = 0
                            JOIN synsets sy ON sy.rowid = s.synset_rowid
                            LEFT JOIN definitions d ON d.synset_rowid = sy.rowid
                            WHERE s.lexicon_rowid = ?
                        """
                        for form, pos, sense_id, definition in con.execute(query, (lex_rowid,)):
                            yield normalize_lemma(form), pos, sense_id, definition or ""
                        return
                finally:
                    con.close()
        except Exception:  # pragma: no cover - fall back to navigation
            pass

    # slow fallback: per-object navigation
    for word in lexicon.words():  # type: ignore[attr-defined]
        lemma = normalize_lemma(word.lemma())
        for sense in word.senses():
            synset = sense.synset()
            yield lemma, synset.pos, sense.id, synset.definition() or ""


def build_identity_clusters(lexicon: object, *, edit_distance_cap: int = 1) -> dict[str, object]:
    """Run the full IC-merge procedure over a ``wn`` lexicon.

    Returns a dict with keys ``clusters`` (list[:class:`IdentityCluster`]),
    ``merge_records`` (flat list[:class:`MergeRecord`]), ``form_to_ic``
    (``{normalized_form: ic_id}``), ``rejected`` (``[(f1, f2, rule_ids,
    best_gloss_score)]`` -- candidates the gloss gate dropped), and ``stats``.
    """

    # 1. collect lemma set + per-form senses
    form_senses: dict[str, _FormSenses] = defaultdict(_FormSenses)
    for lemma, pos, sense_id, definition in _iter_form_pos_sense_def(lexicon):
        if not definition:
            continue
        form_senses[lemma].by_pos[pos].append((sense_id, definition))
    lemma_set = set(form_senses)

    # 2. candidate pairs
    cands = candidate_pairs(lemma_set, edit_distance_cap=edit_distance_cap)

    # 3. gloss gate -> accepted merges
    merge_records: list[MergeRecord] = []
    rejected: list[tuple[str, str, list[str], float]] = []
    accepted: list[
        tuple[str, str, list[str], float, tuple[str, str], str, frozenset[str]]
    ] = []

    for pair, rule_ids in cands.items():
        f1, f2 = sorted(pair)
        fs1, fs2 = form_senses[f1], form_senses[f2]
        best_score = 0.0
        best_pair: tuple[str, str] | None = None
        best_pos = ""
        merged_senses: set[str] = set()
        for pos in set(fs1.by_pos) & set(fs2.by_pos):
            for s1, g1 in fs1.by_pos[pos]:
                for s2, g2 in fs2.by_pos[pos]:
                    score = gloss_similarity(g1, g2)
                    if score >= GLOSS_GATE_THRESHOLD:
                        merged_senses.add(s1)
                        merged_senses.add(s2)
                        if score > best_score:
                            best_score, best_pair, best_pos = score, (s1, s2), pos
        if best_pair is None:
            rejected.append((f1, f2, rule_ids, best_score))
            continue
        accepted.append(
            (f1, f2, rule_ids, best_score, best_pair, best_pos, frozenset(merged_senses))
        )

    # 4. union-find over accepted pairs -> ICs (smallest form is the root id)
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if ry < rx:
            rx, ry = ry, rx
        parent[ry] = rx

    for f1, f2, *_ in accepted:
        union(f1, f2)

    components: dict[str, set[str]] = defaultdict(set)
    for f in list(parent):
        components[find(f)].add(f)

    clusters_by_root: dict[str, IdentityCluster] = {}
    for root, forms in components.items():
        ic = IdentityCluster(ic_id=_ic_id_for_forms(forms), forms=set(forms))
        for f in forms:
            for senses in form_senses[f].by_pos.values():
                for sid, _ in senses:
                    ic.sense_ids.add(sid)
        clusters_by_root[root] = ic

    # 5. emit merge records, attach to the right IC
    for i, (f1, f2, rule_ids, score, sense_pair, pos, merged) in enumerate(accepted):
        ic = clusters_by_root[find(f1)]
        mr = MergeRecord(
            merge_id=f"merge:{ic.ic_id[3:]}:{len(ic.merge_records)}",
            contributing_forms=frozenset({f1, f2}),
            merged_sense_ids=merged,
            rule_id=rule_ids[0] if rule_ids else "edit-distance",
            gloss_score=score,
            matched_sense_pair=sense_pair,
            pos=pos,
        )
        ic.merge_records.append(mr)
        merge_records.append(mr)

    form_to_ic: dict[str, str] = {}
    for ic in clusters_by_root.values():
        for f in ic.forms:
            form_to_ic[f] = ic.ic_id

    clusters = sorted(clusters_by_root.values(), key=lambda c: c.ic_id)
    return {
        "clusters": clusters,
        "merge_records": merge_records,
        "form_to_ic": form_to_ic,
        "rejected": rejected,
        "stats": {
            "lemmas": len(lemma_set),
            "candidate_pairs": len(cands),
            "accepted_pairs": len(accepted),
            "rejected_pairs": len(rejected),
            "clusters": len(clusters),
            "forms_in_clusters": len(form_to_ic),
            "merge_records": len(merge_records),
        },
    }


# ---------------------------------------------------------------------------
# Persisted table + runtime interface
# ---------------------------------------------------------------------------


def dump_table_json(result: dict[str, object], path: Path | None = None) -> dict[str, object]:
    """Serialize a build result to the on-disk IC table format."""

    path = path or _IC_TABLE_JSON
    clusters = result["clusters"]
    payload = {
        "schema": "ic-merge-table/v2",
        "stats": result["stats"],
        "gloss_gate_threshold": GLOSS_GATE_THRESHOLD,
        "clusters": [c.to_json() for c in clusters],  # type: ignore[union-attr]
        "rejected": [
            {"forms": [f1, f2], "rule_ids": rids, "best_gloss_score": round(s, 4)}
            for (f1, f2, rids, s) in result["rejected"]  # type: ignore[misc]
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    return payload


def _load_table_json(path: Path | None = None) -> dict[str, object] | None:
    path = path or _IC_TABLE_JSON
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("schema") != "ic-merge-table/v2":
        return None
    return data


# Module-level lazy cache: {normalized_form: IdentityClusterMerge}
_FORM_INDEX_CACHE: dict[str, IdentityClusterMerge] | None = None


def _index_from_table(data: dict[str, object]) -> dict[str, IdentityClusterMerge]:
    index: dict[str, IdentityClusterMerge] = {}
    for c in data.get("clusters", []):  # type: ignore[union-attr]
        ic_id = c["ic_id"]
        forms = frozenset(c["forms"])
        rule_ids: list[str] = []
        for mr in c.get("merge_records", []):
            rid = mr.get("rule_id")
            if rid and rid not in rule_ids:
                rule_ids.append(rid)
        rationale = (
            "Spelling-variant merge ("
            + ", ".join(rule_ids or ["edit-distance"])
            + ") with gloss-similarity confirmation; all forms retained."
        )
        view = IdentityClusterMerge(
            ic_id=ic_id, forms=forms, rationale=rationale, evidence=tuple(rule_ids)
        )
        for f in forms:
            index[normalize_lemma(f)] = view
    return index


def _index_from_build(lexicon: object | None) -> dict[str, IdentityClusterMerge]:
    if lexicon is None:
        # last resort: load the lexicon ourselves (slow). Mirrors
        # wordnet_pipeline.load_lexicon; not imported from there to avoid a cycle.
        import wn

        wn.download("oewn:2024")
        lexicon = wn.Wordnet("oewn:2024")
    result = build_identity_clusters(lexicon)
    return _index_from_table(dump_table_json(result))


def spelling_variant_index(
    *, rebuild: bool = False, lexicon: object | None = None
) -> dict[str, IdentityClusterMerge]:
    """Return ``{normalized_form: IdentityClusterMerge}`` for all merged forms.

    Uses the persisted ``reports/ic-merge-method.json`` table when available
    (fast, O(1) per lookup). ``rebuild=True`` recomputes from ``lexicon`` (or a
    freshly-loaded OEWN lexicon) and rewrites the table.
    """

    global _FORM_INDEX_CACHE
    if rebuild:
        _FORM_INDEX_CACHE = _index_from_build(lexicon)
        return _FORM_INDEX_CACHE
    if _FORM_INDEX_CACHE is not None:
        return _FORM_INDEX_CACHE
    data = _load_table_json()
    _FORM_INDEX_CACHE = _index_from_table(data) if data is not None else _index_from_build(lexicon)
    return _FORM_INDEX_CACHE


def identity_cluster_for_form(form: str) -> IdentityClusterMerge | None:
    """Runtime interface: the IC merge view for ``form``, or ``None``.

    Preserves the signature ``wordnet_pipeline.build_sense_level_paper_wordnet_graph``
    relies on (``.ic_id`` for graph-node metadata).
    """

    return spelling_variant_index().get(normalize_lemma(form))


def reset_cache() -> None:
    """Drop the in-process index cache (for tests)."""

    global _FORM_INDEX_CACHE
    _FORM_INDEX_CACHE = None


# ---------------------------------------------------------------------------
# Original regression fixture. These seven pairs MUST still be merged by the
# live procedure; the constant is kept so the legacy import/test surface works.
# ---------------------------------------------------------------------------

ORIGINAL_REGRESSION_PAIRS: tuple[tuple[str, str], ...] = (
    ("color", "colour"),
    ("center", "centre"),
    ("theater", "theatre"),
    ("ax", "axe"),
    ("gray", "grey"),
    ("honor", "honour"),
    ("organize", "organise"),
)

HIGH_CONFIDENCE_SPELLING_VARIANTS: tuple[IdentityClusterMerge, ...] = tuple(
    IdentityClusterMerge(
        ic_id="ic:" + sorted(pair)[0],
        forms=frozenset(pair),
        rationale="Original high-confidence US/UK spelling-variant regression fixture; "
        "the live build procedure must reproduce this merge.",
        evidence=("regression-fixture",),
    )
    for pair in ORIGINAL_REGRESSION_PAIRS
)
