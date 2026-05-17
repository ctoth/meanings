"""Validate whether the kernel-pressure-table base assembles sense definitions.

Reads `data/sense-unfolding-index.json` and `data/kernel-pressure-table.csv`.
Defines two bases derived directly from the pressure table:

- L0-only baseline: ICs with `l0_candidate == True`.
- Augmented base: L0 ICs plus pressure-table rows whose `pressure_bucket` is
  in `PRIMITIVE_BUCKETS` (currently `primitive_candidate`, `assembler_helper`,
  and any bucket added to `BASE_PROMOTABLE_BUCKETS`). The augmented layer
  contents follow whatever the pressure-table builder routes into those
  buckets, so adding a new promotion rule in
  `scripts/kernel_pressure_table.py` automatically widens this validator's
  base without further edits here.

For each base, runs an IC-level fixpoint that respects the polysemy OR-junction:
an IC is groundable if it is in the base or at least one of its kernel senses
has every direct_definiens_ic_id groundable. Truncated-closure rows are excluded
from grounding evidence and reported as `graph_data` failures.

Emits both a Markdown report and a JSON sidecar with closure-rate sensitivity
bands, per-base-IC marginal usage counts, top blocker counts by IC, and
Marginal Grounding Yield of the augmented layer versus the L0-only baseline.
"""

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


ARTIFACT_BUCKET = "resource_artifact"
CIRCULAR_BUCKET = "circular_dependency"
EXTERNAL_BUCKET = "external_substrate"
BACKGROUND_BUCKET = "candidate_background"
BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})
PRIMITIVE_BUCKETS = (
    frozenset({"primitive_candidate", "assembler_helper"}) | BASE_PROMOTABLE_BUCKETS
)
SENSITIVITY_BANDS = (50, 100, 200)
FAILURE_PRECEDENCE = ("graph_data", "artifact", "circular", "external", "background")


def emit(message: str, progress_log: Path | None) -> None:
    stamped = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(stamped, flush=True)
    if progress_log is not None:
        progress_log.parent.mkdir(parents=True, exist_ok=True)
        with progress_log.open("a", encoding="utf-8") as handle:
            handle.write(stamped + "\n")


def acquire_lock(path: Path | None) -> None:
    if path is None:
        return
    if path.exists():
        raise RuntimeError(
            f"Run lock already exists: {path}. "
            "Remove only after confirming no validator run is active."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"pid": os.getpid(), "started_at": time.strftime("%Y-%m-%d %H:%M:%S"), "argv": sys.argv},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    atexit.register(lambda: path.exists() and path.unlink())


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def load_pressure_table(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["ic_id"]: row for row in csv.DictReader(handle)}


def load_unfolding(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    if payload.get("schema_version") != 1:
        raise ValueError(f"{path} is not a schema_version=1 unfolding index")
    if payload.get("artifact_id") != "sense-unfolding-index":
        raise ValueError(f"{path} artifact_id is not 'sense-unfolding-index'")
    return payload


def build_bases(pressure: dict[str, dict[str, str]]) -> tuple[set[str], set[str]]:
    l0 = {ic for ic, row in pressure.items() if boolish(row["l0_candidate"])}
    augmented_layer = {ic for ic, row in pressure.items() if row["pressure_bucket"] in PRIMITIVE_BUCKETS}
    return l0, l0 | augmented_layer


def group_senses_by_ic(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["ic_id"]), []).append(row)
    return grouped


def fixpoint_groundable(base: set[str], senses_by_ic: dict[str, list[dict[str, Any]]]) -> set[str]:
    groundable = set(base)
    changed = True
    while changed:
        changed = False
        for ic_id, senses in senses_by_ic.items():
            if ic_id in groundable:
                continue
            for sense in senses:
                if sense.get("closure_truncated"):
                    continue
                definers = sense.get("direct_definiens_ic_ids") or []
                if all(definer in groundable for definer in definers):
                    groundable.add(ic_id)
                    changed = True
                    break
    return groundable


