from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def read_candidates(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in (
            "clean_candidate",
            "admitted_clean",
            "strict_lemma_seed",
            "typed_sense_seed",
            "longman",
            "ogden",
            "high_frequency",
            "early_aoa",
            "high_concreteness",
        ):
            row[field] = parse_bool(str(row.get(field, "")))
        row["evidence_count"] = int(row.get("evidence_count") or 0)
    return rows


def derive_channels(row: dict[str, Any]) -> dict[str, bool | int]:
    structural_channels = int(bool(row["strict_lemma_seed"])) + int(bool(row["typed_sense_seed"]))
    cross_list_channels = int(bool(row["strict_lemma_seed"])) + int(bool(row["longman"])) + int(bool(row["ogden"]))
    grounding_proxy = bool(row["early_aoa"]) or bool(row["high_concreteness"])
    return {
        "strict_admission": bool(row["admitted_clean"]),
        "structural": structural_channels >= 1,
        "structural_channels": structural_channels,
        "cross_list": cross_list_channels >= 2,
        "cross_list_channels": cross_list_channels,
        "grounding_proxy": grounding_proxy,
        "grounding_proxy_channels": int(bool(row["early_aoa"])) + int(bool(row["high_concreteness"])),
    }


def l0_row(row: dict[str, Any]) -> dict[str, Any]:
    channels = derive_channels(row)
    l0_candidate = (
        bool(channels["strict_admission"])
        and bool(channels["structural"])
        and bool(channels["cross_list"])
        and bool(channels["grounding_proxy"])
    )
    return {
        "ic_id": row["ic_id"],
        "primary_alias": row["primary_alias"],
        "aliases": row["aliases"],
        "l0_candidate": l0_candidate,
        "strict_admission": channels["strict_admission"],
        "structural": channels["structural"],
        "structural_channels": channels["structural_channels"],
        "cross_list": channels["cross_list"],
        "cross_list_channels": channels["cross_list_channels"],
        "grounding_proxy": channels["grounding_proxy"],
        "grounding_proxy_channels": channels["grounding_proxy_channels"],
        "strict_lemma_seed": row["strict_lemma_seed"],
        "typed_sense_seed": row["typed_sense_seed"],
        "longman": row["longman"],
        "ogden": row["ogden"],
        "early_aoa": row["early_aoa"],
        "high_concreteness": row["high_concreteness"],
        "high_frequency": row["high_frequency"],
        "frequency": row["frequency"],
        "age_of_acquisition": row["age_of_acquisition"],
        "concreteness": row["concreteness"],
        "resolver_id": row["resolver_id"],
        "typed_seed_source": row["typed_seed_source"],
    }


def channel_count(row: dict[str, Any]) -> int:
    return sum(
        int(bool(row[field]))
        for field in ("strict_admission", "structural", "cross_list", "grounding_proxy")
    )


def sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            not bool(row["l0_candidate"]),
            -channel_count(row),
            -int(row["cross_list_channels"]),
            -int(row["structural_channels"]),
            row["primary_alias"],
        ),
    )


def write_json(path: Path, rows: list[dict[str, Any]], source: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    l0_rows = [row for row in rows if row["l0_candidate"]]
    payload = {
        "schema_version": 1,
        "artifact_id": "l0-grounded-primitives",
        "definition": "candidate grounded primitive ICs from independent channel gates; not a final semantic primitive set",
        "source": str(source),
        "gcide_channel_available": False,
        "channel_policy": {
            "strict_admission": "admitted_clean is true",
            "structural": "strict_lemma_seed or typed_sense_seed",
            "cross_list": "at least two of strict_lemma_seed, longman, ogden; GCIDE unavailable in this slice",
            "grounding_proxy": "early_aoa or high_concreteness; sensorimotor unavailable in this slice",
        },
        "counts": {
            "input_rows": len(rows),
            "l0_candidate_count": len(l0_rows),
            "near_miss_count": sum(1 for row in rows if not row["l0_candidate"] and channel_count(row) == 3),
        },
        "l0_candidates": l0_rows,
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


def write_report(path: Path, rows: list[dict[str, Any]], source: Path, top: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    l0_rows = [row for row in rows if row["l0_candidate"]]
    near_misses = [row for row in rows if not row["l0_candidate"] and channel_count(row) == 3]
    missing_counter: Counter[str] = Counter()
    for row in near_misses:
        for field in ("strict_admission", "structural", "cross_list", "grounding_proxy"):
            if not row[field]:
                missing_counter[field] += 1
    fields = [
        "primary_alias",
        "strict_admission",
        "structural",
        "cross_list",
        "grounding_proxy",
        "strict_lemma_seed",
        "typed_sense_seed",
        "longman",
        "ogden",
        "early_aoa",
        "high_concreteness",
    ]
    lines = [
        "# L0 Grounded-Primitives Derivation",
        "",
        "This is a candidate set, not a final semantic primitive inventory. It uses channel gates over the P2-backed Base English workbench and records unavailable channels explicitly.",
        "",
        "## Summary",
        "",
        f"- Source: `{source}`",
        f"- Input rows: `{len(rows)}`",
        f"- L0 candidate rows: `{len(l0_rows)}`",
        f"- Near misses (3 of 4 channels): `{len(near_misses)}`",
        "- GCIDE channel available: `False`",
        "- Sensorimotor channel available: `False`",
        "",
        "## Channel Counts",
        "",
    ]
    channel_rows = [
        {"channel": field, "count": sum(1 for row in rows if row[field])}
        for field in ("strict_admission", "structural", "cross_list", "grounding_proxy")
    ]
    lines.extend(render_table(channel_rows, ["channel", "count"]))
    lines.extend(["", "## L0 Candidates", ""])
    lines.extend(render_table(l0_rows[:top], fields))
    lines.extend(["", "## Near-Miss Missing Channel Counts", ""])
    lines.extend(render_table([{"missing_channel": k, "count": v} for k, v in missing_counter.most_common()], ["missing_channel", "count"]))
    lines.extend(["", "## Near Misses", ""])
    lines.extend(render_table(near_misses[:top], fields))
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Derive L0 candidate primitive ICs from the Base English candidate workbench.")
    parser.add_argument("--candidates", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--json", type=Path, default=Path("data/l0-grounded-primitives.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/l0-derivation.md"))
    parser.add_argument("--top", type=int, default=75)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = sort_rows([l0_row(row) for row in read_candidates(args.candidates)])
    write_json(args.json, rows, args.candidates)
    write_report(args.report, rows, args.candidates, args.top)
    print(
        json.dumps(
            {
                "input_rows": len(rows),
                "l0_candidate_rows": sum(1 for row in rows if row["l0_candidate"]),
                "json": str(args.json),
                "report": str(args.report),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
