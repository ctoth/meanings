"""Explicit, manually authored interpretations; never a natural-language parser."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from meanings.admission import SenseRecord

type Truth = bool | None
type Bindings = Mapping[str, Callable[[int, int], Truth]]


@dataclass(frozen=True)
class Predicate:
    name: str
    parameter: int


@dataclass(frozen=True)
class Reference:
    sense_id: str


@dataclass(frozen=True)
class And:
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Or:
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Not:
    child: Expression


type Expression = Predicate | Reference | And | Or | Not


@dataclass(frozen=True)
class Interpretation:
    """Retain the dictionary record separately from its authored expression."""

    source: SenseRecord
    expression: Expression


def evaluate(
    sense_id: str,
    value: object,
    interpretations: Mapping[str, Interpretation],
    bindings: Bindings,
) -> Truth:
    """Interpret an integer; None means missing, cyclic or out-of-domain evidence.

    Boolean operators use strong Kleene truth tables: False AND unknown is False,
    True OR unknown is True, and NOT unknown remains unknown. No IC projection or
    lemma fallback is performed. The source definition is retained, not parsed.
    """
    if type(value) is not int:  # bool is an int subclass, not an integer observation
        return None

    def resolve(target: str, active: frozenset[str]) -> Truth:
        entry = interpretations.get(target)
        if entry is None or target in active or entry.source.sense_id != target:
            return None
        return visit(entry.expression, active | {target})

    def visit(expr: Expression, active: frozenset[str]) -> Truth:
        match expr:
            case Predicate(name, parameter):
                predicate = bindings.get(name)
                return None if predicate is None else predicate(value, parameter)
            case Reference(target):
                return resolve(target, active)
            case Not(child):
                result = visit(child, active)
                return None if result is None else not result
            case And(left, right):
                a, b = visit(left, active), visit(right, active)
                if a is False or b is False:
                    return False
                return True if a is True and b is True else None
            case Or(left, right):
                a, b = visit(left, active), visit(right, active)
                if a is True or b is True:
                    return True
                return False if a is False and b is False else None
        raise TypeError(f"Unsupported expression: {expr!r}")

    return resolve(sense_id, frozenset())


def erase_operators(expr: Expression) -> Expression:
    """Control: erase NOT and replace OR with AND, retaining predicate leaves.

    This is a conjunction-of-dependencies control, not a reimplementation of the
    published graph builder (which additionally filters and resolves tokens).
    """
    match expr:
        case Not(child):
            return erase_operators(child)
        case And(left, right) | Or(left, right):
            return And(erase_operators(left), erase_operators(right))
        case Predicate() | Reference():
            return expr
    raise TypeError(f"Unsupported expression: {expr!r}")