def classify_sense(
    sense: dict[str, Any],
    groundable: set[str],
    pressure: dict[str, dict[str, str]],
) -> dict[str, Any]:
    if sense.get("closure_truncated"):
        return {"status": "graph_data", "missing": [], "trivial": False}
    closure = list(sense.get("transitive_closure_ic_ids") or [])
    missing = [ic for ic in closure if ic not in groundable]
    if not missing:
        only_self = len(closure) <= 1 and closure[:1] == [str(sense["ic_id"])]
        trivial = bool(only_self and str(sense["ic_id"]) in groundable)
        return {"status": "closed", "missing": [], "trivial": trivial}
    buckets = {ic: pressure.get(ic, {}).get("pressure_bucket", "") for ic in missing}
    if any(bucket == ARTIFACT_BUCKET for bucket in buckets.values()):
        return {"status": "artifact", "missing": missing, "trivial": False}
    if any(bucket == CIRCULAR_BUCKET for bucket in buckets.values()):
        return {"status": "circular", "missing": missing, "trivial": False}
    if any(bucket == EXTERNAL_BUCKET for bucket in buckets.values()):
        return {"status": "external", "missing": missing, "trivial": False}
    return {"status": "background", "missing": missing, "trivial": False}


def select_targets(
    rows: list[dict[str, Any]],
    *,
    target: str,
    max_closure_size: int | None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        if target == "admitted" and row.get("admission_decision") != "admit":
            continue
        if target == "all":
            pass
        if max_closure_size is not None and int(row.get("closure_size", 0)) > max_closure_size:
            continue
        selected.append(row)
    return selected


def per_band_counts(
    statuses: list[tuple[dict[str, Any], dict[str, Any]]],
    band: int | None,
) -> dict[str, int]:
    bucket: Counter[str] = Counter()
    for row, result in statuses:
        if band is not None and int(row.get("closure_size", 0)) > band:
            continue
        bucket[result["status"]] += 1
    return dict(bucket)


def closure_rate(counts: dict[str, int], non_truncated_only: bool) -> tuple[float, int, int]:
    closed = counts.get("closed", 0)
    total = sum(counts.values()) - (counts.get("graph_data", 0) if non_truncated_only else 0)
    if total <= 0:
        return 0.0, closed, 0
    return closed / total, closed, total


def marginal_usage(
    statuses: list[tuple[dict[str, Any], dict[str, Any]]],
    base: set[str],
) -> Counter[str]:
    usage: Counter[str] = Counter()
    for row, result in statuses:
        if result["status"] != "closed":
            continue
        for ic in row.get("transitive_closure_ic_ids") or []:
            if ic in base:
                usage[ic] += 1
    return usage


def blocker_counts(statuses: list[tuple[dict[str, Any], dict[str, Any]]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for _, result in statuses:
        for ic in result["missing"]:
            counts[ic] += 1
    return counts


def render_md_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def evaluate_base(
    senses_by_ic: dict[str, list[dict[str, Any]]],
    pressure: dict[str, dict[str, str]],
    base: set[str],
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    groundable = fixpoint_groundable(base, senses_by_ic)
    statuses = [(row, classify_sense(row, groundable, pressure)) for row in targets]
    band_results: dict[str, dict[str, Any]] = {}
    for band in SENSITIVITY_BANDS:
        counts = per_band_counts(statuses, band)
        rate, closed, total = closure_rate(counts, non_truncated_only=True)
        band_results[f"closure_size_le_{band}"] = {
            "counts": counts,
            "closure_rate": rate,
            "closed": closed,
            "non_truncated_total": total,
        }
    counts_all = per_band_counts(statuses, None)
    rate_all, closed_all, total_all = closure_rate(counts_all, non_truncated_only=True)
    band_results["all_targets"] = {
        "counts": counts_all,
        "closure_rate": rate_all,
        "closed": closed_all,
        "non_truncated_total": total_all,
    }
    usage = marginal_usage(statuses, base)
    blockers = blocker_counts(statuses)
    return {
        "base_size": len(base),
        "groundable_ic_count": len(groundable),
        "bands": band_results,
        "marginal_usage_by_ic": usage,
        "blocker_counts_by_ic": blockers,
        "statuses": statuses,
        "groundable": groundable,
    }


def marginal_grounding_yield(
    eval_l0: dict[str, Any], eval_aug: dict[str, Any], augmented_layer: set[str]
) -> dict[str, Any]:
    closed_l0 = eval_l0["bands"]["all_targets"]["closed"]
    closed_aug = eval_aug["bands"]["all_targets"]["closed"]
    delta_closed = closed_aug - closed_l0
    added_base = len(augmented_layer)
    mgy = (delta_closed / added_base) if added_base > 0 else 0.0
    return {
        "added_base_size": added_base,
        "closed_l0": closed_l0,
        "closed_augmented": closed_aug,
        "delta_closed": delta_closed,
        "mgy": mgy,
    }


def falsifier_verdict(
    eval_aug: dict[str, Any],
    mgy: dict[str, Any],
    *,
    closure_rate_threshold: float,
    artifact_share_threshold: float,
    mgy_threshold: float,
) -> dict[str, Any]:
    target_band = eval_aug["bands"]["closure_size_le_200"]
    rate = target_band["closure_rate"]
    counts = target_band["counts"]
    non_truncated_total = target_band["non_truncated_total"]
    artifact_share = (counts.get("artifact", 0) / non_truncated_total) if non_truncated_total else 0.0
    triggers: list[str] = []
    if rate < closure_rate_threshold:
        triggers.append(
            f"closure_rate {rate:.3f} below threshold {closure_rate_threshold:.3f} on closure_size <= 200"
        )
    if artifact_share > artifact_share_threshold:
        triggers.append(
            f"artifact_share {artifact_share:.3f} above threshold {artifact_share_threshold:.3f}"
            " on closure_size <= 200"
        )
    if mgy["mgy"] < mgy_threshold:
        triggers.append(
            f"MGY {mgy['mgy']:.3f} below threshold {mgy_threshold:.3f}"
        )
    return {
        "closure_rate_threshold": closure_rate_threshold,
        "artifact_share_threshold": artifact_share_threshold,
        "mgy_threshold": mgy_threshold,
        "closure_rate_at_le_200": rate,
        "artifact_share_at_le_200": artifact_share,
        "mgy": mgy["mgy"],
        "triggered": triggers,
        "weakened": bool(triggers),
    }


def write_json(
    *,
    path: Path,
    args: argparse.Namespace,
    unfolding_meta: dict[str, Any],
    eval_l0: dict[str, Any],
    eval_aug: dict[str, Any],
    mgy: dict[str, Any],
    verdict: dict[str, Any],
    base_l0: set[str],
    base_aug: set[str],
    target_count: int,
) -> None:
    payload = {
        "schema_version": 1,
        "artifact_id": "base-assembler-validation",
        "definition": "closure-coverage scan of the kernel-pressure-table base over the sense unfolding index",
        "command": "uv run python scripts/validate_assembler_definitions.py",
        "argv": sys.argv,
        "unfolding": {
            "source": str(args.unfolding),
            "lexicon_id": unfolding_meta.get("lexicon_id"),
            "source_seed_resolver_id": unfolding_meta.get("source_seed_resolver_id"),
        },
        "pressure_table": str(args.pressure_table),
        "target_selector": {
            "target": args.target,
            "max_closure_size": args.max_closure_size,
            "selected_target_count": target_count,
        },
        "bases": {
            "l0_only": {"size": len(base_l0)},
            "augmented": {"size": len(base_aug)},
            "augmented_layer_size": len(base_aug - base_l0),
        },
        "evaluation": {
            "l0_only": {
                "base_size": eval_l0["base_size"],
                "groundable_ic_count": eval_l0["groundable_ic_count"],
                "bands": eval_l0["bands"],
                "marginal_usage_top": Counter(eval_l0["marginal_usage_by_ic"]).most_common(50),
                "blocker_top": Counter(eval_l0["blocker_counts_by_ic"]).most_common(50),
            },
            "augmented": {
                "base_size": eval_aug["base_size"],
                "groundable_ic_count": eval_aug["groundable_ic_count"],
                "bands": eval_aug["bands"],
                "marginal_usage_top": Counter(eval_aug["marginal_usage_by_ic"]).most_common(50),
                "blocker_top": Counter(eval_aug["blocker_counts_by_ic"]).most_common(50),
            },
        },
        "marginal_grounding_yield": mgy,
        "verdict": verdict,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False, default=list)
        handle.write("\n")


def write_report(
    *,
    path: Path,
    args: argparse.Namespace,
    unfolding_meta: dict[str, Any],
    pressure: dict[str, dict[str, str]],
    eval_l0: dict[str, Any],
    eval_aug: dict[str, Any],
    mgy: dict[str, Any],
    verdict: dict[str, Any],
    base_l0: set[str],
    base_aug: set[str],
    target_count: int,
    failed_examples: list[dict[str, Any]],
) -> None:
    lines: list[str] = []
    lines.append("# Base Assembler Validation")
    lines.append("")
    lines.append(
        "Closure-coverage scan over `data/sense-unfolding-index.json` using the implicit base"
        " derived from `data/kernel-pressure-table.csv` columns."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Unfolding index: `{args.unfolding}` (lexicon `{unfolding_meta.get('lexicon_id')}`)")
    lines.append(f"- Pressure table: `{args.pressure_table}`")
    lines.append(f"- Target selector: `{args.target}` with `closure_size <= {args.max_closure_size}` cutoff")
    lines.append(f"- Selected target rows: `{target_count}`")
    lines.append("")
    lines.append("## Bases")
    lines.append("")
    lines.append(f"- L0-only baseline size: `{len(base_l0)}`")
    primitive_label = " + ".join(sorted(PRIMITIVE_BUCKETS))
    lines.append(f"- Augmented base size (L0 + {primitive_label}): `{len(base_aug)}`")
    lines.append(f"- Augmented layer size ({primitive_label}): `{len(base_aug - base_l0)}`")
    lines.append("")
    lines.append("## Closure Rate by Band")
    lines.append("")
    lines.append("Counts are status histograms over the target selection. Closure rate is")
    lines.append("`closed / (closed + artifact + circular + external + background)`; truncated rows")
    lines.append("are reported as `graph_data` and excluded from the denominator.")
    lines.append("")
    band_rows = []
    for band_key, l0_band in eval_l0["bands"].items():
        aug_band = eval_aug["bands"][band_key]
        band_rows.append(
            {
                "band": band_key,
                "closed_l0": l0_band["closed"],
                "closed_aug": aug_band["closed"],
                "non_truncated_total": l0_band["non_truncated_total"],
                "rate_l0": f"{l0_band['closure_rate']:.4f}",
                "rate_aug": f"{aug_band['closure_rate']:.4f}",
            }
        )
    lines.extend(
        render_md_table(
            band_rows,
            ["band", "closed_l0", "closed_aug", "non_truncated_total", "rate_l0", "rate_aug"],
        )
    )
    lines.append("")
    lines.append("## Status Histogram (augmented base, `closure_size <= 200`)")
    lines.append("")
    counts_le_200 = eval_aug["bands"]["closure_size_le_200"]["counts"]
    hist_rows = [{"status": s, "count": c} for s, c in sorted(counts_le_200.items(), key=lambda kv: -kv[1])]
    lines.extend(render_md_table(hist_rows, ["status", "count"]))
    lines.append("")
    lines.append("## Marginal Grounding Yield")
    lines.append("")
    lines.append(f"- Added base ICs (augmented layer): `{mgy['added_base_size']}`")
    lines.append(f"- Closed under L0 only (all targets): `{mgy['closed_l0']}`")
    lines.append(f"- Closed under augmented (all targets): `{mgy['closed_augmented']}`")
    lines.append(f"- Delta closed: `{mgy['delta_closed']}`")
    lines.append(f"- MGY = delta_closed / added_base_size: `{mgy['mgy']:.4f}`")
    lines.append("")
    lines.append("## Falsifier Verdict")
    lines.append("")
    lines.append(f"- Closure rate at `closure_size <= 200` (augmented): `{verdict['closure_rate_at_le_200']:.4f}`")
    lines.append(f"- Artifact share at `closure_size <= 200` (augmented): `{verdict['artifact_share_at_le_200']:.4f}`")
    lines.append(f"- MGY: `{verdict['mgy']:.4f}`")
    lines.append(f"- Triggered: `{verdict['triggered'] or 'none'}`")
    lines.append(f"- Hypothesis weakened: `{verdict['weakened']}`")
    lines.append("")
    lines.append("## Top Marginal Usage (augmented base)")
    lines.append("")
    lines.append("ICs in the augmented base ranked by number of closed target rows whose closure references them.")
    lines.append("")
    usage_rows = [
        {"ic_id": ic, "primary_alias": ic.removeprefix("ic:"), "closed_uses": count}
        for ic, count in Counter(eval_aug["marginal_usage_by_ic"]).most_common(40)
    ]
    lines.extend(render_md_table(usage_rows, ["ic_id", "primary_alias", "closed_uses"]))
    lines.append("")
    lines.append("## Augmented-Layer Marginal Usage")
    lines.append("")
    aug_layer_size = len(base_aug - base_l0)
    lines.append(
        f"Marginal usage restricted to the {aug_layer_size} augmented-layer ICs added on top of L0."
    )
    lines.append("")
    aug_layer = base_aug - base_l0
    aug_usage = [
        {"ic_id": ic, "primary_alias": ic.removeprefix("ic:"), "closed_uses": eval_aug["marginal_usage_by_ic"].get(ic, 0)}
        for ic in sorted(aug_layer)
    ]
    aug_usage.sort(key=lambda row: -int(row["closed_uses"]))
    lines.extend(render_md_table(aug_usage, ["ic_id", "primary_alias", "closed_uses"]))
    lines.append("")
    lines.append("## Top Blocking ICs (augmented base)")
    lines.append("")
    lines.append("Non-base ICs that prevented closure, with their pressure-bucket label.")
    lines.append("")
    blocker_rows = [
        {
            "ic_id": ic,
            "primary_alias": ic.removeprefix("ic:"),
            "blocked_targets": count,
            "pressure_bucket": pressure.get(ic, {}).get("pressure_bucket", ""),
        }
        for ic, count in Counter(eval_aug["blocker_counts_by_ic"]).most_common(40)
    ]
    lines.extend(
        render_md_table(blocker_rows, ["ic_id", "primary_alias", "blocked_targets", "pressure_bucket"])
    )
    lines.append("")
    lines.append("## Failed Target Examples")
    lines.append("")
    lines.append("Up to ten failed rows per status (augmented base, `closure_size <= 200`).")
    lines.append("")
    for status in ("artifact", "circular", "external", "background", "graph_data"):
        bucket = [row for row in failed_examples if row["status"] == status][:10]
        if not bucket:
            continue
        lines.append(f"### {status}")
        lines.append("")
        lines.extend(
            render_md_table(
                bucket,
                ["sense_id", "ic_id", "label", "pos", "closure_size", "missing_preview"],
            )
        )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def collect_failed_examples(
    statuses: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    max_closure_size: int,
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for row, result in statuses:
        if result["status"] in ("closed",):
            continue
        if int(row.get("closure_size", 0)) > max_closure_size:
            continue
        missing = result["missing"]
        preview = ",".join(missing[:5]) + ("..." if len(missing) > 5 else "")
        examples.append(
            {
                "sense_id": row.get("sense_id"),
                "ic_id": row.get("ic_id"),
                "label": row.get("label"),
                "pos": row.get("pos"),
                "closure_size": row.get("closure_size"),
                "status": result["status"],
                "missing_preview": preview,
            }
        )
    return examples


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate base assembler closure coverage.")
    parser.add_argument("--unfolding", type=Path, default=Path("data/sense-unfolding-index.json"))
    parser.add_argument("--pressure-table", type=Path, default=Path("data/kernel-pressure-table.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/base-assembler-validation.md"))
    parser.add_argument("--json", type=Path, default=Path("reports/base-assembler-validation.json"))
    parser.add_argument(
        "--progress-log",
        type=Path,
        default=Path("reports/base-assembler-validation.progress.log"),
    )
    parser.add_argument("--lock", type=Path, default=Path("reports/base-assembler-validation.lock"))
    parser.add_argument("--target", choices=("admitted", "all"), default="admitted")
    parser.add_argument("--max-closure-size", type=int, default=200)
    parser.add_argument("--closure-rate-threshold", type=float, default=0.60)
    parser.add_argument("--artifact-share-threshold", type=float, default=0.10)
    parser.add_argument("--mgy-threshold", type=float, default=1.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    progress_log = args.progress_log if str(args.progress_log).lower() not in {"", "none", "false"} else None
    lock_path = args.lock if str(args.lock).lower() not in {"", "none", "false"} else None
    acquire_lock(lock_path)

    started = time.perf_counter()
    emit("Loading pressure table", progress_log)
    pressure = load_pressure_table(args.pressure_table)
    emit(f"Loaded {len(pressure)} pressure-table rows", progress_log)

    emit("Loading unfolding index", progress_log)
    unfolding = load_unfolding(args.unfolding)
    rows = unfolding.get("rows", [])
    emit(f"Loaded {len(rows)} unfolding rows", progress_log)

    base_l0, base_aug = build_bases(pressure)
    emit(
        f"Bases: L0 only={len(base_l0)} augmented={len(base_aug)} added_layer={len(base_aug - base_l0)}",
        progress_log,
    )

    senses_by_ic = group_senses_by_ic(rows)

    emit("Selecting target rows", progress_log)
    targets = select_targets(rows, target=args.target, max_closure_size=None)
    emit(f"Selected {len(targets)} target rows", progress_log)

    emit("Evaluating L0-only baseline", progress_log)
    eval_l0 = evaluate_base(senses_by_ic, pressure, base_l0, targets)
    emit("Evaluating augmented base", progress_log)
    eval_aug = evaluate_base(senses_by_ic, pressure, base_aug, targets)

    mgy = marginal_grounding_yield(eval_l0, eval_aug, base_aug - base_l0)
    verdict = falsifier_verdict(
        eval_aug,
        mgy,
        closure_rate_threshold=args.closure_rate_threshold,
        artifact_share_threshold=args.artifact_share_threshold,
        mgy_threshold=args.mgy_threshold,
    )

    failed_examples = collect_failed_examples(
        eval_aug["statuses"], max_closure_size=args.max_closure_size
    )

    unfolding_meta_view = {
        "lexicon_id": unfolding.get("lexicon_id"),
        "source_seed_resolver_id": unfolding.get("source_seed_resolver_id"),
    }

    emit(f"Writing {args.json}", progress_log)
    write_json(
        path=args.json,
        args=args,
        unfolding_meta=unfolding_meta_view,
        eval_l0=eval_l0,
        eval_aug=eval_aug,
        mgy=mgy,
        verdict=verdict,
        base_l0=base_l0,
        base_aug=base_aug,
        target_count=len(targets),
    )

    emit(f"Writing {args.report}", progress_log)
    write_report(
        path=args.report,
        args=args,
        unfolding_meta=unfolding_meta_view,
        pressure=pressure,
        eval_l0=eval_l0,
        eval_aug=eval_aug,
        mgy=mgy,
        verdict=verdict,
        base_l0=base_l0,
        base_aug=base_aug,
        target_count=len(targets),
        failed_examples=failed_examples,
    )

    emit(f"Done in {time.perf_counter() - started:.1f}s", progress_log)
    print(
        json.dumps(
            {
                "base_l0_size": len(base_l0),
                "base_augmented_size": len(base_aug),
                "augmented_layer_size": len(base_aug - base_l0),
                "target_count": len(targets),
                "closure_rate_le_200_l0": eval_l0["bands"]["closure_size_le_200"]["closure_rate"],
                "closure_rate_le_200_aug": eval_aug["bands"]["closure_size_le_200"]["closure_rate"],
                "mgy": mgy["mgy"],
                "verdict_weakened": verdict["weakened"],
                "verdict_triggers": verdict["triggered"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
