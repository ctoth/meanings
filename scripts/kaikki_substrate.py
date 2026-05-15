from __future__ import annotations

import argparse
import atexit
import gzip
import io
import json
import os
import sys
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from meanings.graph_analysis import (
    choose_core_nodes,
    compute_kernel,
    compute_layer_map,
    induced_subgraph,
    layer_histogram,
    source_sccs,
    strongly_connected_components,
)
from meanings.minset import solve_minset
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


def acquire_lock(lock_path: Path | None) -> None:
    if lock_path is None:
        return
    if lock_path.exists():
        raise RuntimeError(
            f"Run lock already exists: {lock_path}. "
            "Remove it only after confirming no Kaikki substrate run is active."
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
    rows = payload.get("l0_candidates", [])
    if not isinstance(rows, list):
        raise ValueError(f"{path} l0_candidates must be a list")
    return {str(row["ic_id"]) for row in rows if isinstance(row, dict) and row.get("l0_candidate")}


def load_clean_candidate_ics(path: Path) -> set[str]:
    import csv

    clean: set[str] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("clean_candidate", "")).lower() == "true":
                clean.add(str(row["ic_id"]))
    return clean


def ic_from_node(node: str) -> str:
    lemma = node.rsplit("::", 1)[0]
    return f"ic:{lemma}"


def overlap_summary(nodes: set[str], l0_ics: set[str], clean_ics: set[str]) -> dict[str, Any]:
    graph_ics = {ic_from_node(node) for node in nodes}
    l0_overlap = graph_ics & l0_ics
    clean_overlap = graph_ics & clean_ics
    return {
        "graph_ic_count": len(graph_ics),
        "l0_candidate_count": len(l0_ics),
        "clean_candidate_count": len(clean_ics),
        "l0_overlap_count": len(l0_overlap),
        "clean_overlap_count": len(clean_overlap),
        "l0_overlap_fraction": len(l0_overlap) / max(len(l0_ics), 1),
        "clean_overlap_fraction": len(clean_overlap) / max(len(clean_ics), 1),
        "l0_missing_examples": sorted(l0_ics - graph_ics)[:50],
        "clean_missing_examples": sorted(clean_ics - graph_ics)[:50],
    }


