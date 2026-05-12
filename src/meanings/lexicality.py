from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from meanings.normalize import normalize_lemma


class LexicalityTag(StrEnum):
    LEXICAL_WORD = "lexical-word"
    SYMBOL_CODE = "symbol-code"
    ABBREVIATION = "abbreviation"
    PROPER_NAME = "proper-name"
    TAXON = "taxon"
    CHEMICAL = "chemical"
    TECHNICAL_TERM = "technical-term"
    PHRASE = "phrase"
    IDIOM = "idiom"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True, slots=True)
class LexicalityClassification:
    tag: LexicalityTag
    reasons: tuple[str, ...]


CHEMICAL_KEYWORDS = (
    "chemical element",
    "chemical symbol",
    "atomic number",
    "radioactive metallic element",
    "metallic element",
    "element of the",
    "nobelium",
    "sulfur",
    "sulphur",
)

TAXON_KEYWORDS = (
    "taxonomic group",
    "taxonomic category",
    "genus of",
    "family of",
    "order of",
    "class of",
    "phylum of",
    "species of",
    "subspecies of",
)

TECHNICAL_KEYWORDS = (
    "computer science",
    "mathematics",
    "physics",
    "linguistics",
    "logic",
    "medicine",
    "law",
    "music",
    "grammar",
)

IDIOM_KEYWORDS = (
    "idiomatic",
    "idiom",
    "colloquial expression",
)

ABBREVIATION_RE = re.compile(r"\b(abbreviation|acronym|initialism|short for)\b", re.IGNORECASE)
CHEMICAL_FORMULA_RE = re.compile(r"\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+\b")


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _case_pattern(surface: str) -> str:
    letters = "".join(char for char in surface if char.isalpha())
    if not letters:
        return "uncased"
    if letters.islower():
        return "lower"
    if letters.isupper():
        return "upper"
    if letters[:1].isupper() and letters[1:].islower():
        return "title"
    return "mixed"


def classify_lexicality(
    lemma: str,
    pos: str,
    definition: str,
    *,
    source_surface: str | None = None,
    synset_id: str | None = None,
    examples: tuple[str, ...] = (),
) -> LexicalityClassification:
    """Classify a WordNet-style sense with conservative surface/gloss rules."""
    normalized = normalize_lemma(lemma)
    surface = source_surface or lemma
    gloss = " ".join((definition, " ".join(examples))).strip()
    reasons: list[str] = []
    token_length = len(normalized.replace("_", ""))
    case_pattern = _case_pattern(surface)

    if _contains_any(gloss, CHEMICAL_KEYWORDS) or CHEMICAL_FORMULA_RE.search(definition):
        reasons.append("gloss.chemical")
        return LexicalityClassification(LexicalityTag.CHEMICAL, tuple(reasons))

    if _contains_any(gloss, TAXON_KEYWORDS):
        reasons.append("gloss.taxon")
        return LexicalityClassification(LexicalityTag.TAXON, tuple(reasons))

    if ABBREVIATION_RE.search(gloss):
        reasons.append("gloss.abbreviation")
        return LexicalityClassification(LexicalityTag.ABBREVIATION, tuple(reasons))

    if case_pattern in {"upper", "mixed"} and token_length <= 5:
        reasons.append("surface.code_case")
        return LexicalityClassification(LexicalityTag.SYMBOL_CODE, tuple(reasons))

    if case_pattern == "title" and pos == "n":
        reasons.append("surface.titlecase_noun")
        return LexicalityClassification(LexicalityTag.PROPER_NAME, tuple(reasons))

    if _contains_any(gloss, IDIOM_KEYWORDS):
        reasons.append("gloss.idiom")
        return LexicalityClassification(LexicalityTag.IDIOM, tuple(reasons))

    if "_" in normalized:
        reasons.append("surface.multiword")
        return LexicalityClassification(LexicalityTag.PHRASE, tuple(reasons))

    if token_length == 1:
        reasons.append("surface.single_character")
        return LexicalityClassification(LexicalityTag.SYMBOL_CODE, tuple(reasons))

    if token_length <= 3 and pos == "n":
        reasons.append("surface.short_noun_unreviewed")
        return LexicalityClassification(LexicalityTag.UNCERTAIN, tuple(reasons))

    if _contains_any(gloss, TECHNICAL_KEYWORDS):
        reasons.append("gloss.technical_domain")
        return LexicalityClassification(LexicalityTag.TECHNICAL_TERM, tuple(reasons))

    if pos in {"a", "n", "r", "s", "v"}:
        reasons.append("pos.lexical")
        return LexicalityClassification(LexicalityTag.LEXICAL_WORD, tuple(reasons))

    reasons.append("fallback.uncertain")
    return LexicalityClassification(LexicalityTag.UNCERTAIN, tuple(reasons))


def classify_oewn_sense(word: object, synset: object) -> LexicalityClassification:
    lemma = word.lemma()
    pos = getattr(word, "pos", getattr(synset, "pos", ""))
    definition = synset.definition() or ""
    examples = tuple(synset.examples() or ()) if hasattr(synset, "examples") else ()
    synset_id = getattr(synset, "id", None)
    return classify_lexicality(
        lemma,
        pos,
        definition,
        source_surface=lemma,
        synset_id=synset_id,
        examples=examples,
    )
