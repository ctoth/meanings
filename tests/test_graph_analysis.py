"""Tests for graph_analysis kernel / SCC handling, focused on self-loops.

``compute_kernel`` iteratively strips dead-end nodes, so the surviving
"Kernel" is every node from which a cycle is reachable (the cyclic Core plus
the acyclic Satellites that feed into it). A self-loop ``u -> u`` is a cycle,
so a self-loop-only node must survive -- it used to be stripped.
"""
from meanings.graph_analysis import compute_kernel, strongly_connected_components


def test_self_loop_only_node_survives_in_the_kernel():
    # c appears only in its own definition; a -> b -> c feeds into it.
    adj = {"a": {"b"}, "b": {"c"}, "c": {"c"}}
    kernel = compute_kernel(set(adj), adj)
    assert "c" in kernel  # a 1-node cycle is irreducible; pre-fix this was {}
    # a and b reach c's loop, so they survive too (as Satellites) -- same as
    # they would for a multi-node cycle.
    assert kernel == {"a", "b", "c"}


def test_self_loop_and_multi_node_cycle_treat_upstream_nodes_the_same():
    self_loop = {"d": {"a"}, "a": {"a"}}
    three_cycle = {"d": {"a"}, "a": {"b"}, "b": {"c"}, "c": {"a"}}
    assert compute_kernel(set(self_loop), self_loop) == {"a", "d"}
    assert compute_kernel(set(three_cycle), three_cycle) == {"a", "b", "c", "d"}


def test_dead_end_periphery_is_stripped_even_next_to_a_self_loop():
    # s -> x (self-loop); x also points at the sink d; y -> {d, e} only reaches sinks.
    adj = {"s": {"x"}, "x": {"x", "d"}, "y": {"d", "e"}}
    assert compute_kernel(set(adj), adj) == {"s", "x"}


def test_fully_acyclic_graph_has_empty_kernel():
    adj = {"a": {"b", "c"}, "b": {"c"}, "c": set()}
    assert compute_kernel(set(adj), adj) == set()


def test_self_loop_is_its_own_strongly_connected_component():
    adj = {"a": {"b"}, "b": {"b"}}
    assert {"b"} in strongly_connected_components(set(adj), adj)
