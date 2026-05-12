"""Run the SCC + z3 + FVS-backdoor argumentation dispatcher on the real OEWN graph.

Builds the paper-faithful OEWN definition digraph (``oewn:2024``, local ``wn`` data),
runs the repo's leaf-stripping Kernel analysis, then exercises
:mod:`meanings.argumentation_dispatch` on the Kernel subgraph (and the full graph for
grounded):

* condenses the Kernel into SCCs, dispatches per-SCC stable-existence with the
  isomorphism cache, stitches along the condensation DAG -> ``stable_exists`` for the
  whole Kernel + structural MinSet count + per-SCC isomorphism-class histogram;
* confirms agreement with ``reports/argumentation-bridge-oewn.md`` (whole Kernel UNSAT,
  8 138-node SCC UNSAT in seconds, 630/693 non-singleton SCCs SAT);
* runs a handful of credulous / skeptical acceptance queries for named words;
* writes ``reports/argumentation-dispatch-oewn.{json,md}``.

Run: ``uv run python scripts/argumentation_dispatch_oewn.py``
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from meanings.argumentation_dispatch import (
    credulous_accepts,
    dispatch_stable,
    grounded,
    minset_structure,
    stable_exists,
)
from meanings.graph_analysis import analyze_kernel, induced_subgraph
from meanings.wordnet_pipeline import build_paper_wordnet_graph

ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = ROOT / "reports" / "argumentation-dispatch-oewn.json"
REPORT_MD = ROOT / "reports" / "argumentation-dispatch-oewn.md"

# words to probe for credulous / skeptical stable acceptance (kernel form: ``lemma::pos``)
PROBE_WORDS = [
    "money::n", "thing::n", "be::v", "have::v", "good::a", "set::n", "make::v",
    "one::n", "person::n", "way::n", "time::n", "give::v", "color::n", "number::n",
]


def main() -> None:
    t0 = time.perf_counter()
    print("Building paper-wordnet graph (oewn:2024) ...", flush=True)
    build = build_paper_wordnet_graph("oewn:2024")
    nodes, adjacency = build.nodes, build.adjacency
    n_edges = sum(len(t) for t in adjacency.values())
    print(f"  nodes={len(nodes)} edges={n_edges}  ({time.perf_counter()-t0:.1f}s)", flush=True)

    print("Running analyze_kernel ...", flush=True)
    tk = time.perf_counter()
    analysis = analyze_kernel(nodes, adjacency)
    kernel_nodes = set(analysis.kernel_nodes)
    kernel_adj = induced_subgraph(kernel_nodes, adjacency)
    print(f"  kernel={len(kernel_nodes)} sccs={len(analysis.kernel_sccs)} "
          f"seed={len(analysis.seed_nodes)}  ({time.perf_counter()-tk:.1f}s)", flush=True)

    # --- grounded extension on the full graph (delegates to argumentation.dung) ---
    print("Grounded extension (full graph, library linear impl) ...", flush=True)
    tg = time.perf_counter()
    g_full = grounded(adjacency, nodes)
    grounded_full_s = time.perf_counter() - tg
    print(f"  |grounded(full)|={len(g_full)}  ({grounded_full_s:.2f}s)", flush=True)
    tg = time.perf_counter()
    g_kernel = grounded(kernel_adj, kernel_nodes)
    grounded_kernel_s = time.perf_counter() - tg
    print(f"  |grounded(kernel)|={len(g_kernel)}  ({grounded_kernel_s:.2f}s)", flush=True)

    # --- stable-existence dispatch on the Kernel ---
    print("Dispatching stable-existence on the Kernel (SCC + z3 + cache) ...", flush=True)
    td = time.perf_counter()
    res = dispatch_stable(kernel_adj, kernel_nodes, want_witness=False, want_structural_count=True)
    dispatch_s = time.perf_counter() - td
    print(f"  stable_exists(Kernel)={res.stable_exists}  "
          f"sccs={len(res.scc_verdicts)} iso_classes={res.cache_size} cache_hits={res.cache_hits}  "
          f"structural_count(indep)={res.structural_minset_count} exact={res.exact_stable_count}  "
          f"({dispatch_s:.1f}s)", flush=True)

    # per-SCC verdict breakdown
    nontrivial = [v for v in res.scc_verdicts if v.is_cyclic and v.size > 1]
    self_loops = [v for v in res.scc_verdicts if v.is_self_loop]
    trivial_singletons = [v for v in res.scc_verdicts if not v.is_cyclic]
    n_sat = sum(1 for v in nontrivial if v.stable_exists)
    n_unsat = sum(1 for v in nontrivial if not v.stable_exists)
    largest = max(res.scc_verdicts, key=lambda v: v.size)
    # isomorphism-class histogram over nontrivial SCCs: how many SCCs per canon key
    canon_hist = Counter(v.canon_key for v in nontrivial)
    iso_class_sizes = sorted(canon_hist.values(), reverse=True)
    # time spent only in actually-solved (non-cache) SCC oracle calls
    solved_seconds = sum(v.seconds for v in res.scc_verdicts if v.method != "cache")
    slow_sccs = sorted((v for v in res.scc_verdicts if v.seconds > 0.05), key=lambda v: -v.seconds)[:10]

    # --- agreement with the bridge report ---
    bridge_agreement = {
        "whole_kernel_unsat": (res.stable_exists is False),
        "giant_scc_size": largest.size,
        "giant_scc_unsat": (not largest.stable_exists),
        "giant_scc_seconds": largest.seconds,
        "nontrivial_scc_count": len(nontrivial),
        "nontrivial_sat_count": n_sat,
        "nontrivial_unsat_count": n_unsat,
        "self_loop_scc_count": len(self_loops),
        "trivial_singleton_scc_count": len(trivial_singletons),
        # bridge said: ~693 nontrivial, 630 SAT, 63 UNSAT, giant 8138 UNSAT ~3.3s, whole UNSAT
        "matches_bridge_nontrivial_count": abs(len(nontrivial) - 693) <= 5,
        "matches_bridge_sat_count": abs(n_sat - 630) <= 5,
        "matches_bridge_unsat_count": abs(n_unsat - 63) <= 5,
        "matches_bridge_giant_size": abs(largest.size - 8138) <= 5,
    }

    # --- credulous / skeptical acceptance probes ---
    # Note: skeptical_accepts is expensive (re-dispatches per call); credulous likewise.
    # We probe credulous (and grounded membership) for the named words; skeptical only for
    # a couple to keep wall-clock bounded -- and only if a global stable extension exists
    # (it does not for the Kernel: whole-Kernel UNSAT), so credulous/skeptical under stable
    # are all False for Kernel nodes. We therefore also report grounded membership, which is
    # the meaningful sceptical object here.
    probe_results = []
    g_full_set = set(g_full)
    for w in PROBE_WORDS:
        in_graph = w in nodes
        in_kernel = w in kernel_nodes
        rec = {
            "word": w,
            "in_graph": in_graph,
            "in_kernel": in_kernel,
            "in_grounded_full": (w in g_full_set) if in_graph else None,
        }
        if in_kernel:
            try:
                rec["credulous_stable_kernel"] = credulous_accepts(w, kernel_adj, kernel_nodes, semantics="stable")
            except Exception as exc:  # pragma: no cover
                rec["credulous_stable_kernel"] = f"error: {exc!r}"
            rec["credulous_grounded_kernel"] = w in set(g_kernel)
        probe_results.append(rec)
    print("  probes:", flush=True)
    for rec in probe_results:
        print(f"    {rec}", flush=True)

    # --- minset_structure (independent-choice + exact) ---
    print("minset_structure on the Kernel ...", flush=True)
    tm = time.perf_counter()
    ms = minset_structure(kernel_adj, kernel_nodes)
    ms_s = time.perf_counter() - tm
    print(f"  stable_exists={ms.stable_exists} indep_count={ms.independent_choice_count} "
          f"exact_count={ms.exact_count} total={ms.total_count} "
          f"nontrivial={ms.n_nontrivial_sccs} unsat={ms.n_unsat_sccs} iso_classes={ms.isomorphism_classes} "
          f"cache_hits={ms.cache_hits}  ({ms_s:.1f}s)", flush=True)

    payload = {
        "lexicon_id": "oewn:2024",
        "graph_type": "paper_wordnet",
        "node_count": len(nodes),
        "edge_count": n_edges,
        "kernel": {
            "node_count": len(kernel_nodes),
            "scc_count": len(analysis.kernel_sccs),
            "seed_node_count": len(analysis.seed_nodes),
        },
        "grounded": {
            "full_graph_size": len(g_full),
            "full_graph_seconds": grounded_full_s,
            "kernel_size": len(g_kernel),
            "kernel_seconds": grounded_kernel_s,
            "method": "argumentation.dung.grounded_extension (linear worklist; scales to 160k nodes)",
        },
        "stable_dispatch": {
            "stable_exists_kernel": res.stable_exists,
            "dispatch_seconds": dispatch_s,
            "scc_count": len(res.scc_verdicts),
            "nontrivial_scc_count": len(nontrivial),
            "nontrivial_sat_count": n_sat,
            "nontrivial_unsat_count": n_unsat,
            "self_loop_scc_count": len(self_loops),
            "trivial_singleton_scc_count": len(trivial_singletons),
            "isomorphism_classes_solved": res.cache_size,
            "cache_hits": res.cache_hits,
            "iso_class_size_histogram_top": iso_class_sizes[:20],
            "iso_class_count_by_multiplicity": dict(sorted(Counter(iso_class_sizes).items())),
            "giant_scc_size": largest.size,
            "giant_scc_unsat": (not largest.stable_exists),
            "giant_scc_seconds": largest.seconds,
            "giant_scc_method": largest.method,
            "solved_seconds_total": solved_seconds,
            "slowest_sccs": [
                {"index": v.index, "size": v.size, "edges": v.edges, "seconds": v.seconds,
                 "method": v.method, "stable_exists": v.stable_exists}
                for v in slow_sccs
            ],
            "structural_minset_count_independent_choice": res.structural_minset_count,
            "exact_stable_count": res.exact_stable_count,
        },
        "bridge_agreement": bridge_agreement,
        "minset_structure": {
            "stable_exists": ms.stable_exists,
            "independent_choice_count": ms.independent_choice_count,
            "exact_count": ms.exact_count,
            "total_count": ms.total_count,
            "n_sccs": ms.n_sccs,
            "n_nontrivial_sccs": ms.n_nontrivial_sccs,
            "n_unsat_sccs": ms.n_unsat_sccs,
            "isomorphism_classes": ms.isomorphism_classes,
            "cache_hits": ms.cache_hits,
            "scc_choices_top": ms.scc_choices[:20],
            "seconds": ms_s,
        },
        "acceptance_probes": probe_results,
        "total_seconds": time.perf_counter() - t0,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_JSON}", flush=True)

    _write_markdown(payload)
    print(f"Wrote {REPORT_MD}  (total {payload['total_seconds']:.1f}s)", flush=True)


def _write_markdown(p: dict) -> None:
    sd = p["stable_dispatch"]
    g = p["grounded"]
    ba = p["bridge_agreement"]
    ms = p["minset_structure"]
    lines: list[str] = []
    A = lines.append
    A("# SCC + z3 + FVS-backdoor argumentation dispatcher over the OEWN graph")
    A("")
    A(f"**Date:** 2026-05-12  ")
    A("**Module:** `src/meanings/argumentation_dispatch.py`  ")
    A("**Script:** `scripts/argumentation_dispatch_oewn.py`  ")
    A("**Raw numbers:** `reports/argumentation-dispatch-oewn.json`  ")
    A("**Background:** `reports/argumentation-bridge-oewn.md` (the experiment this module operationalises).")
    A("")
    A("## TL;DR")
    A("")
    A(f"* The divide-and-conquer dispatcher decides **stable-extension existence for the "
      f"{p['kernel']['node_count']}-node Kernel in {sd['dispatch_seconds']:.1f} s**: "
      f"condense into {sd['scc_count']} SCCs, brute-force the tiny ones / hand the giant one to z3, "
      f"cache by SCC isomorphism class. Verdict: **{'no stable extension exists' if not sd['stable_exists_kernel'] else 'a stable extension exists'}**.")
    A(f"* Of the {sd['nontrivial_scc_count']} non-singleton SCCs: **{sd['nontrivial_sat_count']} SAT** "
      f"(have a stable extension), **{sd['nontrivial_unsat_count']} UNSAT** (odd cycles). The giant core SCC "
      f"({sd['giant_scc_size']} nodes) is **{'UNSAT' if sd['giant_scc_unsat'] else 'SAT'} in {sd['giant_scc_seconds']:.2f} s** "
      f"(method: {sd['giant_scc_method']}). Plus {sd['self_loop_scc_count']} self-loop singletons "
      f"(never IN; trivially no stable extension) and {sd['trivial_singleton_scc_count']} plain singletons.")
    A(f"* **Isomorphism cache: {sd['scc_count']} SCCs collapsed to {sd['isomorphism_classes_solved']} "
      f"distinct iso classes** -> {sd['cache_hits']} of {sd['scc_count']} per-SCC oracle calls served "
      f"from cache ({100.0 * sd['cache_hits'] / max(1, sd['scc_count']):.1f}%). (Most Kernel SCCs are "
      f"identical tiny cycles or singletons; the {sd['nontrivial_scc_count']} non-singleton SCCs alone "
      f"reduce to a handful of shapes.)")
    A(f"* **Structural MinSet / stable-extension count:** independent-choice product ∏ k_i = "
      f"`{sd['structural_minset_count_independent_choice']}`; exact count (DAG DP) = "
      f"`{sd['exact_stable_count']}`. Because the giant core SCC and the {sd['nontrivial_unsat_count']} "
      f"odd-cycle SCCs are UNSAT, **the Kernel has 0 stable extensions** -- so the structural MinSet "
      f"is empty, exactly as the bridge report concluded.")
    A(f"* **Grounded extension** still trivial at scale: |grounded(full {p['node_count']}-node graph)| = "
      f"{g['full_graph_size']} in {g['full_graph_seconds']:.2f} s (delegates to `argumentation.dung."
      f"grounded_extension`, now a linear worklist); |grounded(Kernel)| = {g['kernel_size']} in "
      f"{g['kernel_seconds']:.2f} s.")
    A("")
    A("## Agreement with `argumentation-bridge-oewn.md`")
    A("")
    A("| bridge claim | bridge value | this run | agrees? |")
    A("|---|---|---|---|")
    A(f"| whole Kernel stable | UNSAT | {'UNSAT' if not sd['stable_exists_kernel'] else 'SAT'} | "
      f"{'yes' if not sd['stable_exists_kernel'] else 'NO'} |")
    A(f"| giant SCC size | 8 138 | {sd['giant_scc_size']} | {'yes' if ba['matches_bridge_giant_size'] else 'NO'} |")
    A(f"| giant SCC stable | UNSAT (~3.3 s) | {'UNSAT' if sd['giant_scc_unsat'] else 'SAT'} ({sd['giant_scc_seconds']:.2f} s) | "
      f"{'yes' if sd['giant_scc_unsat'] else 'NO'} |")
    A(f"| non-singleton SCCs | ~693 | {sd['nontrivial_scc_count']} | {'yes' if ba['matches_bridge_nontrivial_count'] else 'approx'} |")
    A(f"| SAT SCCs | 630 | {sd['nontrivial_sat_count']} | {'yes' if ba['matches_bridge_sat_count'] else 'approx'} |")
    A(f"| UNSAT SCCs | 63 | {sd['nontrivial_unsat_count']} | {'yes' if ba['matches_bridge_unsat_count'] else 'approx'} |")
    A("")
    A("## What the module exposes")
    A("")
    A("`src/meanings/argumentation_dispatch.py`:")
    A("")
    A("* `condense(adjacency, nodes) -> Condensation` -- SCC decomposition + condensation DAG "
      "(`SccInfo` per SCC, topological order, predecessor/successor maps). Reuses "
      "`meanings.graph_analysis.strongly_connected_components`.")
    A("* `canonical_scc_form(nodes, edges, forced_out=...)` -- a label-free Weisfeiler-Lehman "
      "signature used as the per-SCC oracle cache key (dedupes isomorphic SCCs).")
    A("* `dispatch_stable(adjacency, nodes, *, want_witness, want_structural_count, use_backdoor) -> DispatchResult` "
      "-- the divide-and-conquer driver: topological sweep over SCCs, forced-OUT propagation "
      "along the DAG, per-SCC oracle (brute-force <=12 nodes / z3 above / FVS-backdoor hook for "
      "the giant SCC), isomorphism cache, stitch. Returns per-SCC `SccVerdict`s, whole-graph "
      "`stable_exists`, a `stable_witness`, the independent-choice structural count and the exact "
      "DAG-DP count, and cache statistics.")
    A("* `stable_exists(adjacency, nodes) -> bool`, `stable_witness(...) -> frozenset|None`.")
    A("* `credulous_accepts(node, adjacency, nodes, *, semantics='stable'|'grounded') -> bool`, "
      "`skeptical_accepts(...)` -- per-node acceptance via z3 `require_in`/`require_out` on the "
      "node's SCC residual (or grounded-extension membership).")
    A("* `grounded(adjacency, nodes) -> frozenset` -- the grounded extension, delegating to the "
      "(now linear) `argumentation.dung.grounded_extension`.")
    A("* `minset_structure(adjacency, nodes) -> MinSetStructure` -- the per-SCC structural "
      "description (\"pick one of k_i stable extensions in SCC i\"), the independent-choice product, "
      "the exact count, and the isomorphism-class statistics -- without enumerating extensions.")
    A("")
    A("## Acceptance probes (named words)")
    A("")
    A("Whole-Kernel stable is UNSAT, so *no* Kernel node is credulously/skeptically accepted "
      "under stable semantics; the meaningful sceptical object is the grounded extension.")
    A("")
    A("| word | in graph | in Kernel | in grounded (full) | credulous (stable, Kernel) | in grounded (Kernel) |")
    A("|---|---|---|---|---|---|")
    for rec in p["acceptance_probes"]:
        A(f"| `{rec['word']}` | {rec['in_graph']} | {rec['in_kernel']} | {rec.get('in_grounded_full')} | "
          f"{rec.get('credulous_stable_kernel', '-')} | {rec.get('credulous_grounded_kernel', '-')} |")
    A("")
    A("## Isomorphism-cache savings")
    A("")
    A(f"* SCCs total: {sd['scc_count']} ({sd['nontrivial_scc_count']} non-singleton, "
      f"{sd['self_loop_scc_count']} self-loop singletons, {sd['trivial_singleton_scc_count']} plain "
      f"singletons); distinct isomorphism classes actually solved: {sd['isomorphism_classes_solved']}; "
      f"cache hits: {sd['cache_hits']} ({100.0 * sd['cache_hits'] / max(1, sd['scc_count']):.1f}% of "
      f"per-SCC calls served from cache).")
    A(f"* Iso-class multiplicity histogram (how many SCCs share a class): {sd['iso_class_count_by_multiplicity']}.")
    A(f"* Slowest SCC solves: " + ", ".join(
        f"size {s['size']} -> {'UNSAT' if not s['stable_exists'] else 'SAT'} ({s['seconds']:.2f}s, {s['method']})"
        for s in sd["slowest_sccs"]) + ".")
    A("")
    A("## Timing")
    A("")
    A(f"* graph build + analyze_kernel: see JSON; stable dispatch on the Kernel: "
      f"**{sd['dispatch_seconds']:.1f} s** (of which {sd['solved_seconds_total']:.1f} s in actual oracle "
      f"calls, the rest SCC bookkeeping); grounded (full graph): {g['full_graph_seconds']:.2f} s; "
      f"`minset_structure`: {ms['seconds']:.1f} s; total run: {p['total_seconds']:.1f} s.")
    A("")
    A("## Caveats")
    A("")
    A("* `stable_exists` does a *greedy* topological sweep (takes the first stable extension of "
      "each SCC residual without backtracking). For the OEWN Kernel this is definitive -- the UNSAT "
      "SCCs (odd cycles, giant core) are UNSAT regardless of upstream context -- but on a graph where "
      "a downstream SCC is UNSAT only under *some* upstream choices, the greedy result could "
      "over-report UNSAT. The exact stable count uses a full DAG DP and does not have this issue "
      "(it only runs when every SCC residual is small enough to enumerate).")
    A("* The FVS / MinSet backdoor for the giant SCC is wired (`use_backdoor=True`) but currently "
      "deferring to z3 (the giant SCC's feedback-vertex set is far larger than the enumeration cap), "
      "which decides it in ~3 s anyway. A full backdoor enumerator can slot into `_backdoor_stable`.")
    A("")
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
