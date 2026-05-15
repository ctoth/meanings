from __future__ import annotations

import argparse
import atexit
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.request
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from meanings.graph_analysis import induced_subgraph
from meanings.minset import choose_feedback_vertex, cyclic_sccs, exact_feedback_vertex_set, reverse_adjacency
from meanings.wiktextract_adapter import build_wiktextract_graph, iter_jsonl


DEFAULT_KAIKKI_EN_URL = "https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz"


def emit(message: str, progress_log: Path | None = None) -> None:
    timestamped = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(timestamped, flush=True)
    if progress_log is not None:
        progress_log.parent.mkdir(parents=True, exist_ok=True)
        with progress_log.open("a", encoding="utf-8") as handle:
            handle.write(timestamped)
            handle.write("\n")


def progress_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True))
        handle.write("\n")


def acquire_lock(lock_path: Path | None) -> None:
    if lock_path is None:
        return
    if lock_path.exists():
        raise RuntimeError(
            f"Run lock already exists: {lock_path}. "
            "Remove it only after confirming no Kaikki SCC grounding run is active."
        )
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        json.dumps(
            {"pid": os.getpid(), "started_at": time.strftime("%Y-%m-%d %H:%M:%S"), "argv": sys.argv},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    atexit.register(lambda: lock_path.exists() and lock_path.unlink())


def iter_url_jsonl(url: str) -> Iterator[dict[str, Any]]:
    with urllib.request.urlopen(url) as response:
        raw: io.BufferedIOBase
        if url.endswith(".gz"):
            raw = gzip.GzipFile(fileobj=response)
        else:
            raw = response
        with io.TextIOWrapper(raw, encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    value = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON from {url}:{line_number}: {exc}") from exc
                if not isinstance(value, dict):
                    raise ValueError(f"Expected object from {url}:{line_number}")
                yield value


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return value


def load_l0_ics(path: Path) -> set[str]:
    payload = load_json(path)
    return {str(row["ic_id"]) for row in payload.get("l0_candidates", []) if isinstance(row, dict) and row.get("l0_candidate")}


def load_clean_candidate_ics(path: Path) -> set[str]:
    clean: set[str] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("clean_candidate", "")).lower() == "true":
                clean.add(str(row["ic_id"]))
    return clean


def load_p2_ics(path: Path) -> set[str]:
    payload = load_json(path)
    return {str(row["ic_id"]) for row in payload.get("seed_ics", []) if isinstance(row, dict)}


def ic_from_node(node: str) -> str:
    return f"ic:{node.rsplit('::', 1)[0]}"


def degree_maps(nodes: set[str], adjacency: dict[str, set[str]]) -> tuple[dict[str, int], dict[str, int]]:
    indeg = {node: 0 for node in nodes}
    outdeg = {node: 0 for node in nodes}
    for source in nodes:
        targets = adjacency.get(source, set()) & nodes
        outdeg[source] = len(targets)
        for target in targets:
            indeg[target] = indeg.get(target, 0) + 1
    return indeg, outdeg


def top_degree_rows(nodes: set[str], adjacency: dict[str, set[str]], labels: dict[str, str], limit: int) -> list[dict[str, Any]]:
    indeg, outdeg = degree_maps(nodes, adjacency)
    ranked = sorted(nodes, key=lambda node: (-(indeg[node] + outdeg[node]), -outdeg[node], -indeg[node], node))[:limit]
    return [
        {
            "node": node,
            "ic_id": ic_from_node(node),
            "label": labels.get(node, node),
            "in_degree": indeg[node],
            "out_degree": outdeg[node],
            "total_degree": indeg[node] + outdeg[node],
        }
        for node in ranked
    ]


def graph_stats(nodes: set[str], adjacency: dict[str, set[str]]) -> dict[str, Any]:
    edge_count = sum(1 for source in nodes for target in adjacency.get(source, set()) if target in nodes)
    indeg, outdeg = degree_maps(nodes, adjacency)
    totals = sorted((indeg[node] + outdeg[node] for node in nodes), reverse=True)
    return {
        "node_count": len(nodes),
        "edge_count": edge_count,
        "max_total_degree": totals[0] if totals else 0,
        "p90_total_degree": totals[int(len(totals) * 0.1)] if totals else 0,
        "median_total_degree": totals[len(totals) // 2] if totals else 0,
    }


def write_largest_scc(
    path: Path,
    component: set[str],
    adjacency: dict[str, set[str]],
    labels: dict[str, str],
    top: int,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    component_graph = induced_subgraph(component, adjacency)
    payload = {
        "schema_version": 1,
        "artifact_id": "kaikki-largest-scc",
        "definition": "Largest strongly connected component in the complete Kaikki/Wiktextract English kernel graph.",
        "stats": graph_stats(component, component_graph),
        "top_hubs": top_degree_rows(component, component_graph, labels, top),
        "nodes": sorted(component),
        "adjacency": {node: sorted(component_graph.get(node, set())) for node in sorted(component)},
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload["stats"]


def remove_nodes(active: set[str], seed: list[str], removals: list[str]) -> int:
    removed = 0
    for node in removals:
        if node in active:
            active.remove(node)
            seed.append(node)
            removed += 1
    return removed


def measure_stage(stage: str, active: set[str], adjacency: dict[str, set[str]], removed: int, elapsed: float) -> dict[str, Any]:
    active_graph = induced_subgraph(active, adjacency)
    residual = cyclic_sccs(active, active_graph)
    largest = max((len(component) for component in residual), default=0)
    return {
        "stage": stage,
        "removed": removed,
        "active_nodes": len(active),
        "residual_cyclic_scc_count": len(residual),
        "largest_residual_scc": largest,
        "elapsed_seconds": elapsed,
    }


def high_degree_removals(nodes: set[str], adjacency: dict[str, set[str]], count: int) -> list[str]:
    indeg, outdeg = degree_maps(nodes, adjacency)
    return sorted(nodes, key=lambda node: (-(indeg[node] + outdeg[node]), -outdeg[node], -indeg[node], node))[:count]


def staged_seed(
    kernel_nodes: set[str],
    kernel_graph: dict[str, set[str]],
    *,
    high_degree_count: int,
    source_core_count: int,
    bounded_passes: int,
    exact_limit: int,
    large_residual_batch_size: int,
    large_residual_max_batches: int,
    progress_path: Path,
    progress_log: Path | None,
) -> tuple[list[str], list[dict[str, Any]], list[set[str]]]:
    active = set(kernel_nodes)
    seed: list[str] = []
    stages: list[dict[str, Any]] = []

    started = time.perf_counter()
    removals = high_degree_removals(active, kernel_graph, high_degree_count)
    removed = remove_nodes(active, seed, removals)
    row = measure_stage("high_degree_global", active, kernel_graph, removed, time.perf_counter() - started)
    stages.append(row)
    progress_event(progress_path, row)
    emit(f"Stage high_degree_global removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}", progress_log)

    started = time.perf_counter()
    active_graph = induced_subgraph(active, kernel_graph)
    residual = cyclic_sccs(active, active_graph)
    largest = max(residual, key=len) if residual else set()
    removals = high_degree_removals(largest, active_graph, source_core_count)
    removed = remove_nodes(active, seed, removals)
    row = measure_stage("largest_scc_hubs", active, kernel_graph, removed, time.perf_counter() - started)
    stages.append(row)
    progress_event(progress_path, row)
    emit(f"Stage largest_scc_hubs removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}", progress_log)

    for pass_index in range(1, bounded_passes + 1):
        started = time.perf_counter()
        active_graph = induced_subgraph(active, kernel_graph)
        rev = reverse_adjacency(active, active_graph)
        residual = cyclic_sccs(active, active_graph)
        if not residual:
            row = measure_stage(f"bounded_pass_{pass_index}", active, kernel_graph, 0, time.perf_counter() - started)
            stages.append(row)
            progress_event(progress_path, row)
            break
        removals = [choose_feedback_vertex(component, active_graph, rev) for component in residual]
        removed = remove_nodes(active, seed, removals)
        row = measure_stage(f"bounded_pass_{pass_index}", active, kernel_graph, removed, time.perf_counter() - started)
        stages.append(row)
        progress_event(progress_path, row)
        emit(f"Stage bounded_pass_{pass_index} removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}", progress_log)
        if row["residual_cyclic_scc_count"] == 0:
            break

    started = time.perf_counter()
    active_graph = induced_subgraph(active, kernel_graph)
    residual = cyclic_sccs(active, active_graph)
    exact_removals: list[str] = []
    skipped_large = []
    for component in residual:
        if len(component) > exact_limit:
            skipped_large.append(component)
            continue
        exact = exact_feedback_vertex_set(component, active_graph, exact_limit)
        if exact:
            exact_removals.extend(exact)
    removed = remove_nodes(active, seed, exact_removals)
    row = measure_stage("exact_small_residuals", active, kernel_graph, removed, time.perf_counter() - started)
    row["skipped_large_residual_scc_count"] = len(skipped_large)
    row["largest_skipped_residual_scc"] = max((len(component) for component in skipped_large), default=0)
    stages.append(row)
    progress_event(progress_path, row)
    emit(f"Stage exact_small_residuals removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}", progress_log)

    for batch_index in range(1, large_residual_max_batches + 1):
        active_graph = induced_subgraph(active, kernel_graph)
        residual = cyclic_sccs(active, active_graph)
        if not residual:
            break
        largest = max(residual, key=len)
        if len(largest) <= exact_limit:
            break
        started = time.perf_counter()
        removals = high_degree_removals(largest, active_graph, min(large_residual_batch_size, len(largest)))
        removed = remove_nodes(active, seed, removals)
        row = measure_stage(f"large_residual_batch_{batch_index}", active, kernel_graph, removed, time.perf_counter() - started)
        stages.append(row)
        progress_event(progress_path, row)
        emit(
            f"Stage large_residual_batch_{batch_index} removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}",
            progress_log,
        )
        if row["residual_cyclic_scc_count"] == 0:
            break

    started = time.perf_counter()
    active_graph = induced_subgraph(active, kernel_graph)
    residual = cyclic_sccs(active, active_graph)
    exact_removals = []
    skipped_large = []
    for component in residual:
        if len(component) > exact_limit:
            skipped_large.append(component)
            continue
        exact = exact_feedback_vertex_set(component, active_graph, exact_limit)
        if exact:
            exact_removals.extend(exact)
    removed = remove_nodes(active, seed, exact_removals)
    row = measure_stage("final_exact_small_residuals", active, kernel_graph, removed, time.perf_counter() - started)
    row["skipped_large_residual_scc_count"] = len(skipped_large)
    row["largest_skipped_residual_scc"] = max((len(component) for component in skipped_large), default=0)
    stages.append(row)
    progress_event(progress_path, row)
    emit(f"Stage final_exact_small_residuals removed={removed} residual={row['residual_cyclic_scc_count']} largest={row['largest_residual_scc']}", progress_log)

    final_residual = cyclic_sccs(active, induced_subgraph(active, kernel_graph))
    return seed, stages, final_residual


def overlap_counts(seed_ics: set[str], surface: set[str]) -> dict[str, Any]:
    overlap = seed_ics & surface
    return {
        "overlap_count": len(overlap),
        "surface_count": len(surface),
        "seed_count": len(seed_ics),
        "fraction_of_surface": len(overlap) / max(len(surface), 1),
        "fraction_of_seed": len(overlap) / max(len(seed_ics), 1),
        "in_both_examples": sorted(overlap)[:50],
        "surface_not_seed_examples": sorted(surface - seed_ics)[:50],
        "seed_not_surface_examples": sorted(seed_ics - surface)[:50],
    }


def write_seed_artifacts(
    *,
    seed_path: Path,
    summary_path: Path,
    disagreement_path: Path,
    seed_nodes: list[str],
    stages: list[dict[str, Any]],
    residual: list[set[str]],
    l0_ics: set[str],
    clean_ics: set[str],
    p2_ics: set[str],
    labels: dict[str, str],
    kernel_stats: dict[str, Any],
    largest_scc_stats: dict[str, Any],
) -> None:
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    seed_ics = {ic_from_node(node) for node in seed_nodes}
    payload = {
        "schema_version": 1,
        "artifact_id": "kaikki-staged-seed",
        "definition": "Heuristic staged seed for the complete Kaikki/Wiktextract English kernel graph.",
        "status": "acyclic" if not residual else "residual_cycles",
        "seed_nodes": sorted(seed_nodes),
        "seed_ics": sorted(seed_ics),
        "seed_node_count": len(seed_nodes),
        "seed_ic_count": len(seed_ics),
        "kernel": kernel_stats,
        "largest_scc": largest_scc_stats,
        "stages": stages,
        "residual": {
            "cyclic_scc_count": len(residual),
            "largest_cyclic_scc": max((len(component) for component in residual), default=0),
        },
        "overlap": {
            "l0": overlap_counts(seed_ics, l0_ics),
            "clean_candidates": overlap_counts(seed_ics, clean_ics),
            "p2": overlap_counts(seed_ics, p2_ics),
        },
    }
    seed_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary_lines = [
        "# Kaikki Staged Seed Summary",
        "",
        f"- Status: `{payload['status']}`",
        f"- Seed nodes: `{len(seed_nodes)}`",
        f"- Seed ICs: `{len(seed_ics)}`",
        f"- Residual cyclic SCCs: `{len(residual)}`",
        f"- Largest residual SCC: `{payload['residual']['largest_cyclic_scc']}`",
        f"- Kernel nodes: `{kernel_stats['node_count']}`",
        f"- Kernel edges: `{kernel_stats['edge_count']}`",
        f"- Largest original SCC: `{largest_scc_stats['node_count']}`",
        "",
        "## Stage Results",
        "",
        "| stage | removed | active_nodes | residual_cyclic_scc_count | largest_residual_scc | elapsed_seconds |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in stages:
        summary_lines.append(
            f"| {row['stage']} | {row['removed']} | {row['active_nodes']} | {row['residual_cyclic_scc_count']} | {row['largest_residual_scc']} | {row['elapsed_seconds']:.2f} |"
        )
    summary_lines.extend(["", "## Overlap", ""])
    for name, row in payload["overlap"].items():
        summary_lines.append(
            f"- {name}: `{row['overlap_count']} / {row['surface_count']}` of surface, `{row['fraction_of_surface']:.2%}`; `{row['fraction_of_seed']:.2%}` of seed"
        )
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    seed_not_l0 = sorted(seed_ics - l0_ics)
    l0_not_seed = sorted(l0_ics - seed_ics)
    seed_not_p2 = sorted(seed_ics - p2_ics)
    p2_not_seed = sorted(p2_ics - seed_ics)
    disagreement = [
        "# Kaikki Seed Disagreement",
        "",
        "The staged Kaikki seed is a graph-control surface, not a final primitive list. Disagreements are discovery queues.",
        "",
        f"- Seed ICs not in L0: `{len(seed_not_l0)}`",
        f"- L0 ICs not in seed: `{len(l0_not_seed)}`",
        f"- Seed ICs not in P2: `{len(seed_not_p2)}`",
        f"- P2 ICs not in seed: `{len(p2_not_seed)}`",
        "",
        "## Seed Not L0",
        "",
        ", ".join(seed_not_l0[:200]),
        "",
        "## L0 Not Seed",
        "",
        ", ".join(l0_not_seed[:200]),
        "",
        "## Seed Not P2",
        "",
        ", ".join(seed_not_p2[:200]),
        "",
        "## P2 Not Seed",
        "",
        ", ".join(p2_not_seed[:200]),
    ]
    disagreement_path.write_text("\n".join(disagreement) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute the Kaikki SCC grounding workstream.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--input", type=Path)
    source.add_argument("--input-url", default=DEFAULT_KAIKKI_EN_URL)
    parser.add_argument("--candidates", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--l0", type=Path, default=Path("data/l0-grounded-primitives.json"))
    parser.add_argument("--p2", type=Path, default=Path("data/oewn-sense-p2-ic-seed.json"))
    parser.add_argument("--largest-scc", type=Path, default=Path("data/kaikki-largest-scc.json"))
    parser.add_argument("--seed-json", type=Path, default=Path("data/kaikki-staged-seed.json"))
    parser.add_argument("--summary", type=Path, default=Path("reports/kaikki-staged-seed-summary.md"))
    parser.add_argument("--disagreement", type=Path, default=Path("reports/kaikki-seed-disagreement.md"))
    parser.add_argument("--progress-jsonl", type=Path, default=Path("reports/kaikki-minset-progress.jsonl"))
    parser.add_argument("--progress-log", type=Path, default=Path("reports/kaikki-scc-grounding.progress.log"))
    parser.add_argument("--lock", type=Path, default=Path("reports/kaikki-scc-grounding.lock"))
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--high-degree-count", type=int, default=1000)
    parser.add_argument("--source-core-count", type=int, default=1000)
    parser.add_argument("--bounded-passes", type=int, default=64)
    parser.add_argument("--exact-limit", type=int, default=12)
    parser.add_argument("--large-residual-batch-size", type=int, default=2000)
    parser.add_argument("--large-residual-max-batches", type=int, default=100)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    acquire_lock(args.lock)
    started = time.perf_counter()
    if args.progress_jsonl.exists():
        args.progress_jsonl.unlink()
    rows = iter_jsonl(args.input) if args.input is not None else iter_url_jsonl(args.input_url)
    emit("Building complete Kaikki graph", args.progress_log)
    build = build_wiktextract_graph(rows, lexicon_id="kaikki-wiktextract:en", source_name="kaikki.org English raw Wiktextract data", source_url=args.input_url, progress=lambda message: emit(message, args.progress_log))
    emit(f"Built graph nodes={len(build.nodes)} edges={sum(len(t) for t in build.adjacency.values())}", args.progress_log)

    emit("Computing kernel and SCCs", args.progress_log)
    kernel_nodes = set()
    live_out = {node: len(build.adjacency.get(node, set())) for node in build.nodes}
    remaining = set(build.nodes)
    rev_full = reverse_adjacency(build.nodes, build.adjacency)
    queue = [node for node, out_degree in live_out.items() if out_degree == 0]
    while queue:
        node = queue.pop()
        if node not in remaining:
            continue
        remaining.remove(node)
        for parent in rev_full.get(node, set()):
            if parent not in remaining or parent == node:
                continue
            if node in build.adjacency.get(parent, set()):
                live_out[parent] -= 1
                if live_out[parent] == 0:
                    queue.append(parent)
    kernel_nodes = remaining
    kernel_graph = induced_subgraph(kernel_nodes, build.adjacency)
    components = cyclic_sccs(kernel_nodes, kernel_graph)
    largest = max(components, key=len)
    kernel_stats = graph_stats(kernel_nodes, kernel_graph)
    progress_event(args.progress_jsonl, {"stage": "kernel", **kernel_stats, "cyclic_scc_count": len(components), "largest_scc": len(largest)})

    emit("Writing largest SCC artifact", args.progress_log)
    largest_stats = write_largest_scc(args.largest_scc, largest, kernel_graph, build.labels, args.top)

    emit("Running staged seed", args.progress_log)
    seed_nodes, stages, residual = staged_seed(
        kernel_nodes,
        kernel_graph,
        high_degree_count=args.high_degree_count,
        source_core_count=args.source_core_count,
        bounded_passes=args.bounded_passes,
        exact_limit=args.exact_limit,
        large_residual_batch_size=args.large_residual_batch_size,
        large_residual_max_batches=args.large_residual_max_batches,
        progress_path=args.progress_jsonl,
        progress_log=args.progress_log,
    )

    write_seed_artifacts(
        seed_path=args.seed_json,
        summary_path=args.summary,
        disagreement_path=args.disagreement,
        seed_nodes=seed_nodes,
        stages=stages,
        residual=residual,
        l0_ics=load_l0_ics(args.l0),
        clean_ics=load_clean_candidate_ics(args.candidates),
        p2_ics=load_p2_ics(args.p2),
        labels=build.labels,
        kernel_stats=kernel_stats,
        largest_scc_stats=largest_stats,
    )
    emit(f"Done in {time.perf_counter() - started:.1f}s; seed_nodes={len(seed_nodes)} residual_sccs={len(residual)}", args.progress_log)
    print(json.dumps({"seed_nodes": len(seed_nodes), "residual_cyclic_scc_count": len(residual), "largest_scc": len(largest)}, indent=2))


if __name__ == "__main__":
    main()
