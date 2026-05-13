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
        # `s` is now whitelisted as the plural-marker / function-word reading;
        # the whitelist fires BEFORE the single-character rule, so even a
        # letter-of-the-alphabet gloss on the bare lemma `s` resolves to
        # lexical-word.  (The trained gloss classifier still tags `s::n` as
        # `symbol-code` when the gloss is "the 19th letter ..." and the lemma
        # is not whitelisted -- e.g. when wn returns it under a different form
        # -- which the head-to-head exercises.)
        "s": classify_lexicality("s", "n", "the 19th letter of the Roman alphabet").tag,
        # `e` / `g` are NOT on the whitelist (they are not English function
        # words), so single_character fires and they stay symbol-code.
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
        "s": LexicalityTag.LEXICAL_WORD,
        "e": LexicalityTag.SYMBOL_CODE,
        "g": LexicalityTag.SYMBOL_CODE,
        "ph": LexicalityTag.SYMBOL_CODE,
        "th": LexicalityTag.SYMBOL_CODE,
        "ax": LexicalityTag.LEXICAL_WORD,
        "axe": LexicalityTag.LEXICAL_WORD,
    }


# --- round-7 hole #1: whitelist fires before single_character/case rules ----

def test_whitelisted_single_character_lemmas_get_lexical_word() -> None:
    """`a` and `s` (whitelisted single-character function words) must resolve
    to `lexical-word` via the short-token whitelist, NOT to `symbol-code` via
    `surface.single_character`.  This is the round-7 hole #1 fix: the whitelist
    check must run BEFORE the single-character rule so genuine function words
    do not get stamped as symbol-codes and excluded by the admission policy.
    """
    a_result = classify_lexicality("a", "n", "the indefinite article")
    assert a_result.tag == LexicalityTag.LEXICAL_WORD
    assert a_result.reasons == ("surface.short_token_whitelist",)

    s_result = classify_lexicality("s", "n", "the plural marker suffix")
    assert s_result.tag == LexicalityTag.LEXICAL_WORD
    assert s_result.reasons == ("surface.short_token_whitelist",)

    # Non-whitelisted single chars still resolve to symbol-code.
    e_result = classify_lexicality("e", "n", "the 5th letter of the Roman alphabet")
    assert e_result.tag == LexicalityTag.SYMBOL_CODE
    assert e_result.reasons == ("surface.single_character",)


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
    # Single-char function words ARE whitelisted (round-7 hole #1).
    assert is_short_token_whitelisted("a")
    assert is_short_token_whitelisted("s")
    assert is_short_token_whitelisted("i")
    # Plain letters of the alphabet are NOT whitelisted -- they remain
    # symbol-code via the single-character rule.
    assert not is_short_token_whitelisted("e")
    assert not is_short_token_whitelisted("g")
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


def test_low_confidence_path_is_present() -> None:
    """The `trained.lowconf.*` path must remain reachable in principle: when
    the trained classifier's top probability falls below
    `_TRAINED_CONFIDENCE_THRESHOLD`, the verdict is `uncertain` (single-word
    lemma) or `phrase` (multiword lemma).  Round-7 hole #2/#3 narrowed the
    classifier's label space (removing technical-term/symbol-code/abbreviation,
    which the surface layer now owns end-to-end), which sharpens the softmax;
    real-data uncertain firings are rarer but the structural path remains.

    This test exercises the path by patching the threshold up to 1.0 so any
    gloss the trained classifier handles falls below it.
    """
    from meanings import lexicality as lex_mod

    saved = lex_mod._TRAINED_CONFIDENCE_THRESHOLD
    try:
        lex_mod._TRAINED_CONFIDENCE_THRESHOLD = 1.0  # nothing clears
        result = classify_lexicality("zibwop", "n", "characteristic of")
        # Single-word + no surface rule + below threshold -> uncertain.
        assert result.tag == LexicalityTag.UNCERTAIN
        assert result.reasons[0].startswith("trained.lowconf.")
    finally:
        lex_mod._TRAINED_CONFIDENCE_THRESHOLD = saved


# --- round-7 hole #2: technical-term is rule-gated -------------------------

def test_technical_domain_gloss_is_surface_technical_term() -> None:
    """A gloss with an explicit "in <domain>," or "(domain)" marker resolves to
    `technical-term` via the surface layer (round-7 hole #2 fix), NOT via the
    trained classifier (which no longer carries the class)."""
    r1 = classify_lexicality(
        "derivative", "n", "in mathematics, the rate of change of a function"
    )
    assert r1.tag == LexicalityTag.TECHNICAL_TERM
    assert r1.reasons == ("surface.technical_domain",)

    r2 = classify_lexicality(
        "vector", "n", "(physics) a quantity with both magnitude and direction"
    )
    assert r2.tag == LexicalityTag.TECHNICAL_TERM
    assert r2.reasons == ("surface.technical_domain",)


def test_mere_discipline_mention_does_not_fire_technical_term() -> None:
    """The technical-domain rule is high-precision: a gloss that merely mentions
    a discipline (without an "in <domain>," restrictor or "(domain)" tag) does
    NOT fire the rule."""
    r = classify_lexicality(
        "history", "n",
        "the study of past events including political and social developments",
    )
    assert r.tag != LexicalityTag.TECHNICAL_TERM


# --- round-7 hole #4: CONSTRUCTION tag for multi-token non-compositional ---

def test_multiword_idiomatic_gloss_is_construction() -> None:
    """A multiword lemma with an idiomatic-marker gloss routes to
    `CONSTRUCTION` via `surface.construction_idiomatic`, not `IDIOM`.  Round-7
    hole #4: construction is the proper category for "11_november",
    "bless_her_heart", and other multi-token non-compositional expressions.
    """
    r = classify_lexicality(
        "kick_the_bucket", "v", "an idiom meaning to die"
    )
    assert r.tag == LexicalityTag.CONSTRUCTION
    assert r.reasons == ("surface.construction_idiomatic",)


def test_single_word_interjection_gloss_stays_idiom() -> None:
    """Single-word interjection/exclamation glosses still tag IDIOM (the legacy
    tag, kept for single-word interjections like 'ouch', 'ahem').  Round-7
    hole #4 only re-routes multiword idiomatic glosses to CONSTRUCTION."""
    r = classify_lexicality(
        "ouch", "r", "used to express sudden pain"
    )
    assert r.tag == LexicalityTag.IDIOM
    assert r.reasons == ("surface.idiom",)


# --- round-7 hole #3: color/colour is lexical-word, not technical-term -----

def test_color_lemma_is_lexical_word_not_technical_term() -> None:
    """`color` (the OEWN noun) is an ordinary lexical word; its gloss has no
    technical-domain marker, so the surface rule does not fire, and the trained
    classifier (no longer carrying `technical-term`) tags it `lexical-word`.
    Round-7 hole #3."""
    r = classify_lexicality(
        "color",
        "n",
        "a visual attribute of things that results from the light they emit or transmit or reflect",
    )
    assert r.tag == LexicalityTag.LEXICAL_WORD
    _assert_has_path_trace(r)
    r2 = classify_lexicality(
        "colour",
        "n",
        "a visual attribute of things that results from the light they emit or transmit or reflect",
    )
    assert r2.tag == LexicalityTag.LEXICAL_WORD


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
