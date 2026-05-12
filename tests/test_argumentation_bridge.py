"""Smoke tests for meanings.argumentation_bridge on tiny hand-built digraphs."""

from argumentation.bipolar import bipolar_grounded_extension
from argumentation.dung import grounded_extension, stable_extensions

from meanings.argumentation_bridge import (
    bipolar_support_framework,
    dung_attack_framework,
    edges_of,
)


def test_chain_round_trips_and_grounded_takes_alternating_layers():
    # a -> b -> c, read as attacks. a unattacked => IN; b attacked by IN a => OUT;
    # c attacked only by OUT b => IN.
    adj = {"a": {"b"}, "b": {"c"}, "c": set()}
    af = dung_attack_framework(set(adj), adj)
    assert af.arguments == frozenset({"a", "b", "c"})
    assert af.defeats == edges_of(set(adj), adj) == frozenset({("a", "b"), ("b", "c")})
    assert grounded_extension(af) == frozenset({"a", "c"})


def test_two_cycle_attack_grounded_empty_two_stable():
    # a <-> b: even cycle. grounded undecided => empty; two stable extensions.
    adj = {"a": {"b"}, "b": {"a"}}
    af = dung_attack_framework(set(adj), adj)
    assert grounded_extension(af) == frozenset()
    assert sorted(stable_extensions(af), key=sorted) == [frozenset({"a"}), frozenset({"b"})]


def test_self_loop_attack_node_never_accepted_and_no_stable():
    # c -> c: self-attack. c can never be in any extension; with c alone there is
    # no stable extension at all.
    adj = {"c": {"c"}}
    af = dung_attack_framework(set(adj), adj)
    assert ("c", "c") in af.defeats
    assert grounded_extension(af) == frozenset()
    assert stable_extensions(af) == []


def test_support_framework_carries_edges_as_supports_no_defeats():
    adj = {"a": {"b"}, "b": {"c"}, "c": set()}
    baf = bipolar_support_framework(set(adj), adj)
    assert baf.defeats == frozenset()
    assert baf.supports == frozenset({("a", "b"), ("b", "c")})
    # Support-only bipolar AF: nothing attacks anything => grounded is everything.
    assert bipolar_grounded_extension(baf) == frozenset({"a", "b", "c"})
