"""Compute Perron eigenvector (PageRank + undamped dominant on the kernel SCC)
over the OEWN paper-wordnet definition digraph and compare against the
combinatorial seed / kernel-core-satellite layering / degree.

Pure-Python power iteration (no numpy in this env). Writes a JSON blob to
reports/perron-frobenius-oewn.json with all the numbers the findings report needs.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from meanings.wordnet_pipeline import build_paper_wordnet_graph
from meanings.graph_analysis import (
    analyze_kernel,
    induced_subgraph,
    strongly_connected_components,
    compute_kernel,
)


def pagerank(nodes, adjacency, damping=0.85, iters=200, tol=1e-12):
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}
    out = [list(adjacency.get(node, ())) for node in nodes]
    outdeg = [len(o) for o in out]
    # build reverse: list of (src_index) for each target
    rev = [[] for _ in range(n)]
    for i, targets in enumerate(out):
        for t in targets:
            rev[idx[t]].append(i)
    pr = [1.0 / n] * n
    base = (1.0 - damping) / n
    for _ in range(iters):
        dangling = sum(pr[i] for i in range(n) if outdeg[i] == 0)
        new = [base + damping * dangling / n] * n
        for j in range(n):
            s = 0.0
            for i in rev[j]:
                s += pr[i] / outdeg[i]
            new[j] += damping * s
        diff = sum(abs(new[k] - pr[k]) for k in range(n))
        pr = new
        if diff < tol:
            break
    return {node: pr[idx[node]] for node in nodes}


def undamped_perron(nodes, adjacency, iters=500, tol=1e-13):
    """Dominant right eigenvector of the adjacency matrix A where A[i][j]=1 if i->j.
    We want v s.t. lambda v = A^T v  (importance flows from predecessors):
    v_j = (1/lambda) sum_{i->j} v_i. That's the 'PageRank-like' authority direction.
    Requires the subgraph strongly connected for Perron-Frobenius uniqueness.
    Returns (eigenvector dict normalized to sum 1, lambda estimate)."""
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}
    out = [list(adjacency.get(node, ())) for node in nodes]
    rev = [[] for _ in range(n)]
    for i, targets in enumerate(out):
        for t in targets:
            rev[idx[t]].append(i)
    v = [1.0] * n
    lam = 1.0
    for _ in range(iters):
        nv = [0.0] * n
        for j in range(n):
            s = 0.0
            for i in rev[j]:
                s += v[i]
            nv[j] = s
        norm = math.sqrt(sum(x * x for x in nv))
        if norm == 0:
            break
        nv = [x / norm for x in nv]
        # Rayleigh-ish: lambda ~ <v, A^T v>/<v,v> but v normalized => sum v_i * nv_i * old_norm
        diff = sum(abs(nv[k] - v[k]) for k in range(n))
        # estimate lambda from ratio before normalization
        # recompute unnormalized product norm for lambda
        v = nv
        if diff < tol:
            break
    # lambda estimate: apply once more, take norm
    nv = [0.0] * n
    for j in range(n):
        s = 0.0
        for i in rev[j]:
            s += v[i]
        nv[j] = s
    lam = math.sqrt(sum(x * x for x in nv)) / math.sqrt(sum(x * x for x in v))
    total = sum(v)
    return {node: v[idx[node]] / total for node in nodes}, lam


def spearman(rank_a: dict, rank_b: dict):
    """Spearman rho over the common keys (both dicts map key->score; higher score better)."""
    common = list(set(rank_a) & set(rank_b))
    if len(common) < 3:
        return None
    def ranks(d):
        order = sorted(common, key=lambda k: d[k])
        r = {}
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and d[order[j + 1]] == d[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(rank_a), ranks(rank_b)
    n = len(common)
    d2 = sum((ra[k] - rb[k]) ** 2 for k in common)
    return 1 - 6 * d2 / (n * (n * n - 1))


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def main():
    print("building paper-wordnet graph...")
    build = build_paper_wordnet_graph()
    nodes = list(build.nodes)
    adj = build.adjacency
    print(f"nodes={len(nodes)} edges={sum(len(v) for v in adj.values())}")

    print("kernel analysis (exact-small-greedy seed, source-union core)...")
    analysis = analyze_kernel(build.nodes, build.adjacency,
                              seed_method="exact-small-greedy", core_policy="source-union")
    kernel = analysis.kernel_nodes
    core = analysis.core_nodes
    sats = analysis.satellite_nodes
    seed = set(analysis.seed_nodes)
    layers = analysis.layer_by_node
    largest_scc = max(analysis.kernel_sccs, key=len)
    print(f"kernel={len(kernel)} core={len(core)} sats={len(sats)} seed={len(seed)} "
          f"largest_kernel_scc={len(largest_scc)}")

    # full-graph PageRank
    print("full-graph PageRank...")
    pr_full = pagerank(nodes, adj, damping=0.85, iters=300)

    # undamped Perron on the largest kernel SCC
    print("undamped Perron on largest kernel SCC...")
    scc_nodes = list(largest_scc)
    scc_adj = induced_subgraph(largest_scc, adj)
    perron_scc, lam = undamped_perron(scc_nodes, scc_adj, iters=800)
    print(f"dominant eigenvalue (largest kernel SCC) ~ {lam:.4f}")

    # PageRank restricted (recomputed) on the largest kernel SCC for comparison
    print("PageRank on largest kernel SCC subgraph...")
    pr_scc = pagerank(scc_nodes, scc_adj, damping=0.85, iters=300)

    # degree maps
    indeg = {node: 0 for node in nodes}
    for ts in adj.values():
        for t in ts:
            indeg[t] += 1
    outdeg = {node: len(adj.get(node, ())) for node in nodes}

    # ---- comparisons ----
    out = {}
    out["graph"] = {"nodes": len(nodes), "edges": sum(len(v) for v in adj.values())}
    out["kernel"] = {"kernel": len(kernel), "core": len(core), "satellites": len(sats),
                     "seed": len(seed), "largest_kernel_scc": len(largest_scc),
                     "dominant_eigenvalue_largest_kernel_scc": lam}

    # (a) does PageRank rank high the seed/kernel nodes?
    pr_sorted = sorted(nodes, key=lambda n: pr_full[n], reverse=True)
    for K in (100, 500, 1000, 2370, 5000, 12853):
        topK = set(pr_sorted[:K])
        out.setdefault("pagerank_topK_overlap", {})[str(K)] = {
            "in_kernel": len(topK & kernel),
            "in_core": len(topK & core),
            "in_seed": len(topK & seed),
            "frac_kernel": len(topK & kernel) / K,
            "frac_seed": len(topK & seed) / K,
        }
    # mean PageRank by component
    def mean_pr(s):
        s = list(s)
        return sum(pr_full[n] for n in s) / len(s) if s else 0.0
    out["mean_pagerank_by_component"] = {
        "all": sum(pr_full.values()) / len(nodes),
        "rest": mean_pr(build.nodes - kernel),
        "kernel": mean_pr(kernel),
        "core": mean_pr(core),
        "satellites": mean_pr(sats),
        "seed": mean_pr(seed),
        "non_seed_kernel": mean_pr(kernel - seed),
    }
    # rank position of seed nodes in global PageRank order
    pos = {n: i for i, n in enumerate(pr_sorted)}
    seed_positions = sorted(pos[n] for n in seed)
    out["seed_pagerank_rank_percentiles"] = {
        "min": seed_positions[0],
        "p25": seed_positions[len(seed_positions) // 4],
        "median": seed_positions[len(seed_positions) // 2],
        "p75": seed_positions[3 * len(seed_positions) // 4],
        "max": seed_positions[-1],
        "n_in_top_2370": sum(1 for p in seed_positions if p < 2370),
    }

    # (b) layering vs PageRank: correlation between layer index and -log(pagerank) over Rest
    rest_with_layer = [n for n in layers if n not in seed]  # layers includes seed at layer 0
    # actually layers maps ALL kernel nodes (seed at 0) -> use full
    xs_layer = [layers[n] for n in layers]
    ys_neglogpr = [-math.log(pr_full[n]) for n in layers]
    out["layer_vs_neglog_pagerank_pearson_kernel"] = pearson(xs_layer, ys_neglogpr)
    # spearman: high pagerank should be low layer => negative
    out["layer_vs_pagerank_spearman_kernel"] = spearman(
        {n: -layers[n] for n in layers}, {n: pr_full[n] for n in layers})

    # (c) PageRank vs degree (the falsifier check)
    out["pagerank_vs_indegree_spearman_full"] = spearman(pr_full, {n: indeg[n] for n in nodes})
    out["pagerank_vs_outdegree_spearman_full"] = spearman(pr_full, {n: outdeg[n] for n in nodes})
    # within the SCC: undamped Perron vs in-degree (inside SCC)
    indeg_scc = {n: 0 for n in scc_nodes}
    for s, ts in scc_adj.items():
        for t in ts:
            indeg_scc[t] += 1
    out["perron_scc_vs_indegree_scc_spearman"] = spearman(perron_scc, indeg_scc)
    out["perron_scc_vs_pagerank_scc_spearman"] = spearman(perron_scc, pr_scc)
    out["perron_scc_vs_pagerank_full_spearman"] = spearman(
        perron_scc, {n: pr_full[n] for n in scc_nodes})
    # do top undamped-Perron nodes lie in the seed?
    perron_sorted = sorted(scc_nodes, key=lambda n: perron_scc[n], reverse=True)
    seed_in_scc = seed & largest_scc
    out["seed_nodes_in_largest_scc"] = len(seed_in_scc)
    for K in (50, 100, 200, 500, 1000):
        topK = set(perron_sorted[:K])
        out.setdefault("perron_topK_in_seed", {})[str(K)] = {
            "n": len(topK & seed_in_scc), "frac": len(topK & seed_in_scc) / K}

    # top lists with labels
    out["top30_pagerank_full"] = [
        {"node": n, "label": build.labels.get(n, n), "pagerank": pr_full[n],
         "indeg": indeg[n], "outdeg": outdeg[n],
         "in_kernel": n in kernel, "in_core": n in core, "in_seed": n in seed,
         "layer": layers.get(n)}
        for n in pr_sorted[:30]]
    out["top30_undamped_perron_largest_scc"] = [
        {"node": n, "label": build.labels.get(n, n), "perron": perron_scc[n],
         "indeg_scc": indeg_scc[n], "indeg_full": indeg[n], "in_core": n in core,
         "in_seed": n in seed, "layer": layers.get(n)}
        for n in perron_sorted[:30]]
    out["top30_pagerank_largest_scc"] = [
        {"node": n, "label": build.labels.get(n, n), "pagerank_scc": pr_scc[n],
         "in_core": n in core, "in_seed": n in seed}
        for n in sorted(scc_nodes, key=lambda n: pr_scc[n], reverse=True)[:30]]
    # the combinatorial seed top (degree score), for side-by-side
    out["top30_combinatorial_seed_by_degreescore"] = [
        {"node": n, "label": build.labels.get(n, n),
         "degree_score": indeg[n] + outdeg[n], "pagerank_full": pr_full[n],
         "pagerank_rank": pos[n]}
        for n in sorted(seed, key=lambda n: indeg[n] + outdeg[n], reverse=True)[:30]]

    # how many SCCs in the kernel; Frobenius normal form layering = condensation DAG depth
    out["kernel_scc_size_histogram"] = dict(Counter(len(c) for c in analysis.kernel_sccs))
    out["kernel_scc_count"] = len(analysis.kernel_sccs)
    out["source_scc_count"] = len(analysis.source_sccs)

    Path("reports/perron-frobenius-oewn.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("wrote reports/perron-frobenius-oewn.json")
    print(json.dumps({k: v for k, v in out.items()
                      if not k.startswith("top30")}, indent=2)[:4000])


if __name__ == "__main__":
    main()
