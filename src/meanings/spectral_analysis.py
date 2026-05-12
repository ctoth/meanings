"""Spectral valuation of dictionary definition digraphs.

Pure-Python (no numpy dependency in this environment). Provides:

* :func:`perron_scores` -- damped or un-damped dominant-eigenvector scores over
  an adjacency map, with an explicit ``orientation`` argument and an explicit
  ``component_policy`` for handling reducibility.
* :func:`scc_local_eigenvectors` -- per-SCC un-damped Perron eigenvectors for
  the nontrivial strongly connected components of a (sub)graph.
* :func:`degree_rank_scores` / :func:`randomized_edge_null` /
  :func:`label_shuffled_layers` -- null models for incremental-value checks.
* :func:`spearman` -- Spearman rho over the common keys of two score maps.

Edge convention in this repo: ``u -> v`` means "u occurs in the definition of
v" (the *defining -> defined* / *forward* orientation). Hence:

* ``orientation="forward"`` (a.k.a. authority / downstream-use PageRank):
  importance flows from a definer to the words it helps define -- a node scores
  high when *important words use it as a definer*... no: it scores high when it
  is *pointed at by important nodes*, i.e. when it is a definitional **sink**.
  This measures *dependency on already-important definers*.
* ``orientation="reverse"`` (PageRank on the transposed graph): importance flows
  from a defined word back to the words that define it -- a node scores high
  when *it occurs in the definitions of many / important words*. This measures
  *definitional productivity / downstream use* and is the eigenvector
  relaxation of the feedback-vertex heuristic ``choose_feedback_vertex``, which
  maximises ``internal_out + internal_in``.
"""
from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass, field

from meanings.graph_analysis import (
    Adjacency,
    induced_subgraph,
    reverse_adjacency,
    strongly_connected_components,
)

__all__ = [
    "SpectralResult",
    "perron_scores",
    "scc_local_eigenvectors",
    "degree_rank_scores",
    "randomized_edge_null",
    "label_shuffled_layers",
    "spearman",
    "overlap_at_k",
    "rank_positions",
]

Orientation = str  # "forward" | "reverse"
ComponentPolicy = str  # "damped-full" | "largest-scc" | "scc-local" | "raw"


@dataclass(slots=True)
class SpectralResult:
    scores: dict[str, float]
    orientation: Orientation
    component_policy: ComponentPolicy
    damping: float | None
    dominant_eigenvalue: float | None
    converged: bool
    iterations: int
    scope_nodes: int
    notes: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# core iterations
# --------------------------------------------------------------------------- #
def _oriented_adjacency(nodes: list[str], adjacency: Adjacency, orientation: Orientation) -> Adjacency:
    node_set = set(nodes)
    if orientation == "forward":
        return {n: {t for t in adjacency.get(n, ()) if t in node_set} for n in nodes}
    if orientation == "reverse":
        return reverse_adjacency(node_set, induced_subgraph(node_set, adjacency))
    raise ValueError(f"orientation must be 'forward' or 'reverse', got {orientation!r}")


def _pagerank(nodes: list[str], out_adj: Adjacency, damping: float, iters: int, tol: float) -> tuple[dict[str, float], bool, int]:
    n = len(nodes)
    if n == 0:
        return {}, True, 0
    idx = {node: i for i, node in enumerate(nodes)}
    out = [list(out_adj.get(node, ())) for node in nodes]
    outdeg = [len(o) for o in out]
    rev: list[list[int]] = [[] for _ in range(n)]
    for i, targets in enumerate(out):
        for t in targets:
            rev[idx[t]].append(i)
    pr = [1.0 / n] * n
    base = (1.0 - damping) / n
    converged = False
    used = 0
    for used in range(1, iters + 1):
        dangling = sum(pr[i] for i in range(n) if outdeg[i] == 0)
        const = base + damping * dangling / n
        new = [const] * n
        for j in range(n):
            s = 0.0
            for i in rev[j]:
                s += pr[i] / outdeg[i]
            new[j] += damping * s
        diff = sum(abs(new[k] - pr[k]) for k in range(n))
        pr = new
        if diff < tol:
            converged = True
            break
    return {node: pr[idx[node]] for node in nodes}, converged, used


