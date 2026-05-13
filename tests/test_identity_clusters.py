from __future__ import annotations

import pytest

from meanings.identity_clusters import (
    GLOSS_GATE_THRESHOLD,
    HIGH_CONFIDENCE_SPELLING_VARIANTS,
    IdentityCluster,
    MergeRecord,
    ORIGINAL_REGRESSION_PAIRS,
    _is_code_like,
    build_identity_clusters,
    candidate_pairs,
    candidate_variants,
    gloss_similarity,
    identity_cluster_for_form,
    levenshtein,
    spelling_variant_index,
)


# ---------------------------------------------------------------------------
# Edit distance
# ---------------------------------------------------------------------------


def test_levenshtein_basic() -> None:
    assert levenshtein("color", "colour") == 1
    assert levenshtein("center", "centre") == 2
    assert levenshtein("kitten", "sitting") == 3
    assert levenshtein("abc", "abc") == 0
    assert levenshtein("abc", "abcd", cap=1) == 1
    # cap short-circuits without finishing the matrix
    assert levenshtein("abcdef", "uvwxyz", cap=2) == 3


# ---------------------------------------------------------------------------
# Orthographic rules / candidate detection
# ---------------------------------------------------------------------------


def test_orthographic_rules_fire() -> None:
    def others(lemma: str) -> set[str]:
        return {h.other for h in candidate_variants(lemma)}

    assert "colour" in others("color")
    assert "centre" in others("center")
    assert "organise" in others("organize")
    assert "analyse" in others("analyze")
    assert "catalogue" in others("catalog")
    assert "defense" in others("defence")
    assert "judgement" in others("judgment")
    assert "travelled" in others("traveled")
    assert "fetus" in others("foetus")
    # lexical pair list
    assert "gray" in others("grey")
    assert "axe" in others("ax")
    assert "plow" in others("plough")


def test_candidate_pairs_membership_and_edit_distance() -> None:
    lex = {
        "color",
        "colour",
        "center",
        "centre",
        "organize",
        "organise",
        "catalog",
        "catalogue",
        "traveled",
        "travelled",
        "foetus",
        "fetus",
        "colon",  # edit-distance neighbour of "color" -> candidate, rejected later by gloss gate
        "cloud",
        "clout",  # edit-distance candidate
        "zzzzz",  # in lexicon, no neighbour
    }
    pairs = candidate_pairs(lex)

    assert frozenset({"color", "colour"}) in pairs
    assert pairs[frozenset({"color", "colour"})] == ["spelling.or_our"]
    assert frozenset({"center", "centre"}) in pairs
    assert frozenset({"organize", "organise"}) in pairs
    assert frozenset({"catalog", "catalogue"}) in pairs
    assert frozenset({"traveled", "travelled"}) in pairs
    # generic edit-distance pass
    assert pairs[frozenset({"colon", "color"})] == ["edit-distance"]
    assert frozenset({"cloud", "clout"}) in pairs
    # both members must be in the lexicon: "behaviour" not present, so no pair
    assert not any("behaviour" in p for p in pairs)
    # rule tag wins over edit-distance when both fire
    assert "edit-distance" not in pairs[frozenset({"color", "colour"})]


def test_code_like_excluded() -> None:
    assert _is_code_like("lxviii")  # Roman numeral
    assert _is_code_like("clxxv")
    assert _is_code_like("kibit")  # IEC unit
    assert _is_code_like("mibyte")
    assert _is_code_like("brr")  # no vowel
    assert not _is_code_like("color")
    assert not _is_code_like("rhythm")  # 'y' counts as a vowel
    assert not _is_code_like("ax")
    # Roman numerals do not enter candidate pairs even with an edit-distance neighbour
    pairs = candidate_pairs({"lviii", "lxviii", "lxiii", "color", "colour"})
    assert not any(_is_code_like(f) for p in pairs for f in p)


# ---------------------------------------------------------------------------
# Gloss-similarity gate
# ---------------------------------------------------------------------------


