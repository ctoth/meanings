from __future__ import annotations

from meanings.minset import solve_minset


def test_exact_cutting_solves_small_directed_cycle():
    adjacency = {
        "a": {"b"},
        "b": {"c"},
        "c": {"a"},
    }

    result = solve_minset(set(adjacency), adjacency, "exact-cutting")

    assert result.exact is True
    assert result.lower_bound == 1
    assert result.upper_bound == 1
    assert len(result.nodes) == 1
    assert result.residual_cyclic_scc_count == 0
    assert result.scc_exact_count == 1
    assert result.scc_heuristic_count == 0


def test_exact_small_greedy_reports_heuristic_for_large_component():
    nodes = {f"n{i}" for i in range(13)}
    adjacency = {node: set() for node in nodes}
    for index in range(13):
        adjacency[f"n{index}"].add(f"n{(index + 1) % 13}")

    result = solve_minset(nodes, adjacency, "exact-small-greedy")

    assert result.exact is False
    assert result.lower_bound is None
    assert result.upper_bound == 1
    assert len(result.nodes) == 1
    assert result.residual_cyclic_scc_count == 0
    assert result.scc_exact_count == 0
    assert result.scc_heuristic_count == 1


def test_bounded_scc_keeps_baseline_cycle_breaking_shape():
    adjacency = {
        "a": {"b"},
        "b": {"a"},
        "c": {"d"},
        "d": {"c"},
    }

    result = solve_minset(set(adjacency), adjacency, "bounded-scc")

    assert result.exact is False
    assert result.lower_bound is None
    assert result.upper_bound == 2
    assert len(result.nodes) == 2
    assert result.residual_cyclic_scc_count == 0
    assert result.scc_heuristic_count == 2
