"""Inventory `candidate_background` and `external_substrate` blockers.

Read-only Phase 1 audit for
`reports/background-bucket-reaudit-workstream.md`.

For every IC currently classified `pressure_bucket in
{"candidate_background", "external_substrate"}`:

- Count how many admitted, non-truncated rows in
  `data/sense-unfolding-index.json` reference the IC in
  `transitive_closure_ic_ids`.
- Carry the psycholinguistic profile so Phase 2 can write data-driven
  promotion rules.

The script reports the two buckets separately. For each bucket it
contrasts the psycholinguistic profile of the top-100 blockers against
the bottom-100 blockers - the workstream's Phase 1 falsifier check.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


TARGET_BUCKETS = ("candidate_background", "external_substrate")


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


def containment_counts(unfolding_rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in unfolding_rows:
        if row.get("admission_decision") != "admit":
            continue
        if row.get("closure_truncated"):
            continue
        for ic in row.get("transitive_closure_ic_ids") or []:
            counts[ic] += 1
    return counts


def parse_float(value: str) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def render_md_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def format_optional_float(value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        return f"{float(value):.3f}"
    if isinstance(value, str):
        try:
            return f"{float(value):.3f}"
        except ValueError:
            return value
    return str(value)


def build_bucket_audit(
    bucket: str,
    pressure_rows: list[dict[str, str]],
    containment: Counter[str],
) -> list[dict[str, Any]]:
    audit: list[dict[str, Any]] = []
    for row in pressure_rows:
        if row.get("pressure_bucket") != bucket:
            continue
        ic_id = row["ic_id"]
        count = int(containment.get(ic_id, 0))
        audit.append(
            {
                "ic_id": ic_id,
                "primary_alias": row.get("primary_alias", ""),
                "typed_bucket": row.get("typed_bucket", ""),
                "flags": row.get("flags", ""),
                "p2_seed": boolish(row.get("p2_seed", "")),
                "strict_admission": boolish(row.get("strict_admission", "")),
                "obstruction_core": boolish(row.get("obstruction_core", "")),
                "containment_admitted": count,
                "frequency": parse_float(row.get("frequency", "")),
                "age_of_acquisition": parse_float(row.get("age_of_acquisition", "")),
                "concreteness": parse_float(row.get("concreteness", "")),
                "high_frequency": boolish(row.get("high_frequency", "")),
                "early_aoa": boolish(row.get("early_aoa", "")),
                "high_concreteness": boolish(row.get("high_concreteness", "")),
            }
        )
    audit.sort(key=lambda r: (-int(r["containment_admitted"]), str(r["ic_id"])))
    return audit


def norm_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def median_optional(values: list[float]) -> float | None:
        return statistics.median(values) if values else None

    freq = [r["frequency"] for r in rows if r["frequency"] is not None]
    aoa = [r["age_of_acquisition"] for r in rows if r["age_of_acquisition"] is not None]
    conc = [r["concreteness"] for r in rows if r["concreteness"] is not None]
    return {
        "row_count": len(rows),
        "has_frequency_count": len(freq),
        "has_aoa_count": len(aoa),
        "has_concreteness_count": len(conc),
        "frequency_median": median_optional(freq),
        "aoa_median": median_optional(aoa),
        "concreteness_median": median_optional(conc),
        "high_frequency_count": sum(1 for r in rows if r["high_frequency"]),
        "early_aoa_count": sum(1 for r in rows if r["early_aoa"]),
        "high_concreteness_count": sum(1 for r in rows if r["high_concreteness"]),
        "all_three_count": sum(
            1 for r in rows if r["high_frequency"] and r["early_aoa"] and r["high_concreteness"]
        ),
        "p2_seed_count": sum(1 for r in rows if r["p2_seed"]),
    }


def write_json(
    path: Path,
    *,
    args: argparse.Namespace,
    bucket_audits: dict[str, list[dict[str, Any]]],
    bucket_summaries: dict[str, dict[str, Any]],
    top_bottom_contrast: dict[str, dict[str, dict[str, Any]]],
) -> None:
    payload = {
        "schema_version": 1,
        "artifact_id": "background-bucket-audit",
        "definition": "containment audit of candidate_background and external_substrate ICs",
        "inputs": {
            "pressure_table": str(args.pressure_table),
            "unfolding": str(args.unfolding),
        },
        "summary": bucket_summaries,
        "top_bottom_norm_contrast": top_bottom_contrast,
        "audit": bucket_audits,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False, default=str)
        handle.write("\n")


def write_report(
    path: Path,
    *,
    args: argparse.Namespace,
    bucket_audits: dict[str, list[dict[str, Any]]],
    bucket_summaries: dict[str, dict[str, Any]],
    top_bottom_contrast: dict[str, dict[str, dict[str, Any]]],
) -> None:
    lines: list[str] = []
    lines.append("# Background Bucket Audit")
    lines.append("")
    lines.append(
        "Read-only Phase 1 inventory of `candidate_background` and"
        " `external_substrate` ICs in `data/kernel-pressure-table.csv`."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Pressure table: `{args.pressure_table}`")
    lines.append(f"- Unfolding index: `{args.unfolding}`")
    lines.append("")
    lines.append("## Bucket Summary")
    lines.append("")
    summary_rows = []
    for bucket in TARGET_BUCKETS:
        s = bucket_summaries[bucket]
        summary_rows.append(
            {
                "pressure_bucket": bucket,
                "rows": s["row_count"],
                "blocking": s["blocking_count"],
                "non_blocking": s["non_blocking_count"],
                "with_freq": s["has_frequency_count"],
                "with_aoa": s["has_aoa_count"],
                "with_conc": s["has_concreteness_count"],
                "freq_med": format_optional_float(s["frequency_median"]),
                "aoa_med": format_optional_float(s["aoa_median"]),
                "conc_med": format_optional_float(s["concreteness_median"]),
                "high_freq": s["high_frequency_count"],
                "early_aoa": s["early_aoa_count"],
                "high_conc": s["high_concreteness_count"],
                "all_three": s["all_three_count"],
                "p2_seed": s["p2_seed_count"],
            }
        )
    lines.extend(
        render_md_table(
            summary_rows,
            [
                "pressure_bucket",
                "rows",
                "blocking",
                "non_blocking",
                "with_freq",
                "with_aoa",
                "with_conc",
                "freq_med",
                "aoa_med",
                "conc_med",
                "high_freq",
                "early_aoa",
                "high_conc",
                "all_three",
                "p2_seed",
            ],
        )
    )
    lines.append("")
    lines.append("## Top-100 vs Bottom-100 Norm Contrast")
    lines.append("")
    lines.append(
        "If the top-100 blockers do not have meaningfully higher frequency / earlier"
    )
    lines.append(
        "AOA / higher concreteness than the bottom-100 (among ICs with at least one"
    )
    lines.append("blocked target), the promote-by-norms hypothesis fails.")
    lines.append("")
    contrast_rows = []
    for bucket in TARGET_BUCKETS:
        contrast = top_bottom_contrast[bucket]
        contrast_rows.append(
            {
                "pressure_bucket": bucket,
                "top100_freq_med": format_optional_float(contrast["top"]["frequency_median"]),
                "bot100_freq_med": format_optional_float(contrast["bot"]["frequency_median"]),
                "top100_aoa_med": format_optional_float(contrast["top"]["aoa_median"]),
                "bot100_aoa_med": format_optional_float(contrast["bot"]["aoa_median"]),
                "top100_conc_med": format_optional_float(contrast["top"]["concreteness_median"]),
                "bot100_conc_med": format_optional_float(contrast["bot"]["concreteness_median"]),
                "top100_p2_seed": contrast["top"]["p2_seed_count"],
                "bot100_p2_seed": contrast["bot"]["p2_seed_count"],
            }
        )
    lines.extend(
        render_md_table(
            contrast_rows,
            [
                "pressure_bucket",
                "top100_freq_med",
                "bot100_freq_med",
                "top100_aoa_med",
                "bot100_aoa_med",
                "top100_conc_med",
                "bot100_conc_med",
                "top100_p2_seed",
                "bot100_p2_seed",
            ],
        )
    )
    lines.append("")
    for bucket in TARGET_BUCKETS:
        audit = bucket_audits[bucket]
        blocking = [r for r in audit if int(r["containment_admitted"]) > 0]
        lines.append(f"## Top 50 Blocking ICs - `{bucket}`")
        lines.append("")
        top_rows = []
        for row in blocking[:50]:
            top_rows.append(
                {
                    "ic_id": row["ic_id"],
                    "primary_alias": row["primary_alias"],
                    "containment_admitted": row["containment_admitted"],
                    "p2_seed": row["p2_seed"],
                    "typed_bucket": row["typed_bucket"],
                    "freq": format_optional_float(row["frequency"]),
                    "aoa": format_optional_float(row["age_of_acquisition"]),
                    "conc": format_optional_float(row["concreteness"]),
                    "norms": "+".join(
                        flag
                        for flag, ok in (
                            ("HF", row["high_frequency"]),
                            ("EA", row["early_aoa"]),
                            ("HC", row["high_concreteness"]),
                        )
                        if ok
                    )
                    or "-",
                }
            )
        lines.extend(
            render_md_table(
                top_rows,
                [
                    "ic_id",
                    "primary_alias",
                    "containment_admitted",
                    "p2_seed",
                    "typed_bucket",
                    "freq",
                    "aoa",
                    "conc",
                    "norms",
                ],
            )
        )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory candidate_background and external_substrate blockers."
    )
    parser.add_argument(
        "--pressure-table", type=Path, default=Path("data/kernel-pressure-table.csv")
    )
    parser.add_argument("--unfolding", type=Path, default=Path("data/sense-unfolding-index.json"))
    parser.add_argument(
        "--report", type=Path, default=Path("reports/background-bucket-audit.md")
    )
    parser.add_argument(
        "--json", type=Path, default=Path("reports/background-bucket-audit.json")
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pressure_rows = load_pressure_table(args.pressure_table)
    unfolding_rows = load_unfolding(args.unfolding)
    containment = containment_counts(unfolding_rows)

    bucket_audits: dict[str, list[dict[str, Any]]] = {}
    bucket_summaries: dict[str, dict[str, Any]] = {}
    top_bottom_contrast: dict[str, dict[str, dict[str, Any]]] = {}
    for bucket in TARGET_BUCKETS:
        audit = build_bucket_audit(bucket, pressure_rows, containment)
        blocking = [r for r in audit if int(r["containment_admitted"]) > 0]
        summary = norm_summary(blocking)
        summary["row_count"] = len(audit)
        summary["blocking_count"] = len(blocking)
        summary["non_blocking_count"] = len(audit) - len(blocking)
        bucket_audits[bucket] = audit
        bucket_summaries[bucket] = summary
        top = blocking[:100]
        bot = blocking[-100:]
        top_bottom_contrast[bucket] = {
            "top": norm_summary(top),
            "bot": norm_summary(bot),
        }

    write_json(
        args.json,
        args=args,
        bucket_audits=bucket_audits,
        bucket_summaries=bucket_summaries,
        top_bottom_contrast=top_bottom_contrast,
    )
    write_report(
        args.report,
        args=args,
        bucket_audits=bucket_audits,
        bucket_summaries=bucket_summaries,
        top_bottom_contrast=top_bottom_contrast,
    )
    print(
        json.dumps(
            {
                bucket: {
                    "blocking": bucket_summaries[bucket]["blocking_count"],
                    "total": bucket_summaries[bucket]["row_count"],
                    "all_three_norms": bucket_summaries[bucket]["all_three_count"],
                    "p2_seed_blocking": bucket_summaries[bucket]["p2_seed_count"],
                    "top100_freq_med": top_bottom_contrast[bucket]["top"]["frequency_median"],
                    "bot100_freq_med": top_bottom_contrast[bucket]["bot"]["frequency_median"],
                }
                for bucket in TARGET_BUCKETS
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