def test_gloss_similarity_separates_real_variants_from_lookalikes() -> None:
    # near-identical glosses -> high Jaccard, above the gate
    s = gloss_similarity(
        "a visual attribute of things that results from the light they emit",
        "a visual attribute of things that results from the light they reflect",
    )
    assert s >= GLOSS_GATE_THRESHOLD

    # unrelated glosses for edit-distance look-alikes -> ~0, below the gate
    assert gloss_similarity(
        "the part of the large intestine between the cecum and the rectum",
        "a visual attribute of things that results from the light they emit",
    ) < GLOSS_GATE_THRESHOLD
    assert gloss_similarity(
        "to delay or postpone something to a later time",
        "to be unlike or dissimilar in nature or quality",
    ) < GLOSS_GATE_THRESHOLD

    # empty glosses
    assert gloss_similarity("", "anything at all") == 0.0


# ---------------------------------------------------------------------------
# build_identity_clusters over a small fake lexicon
# ---------------------------------------------------------------------------


class _FakeSynset:
    def __init__(self, pos: str, definition: str) -> None:
        self.pos = pos
        self._definition = definition

    def definition(self) -> str:
        return self._definition


class _FakeSense:
    def __init__(self, sid: str, synset: _FakeSynset) -> None:
        self.id = sid
        self._synset = synset

    def synset(self) -> _FakeSynset:
        return self._synset


class _FakeWord:
    def __init__(self, lemma: str, senses: list[_FakeSense]) -> None:
        self._lemma = lemma
        self._senses = senses

    def lemma(self) -> str:
        return self._lemma

    def senses(self) -> list[_FakeSense]:
        return self._senses


class _FakeLexicon:
    def __init__(self, words: list[_FakeWord]) -> None:
        self._words = words

    def lexicons(self):  # so the SQL fast-path is skipped (no .id), falls back to nav
        return []

    def words(self) -> list[_FakeWord]:
        return self._words


_COLOR_GLOSS = "a visual attribute of things that results from the light they emit or reflect"
_BAD_COLON_GLOSS = "the part of the large intestine between the cecum and the rectum"
_ORG_GLOSS = "to arrange or form into a coherent unity or functioning whole"


def _fake_lexicon() -> _FakeLexicon:
    return _FakeLexicon(
        [
            _FakeWord("color", [_FakeSense("s:color:1", _FakeSynset("n", _COLOR_GLOSS))]),
            _FakeWord("colour", [_FakeSense("s:colour:1", _FakeSynset("n", _COLOR_GLOSS))]),
            # an edit-distance look-alike of "color" whose gloss is unrelated -> must NOT merge
            _FakeWord("colon", [_FakeSense("s:colon:1", _FakeSynset("n", _BAD_COLON_GLOSS))]),
            _FakeWord("organize", [_FakeSense("s:organize:1", _FakeSynset("v", _ORG_GLOSS))]),
            _FakeWord("organise", [_FakeSense("s:organise:1", _FakeSynset("v", _ORG_GLOSS))]),
            # an isolated word
            _FakeWord("aardvark", [_FakeSense("s:aardvark:1", _FakeSynset("n", "a nocturnal mammal"))]),
        ]
    )


def test_build_identity_clusters_small() -> None:
    result = build_identity_clusters(_fake_lexicon())
    form_to_ic = result["form_to_ic"]

    # color & colour merge; organize & organise merge
    assert form_to_ic["color"] == form_to_ic["colour"]
    assert form_to_ic["organize"] == form_to_ic["organise"]
    assert form_to_ic["color"] != form_to_ic["organize"]
    # colon is an edit-distance candidate of color but the gloss gate rejects it
    assert "colon" not in form_to_ic
    # isolated word never gets an IC
    assert "aardvark" not in form_to_ic

    # the merge of color/colour is rejected for nothing and recorded with provenance
    clusters = {c.ic_id: c for c in result["clusters"]}
    color_ic = clusters[form_to_ic["color"]]
    assert isinstance(color_ic, IdentityCluster)
    assert color_ic.forms == {"color", "colour"}
    assert {"s:color:1", "s:colour:1"} <= color_ic.sense_ids
    assert len(color_ic.merge_records) == 1
    mr = color_ic.merge_records[0]
    assert isinstance(mr, MergeRecord)
    assert mr.contributing_forms == frozenset({"color", "colour"})
    assert mr.merged_sense_ids == frozenset({"s:color:1", "s:colour:1"})
    assert mr.rule_id == "spelling.or_our"
    assert mr.gloss_score >= GLOSS_GATE_THRESHOLD
    assert mr.pos == "n"

    # colon/color appears among the rejected candidates with a sub-threshold score
    rejected_pairs = {frozenset({f1, f2}) for (f1, f2, _, _) in result["rejected"]}
    assert frozenset({"colon", "color"}) in rejected_pairs

    # every form is kept -- merge, not canonicalization
    all_cluster_forms = {f for c in result["clusters"] for f in c.forms}
    assert {"color", "colour"} <= all_cluster_forms


