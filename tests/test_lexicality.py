from __future__ import annotations

from meanings.lexicality import (
    LexicalityTag,
    classify_lexicality,
    is_short_token_whitelisted,
)


def _assert_has_path_trace(result) -> None:
    """Every verdict must carry exactly one reason naming the path that
    produced it: surface.* / trained.* / fallback.*."""
    assert result.reasons, "classification must carry a non-empty path trace"
    assert all(
        r.startswith(("surface.", "trained.", "fallback."))
        for r in result.reasons
    ), result.reasons


# --- surface layer (deterministic, model-independent) ----------------------

def test_chemical_formula_lemma_is_surface_chemical() -> None:
    result = classify_lexicality("H2O", "n", "a clear liquid compound of hydrogen and oxygen")
    assert result.tag == LexicalityTag.CHEMICAL
    assert result.reasons == ("surface.chemical_formula",)


def test_abbreviation_gloss_is_surface_abbreviation() -> None:
    result = classify_lexicality("etc", "r", "an abbreviation for et cetera")
    assert result.tag == LexicalityTag.ABBREVIATION
    assert result.reasons == ("surface.abbreviation",)


def test_classifies_multiword_as_phrase() -> None:
    # Multiword lemmas are no longer short-circuited to `phrase` by the surface
    # layer (a Linnaean binomial must not be stamped `phrase` before its gloss
    # is read) -- the trained classifier decides phrase vs. multiword
    # chemical/taxon/proper-name.  A compositional multiword -> phrase.
    result = classify_lexicality(
        "good_luck", "n", "an auspicious state resulting from favorable outcomes"
    )
    assert result.tag == LexicalityTag.PHRASE
    _assert_has_path_trace(result)


def test_multiword_chemical_not_stamped_phrase() -> None:
    # `sodium_chloride` with a compound gloss must be `chemical`, not `phrase`
    # (the bug the surface-layer multiword short-circuit caused).
    result = classify_lexicality(
        "sodium_chloride", "n", "a white crystalline compound used as a food seasoning and preservative"
    )
    assert result.tag == LexicalityTag.CHEMICAL
    _assert_has_path_trace(result)


def test_short_token_verdicts_for_artifact_cases() -> None:
    verdicts = {
        "no": classify_lexicality("no", "r", "used to express negation").tag,
        "No": classify_lexicality("No", "n", "a written code label").tag,
        "no_nobelium": classify_lexicality(
            "no", "n", "a radioactive metallic element; nobelium"
        ).tag,
        "s": classify_lexicality("s", "n", "the 19th letter of the Roman alphabet").tag,
        "e": classify_lexicality("e", "n", "the 5th letter of the Roman alphabet").tag,
        "g": classify_lexicality("g", "n", "the 7th letter of the Roman alphabet").tag,
        "ph": classify_lexicality("ph", "n", "a scale of hydrogen ion concentration").tag,
        "th": classify_lexicality("th", "n", "a digraph used in English spelling").tag,
        "ax": classify_lexicality("ax", "n", "an edge tool with a heavy bladed head").tag,
        "axe": classify_lexicality("axe", "n", "an edge tool with a heavy bladed head").tag,
    }
    assert verdicts == {
        "no": LexicalityTag.LEXICAL_WORD,
        "No": LexicalityTag.SYMBOL_CODE,
        # "no" as Nobelium: the surface layer fires short-token-whitelist
        # ("no" is whitelisted) BEFORE any gloss inspection -> lexical-word.
        # (The dedicated test below pins the Nobelium gloss on a non-whitelisted
        # lemma to confirm the trained classifier catches formula-less chemicals.)
        "no_nobelium": LexicalityTag.LEXICAL_WORD,
        "s": LexicalityTag.SYMBOL_CODE,
        "e": LexicalityTag.SYMBOL_CODE,
        "g": LexicalityTag.SYMBOL_CODE,
        "ph": LexicalityTag.SYMBOL_CODE,
        "th": LexicalityTag.SYMBOL_CODE,
        "ax": LexicalityTag.LEXICAL_WORD,
        "axe": LexicalityTag.LEXICAL_WORD,
    }


def test_nobelium_full_name_is_chemical_via_trained_layer() -> None:
    # The synthesis's "no::n = Nobelium" case, but with the full lemma so the
    # short-token surface rules do not pre-empt the gloss-cue classifier.
    result = classify_lexicality(
        "nobelium", "n", "a radioactive transuranic element with atomic number 102"
    )
    assert result.tag == LexicalityTag.CHEMICAL
    _assert_has_path_trace(result)


def test_short_token_whitelist_is_small_and_explicit() -> None:
    assert is_short_token_whitelisted("no")
    assert is_short_token_whitelisted("ax")
    assert is_short_token_whitelisted("axe")
    assert not is_short_token_whitelisted("ph")
    assert not is_short_token_whitelisted("th")


# --- trained gloss-cue layer ----------------------------------------------

def test_taxon_outside_old_template_is_tagged_taxon() -> None:
    # "the type genus, comprising the maples" matches none of the old
    # `genus of`/`family of`/`order of`/... templates, so the pre-hybrid pile
    # fell through to `surface.titlecase_noun` -> proper-name.  The trained
    # gloss classifier picks up the taxonomic-rank signal -> taxon.
    result = classify_lexicality("Acer", "n", "the type genus, comprising the maples")
    assert result.tag == LexicalityTag.TAXON
    _assert_has_path_trace(result)
    assert result.reasons[0].startswith("trained.")


def test_formula_less_chemical_is_tagged_chemical() -> None:
    # No bare formula in the lemma, no literal "chemical element" / "chemical
    # symbol" in the gloss -> the old rules dropped it to lexical-word.  A
    # single-word lemma so the multiword->phrase surface rule does not pre-empt.
    result = classify_lexicality(
        "aspirin",
        "n",
        "a white crystalline compound derived from salicylic acid and used as an analgesic and antipyretic and to reduce inflammation",
    )
    assert result.tag == LexicalityTag.CHEMICAL
    _assert_has_path_trace(result)


def test_low_confidence_gloss_returns_uncertain() -> None:
    # A fragmentary gloss the trained classifier cannot place above the
    # confidence threshold, with no surface rule firing -> uncertain.  (The old
    # pile never reached `fallback.uncertain` on real OEWN data.)
    result = classify_lexicality("zibwop", "n", "characteristic of")
    assert result.tag == LexicalityTag.UNCERTAIN
    assert result.reasons[0].startswith("trained.lowconf.")


def test_every_verdict_carries_a_path_trace() -> None:
    for lemma, pos, gloss in [
        ("water", "n", "a clear tasteless odorless liquid"),
        ("run", "v", "move fast on foot"),
        ("Lincoln", "n", "16th President of the United States"),
        ("DNA", "n", "the nucleic acid that carries genetic information"),
        ("ox", "n", "an adult castrated bull"),
    ]:
        result = classify_lexicality(lemma, pos, gloss)
        _assert_has_path_trace(result)
