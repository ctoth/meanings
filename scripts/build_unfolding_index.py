from __future__ import annotations

import argparse
import atexit
import json
import os
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from meanings.graph_analysis import compute_kernel, compute_layer_map, induced_subgraph, reverse_adjacency
from meanings.wordnet_pipeline import build_sense_level_paper_wordnet_graph_with_ic_fallback


EXPECTED_P2_ARTIFACT_ID = "oewn-sense-p2-ic-seed"
EXPECTED_P2_SURFACE = "strict_graph_seed_p2_sense_ic"


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
            "Remove it only after confirming no unfolding-index run is active."
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


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return value


def load_p2_seed(path: Path) -> tuple[dict[str, Any], set[str], set[str], dict[str, dict[str, Any]]]:
    payload = load_json(path)
    if payload.get("schema_version") != 1:
        raise ValueError(f"{path} is not a schema_version=1 P2 seed artifact")
    if payload.get("artifact_id") != EXPECTED_P2_ARTIFACT_ID:
        raise ValueError(f"{path} artifact_id is not {EXPECTED_P2_ARTIFACT_ID!r}")
    if payload.get("surface") != EXPECTED_P2_SURFACE:
        raise ValueError(f"{path} surface is not {EXPECTED_P2_SURFACE!r}")

    seed_sense_ids: set[str] = set()
    seed_ic_ids: set[str] = set()
    rows_by_ic: dict[str, dict[str, Any]] = {}
    rows = payload.get("seed_ics", [])
    if not isinstance(rows, list):
        raise ValueError(f"{path} seed_ics must be a list")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{path} seed_ics contains a non-object row")
        ic_id = str(row["ic_id"])
        seed_ic_ids.add(ic_id)
        rows_by_ic[ic_id] = row
        for sense_id in row.get("seed_sense_ids_for_ic", []):
            seed_sense_ids.add(str(sense_id))
    if not seed_sense_ids:
        raise ValueError(f"{path} has no seed_sense_ids_for_ic values")
    return payload, seed_sense_ids, seed_ic_ids, rows_by_ic


def load_admitted_ics(path: Path) -> set[str]:
    payload = load_json(path)
    admitted = payload.get("admitted", [])
    if not isinstance(admitted, list):
        raise ValueError(f"{path} admitted must be a list")
    return {str(row["ic_id"]) if isinstance(row, dict) else str(row) for row in admitted}


def truncate_sorted(values: set[str], limit: int) -> tuple[list[str], bool]:
    ordered = sorted(values)
    return ordered[:limit], len(ordered) > limit


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    index = min(len(values) - 1, round((len(values) - 1) * pct))
    return sorted(values)[index]


def validate_graph_against_seed(payload: dict[str, Any], build: Any) -> None:
    graph = payload.get("graph", {})
    if not isinstance(graph, dict):
        raise ValueError("P2 payload graph metadata must be an object")
    expected_nodes = int(graph.get("node_count", -1))
    expected_edges = int(graph.get("edge_count", -1))
    actual_edges = sum(len(targets) for targets in build.adjacency.values())
    if expected_nodes != len(build.nodes):
        raise ValueError(f"P2 graph node count mismatch: artifact={expected_nodes}, rebuilt={len(build.nodes)}")
    if expected_edges != actual_edges:
        raise ValueError(f"P2 graph edge count mismatch: artifact={expected_edges}, rebuilt={actual_edges}")


