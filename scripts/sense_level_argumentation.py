"""Agenda #3: the rival-sense attack layer on the sense-level OEWN graph, and the
bipolar-AF / ADF semantics over it.

Builds the sense-level paper-WordNet support graph (``oewn:2024``, local ``wn`` data),
attaches the rival-sense *attack* layer (two senses of the same form attack each
other, cross-POS), then:

1. reports the attack layer: ordered/unordered edge counts, the distribution of
   rival-sense clique sizes, how many sense nodes are in a nontrivial clique;
2. runs the Kernel analysis on the support graph (sign-correct);
3. builds two Dung AFs over the sense graph and over its Kernel:
   - **Model A** (attacks only): just the rival-sense clique edges -> a disjoint
     union of cliques. Stable extensions: exactly one per chosen reading per clique,
     so the count is the product of clique sizes. (Multiplicity is exact but vacuous
     -- the lexicon wiring plays no role.)
   - **Model B** (bipolar / Cayrol derived): support edges + rival-sense attacks,
     flattened to a Dung AF via Cayrol & Lagasquie-Schiex 2005 derived defeats. The
     support structure couples the cliques; stable existence is now non-trivial.
4. decides stable existence with z3 (``argumentation.af_sat.find_stable_extension``)
   on a small Kernel-SCC slice (Model B) and -- time-boxed -- on the whole sense
   Kernel (Model B); computes the grounded extension; enumerates preferred extensions
   on the small slice; runs ``enforce_skeptical`` on a handful of slice nodes;
5. runs the h-categoriser ranking semantics over the bipolar (support+attack) graph
   and reports rho-with-degree + the top words;
6. writes ``reports/sense-level-argumentation.json``.

Run: ``uv run python scripts/sense_level_argumentation.py``
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

from argumentation.af_sat import find_stable_extension
from argumentation.af_sat import grounded_extension as af_sat_grounded
# (cayrol_derived_defeats used inside derived_dung_framework, not here)
from argumentation.dung import ArgumentationFramework, grounded_extension, preferred_extensions
from argumentation.enforcement import enforce_skeptical
from argumentation.ranking import h_categoriser_ranking

from meanings.argumentation_bridge import derived_dung_framework, edges_of
from meanings.graph_analysis import (
    analyze_kernel,
    induced_subgraph,
    strongly_connected_components,
)
from meanings.wordnet_pipeline import build_sense_level_paper_wordnet_graph_with_attacks

REPORT_JSON = Path(__file__).resolve().parent.parent / "reports" / "sense-level-argumentation.json"
KERNEL_DERIVED_DEFEAT_TIME_CAP_S = 180.0
KERNEL_STABLE_Z3_TIME_CAP_S = 240.0
SLICE_SCC_COUNT = 6  # small Kernel SCCs that contain rival-sense cliques
SLICE_MAX_SCC_NODES = 14  # keep brute-force preferred enumeration feasible


def _outdegree(adj: dict[str, set[str]]) -> dict[str, int]:
    return {n: len(t) for n, t in adj.items()}


def _spearman(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")

    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def main() -> None:
    t0 = time.perf_counter()
    print("Building sense-level support graph + rival-sense attack layer...")
    g = build_sense_level_paper_wordnet_graph_with_attacks()
    print(f"  nodes={len(g.nodes)} support_edges={sum(len(t) for t in g.supports.values())} "
          f"attack_edges(ordered)={g.attack_edge_count} time={time.perf_counter()-t0:.1f}s")

    # --- 1. attack-layer descriptive stats -------------------------------------
    clique_sizes = Counter(len(members) for members in g.rivalry_cliques.values())
    nodes_in_clique = sum(len(members) for members in g.rivalry_cliques.values())
    attack_stats = {
        "sense_nodes": len(g.nodes),
        "support_edges": sum(len(t) for t in g.supports.values()),
        "attack_edges_ordered": g.attack_edge_count,
        "attack_pairs_unordered": g.unordered_attack_pair_count,
        "rival_sense_clique_count": len(g.rivalry_cliques),
        "rival_sense_clique_size_histogram": dict(sorted(clique_sizes.items())),
        "sense_nodes_in_nontrivial_clique": nodes_in_clique,
        "fraction_sense_nodes_in_clique": nodes_in_clique / len(g.nodes),
        "largest_clique_size": max((len(m) for m in g.rivalry_cliques.values()), default=0),
        "largest_cliques": sorted(
            ((k, len(m)) for k, m in g.rivalry_cliques.items()), key=lambda kv: -kv[1]
        )[:15],
    }
    # multiplicativity ceiling for Model A (product of clique sizes): report log10.
    log10_product = sum(len(m) * math.log10(len(m)) for m in g.rivalry_cliques.values())
    attack_stats["model_a_stable_extension_count_log10"] = log10_product
    print(f"  rival cliques: {len(g.rivalry_cliques)}  nodes in cliques: {nodes_in_clique}  "
          f"log10(Model-A stable count) ~= {log10_product:.1f}")

    # --- 2. Kernel on the support graph ---------------------------------------
    print("Kernel analysis on the support graph...")
    tk = time.perf_counter()
    analysis = analyze_kernel(g.nodes, g.supports)
    kernel_nodes = analysis.kernel_nodes
    kernel_support = induced_subgraph(kernel_nodes, g.supports)
    kernel_attacks = induced_subgraph(kernel_nodes, g.attacks)
    kernel_stats = {
        "kernel_nodes": len(kernel_nodes),
        "kernel_sccs": len(analysis.kernel_sccs),
        "seed_nodes": len(analysis.seed_nodes),
        "seed_method": analysis.seed_method,
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "kernel_support_edges": sum(len(t) for t in kernel_support.values()),
        "kernel_attack_edges_ordered": sum(len(t) for t in kernel_attacks.values()),
        "kernel_nodes_in_clique": sum(1 for n in kernel_nodes if g.attacks[n]),
        "time_s": time.perf_counter() - tk,
    }
    print(f"  kernel_nodes={len(kernel_nodes)} sccs={len(analysis.kernel_sccs)} "
          f"kernel_nodes_in_clique={kernel_stats['kernel_nodes_in_clique']} "
          f"time={kernel_stats['time_s']:.1f}s")

    # --- 3a. Model A: attacks only, full sense graph --------------------------
    # The attacks adjacency is exactly the disjoint union of form-cliques. Stable
    # extensions = product over cliques of clique size; grounded = empty inside
    # cliques, everything-else-untouched outside. We report the structure, not the
    # (astronomically large) enumeration.
    model_a = {
        "description": "Dung AF = rival-sense attack edges only (disjoint clique union)",
        "stable_existence": True,  # every clique-union AF has stable extensions
        "stable_extension_count_log10": log10_product,
        "grounded_extension_size": len(g.nodes) - nodes_in_clique,  # singletons IN, clique nodes UNDEC
        "note": "multiplicity is exact and multiplicative but vacuous: no support edge plays any role",
    }

    # --- 3b. Model B: bipolar / Cayrol derived, small Kernel-SCC slice --------
    print("Selecting a small Kernel-SCC slice that contains rival-sense cliques...")
    # Prefer SCCs that contain *internal* rival-sense attacks (rival senses both in
    # the same SCC) -- otherwise the Cayrol-derived defeat set is empty and the AF is
    # trivial. Fall back to any SCC with a clique member if too few qualify.
    sccs_internal = [scc for scc in analysis.kernel_sccs
                     if 2 <= len(scc) <= SLICE_MAX_SCC_NODES
                     and any(g.attacks[n] & scc for n in scc)]
    sccs_any = [scc for scc in analysis.kernel_sccs
                if 2 <= len(scc) <= SLICE_MAX_SCC_NODES and any(g.attacks[n] for n in scc)]
    pool = sccs_internal + [s for s in sccs_any if s not in sccs_internal]
    small_sccs = sorted(pool, key=lambda s: (-len(s), tuple(sorted(s))))[:SLICE_SCC_COUNT]
    n_internal = len(sccs_internal)
    slice_results: list[dict] = []
    for scc in small_sccs:
        sub_supports = induced_subgraph(scc, g.supports)
        sub_attacks = induced_subgraph(scc, g.attacks)
        af = derived_dung_framework(scc, sub_supports, sub_attacks)
        try:
            preferred = preferred_extensions(af)
        except Exception as exc:  # noqa: BLE001
            preferred = None
            pref_err = repr(exc)
        else:
            pref_err = None
        grounded = grounded_extension(af)
        stable = find_stable_extension(af)
        # enforce_skeptical on up to 3 nodes of the SCC
        enforce = []
        for arg in sorted(scc)[:3]:
            try:
                res = enforce_skeptical(af, arg, semantics="preferred", max_cost=2)
                enforce.append({"argument": arg, "cost": res.cost,
                                "edit_additions": sorted(map(list, res.edit.additions)) if hasattr(res.edit, "additions") else None,
                                "n_extensions": len(res.extensions)})
            except Exception as exc:  # noqa: BLE001
                enforce.append({"argument": arg, "error": repr(exc)})
        sample = sorted(scc)[:6]
        slice_results.append({
            "scc_size": len(scc),
            "nodes_sample": [g.labels.get(n, n) for n in sample],
            "support_edges": sum(len(t) for t in sub_supports.values()),
            "attack_edges_ordered": sum(len(t) for t in sub_attacks.values()),
            "derived_dung_defeats": len(af.defeats),
            "grounded_size": len(grounded),
            "preferred_count": None if preferred is None else len(preferred),
            "preferred_error": pref_err,
            "preferred_sizes": None if preferred is None else sorted(len(e) for e in preferred),
            "stable_exists": stable is not None,
            "stable_size": None if stable is None else len(stable),
            "enforce_skeptical": enforce,
        })
        print(f"  SCC|{len(scc)}|: defeats={len(af.defeats)} grounded={len(grounded)} "
              f"preferred={None if preferred is None else len(preferred)} "
              f"stable_exists={stable is not None}")

    # --- 3c. Whole sense Kernel: attacks-only Dung AF (scalable) -------------
    # A first attempt ran the full Cayrol derived-defeat closure on the whole
    # 12,142-node Kernel; it blew past 9 GB RSS without terminating (an attacker on
    # any node of a support SCC ends up attacking everything that SCC reaches, and
    # the Kernel's giant SCC reaches almost everything -> a near-complete defeat
    # relation). So the Cayrol-derived Model B is only feasible per small SCC (above).
    # On the whole Kernel we report the *attacks-only* Dung AF (rival-sense clique
    # edges, no support propagation): scalable, and it answers the headline question
    # "is the Kernel-with-attacks AF UNSAT or SAT for stable?" directly.
    print("Whole sense Kernel: attacks-only Dung AF (rival-sense cliques restricted to Kernel)...")
    kernel_b: dict = {"model": "attacks-only Dung AF on the Kernel (no support propagation)",
                      "cayrol_derived_whole_kernel": "infeasible: closure blew past 9 GB RSS without terminating; feasible only per small SCC"}
    td = time.perf_counter()
    # restrict each rival clique to the Kernel
    kernel_clique_sizes = Counter()
    for members in g.rivalry_cliques.values():
        in_k = [m for m in members if m in kernel_nodes]
        if len(in_k) >= 2:
            kernel_clique_sizes[len(in_k)] += 1
    log10_kernel_product = sum(c * (k * math.log10(k)) for k, c in kernel_clique_sizes.items())
    af_attacks_only = ArgumentationFramework(arguments=frozenset(kernel_nodes),
                                             defeats=edges_of(kernel_nodes, kernel_attacks))
    gr = grounded_extension(af_attacks_only)
    tg = time.perf_counter() - td
    ts = time.perf_counter()
    stable = find_stable_extension(af_attacks_only)
    kernel_b.update({
        "kernel_rival_clique_count": sum(kernel_clique_sizes.values()),
        "kernel_rival_clique_size_histogram": dict(sorted(kernel_clique_sizes.items())),
        "kernel_attack_edges_ordered": sum(len(t) for t in kernel_attacks.values()),
        "grounded_size": len(gr),
        "grounded_time_s": tg,
        "stable_exists": stable is not None,
        "stable_size": None if stable is None else len(stable),
        "stable_z3_time_s": time.perf_counter() - ts,
        "stable_extension_count_log10": log10_kernel_product,
        "note": ("the attacks-only Kernel AF is a disjoint union of rival-sense cliques "
                 "(plus isolated nodes), so it always has stable extensions; their count "
                 "is the product of Kernel-restricted clique sizes -- a true but vacuous "
                 "multiplicativity (the lexicon's support wiring plays no role here)"),
    })
    print(f"  attacks-only Kernel AF: stable_exists={stable is not None} "
          f"grounded={len(gr)} log10(stable count)~={log10_kernel_product:.0f}")

    # --- 5. ranking semantics over the bipolar (support+attack) graph --------
    # h-categoriser is for attack graphs; we feed it BOTH the support edges (as
    # attacks -- the sign-incorrect lemma-level finding to re-test) and, separately,
    # the rival-sense attacks. We use the Kernel subgraph for tractability.
    print("h-categoriser ranking on the Kernel: (a) support-as-attack, (b) +rival attacks...")
    ranking_out: dict = {}
    try:
        # variant (a): support edges as attacks (re-run of the lemma-level finding)
        af_sup = ArgumentationFramework(arguments=frozenset(kernel_nodes),
                                        defeats=edges_of(kernel_nodes, kernel_support))
        tr = time.perf_counter()
        rk_a = h_categoriser_ranking(af_sup)
        outdeg = _outdegree(kernel_support)  # attackers-of count == in-degree of support edge target... actually rank by #attackers
        # number of attackers of n under support-as-attack = in-degree in support graph
        indeg: dict[str, int] = {n: 0 for n in kernel_nodes}
        for s, ts_ in kernel_support.items():
            for t in ts_:
                indeg[t] += 1
        order_a = sorted(kernel_nodes, key=lambda n: rk_a.scores.get(n, 0.0), reverse=True)
        # spearman of h-cat score with -in-degree (more attackers -> lower score)
        nodes_list = list(kernel_nodes)
        rho_a = _spearman([rk_a.scores.get(n, 0.0) for n in nodes_list],
                          [-indeg[n] for n in nodes_list])
        ranking_out["support_as_attack"] = {
            "h_cat_time_s": time.perf_counter() - tr,
            "rho_score_vs_neg_indegree": rho_a,
            "top_words": [g.labels.get(n, n) for n in order_a[:25]],
        }
        print(f"  (a) support-as-attack: rho(score, -indeg)={rho_a:.3f}")

        # variant (b): support edges + rival-sense attacks both as attacks
        combined = edges_of(kernel_nodes, kernel_support) | edges_of(kernel_nodes, kernel_attacks)
        af_comb = ArgumentationFramework(arguments=frozenset(kernel_nodes), defeats=combined)
        tr2 = time.perf_counter()
        rk_b = h_categoriser_ranking(af_comb)
        attackers_b: dict[str, int] = {n: 0 for n in kernel_nodes}
        for (s, t) in combined:
            attackers_b[t] += 1
        order_b = sorted(kernel_nodes, key=lambda n: rk_b.scores.get(n, 0.0), reverse=True)
        rho_b = _spearman([rk_b.scores.get(n, 0.0) for n in nodes_list],
                          [-attackers_b[n] for n in nodes_list])
        # also rho between the two rankings
        rho_ab = _spearman([rk_a.scores.get(n, 0.0) for n in nodes_list],
                           [rk_b.scores.get(n, 0.0) for n in nodes_list])
        ranking_out["support_plus_rival_as_attack"] = {
            "h_cat_time_s": time.perf_counter() - tr2,
            "rho_score_vs_neg_attackercount": rho_b,
            "rho_vs_support_only_ranking": rho_ab,
            "top_words": [g.labels.get(n, n) for n in order_b[:25]],
        }
        print(f"  (b) support+rival: rho(score, -#attackers)={rho_b:.3f}  rho(a,b)={rho_ab:.3f}")
    except Exception as exc:  # noqa: BLE001
        ranking_out["error"] = repr(exc)
        print(f"  ranking failed: {exc!r}")

    payload = {
        "lexicon_id": g.lexicon_id,
        "attack_layer": attack_stats,
        "kernel_support_graph": kernel_stats,
        "model_a_attacks_only": model_a,
        "model_b_small_kernel_scc_slice": {
            "kernel_sccs_with_internal_rival_attacks": n_internal,
            "kernel_sccs_with_any_clique_member_in_size_range": len([
                s for s in analysis.kernel_sccs
                if 2 <= len(s) <= SLICE_MAX_SCC_NODES and any(g.attacks[n] for n in s)
            ]),
            "slice": slice_results,
        },
        "model_b_whole_sense_kernel": kernel_b,
        "ranking_semantics_bipolar": ranking_out,
        "total_runtime_s": time.perf_counter() - t0,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"\nWrote {REPORT_JSON}  (total {payload['total_runtime_s']:.1f}s)")


if __name__ == "__main__":
    main()