def seed_overlap_summary(seed_nodes: set[str], l0_ics: set[str], clean_ics: set[str]) -> dict[str, Any]:
    seed_ics = {ic_from_node(node) for node in seed_nodes}
    l0_overlap = seed_ics & l0_ics
    clean_overlap = seed_ics & clean_ics
    return {
        "seed_ic_count": len(seed_ics),
        "l0_overlap_count": len(l0_overlap),
        "clean_overlap_count": len(clean_overlap),
        "l0_overlap_fraction_of_l0": len(l0_overlap) / max(len(l0_ics), 1),
        "clean_overlap_fraction_of_clean": len(clean_overlap) / max(len(clean_ics), 1),
        "l0_overlap_fraction_of_seed": len(l0_overlap) / max(len(seed_ics), 1),
        "clean_overlap_fraction_of_seed": len(clean_overlap) / max(len(seed_ics), 1),
        "seed_examples": sorted(seed_ics)[:50],
        "l0_in_seed_examples": sorted(l0_overlap)[:50],
        "clean_in_seed_examples": sorted(clean_overlap)[:50],
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    graph = payload["graph"]
    overlap = payload["overlap"]
    analysis = payload.get("analysis")
    lines = [
        "# Kaikki Wiktextract Substrate",
        "",
        "This is the external full-definition substrate path for attacking the lexicographer's confound. It builds a graph from Wiktextract/Kaikki English entries using the same node and edge convention as the OEWN paper-wordnet graph where possible.",
        "",
        "## Provenance",
        "",
        f"- Source name: `{payload['source_name']}`",
        f"- Source URL: `{payload.get('source_url') or ''}`",
        f"- Local input: `{payload.get('input_path') or ''}`",
        f"- Max English entries: `{payload.get('max_entries')}`",
        "",
        "## Graph",
        "",
        f"- Nodes: `{graph['node_count']}`",
        f"- Edges: `{graph['edge_count']}`",
        f"- Edges per node: `{graph['edges_per_node']:.6f}`",
        f"- Directed edge density: `{graph['directed_edge_density']:.12f}`",
        f"- Candidate matches: `{graph['resolution_stats'].get('candidate_matches', 0)}`",
        f"- Ambiguous skipped: `{graph['resolution_stats'].get('ambiguous_skipped', 0)}`",
        f"- Missing skipped: `{graph['resolution_stats'].get('missing_skipped', 0)}`",
        "",
        "## Base Surface Overlap",
        "",
        f"- Graph IC count: `{overlap['graph_ic_count']}`",
        f"- L0 overlap: `{overlap['l0_overlap_count']} / {overlap['l0_candidate_count']}` (`{overlap['l0_overlap_fraction']:.2%}`)",
        f"- Clean candidate overlap: `{overlap['clean_overlap_count']} / {overlap['clean_candidate_count']}` (`{overlap['clean_overlap_fraction']:.2%}`)",
    ]
    if analysis is not None:
        seed_overlap = analysis.get("seed_overlap", {})
        lines.extend(
            [
                "",
                "## Kernel Analysis",
                "",
                f"- Kernel nodes: `{analysis['kernel_node_count']}`",
                f"- Kernel SCCs: `{analysis.get('kernel_scc_count', 0)}`",
                f"- Largest kernel SCC: `{analysis.get('largest_kernel_scc', 0)}`",
                f"- Core nodes: `{analysis.get('core_node_count', 0)}`",
                f"- Satellite nodes: `{analysis.get('satellite_node_count', 0)}`",
                f"- Seed status: `{analysis.get('seed_status', 'not_run')}`",
            ]
        )
        if analysis.get("seed_status") == "complete":
            lines.extend(
                [
                    f"- Seed nodes: `{analysis.get('seed_node_count', 0)}`",
                    f"- Residual cyclic SCCs: `{analysis.get('residual_cyclic_scc_count', 0)}`",
                    f"- Seed IC count: `{seed_overlap.get('seed_ic_count', 0)}`",
                    f"- L0 in seed: `{seed_overlap.get('l0_overlap_count', 0)} / {overlap['l0_candidate_count']}` (`{seed_overlap.get('l0_overlap_fraction_of_l0', 0):.2%}`)",
                    f"- Clean candidates in seed: `{seed_overlap.get('clean_overlap_count', 0)} / {overlap['clean_candidate_count']}` (`{seed_overlap.get('clean_overlap_fraction_of_clean', 0):.2%}`)",
                ]
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and summarize a Kaikki/Wiktextract English definition substrate.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--input", type=Path)
    source.add_argument("--input-url", default=DEFAULT_KAIKKI_EN_URL)
    parser.add_argument("--source-name", default="kaikki.org English raw Wiktextract data")
    parser.add_argument("--max-entries", type=int)
    parser.add_argument("--analyze-kernel", action="store_true")
    parser.add_argument("--kernel-only", action="store_true", help="Compute kernel/core structure but skip MinSet seed extraction.")
    parser.add_argument("--seed-method", default="exact-small-greedy")
    parser.add_argument("--candidates", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--l0", type=Path, default=Path("data/l0-grounded-primitives.json"))
    parser.add_argument("--json", type=Path, default=Path("reports/kaikki-substrate-summary.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/kaikki-substrate-summary.md"))
    parser.add_argument("--progress-log", type=Path, default=Path("reports/kaikki-substrate.progress.log"))
    parser.add_argument("--lock", type=Path, default=Path("reports/kaikki-substrate.lock"))
    return parser


def write_outputs(json_path: Path, report_path: Path, payload: dict[str, Any]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report_path, payload)


def main() -> None:
    args = build_parser().parse_args()
    progress_log = args.progress_log if str(args.progress_log).lower() not in {"", "none", "false"} else None
    lock_path = args.lock if str(args.lock).lower() not in {"", "none", "false"} else None
    acquire_lock(lock_path)
    started = time.perf_counter()

    if args.input is not None:
        rows = iter_jsonl(args.input)
        source_url = None
        input_path = str(args.input)
        emit(f"Reading local Wiktextract JSONL: {args.input}", progress_log)
    else:
        rows = iter_url_jsonl(args.input_url)
        source_url = args.input_url
        input_path = None
        emit(f"Streaming Wiktextract JSONL: {args.input_url}", progress_log)

    build = build_wiktextract_graph(
        rows,
        lexicon_id="kaikki-wiktextract:en",
        source_name=args.source_name,
        source_url=source_url,
        max_entries=args.max_entries,
        progress=lambda message: emit(message, progress_log),
    )
    edge_count = sum(len(targets) for targets in build.adjacency.values())
    directed_denominator = len(build.nodes) * max(len(build.nodes) - 1, 1)
    emit(f"Built graph: nodes={len(build.nodes)}, edges={edge_count}", progress_log)

    l0_ics = load_l0_ics(args.l0)
    clean_ics = load_clean_candidate_ics(args.candidates)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": "kaikki-substrate-summary",
        "source_name": args.source_name,
        "source_url": source_url,
        "input_path": input_path,
        "max_entries": args.max_entries,
        "graph": {
            "graph_type": build.graph_type,
            "node_count": len(build.nodes),
            "edge_count": edge_count,
            "edges_per_node": edge_count / max(len(build.nodes), 1),
            "directed_edge_density": edge_count / directed_denominator,
            "resolution_stats": build.metadata.get("resolution_stats", {}),
        },
        "overlap": overlap_summary(build.nodes, l0_ics, clean_ics),
        "runtime_seconds": time.perf_counter() - started,
    }

    if args.analyze_kernel or args.kernel_only:
        emit("Computing kernel structure", progress_log)
        kernel_started = time.perf_counter()
        kernel_nodes = compute_kernel(build.nodes, build.adjacency)
        kernel_graph = induced_subgraph(kernel_nodes, build.adjacency)
        kernel_sccs = strongly_connected_components(kernel_nodes, kernel_graph)
        src_sccs = source_sccs(kernel_nodes, kernel_graph)
        core_nodes = choose_core_nodes(kernel_sccs, src_sccs, "source-union")
        payload["analysis"] = {
            "kernel_node_count": len(kernel_nodes),
            "kernel_scc_count": len(kernel_sccs),
            "largest_kernel_scc": max((len(component) for component in kernel_sccs), default=0),
            "source_scc_count": len(src_sccs),
            "core_node_count": len(core_nodes),
            "satellite_node_count": len(kernel_nodes - core_nodes),
            "kernel_runtime_seconds": time.perf_counter() - kernel_started,
            "seed_method": args.seed_method,
            "seed_status": "skipped_kernel_only" if args.kernel_only else "not_started",
        }
        write_outputs(args.json, args.report, payload)
        emit(
            f"Kernel checkpoint: kernel={len(kernel_nodes)}, sccs={len(kernel_sccs)}, largest_scc={payload['analysis']['largest_kernel_scc']}",
            progress_log,
        )

        if args.analyze_kernel and not args.kernel_only:
            emit(f"Solving MinSet with {args.seed_method}", progress_log)
            minset = solve_minset(kernel_nodes, kernel_graph, args.seed_method)
            layers: dict[str, int] = {}
            if minset.residual_cyclic_scc_count == 0 and minset.nodes:
                emit("Computing kernel layers after seed removal", progress_log)
                layers = compute_layer_map(kernel_nodes, kernel_graph, set(minset.nodes))
            payload["analysis"] |= {
                "seed_status": "complete",
                "seed_node_count": len(minset.nodes),
                "seed_exact": minset.exact,
                "seed_lower_bound": minset.lower_bound,
                "seed_upper_bound": minset.upper_bound,
                "seed_runtime_seconds": minset.runtime_seconds,
                "residual_cyclic_scc_count": minset.residual_cyclic_scc_count,
                "seed_scc_exact_count": minset.scc_exact_count,
                "seed_scc_heuristic_count": minset.scc_heuristic_count,
                "layer_histogram": {str(k): v for k, v in layer_histogram(layers).items()},
                "seed_overlap": seed_overlap_summary(set(minset.nodes), l0_ics, clean_ics),
            }

    write_outputs(args.json, args.report, payload)
    emit(f"Wrote {args.json} and {args.report} in {payload['runtime_seconds']:.1f}s", progress_log)
    print(json.dumps({"json": str(args.json), "report": str(args.report), "nodes": len(build.nodes), "edges": edge_count}, indent=2))


if __name__ == "__main__":
    main()
