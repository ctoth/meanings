"""Smoke tests for meanings.spectral_analysis (the repo had no test suite before)."""
from __future__ import annotations

from meanings.spectral_analysis import (
    degree_rank_scores,
    overlap_at_k,
    perron_scores,
    randomized_edge_null,
    scc_local_eigenvectors,
    spearman,
)


def _cycle3():
    # a -> b -> c -> a, plus a pendant sink d that a points at
    return {"a": {"b", "d"}, "b": {"c"}, "c": {"a"}, "d": set()}


def test_reverse_pagerank_runs_and_sums_to_one():
    adj = _cycle3()
    res = perron_scores(adj, set(adj), orientation="reverse", component_policy="damped-full", iters=200)
    assert abs(sum(res.scores.values()) - 1.0) < 1e-6
    assert res.orientation == "reverse"
    assert res.scores  # non-empty


def test_forward_vs_reverse_differ_on_directed_graph():
    # hub h points at many leaves; leaves point back at h via one chain.
    #   h -> l1..l4 ;  l1 -> h   (so h is a definitional sink for l1, and a productive definer for l1..l4)
    adj = {"h": {"l1", "l2", "l3", "l4"}, "l1": {"h"}, "l2": set(), "l3": set(), "l4": set()}
    fwd_res = perron_scores(adj, set(adj), orientation="forward", component_policy="damped-full", iters=300)
    rev_res = perron_scores(adj, set(adj), orientation="reverse", component_policy="damped-full", iters=300)
    assert fwd_res.orientation == "forward" and rev_res.orientation == "reverse"
    # different orientations -> different scores on a non-symmetric graph
    assert fwd_res.scores != rev_res.scores
    # l1 is a definitional sink for h (h->l1->h) under forward flow but a productive
    # definer under reverse flow, so its score must move between orientations
    assert abs(fwd_res.scores["l1"] - rev_res.scores["l1"]) > 1e-6
    rev_order = sorted(rev_res.scores, key=rev_res.scores.get, reverse=True)
    # reverse PageRank rewards out-flow: a leaf with no out-edges is strictly last under reverse
    assert rev_order[-1] in {"l2", "l3", "l4"}


def test_largest_scc_eigenvector_is_uniform_on_a_clean_cycle():
    adj = _cycle3()
    res = perron_scores(adj, {"a", "b", "c"}, orientation="reverse", component_policy="largest-scc", iters=800)
    vals = list(res.scores.values())
    assert len(vals) == 3
    assert max(vals) - min(vals) < 1e-6  # symmetric 3-cycle -> uniform Perron vector
    assert abs(res.dominant_eigenvalue - 1.0) < 1e-3


def test_scc_local_eigenvectors_finds_the_cycle():
    adj = _cycle3()
    blocks = scc_local_eigenvectors(adj, set(adj), min_size=2)
    assert len(blocks) == 1
    assert blocks[0].size == 3
    assert set(blocks[0].scores) == {"a", "b", "c"}


def test_degree_null_and_overlap_helpers():
    adj = _cycle3()
    deg = degree_rank_scores(adj, set(adj), mode="total")
    assert deg["a"] >= deg["d"]
    assert overlap_at_k(deg, deg, 2) == 1.0


def test_spearman_perfect_and_anti():
    a = {"x": 1.0, "y": 2.0, "z": 3.0}
    b = {"x": 10.0, "y": 20.0, "z": 30.0}
    c = {"x": 3.0, "y": 2.0, "z": 1.0}
    assert abs(spearman(a, b) - 1.0) < 1e-9
    assert abs(spearman(a, c) + 1.0) < 1e-9


def test_randomized_edge_null_preserves_degrees():
    # bigger graph so swaps are possible
    adj = {f"n{i}": {f"n{(i + 1) % 8}", f"n{(i + 3) % 8}"} for i in range(8)}
    res = randomized_edge_null(adj, set(adj), orientation="reverse", seed=3, swaps_per_edge=5, iters=100)
    assert abs(sum(res.scores.values()) - 1.0) < 1e-5
    assert res.notes.get("null") == "degree_preserving_edge_swap"
    assert res.notes.get("swaps_done", 0) > 0
