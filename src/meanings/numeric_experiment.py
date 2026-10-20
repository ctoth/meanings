"""Run the bounded numeric interpretation experiment; write JSON to stdout only.

Run from the repository root: python -m meanings.numeric_experiment
"""

from __future__ import annotations

import argparse
import json
import operator
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from meanings.admission import SenseRecord
from meanings.interpretation import (
    Bindings, Interpretation, Not, Or, Predicate, Reference, erase_operators, evaluate,
)

EVEN = "oewn-even__3.00.02.."
ODD = "oewn-odd__3.00.00.."
POSITIVE = "oewn-positive__5.00.00.plus.00"
NEGATIVE = "oewn-negative__5.00.00.minus.00"
NONNEGATIVE = "oewn-nonnegative__5.00.00.plus.00"

# Manually authored interpretations of the separate source fixture, not a parser.
# Substitution in odd's gloss is explicit: "divisible by two" references EVEN.
AUTHORED = {
    EVEN: Predicate("divisible_by", 2),
    ODD: Not(Reference(EVEN)),
    POSITIVE: Predicate("greater_than", 0),
    NEGATIVE: Predicate("less_than", 0),
    NONNEGATIVE: Or(Reference(POSITIVE), Predicate("equal_to", 0)),
}
BINDINGS: Bindings = {
    "divisible_by": lambda value, divisor: None if divisor == 0 else value % divisor == 0,
    "greater_than": operator.gt,
    "less_than": operator.lt,
    "equal_to": operator.eq,
}


def load_interpretations(path: Path) -> dict[str, Interpretation]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        row["sense_id"]: Interpretation(
            SenseRecord(**row, lexicality="unclassified"), AUTHORED[row["sense_id"]]
        )
        for row in payload["senses"]
    }


def reference_extensions() -> dict[str, frozenset[int]]:
    """Exact finite reference sets, built by enumeration rather than the bindings."""
    evens = frozenset(2 * k for k in range(-500, 501))
    return {
        EVEN: evens,
        ODD: frozenset(range(-1000, 1001)) - evens,
        POSITIVE: frozenset(range(1, 1001)),
        NEGATIVE: frozenset(range(-1000, 0)),
        NONNEGATIVE: frozenset(range(0, 1001)),
    }


def run_experiment(interpretations: Mapping[str, Interpretation]) -> dict[str, object]:
    references = reference_extensions()
    wrong = dict(BINDINGS)
    wrong["greater_than"], wrong["less_than"] = wrong["less_than"], wrong["greater_than"]
    erased = {key: replace(item, expression=erase_operators(item.expression))
              for key, item in interpretations.items()}
    arms = {"correct": (interpretations, BINDINGS),
            "wrong_binding": (interpretations, wrong),
            "operator_erasure": (erased, BINDINGS)}
    splits = {"development": range(-10, 11),
              "held_out": (*range(-1000, -10), *range(11, 1001))}
    results = {}
    for split, values in splits.items():
        results[split] = {}
        for arm, (senses, bindings) in arms.items():
            counts = {}
            for target, extension in references.items():
                predictions = [evaluate(target, value, senses, bindings) for value in values]
                counts[target] = {
                    "observations": len(values),
                    "errors": sum(answer is not None and answer != (value in extension)
                                  for value, answer in zip(values, predictions)),
                    "unknown": sum(answer is None for answer in predictions),
                }
            results[split][arm] = {
                "judgments": sum(c["observations"] for c in counts.values()),
                "errors": sum(c["errors"] for c in counts.values()),
                "unknown": sum(c["unknown"] for c in counts.values()),
                "by_sense": counts,
            }
    return {
        "claim": "Exact authored numeric semantics only; no intrinsic-grounding or English-parsing claim.",
        "exact_reference_check_passed": all(
            result["correct"]["errors"] == 0 and result["correct"]["unknown"] == 0
            for result in results.values()
        ),
        "domain": "Python integers excluding bool; finite reference universe -1000..1000",
        "split": "Development -10..10; held-out -1000..-11 and 11..1000; no fitting or tuning.",
        "controls": "Swap greater_than/less_than bindings only; erase NOT and replace OR with AND.",
        "interpretations": [{"sense_id": item.source.sense_id,
                             "source_gloss": item.source.definition,
                             "source_synset": item.source.source_synset,
                             "manually_authored_expression": repr(item.expression)}
                            for item in interpretations.values()],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--senses", type=Path, default=Path("data/numeric-senses.json"))
    args = parser.parse_args()
    report = run_experiment(load_interpretations(args.senses))
    print(json.dumps(report, indent=2))
    if not report["exact_reference_check_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
