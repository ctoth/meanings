from dataclasses import replace
from pathlib import Path

import pytest

from meanings.admission import SenseRecord
from meanings.interpretation import (
    And, Interpretation, Not, Or, Predicate, Reference, erase_operators, evaluate,
)
from meanings.numeric_experiment import (
    BINDINGS, EVEN, NONNEGATIVE, ODD, POSITIVE, load_interpretations, run_experiment,
)

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "numeric-senses.json"


def entry(sense_id, expression):
    source = SenseRecord(sense_id, "test", "test", "a", "test-only source", "unclassified")
    return Interpretation(source, expression)


@pytest.mark.parametrize("a,b,and_result,or_result", [
    (True, True, True, True), (True, False, False, True),
    (True, None, None, True), (False, True, False, True),
    (False, False, False, False), (False, None, False, None),
    (None, True, None, True), (None, False, False, None),
    (None, None, None, None),
])
def test_partial_evidence_truth_tables(a, b, and_result, or_result):
    bindings = {"a": lambda value, parameter: a, "b": lambda value, parameter: b}
    senses = {"and": entry("and", And(Predicate("a", 0), Predicate("b", 0))),
              "or": entry("or", Or(Predicate("a", 0), Predicate("b", 0))),
              "not": entry("not", Not(Predicate("a", 0)))}
    assert evaluate("and", 0, senses, bindings) is and_result
    assert evaluate("or", 0, senses, bindings) is or_result
    assert evaluate("not", 0, senses, bindings) is (None if a is None else not a)


@pytest.mark.parametrize("value", [None, True, False, "2", 2.0, [], {}])
def test_out_of_domain_observations_remain_unknown(value):
    assert evaluate(EVEN, value, load_interpretations(FIXTURE), BINDINGS) is None


def test_missing_predicates_senses_cycles_and_mismatched_source_ids_remain_unknown():
    senses = {"a": entry("a", Reference("b")), "b": entry("b", Reference("a")),
              "missing": entry("missing", Predicate("unbound", 0)),
              "zero_divisor": entry("zero_divisor", Predicate("divisible_by", 0)),
              "wrong_id": entry("other_id", Predicate("equal_to", 0))}
    for sense_id in ["a", "b", "missing", "zero_divisor", "wrong_id", "absent"]:
        assert evaluate(sense_id, 0, senses, BINDINGS) is None


def test_numeric_source_records_and_sense_specific_reference_composition():
    senses = load_interpretations(FIXTURE)
    assert len(senses) == 5
    assert senses[ODD].source.definition == "not divisible by two"
    assert senses[ODD].expression == Not(Reference(EVEN))
    assert evaluate(ODD, -3, senses, BINDINGS) is True
    assert evaluate(ODD, 0, senses, BINDINGS) is False
    assert evaluate(NONNEGATIVE, 0, senses, BINDINGS) is True
    assert evaluate(NONNEGATIVE, -1, senses, BINDINGS) is False
    # Never substitute a shared surface form or another medical/photographic sense.
    assert evaluate("positive", 3, senses, BINDINGS) is None
    assert evaluate("oewn-positive__3.00.04..", 3, senses, BINDINGS) is None
    without_positive = {sid: item for sid, item in senses.items() if sid != POSITIVE}
    assert evaluate(NONNEGATIVE, 3, without_positive, BINDINGS) is None
    assert evaluate(NONNEGATIVE, 0, without_positive, BINDINGS) is True


def test_operator_control_keeps_source_glosses_but_changes_the_interpretation():
    senses = load_interpretations(FIXTURE)
    erased = {sid: replace(item, expression=erase_operators(item.expression))
              for sid, item in senses.items()}
    assert erased[ODD].source is senses[ODD].source
    assert erased[ODD].source.definition == "not divisible by two"
    assert isinstance(senses[ODD].expression, Not)
    assert evaluate(ODD, 3, erased, BINDINGS) is False
    assert evaluate(NONNEGATIVE, 0, erased, BINDINGS) is False


def test_exact_references_and_fixed_controls_on_disjoint_integer_ranges():
    report = run_experiment(load_interpretations(FIXTURE))
    assert report["exact_reference_check_passed"] is True
    for split, judgments, wrong_errors, erased_errors in [
        ("development", 105, 60, 32), ("held_out", 9900, 5940, 2970),
    ]:
        results = report["results"][split]
        assert results["correct"]["judgments"] == judgments
        assert results["correct"]["errors"] == 0
        assert results["wrong_binding"]["errors"] == wrong_errors
        assert results["operator_erasure"]["errors"] == erased_errors
        assert all(arm["unknown"] == 0 for arm in results.values())


def test_missing_grounding_cannot_pass_exact_reference_check_by_abstaining():
    senses = load_interpretations(FIXTURE)
    report = run_experiment({sid: item for sid, item in senses.items() if sid != POSITIVE})
    assert report["exact_reference_check_passed"] is False
    assert report["results"]["held_out"]["correct"]["unknown"] > 0