def _power_iteration_eigenvector(
    nodes: list[str], out_adj: Adjacency, iters: int, tol: float
) -> tuple[dict[str, float], float, bool, int]:
    """Dominant eigenvector of M where M[j] receives sum over predecessors-in-``out_adj``.

    i.e. v_j <- sum_{i : i -> j in out_adj} v_i, then normalise. For a strongly
    connected ``out_adj`` this converges (Perron-Frobenius) to the unique
    positive dominant eigenvector; ``lambda`` is the dominant eigenvalue.
    Returns scores normalised to sum 1.
    """
    n = len(nodes)
    if n == 0:
        return {}, 0.0, True, 0
    idx = {node: i for i, node in enumerate(nodes)}
    out = [list(out_adj.get(node, ())) for node in nodes]
    rev: list[list[int]] = [[] for _ in range(n)]
    for i, targets in enumerate(out):
        for t in targets:
            rev[idx[t]].append(i)
    v = [1.0] * n
    converged = False
    used = 0
    for used in range(1, iters + 1):
        nv = [0.0] * n
        for j in range(n):
            s = 0.0
            for i in rev[j]:
                s += v[i]
            nv[j] = s
        norm = math.sqrt(sum(x * x for x in nv))
        if norm == 0.0:
            break
        nv = [x / norm for x in nv]
        diff = sum(abs(nv[k] - v[k]) for k in range(n))
        v = nv
        if diff < tol:
            converged = True
            break
    # Rayleigh quotient for lambda: ||M v|| / ||v||  with v already unit-norm
    nv = [0.0] * n
    for j in range(n):
        s = 0.0
        for i in rev[j]:
            s += v[i]
        nv[j] = s
    num = math.sqrt(sum(x * x for x in nv))
    den = math.sqrt(sum(x * x for x in v))
    lam = num / den if den else 0.0
    total = sum(v) or 1.0
    return {node: v[idx[node]] / total for node in nodes}, lam, converged, used


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def perron_scores(
    adjacency: Adjacency,
    nodes: set[str] | list[str],
    *,
    orientation: Orientation = "reverse",
    component_policy: ComponentPolicy = "damped-full",
    damping: float = 0.85,
    iters: int = 300,
    tol: float = 1e-12,
) -> SpectralResult:
    """Dominant-eigenvector valuation of ``adjacency`` restricted to ``nodes``.

    ``orientation``:
        ``"forward"`` -- score flows along ``u -> v`` (authority / downstream-use;
        on this repo's convention, definitional-sink importance =
        *dependency on already-important definers*).
        ``"reverse"`` -- score flows along the transposed edge (definitional
        productivity / downstream use; eigenvector relaxation of the FVS
        out-flow heuristic).

    ``component_policy``:
        ``"damped-full"`` -- run damped PageRank over the whole node set
        (teleportation restores irreducibility; the modelling hack).
        ``"largest-scc"`` -- restrict to the largest strongly connected
        component of the oriented graph and run the *un-damped* power iteration
        there (a genuine Perron eigenvector of an irreducible block).
        ``"scc-local"`` -- like ``largest-scc`` but returns the union of
        per-SCC un-damped eigenvectors for every nontrivial SCC (each block's
        own Perron eigenvector; cross-block magnitudes are *not* comparable --
        see :func:`scc_local_eigenvectors`).
        ``"raw"`` -- un-damped power iteration over the whole (possibly
        reducible) node set; provided only for diagnostics, not principled.
    """
    node_list = list(nodes)
    out_adj = _oriented_adjacency(node_list, adjacency, orientation)

    if component_policy == "damped-full":
        scores, conv, used = _pagerank(node_list, out_adj, damping, iters, tol)
        return SpectralResult(scores, orientation, component_policy, damping, 1.0, conv, used, len(node_list))

    if component_policy == "raw":
        scores, lam, conv, used = _power_iteration_eigenvector(node_list, out_adj, iters, tol)
        return SpectralResult(scores, orientation, component_policy, None, lam, conv, used, len(node_list),
                              notes={"warning": "graph may be reducible; eigenvector not unique"})

    sccs = strongly_connected_components(set(node_list), out_adj)
    nontrivial = [c for c in sccs if len(c) > 1 or any(u in out_adj.get(u, ()) for u in c)]

    if component_policy == "largest-scc":
        if not nontrivial:
            return SpectralResult({}, orientation, component_policy, None, 0.0, True, 0, 0,
                                  notes={"warning": "no nontrivial SCC"})
        block = max(nontrivial, key=len)
        block_adj = induced_subgraph(block, out_adj)
        scores, lam, conv, used = _power_iteration_eigenvector(list(block), block_adj, max(iters, 800), tol)
        return SpectralResult(scores, orientation, component_policy, None, lam, conv, used, len(block),
                              notes={"scc_count": len(sccs), "nontrivial_scc_count": len(nontrivial),
                                     "largest_scc_size": len(block)})

    if component_policy == "scc-local":
        local = scc_local_eigenvectors(out_adj, set(node_list), iters=max(iters, 800), tol=tol)
        merged: dict[str, float] = {}
        lam_max = 0.0
        for blk in local:
            merged.update(blk["scores"])
            lam_max = max(lam_max, blk["dominant_eigenvalue"])
        return SpectralResult(merged, orientation, component_policy, None, lam_max, all(b["converged"] for b in local),
                              max((b["iterations"] for b in local), default=0), sum(len(b["scores"]) for b in local),
                              notes={"scc_count": len(sccs), "nontrivial_scc_count": len(nontrivial),
                                     "per_scc": [{"size": len(b["scores"]), "lambda": b["dominant_eigenvalue"]} for b in local]})

    raise ValueError(f"unknown component_policy {component_policy!r}")


