"""Inventory the `resource_artifact` ICs in the kernel pressure table.

Read-only Phase 1 audit for `reports/artifact-bucket-reaudit-workstream.md`.

For each IC currently classified `pressure_bucket = "resource_artifact"`:

- Count how many admitted, non-truncated rows in
  `data/sense-unfolding-index.json` reference the IC in
  `transitive_closure_ic_ids`. This is an upper bound on the IC's blocker
  impact: any admitted target whose closure references the IC cannot
  close unless the IC is itself groundable.
- Carry the `typed_bucket` label so the report can group by classification
  reason.
- Carry a small psycholinguistic profile (`frequency`,
  `age_of_acquisition`, `concreteness`, `high_frequency`, `early_aoa`,
  `high_concreteness`) so Phase 2 can write data-driven rules.

The script does not propose changes. It only describes state.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ARTIFACT_BUCKET = "resource_artifact"


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def load_pressure_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_unfolding(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{path} rows must be a list")
    return rows


def containment_counts(
    unfolding_rows: list[dict[str, Any]], targets_only_admitted: bool
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in unfolding_rows:
        if targets_only_admitted and row.get("admission_decision") != "admit":
            continue
        if row.get("closure_truncated"):
            continue
        for ic in row.get("transitive_closure_ic_ids") or []:
            counts[ic] += 1
    return counts


def render_md_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def format_optional_float(value: str) -> str:
    if not value:
        return ""
    try:
        return f"{float(value):.3f}"
    except ValueError:
        return value


def build_audit(
    pressure_rows: list[dict[str, str]],
    unfolding_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    containment = containment_counts(unfolding_rows, targets_only_admitted=True)
    audit: list[dict[str, Any]] = []
    for row in pressure_rows:
        if row.get("pressure_bucket") != ARTIFACT_BUCKET:
            continue
        ic_id = row["ic_id"]
        count = int(containment.get(ic_id, 0))
        audit.append(
            {
                "ic_id": ic_id,
                "primary_alias": row.get("primary_alias", ""),
                "typed_bucket": row.get("typed_bucket", ""),
                "flags": row.get("flags", ""),
                "containment_admitted": count,
                "frequency": row.get("frequency", ""),
                "age_of_acquisition": row.get("age_of_acquisition", ""),
                "concreteness": row.get("concreteness", ""),
                "high_frequency": row.get("high_frequency", ""),
                "early_aoa": row.get("early_aoa", ""),
                "high_concreteness": row.get("high_concreteness", ""),
            }
        )
    audit.sort(key=lambda row: (-int(row["containment_admitted"]), str(row["ic_id"])))

    blocking_audit = [row for row in audit if int(row["containment_admitted"]) > 0]
    nonblocking_count = len(audit) - len(blocking_audit)
    by_typed_bucket: Counter[str] = Counter(str(row["typed_bucket"]) or "<empty>" for row in blocking_audit)
    blockers_by_typed_bucket: dict[str, int] = {}
    for row in blocking_audit:
        bucket = str(row["typed_bucket"]) or "<empty>"
        blockers_by_typed_bucket[bucket] = blockers_by_typed_bucket.get(bucket, 0) + int(
            row["containment_admitted"]
        )

    summary = {
        "resource_artifact_total": len(audit),
        "blocking_at_least_one_admitted": len(blocking_audit),
        "non_blocking_count": nonblocking_count,
        "typed_bucket_row_counts": dict(by_typed_bucket.most_common()),
        "typed_bucket_blocker_sums": dict(
            sorted(blockers_by_typed_bucket.items(), key=lambda kv: -kv[1])
        ),
    }

    top100 = blocking_audit[:100]
    top100_typed_buckets: Counter[str] = Counter(str(row["typed_bucket"]) or "<empty>" for row in top100)
    summary["top100_typed_bucket_counts"] = dict(top100_typed_buckets.most_common())

    return audit, summary


def write_json(
    path: Path,
    *,
    args: argparse.Namespace,
    audit: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    payload = {
        "schema_version": 1,
        "artifact_id": "artifact-bucket-audit",
        "definition": "containment audit of resource_artifact ICs over admitted non-truncated unfolding rows",
        "inputs": {
            "pressure_table": str(args.pressure_table),
            "unfolding": str(args.unfolding),
        },
        "summary": summary,
        "audit": audit,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_report(
    path: Path,
    *,
    args: argparse.Namespace,
    audit: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    blocking = [row for row in audit if int(row["containment_admitted"]) > 0]
    lines: list[str] = []
    lines.append("# Artifact Bucket Audit")
    lines.append("")
    lines.append(
        "Read-only Phase 1 inventory of every IC currently labelled"
        " `pressure_bucket = resource_artifact` in `data/kernel-pressure-table.csv`."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Pressure table: `{args.pressure_table}`")
    lines.append(f"- Unfolding index: `{args.unfolding}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total `resource_artifact` rows: `{summary['resource_artifact_total']}`")
    lines.append(
        f"- Rows blocking at least one admitted target: `{summary['blocking_at_least_one_admitted']}`"
    )
    lines.append(
        f"- Rows with zero containment in admitted targets: `{summary['non_blocking_count']}`"
    )
    lines.append("")
    lines.append("Containment is the number of admitted, non-truncated rows in")
    lines.append("`data/sense-unfolding-index.json` whose `transitive_closure_ic_ids` references")
    lines.append("the IC. It is an upper bound on the IC's blocker impact under any base that")
    lines.append("does not include the IC.")
    lines.append("")
    lines.append("## Typed Bucket — Row Counts (blocking only)")
    lines.append("")
    lines.append("How many `resource_artifact` ICs sit in each `typed_bucket`, among ICs that")
    lines.append("block at least one admitted target.")
    lines.append("")
    bucket_count_rows = [
        {"typed_bucket": bucket, "row_count": count}
        for bucket, count in summary["typed_bucket_row_counts"].items()
    ]
    lines.extend(render_md_table(bucket_count_rows, ["typed_bucket", "row_count"]))
    lines.append("")
    lines.append("## Typed Bucket — Blocker Sums")
    lines.append("")
    lines.append("Sum of containment counts within each `typed_bucket`. This is the cumulative")
    lines.append("admitted-target reach of the bucket — the falsifier metric for the")
    lines.append("workstream's Phase 1 acceptance gate.")
    lines.append("")
    blocker_sum_rows = [
        {"typed_bucket": bucket, "blocker_sum": count}
        for bucket, count in summary["typed_bucket_blocker_sums"].items()
    ]
    lines.extend(render_md_table(blocker_sum_rows, ["typed_bucket", "blocker_sum"]))
    lines.append("")
    lines.append("## Top 100 Blockers — Typed Bucket Distribution")
    lines.append("")
    lines.append(
        "Distribution of `typed_bucket` over the top 100 blocking ICs. The workstream's"
    )
    lines.append(
        "Phase 1 falsifier triggers if this distribution does not concentrate in one or"
    )
    lines.append("two `typed_bucket` values.")
    lines.append("")
    top100_rows = [
        {"typed_bucket": bucket, "count_in_top_100": count}
        for bucket, count in summary["top100_typed_bucket_counts"].items()
    ]
    lines.extend(render_md_table(top100_rows, ["typed_bucket", "count_in_top_100"]))
    lines.append("")
    lines.append("## Top 60 Blocking ICs")
    lines.append("")
    lines.append("Ranked by containment over admitted, non-truncated targets.")
    lines.append("")
    top_rows = [
        {
            "ic_id": row["ic_id"],
            "primary_alias": row["primary_alias"],
            "typed_bucket": row["typed_bucket"],
            "containment_admitted": row["containment_admitted"],
            "frequency": format_optional_float(str(row["frequency"])),
            "age_of_acquisition": format_optional_float(str(row["age_of_acquisition"])),
            "concreteness": format_optional_float(str(row["concreteness"])),
        }
        for row in blocking[:60]
    ]
    lines.extend(
        render_md_table(
            top_rows,
            [
                "ic_id",
                "primary_alias",
                "typed_bucket",
                "containment_admitted",
                "frequency",
                "age_of_acquisition",
                "concreteness",
            ],
        )
    )
    lines.append("")
    lines.append("## Per-Typed-Bucket Top 20 Examples")
    lines.append("")
    by_bucket: dict[str, list[dict[str, Any]]] = {}
    for row in blocking:
        by_bucket.setdefault(str(row["typed_bucket"]) or "<empty>", []).append(row)
    for bucket in sorted(by_bucket, key=lambda key: -sum(int(r["containment_admitted"]) for r in by_bucket[key])):
        bucket_rows = by_bucket[bucket][:20]
        lines.append(f"### {bucket}")
        lines.append("")
        example_rows = [
            {
                "ic_id": row["ic_id"],
                "primary_alias": row["primary_alias"],
                "containment_admitted": row["containment_admitted"],
                "frequency": format_optional_float(str(row["frequency"])),
                "concreteness": format_optional_float(str(row["concreteness"])),
            }
            for row in bucket_rows
        ]
        lines.extend(
            render_md_table(
                example_rows,
                ["ic_id", "primary_alias", "containment_admitted", "frequency", "concreteness"],
            )
        )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inventory resource_artifact ICs.")
    parser.add_argument("--pressure-table", type=Path, default=Path("data/kernel-pressure-table.csv"))
    parser.add_argument("--unfolding", type=Path, default=Path("data/sense-unfolding-index.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/artifact-bucket-audit.md"))
    parser.add_argument("--json", type=Path, default=Path("reports/artifact-bucket-audit.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pressure_rows = load_pressure_table(args.pressure_table)
    unfolding_rows = load_unfolding(args.unfolding)
    audit, summary = build_audit(pressure_rows, unfolding_rows)
    write_json(args.json, args=args, audit=audit, summary=summary)
    write_report(args.report, args=args, audit=audit, summary=summary)
    print(
        json.dumps(
            {
                "resource_artifact_total": summary["resource_artifact_total"],
                "blocking_count": summary["blocking_at_least_one_admitted"],
                "top100_typed_bucket_counts": summary["top100_typed_bucket_counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
