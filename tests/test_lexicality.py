from __future__ import annotations

from meanings.lexicality import LexicalityTag, classify_lexicality


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
