from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from base_english_candidates import (  # noqa: E402
    EARLY_AOA_THRESHOLD,
    HIGH_CONCRETENESS_THRESHOLD,
    HIGH_FREQUENCY_THRESHOLD,
)


ARTIFACT_BUCKETS = frozenset(
    {
        "abbreviation_or_code",
        "proper_name",
        "taxon",
        "technical_term",
        "morphology_register_artifact",
    }
)

# Buckets eligible for the high-frequency `common_vocabulary` override.
# `taxon` is deliberately excluded: taxonomic vocabulary is artifact pressure
# even when it happens to be a common English surface form.
COMMON_VOCABULARY_ELIGIBLE = ARTIFACT_BUCKETS - {"taxon"}

# Buckets that promote a candidate_background IC into the validator's base.
# Membership in this set is consumed by
# scripts/validate_assembler_definitions.py via PRIMITIVE_BUCKETS.
BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})


def normalize_surface(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "")


def read_norm_file(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return {}
        word_field = next(
            (name for name in reader.fieldnames if name.lower() in {"word", "lemma", "term"}),
            None,
        )
        if word_field is None:
            return {}
        value_field = next((name for name in reader.fieldnames if name != word_field), None)
        if value_field is None:
            return {}
        norms: dict[str, float] = {}
        for row in reader:
            word = normalize_surface(row.get(word_field, "") or "")
            if not word:
                continue
            try:
                norms[word] = float(row.get(value_field, "") or "")
            except ValueError:
                continue
        return norms


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def surface_for_ic(ic_id: str) -> str:
    return ic_id.removeprefix("ic:")


def ic_for_node(node: str) -> str:
    return f"ic:{node.rsplit('::', 1)[0].lower()}"


def read_candidates(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["ic_id"]: row for row in csv.DictReader(handle)}


def read_l0(path: Path) -> set[str]:
    payload = read_json(path)
    return {str(row["ic_id"]) for row in payload.get("l0_candidates", []) if row.get("ic_id")}


def read_p2(path: Path) -> set[str]:
    payload = read_json(path)
    return {str(row["ic_id"]) for row in payload.get("seed_ics", []) if row.get("ic_id")}


def read_staged_seed(path: Path) -> set[str]:
    payload = read_json(path)
    return {str(ic_id) for ic_id in payload.get("seed_ics", [])}


def read_typed_buckets(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["ic_id"]: row["bucket"] for row in csv.DictReader(handle)}


def read_obstruction(path: Path) -> tuple[set[str], set[str], set[str]]:
    payload = read_json(path)
    explanation = payload.get("explanation", {})
    core = {ic_for_node(str(node)) for node in explanation.get("core_argument_ids", [])}
    coverage = {ic_for_node(str(node)) for node in explanation.get("coverage_argument_ids", [])}
    attack_endpoints: set[str] = set()
    for source, target in explanation.get("core_attack_ids", []):
        attack_endpoints.add(ic_for_node(str(source)))
        attack_endpoints.add(ic_for_node(str(target)))
    return core, coverage, attack_endpoints


def pressure_bucket(row: dict[str, Any]) -> tuple[str, str]:
    typed_bucket = str(row.get("typed_bucket") or "")
    flags = set(str(row.get("flags") or "").split(";")) - {""}
    if typed_bucket in COMMON_VOCABULARY_ELIGIBLE and bool(row.get("high_frequency")):
        return "common_vocabulary", "artifact lexicality but high frequency"
    if typed_bucket in ARTIFACT_BUCKETS or flags & {"numeric_form", "multiword", "technical_only"}:
        return "resource_artifact", "artifact bucket or candidate flag"
    if bool(row["obstruction_core"]) and (bool(row["l0_candidate"]) or bool(row["clean_candidate"])):
        return "primitive_candidate", "obstruction core plus L0/clean support"
    if bool(row["obstruction_core"]) and bool(row["high_frequency"]):
        return "assembler_helper", "obstruction core plus high-frequency support"
    if bool(row["obstruction_core"]):
        return "circular_dependency", "obstruction core without clean primitive support"
    if typed_bucket == "resource_specific_tail" or bool(row["kaikki_staged_seed"]) and not bool(row["p2_seed"]):
        return "external_substrate", "Kaikki-only or resource-tail signal"
    if (
        bool(row.get("p2_seed"))
        and bool(row.get("high_frequency"))
        and bool(row.get("early_aoa"))
        and not bool(row.get("obstruction_core"))
    ):
        return "base_promotable_terminal_common", "P2 terminal plus high frequency plus early AOA"
    return "candidate_background", "known candidate surface without current obstruction pressure"


def build_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    candidates = read_candidates(args.candidates)
    l0 = read_l0(args.l0)
    p2 = read_p2(args.p2_seed)
    staged = read_staged_seed(args.staged_seed)
    typed = read_typed_buckets(args.typed_buckets)
    obstruction_core, obstruction_coverage, obstruction_attack = read_obstruction(args.obstruction)
    frequency_norms = read_norm_file(args.frequency)
    aoa_norms = read_norm_file(args.age_of_acquisition)
    concreteness_norms = read_norm_file(args.concreteness)
    all_ics = set(candidates) | l0 | p2 | staged | set(typed) | obstruction_core | obstruction_coverage | obstruction_attack

    rows: list[dict[str, Any]] = []
    for ic_id in sorted(all_ics, key=surface_for_ic):
        candidate = candidates.get(ic_id, {})
        primary_alias = candidate.get("primary_alias") or surface_for_ic(ic_id)
        norm_key = normalize_surface(primary_alias)
        freq_value = frequency_norms.get(norm_key)
        aoa_value = aoa_norms.get(norm_key)
        conc_value = concreteness_norms.get(norm_key)
        row: dict[str, Any] = {
            "ic_id": ic_id,
            "primary_alias": primary_alias,
            "l0_candidate": ic_id in l0,
            "clean_candidate": boolish(candidate.get("clean_candidate", "")),
            "p2_seed": ic_id in p2,
            "kaikki_staged_seed": ic_id in staged,
            "obstruction_core": ic_id in obstruction_core,
            "obstruction_coverage": ic_id in obstruction_coverage,
            "obstruction_attack_endpoint": ic_id in obstruction_attack,
            "strict_admission": boolish(candidate.get("admitted_clean", "")),
            "evidence_count": candidate.get("evidence_count", ""),
            "frequency": "" if freq_value is None else freq_value,
            "age_of_acquisition": "" if aoa_value is None else aoa_value,
            "concreteness": "" if conc_value is None else conc_value,
            "high_frequency": (freq_value or 0.0) >= HIGH_FREQUENCY_THRESHOLD,
            "early_aoa": (aoa_value if aoa_value is not None else 99.0) <= EARLY_AOA_THRESHOLD,
            "high_concreteness": (conc_value or 0.0) >= HIGH_CONCRETENESS_THRESHOLD,
            "typed_bucket": typed.get(ic_id, ""),
            "flags": candidate.get("flags", ""),
        }
        row["pressure_bucket"], row["review_reason"] = pressure_bucket(row)
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "ic_id",
        "primary_alias",
        "l0_candidate",
        "clean_candidate",
        "p2_seed",
        "kaikki_staged_seed",
        "obstruction_core",
        "obstruction_coverage",
        "obstruction_attack_endpoint",
        "strict_admission",
        "evidence_count",
        "frequency",
        "age_of_acquisition",
        "concreteness",
        "high_frequency",
        "early_aoa",
        "high_concreteness",
        "typed_bucket",
        "flags",
        "pressure_bucket",
        "review_reason",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "artifact_id": "kernel-pressure-table",
        "definition": "IC-level agreement and obstruction-pressure table; buckets are review queues, not calibrated scores",
        "sources": {
            "candidates": str(args.candidates),
            "l0": str(args.l0),
            "p2_seed": str(args.p2_seed),
            "staged_seed": str(args.staged_seed),
            "typed_buckets": str(args.typed_buckets),
            "obstruction": str(args.obstruction),
        },
        "counts": {
            "rows": len(rows),
            "obstruction_core_rows": sum(1 for row in rows if row["obstruction_core"]),
            "l0_rows": sum(1 for row in rows if row["l0_candidate"]),
            "clean_candidate_rows": sum(1 for row in rows if row["clean_candidate"]),
        },
        "pressure_bucket_counts": dict(Counter(str(row["pressure_bucket"]) for row in rows)),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "\\|") for field in fields) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, Any]], top: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pressure_counts = Counter(str(row["pressure_bucket"]) for row in rows)
    obstruction_rows = [row for row in rows if row["obstruction_core"]]
    obstruction_counts = Counter(str(row["pressure_bucket"]) for row in obstruction_rows)
    fields = [
        "primary_alias",
        "pressure_bucket",
        "typed_bucket",
        "l0_candidate",
        "clean_candidate",
        "p2_seed",
        "kaikki_staged_seed",
        "obstruction_coverage",
        "review_reason",
    ]
    lines = [
        "# Kernel Pressure Table",
        "",
        "This is an IC-level review table over structural, candidate, and obstruction evidence. It deliberately avoids a composite score.",
        "",
        "## Summary",
        "",
        f"- Rows: `{len(rows)}`",
        f"- Obstruction-core rows: `{len(obstruction_rows)}`",
        f"- L0 rows: `{sum(1 for row in rows if row['l0_candidate'])}`",
        f"- Clean candidate rows: `{sum(1 for row in rows if row['clean_candidate'])}`",
        "",
        "## Pressure Bucket Counts",
        "",
    ]
    lines.extend(render_table([{"pressure_bucket": bucket, "count": count} for bucket, count in pressure_counts.most_common()], ["pressure_bucket", "count"]))
    lines.extend(["", "## Obstruction Core Counts", ""])
    lines.extend(render_table([{"pressure_bucket": bucket, "count": count} for bucket, count in obstruction_counts.most_common()], ["pressure_bucket", "count"]))
    lines.extend(["", "## Obstruction Core Rows", ""])
    lines.extend(render_table(obstruction_rows[:top], fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an IC-level kernel pressure table from candidate and obstruction artifacts.")
    parser.add_argument("--candidates", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--l0", type=Path, default=Path("data/l0-grounded-primitives.json"))
    parser.add_argument("--p2-seed", type=Path, default=Path("data/oewn-sense-p2-ic-seed.json"))
    parser.add_argument("--staged-seed", type=Path, default=Path("data/kaikki-staged-seed.json"))
    parser.add_argument("--typed-buckets", type=Path, default=Path("data/kaikki-seed-disagreement-typed.csv"))
    parser.add_argument("--obstruction", type=Path, default=Path("reports/kaikki-obstruction-probe-no-self-loops.json"))
    parser.add_argument("--frequency", type=Path, default=Path("data/psycholinguistic/frequency.csv"))
    parser.add_argument("--age-of-acquisition", type=Path, default=Path("data/psycholinguistic/age_of_acquisition.csv"))
    parser.add_argument("--concreteness", type=Path, default=Path("data/psycholinguistic/concreteness.csv"))
    parser.add_argument("--csv", type=Path, default=Path("data/kernel-pressure-table.csv"))
    parser.add_argument("--json", type=Path, default=Path("data/kernel-pressure-table.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/kernel-pressure-table.md"))
    parser.add_argument("--top", type=int, default=120)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_rows(args)
    write_csv(args.csv, rows)
    write_json(args.json, rows, args)
    write_report(args.report, rows, args.top)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "obstruction_core_rows": sum(1 for row in rows if row["obstruction_core"]),
                "csv": str(args.csv),
                "json": str(args.json),
                "report": str(args.report),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
