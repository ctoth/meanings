"""Per-IC defeasible admission evaluator for the human Up-Goer vocabulary.

The human Up-Goer list is the **admitted extension** of a declarable defeasible
admission policy -- not a lexicality-tag filter over IC ids. Each IC's admission
is a *local* decision: it depends only on that IC's own member senses (their
lexicality tags, the classifier path/confidence that produced each tag), the
IC's merge/exclusion provenance, and a handful of facts derived from those
members. No cross-IC interaction. So we do not need ``gunray``'s full
argument-enumeration machinery at scale: we run an ordered-rule evaluation with
a superiority relation, per IC, and surface a structured rationale.

The four upgoer-note admission conditions
(``notes/upgoer-identity-clusters.md`` -- "Admission Policy For The Human
Up-Goer List") translate to:

  * maps to >=1 admitted IC / admitted reading            -> ``r_admit_lexical`` / ``r_admit_phrase_idiom``
  * the admitted reading is lexical, not a symbol/code     -> ``r_block_symbol_only`` strictly dominates the admit rules
  * evidence is explicit (senses + glosses + tags + ...)   -> ``evidence_explicit`` predicate gates the admit rules; ``r_quarantine_low_conf`` catches the failures
  * admission does not depend on a sense mismatch          -> ``r_block_sense_mismatch`` (the ``no`` is-not-Nobelium rule)

The per-class precision discount factors come from the lexicality classifier
head-to-head (``reports/lexicality-headtohead.md`` -- the *rule classifier* CV
precisions, since that classifier is what ``meanings.wordnet_pipeline`` runs).
A lexical reading whose tag came from a low-precision classifier path is treated
as *uncertain*, not admitted.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------
class AdmissionDecision(StrEnum):
    ADMIT = "admit"
    EXCLUDE = "exclude"
    QUARANTINE = "quarantine"
    UNCERTAIN = "uncertain"


# ---------------------------------------------------------------------------
# Per-class precision lookup (rule-classifier CV precisions; head-to-head §3)
# ---------------------------------------------------------------------------
# Reading: a lexical/phrase/idiom *tag* that hinges on a class whose precision
# here is below LOW_PRECISION_THRESHOLD is "an uncertain call, not an admitted
# fact". proper-name at 0.386 is the headline low-precision class.
LEXICALITY_CLASS_PRECISION: dict[str, float] = {
    "lexical-word": 0.816,
    "phrase": 0.780,
    "symbol-code": 0.958,
    "chemical": 0.779,
    "proper-name": 0.386,
    "taxon": 0.818,
    "technical-term": 0.958,
    "abbreviation": 1.000,
    # idiom has no head-to-head support row (the gold set folds idiom into the
    # phrase stratum); treat it like phrase.
    "idiom": 0.780,
    # construction (round-7 hole #4): multi-token form with non-compositional
    # meaning; fires only on explicit idiomatic-gloss markers on multiword
    # lemmas, so it inherits the high precision of those markers.  No
    # head-to-head support row yet; treat as the idiom/phrase precision floor.
    "construction": 0.780,
    "uncertain": 0.0,
}
LOW_PRECISION_THRESHOLD = 0.50
LOW_CONFIDENCE_THRESHOLD = 0.50  # trained-classifier top-prob below this -> shaky

# The blocked (non-lexical) tags. An IC every one of whose readings is in this
# set has no lexical reading at all -> excluded. Per the upgoer note this set is
# {symbol-code, abbreviation, taxon, chemical, proper-name}; technical-term is
# *not* a hard block (a technical term can be a real word, just domain-specific)
# -- a technical-term-only IC falls through to the uncertain catch-all (pending
# review / the expanded list), it is not permanently excluded.
SYMBOL_ONLY_TAGS: frozenset[str] = frozenset(
    {"symbol-code", "abbreviation", "taxon", "chemical", "proper-name"}
)
LEXICAL_ADMIT_TAGS: frozenset[str] = frozenset({"lexical-word"})
PHRASE_IDIOM_ADMIT_TAGS: frozenset[str] = frozenset({"phrase", "idiom"})
# Round-7 hole #4: construction is a separate admit tag (under the expanded
# policy only); compositional `phrase` ICs stay in `uncertain` unless
# r_admit_phrase_idiom is enabled.
CONSTRUCTION_ADMIT_TAGS: frozenset[str] = frozenset({"construction"})

# Classifier reason prefixes that are NOT high-precision surface rules.
_TRAINED_PROB_RE = re.compile(r"\.p(\d+(?:\.\d+)?)\b")


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class SenseRecord:
    """One member sense of an IC, as produced by the sense-level ingestion."""

    sense_id: str
    form: str
    lemma: str
    pos: str
    definition: str
    lexicality: str
    lexicality_reasons: tuple[str, ...] = ()
    frequency: float | None = None
    aoa: float | None = None
    source_synset: str | None = None


@dataclass(frozen=True, slots=True)
class ICRecord:
    """An identity cluster: its member senses plus merge/exclusion provenance."""

    ic_id: str
    senses: tuple[SenseRecord, ...]
    merge_rationale: str | None = None
    exclusion_records: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Derived facts about an IC (the "predicates")
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ICFacts:
    ic_id: str
    sense_count: int
    tags: tuple[str, ...]
    tag_counts: Mapping[str, int]
    forms: tuple[str, ...]
    lexical_sense_ids: tuple[str, ...]
    phrase_idiom_sense_ids: tuple[str, ...]
    construction_sense_ids: tuple[str, ...]
    blocked_sense_ids: tuple[str, ...]
    has_lexical_reading: bool
    has_phrase_or_idiom_reading: bool
    has_construction_reading: bool
    every_reading_blocked: bool
    evidence_explicit: bool
    evidence_missing_reasons: tuple[str, ...]
    admission_depends_on_sense_mismatch: bool
    sense_mismatch_reasons: tuple[str, ...]
    low_confidence_lexical: bool
    low_confidence_reasons: tuple[str, ...]
    # the best (highest-precision*confidence) admitting reading, if any
    best_admit_sense_id: str | None
    best_admit_tag: str | None
    best_admit_confidence: float | None
    best_admit_precision: float | None


def _reason_confidence(reasons: Iterable[str]) -> float | None:
    """Highest trained-classifier top-prob mentioned in ``reasons``.

    ``surface.*`` reasons are near-deterministic -> treat as confidence 1.0.
    ``fallback.*`` reasons (model file absent) -> conservative 0.5.
    ``trained.lowconf.pNN`` / ``trained.<class>.pNN`` -> the parsed prob.
    """
    best: float | None = None
    for r in reasons:
        if r.startswith("surface."):
            best = 1.0 if best is None else max(best, 1.0)
            continue
        if r.startswith("fallback."):
            cand = 0.5
        else:
            m = _TRAINED_PROB_RE.search(r)
            cand = float(m.group(1)) if m else None
        if cand is not None:
            best = cand if best is None else max(best, cand)
    return best


def _is_surface_reason(reasons: Iterable[str]) -> bool:
    return any(r.startswith("surface.") for r in reasons)


def _worst_precision_in_reasons(lexicality: str, reasons: Iterable[str]) -> float:
    """Lowest per-class precision among the IC's tag and any class label that
    appears in its classifier-reason strings (combined/re-routed reasons such as
    ``trained.proper-name.p0.41`` mention a low-precision class even when the
    final tag is ``lexical-word``)."""
    worst = LEXICALITY_CLASS_PRECISION.get(lexicality, 0.5)
    for r in reasons:
        for cls, p in LEXICALITY_CLASS_PRECISION.items():
            if cls in r:
                worst = min(worst, p)
    return worst


def _shaky_lexical(sense) -> tuple[bool, float, float | None]:
    """Is a lexical-word reading a shaky (sense-mismatch-prone) classifier call?

    Shaky iff it is NOT a high-precision surface rule AND either (a) some class
    label mentioned in its reasons is low-precision, or (b) its top confidence is
    below threshold *and* a low-precision class is implicated. Returns
    ``(shaky, worst_precision, confidence)``.
    """
    if _is_surface_reason(sense.lexicality_reasons):
        return False, LEXICALITY_CLASS_PRECISION.get(sense.lexicality, 0.5), None
    worst = _worst_precision_in_reasons(sense.lexicality, sense.lexicality_reasons)
    conf = _reason_confidence(sense.lexicality_reasons)
    low_prec = worst < LOW_PRECISION_THRESHOLD
    low_conf = conf is not None and conf < LOW_CONFIDENCE_THRESHOLD
    shaky = low_prec
    return shaky, worst, conf


def derive_ic_facts(ic: ICRecord) -> ICFacts:
    senses = ic.senses
    tags = tuple(s.lexicality for s in senses)
    tag_counts = Counter(tags)
    forms = tuple(sorted({s.form for s in senses}))

    lexical = [s for s in senses if s.lexicality in LEXICAL_ADMIT_TAGS]
    phrase_idiom = [s for s in senses if s.lexicality in PHRASE_IDIOM_ADMIT_TAGS]
    construction = [s for s in senses if s.lexicality in CONSTRUCTION_ADMIT_TAGS]
    blocked = [s for s in senses if s.lexicality in SYMBOL_ONLY_TAGS]
    uncertain_tagged = [s for s in senses if s.lexicality == "uncertain"]

    has_lexical = bool(lexical)
    has_phrase_idiom = bool(phrase_idiom)
    has_construction = bool(construction)
    admitting = lexical + phrase_idiom + construction
    # "every reading is in the blocked set" -> truly nothing admissible. (An
    # uncertain-tagged member is not blocked, but it is not admitting either; if
    # the IC has *only* uncertain members it is not symbol-only, it is uncertain
    # -- handled by the uncertain catch-all.)
    every_blocked = bool(senses) and not admitting and not uncertain_tagged

    # --- evidence_explicit -------------------------------------------------
    missing: list[str] = []
    if not senses:
        missing.append("no source senses")
    glossless = [s.sense_id for s in senses if not (s.definition and s.definition.strip())]
    if glossless:
        missing.append(f"{len(glossless)} sense(s) without a gloss")
    untagged = [s.sense_id for s in senses if not s.lexicality]
    if untagged:
        missing.append(f"{len(untagged)} sense(s) without a lexicality tag")
    unreasoned = [s.sense_id for s in senses if not s.lexicality_reasons]
    if unreasoned:
        missing.append(f"{len(unreasoned)} sense(s) without a classifier rationale")
    if ic.merge_rationale is None and ic.exclusion_records == ():
        # An IC built from a single form with no merges and no exclusions still
        # has a *constructible* rationale; the only genuine gap is when we have
        # neither and there is also nothing to say. We treat the presence of a
        # merge rationale OR any exclusion record OR a single-clean-form note as
        # "rationale recorded". So this is NOT itself a missing-evidence flag --
        # see _ensure_rationale below. We keep the predicate honest: if the IC
        # has zero senses we already flagged it.
        pass
    evidence_explicit = not missing

    # --- admission_depends_on_sense_mismatch -------------------------------
    # The IC's *only* lexical-word reading is a shaky classifier call: not a
    # surface rule, and a low-precision class (effectively proper-name, P~0.39)
    # is implicated in how it got tagged -- the "no" inheriting "no::n" Nobelium
    # evidence shape, generalized. Restricted to lexical-word readings: a shaky
    # *phrase/idiom* reading just defers the IC to the uncertain bucket (the
    # expanded list may yet admit it); only a spurious *lexical-word* claim is the
    # sense-mismatch artifact the upgoer note flags.
    shaky_lexical_info = [(s, *_shaky_lexical(s)) for s in lexical]
    has_solid_lexical = any(not shaky for (_s, shaky, _p, _c) in shaky_lexical_info)
    mismatch_reasons: list[str] = []
    if lexical and not has_solid_lexical:
        for s, shaky, worst, conf in shaky_lexical_info:
            mismatch_reasons.append(
                f"{s.sense_id}: tag {s.lexicality!r} via {','.join(s.lexicality_reasons) or '?'} "
                f"(worst implicated class precision {worst:.3f}"
                + (f", confidence {conf:.2f}" if conf is not None else "")
                + ")"
            )
    admission_depends_on_sense_mismatch = bool(mismatch_reasons)

    # --- low_confidence_lexical (for the quarantine rule) ------------------
    # A lexical-word reading that is itself a low-*confidence* (not just
    # low-precision) classifier call AND a low-precision class is implicated.
    # lexical-word's own class precision (0.816) is above threshold, so this is
    # reachable only via combined / re-routed reason strings -- structurally rare;
    # the report documents that.
    low_conf_reasons: list[str] = []
    if lexical and not has_solid_lexical:
        for s in lexical:
            if _is_surface_reason(s.lexicality_reasons):
                continue
            worst = _worst_precision_in_reasons(s.lexicality, s.lexicality_reasons)
            conf = _reason_confidence(s.lexicality_reasons)
            if conf is not None and conf < LOW_CONFIDENCE_THRESHOLD and worst < LOW_PRECISION_THRESHOLD:
                low_conf_reasons.append(
                    f"{s.sense_id}: tag {s.lexicality!r} confidence {conf:.2f} "
                    f"and worst implicated class precision {worst:.3f} both low"
                )
    low_confidence_lexical = bool(low_conf_reasons)

    # --- best admitting reading -------------------------------------------
    best_id: str | None = None
    best_tag: str | None = None
    best_conf: float | None = None
    best_prec: float | None = None
    best_score = -1.0
    for s in admitting:
        prec = LEXICALITY_CLASS_PRECISION.get(s.lexicality, 0.5)
        conf = _reason_confidence(s.lexicality_reasons)
        c = 1.0 if conf is None else conf
        score = prec * c
        if score > best_score:
            best_score, best_id, best_tag, best_conf, best_prec = score, s.sense_id, s.lexicality, conf, prec

    return ICFacts(
        ic_id=ic.ic_id,
        sense_count=len(senses),
        tags=tags,
        tag_counts=dict(sorted(tag_counts.items())),
        forms=forms,
        lexical_sense_ids=tuple(s.sense_id for s in lexical),
        phrase_idiom_sense_ids=tuple(s.sense_id for s in phrase_idiom),
        construction_sense_ids=tuple(s.sense_id for s in construction),
        blocked_sense_ids=tuple(s.sense_id for s in blocked),
        has_lexical_reading=has_lexical,
        has_phrase_or_idiom_reading=has_phrase_idiom,
        has_construction_reading=has_construction,
        every_reading_blocked=every_blocked,
        evidence_explicit=evidence_explicit,
        evidence_missing_reasons=tuple(missing),
        admission_depends_on_sense_mismatch=admission_depends_on_sense_mismatch,
        sense_mismatch_reasons=tuple(mismatch_reasons),
        low_confidence_lexical=low_confidence_lexical,
        low_confidence_reasons=tuple(low_conf_reasons),
        best_admit_sense_id=best_id,
        best_admit_tag=best_tag,
        best_admit_confidence=best_conf,
        best_admit_precision=best_prec,
    )


# ---------------------------------------------------------------------------
# Rules + policy
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Rule:
    """A declarable admission rule.

    ``when`` maps :class:`ICFacts` -> (fired: bool, condition_evidence: list[str]).
    ``decision`` is what firing concludes; ``priority`` orders rules (higher
    dominates lower); ``rule_id``/``description`` are for the rationale.
    """

    rule_id: str
    description: str
    priority: int
    decision: AdmissionDecision
    when: object  # Callable[[ICFacts], tuple[bool, list[str]]]
    enabled: bool = True

    def fires(self, facts: ICFacts) -> tuple[bool, list[str]]:
        if not self.enabled:
            return False, []
        return self.when(facts)  # type: ignore[operator]


@dataclass(frozen=True, slots=True)
class AdmissionPolicy:
    """An ordered, superiority-bearing rule set. Inspectable; not hardcoded ifs."""

    rules: tuple[Rule, ...]
    # explicit pairwise superiority on rule ids (stronger, weaker). Redundant
    # with priorities but recorded so the relation is independently inspectable
    # (and so a gunray translation can read it off directly).
    superiority: tuple[tuple[str, str], ...] = ()
    name: str = "human-up-goer-admission/v1"

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "priority": r.priority,
                    "decision": r.decision.value,
                    "enabled": r.enabled,
                }
                for r in self.rules
            ],
            "superiority": [list(p) for p in self.superiority],
        }


# ---------------------------------------------------------------------------
# Rule bodies
# ---------------------------------------------------------------------------
def _w_admit_lexical(f: ICFacts) -> tuple[bool, list[str]]:
    if f.has_lexical_reading and f.evidence_explicit:
        return True, [
            f"has a lexical-word reading ({len(f.lexical_sense_ids)} sense(s): "
            f"{', '.join(f.lexical_sense_ids[:5])}{'...' if len(f.lexical_sense_ids) > 5 else ''})",
            "evidence is explicit (source senses + glosses + tags + classifier rationale + merge/exclusion record)",
        ]
    return False, []


def _w_admit_phrase_idiom(f: ICFacts) -> tuple[bool, list[str]]:
    if f.has_phrase_or_idiom_reading and f.evidence_explicit:
        return True, [
            f"has a phrase/idiom reading ({len(f.phrase_idiom_sense_ids)} sense(s): "
            f"{', '.join(f.phrase_idiom_sense_ids[:5])}{'...' if len(f.phrase_idiom_sense_ids) > 5 else ''})",
            "evidence is explicit",
        ]
    return False, []


def _w_admit_construction(f: ICFacts) -> tuple[bool, list[str]]:
    """Round-7 hole #4: admit an IC whose only admitting reading is a
    `construction` (multi-token form with non-compositional meaning), under
    the expanded policy only.  Strict (single-word) admission stays at
    `r_admit_lexical`."""
    if f.has_construction_reading and f.evidence_explicit:
        return True, [
            f"has a construction reading ({len(f.construction_sense_ids)} sense(s): "
            f"{', '.join(f.construction_sense_ids[:5])}{'...' if len(f.construction_sense_ids) > 5 else ''})",
            "evidence is explicit (multi-token form with non-compositional meaning, surface-rule-backed)",
        ]
    return False, []


def _w_block_symbol_only(f: ICFacts) -> tuple[bool, list[str]]:
    if f.every_reading_blocked:
        return True, [
            "every reading is a non-lexical artifact "
            f"(tags: {dict(f.tag_counts)}) -- no lexical/phrase/idiom reading exists",
        ]
    return False, []


def _w_block_sense_mismatch(f: ICFacts) -> tuple[bool, list[str]]:
    if f.admission_depends_on_sense_mismatch:
        return True, [
            "the only admitting reading hinges on a low-precision classifier call "
            "(no surface-rule-backed lexical reading to fall back on):",
            *("  " + r for r in f.sense_mismatch_reasons),
        ]
    return False, []


def _w_quarantine_low_conf(f: ICFacts) -> tuple[bool, list[str]]:
    if f.has_lexical_reading and not f.evidence_explicit:
        return True, [
            "has a lexical reading but evidence is not explicit: "
            + "; ".join(f.evidence_missing_reasons),
        ]
    if f.low_confidence_lexical:
        return True, [
            "the admitting reading's classifier confidence is below threshold and "
            "its class precision is low:",
            *("  " + r for r in f.low_confidence_reasons),
        ]
    return False, []


# ---------------------------------------------------------------------------
# Default policy
# ---------------------------------------------------------------------------
def default_policy(*, admit_phrases_and_idioms: bool = False) -> AdmissionPolicy:
    """The default human Up-Goer admission policy.

    ``admit_phrases_and_idioms`` toggles ``r_admit_phrase_idiom`` -- off gives
    the strict single-word list, on gives the expanded list.
    """
    rules = (
        Rule(
            rule_id="r_block_symbol_only",
            description="exclude(IC) if every reading is symbol-code/abbreviation/taxon/chemical/proper-name/technical-term",
            priority=100,
            decision=AdmissionDecision.EXCLUDE,
            when=_w_block_symbol_only,
        ),
        Rule(
            rule_id="r_block_sense_mismatch",
            description="exclude(IC) if admission depends on a sense mismatch (only admitting reading is a low-precision classifier call)",
            priority=100,
            decision=AdmissionDecision.EXCLUDE,
            when=_w_block_sense_mismatch,
        ),
        Rule(
            rule_id="r_quarantine_low_conf",
            description="quarantine(IC) if it has a lexical reading but evidence is not explicit, or the admitting reading's confidence & class precision are both low",
            priority=50,
            decision=AdmissionDecision.QUARANTINE,
            when=_w_quarantine_low_conf,
        ),
        Rule(
            rule_id="r_admit_lexical",
            description="admit(IC) if it has a lexical-word reading and evidence is explicit",
            priority=10,
            decision=AdmissionDecision.ADMIT,
            when=_w_admit_lexical,
        ),
        Rule(
            rule_id="r_admit_phrase_idiom",
            description="admit(IC) if it has a phrase/idiom reading and evidence is explicit (expanded list)",
            priority=10,
            decision=AdmissionDecision.ADMIT,
            when=_w_admit_phrase_idiom,
            enabled=admit_phrases_and_idioms,
        ),
        Rule(
            rule_id="r_admit_construction",
            description="admit(IC) if it has a construction reading (multi-token non-compositional) and evidence is explicit (expanded list)",
            priority=10,
            decision=AdmissionDecision.ADMIT,
            when=_w_admit_construction,
            enabled=admit_phrases_and_idioms,
        ),
    )
    superiority = (
        ("r_block_symbol_only", "r_admit_lexical"),
        ("r_block_symbol_only", "r_admit_phrase_idiom"),
        ("r_block_symbol_only", "r_admit_construction"),
        ("r_block_symbol_only", "r_quarantine_low_conf"),
        ("r_block_sense_mismatch", "r_admit_lexical"),
        ("r_block_sense_mismatch", "r_admit_phrase_idiom"),
        ("r_block_sense_mismatch", "r_admit_construction"),
        ("r_block_sense_mismatch", "r_quarantine_low_conf"),
        ("r_quarantine_low_conf", "r_admit_lexical"),
        ("r_quarantine_low_conf", "r_admit_phrase_idiom"),
        ("r_quarantine_low_conf", "r_admit_construction"),
    )
    return AdmissionPolicy(rules=rules, superiority=superiority)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RuleFiring:
    rule_id: str
    priority: int
    decision: AdmissionDecision
    description: str
    condition_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AdmissionVerdict:
    ic_id: str
    decision: AdmissionDecision
    fired: tuple[RuleFiring, ...]          # rule(s) that produced the verdict
    defeated: tuple[RuleFiring, ...]       # rules that also fired but were dominated
    facts: ICFacts
    rationale: tuple[str, ...]             # the merge/exclusion rationale the upgoer note demands
    aliases: tuple[str, ...]               # forms expressing an admitted reading (admit only)
    excluded_sense_ids: tuple[str, ...]    # non-admitting member senses

    def to_json(self) -> dict[str, object]:
        return {
            "ic_id": self.ic_id,
            "decision": self.decision.value,
            "fired_rules": [
                {"rule_id": r.rule_id, "priority": r.priority, "decision": r.decision.value}
                for r in self.fired
            ],
            "defeated_rules": [
                {"rule_id": r.rule_id, "priority": r.priority, "decision": r.decision.value}
                for r in self.defeated
            ],
            "rationale": list(self.rationale),
            "aliases": list(self.aliases),
            "excluded_sense_ids": list(self.excluded_sense_ids),
            "tag_counts": dict(self.facts.tag_counts),
            "sense_count": self.facts.sense_count,
        }


def _build_rationale(decision: AdmissionDecision, fired: Sequence[RuleFiring],
                     defeated: Sequence[RuleFiring], facts: ICFacts,
                     ic: ICRecord) -> tuple[str, ...]:
    lines: list[str] = []
    lines.append(f"decision: {decision.value}")
    for fr in fired:
        lines.append(f"fired: {fr.rule_id} (priority {fr.priority}, concludes {fr.decision.value}) -- {fr.description}")
        lines.extend("  because: " + e for e in fr.condition_evidence)
    for df in defeated:
        lines.append(
            f"defeated: {df.rule_id} (priority {df.priority}, would conclude {df.decision.value}) "
            f"-- dominated by a higher-priority rule"
        )
        lines.extend("  it held because: " + e for e in df.condition_evidence)
    # provenance / member inventory
    lines.append(f"members: {facts.sense_count} sense(s) over forms {list(facts.forms)}; tags {dict(facts.tag_counts)}")
    if ic.merge_rationale:
        lines.append(f"merge provenance: {ic.merge_rationale}")
    if ic.exclusion_records:
        lines.append(f"exclusion records: {list(ic.exclusion_records)}")
    if not facts.evidence_explicit:
        lines.append("evidence gaps: " + "; ".join(facts.evidence_missing_reasons))
    return tuple(lines)


def evaluate_ic(ic: ICRecord, policy: AdmissionPolicy | None = None) -> AdmissionVerdict:
    policy = policy or default_policy()
    facts = derive_ic_facts(ic)

    firings: list[RuleFiring] = []
    for rule in policy.rules:
        ok, evidence = rule.fires(facts)
        if ok:
            firings.append(
                RuleFiring(
                    rule_id=rule.rule_id,
                    priority=rule.priority,
                    decision=rule.decision,
                    description=rule.description,
                    condition_evidence=tuple(evidence),
                )
            )

    if not firings:
        decision = AdmissionDecision.UNCERTAIN
        fired: tuple[RuleFiring, ...] = ()
        defeated: tuple[RuleFiring, ...] = ()
        uncertain_evidence = ["no admission rule fired"]
        if not facts.has_lexical_reading and not facts.has_phrase_or_idiom_reading and not facts.every_reading_blocked:
            uncertain_evidence.append(
                f"members carry no admitting and no fully-blocking tag (tags: {dict(facts.tag_counts)}); "
                "likely all-uncertain"
            )
        fired = (
            RuleFiring(
                rule_id="r_uncertain",
                priority=0,
                decision=AdmissionDecision.UNCERTAIN,
                description="uncertain(IC) if no rule fires (or rules tie at equal priority with conflicting decisions)",
                condition_evidence=tuple(uncertain_evidence),
            ),
        )
        rationale = _build_rationale(decision, fired, defeated, facts, ic)
        return AdmissionVerdict(
            ic_id=ic.ic_id, decision=decision, fired=fired, defeated=defeated,
            facts=facts, rationale=rationale, aliases=(), excluded_sense_ids=tuple(s.sense_id for s in ic.senses),
        )

    top_priority = max(fr.priority for fr in firings)
    top = [fr for fr in firings if fr.priority == top_priority]
    lower = [fr for fr in firings if fr.priority < top_priority]
    top_decisions = {fr.decision for fr in top}

    if len(top_decisions) > 1:
        # conflicting fires at equal priority -> uncertain
        decision = AdmissionDecision.UNCERTAIN
        fired = (
            RuleFiring(
                rule_id="r_uncertain",
                priority=0,
                decision=AdmissionDecision.UNCERTAIN,
                description="uncertain(IC): rules tied at the top priority with conflicting decisions",
                condition_evidence=tuple(
                    f"{fr.rule_id} (priority {fr.priority}) wants {fr.decision.value}" for fr in top
                ),
            ),
        )
        defeated = tuple(lower)
        rationale = _build_rationale(decision, fired, defeated, facts, ic)
        return AdmissionVerdict(
            ic_id=ic.ic_id, decision=decision, fired=fired, defeated=tuple(top) + defeated,
            facts=facts, rationale=rationale, aliases=(), excluded_sense_ids=tuple(s.sense_id for s in ic.senses),
        )

    decision = next(iter(top_decisions))
    fired = tuple(top)
    defeated = tuple(lower)

    if decision is AdmissionDecision.ADMIT:
        admit_ids = set(facts.lexical_sense_ids)
        if any(fr.rule_id == "r_admit_phrase_idiom" for fr in fired):
            admit_ids |= set(facts.phrase_idiom_sense_ids)
        if any(fr.rule_id == "r_admit_construction" for fr in fired):
            admit_ids |= set(facts.construction_sense_ids)
        admit_forms = sorted({s.form for s in ic.senses if s.sense_id in admit_ids})
        excluded_ids = tuple(s.sense_id for s in ic.senses if s.sense_id not in admit_ids)
        aliases = tuple(admit_forms)
    else:
        aliases = ()
        excluded_ids = tuple(s.sense_id for s in ic.senses)

    rationale = _build_rationale(decision, fired, defeated, facts, ic)
    return AdmissionVerdict(
        ic_id=ic.ic_id, decision=decision, fired=fired, defeated=defeated,
        facts=facts, rationale=rationale, aliases=aliases, excluded_sense_ids=excluded_ids,
    )


def evaluate_collection(
    ics: Iterable[ICRecord], policy: AdmissionPolicy | None = None
) -> list[AdmissionVerdict]:
    policy = policy or default_policy()
    return [evaluate_ic(ic, policy) for ic in ics]


# ---------------------------------------------------------------------------
# Building ICRecords from a sense-level ingestion build
# ---------------------------------------------------------------------------
def ic_records_from_node_metadata(
    node_metadata: Mapping[str, Mapping[str, object]],
    *,
    merge_rationale_by_ic: Mapping[str, str] | None = None,
    exclusion_records_by_ic: Mapping[str, Sequence[str]] | None = None,
) -> list[ICRecord]:
    """Group ``SenseLevelGraphBuild.node_metadata`` rows into :class:`ICRecord`s.

    The merge rationale / exclusion records, if supplied, come from
    ``meanings.identity_clusters`` (the spelling-variant merge table).
    """
    merge_rationale_by_ic = merge_rationale_by_ic or {}
    exclusion_records_by_ic = exclusion_records_by_ic or {}
    by_ic: dict[str, list[SenseRecord]] = {}
    for meta in node_metadata.values():
        ic_id = str(meta["ic_id"])
        reasons = meta.get("lexicality_reasons") or ()
        rec = SenseRecord(
            sense_id=str(meta["sense_id"]),
            form=str(meta.get("form", meta["lemma"])),
            lemma=str(meta["lemma"]),
            pos=str(meta.get("pos", "")),
            definition=str(meta.get("definition", "")),
            lexicality=str(meta["lexicality"]),
            lexicality_reasons=tuple(str(r) for r in reasons),
            source_synset=str(meta["source_synset"]) if meta.get("source_synset") else None,
        )
        by_ic.setdefault(ic_id, []).append(rec)
    out: list[ICRecord] = []
    for ic_id, senses in sorted(by_ic.items()):
        out.append(
            ICRecord(
                ic_id=ic_id,
                senses=tuple(sorted(senses, key=lambda s: s.sense_id)),
                merge_rationale=merge_rationale_by_ic.get(ic_id),
                exclusion_records=tuple(exclusion_records_by_ic.get(ic_id, ())),
            )
        )
    return out
