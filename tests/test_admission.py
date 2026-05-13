from __future__ import annotations

from meanings.admission import (
    AdmissionDecision,
    ICRecord,
    SenseRecord,
    default_policy,
    derive_ic_facts,
    evaluate_ic,
    ic_records_from_node_metadata,
)


def _sense(sense_id, lemma, lex, reasons, *, form=None, pos="n", definition="a gloss with some words"):
    return SenseRecord(
        sense_id=sense_id,
        form=form or lemma,
        lemma=lemma,
        pos=pos,
        definition=definition,
        lexicality=lex,
        lexicality_reasons=tuple(reasons),
        source_synset=f"{sense_id}-syn",
    )


def test_clean_lexical_ic_admitted():
    ic = ICRecord(
        ic_id="ic:dog",
        senses=(
            _sense("dog%1", "dog", "lexical-word", ("trained.lexical-word.p0.91",)),
            _sense("dog%2", "dog", "lexical-word", ("trained.lexical-word.p0.77",), pos="v"),
        ),
        merge_rationale="single clean form; no merge",
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.ADMIT
    assert {f.rule_id for f in v.fired} == {"r_admit_lexical"}
    assert v.aliases == ("dog",)
    assert v.rationale  # populated
    assert any("fired: r_admit_lexical" in line for line in v.rationale)


def test_symbol_code_only_ic_excluded():
    ic = ICRecord(
        ic_id="ic:zz",
        senses=(
            _sense("zz%1", "zz", "symbol-code", ("surface.short_token_unlisted",)),
            _sense("zz%2", "zz", "abbreviation", ("surface.abbreviation",)),
        ),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.EXCLUDE
    assert "r_block_symbol_only" in {f.rule_id for f in v.fired}
    assert v.aliases == ()


def test_lexical_reading_hinging_on_low_precision_call_blocked():
    # The IC's only lexical-word reading is a shaky classifier call: a
    # low-precision class (proper-name, P~0.39) is implicated in how it got
    # tagged, and there is no surface-rule-backed lexical reading to fall back on.
    # -> r_block_sense_mismatch fires -> exclude (never a clean admit).
    ic = ICRecord(
        ic_id="ic:borderline",
        senses=(
            _sense("b%1", "borderline", "proper-name", ("trained.proper-name.p0.41",)),
            _sense("b%2", "borderline", "lexical-word",
                   ("trained.lexical-word.p0.42", "rerouted-from.proper-name")),
        ),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.EXCLUDE
    assert "r_block_sense_mismatch" in {f.rule_id for f in v.fired}


def test_lexical_reading_with_one_solid_call_still_admitted():
    # Same IC but the lexical-word reading also has a *solid* (surface-rule)
    # backing alongside the shaky one -> not a sense-mismatch -> admitted.
    ic = ICRecord(
        ic_id="ic:borderline2",
        senses=(
            _sense("b%1", "borderline2", "proper-name", ("trained.proper-name.p0.41",)),
            _sense("b%2", "borderline2", "lexical-word", ("trained.lexical-word.p0.42", "rerouted-from.proper-name")),
            _sense("b%3", "borderline2", "lexical-word", ("surface.short_token_whitelist",)),
        ),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.ADMIT


def test_missing_evidence_quarantined():
    ic = ICRecord(
        ic_id="ic:nogloss",
        senses=(
            _sense("ng%1", "nogloss", "lexical-word", ("surface.short_token_whitelist",), definition=""),
        ),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.QUARANTINE
    assert "r_quarantine_low_conf" in {f.rule_id for f in v.fired}


def test_no_resolves_to_admitted_negation():
    # 'no': the negation reading (lexical via the short-token whitelist) plus the
    # Nobelium reading (symbol-code via the short-token case rejection). The IC
    # is admitted, aliases = the forms expressing the admitted (negation) reading,
    # the Nobelium sense is excluded.
    ic = ICRecord(
        ic_id="ic:no",
        senses=(
            _sense("no%1::r", "no", "lexical-word", ("surface.short_token_whitelist",), pos="r",
                   definition="used to express negation, denial, or refusal"),
            _sense("No%1::n", "no", "symbol-code", ("surface.short_token_case_rejected",), form="No", pos="n",
                   definition="a radioactive metallic transuranic element; nobelium"),
        ),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.ADMIT
    assert v.aliases == ("no",)
    assert "No%1::n" in v.excluded_sense_ids or "no%1::r" not in v.excluded_sense_ids
    assert v.excluded_sense_ids == ("No%1::n",)


def test_all_uncertain_ic_is_uncertain():
    ic = ICRecord(
        ic_id="ic:huh",
        senses=(_sense("huh%1", "huh", "uncertain", ("trained.lowconf.p0.22",)),),
    )
    v = evaluate_ic(ic)
    assert v.decision is AdmissionDecision.UNCERTAIN
    assert "r_uncertain" in {f.rule_id for f in v.fired}


def test_construction_admitted_only_under_expanded_policy():
    # Round-7 hole #4: a multiword construction IC is admitted only when the
    # expanded policy is enabled (r_admit_construction), and yields the
    # multi-token form as an alias.
    ic = ICRecord(
        ic_id="ic:bless_her_heart",
        senses=(
            _sense(
                "bhh%1", "bless_her_heart", "construction",
                ("surface.construction_idiomatic",), pos="v",
                definition="an idiomatic Southern American expression of sympathy or condescension",
            ),
        ),
    )
    strict = evaluate_ic(ic, default_policy(admit_phrases_and_idioms=False))
    # strict: r_admit_construction disabled, no other rule fires -> uncertain
    assert strict.decision is AdmissionDecision.UNCERTAIN
    expanded = evaluate_ic(ic, default_policy(admit_phrases_and_idioms=True))
    assert expanded.decision is AdmissionDecision.ADMIT
    assert "r_admit_construction" in {f.rule_id for f in expanded.fired}
    assert expanded.aliases == ("bless_her_heart",)


def test_construction_admission_facts_track_construction_senses():
    # derive_ic_facts surfaces the construction reading on `ICFacts`.
    ic = ICRecord(
        ic_id="ic:ic_const",
        senses=(
            _sense("c%1", "11_november", "construction",
                   ("surface.construction_idiomatic",), pos="n",
                   definition="(an idiomatic / non-compositional date expression)"),
        ),
    )
    from meanings.admission import derive_ic_facts
    facts = derive_ic_facts(ic)
    assert facts.has_construction_reading
    assert facts.construction_sense_ids == ("c%1",)
    # construction is NOT in the symbol-only set, so the IC is not blocked.
    assert not facts.every_reading_blocked


def test_phrase_idiom_admitted_only_when_toggled():
    ic = ICRecord(
        ic_id="ic:kick_the_bucket",
        senses=(_sense("ktb%1", "kick_the_bucket", "idiom", ("surface.idiom",), pos="v",
                       definition="an idiom meaning to die"),),
    )
    strict = evaluate_ic(ic, default_policy(admit_phrases_and_idioms=False))
    # under the strict policy: no admitting tag fires (idiom rule disabled),
    # block_symbol_only does not fire (idiom is not a blocked tag), nothing fires
    # -> uncertain.
    assert strict.decision is AdmissionDecision.UNCERTAIN
    expanded = evaluate_ic(ic, default_policy(admit_phrases_and_idioms=True))
    assert expanded.decision is AdmissionDecision.ADMIT
    assert expanded.aliases == ("kick_the_bucket",)


def test_derive_facts_and_node_metadata_roundtrip():
    node_metadata = {
        "no%1::r": {
            "sense_id": "no%1::r", "source_synset": "syn-1", "lemma": "no", "form": "no",
            "pos": "r", "definition": "used to express negation",
            "lexicality": "lexical-word", "lexicality_reasons": ["surface.short_token_whitelist"],
            "ic_id": "ic:no",
        },
        "No%1::n": {
            "sense_id": "No%1::n", "source_synset": "syn-2", "lemma": "no", "form": "No",
            "pos": "n", "definition": "nobelium",
            "lexicality": "symbol-code", "lexicality_reasons": ["surface.short_token_case_rejected"],
            "ic_id": "ic:no",
        },
    }
    ics = ic_records_from_node_metadata(node_metadata)
    assert len(ics) == 1
    facts = derive_ic_facts(ics[0])
    assert facts.has_lexical_reading
    assert not facts.every_reading_blocked
    assert "no" in facts.forms and "No" in facts.forms
    v = evaluate_ic(ics[0])
    assert v.decision is AdmissionDecision.ADMIT
