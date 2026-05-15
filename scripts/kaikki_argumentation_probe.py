from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from argumentation.af_sat import SATCheck, find_stable_extension
from argumentation.dung import ArgumentationFramework, grounded_extension


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
            "Remove it only after confirming no Kaikki argumentation probe is active."
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


def fingerprint(values: frozenset[str] | None) -> str | None:
    if values is None:
        return None
    joined = "\n".join(sorted(values)).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


def write_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Kaikki Argumentation Probe",
        "",
        f"- Source: `{result['source']}`",
        f"- Argumentation pin: `{result['argumentation_pin']}`",
        f"- Nodes: `{result['nodes']}`",
        f"- Edges: `{result['edges']}`",
    ]
    if "grounded" in result:
        grounded = result["grounded"]
        lines.extend(
            [
                "",
                "## Grounded",
                "",
                f"- Status: `{grounded['status']}`",
                f"- Extension size: `{grounded.get('extension_size')}`",
                f"- Runtime seconds: `{grounded['runtime_seconds']:.3f}`",
                f"- Fingerprint: `{grounded.get('fingerprint')}`",
            ]
        )
    if "stable" in result:
        stable = result["stable"]
        lines.extend(
            [
                "",
                "## Stable",
                "",
                f"- Status: `{stable['status']}`",
                f"- Stable exists: `{stable.get('stable_exists')}`",
                f"- Extension size: `{stable.get('extension_size')}`",
                f"- Runtime seconds: `{stable['runtime_seconds']:.3f}`",
                f"- Fingerprint: `{stable.get('fingerprint')}`",
                f"- SAT checks: `{len(stable.get('sat_checks', []))}`",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe argumentation semantics on the isolated Kaikki largest SCC.")
    parser.add_argument("--input", type=Path, default=Path("data/kaikki-largest-scc.json"))
    parser.add_argument("--json", type=Path, default=Path("reports/kaikki-argumentation-probe.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/kaikki-argumentation-probe.md"))
    parser.add_argument("--progress-log", type=Path, default=Path("reports/kaikki-argumentation-probe.progress.log"))
    parser.add_argument("--lock", type=Path, default=Path("reports/kaikki-argumentation-probe.lock"))
    parser.add_argument("--mode", choices=("grounded", "stable", "both"), default="both")
    parser.add_argument("--no-simplify", action="store_true")
    parser.add_argument("--argumentation-pin", default="8e7247fe8e9c89636b3753a0feac5545f131c853")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    acquire_lock(args.lock)
    emit(f"Loading {args.input}", args.progress_log)
    nodes, edges, stats = load_largest_scc(args.input)
    framework = ArgumentationFramework(arguments=nodes, defeats=edges)
    result: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": "kaikki-argumentation-probe",
        "source": str(args.input),
        "argumentation_pin": args.argumentation_pin,
        "nodes": len(nodes),
        "edges": len(edges),
        "source_stats": stats,
    }

    if args.mode in {"grounded", "both"}:
        emit("Running grounded_extension", args.progress_log)
        started = time.perf_counter()
        extension = grounded_extension(framework)
        result["grounded"] = {
            "status": "complete",
            "extension_size": len(extension),
            "runtime_seconds": time.perf_counter() - started,
            "fingerprint": fingerprint(extension),
        }
        emit(f"grounded complete size={len(extension)}", args.progress_log)

    if args.mode in {"stable", "both"}:
        emit("Running find_stable_extension", args.progress_log)
        checks: list[dict[str, Any]] = []

        def trace_sink(check: SATCheck) -> None:
            row = {
                "utility_name": check.utility_name,
                "result": check.result,
                "elapsed_ms": check.elapsed_ms,
                "argument_count": check.argument_count,
                "attack_count": check.attack_count,
                "model_extension_size": check.model_extension_size,
                "model_extension_fingerprint": check.model_extension_fingerprint,
            }
            checks.append(row)
            emit(f"sat check {check.utility_name} result={check.result} elapsed_ms={check.elapsed_ms:.1f}", args.progress_log)

        started = time.perf_counter()
        extension = find_stable_extension(framework, trace_sink=trace_sink, simplify=not args.no_simplify)
        result["stable"] = {
            "status": "complete",
            "stable_exists": extension is not None,
            "extension_size": None if extension is None else len(extension),
            "runtime_seconds": time.perf_counter() - started,
            "fingerprint": fingerprint(extension),
            "sat_checks": checks,
            "simplify": not args.no_simplify,
        }
        emit(f"stable complete exists={extension is not None}", args.progress_log)

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(args.report, result)
    print(json.dumps({"json": str(args.json), "report": str(args.report), "nodes": len(nodes), "edges": len(edges)}, indent=2))


if __name__ == "__main__":
    main()