def build_index_rows(
    *,
    kernel_nodes: set[str],
    kernel_graph: dict[str, set[str]],
    layer_by_node: dict[str, int],
    seed_sense_ids: set[str],
    seed_ic_ids: set[str],
    admitted_ics: set[str],
    metadata: dict[str, dict[str, object]],
    max_ids: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reverse_kernel = reverse_adjacency(kernel_nodes, kernel_graph)
    all_closures: dict[str, set[str]] = {}
    seed_closures: dict[str, set[str]] = {}
    rows: list[dict[str, Any]] = []
    missing_predecessor_closure = 0

    for node in sorted(kernel_nodes, key=lambda item: (layer_by_node.get(item, 10**9), item)):
        meta = metadata[node]
        ic_id = str(meta["ic_id"])
        direct_sources = {source for source in reverse_kernel.get(node, set()) if source in layer_by_node}
        direct_ic_ids = {str(metadata[source]["ic_id"]) for source in direct_sources}

        if node in seed_sense_ids:
            all_closure = {ic_id}
            seed_closure = {ic_id} if ic_id in seed_ic_ids else set()
        else:
            all_closure = set(direct_ic_ids)
            seed_closure: set[str] = set()
            for source in direct_sources:
                if source not in all_closures:
                    missing_predecessor_closure += 1
                    continue
                all_closure.update(all_closures[source])
                seed_closure.update(seed_closures[source])

        all_closures[node] = all_closure
        seed_closures[node] = seed_closure
        closure_ids, closure_truncated = truncate_sorted(all_closure, max_ids)
        seed_ids, seed_truncated = truncate_sorted(seed_closure, max_ids)

        rows.append(
            {
                "sense_id": node,
                "ic_id": ic_id,
                "label": str(meta.get("lemma", "")),
                "pos": str(meta.get("pos", "")),
                "layer": layer_by_node.get(node),
                "direct_definiens_ic_ids": sorted(direct_ic_ids),
                "transitive_closure_ic_ids": closure_ids,
                "closure_size": len(all_closure),
                "closure_truncated": closure_truncated,
                "seed_ics_in_closure": seed_ids,
                "seed_closure_size": len(seed_closure),
                "seed_closure_truncated": seed_truncated,
                "admission_decision": "admit" if ic_id in admitted_ics else "not_admitted_or_unavailable",
                "rationale_ref": ic_id,
            }
        )

    summary = {
        "missing_predecessor_closure_count": missing_predecessor_closure,
        "closure_size_median": statistics.median([row["closure_size"] for row in rows]) if rows else 0,
        "closure_size_p90": percentile([row["closure_size"] for row in rows], 0.90),
        "closure_size_max": max((row["closure_size"] for row in rows), default=0),
        "seed_closure_size_median": statistics.median([row["seed_closure_size"] for row in rows]) if rows else 0,
        "seed_closure_size_p90": percentile([row["seed_closure_size"] for row in rows], 0.90),
        "seed_closure_size_max": max((row["seed_closure_size"] for row in rows), default=0),
        "truncated_closure_rows": sum(1 for row in rows if row["closure_truncated"]),
        "truncated_seed_closure_rows": sum(1 for row in rows if row["seed_closure_truncated"]),
    }
    return rows, summary


def write_index(
    *,
    path: Path,
    lexicon_id: str,
    p2_seed_path: Path,
    p2_payload: dict[str, Any],
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    layer_histogram: dict[int, int],
    residual_unlayered_count: int,
    max_ids: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "artifact_id": "sense-unfolding-index",
        "definition": "kernel-only OEWN sense unfolding index over the IC-fallback sense graph using the P2 sense seed",
        "lexicon_id": lexicon_id,
        "source_seed": str(p2_seed_path),
        "source_seed_resolver_id": p2_payload.get("resolver_id"),
        "closure_policy": {
            "graph": "IC-fallback sense graph",
            "node_scope": "kernel nodes only",
            "seed_nodes": "all P2 source sense seeds from seed_sense_ids_for_ic, not only exported IC representatives",
            "edge_direction": "source sense -> target sense; direct definers of a target are reverse-adjacency sources",
            "closure_ids": f"full closure counts retained; ID lists truncated to {max_ids} entries when larger",
        },
        "summary": summary | {
            "indexed_sense_count": len(rows),
            "residual_unlayered_count": residual_unlayered_count,
            "layer_histogram": {str(key): value for key, value in sorted(layer_histogram.items())},
        },
        "rows": rows,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def render_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    *,
    path: Path,
    output_path: Path,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    layer_histogram: dict[int, int],
    residual_unlayered_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    closure_rows = sorted(rows, key=lambda row: (-int(row["closure_size"]), str(row["sense_id"])))[:40]
    seed_rows = sorted(rows, key=lambda row: (-int(row["seed_closure_size"]), str(row["sense_id"])))[:40]
    layer_rows = [{"layer": layer, "count": count} for layer, count in sorted(layer_histogram.items())]
    decision_rows = [
        {"admission_decision": decision, "count": count}
        for decision, count in Counter(str(row["admission_decision"]) for row in rows).most_common()
    ]
    fields = [
        "sense_id",
        "ic_id",
        "label",
        "pos",
        "layer",
        "closure_size",
        "seed_closure_size",
        "admission_decision",
    ]
    lines = [
        "# Sense Unfolding Index",
        "",
        "This is a kernel-only prototype over the OEWN IC-fallback sense graph. It tests whether the P2 seed can unfold cyclic definitions into finite IC closures.",
        "",
        "## Summary",
        "",
        f"- Output: `{output_path}`",
        f"- Indexed kernel senses: `{len(rows)}`",
        f"- Residual unlayered kernel senses: `{residual_unlayered_count}`",
        f"- Missing predecessor closure references: `{summary['missing_predecessor_closure_count']}`",
        f"- Median closure size: `{summary['closure_size_median']}`",
        f"- P90 closure size: `{summary['closure_size_p90']}`",
        f"- Max closure size: `{summary['closure_size_max']}`",
        f"- Median seed-closure size: `{summary['seed_closure_size_median']}`",
        f"- P90 seed-closure size: `{summary['seed_closure_size_p90']}`",
        f"- Max seed-closure size: `{summary['seed_closure_size_max']}`",
        f"- Rows with truncated closure IDs: `{summary['truncated_closure_rows']}`",
        f"- Rows with truncated seed-closure IDs: `{summary['truncated_seed_closure_rows']}`",
        "",
        "## Layer Histogram",
        "",
    ]
    lines.extend(render_table(layer_rows, ["layer", "count"]))
    lines.extend(["", "## Admission Decisions", ""])
    lines.extend(render_table(decision_rows, ["admission_decision", "count"]))
    lines.extend(["", "## Largest Closures", ""])
    lines.extend(render_table(closure_rows, fields))
    lines.extend(["", "## Largest Seed Closures", ""])
    lines.extend(render_table(seed_rows, fields))
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a kernel-only sense unfolding index from the P2 seed.")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument("--p2-seed", type=Path, default=Path("data/oewn-sense-p2-ic-seed.json"))
    parser.add_argument("--admission", type=Path, default=Path("data/oewn-upgoer-admitted.json"))
    parser.add_argument("--output", type=Path, default=Path("data/sense-unfolding-index.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/unfolding-index.md"))
    parser.add_argument("--progress-log", type=Path, default=Path("reports/unfolding-index.progress.log"))
    parser.add_argument("--lock", type=Path, default=Path("reports/unfolding-index.lock"))
    parser.add_argument("--max-closure-ids", type=int, default=500)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    progress_log = args.progress_log if str(args.progress_log).lower() not in {"", "none", "false"} else None
    lock_path = args.lock if str(args.lock).lower() not in {"", "none", "false"} else None
    acquire_lock(lock_path)

    started = time.perf_counter()
    emit("Loading P2 seed and admission data", progress_log)
    p2_payload, seed_sense_ids, seed_ic_ids, _rows_by_ic = load_p2_seed(args.p2_seed)
    admitted_ics = load_admitted_ics(args.admission)
    emit(f"Loaded P2 seed: sense seeds={len(seed_sense_ids)}, IC seeds={len(seed_ic_ids)}", progress_log)

    emit("Building IC-fallback sense graph", progress_log)
    build_started = time.perf_counter()
    build = build_sense_level_paper_wordnet_graph_with_ic_fallback(args.lexicon)
    emit(
        f"Built graph in {time.perf_counter() - build_started:.1f}s: nodes={len(build.nodes)}, edges={sum(len(t) for t in build.adjacency.values())}",
        progress_log,
    )
    validate_graph_against_seed(p2_payload, build)

    missing_seed_nodes = sorted(seed_sense_ids - build.nodes)
    if missing_seed_nodes:
        raise ValueError(f"P2 seed has {len(missing_seed_nodes)} sense IDs absent from rebuilt graph")

    emit("Computing kernel and P2 layers", progress_log)
    kernel_started = time.perf_counter()
    kernel_nodes = compute_kernel(build.nodes, build.adjacency)
    kernel_graph = induced_subgraph(kernel_nodes, build.adjacency)
    layer_by_node = compute_layer_map(kernel_nodes, kernel_graph, seed_sense_ids & kernel_nodes)
    residual_unlayered_count = len(kernel_nodes - set(layer_by_node))
    layer_hist = dict(sorted(Counter(layer_by_node.values()).items()))
    emit(
        f"Computed layers in {time.perf_counter() - kernel_started:.1f}s: kernel={len(kernel_nodes)}, layered={len(layer_by_node)}, residual_unlayered={residual_unlayered_count}",
        progress_log,
    )

    emit("Computing closure index rows", progress_log)
    rows_started = time.perf_counter()
    rows, summary = build_index_rows(
        kernel_nodes=kernel_nodes,
        kernel_graph=kernel_graph,
        layer_by_node=layer_by_node,
        seed_sense_ids=seed_sense_ids,
        seed_ic_ids=seed_ic_ids,
        admitted_ics=admitted_ics,
        metadata=build.node_metadata,
        max_ids=args.max_closure_ids,
    )
    emit(f"Computed {len(rows)} rows in {time.perf_counter() - rows_started:.1f}s", progress_log)

    emit(f"Writing {args.output} and {args.report}", progress_log)
    write_index(
        path=args.output,
        lexicon_id=args.lexicon,
        p2_seed_path=args.p2_seed,
        p2_payload=p2_payload,
        rows=rows,
        summary=summary,
        layer_histogram=layer_hist,
        residual_unlayered_count=residual_unlayered_count,
        max_ids=args.max_closure_ids,
    )
    write_report(
        path=args.report,
        output_path=args.output,
        rows=rows,
        summary=summary,
        layer_histogram=layer_hist,
        residual_unlayered_count=residual_unlayered_count,
    )
    emit(f"Done in {time.perf_counter() - started:.1f}s", progress_log)
    print(
        json.dumps(
            {
                "indexed_sense_count": len(rows),
                "residual_unlayered_count": residual_unlayered_count,
                "closure_size_median": summary["closure_size_median"],
                "closure_size_p90": summary["closure_size_p90"],
                "closure_size_max": summary["closure_size_max"],
                "output": str(args.output),
                "report": str(args.report),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
