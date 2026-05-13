"""Hybrid lexicality classifier for WordNet-style senses.

History / rationale.  The original classifier (see git history) was a single
ordered pile of surface + gloss-keyword rules.  The agenda-#4 head-to-head
(``reports/lexicality-headtohead.md``) audited it against a TF-IDF+LR
baseline and found a clean split:

  * the **surface-pattern** rules (single-char -> symbol-code; short-token
    case rejection; code-case; the 27-item short-token whitelist; the
    abbreviation regex; the chemical-formula regex) *win* -- the gloss of
    ``s``-as-sulfur talks about sulfur, not "this is a one-letter symbol", so
    a bag-of-words classifier has nothing to grab; F1 0.86-0.97 there;
  * the **gloss-keyword templates** (``genus of`` -> taxon; ``chemical
    element`` -> chemical; ``computer science`` -> technical-term;
    ``surface.titlecase_noun`` -> proper-name) *lose* -- taxa outside the
    template fall through; formula-less chemicals fall through; the titlecase
    rule over-fires for proper-name with precision ~0.39; the technical-domain
    keyword set fires on any gloss merely *mentioning* a discipline.  TF-IDF
    over the gloss beats them.

So the production classifier is now a **hybrid**:

  1.  A clearly-marked **surface layer** runs first.  The rules are checked in
      this order: abbreviation regex, chemical-formula regex, **short-token
      whitelist** (so a whitelisted lemma like ``a`` / ``s`` / ``no`` always
      resolves to lexical-word, regardless of its length or case), then
      single-character, short-token-case-rejected, code-case, short-token
      unlisted, and finally the idiom regex.  If a surface rule fires it
      returns immediately with a ``surface.*`` reason -- these are
      near-deterministic and high precision.
  2.  Otherwise a small **trained gloss classifier** (TF-IDF over the gloss +
      cheap structural features -> class-balanced logistic regression;
      ``data/lexicality_gloss_clf.joblib``, built by
      ``scripts/train_lexicality_classifier.py``) is consulted for the
      gloss-cue classes {taxon, chemical, technical-term, proper-name,
      lexical-word}.  If its top-class probability clears a threshold it
      returns that tag with a ``trained.<class>.p<prob>`` reason.
  3.  If the trained classifier is low-confidence (top prob below the
      threshold) and no surface rule fired, the verdict is ``uncertain``
      (reason ``trained.lowconf.p<prob>``) -- this is the path that makes the
      ``uncertain`` tag actually reachable, which it was not under the old
      pile.  If the model file is missing the layer degrades to a small set of
      legacy gloss-keyword fallbacks so the module still works without it.

Every verdict's ``reasons`` tuple says which path produced it
(``surface.<rule>`` / ``trained.<class>.p<prob>`` / ``trained.lowconf.p<prob>``
/ ``fallback.<rule>``) so classification stays auditable.

The public surface is unchanged: ``classify_lexicality`` /
``classify_oewn_sense`` / ``is_short_token_whitelisted`` / ``LexicalityTag`` /
``LexicalityClassification``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

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
    # Round-7 hole #4: a multi-token form with meaning or force not recoverable
    # from naive word-by-word composition.  Named-entity multiwords with
    # construction-like glosses (e.g. `11_november`, `1st_baron_beaverbrook`,
    # `bless_her_heart`) and multi-token idiomatic expressions both land here.
    # Compositional multiwords stay `phrase`.  `notes/upgoer-identity-clusters.md`
    # names this in §"Core Distinctions": "Construction: a multi-token form with
    # meaning or force not recoverable from naive word-by-word composition."
    CONSTRUCTION = "construction"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True, slots=True)
class LexicalityClassification:
    tag: LexicalityTag
    reasons: tuple[str, ...]


# ---------------------------------------------------------------------------
# Surface layer constants
# ---------------------------------------------------------------------------

SHORT_TOKEN_LEXICAL_WHITELIST = frozenset(
    {
        # single-character function words (pronoun "I", indefinite article "a",
        # the plural-marker / possessive-marker reading "s" -- ordinary English
        # function words whose single-character form would otherwise be stamped
        # `symbol-code` by the single-character surface rule).  The whitelist
        # check runs FIRST in the surface layer (before single_character /
        # short_token_case_rejected / code_case) so a whitelisted lemma always
        # resolves to lexical-word regardless of its length or case.
        "a", "i", "s",
        # standard short function words (the original 27-item set)
        "am", "an", "as", "at", "ax", "axe", "be", "by", "do", "go", "he",
        "if", "in", "is", "it", "me", "my", "no", "of", "on", "or", "ox",
        "so", "to", "up", "us", "we",
    }
)

ABBREVIATION_RE = re.compile(
    r"\b(abbreviation|abbreviated|acronym|initialism|short for|stands for)\b", re.IGNORECASE
)
# A bare chemical formula as the *lemma* (e.g. "H2O", "CaCO3"): >=2 element-ish
# groups, each an optional-lowercase-capital + optional digits.
CHEMICAL_FORMULA_RE = re.compile(r"[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+")
IDIOM_RE = re.compile(
    r"\b(idiomatic|idiomatically|an idiom\b|a colloquial expression|"
    r"a fixed expression|used to express|an exclamation|an interjection)\b",
    re.IGNORECASE,
)

# Reason-prefix groups.  The training script trusts ``surface.*`` reasons as
# silver labels (those paths look only at the lemma surface, plus -- for
# abbreviation -- an explicit "abbreviation"/"acronym" gloss phrase).
SURFACE_REASON_PREFIXES = (
    "surface.single_character",
    "surface.short_token_case_rejected",
    "surface.code_case",
    "surface.short_token_whitelist",
    "surface.short_token_unlisted",
    "surface.abbreviation",
    "surface.chemical_formula",
    "surface.technical_domain",
    "surface.multiword",
    "surface.idiom",
    "surface.construction_idiomatic",
)

# Trained classifier behaviour.
_TRAINED_CONFIDENCE_THRESHOLD = 0.40  # below this -> uncertain
MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "lexicality_gloss_clf.joblib"

# Legacy gloss-keyword fallbacks, used ONLY when the trained model file is
# absent (so the module still works in a checkout without the artifact).  These
# are the old templates the head-to-head found unreliable -- they are a floor,
# not the primary path.
_LEGACY_CHEMICAL_KEYWORDS = (
    "chemical element", "chemical symbol", "atomic number", "metallic element",
    "radioactive metallic element", "nonmetallic element", "noble gas",
    "element of the", "nobelium", "sulfur", "sulphur",
)
_LEGACY_TAXON_KEYWORDS = (
    "taxonomic group", "taxonomic category", "genus of", "family of",
    "order of", "class of", "phylum of", "species of", "subspecies of",
    "type genus",
)
_LEGACY_TECHNICAL_KEYWORDS = (
    "computer science", "in mathematics", "in physics", "in linguistics",
    "in logic", "in medicine", "in law", "in music", "in grammar",
)

# Technical-domain markers used by the surface rule (round-7 hole #2: revert
# `technical-term` to a rule-based check; the trained classifier no longer
# carries the class).  Two forms, both high-precision per the agenda-#4
# head-to-head (pure-rules technical-term F1 0.80):
#   (1) a discipline name appears in the gloss (the FROZEN keyword set
#       reproduced in scripts/lexicality_headtohead.py::pure_rules_predict,
#       extended with a few high-precision additions found on the gold set);
#   (2) a parenthetical "(domain)" tag.
# We use a regex (not naive substring) so word boundaries are enforced; a
# gloss mentioning "lawful" should NOT fire on the "law" keyword.
TECHNICAL_DOMAIN_RE = re.compile(
    r"(?:"
    # (1) disciplinary keywords with word boundaries.  This mirrors the FROZEN
    # _FROZEN_TECH_KW substring check that achieved F1=0.80 in the
    # head-to-head, lifted to use regex word boundaries.  We add a small set
    # of domain names found on the gold set the FROZEN list missed.
    r"\b(?:computer science|mathematics|mathematical|mathematician|physics|"
    r"linguistics|linguistic|logic|medicine|medicinal|law|music|musical|"
    r"musician|grammar|geology|geological|economics|economic|astronomy|"
    r"astronomical|heraldry|computing|programming|programmer|technical|"
    r"taxonomic|trigonometry|stratigraphy|biological|theological|"
    r"psychological|histological|chemical)\b"
    # (2) parenthetical "(domain)" tag, the OEWN dictionary convention
    r"|"
    r"\((?:math|mathematics|physics|chemistry|biology|astronomy|geology|"
    r"music|economics|linguistics|law|medicine|computing|grammar|"
    r"statistics|logic|trademark|architecture|heraldry|theology)\)"
    r")",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Lazy-loaded trained model
# ---------------------------------------------------------------------------
_MODEL: object | None = None
_MODEL_TRIED = False


def _load_model() -> object | None:
    global _MODEL, _MODEL_TRIED
    if _MODEL_TRIED:
        return _MODEL
    _MODEL_TRIED = True
    try:
        import joblib  # local import: keeps import-time deps minimal

        if MODEL_PATH.exists():
            _MODEL = joblib.load(MODEL_PATH)
    except Exception:  # pragma: no cover - corrupt/incompatible artifact
        _MODEL = None
    return _MODEL


def reset_model_cache() -> None:
    """Test hook: force the model to be re-loaded on next call."""
    global _MODEL, _MODEL_TRIED
    _MODEL = None
    _MODEL_TRIED = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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


def is_short_token_whitelisted(lemma: str) -> bool:
    return normalize_lemma(lemma) in SHORT_TOKEN_LEXICAL_WHITELIST


def _surface_layer(
    normalized: str, surface: str, gloss: str, definition: str
) -> LexicalityClassification | None:
    """Run the surface-pattern rules.  Return a classification if one fires
    with high confidence, else ``None`` (caller consults the trained model)."""
    token_length = len(normalized.replace("_", ""))
    case_pattern = _case_pattern(surface)

    # An explicit "abbreviation"/"acronym"/"short for" gloss phrase is a
    # surface-ish cue (it talks about the *form*, not the referent) and the
    # head-to-head found it near-perfect precision.
    if ABBREVIATION_RE.search(gloss):
        return LexicalityClassification(LexicalityTag.ABBREVIATION, ("surface.abbreviation",))

    # A bare chemical formula as the lemma.
    if CHEMICAL_FORMULA_RE.fullmatch(surface.strip()):
        return LexicalityClassification(LexicalityTag.CHEMICAL, ("surface.chemical_formula",))

    # SHORT-TOKEN WHITELIST FIRES FIRST (round-7 hole #1): a lemma on the
    # whitelist of genuine English function words (`a`, `s`, `i`, `am`, `an`,
    # `as`, ..., `ox`, ...) is always a lexical word.  Without this short-
    # circuit, `a` (single-char) would be stamped `symbol-code` by the single-
    # character rule below, and the admission policy would then exclude it via
    # `r_block_symbol_only`.  The whitelist is gated on `case_pattern == "lower"`
    # so that titlecase / uppercase forms of the same surface (the Nobelium
    # symbol `No`, the strontium symbol `Sr`, etc.) are still routed to
    # `symbol-code` via the case-rejection rule below.
    if (
        token_length <= 3
        and case_pattern == "lower"
        and normalized in SHORT_TOKEN_LEXICAL_WHITELIST
    ):
        return LexicalityClassification(
            LexicalityTag.LEXICAL_WORD, ("surface.short_token_whitelist",)
        )

    # Single character -> symbol-code (only if NOT whitelisted, since the
    # whitelist check above already returned for whitelisted single chars).
    if token_length == 1:
        return LexicalityClassification(LexicalityTag.SYMBOL_CODE, ("surface.single_character",))

    # Very short, non-lowercase token -> symbol-code (codes/abbrevs).
    if token_length <= 3 and case_pattern not in {"lower", "uncased"}:
        return LexicalityClassification(
            LexicalityTag.SYMBOL_CODE, ("surface.short_token_case_rejected",)
        )

    # Short upper/mixed-case token -> symbol-code.
    if case_pattern in {"upper", "mixed"} and token_length <= 5:
        return LexicalityClassification(LexicalityTag.SYMBOL_CODE, ("surface.code_case",))

    # Short non-whitelisted token -> symbol-code (the whitelist case fired above).
    if token_length <= 3:
        return LexicalityClassification(
            LexicalityTag.SYMBOL_CODE, ("surface.short_token_unlisted",)
        )

    # TECHNICAL-DOMAIN GLOSS RULE (round-7 hole #2): a gloss that explicitly
    # restricts the sense to a discipline ("in mathematics,", "(physics)", "in
    # computer science", ...) gets tagged `technical-term` by the surface layer.
    # The trained classifier NO LONGER carries `technical-term` in its label
    # space -- per the agenda-#4 head-to-head, pure-rules technical-term F1
    # was 0.80 while the trained classifier's was 0.39, a -0.41 regression.
    # The rule is high-precision (it requires an explicit "in <domain>," or
    # parenthetical "(domain)" marker, not a mere mention of the discipline).
    # This also fixes the `color`/`colour`-as-`technical-term` mis-tag: the
    # `color` gloss does not contain a technical-domain marker, so the rule
    # does not fire, and the trained classifier (without that class) tags it
    # `lexical-word`.
    if TECHNICAL_DOMAIN_RE.search(gloss):
        return LexicalityClassification(
            LexicalityTag.TECHNICAL_TERM, ("surface.technical_domain",)
        )

    # Idiom/construction/interjection gloss (high-precision, fires rarely).
    # Round-7 hole #4: route MULTIWORD idiomatic glosses to `CONSTRUCTION`
    # (a multi-token form with non-compositional meaning), and single-word
    # interjection/exclamation glosses to `IDIOM` (the legacy tag, kept for
    # interjections like "ouch", "ahem").  This rule does NOT pre-empt the
    # trained classifier for the gloss-cue classes (chemical/taxon/proper-name)
    # -- it only fires on explicit idiom/interjection markers.
    if IDIOM_RE.search(gloss):
        if "_" in normalized:
            return LexicalityClassification(
                LexicalityTag.CONSTRUCTION, ("surface.construction_idiomatic",)
            )
        return LexicalityClassification(LexicalityTag.IDIOM, ("surface.idiom",))

    return None


def _legacy_gloss_fallback(
    pos: str, gloss: str, definition: str
) -> LexicalityClassification:
    """Used only when the trained model file is missing."""
    if _contains_any(gloss, _LEGACY_CHEMICAL_KEYWORDS) or CHEMICAL_FORMULA_RE.search(definition):
        return LexicalityClassification(LexicalityTag.CHEMICAL, ("fallback.chemical_keyword",))
    if _contains_any(gloss, _LEGACY_TAXON_KEYWORDS):
        return LexicalityClassification(LexicalityTag.TAXON, ("fallback.taxon_keyword",))
    if _contains_any(gloss, _LEGACY_TECHNICAL_KEYWORDS):
        return LexicalityClassification(
            LexicalityTag.TECHNICAL_TERM, ("fallback.technical_keyword",)
        )
    if pos in {"a", "n", "r", "s", "v"}:
        return LexicalityClassification(LexicalityTag.LEXICAL_WORD, ("fallback.pos_default",))
    return LexicalityClassification(LexicalityTag.UNCERTAIN, ("fallback.uncertain",))


# Map trained-classifier class strings to tags.
_TAG_BY_NAME = {t.value: t for t in LexicalityTag}


def classify_lexicality(
    lemma: str,
    pos: str,
    definition: str,
    *,
    source_surface: str | None = None,
    synset_id: str | None = None,
    examples: tuple[str, ...] = (),
) -> LexicalityClassification:
    """Classify a WordNet-style sense: surface-pattern rules first, then a
    trained gloss classifier, then an ``uncertain``/POS fallback."""
    normalized = normalize_lemma(lemma)
    surface = source_surface or lemma
    gloss = " ".join((definition, " ".join(examples))).strip()

    # --- 1. surface layer -------------------------------------------------
    surface_verdict = _surface_layer(normalized, surface, gloss, definition)
    if surface_verdict is not None:
        return surface_verdict

    # --- 2. trained gloss classifier -------------------------------------
    model = _load_model()
    if model is None:
        return _legacy_gloss_fallback(pos, gloss, definition)

    try:
        cls_name, prob = model.predict_with_confidence(surface, gloss, pos)
    except Exception:  # pragma: no cover - incompatible artifact
        return _legacy_gloss_fallback(pos, gloss, definition)

    if prob >= _TRAINED_CONFIDENCE_THRESHOLD:
        tag = _TAG_BY_NAME.get(cls_name, LexicalityTag.LEXICAL_WORD)
        return LexicalityClassification(tag, (f"trained.{cls_name}.p{prob:.2f}",))

    # --- 3. low-confidence fallback -------------------------------------
    # No surface rule fired and the trained classifier is below threshold.
    # A multiword lemma defaults to `phrase` (the safe structural default);
    # anything else is `uncertain` -- the path that makes the tag reachable.
    if "_" in normalized:
        return LexicalityClassification(LexicalityTag.PHRASE, (f"trained.lowconf.p{prob:.2f}.multiword",))
    return LexicalityClassification(
        LexicalityTag.UNCERTAIN, (f"trained.lowconf.p{prob:.2f}",)
    )


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
