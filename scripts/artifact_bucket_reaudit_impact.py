"""Compute the A/B impact of the Phase 2 artifact-bucket rules.

Loads the pre-change and post-change pressure tables, classifies every
admitted unfolding-index target under both, and emits the workstream's
Phase 4 deliverables: closed/artifact/MGY before/after, bucket migration
list, and per-sense regression check.

This script re-uses the closure-fixpoint and status-classification logic
from `scripts/validate_assembler_definitions.py` so that the impact
report uses exactly the validator's metric.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from validate_assembler_definitions import (  # noqa: E402
    build_bases,
    classify_sense,
    fixpoint_groundable,
    group_senses_by_ic,
    load_pressure_table,
    load_unfolding,
    select_targets,
)


SENSITIVITY_BANDS = (50, 100, 200)


def evaluate(
    pressure: dict[str, dict[str, str]],
    senses_by_ic: dict[str, list[dict[str, Any]]],
    targets: list[dict[str, Any]],
    base: set[str],
) -> dict[str, Any]:
    groundable = fixpoint_groundable(base, senses_by_ic)
    per_sense: dict[str, str] = {}
    blocker_counts: Counter[str] = Counter()
    band_counts: dict[int, Counter[str]] = {band: Counter() for band in SENSITIVITY_BANDS}
    all_counts: Counter[str] = Counter()
    for row in targets:
        result = classify_sense(row, groundable, pressure)
        status = result["status"]
        per_sense[str(row["sense_id"])] = status
        all_counts[status] += 1
        for band in SENSITIVITY_BANDS:
            if int(row.get("closure_size", 0)) <= band:
                band_counts[band][status] += 1
        for ic in result["missing"]:
            blocker_counts[ic] += 1
    return {
        "groundable_count": len(groundable),
        "per_sense_status": per_sense,
        "all_counts": dict(all_counts),
        "band_counts": {band: dict(counts) for band, counts in band_counts.items()},
        "blocker_counts": blocker_counts,
    }


def closure_rate(counts: dict[str, int]) -> tuple[float, int, int]:
    closed = counts.get("closed", 0)
    non_truncated_total = sum(counts.values()) - counts.get("graph_data", 0)
    if non_truncated_total <= 0:
        return 0.0, closed, 0
    return closed / non_truncated_total, closed, non_truncated_total


def artifact_share(counts: dict[str, int]) -> tuple[float, int, int]:
    artifact = counts.get("artifact", 0)
    non_truncated_total = sum(counts.values()) - counts.get("graph_data", 0)
    if non_truncated_total <= 0:
        return 0.0, artifact, 0
    return artifact / non_truncated_total, artifact, non_truncated_total


def render_md_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def bucket_migration(
    pre: dict[str, dict[str, str]], post: dict[str, dict[str, str]]
) -> tuple[Counter[tuple[str, str]], list[dict[str, str]]]:
    transitions: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, str]] = []
    for ic_id, pre_row in pre.items():
        post_row = post.get(ic_id)
        if post_row is None:
            continue
        pre_b = pre_row.get("pressure_bucket", "")
        post_b = post_row.get("pressure_bucket", "")
        if pre_b != post_b:
            transitions[(pre_b, post_b)] += 1
            rows.append(
                {
                    "ic_id": ic_id,
                    "primary_alias": post_row.get("primary_alias", ""),
                    "pre_pressure_bucket": pre_b,
                    "post_pressure_bucket": post_b,
                    "typed_bucket_pre": pre_row.get("typed_bucket", ""),
                    "typed_bucket_post": post_row.get("typed_bucket", ""),
                    "frequency_post": post_row.get("frequency", ""),
                    "high_frequency_post": post_row.get("high_frequency", ""),
                }
            )
    rows.sort(key=lambda row: (row["pre_pressure_bucket"], row["post_pressure_bucket"], row["ic_id"]))
    return transitions, rows


def compute_regressions(
    pre_status: dict[str, str], post_status: dict[str, str]
) -> list[tuple[str, str, str]]:
    regressions: list[tuple[str, str, str]] = []
    for sense_id, pre_s in pre_status.items():
        post_s = post_status.get(sense_id, "<missing>")
        if pre_s == "closed" and post_s != "closed":
            regressions.append((sense_id, pre_s, post_s))
    return regressions


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute artifact-bucket re-audit impact.")
    parser.add_argument(
        "--pressure-table-pre", type=Path, default=Path("data/kernel-pressure-table.pre.csv")
    )
    parser.add_argument(
        "--pressure-table-post", type=Path, default=Path("data/kernel-pressure-table.csv")
    )
    parser.add_argument("--unfolding", type=Path, default=Path("data/sense-unfolding-index.json"))
    parser.add_argument(
        "--report", type=Path, default=Path("reports/artifact-bucket-reaudit-impact.md")
    )
    parser.add_argument(
        "--json", type=Path, default=Path("reports/artifact-bucket-reaudit-impact.json")
    )
    parser.add_argument(
        "--per-sense-csv",
        type=Path,
        default=Path("reports/artifact-bucket-reaudit-impact-per-sense.csv"),
    )
    parser.add_argument("--max-closure-size", type=int, default=200)
    args = parser.parse_args()

    pressure_pre = load_pressure_table(args.pressure_table_pre)
    pressure_post = load_pressure_table(args.pressure_table_post)
    unfolding = load_unfolding(args.unfolding)
    rows = unfolding.get("rows", [])

    base_pre_l0, base_pre_aug = build_bases(pressure_pre)
    base_post_l0, base_post_aug = build_bases(pressure_post)
    augmented_layer_pre = sorted(base_pre_aug - base_pre_l0)
    augmented_layer_post = sorted(base_post_aug - base_post_l0)

    senses_by_ic = group_senses_by_ic(rows)
    targets = select_targets(rows, target="admitted", max_closure_size=None)

    eval_pre_l0 = evaluate(pressure_pre, senses_by_ic, targets, base_pre_l0)
    eval_pre_aug = evaluate(pressure_pre, senses_by_ic, targets, base_pre_aug)
    eval_post_l0 = evaluate(pressure_post, senses_by_ic, targets, base_post_l0)
    eval_post_aug = evaluate(pressure_post, senses_by_ic, targets, base_post_aug)

    regressions = compute_regressions(
        eval_pre_aug["per_sense_status"], eval_post_aug["per_sense_status"]
    )

    counts_pre_le_200 = eval_pre_aug["band_counts"][200]
    counts_post_le_200 = eval_post_aug["band_counts"][200]
    rate_pre, closed_pre, total_pre = closure_rate(counts_pre_le_200)
    rate_post, closed_post, total_post = closure_rate(counts_post_le_200)
    art_pre, art_count_pre, _ = artifact_share(counts_pre_le_200)
    art_post, art_count_post, _ = artifact_share(counts_post_le_200)

    mgy_pre = (
        (eval_pre_aug["all_counts"].get("closed", 0) - eval_pre_l0["all_counts"].get("closed", 0))
        / max(1, len(augmented_layer_pre))
    )
    mgy_post = (
        (eval_post_aug["all_counts"].get("closed", 0) - eval_post_l0["all_counts"].get("closed", 0))
        / max(1, len(augmented_layer_post))
    )

    transitions, migration_rows = bucket_migration(pressure_pre, pressure_post)

    args.per_sense_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.per_sense_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sense_id", "status_pre_aug", "status_post_aug"])
        for sense_id in sorted(eval_pre_aug["per_sense_status"]):
            writer.writerow(
                [
                    sense_id,
                    eval_pre_aug["per_sense_status"][sense_id],
                    eval_post_aug["per_sense_status"].get(sense_id, "<missing>"),
                ]
            )

    payload = {
        "schema_version": 1,
        "artifact_id": "artifact-bucket-reaudit-impact",
        "definition": "A/B impact report for Phase 4 of artifact-bucket-reaudit-workstream",
        "inputs": {
            "pressure_table_pre": str(args.pressure_table_pre),
            "pressure_table_post": str(args.pressure_table_post),
            "unfolding": str(args.unfolding),
        },
        "augmented_layer": {
            "pre": augmented_layer_pre,
            "post": augmented_layer_post,
            "added": sorted(set(augmented_layer_post) - set(augmented_layer_pre)),
            "removed": sorted(set(augmented_layer_pre) - set(augmented_layer_post)),
        },
        "closure_size_le_200": {
            "counts_pre_aug": counts_pre_le_200,
            "counts_post_aug": counts_post_le_200,
            "closure_rate_pre": rate_pre,
            "closure_rate_post": rate_post,
            "closure_rate_delta": rate_post - rate_pre,
            "artifact_share_pre": art_pre,
            "artifact_share_post": art_post,
            "artifact_share_delta_pp": (art_post - art_pre) * 100,
        },
        "all_targets": {
            "counts_pre_aug": eval_pre_aug["all_counts"],
            "counts_post_aug": eval_post_aug["all_counts"],
            "closed_pre_l0": eval_pre_l0["all_counts"].get("closed", 0),
            "closed_post_l0": eval_post_l0["all_counts"].get("closed", 0),
            "closed_pre_aug": eval_pre_aug["all_counts"].get("closed", 0),
            "closed_post_aug": eval_post_aug["all_counts"].get("closed", 0),
            "mgy_pre": mgy_pre,
            "mgy_post": mgy_post,
        },
        "regression": {
            "regressed_count": len(regressions),
            "examples": regressions[:50],
        },
        "bucket_migration": {
            "transitions": [{"from": pre, "to": post, "count": count} for (pre, post), count in transitions.most_common()],
            "total_changed_ics": len(migration_rows),
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    with args.json.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")

    lines: list[str] = []
    lines.append("# Artifact Bucket Re-audit Impact")
    lines.append("")
    lines.append("Phase 4 A/B diff for `reports/artifact-bucket-reaudit-workstream.md`.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Pre pressure table: `{args.pressure_table_pre}`")
    lines.append(f"- Post pressure table: `{args.pressure_table_post}`")
    lines.append(f"- Unfolding index: `{args.unfolding}`")
    lines.append("")
    lines.append("## Augmented Layer")
    lines.append("")
    lines.append(f"- Pre augmented layer size: `{len(augmented_layer_pre)}`")
    lines.append(f"- Post augmented layer size: `{len(augmented_layer_post)}`")
    added = sorted(set(augmented_layer_post) - set(augmented_layer_pre))
    removed = sorted(set(augmented_layer_pre) - set(augmented_layer_post))
    lines.append(f"- Added by R1 norm join: `{added or 'none'}`")
    lines.append(f"- Removed: `{removed or 'none'}`")
    lines.append("")
    lines.append("## Closure Status — `closure_size <= 200`")
    lines.append("")
    band_rows = []
    for status in sorted(set(counts_pre_le_200) | set(counts_post_le_200)):
        band_rows.append(
            {
                "status": status,
                "pre": counts_pre_le_200.get(status, 0),
                "post": counts_post_le_200.get(status, 0),
                "delta": counts_post_le_200.get(status, 0) - counts_pre_le_200.get(status, 0),
            }
        )
    lines.extend(render_md_table(band_rows, ["status", "pre", "post", "delta"]))
    lines.append("")
    lines.append(f"- Closure rate pre: `{rate_pre:.4f}` (`{closed_pre}/{total_pre}`)")
    lines.append(f"- Closure rate post: `{rate_post:.4f}` (`{closed_post}/{total_post}`)")
    lines.append(f"- Closure rate delta: `{(rate_post - rate_pre) * 100:+.2f} pp`")
    lines.append(f"- Artifact share pre: `{art_pre:.4f}` (`{art_count_pre}`)")
    lines.append(f"- Artifact share post: `{art_post:.4f}` (`{art_count_post}`)")
    lines.append(
        f"- Artifact share delta: `{(art_post - art_pre) * 100:+.2f} pp`"
    )
    lines.append("")
    lines.append("## All Targets")
    lines.append("")
    lines.append(f"- Closed under L0 only, pre: `{eval_pre_l0['all_counts'].get('closed', 0)}`")
    lines.append(f"- Closed under L0 only, post: `{eval_post_l0['all_counts'].get('closed', 0)}`")
    lines.append(f"- Closed under augmented, pre: `{eval_pre_aug['all_counts'].get('closed', 0)}`")
    lines.append(f"- Closed under augmented, post: `{eval_post_aug['all_counts'].get('closed', 0)}`")
    lines.append(f"- MGY pre: `{mgy_pre:.4f}` over `{len(augmented_layer_pre)}` added ICs")
    lines.append(f"- MGY post: `{mgy_post:.4f}` over `{len(augmented_layer_post)}` added ICs")
    lines.append("")
    lines.append("## Regression Gate")
    lines.append("")
    lines.append(f"- Regressed sense count (closed pre, not closed post): `{len(regressions)}`")
    if regressions:
        lines.append("")
        lines.append("First 50 regressed senses:")
        lines.append("")
        reg_rows = [
            {"sense_id": s, "status_pre": pre, "status_post": post}
            for (s, pre, post) in regressions[:50]
        ]
        lines.extend(render_md_table(reg_rows, ["sense_id", "status_pre", "status_post"]))
    lines.append("")
    lines.append("## Bucket Transitions")
    lines.append("")
    transition_rows = [
        {"from": pre, "to": post, "count": count}
        for (pre, post), count in transitions.most_common()
    ]
    lines.extend(render_md_table(transition_rows, ["from", "to", "count"]))
    lines.append("")
    lines.append(f"Total ICs with changed `pressure_bucket`: `{len(migration_rows)}`.")
    lines.append("")
    lines.append("## Top 50 Migrated ICs by Frequency")
    lines.append("")
    migration_sample = sorted(
        migration_rows,
        key=lambda row: (
            row["pre_pressure_bucket"] != "resource_artifact",
            -float(row["frequency_post"] or 0),
            row["ic_id"],
        ),
    )[:50]
    lines.extend(
        render_md_table(
            migration_sample,
            [
                "ic_id",
                "primary_alias",
                "pre_pressure_bucket",
                "post_pressure_bucket",
                "typed_bucket_post",
                "frequency_post",
                "high_frequency_post",
            ],
        )
    )
    lines.append("")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")

    print(
        json.dumps(
            {
                "regressed_count": len(regressions),
                "closure_rate_pre_le_200": rate_pre,
                "closure_rate_post_le_200": rate_post,
                "artifact_share_pre_le_200": art_pre,
                "artifact_share_post_le_200": art_post,
                "artifact_share_delta_pp": (art_post - art_pre) * 100,
                "closed_pre_aug": eval_pre_aug["all_counts"].get("closed", 0),
                "closed_post_aug": eval_post_aug["all_counts"].get("closed", 0),
                "mgy_pre": mgy_pre,
                "mgy_post": mgy_post,
                "augmented_layer_pre_size": len(augmented_layer_pre),
                "augmented_layer_post_size": len(augmented_layer_post),
                "total_bucket_changes": len(migration_rows),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
