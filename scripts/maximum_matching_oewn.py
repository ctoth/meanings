"""Maximum-matching driver-node set (Liu-Slotine-Barabasi structural controllability)
on the OEWN paper-wordnet definition digraph, compared against the combinatorial
FVS-seed / kernel / core / satellites.

Driver nodes (Liu et al. 2011): build the bipartite graph B with left = nodes as
edge-tails, right = nodes as edge-heads; edge (u->v) in G  ->  edge (u_L, v_R) in B.
A maximum matching M* of B leaves N - |M*| right-vertices unmatched; those unmatched
"heads" are the minimum driver-node set.  We use Hopcroft-Karp.

We run it on:
  (1) the FULL definition digraph (Liu's natural domain), and
  (2) the kernel subgraph (the graph on which the repo's exact-small-greedy FVS-seed
      is actually computed),
and report sizes / overlap / disagreements vs. the FVS-seed, kernel, core, satellites.

Pure-Python (no numpy needed). Writes reports/maximum-matching-oewn.json.
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

from meanings.wordnet_pipeline import build_paper_wordnet_graph
from meanings.graph_analysis import (
    analyze_kernel,
    induced_subgraph,
)


def hopcroft_karp(adj_left: dict, left_nodes, right_nodes):
    """Maximum bipartite matching. adj_left: left_node -> iterable of right_nodes.
    Returns (match_left, match_right) dicts; unmatched nodes absent from the dicts."""
    INF = float("inf")
    pair_u = {u: None for u in left_nodes}
    pair_v = {v: None for v in right_nodes}
    dist = {}

    def bfs():
        q = deque()
        for u in left_nodes:
            if pair_u[u] is None:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        found = False
        while q:
            u = q.popleft()
            for v in adj_left.get(u, ()):  # u -> v
                w = pair_v[v]
                if w is None:
                    found = True
                elif dist[w] == INF:
                    dist[w] = dist[u] + 1
                    q.append(w)
        return found

    def dfs(u):
        for v in adj_left.get(u, ()):
            w = pair_v[v]
            if w is None or (dist[w] == dist[u] + 1 and dfs(w)):
                pair_u[u] = v
                pair_v[v] = u
                return True
        dist[u] = INF
        return False

    sys.setrecursionlimit(1_000_000)
    matching = 0
    while bfs():
        for u in left_nodes:
            if pair_u[u] is None:
                if dfs(u):
                    matching += 1
    match_left = {u: v for u, v in pair_u.items() if v is not None}
    match_right = {v: u for v, u in pair_v.items() if u is not None}
    return match_left, match_right, matching


def driver_nodes(nodes, adjacency):
    """Liu et al.: driver set = right-vertices (heads) unmatched in max matching.
    Self-loops (u->u): include them as bipartite edge u_L -> u_R (Lin's framework
    allows them; a self-loop lets a node match itself = self-controlled).
    Returns (driver_set, matching_size)."""
    left = list(nodes)
    right = list(nodes)
    adj_left = {u: [v for v in adjacency.get(u, ())] for u in left}
    match_left, match_right, m = hopcroft_karp(adj_left, left, right)
    matched_heads = set(match_right.keys())
    drivers = set(right) - matched_heads
    return drivers, m


def summarize(name, drivers, m, n, *, kernel=None, core=None, sats=None,
              seed=None, labels=None):
    d = {
        "graph": name,
        "n": n,
        "matching_size": m,
        "n_drivers": len(drivers),
        "n_D_fraction": len(drivers) / n if n else None,
    }
    if kernel is not None:
        d["drivers_in_kernel"] = len(drivers & kernel)
        d["drivers_in_kernel_frac_of_drivers"] = len(drivers & kernel) / len(drivers) if drivers else None
        d["drivers_in_kernel_frac_of_kernel"] = len(drivers & kernel) / len(kernel) if kernel else None
    if core is not None:
        d["drivers_in_core"] = len(drivers & core)
        d["core_size"] = len(core)
    if sats is not None:
        d["drivers_in_satellites"] = len(drivers & sats)
    if seed is not None:
        d["seed_size"] = len(seed)
        d["drivers_cap_seed"] = len(drivers & seed)
        d["seed_minus_drivers"] = len(seed - drivers)
        d["drivers_minus_seed"] = len(drivers - seed)
        d["jaccard_drivers_seed"] = (
            len(drivers & seed) / len(drivers | seed) if (drivers | seed) else None
        )
    return d


def main():
    print("building paper-wordnet graph...")
    build = build_paper_wordnet_graph()
    nodes = set(build.nodes)
    adj = build.adjacency
    n = len(nodes)
    edges = sum(len(v) for v in adj.values())
    self_loops = sum(1 for u in nodes if u in adj.get(u, ()))
    print(f"nodes={n} edges={edges} self_loops={self_loops}")

    print("kernel analysis (exact-small-greedy seed, source-union core)...")
    analysis = analyze_kernel(build.nodes, build.adjacency,
                              seed_method="exact-small-greedy", core_policy="source-union")
    kernel = analysis.kernel_nodes
    core = analysis.core_nodes
    sats = analysis.satellite_nodes
    seed = set(analysis.seed_nodes)
    kernel_adj = induced_subgraph(kernel, adj)
    print(f"kernel={len(kernel)} core={len(core)} sats={len(sats)} seed={len(seed)}")

    out = {}
    out["graph_stats"] = {"nodes": n, "edges": edges, "self_loops": self_loops,
                          "kernel": len(kernel), "core": len(core),
                          "satellites": len(sats), "fvs_seed": len(seed),
                          "seed_method": "exact-small-greedy"}

    # ---- (1) full digraph ----
    print("max matching on FULL digraph (Hopcroft-Karp)...")
    drivers_full, m_full = driver_nodes(nodes, adj)
    print(f"  matching={m_full} drivers={len(drivers_full)} ({len(drivers_full)/n:.4f})")
    out["full_graph"] = summarize("full", drivers_full, m_full, n,
                                  kernel=kernel, core=core, sats=sats, seed=seed)

    # also: in-degree-0 nodes (pure sources) MUST be drivers; how many?
    indeg = {x: 0 for x in nodes}
    for ts in adj.values():
        for t in ts:
            indeg[t] += 1
    sources = {x for x in nodes if indeg[x] == 0}
    out["full_graph"]["pure_source_nodes_indeg0"] = len(sources)
    out["full_graph"]["drivers_that_are_pure_sources"] = len(drivers_full & sources)
    out["full_graph"]["drivers_with_indeg_ge_1"] = len(drivers_full - sources)

    # ---- (2) kernel subgraph ----
    print("max matching on KERNEL subgraph...")
    drivers_kern, m_kern = driver_nodes(kernel, kernel_adj)
    print(f"  matching={m_kern} drivers={len(drivers_kern)} ({len(drivers_kern)/len(kernel):.4f})")
    out["kernel_graph"] = summarize("kernel", drivers_kern, m_kern, len(kernel),
                                    core=core, sats=sats, seed=seed)
    out["kernel_graph"]["drivers_cap_seed"] = len(drivers_kern & seed)
    out["kernel_graph"]["seed_minus_drivers"] = sorted_sample(seed - drivers_kern)
    out["kernel_graph"]["drivers_minus_seed_count"] = len(drivers_kern - seed)
    out["kernel_graph"]["seed_minus_drivers_count"] = len(seed - drivers_kern)

    # labelled disagreements (kernel graph): "drivers but not grounders" and vice versa
    def lab(s, k=40):
        return [build.labels.get(x, x) for x in sorted(s)[:k]]
    out["kernel_graph"]["sample_driver_not_seed"] = lab(drivers_kern - seed)
    out["kernel_graph"]["sample_seed_not_driver"] = lab(seed - drivers_kern)

    # full graph labelled samples
    out["full_graph"]["sample_driver_not_seed_in_kernel"] = lab((drivers_full - seed) & kernel)
    out["full_graph"]["sample_driver_outside_kernel"] = lab(drivers_full - kernel)
    out["full_graph"]["sample_seed_not_driver"] = lab(seed - drivers_full)

    Path("reports/maximum-matching-oewn.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("wrote reports/maximum-matching-oewn.json")
    printable = {k: (v if not isinstance(v, dict) else
                     {kk: vv for kk, vv in v.items() if not isinstance(vv, list)})
                 for k, v in out.items()}
    print(json.dumps(printable, indent=2))


def sorted_sample(s, k=40):
    return sorted(s)[:k]


if __name__ == "__main__":
    main()