def scc_local_eigenvectors(
    adjacency: Adjacency,
    nodes: set[str],
    *,
    min_size: int = 2,
    iters: int = 800,
    tol: float = 1e-13,
) -> list[dict[str, object]]:
    """Un-damped Perron eigenvector inside each nontrivial SCC of ``adjacency``.

    ``adjacency`` is taken as already-oriented (the caller decides forward vs
    reverse). Each returned dict has ``scores`` (sum-1 within that block),
    ``dominant_eigenvalue``, ``size``, ``converged``, ``iterations``. Blocks are
    returned largest first. Cross-block magnitudes are NOT comparable.
    """
    sub = induced_subgraph(nodes, adjacency)
    sccs = strongly_connected_components(nodes, sub)
    out: list[dict[str, object]] = []
    for comp in sccs:
        is_loop = len(comp) >= min_size or any(u in sub.get(u, ()) for u in comp)
        if not is_loop:
            continue
        comp_adj = induced_subgraph(comp, sub)
        scores, lam, conv, used = _power_iteration_eigenvector(list(comp), comp_adj, iters, tol)
        out.append({"scores": scores, "dominant_eigenvalue": lam, "size": len(comp),
                    "converged": conv, "iterations": used})
    out.sort(key=lambda b: b["size"], reverse=True)  # type: ignore[arg-type, return-value]
    return out


# --------------------------------------------------------------------------- #
# null models
# --------------------------------------------------------------------------- #
def degree_rank_scores(
    adjacency: Adjacency,
    nodes: set[str] | list[str],
    *,
    mode: str = "total",
) -> dict[str, float]:
    """Degree-based null. ``mode`` in {"in", "out", "total"}."""
    node_set = set(nodes)
    indeg = {n: 0 for n in node_set}
    for src, targets in adjacency.items():
        if src not in node_set:
            continue
        for t in targets:
            if t in node_set:
                indeg[t] += 1
    outdeg = {n: sum(1 for t in adjacency.get(n, ()) if t in node_set) for n in node_set}
    if mode == "in":
        return {n: float(indeg[n]) for n in node_set}
    if mode == "out":
        return {n: float(outdeg[n]) for n in node_set}
    if mode == "total":
        return {n: float(indeg[n] + outdeg[n]) for n in node_set}
    raise ValueError(f"mode must be in/out/total, got {mode!r}")


