"""Spectral-valuation comparison report for the OEWN paper-wordnet digraph.

Builds the paper-wordnet graph (the same surface the repo computes the
combinatorial kernel/seed on), then for each spectral variant
(forward/reverse PageRank on the full graph; un-damped Perron on the largest
kernel-SCC under both orientations) compares the ranking against:

  (a) combinatorial seed membership
  (b) the FVS heuristic degree-score (internal_out + internal_in on the kernel)
  (c) Kernel / Core / Satellite layers
  (d) in/out-degree (null)
  + a degree-preserving randomized-edge null

Writes reports/spectral-valuation-oewn.json (data) and prints a summary.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from meanings.graph_analysis import (
    analyze_kernel,
    induced_subgraph,
    reverse_adjacency,
)
from meanings.spectral_analysis import (
    degree_rank_scores,
    label_shuffled_layers,
    overlap_at_k,
    perron_scores,
    randomized_edge_null,
    rank_positions,
    scc_local_eigenvectors,
    spearman,
)
from meanings.wordnet_pipeline import build_paper_wordnet_graph

WATCH_WORDS = ["small", "large", "white", "plant", "body", "water", "part", "form", "act", "various", "born", "english"]


def watch_lookup(node_list, labels):
    """Map watch lemma -> the node key whose lemma part matches (prefer the highest-degree later)."""
    out = {}
    for w in WATCH_WORDS:
        cands = [n for n in node_list if n.split("::", 1)[0] == w]
        if cands:
            out[w] = cands
    return out


def best_rank_for_word(word, cand_nodes, pos_map):
    """Best (smallest) rank over the candidate nodes for a lemma."""
    ranks = [pos_map[n] for n in cand_nodes if n in pos_map]
    return min(ranks) if ranks else None


def main():
    print("building paper-wordnet graph (oewn:2024)...", flush=True)
    build = build_paper_wordnet_graph()
    nodes = build.nodes
    adj = build.adjacency
    node_list = list(nodes)
    n_nodes = len(node_list)
    n_edges = sum(len(v) for v in adj.values())
    print(f"nodes={n_nodes} edges={n_edges}", flush=True)

    print("kernel analysis (exact-small-greedy seed, source-union core)...", flush=True)
    analysis = analyze_kernel(nodes, adj, seed_method="exact-small-greedy", core_policy="source-union")
    kernel = analysis.kernel_nodes
    core = analysis.core_nodes
    sats = analysis.satellite_nodes
    seed = set(analysis.seed_nodes)
    layers = analysis.layer_by_node
    kernel_adj = induced_subgraph(kernel, adj)
    kernel_rev = reverse_adjacency(kernel, kernel_adj)
    largest_scc = max(analysis.kernel_sccs, key=len)
    print(f"kernel={len(kernel)} core={len(core)} sats={len(sats)} seed={len(seed)} "
          f"largest_kernel_scc={len(largest_scc)} kernel_sccs={len(analysis.kernel_sccs)}", flush=True)

    # FVS heuristic degree-score on the kernel (the exact key choose_feedback_vertex uses)
    fvs_score = {
        n: sum(1 for t in kernel_adj.get(n, ()) if t in kernel and t != n)
           + sum(1 for s in kernel_rev.get(n, ()) if s in kernel and s != n)
        for n in kernel
    }
    # global degree nulls
    indeg = {n: 0 for n in node_list}
    for ts in adj.values():
        for t in ts:
            indeg[t] += 1
    outdeg = {n: len(adj.get(n, ())) for n in node_list}

    # ---- spectral variants ----
    print("forward (authority) PageRank, full graph...", flush=True)
    pr_fwd = perron_scores(adj, nodes, orientation="forward", component_policy="damped-full", iters=300)
    print(f"  converged={pr_fwd.converged} iters={pr_fwd.iterations}", flush=True)

    print("reverse PageRank (transpose), full graph...", flush=True)
    pr_rev = perron_scores(adj, nodes, orientation="reverse", component_policy="damped-full", iters=300)
    print(f"  converged={pr_rev.converged} iters={pr_rev.iterations}", flush=True)

    print("un-damped Perron on largest kernel SCC (forward orientation)...", flush=True)
    perron_fwd = perron_scores(adj, largest_scc, orientation="forward", component_policy="largest-scc", iters=800)
    print(f"  lambda={perron_fwd.dominant_eigenvalue:.4f} converged={perron_fwd.converged} iters={perron_fwd.iterations}", flush=True)

    print("un-damped Perron on largest kernel SCC (reverse orientation)...", flush=True)
    perron_rev = perron_scores(adj, largest_scc, orientation="reverse", component_policy="largest-scc", iters=800)
    print(f"  lambda={perron_rev.dominant_eigenvalue:.4f} converged={perron_rev.converged} iters={perron_rev.iterations}", flush=True)

    # nontrivial small-SCC eigenvectors (reverse) -- count + a few examples
    print("scc-local eigenvectors (reverse, kernel)...", flush=True)
    kernel_rev_oriented = reverse_adjacency(kernel, kernel_adj)
    local_rev = scc_local_eigenvectors(kernel_rev_oriented, kernel, min_size=2, iters=400)
    print(f"  nontrivial kernel SCCs (reverse-oriented): {len(local_rev)}", flush=True)

    # ---- null: degree-preserving edge swap, reverse PageRank, on the kernel ----
    print("degree-preserving randomized-edge null (reverse PageRank, kernel)...", flush=True)
    null_rev = randomized_edge_null(kernel_adj, kernel, orientation="reverse",
                                    component_policy="damped-full", seed=1, swaps_per_edge=8, iters=200)
    print(f"  swaps {null_rev.notes.get('swaps_done')}/{null_rev.notes.get('swaps_target')}", flush=True)
    layers_shuf = label_shuffled_layers(layers, seed=1) if layers else {}

    # ============================ comparisons ============================ #
    out: dict[str, object] = {}
    out["graph"] = {"nodes": n_nodes, "edges": n_edges, "lexicon": "oewn:2024", "graph_type": "paper-wordnet"}
    out["kernel"] = {
        "kernel": len(kernel), "core": len(core), "satellites": len(sats), "seed": len(seed),
        "kernel_sccs": len(analysis.kernel_sccs), "source_sccs": len(analysis.source_sccs),
        "largest_kernel_scc": len(largest_scc),
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "n_layers": (max(layers.values()) + 1) if layers else 0,
        "perron_lambda_largest_scc_forward": perron_fwd.dominant_eigenvalue,
        "perron_lambda_largest_scc_reverse": perron_rev.dominant_eigenvalue,
        "nontrivial_kernel_sccs_reverse": len(local_rev),
    }

    # restrict score maps to the kernel for the headline FVS comparisons
    def on_kernel(d):
        return {k: v for k, v in d.items() if k in kernel}

    pr_fwd_k = on_kernel(pr_fwd.scores)
    pr_rev_k = on_kernel(pr_rev.scores)
    indeg_k = {n: float(indeg[n]) for n in kernel}
    outdeg_k = {n: float(outdeg[n]) for n in kernel}
    seed_indicator = {n: (1.0 if n in seed else 0.0) for n in kernel}
    core_indicator = {n: (1.0 if n in core else 0.0) for n in kernel}
    layer_score = {n: float(-layers[n]) for n in layers}  # higher = shallower

    spectral_maps = {
        "reverse_pagerank_full": pr_rev.scores,
        "forward_pagerank_full": pr_fwd.scores,
        "perron_largest_scc_reverse": perron_rev.scores,
        "perron_largest_scc_forward": perron_fwd.scores,
    }
    baselines = {
        "fvs_degree_score_kernel": fvs_score,
        "seed_membership_kernel": seed_indicator,
        "core_membership_kernel": core_indicator,
        "indegree_kernel": indeg_k,
        "outdegree_kernel": outdeg_k,
        "layer_shallowness_kernel": layer_score,
    }
    comp: dict[str, dict[str, object]] = {}
    for sname, smap in spectral_maps.items():
        smap_k = on_kernel(smap)
        entry: dict[str, object] = {}
        for bname, bmap in baselines.items():
            rho = spearman(smap_k, bmap)
            entry[f"spearman_vs_{bname}"] = rho
        # overlap@k with the FVS degree-score top
        for K in (50, 100, 200, 500, 1000, 2370):
            entry[f"overlap@{K}_vs_fvs_degree_score"] = overlap_at_k(smap_k, fvs_score, K)
        # seed recall at k
        seed_in_kernel = seed & kernel
        order = sorted(smap_k, key=lambda x: smap_k[x], reverse=True)
        for K in (100, 500, 1000, 2370):
            topK = set(order[:K])
            entry[f"seed_recall@{K}"] = len(topK & seed_in_kernel) / max(1, len(seed_in_kernel))
            entry[f"seed_precision@{K}"] = len(topK & seed_in_kernel) / K
        comp[sname] = entry
    out["comparisons_on_kernel"] = comp

    # full-graph degree correlations of the two PageRanks (orientation contrast)
    out["full_graph"] = {
        "reverse_pagerank_vs_indegree_spearman": spearman(pr_rev.scores, {n: float(indeg[n]) for n in node_list}),
        "reverse_pagerank_vs_outdegree_spearman": spearman(pr_rev.scores, {n: float(outdeg[n]) for n in node_list}),
        "forward_pagerank_vs_indegree_spearman": spearman(pr_fwd.scores, {n: float(indeg[n]) for n in node_list}),
        "forward_pagerank_vs_outdegree_spearman": spearman(pr_fwd.scores, {n: float(outdeg[n]) for n in node_list}),
        "reverse_vs_forward_pagerank_spearman": spearman(pr_rev.scores, pr_fwd.scores),
        "reverse_pagerank_vs_total_degree_spearman": spearman(
            pr_rev.scores, {n: float(indeg[n] + outdeg[n]) for n in node_list}),
    }

    # null comparison: reverse PageRank on the real kernel vs on the degree-preserved random kernel
    out["null_models"] = {
        "reverse_pagerank_real_vs_randomized_edge_spearman": spearman(pr_rev_k, null_rev.scores),
        "reverse_pagerank_real_vs_degree_total_spearman": spearman(
            pr_rev_k, {n: float(indeg[n] + outdeg[n]) for n in kernel}),
        "randomized_edge_null_vs_degree_total_spearman": spearman(
            null_rev.scores, {n: float(indeg[n] + outdeg[n]) for n in kernel}),
        "layer_shallowness_real_vs_shuffled_spearman": (
            spearman(layer_score, {n: float(-layers_shuf[n]) for n in layers_shuf}) if layers_shuf else None),
        "comment": ("real reverse-PageRank should track degree+structure; the randomized-edge null "
                    "keeps every node's in/out degree, so residual correlation = pure degree, and the gap "
                    "real-vs-null minus real-vs-degree is the structural signal."),
    }

    # ---- watch words: where do small/large/white/plant/body/water land? ----
    out["watch_words"] = {}
    for sname, smap in spectral_maps.items():
        pos = rank_positions(smap)
        m = len(pos)
        entry = {}
        for w in WATCH_WORDS:
            cands = [nd for nd in node_list if nd.split("::", 1)[0] == w and nd in pos]
            if not cands:
                entry[w] = None
                continue
            best = min(pos[nd] for nd in cands)
            entry[w] = {"best_rank": best, "of": m, "percentile": round(100.0 * best / m, 3),
                        "node": min(cands, key=lambda nd: pos[nd])}
        out["watch_words"][sname] = entry
    # and where they land on the FVS degree-score (reference)
    fvs_pos = rank_positions(fvs_score)
    m = len(fvs_pos)
    out["watch_words"]["fvs_degree_score_kernel"] = {}
    for w in WATCH_WORDS:
        cands = [nd for nd in fvs_pos if nd.split("::", 1)[0] == w]
        if cands:
            best = min(fvs_pos[nd] for nd in cands)
            out["watch_words"]["fvs_degree_score_kernel"][w] = {
                "best_rank": best, "of": m, "percentile": round(100.0 * best / m, 3),
                "node": min(cands, key=lambda nd: fvs_pos[nd])}
        else:
            out["watch_words"]["fvs_degree_score_kernel"][w] = None

    # ---- top lists ----
    def top_list(smap, k, restrict=None):
        keys = smap if restrict is None else {x: smap[x] for x in smap if x in restrict}
        order = sorted(keys, key=lambda x: keys[x], reverse=True)[:k]
        return [{"node": x, "label": build.labels.get(x, x), "score": smap[x],
                 "indeg": indeg.get(x), "outdeg": outdeg.get(x),
                 "in_kernel": x in kernel, "in_core": x in core, "in_seed": x in seed,
                 "fvs_score": fvs_score.get(x), "layer": layers.get(x)} for x in order]

    out["top30"] = {
        "reverse_pagerank_full": top_list(pr_rev.scores, 30),
        "forward_pagerank_full": top_list(pr_fwd.scores, 30),
        "perron_largest_scc_reverse": top_list(perron_rev.scores, 30),
        "perron_largest_scc_forward": top_list(perron_fwd.scores, 30),
        "fvs_degree_score_kernel": top_list(fvs_score, 30),
    }
    # a few small-SCC examples (reverse-oriented eigenvectors)
    out["small_scc_examples_reverse"] = [
        {"size": b["size"], "lambda": b["dominant_eigenvalue"],
         "members": [{"node": nd, "label": build.labels.get(nd, nd), "score": sc}
                     for nd, sc in sorted(b["scores"].items(), key=lambda kv: kv[1], reverse=True)[:6]]}
        for b in local_rev[1:6]  # skip the giant one
    ]
    out["kernel_scc_size_histogram"] = dict(sorted(Counter(len(c) for c in analysis.kernel_sccs).items()))

    Path("reports/spectral-valuation-oewn.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("\nwrote reports/spectral-valuation-oewn.json", flush=True)

    # ----- console summary -----
    print("\n=== SUMMARY ===")
    print(f"graph: {n_nodes} nodes / {n_edges} edges; kernel {len(kernel)}; largest kernel SCC {len(largest_scc)}")
    for sname in spectral_maps:
        e = comp[sname]
        print(f"\n[{sname}]")
        print(f"  vs FVS degree-score (kernel) : rho = {e['spearman_vs_fvs_degree_score_kernel']}")
        print(f"  vs seed membership (kernel)  : rho = {e['spearman_vs_seed_membership_kernel']}")
        print(f"  vs core membership (kernel)  : rho = {e['spearman_vs_core_membership_kernel']}")
        print(f"  vs in-degree (kernel)        : rho = {e['spearman_vs_indegree_kernel']}")
        print(f"  vs out-degree (kernel)       : rho = {e['spearman_vs_outdegree_kernel']}")
        print(f"  vs layer-shallowness (kernel): rho = {e['spearman_vs_layer_shallowness_kernel']}")
        print(f"  overlap@500 vs FVS top       : {e['overlap@500_vs_fvs_degree_score']:.3f}")
        print(f"  seed recall@2370             : {e['seed_recall@2370']:.3f}")
        ww = out["watch_words"][sname]
        print("  watch words (best rank / total):")
        for w in ["small", "large", "white", "plant", "body", "water"]:
            v = ww.get(w)
            print(f"    {w:8s}: {v['best_rank'] if v else 'absent'} / {v['of'] if v else '-'}"
                  + (f"  (p{v['percentile']})" if v else ""))
    print("\nfull-graph orientation contrast:")
    for k, v in out["full_graph"].items():
        print(f"  {k}: {v}")
    print("\nnull models:")
    for k, v in out["null_models"].items():
        if k != "comment":
            print(f"  {k}: {v}")

    # explicit verdict on the reverse-PageRank prediction
    rho_seed_deg = comp["reverse_pagerank_full"]["spearman_vs_fvs_degree_score_kernel"]
    ww_rev = out["watch_words"]["reverse_pagerank_full"]
    near_top = {w: (ww_rev[w]["percentile"] if ww_rev.get(w) else None) for w in
                ["small", "large", "white", "plant", "body", "water"]}
    print("\n=== VERDICT (reverse-PageRank prediction) ===")
    print(f"  predicted: rho(reverse-PageRank, FVS degree-score) > 0.6  -> actual rho = {rho_seed_deg}")
    print(f"  predicted: small/large/white/plant/body/water near the TOP -> actual percentiles = {near_top}")
    holds = (rho_seed_deg is not None and rho_seed_deg > 0.6
             and all(p is not None and p < 25.0 for p in near_top.values()))
    print(f"  => prediction holds: {holds}")


if __name__ == "__main__":
    main()
