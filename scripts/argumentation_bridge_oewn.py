"""Run grounded (and probe stable) argumentation semantics on the full OEWN graph.

Builds the paper-faithful OEWN definition digraph (``oewn:2024``, local ``wn`` data),
runs the repo's leaf-stripping Kernel analysis, then:

1. builds two AF encodings (Dung attack reading, bipolar support reading) via
   :mod:`meanings.argumentation_bridge`;
2. computes and times the grounded extension of each;
3. compares the attack-reading grounded extension against the
   ``{Rest, Kernel, Core, Satellites, seed}`` partition (Jaccard, set differences,
   examples);
4. probes the harder end: z3-backed stable-extension search on each Kernel SCC, and
   on the whole Kernel subgraph;
5. writes numbers to ``reports/argumentation-bridge-oewn.json``.

Run: ``uv run python scripts/argumentation_bridge_oewn.py``
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from collections import deque

from argumentation.dung import ArgumentationFramework, grounded_extension
from argumentation.bipolar import bipolar_grounded_extension

from meanings.argumentation_bridge import (
    dung_attack_framework,
    bipolar_support_framework,
    scc_attack_framework,
)
from meanings.graph_analysis import Adjacency, analyze_kernel, induced_subgraph, reverse_adjacency
from meanings.wordnet_pipeline import build_paper_wordnet_graph

REPORT_JSON = Path(__file__).resolve().parent.parent / "reports" / "argumentation-bridge-oewn.json"
STABLE_PROBE_TIME_BUDGET_S = 300.0  # stop probing more SCCs once cumulative time exceeds this
LIBRARY_GROUNDED_KERNEL_TIME_CAP_S = 120.0  # run argumentation.grounded_extension on the Kernel under a cap


def grounded_extension_fast(nodes: set[str], adjacency: Adjacency) -> frozenset[str]:
    """Linear-time grounded extension under the *attack* reading (``u -> v`` = u attacks v).

    Standard worklist labelling: a node is IN once all its attackers are OUT; a node is
    OUT once at least one attacker is IN; the remainder is UNDEC. The grounded extension
    is the IN set. We do this ourselves because ``argumentation.dung.grounded_extension``
    re-scans the growing accepted set inside ``defends`` and is super-quadratic in the
    extension size -- it does not finish on a 160k-node graph in any reasonable time.
    """
    rev = reverse_adjacency(nodes, adjacency)  # rev[v] = attackers of v
    live_attackers = {v: sum(1 for a in rev.get(v, ()) if a in nodes) for v in nodes}
    label: dict[str, str] = {}
    queue: deque[str] = deque(v for v in nodes if live_attackers[v] == 0)
    while queue:
        v = queue.popleft()
        if v in label:
            continue
        # Decide v: if it still has live (un-OUT) attackers, it can only be here because
        # they were all OUT at enqueue time -> IN. Otherwise it has no attackers -> IN.
        label[v] = "IN"
        for w in adjacency.get(v, ()):  # v attacks w
            if w in nodes and w not in label:
                # w is attacked by an IN node -> OUT
                label[w] = "OUT"
                # propagate: w being OUT may free w's targets' attacker counts
                for x in adjacency.get(w, ()):
                    if x in nodes and x not in label:
                        live_attackers[x] -= 1
                        if live_attackers[x] == 0:
                            queue.append(x)
    return frozenset(v for v, lab in label.items() if lab == "IN")


def _library_grounded_worker(nodes: set[str], adjacency: Adjacency, q) -> None:  # pragma: no cover
    import time as _t
    from argumentation.dung import grounded_extension as _ge
    from meanings.argumentation_bridge import dung_attack_framework as _mk
    t = _t.perf_counter()
    af = _mk(set(nodes), adjacency)
    ext = _ge(af)
    q.put({"completed": True, "size": len(ext), "seconds": _t.perf_counter() - t})


def run_library_grounded_with_cap(nodes: set[str], adjacency: Adjacency, cap_s: float) -> dict[str, object]:
    """Run ``argumentation.dung.grounded_extension`` in a child process with a wall-clock cap.

    The library impl is super-quadratic in extension size; this lets us measure how far it
    gets at the Kernel scale without risking the whole experiment.
    """
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_library_grounded_worker, args=(nodes, adjacency, q))
    t0 = time.perf_counter()
    p.start()
    p.join(cap_s)
    if p.is_alive():
        p.terminate()
        p.join()
        return {"completed": False, "timed_out_after_s": time.perf_counter() - t0, "cap_s": cap_s,
                "note": "argumentation.dung.grounded_extension did not finish within the cap on the Kernel subgraph"}
    try:
        return q.get_nowait()
    except Exception as exc:  # pragma: no cover
        return {"completed": False, "error": repr(exc)}


def overlap_stats(a: set[str], b: set[str], examples: int = 8) -> dict[str, object]:
    inter = a & b
    union = a | b
    only_a = a - b
    only_b = b - a
    return {
        "size_a": len(a),
        "size_b": len(b),
        "intersection": len(inter),
        "jaccard": (len(inter) / len(union)) if union else 1.0,
        "only_a_count": len(only_a),
        "only_b_count": len(only_b),
        "only_a_examples": sorted(only_a)[:examples],
        "only_b_examples": sorted(only_b)[:examples],
    }


def main() -> None:
    t0 = time.perf_counter()
    print("Building paper-wordnet graph (oewn:2024) ...", flush=True)
    build = build_paper_wordnet_graph("oewn:2024")
    nodes = build.nodes
    adjacency = build.adjacency
    n_edges = sum(len(t) for t in adjacency.values())
    print(f"  nodes={len(nodes)} edges={n_edges}  ({time.perf_counter()-t0:.1f}s)", flush=True)

    print("Running analyze_kernel ...", flush=True)
    tk = time.perf_counter()
    analysis = analyze_kernel(nodes, adjacency)
    print(f"  kernel={len(analysis.kernel_nodes)} core={len(analysis.core_nodes)} "
          f"sats={len(analysis.satellite_nodes)} seed={len(analysis.seed_nodes)} "
          f"sccs={len(analysis.kernel_sccs)} residual_cyclic_sccs={analysis.residual_cyclic_scc_count} "
          f"({time.perf_counter()-tk:.1f}s)", flush=True)

    rest = nodes - analysis.kernel_nodes
    partition = {
        "rest": rest,
        "kernel": set(analysis.kernel_nodes),
        "core": set(analysis.core_nodes),
        "satellites": set(analysis.satellite_nodes),
        "seed": set(analysis.seed_nodes),
    }

    # --- sanity: our fast grounded matches the library on a tiny graph ---
    _tiny_adj = {"a": {"b"}, "b": {"c"}, "c": set()}
    assert grounded_extension_fast(set(_tiny_adj), _tiny_adj) == grounded_extension(
        dung_attack_framework(set(_tiny_adj), _tiny_adj)
    ), "fast grounded disagrees with argumentation.dung.grounded_extension on a chain"
    _cyc = {"a": {"b"}, "b": {"a"}}
    assert grounded_extension_fast(set(_cyc), _cyc) == frozenset()

    # --- grounded extension, attack reading (full 160k graph), our fast labelling ---
    print("Building Dung attack AF (full graph) ...", flush=True)
    tb = time.perf_counter()
    dung_af = dung_attack_framework(nodes, adjacency)
    build_dung_s = time.perf_counter() - tb
    print(f"  AF built: {len(dung_af.arguments)} args, {len(dung_af.defeats)} defeats ({build_dung_s:.2f}s)",
          flush=True)
    print("Computing grounded extension (fast labelling) ...", flush=True)
    tg = time.perf_counter()
    grounded_attack = grounded_extension_fast(nodes, adjacency)
    grounded_attack_s = time.perf_counter() - tg
    print(f"  |grounded(attack)|={len(grounded_attack)}  fast_grounded={grounded_attack_s:.2f}s", flush=True)

    # --- grounded extension, support reading (bipolar, empty defeats) ---
    # NOTE: argumentation.bipolar.bipolar_grounded_extension recomputes the Cayrol defeat
    # closure inside defends() once per argument -- ~160k recomputations of a closure over
    # 677k support edges -- so it does not finish at this scale. But the answer is
    # analytically determined: with an empty defeat relation the closure is empty, every
    # argument is (vacuously) defended, and the grounded extension is the whole argument
    # set. We construct the BAF (to confirm it builds) and compute |grounded| analytically,
    # and only run the library's bipolar_grounded_extension on a tiny graph as a check.
    print("Building bipolar support AF (full graph) ...", flush=True)
    tb = time.perf_counter()
    baf = bipolar_support_framework(nodes, adjacency)
    build_baf_s = time.perf_counter() - tb
    assert bipolar_grounded_extension(bipolar_support_framework(set(_tiny_adj), _tiny_adj)) == frozenset(_tiny_adj)
    grounded_support_size = len(baf.arguments)  # = len(nodes), analytically
    print(f"  BAF built: {len(baf.arguments)} args, {len(baf.supports)} supports, 0 defeats ({build_baf_s:.2f}s); "
          f"|grounded(support)|={grounded_support_size} (analytic: empty-defeat BAF => grounded = all args)",
          flush=True)

    # --- cross-check our fast grounded against the library on the Kernel subgraph,
    #     and time how the library impl behaves at the (smaller) Kernel scale ---
    kernel_set = set(analysis.kernel_nodes)
    kernel_adj = induced_subgraph(kernel_set, adjacency)
    tg = time.perf_counter()
    grounded_attack_kernel_fast = grounded_extension_fast(kernel_set, kernel_adj)
    grounded_kernel_fast_s = time.perf_counter() - tg
    print(f"  |grounded(attack, Kernel-subgraph, fast)|={len(grounded_attack_kernel_fast)}  ({grounded_kernel_fast_s:.3f}s)",
          flush=True)
    library_kernel = run_library_grounded_with_cap(kernel_set, kernel_adj, LIBRARY_GROUNDED_KERNEL_TIME_CAP_S)
    print(f"  library grounded on Kernel: {library_kernel}", flush=True)

    # --- alignment of attack-reading grounded extension with the partition ---
    determinate = rest | grounded_attack  # candidate "the part that's forced"
    alignment = {name: overlap_stats(grounded_attack, members) for name, members in partition.items()}
    alignment["rest_plus_grounded_vs_nodes"] = overlap_stats(determinate, nodes)
    # is grounded(attack) entirely outside the Kernel? (i.e. == determinate acyclic part?)
    grounded_in_kernel = grounded_attack & set(analysis.kernel_nodes)
    rest_not_grounded = rest - grounded_attack

    # --- stable-extension probe via z3, per Kernel SCC ---
    print("Probing stable extensions (z3) on Kernel SCCs ...", flush=True)
    try:
        from argumentation.af_sat import find_stable_extension
        z3_available = True
    except Exception as exc:  # pragma: no cover - depends on env
        z3_available = False
        find_stable_extension = None
        print(f"  z3 / af_sat unavailable: {exc}", flush=True)

    scc_probe: list[dict[str, object]] = []
    trivial_singleton_count = 0
    trivial_self_loop_count = 0
    cumulative_probe_s = 0.0
    sccs_sorted = sorted(analysis.kernel_sccs, key=len, reverse=True)
    if z3_available:
        for i, scc in enumerate(sccs_sorted):
            if len(scc) < 2:
                # singleton SCC: cyclic only if self-loop. Trivial; just count it.
                if any(n in adjacency.get(n, set()) for n in scc):
                    trivial_self_loop_count += 1
                else:
                    trivial_singleton_count += 1
                continue
            if cumulative_probe_s > STABLE_PROBE_TIME_BUDGET_S:
                scc_probe.append({"index": i, "size": len(scc), "result": "skipped_time_budget"})
                continue
            af = scc_attack_framework(scc, adjacency)
            ts = time.perf_counter()
            try:
                ext = find_stable_extension(af)
                dt = time.perf_counter() - ts
                cumulative_probe_s += dt
                scc_probe.append({
                    "index": i, "size": len(scc), "edges": len(af.defeats),
                    "result": "sat" if ext is not None else "unsat",
                    "extension_size": (len(ext) if ext is not None else None),
                    "seconds": dt,
                })
                if i < 20 or dt > 1.0:
                    print(f"  SCC[{i}] size={len(scc)} -> {'SAT' if ext is not None else 'UNSAT'} "
                          f"({dt:.3f}s)", flush=True)
            except Exception as exc:  # pragma: no cover
                dt = time.perf_counter() - ts
                cumulative_probe_s += dt
                scc_probe.append({"index": i, "size": len(scc), "result": "error", "error": repr(exc),
                                  "seconds": dt})
                print(f"  SCC[{i}] size={len(scc)} -> ERROR {exc!r}", flush=True)

    # --- stable-extension probe on the whole Kernel subgraph ---
    kernel_stable: dict[str, object] = {}
    if z3_available:
        print("Probing stable extension (z3) on the whole Kernel subgraph ...", flush=True)
        kernel_af = dung_attack_framework(set(analysis.kernel_nodes), induced_subgraph(set(analysis.kernel_nodes), adjacency))
        ts = time.perf_counter()
        try:
            ext = find_stable_extension(kernel_af)
            dt = time.perf_counter() - ts
            kernel_stable = {
                "nodes": len(analysis.kernel_nodes),
                "edges": len(kernel_af.defeats),
                "result": "sat" if ext is not None else "unsat",
                "extension_size": (len(ext) if ext is not None else None),
                "seconds": dt,
            }
            if ext is not None:
                seed_set = set(analysis.seed_nodes)
                # In a stable extension, every outsider is attacked; outsiders form an
                # attacking set. Relation to MinSet/seed: how much do they overlap?
                outsiders = set(analysis.kernel_nodes) - ext
                kernel_stable["outsiders_count"] = len(outsiders)
                kernel_stable["seed_vs_extension"] = overlap_stats(seed_set, ext)
                kernel_stable["seed_vs_outsiders"] = overlap_stats(seed_set, outsiders)
            print(f"  Kernel stable: {kernel_stable['result']} ({dt:.2f}s)", flush=True)
        except Exception as exc:  # pragma: no cover
            dt = time.perf_counter() - ts
            kernel_stable = {"result": "error", "error": repr(exc), "seconds": dt}
            print(f"  Kernel stable: ERROR {exc!r} ({dt:.2f}s)", flush=True)

    payload = {
        "lexicon_id": "oewn:2024",
        "graph_type": "paper_wordnet",
        "node_count": len(nodes),
        "edge_count": n_edges,
        "kernel_analysis": {
            "kernel_node_count": len(analysis.kernel_nodes),
            "core_node_count": len(analysis.core_nodes),
            "satellite_node_count": len(analysis.satellite_nodes),
            "seed_node_count": len(analysis.seed_nodes),
            "rest_node_count": len(rest),
            "kernel_scc_count": len(analysis.kernel_sccs),
            "largest_kernel_scc_sizes": sorted((len(s) for s in analysis.kernel_sccs), reverse=True)[:10],
            "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        },
        "grounded": {
            "attack_reading": {
                "size": len(grounded_attack),
                "fraction_of_nodes": len(grounded_attack) / len(nodes),
                "af_build_seconds": build_dung_s,
                "fast_grounded_seconds": grounded_attack_s,
                "intersection_with_kernel": len(grounded_in_kernel),
                "rest_minus_grounded_count": len(rest_not_grounded),
                "rest_minus_grounded_examples": sorted(rest_not_grounded)[:8],
                "method": "linear worklist labelling (own impl); argumentation.dung.grounded_extension does not scale to this size",
                "kernel_subgraph": {
                    "size": len(grounded_attack_kernel_fast),
                    "fast_grounded_seconds": grounded_kernel_fast_s,
                    "library_grounded_on_kernel": library_kernel,
                },
            },
            "support_reading": {
                "size": grounded_support_size,
                "fraction_of_nodes": grounded_support_size / len(nodes),
                "baf_build_seconds": build_baf_s,
                "note": ("support-only bipolar AF has empty defeats; grounded = all arguments analytically. "
                         "argumentation.bipolar.bipolar_grounded_extension does not scale here: defends() "
                         "recomputes the Cayrol defeat closure once per argument."),
            },
        },
        "alignment_attack_grounded_vs_partition": alignment,
        "stable_probe": {
            "z3_available": z3_available,
            "nontrivial_scc_count": len(scc_probe),
            "trivial_singleton_scc_count": trivial_singleton_count,
            "trivial_self_loop_scc_count": trivial_self_loop_count,
            "scc_probe": scc_probe,
            "scc_probe_cumulative_seconds": cumulative_probe_s,
            "kernel_whole": kernel_stable,
        },
        "total_seconds": time.perf_counter() - t0,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_JSON}  (total {payload['total_seconds']:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
