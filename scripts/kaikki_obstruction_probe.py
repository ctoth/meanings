from __future__ import annotations

import argparse
import atexit
import csv
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from argumentation.af_sat import explain_stable_unsat
from argumentation.dung import ArgumentationFramework


ARGUMENTATION_PIN = "9a9f4c553c7fde3ff30ef15e062c6d4ef8e672ac"


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
            "Remove it only after confirming no Kaikki obstruction probe is active."
        )
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        json.dumps({"pid": os.getpid(), "started_at": time.strftime("%Y-%m-%d %H:%M:%S"), "argv": sys.argv}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    atexit.register(lambda: lock_path.exists() and lock_path.unlink())


def load_largest_scc(path: Path) -> tuple[frozenset[str], frozenset[tuple[str, str]], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    adjacency = payload["adjacency"]
    nodes = frozenset(str(node) for node in payload["nodes"])
    edges = frozenset(
        (str(source), str(target))
        for source, targets in adjacency.items()
        for target in targets
    )
    return nodes, edges, payload.get("stats", {})


def ic_for_node(node: str) -> str:
    surface = node.rsplit("::", 1)[0]
    return f"ic:{surface.lower()}"


def read_typed_buckets(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            str(row["ic_id"]): str(row["bucket"])
            for row in csv.DictReader(handle)
            if row.get("ic_id") and row.get("bucket")
        }


def bounded(values: list[Any], limit: int) -> dict[str, Any]:
    return {
        "count": len(values),
        "truncated": len(values) > limit,
        "items": values[:limit],
    }


def summarize_core(
    *,
    core_arguments: tuple[str, ...],
    core_attacks: tuple[tuple[str, str], ...],
    coverage_arguments: tuple[str, ...],
    typed_buckets: dict[str, str],
    detail_limit: int,
) -> dict[str, Any]:
    core_ics = sorted({ic_for_node(argument) for argument in core_arguments})
    coverage_ics = sorted({ic_for_node(argument) for argument in coverage_arguments})
    attack_ics = sorted({(ic_for_node(source), ic_for_node(target)) for source, target in core_attacks})
    bucket_counts = Counter(typed_buckets.get(ic_id, "not_in_seed_not_l0") for ic_id in core_ics)
    return {
        "core_argument_count": len(core_arguments),
        "core_attack_count": len(core_attacks),
        "coverage_argument_count": len(coverage_arguments),
        "core_ic_count": len(core_ics),
        "coverage_ic_count": len(coverage_ics),
        "core_bucket_counts": dict(sorted(bucket_counts.items())),
        "core_arguments": bounded(list(core_arguments), detail_limit),
        "core_ics": bounded(core_ics, detail_limit),
        "coverage_ics": bounded(coverage_ics, detail_limit),
        "core_attacks": bounded([{"source": source, "target": target} for source, target in core_attacks], detail_limit),
        "core_attack_ics": bounded([{"source_ic": source, "target_ic": target} for source, target in attack_ics], detail_limit),
    }


def write_report(path: Path, result: dict[str, Any]) -> None:
    explanation = result["explanation"]
    core = result["core_summary"]
    lines = [
        "# Kaikki Obstruction Probe",
        "",
        "This report records the tracked-clause stable-extension explanation surface. The solver core is not guaranteed minimal.",
        "",
        "## Summary",
        "",
        f"- Source: `{result['source']}`",
        f"- Argumentation pin: `{result['argumentation_pin']}`",
        f"- Nodes: `{result['nodes']}`",
        f"- Edges: `{result['edges']}`",
        f"- Status: `{explanation['status']}`",
        f"- Stable exists: `{explanation['stable_exists']}`",
        f"- Runtime seconds: `{explanation['runtime_seconds']:.3f}`",
        f"- Clause groups: `{explanation['clause_group_count']}`",
        "",
        "## Core Summary",
        "",
        f"- Core arguments: `{core['core_argument_count']}`",
        f"- Core attacks: `{core['core_attack_count']}`",
        f"- Coverage arguments: `{core['coverage_argument_count']}`",
        f"- Core ICs: `{core['core_ic_count']}`",
        f"- Coverage ICs: `{core['coverage_ic_count']}`",
        "",
        "## Core Bucket Counts",
        "",
        "| bucket | count |",
        "| --- | --- |",
    ]
    for bucket, count in core["core_bucket_counts"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(["", "## Core IC Sample", ""])
    lines.extend(f"- `{ic_id}`" for ic_id in core["core_ics"]["items"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract a tracked stable-unsat explanation from the isolated Kaikki largest SCC.")
    parser.add_argument("--input", type=Path, default=Path("data/kaikki-largest-scc.json"))
    parser.add_argument("--typed-buckets", type=Path, default=Path("data/kaikki-seed-disagreement-typed.csv"))
    parser.add_argument("--json", type=Path, default=Path("reports/kaikki-obstruction-probe.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/kaikki-obstruction-probe.md"))
    parser.add_argument("--progress-log", type=Path, default=Path("reports/kaikki-obstruction-probe.progress.log"))
    parser.add_argument("--lock", type=Path, default=Path("reports/kaikki-obstruction-probe.lock"))
    parser.add_argument("--detail-limit", type=int, default=200)
    parser.add_argument("--no-simplify", action="store_true")
    parser.add_argument("--argumentation-pin", default=ARGUMENTATION_PIN)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    acquire_lock(args.lock)
    emit(f"Loading {args.input}", args.progress_log)
    nodes, edges, stats = load_largest_scc(args.input)
    emit(f"Loaded nodes={len(nodes)} edges={len(edges)}", args.progress_log)
    framework = ArgumentationFramework(arguments=nodes, defeats=edges)
    typed_buckets = read_typed_buckets(args.typed_buckets)
    emit("Running explain_stable_unsat", args.progress_log)
    explanation = explain_stable_unsat(
        framework,
        simplify=not args.no_simplify,
        metadata={"source": str(args.input), "argumentation_pin": args.argumentation_pin},
    )
    emit(
        f"explanation complete status={explanation.status} stable_exists={explanation.stable_exists}",
        args.progress_log,
    )
    explanation_dict = explanation.to_dict()
    result = {
        "schema_version": 1,
        "artifact_id": "kaikki-obstruction-probe",
        "source": str(args.input),
        "typed_buckets": str(args.typed_buckets),
        "argumentation_pin": args.argumentation_pin,
        "nodes": len(nodes),
        "edges": len(edges),
        "source_stats": stats,
        "simplify": not args.no_simplify,
        "explanation": explanation_dict,
        "core_summary": summarize_core(
            core_arguments=tuple(explanation.core_argument_ids),
            core_attacks=tuple(explanation.core_attack_ids),
            coverage_arguments=tuple(explanation.coverage_argument_ids),
            typed_buckets=typed_buckets,
            detail_limit=args.detail_limit,
        ),
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(args.report, result)
    print(
        json.dumps(
            {
                "json": str(args.json),
                "report": str(args.report),
                "status": explanation.status,
                "stable_exists": explanation.stable_exists,
                "core_argument_count": result["core_summary"]["core_argument_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