# ---------------------------------------------------------------------------
# Regression: the original 7 hand-coded pairs must still merge.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("left,right", ORIGINAL_REGRESSION_PAIRS)
def test_original_regression_pairs_still_merge(left: str, right: str) -> None:
    rl = identity_cluster_for_form(left)
    rr = identity_cluster_for_form(right)
    assert rl is not None, f"{left} should be in an IC"
    assert rr is not None, f"{right} should be in an IC"
    assert rl.ic_id == rr.ic_id, f"{left} and {right} should share an IC"
    assert {left, right}.issubset(rl.forms)


def test_high_confidence_constant_matches_regression_pairs() -> None:
    pairs_from_const = {tuple(sorted(r.forms)) for r in HIGH_CONFIDENCE_SPELLING_VARIANTS}
    assert pairs_from_const == {tuple(sorted(p)) for p in ORIGINAL_REGRESSION_PAIRS}


# ---------------------------------------------------------------------------
# New pairs the procedure should catch (verified against the OEWN-built table).
# ---------------------------------------------------------------------------

_SHOULD_MERGE = [
    ("analyze", "analyse"),
    ("catalog", "catalogue"),
    ("defence", "defense"),
    ("foetus", "fetus"),
    ("judgment", "judgement"),
    ("traveled", "travelled"),
    ("encyclopaedia", "encyclopedia"),
    ("organisation", "organization"),  # -isation/-ization variant
    ("organise", "organize"),
    ("saber", "sabre"),
    ("polarise", "polarize"),
    ("aluminium", "aluminum"),
    ("metre", "meter"),
]


@pytest.mark.parametrize("left,right", _SHOULD_MERGE)
def test_new_pairs_merge(left: str, right: str) -> None:
    rl = identity_cluster_for_form(left)
    rr = identity_cluster_for_form(right)
    assert rl is not None and rr is not None, f"{left}/{right} should both be in an IC"
    assert rl.ic_id == rr.ic_id, f"{left} and {right} should share an IC ({rl.ic_id} vs {rr.ic_id})"


# Pairs that look alike (edit-distance / orthographic shape) but must NOT be merged
# because the gloss gate sees them denote different things -- the edit-distance
# false positives the gate is there to catch.
_SHOULD_NOT_MERGE = [
    ("colon", "color"),
    ("desert", "dessert"),
    ("affect", "effect"),
    ("loose", "lose"),
    ("then", "than"),
]


@pytest.mark.parametrize("left,right", _SHOULD_NOT_MERGE)
def test_lookalike_pairs_do_not_merge(left: str, right: str) -> None:
    rl = identity_cluster_for_form(left)
    rr = identity_cluster_for_form(right)
    # Either form may be in some unrelated IC, but they must not share one.
    if rl is not None and rr is not None:
        assert rl.ic_id != rr.ic_id, f"{left} and {right} must NOT share an IC"


# ---------------------------------------------------------------------------
# Runtime interface contract used by wordnet_pipeline.
# ---------------------------------------------------------------------------


def test_identity_cluster_for_form_interface() -> None:
    r = identity_cluster_for_form("color")
    assert r is not None
    assert r.ic_id.startswith("ic:")
    assert "color" in r.forms and "colour" in r.forms
    assert r.rationale  # non-empty
    assert isinstance(r.evidence, tuple)
    # normalization: hyphen/space/case folded
    assert identity_cluster_for_form("COLOR") is r or identity_cluster_for_form("COLOR").ic_id == r.ic_id
    # unknown form -> None
    assert identity_cluster_for_form("xqzptv_not_a_word") is None


def test_spelling_variant_index_is_form_keyed() -> None:
    from meanings.normalize import normalize_lemma

    index = spelling_variant_index()
    assert "color" in index and "colour" in index
    assert index["color"].ic_id == index["colour"].ic_id
    # every key is a normalized member form of the view it maps to
    for form, view in list(index.items())[:300]:
        assert form in {normalize_lemma(f) for f in view.forms}
