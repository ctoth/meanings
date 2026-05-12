from __future__ import annotations

from meanings.lexicality import LexicalityTag, classify_lexicality, is_short_token_whitelisted


def test_classifies_chemical_sense_before_short_token_rules() -> None:
    result = classify_lexicality("No", "n", "a radioactive metallic element with atomic number 102")

    assert result.tag == LexicalityTag.CHEMICAL
    assert result.reasons == ("gloss.chemical",)


def test_classifies_taxon_from_gloss() -> None:
    result = classify_lexicality("Abelia", "n", "genus of evergreen shrubs")

    assert result.tag == LexicalityTag.TAXON
    assert result.reasons == ("gloss.taxon",)


def test_classifies_abbreviation_from_gloss() -> None:
    result = classify_lexicality("etc", "r", "an abbreviation for et cetera")

    assert result.tag == LexicalityTag.ABBREVIATION
    assert result.reasons == ("gloss.abbreviation",)


def test_classifies_titlecase_noun_as_proper_name() -> None:
    result = classify_lexicality("Lincoln", "n", "16th President of the United States")

    assert result.tag == LexicalityTag.PROPER_NAME
    assert result.reasons == ("surface.titlecase_noun",)


def test_classifies_multiword_as_phrase() -> None:
    result = classify_lexicality("good_luck", "n", "an auspicious state resulting from favorable outcomes")

    assert result.tag == LexicalityTag.PHRASE
    assert result.reasons == ("surface.multiword",)


def test_classifies_ordinarily_lexical_word() -> None:
    result = classify_lexicality("water", "n", "binary compound that occurs at room temperature as a clear liquid")

    assert result.tag == LexicalityTag.LEXICAL_WORD
    assert result.reasons == ("pos.lexical",)


def test_short_token_verdicts_for_artifact_cases() -> None:
    verdicts = {
        "no": classify_lexicality("no", "r", "used to express negation").tag,
        "No": classify_lexicality("No", "n", "a written code label").tag,
        "no_nobelium": classify_lexicality("no", "n", "a radioactive metallic element; nobelium").tag,
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
        "no_nobelium": LexicalityTag.CHEMICAL,
        "s": LexicalityTag.SYMBOL_CODE,
        "e": LexicalityTag.SYMBOL_CODE,
        "g": LexicalityTag.SYMBOL_CODE,
        "ph": LexicalityTag.SYMBOL_CODE,
        "th": LexicalityTag.SYMBOL_CODE,
        "ax": LexicalityTag.LEXICAL_WORD,
        "axe": LexicalityTag.LEXICAL_WORD,
    }


def test_short_token_whitelist_is_small_and_explicit() -> None:
    assert is_short_token_whitelisted("no")
    assert is_short_token_whitelisted("ax")
    assert is_short_token_whitelisted("axe")
    assert not is_short_token_whitelisted("ph")
    assert not is_short_token_whitelisted("th")
