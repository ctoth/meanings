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

  1.  A clearly-marked **surface layer** runs first (single-char, short-token
      cases, code-case, abbreviation regex, chemical-formula regex, multiword
      -> phrase, idiom regex, short-token whitelist).  If a surface rule fires
      it returns immediately with a ``surface.*`` reason -- these are
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
    "surface.multiword",
    "surface.idiom",
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

    # Single character -> symbol-code.
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

    # Short token: explicit whitelist -> lexical-word, else symbol-code.
    if token_length <= 3:
        if normalized in SHORT_TOKEN_LEXICAL_WHITELIST:
            return LexicalityClassification(
                LexicalityTag.LEXICAL_WORD, ("surface.short_token_whitelist",)
            )
        return LexicalityClassification(
            LexicalityTag.SYMBOL_CODE, ("surface.short_token_unlisted",)
        )

    # Idiom/interjection gloss (high-precision, fires rarely).  Note: `idiom`
    # is NOT in the trained model's label space, so this rule is how an idiom
    # gets tagged at all -- but it does NOT pre-empt the trained classifier for
    # the gloss-cue classes (chemical/taxon/proper-name), it only fires on the
    # explicit idiom/interjection markers.  Multiword lemmas are NOT short-circuited
    # to `phrase` here -- the trained classifier handles phrase vs. multiword
    # chemical/taxon/proper-name (a Linnaean binomial like `Felis_catus` must
    # not be stamped `phrase` before the gloss is read).
    if IDIOM_RE.search(gloss):
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
