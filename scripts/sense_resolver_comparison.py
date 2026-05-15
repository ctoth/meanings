"""Edge-budget-controlled comparison: audit-baseline vs IC-fallback resolver.

Builds two sense-level support graphs:

  (A) baseline   -- build_sense_level_paper_wordnet_graph(polysemy_fallback=False)
                    (the published 925,283 candidate matches -> 423,927 resolved,
                    499,860 ambiguous_skipped behaviour)
  (B) ic_fallback -- build_sense_level_paper_wordnet_graph(polysemy_fallback=True)
                    (same resolver, but on a same-POS overlap tie / zero-overlap
                    or a global tie / zero-overlap, fall back to the lowest-rank
                    sense within the candidate IC instead of skipping)

For each graph: analyze_kernel with exact-small-greedy + source-union; report
node / edge / Kernel / Core / Satellite / seed / residual-cyclic-SCC counts;
literal-self-loop count; in-degree for the named genus victim words and
whether their senses are in the Kernel.

Verdict triage (audit finding #2 + synthesis section 3/7/10):
  (i)   sense_Kernel(B) materially smaller than lemma-Kernel (18,151)
        -> artifact-dissolution claim survives the edge-budget control
  (ii)  sense_Kernel(B) about the same as lemma-Kernel
        -> the original 12,142 shrink was mostly dropped edges
  (iii) sense_Kernel(B) materially larger than lemma-Kernel
        -> genus-word reincorporation creates cycles the lemma graph hid via
           lemma-collapse; the comparison is fundamentally non-apples-to-apples
           and the synthesis should retire the size comparison

Outputs:
  reports/sense-resolver-comparison.json
  reports/sense-resolver-comparison-summary.md
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from meanings.graph_analysis import analyze_kernel
from meanings.wordnet_pipeline import (
    SenseLevelGraphBuild,
    build_sense_level_paper_wordnet_graph,
)


GENUS_VICTIMS = ["line", "head", "break", "take", "make", "set", "run", "point"]
LEMMA_LEVEL_KERNEL = 18151  # from synthesis section 3 / sense_ingestion_rebuild constants
LEMMA_LEVEL_SELF_LOOPS = 3413
SEED_METHOD = "exact-small-greedy"
CORE_POLICY = "source-union"


def self_loop_count(build: SenseLevelGraphBuild) -> int:
    return sum(1 for node, targets in build.adjacency.items() if node in targets)


def emit(message: str, progress_log: Path | None = None) -> None:
    timestamped = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(timestamped, flush=True)
    if progress_log is not None:
        progress_log.parent.mkdir(parents=True, exist_ok=True)
        with progress_log.open("a", encoding="utf-8") as handle:
            handle.write(timestamped)
            handle.write("\n")


def acquire_lock(lock_path: Path | None) -> None:
    if lock_path is None:
        return
    if lock_path.exists():
        raise RuntimeError(
            f"Run lock already exists: {lock_path}. "
            "Remove it only after confirming no resolver comparison is active."
        )
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "argv": sys.argv,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    atexit.register(lambda: lock_path.exists() and lock_path.unlink())


def indegree_of(build: SenseLevelGraphBuild) -> dict[str, int]:
    indeg: dict[str, int] = {node: 0 for node in build.adjacency}
    for targets in build.adjacency.values():
        for target in targets:
            indeg[target] = indeg.get(target, 0) + 1
    return indeg


def genus_victim_status(
    build: SenseLevelGraphBuild,
    kernel_nodes: set[str],
) -> dict[str, dict[str, Any]]:
    """For each genus victim lemma: total senses, senses in Kernel, sum incoming edges."""
    indeg = indegree_of(build)
    out: dict[str, dict[str, Any]] = {}
    for lemma in GENUS_VICTIMS:
        sense_nodes = [
            node
            for node, meta in build.node_metadata.items()
            if str(meta["lemma"]) == lemma
        ]
        if not sense_nodes:
            out[lemma] = {
                "total_senses": 0,
                "senses_in_kernel": 0,
                "total_in_degree": 0,
                "max_in_degree": 0,
                "kernel_sense_pos_counts": {},
            }
            continue
        in_kernel = [n for n in sense_nodes if n in kernel_nodes]
        pos_counts: dict[str, int] = {}
        for n in in_kernel:
            p = str(build.node_metadata[n]["pos"])
            pos_counts[p] = pos_counts.get(p, 0) + 1
        out[lemma] = {
            "total_senses": len(sense_nodes),
            "senses_in_kernel": len(in_kernel),
            "total_in_degree": sum(indeg.get(n, 0) for n in sense_nodes),
            "max_in_degree": max((indeg.get(n, 0) for n in sense_nodes), default=0),
            "kernel_sense_pos_counts": pos_counts,
        }
    return out


def project_to_ic(build: SenseLevelGraphBuild) -> tuple[set[str], dict[str, set[str]]]:
    """Collapse senses to ICs. One IC node per ic_id; edge u_ic -> v_ic if any
    sense edge crosses ICs. Self-loops within an IC are dropped (an IC defining
    itself is not informative for the FVS computation)."""
    sense_to_ic: dict[str, str] = {}
    for node, meta in build.node_metadata.items():
        sense_to_ic[node] = str(meta["ic_id"])
    ic_nodes: set[str] = set(sense_to_ic.values())
    ic_adj: dict[str, set[str]] = {ic: set() for ic in ic_nodes}
    for u, targets in build.adjacency.items():
        u_ic = sense_to_ic.get(u)
        if u_ic is None:
            continue
        for v in targets:
            v_ic = sense_to_ic.get(v)
            if v_ic is None or v_ic == u_ic:
                continue
            ic_adj[u_ic].add(v_ic)
    return ic_nodes, ic_adj


def restrict_to_ic_representatives(
    build: SenseLevelGraphBuild, seed_nodes: list[str]
) -> list[str]:
    """P2: take a seed of sense nodes, pick one representative per IC.

    Choose the representative with the highest in-degree in the sense graph
    (most-cited sense of the IC's seed members); break ties by sense id.
    """
    indeg = indegree_of(build)
    by_ic: dict[str, list[str]] = {}
    for node in seed_nodes:
        ic_id = str(build.node_metadata[node]["ic_id"])
        by_ic.setdefault(ic_id, []).append(node)
    reps: list[str] = []
    for ic_id, members in sorted(by_ic.items()):
        rep = max(members, key=lambda n: (indeg.get(n, 0), n))
        reps.append(rep)
    return reps


def p2_seed_payload(
    *,
    lexicon_id: str,
    build: SenseLevelGraphBuild,
    analysis: object,
    reps: list[str],
) -> dict[str, Any]:
    """Export the P2 strict seed as a first-class IC artifact.

    P2 is the chosen surface from the round-8 comparison: compute the FVS on
    the sense graph, then restrict to one representative sense per IC at export.
    """
    indeg = indegree_of(build)
    by_ic: dict[str, list[str]] = {}
    for node in analysis.seed_nodes:  # type: ignore[attr-defined]
        by_ic.setdefault(str(build.node_metadata[node]["ic_id"]), []).append(node)
    rows: list[dict[str, Any]] = []
    for sense_id in sorted(reps, key=lambda node: (str(build.node_metadata[node]["ic_id"]), node)):
        meta = build.node_metadata[sense_id]
        ic_id = str(meta["ic_id"])
        rows.append(
            {
                "ic_id": ic_id,
                "representative_sense_id": sense_id,
                "representative_lemma": str(meta["lemma"]),
                "representative_pos": str(meta["pos"]),
                "representative_in_degree": indeg.get(sense_id, 0),
                "source_synset": str(meta.get("source_synset", "")),
                "lexicality": str(meta.get("lexicality", "")),
                "seed_sense_count_for_ic": len(by_ic.get(ic_id, [])),
                "seed_sense_ids_for_ic": sorted(by_ic.get(ic_id, [])),
            }
        )
    return {
        "schema_version": 1,
        "artifact_id": "oewn-sense-p2-ic-seed",
        "surface": "strict_graph_seed_p2_sense_ic",
        "policy": "feedback vertex result on IC-fallback sense graph, restricted to one representative sense per IC at export",
        "lexicon_id": lexicon_id,
        "resolver_id": "ic_fallback_polysemy_true__sense_fvs__ic_export_p2",
        "workflow": "sense_graph_fvs_then_one_representative_ic_at_export",
        "argv": sys.argv,
        "graph": {
            "graph_type": "sense_ic_fallback",
            "node_count": len(build.nodes),
            "edge_count": analysis.edges,  # type: ignore[attr-defined]
            "self_loop_count": self_loop_count(build),
            "resolution_stats": dict(build.resolution_stats),
        },
        "analysis": {
            "seed_method": SEED_METHOD,
            "core_policy": CORE_POLICY,
            "kernel_count": len(analysis.kernel_nodes),  # type: ignore[attr-defined]
            "sense_seed_count": len(analysis.seed_nodes),  # type: ignore[attr-defined]
            "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,  # type: ignore[attr-defined]
        },
        "export": {
            "representative_policy": "highest_in_degree_seed_sense_per_ic_then_highest_sense_id",
            "ic_seed_count": len({row["ic_id"] for row in rows}),
        },
        "seed_ics": rows,
        "diagnostics": {
            "sense_level_genus_victims": genus_victim_status(build, set(analysis.kernel_nodes)),  # type: ignore[attr-defined]
        },
    }


def summarize(
    label: str,
    build: SenseLevelGraphBuild,
    analysis: object,
    runtime_seconds: float,
) -> dict[str, Any]:
    return {
        "label": label,
        "node_count": len(build.nodes),
        "edge_count": analysis.edges,  # type: ignore[attr-defined]
        "edges_per_node": analysis.edges / max(len(build.nodes), 1),  # type: ignore[attr-defined]
        "self_loop_count": self_loop_count(build),
        "kernel_node_count": len(analysis.kernel_nodes),  # type: ignore[attr-defined]
        "kernel_scc_count": len(analysis.kernel_sccs),  # type: ignore[attr-defined]
        "core_node_count": len(analysis.core_nodes),  # type: ignore[attr-defined]
        "satellite_node_count": len(analysis.satellite_nodes),  # type: ignore[attr-defined]
        "seed_node_count": len(analysis.seed_nodes),  # type: ignore[attr-defined]
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,  # type: ignore[attr-defined]
        "resolution_stats": dict(build.resolution_stats),
        "genus_victims": genus_victim_status(build, analysis.kernel_nodes),  # type: ignore[attr-defined]
        "runtime_seconds": runtime_seconds,
    }


def classify_verdict(
    baseline_kernel: int,
    ic_fallback_kernel: int,
    lemma_kernel: int,
) -> tuple[str, str]:
    delta = ic_fallback_kernel - lemma_kernel
    rel = abs(delta) / lemma_kernel
    if delta < 0 and rel >= 0.2:
        verdict = "(i)"
        statement = (
            f"sense-Kernel with IC-fallback ({ic_fallback_kernel}) is still "
            f"materially smaller than the lemma-Kernel ({lemma_kernel}, "
            f"{rel:.0%} less). The artifact-dissolution claim survives the "
            "edge-budget control: even with the genus-word edges restored, the "
            "sense graph carries a smaller cyclic core."
        )
    elif rel < 0.2:
        verdict = "(ii)"
        statement = (
            f"sense-Kernel with IC-fallback ({ic_fallback_kernel}) is about the "
            f"same size as the lemma-Kernel ({lemma_kernel}, "
            f"{abs(delta) / lemma_kernel:.0%} delta). The original sense-level "
            f"Kernel shrink {baseline_kernel} vs {lemma_kernel} was substantially "
            "dropped edges, not artifact dissolution: when the resolver keeps the "
            "genus-word edges, the cyclic core comes back. The audit's charge survives."
        )
    else:
        verdict = "(iii)"
        statement = (
            f"sense-Kernel with IC-fallback ({ic_fallback_kernel}) is materially "
            f"larger than the lemma-Kernel ({lemma_kernel}, "
            f"{rel:.0%} more). The genus-word reincorporation creates new sense-"
            "level cycles that the lemma graph had as different (lemma-collapsed) "
            "cycles. The comparison is non-apples-to-apples and the synthesis "
            "should drop the size comparison."
        )
    return verdict, statement


def write_outputs(
    payload: dict[str, Any],
    json_path: Path,
    md_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Sense Resolver Comparison",
        "",
        "Edge-budget-controlled comparison of the audit-baseline resolver vs",
        "the IC-fallback resolver. See `reports/sense-resolver-fix.md` for the",
        "full writeup.",
        "",
        "## Side-by-side",
        "",
        "| Metric | baseline | ic_fallback | lemma-level |",
        "|---|---|---|---|",
    ]
    b = payload["baseline"]
    f = payload["ic_fallback"]
    rows = [
        ("nodes", b["node_count"], f["node_count"], "160,010"),
        ("edges", b["edge_count"], f["edge_count"], "n/a"),
        ("edges/node", f"{b['edges_per_node']:.2f}", f"{f['edges_per_node']:.2f}", "4.24"),
        ("self-loops", b["self_loop_count"], f["self_loop_count"], LEMMA_LEVEL_SELF_LOOPS),
        ("Kernel", b["kernel_node_count"], f["kernel_node_count"], LEMMA_LEVEL_KERNEL),
        ("Core", b["core_node_count"], f["core_node_count"], "510"),
        ("Satellites", b["satellite_node_count"], f["satellite_node_count"], "17,641"),
        ("seed", b["seed_node_count"], f["seed_node_count"], "5,044"),
        ("residual cyclic SCCs", b["residual_cyclic_scc_count"], f["residual_cyclic_scc_count"], "0"),
    ]
    for name, bv, fv, lv in rows:
        lines.append(f"| {name} | {bv} | {fv} | {lv} |")
    lines.extend(["", "## Genus victims (high-polysemy words from audit finding #2)", ""])
    lines.append("Format: `senses_in_kernel / total_senses (total_in_degree)`")
    lines.append("")
    lines.append("| Lemma | baseline | ic_fallback |")
    lines.append("|---|---|---|")
    for lemma in GENUS_VICTIMS:
        bgv = b["genus_victims"][lemma]
        fgv = f["genus_victims"][lemma]
        lines.append(
            f"| `{lemma}` | "
            f"{bgv['senses_in_kernel']}/{bgv['total_senses']} ({bgv['total_in_degree']}) | "
            f"{fgv['senses_in_kernel']}/{fgv['total_senses']} ({fgv['total_in_degree']}) |"
        )
    lines.extend(["", "## Verdict", ""])
    lines.append(f"- **{payload['verdict']['code']}** — {payload['verdict']['statement']}")
    lines.extend(["", "## IC-projection P1 vs P2", ""])
    p1 = payload["ic_projection"]["P1_ic_graph"]
    p2 = payload["ic_projection"]["P2_restrict_at_export"]
    lines.append(f"- P1 (collapse IC -> one node, then FVS): seed = `{p1['seed_size']}`")
    lines.append(f"- P2 (sense-graph FVS, then restrict to one rep per IC): seed = `{p2['seed_size']}`")
    lines.append(f"- Delta: `{p2['seed_size'] - p1['seed_size']}`")
    lines.append(f"- IC ids in P1-only: `{len(payload['ic_projection']['p1_only_ics'])}`")
    lines.append(f"- IC ids in P2-only: `{len(payload['ic_projection']['p2_only_ics'])}`")
    lines.append(f"- IC ids in both: `{len(payload['ic_projection']['both_ics'])}`")
    lines.extend([
        "",
        "Recommendation: " + payload["ic_projection"]["recommendation"],
        "",
        "## Self-loop prediction check",
        "",
        f"- baseline self-loops: `{b['self_loop_count']}` "
        f"(vs lemma-level `{LEMMA_LEVEL_SELF_LOOPS}`)",
        f"- ic_fallback self-loops: `{f['self_loop_count']}` "
        f"(vs lemma-level `{LEMMA_LEVEL_SELF_LOOPS}`)",
        "",
        "The synthesis section 3 prediction was 'near-zero on the sense graph'.",
        "Whether that holds after the resolver fix is shown above.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument(
        "--json", default="reports/sense-resolver-comparison.json", type=Path
    )
    parser.add_argument(
        "--md", default="reports/sense-resolver-comparison-summary.md", type=Path
    )
    parser.add_argument(
        "--p2-seed", default="data/oewn-sense-p2-ic-seed.json", type=Path
    )
    parser.add_argument(
        "--progress-log", default=None, type=Path,
        help="Optional progress log for long non-interactive runs.",
    )
    parser.add_argument(
        "--lock", default=Path("reports/sense-resolver-comparison.lock"), type=Path,
        help="Lock file preventing overlapping resolver comparison runs. Use --lock '' to disable.",
    )
    args = parser.parse_args()
    lock_arg = str(args.lock).strip().lower()
    lock_path = None if lock_arg in {"", ".", "none", "false"} else args.lock
    acquire_lock(lock_path)
    if args.progress_log and args.progress_log.exists():
        args.progress_log.unlink()

    emit("[1/4] Building baseline sense-level graph (polysemy_fallback=False)...", args.progress_log)
    t0 = time.time()
    baseline_build = build_sense_level_paper_wordnet_graph(args.lexicon, polysemy_fallback=False)
    baseline_build_runtime = time.time() - t0
    emit(
        f"      build complete in {baseline_build_runtime:.1f}s -- "
        f"{len(baseline_build.nodes)} nodes, "
        f"{sum(len(t) for t in baseline_build.adjacency.values())} edges",
        args.progress_log,
    )
    t1 = time.time()
    baseline_analysis = analyze_kernel(
        baseline_build.nodes, baseline_build.adjacency,
        seed_method=SEED_METHOD, core_policy=CORE_POLICY,
    )
    baseline_analysis_runtime = time.time() - t1
    emit(
        f"      analyze_kernel complete in {baseline_analysis_runtime:.1f}s -- "
        f"Kernel {len(baseline_analysis.kernel_nodes)}",
        args.progress_log,
    )

    emit("[2/4] Building IC-fallback sense-level graph (polysemy_fallback=True)...", args.progress_log)
    t2 = time.time()
    fallback_build = build_sense_level_paper_wordnet_graph(args.lexicon, polysemy_fallback=True)
    fallback_build_runtime = time.time() - t2
    emit(
        f"      build complete in {fallback_build_runtime:.1f}s -- "
        f"{len(fallback_build.nodes)} nodes, "
        f"{sum(len(t) for t in fallback_build.adjacency.values())} edges",
        args.progress_log,
    )
    t3 = time.time()
    fallback_analysis = analyze_kernel(
        fallback_build.nodes, fallback_build.adjacency,
        seed_method=SEED_METHOD, core_policy=CORE_POLICY,
    )
    fallback_analysis_runtime = time.time() - t3
    emit(
        f"      analyze_kernel complete in {fallback_analysis_runtime:.1f}s -- "
        f"Kernel {len(fallback_analysis.kernel_nodes)}",
        args.progress_log,
    )

    emit("[3/4] IC-projection comparison...", args.progress_log)
    # P1: project to IC graph, then FVS
    t4 = time.time()
    ic_nodes, ic_adj = project_to_ic(fallback_build)
    p1_analysis = analyze_kernel(
        ic_nodes, ic_adj,
        seed_method=SEED_METHOD, core_policy=CORE_POLICY,
    )
    p1_runtime = time.time() - t4
    p1_seed_ics = set(p1_analysis.seed_nodes)
    emit(
        f"      P1: {len(ic_nodes)} IC nodes, "
        f"{p1_analysis.edges} edges, Kernel {len(p1_analysis.kernel_nodes)}, "
        f"seed {len(p1_analysis.seed_nodes)} in {p1_runtime:.1f}s",
        args.progress_log,
    )
    # P2: take the sense-graph FVS seed, restrict to one rep per IC
    p2_reps = restrict_to_ic_representatives(fallback_build, fallback_analysis.seed_nodes)
    p2_seed_ics = {
        str(fallback_build.node_metadata[n]["ic_id"]) for n in p2_reps
    }
    emit(
        f"      P2: sense-seed {len(fallback_analysis.seed_nodes)} -> "
        f"{len(p2_reps)} IC reps ({len(p2_seed_ics)} unique ICs)",
        args.progress_log,
    )

    # which ICs each path has that the other doesn't
    p1_only = sorted(p1_seed_ics - p2_seed_ics)
    p2_only = sorted(p2_seed_ics - p1_seed_ics)
    both = sorted(p1_seed_ics & p2_seed_ics)

    verdict_code, verdict_statement = classify_verdict(
        len(baseline_analysis.kernel_nodes),
        len(fallback_analysis.kernel_nodes),
        LEMMA_LEVEL_KERNEL,
    )

    emit("[4/4] Writing outputs...", args.progress_log)
    payload: dict[str, Any] = {
        "lexicon_id": args.lexicon,
        "baseline": summarize(
            "baseline (audit-baseline, ambiguous_skipped)",
            baseline_build, baseline_analysis,
            baseline_build_runtime + baseline_analysis_runtime,
        ),
        "ic_fallback": summarize(
            "ic_fallback (polysemy_fallback=True)",
            fallback_build, fallback_analysis,
            fallback_build_runtime + fallback_analysis_runtime,
        ),
        "verdict": {
            "code": verdict_code,
            "statement": verdict_statement,
            "lemma_level_kernel_reference": LEMMA_LEVEL_KERNEL,
            "ic_fallback_kernel": len(fallback_analysis.kernel_nodes),
            "baseline_kernel": len(baseline_analysis.kernel_nodes),
        },
        "ic_projection": {
            "P1_ic_graph": {
                "ic_node_count": len(ic_nodes),
                "ic_edge_count": p1_analysis.edges,
                "ic_kernel_size": len(p1_analysis.kernel_nodes),
                "seed_size": len(p1_analysis.seed_nodes),
                "residual_cyclic_scc_count": p1_analysis.residual_cyclic_scc_count,
                "runtime_seconds": p1_runtime,
            },
            "P2_restrict_at_export": {
                "sense_seed_size": len(fallback_analysis.seed_nodes),
                "ic_rep_count": len(p2_reps),
                "seed_size": len(p2_seed_ics),
            },
            "p1_only_ics": p1_only[:200],
            "p2_only_ics": p2_only[:200],
            "both_ics": both[:200],
            "p1_only_count": len(p1_only),
            "p2_only_count": len(p2_only),
            "both_count": len(both),
            "recommendation": _ic_projection_recommendation(
                len(p1_analysis.seed_nodes), len(p2_seed_ics),
                p1_analysis.residual_cyclic_scc_count,
            ),
        },
    }
    write_outputs(payload, args.json, args.md)
    p2_payload = p2_seed_payload(
        lexicon_id=args.lexicon,
        build=fallback_build,
        analysis=fallback_analysis,
        reps=p2_reps,
    )
    args.p2_seed.parent.mkdir(parents=True, exist_ok=True)
    args.p2_seed.write_text(
        json.dumps(p2_payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    emit(f"      wrote {args.json} + {args.md} + {args.p2_seed}", args.progress_log)
    emit(f"Verdict: {verdict_code} -- see {args.md}", args.progress_log)


def _ic_projection_recommendation(p1_seed: int, p2_seed: int, p1_residual: int) -> str:
    if p1_residual > 0:
        return (
            "P2 (restrict sense-graph seed at export). P1's IC-projected graph "
            "has residual cyclic SCCs after the seed -- the projection step "
            "collapsed too many edges into cycles, so the IC-graph FVS isn't "
            "a clean acyclic-closure witness."
        )
    if p1_seed <= p2_seed:
        return (
            "P1 (FVS on the IC-projected graph). P1's seed is at least as "
            "tight as P2's, and it computes the FVS on the surface the "
            "strict-seed export actually targets (one IC = one referential "
            "unit) instead of computing it on the sense graph and projecting "
            "after, which can include redundant IC members."
        )
    return (
        "P2 (restrict sense-graph seed at export). P2's seed is tighter; "
        "the sense-graph FVS has access to the full edge structure and the "
        "per-IC representative is then the highest-in-degree-cited sense, "
        "which is a more informative anchor than 'this IC was in the FVS' "
        "would be."
    )


if __name__ == "__main__":
    main()