def randomized_edge_null(
    adjacency: Adjacency,
    nodes: set[str] | list[str],
    *,
    orientation: Orientation = "reverse",
    component_policy: ComponentPolicy = "damped-full",
    seed: int = 0,
    swaps_per_edge: int = 10,
    damping: float = 0.85,
    iters: int = 200,
    tol: float = 1e-11,
) -> SpectralResult:
    """Degree-preserving randomized-edge null: directed double-edge swaps that
    preserve every node's in- and out-degree, then re-run :func:`perron_scores`.

    A spectral ranking that is "real" should not survive (rank-correlate with
    the true one) under this null beyond what degree alone explains.
    """
    rng = random.Random(seed)
    node_set = set(nodes)
    edges = [(u, v) for u, targets in adjacency.items() if u in node_set for v in targets if v in node_set and u != v]
    edge_set = set(edges)
    target = swaps_per_edge * len(edges)
    attempts = 0
    max_attempts = 50 * max(target, 1)
    done = 0
    while done < target and attempts < max_attempts:
        attempts += 1
        if len(edges) < 2:
            break
        i = rng.randrange(len(edges))
        j = rng.randrange(len(edges))
        if i == j:
            continue
        a, b = edges[i]
        c, d = edges[j]
        # swap targets: a->d, c->b
        if a == d or c == b:
            continue
        if (a, d) in edge_set or (c, b) in edge_set:
            continue
        edge_set.discard((a, b))
        edge_set.discard((c, d))
        edge_set.add((a, d))
        edge_set.add((c, b))
        edges[i] = (a, d)
        edges[j] = (c, b)
        done += 1
    rand_adj: Adjacency = {n: set() for n in node_set}
    for u, v in edge_set:
        rand_adj[u].add(v)
    result = perron_scores(rand_adj, node_set, orientation=orientation,
                           component_policy=component_policy, damping=damping, iters=iters, tol=tol)
    result.notes = dict(result.notes)
    result.notes.update({"null": "degree_preserving_edge_swap", "swaps_done": done, "swaps_target": target})
    return result


def label_shuffled_layers(layer_by_node: dict[str, int], *, seed: int = 0) -> dict[str, int]:
    """Permute layer labels across nodes (preserves the layer-size histogram).
    Use as a null for "does layer index predict X"."""
    rng = random.Random(seed)
    keys = list(layer_by_node)
    vals = [layer_by_node[k] for k in keys]
    rng.shuffle(vals)
    return dict(zip(keys, vals))


# --------------------------------------------------------------------------- #
# comparison helpers
# --------------------------------------------------------------------------- #
def rank_positions(scores: dict[str, float], *, descending: bool = True) -> dict[str, int]:
    """0-based rank position of each key (0 = best)."""
    order = sorted(scores, key=lambda k: scores[k], reverse=descending)
    return {k: i for i, k in enumerate(order)}


def overlap_at_k(scores_a: dict[str, float], scores_b: dict[str, float], k: int) -> float:
    """Jaccard-style overlap of the top-k of two score maps over their common keys."""
    common = set(scores_a) & set(scores_b)
    a = sorted(common, key=lambda x: scores_a[x], reverse=True)[:k]
    b = sorted(common, key=lambda x: scores_b[x], reverse=True)[:k]
    if not a or not b:
        return 0.0
    return len(set(a) & set(b)) / len(set(a) | set(b))


def spearman(scores_a: dict[str, float], scores_b: dict[str, float]) -> float | None:
    """Spearman rho over the keys present in both maps (higher score => better rank)."""
    common = list(set(scores_a) & set(scores_b))
    n = len(common)
    if n < 3:
        return None

    def ranks(d: dict[str, float]) -> dict[str, float]:
        order = sorted(common, key=lambda k: d[k])
        r: dict[str, float] = {}
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and d[order[j + 1]] == d[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r

    ra, rb = ranks(scores_a), ranks(scores_b)
    # use the Pearson-on-ranks form to be tie-correct
    mean_a = sum(ra.values()) / n
    mean_b = sum(rb.values()) / n
    sab = sum((ra[k] - mean_a) * (rb[k] - mean_b) for k in common)
    saa = sum((ra[k] - mean_a) ** 2 for k in common)
    sbb = sum((rb[k] - mean_b) ** 2 for k in common)
    if saa == 0.0 or sbb == 0.0:
        return None
    return sab / math.sqrt(saa * sbb)
