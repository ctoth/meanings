from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CSV_FIELDS = (
    "ic_id",
    "primary_alias",
    "aliases",
    "decision",
    "evidence_count",
    "clean_candidate",
    "admitted_clean",
    "strict_lemma_seed",
    "typed_sense_seed",
    "resolver_id",
    "longman",
    "ogden",
    "high_frequency",
    "early_aoa",
    "high_concreteness",
    "frequency",
    "age_of_acquisition",
    "concreteness",
    "sense_count",
    "tag_counts",
    "fired_rules",
    "flags",
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def read_word_set(path: Path) -> set[str]:
    words: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            word = normalize_surface(line.strip())
            if word:
                words.add(word)
    return words


def normalize_surface(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "")


def read_norms(paths: list[Path]) -> dict[str, dict[str, float]]:
    norms: dict[str, dict[str, float]] = {}
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                continue
            word_field = next((name for name in reader.fieldnames if name.lower() in {"word", "lemma", "term"}), None)
            value_fields = [name for name in reader.fieldnames if name != word_field]
            if not word_field or not value_fields:
                continue
            value_field = value_fields[0]
            metric = value_field.strip().lower()
            for row in reader:
                word = normalize_surface(row.get(word_field, ""))
                if not word:
                    continue
                try:
                    value = float(row.get(value_field, ""))
                except ValueError:
                    continue
                norms.setdefault(word, {})[metric] = value
    return norms


def read_seed_surfaces(path: Path) -> set[str]:
    seeds: set[str] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            seeds.add(normalize_surface(row.get("lemma", "")))
    return seeds


def read_typed_seed_ics(path: Path) -> set[str]:
    payload = read_json(path)
    return {str(row.get("ic_id")) for row in payload.get("seed_senses", []) if row.get("ic_id")}


def flags_for(alias: str, aliases: list[str], tag_counts: dict[str, Any], norm_row: dict[str, float]) -> list[str]:
    flags: list[str] = []
    normalized = normalize_surface(alias)
    if re.fullmatch(r"\d+(st|nd|rd|th)?", normalized):
        flags.append("numeric_form")
    if "_" in normalized or any(" " in item for item in aliases):
        flags.append("multiword")
    if not norm_row.get("frequency"):
        flags.append("missing_frequency")
    if not norm_row.get("age_of_acquisition"):
        flags.append("missing_aoa")
    if not norm_row.get("concreteness"):
        flags.append("missing_concreteness")
    if set(tag_counts) <= {"technical-term"}:
        flags.append("technical_only")
    if any(tag in tag_counts for tag in ("proper-name", "taxon", "chemical", "symbol-code", "abbreviation")):
        flags.append("artifact_reading_present")
    return flags


def evidence_count(
    *,
    admitted_clean: bool,
    strict_lemma_seed: bool,
    typed_sense_seed: bool,
    longman: bool,
    ogden: bool,
    high_frequency: bool,
    early_aoa: bool,
    high_concreteness: bool,
) -> int:
    return sum(
        (
            admitted_clean,
            strict_lemma_seed,
            typed_sense_seed,
            longman,
            ogden,
            high_frequency,
            early_aoa,
            high_concreteness,
        )
    )


def best_norm_row(aliases: list[str], norms: dict[str, dict[str, float]]) -> dict[str, float]:
    rows = [norms.get(normalize_surface(alias), {}) for alias in aliases]
    rows = [row for row in rows if row]
    if not rows:
        return {}
    return {
        "frequency": max((row.get("frequency") for row in rows if row.get("frequency") is not None), default=None),
        "age_of_acquisition": min((row.get("age_of_acquisition") for row in rows if row.get("age_of_acquisition") is not None), default=None),
        "concreteness": max((row.get("concreteness") for row in rows if row.get("concreteness") is not None), default=None),
    }


def build_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    admission = read_json(args.admission)
    strict_seeds = read_seed_surfaces(args.seed_surfaces)
    typed_seed_ics = read_typed_seed_ics(args.typed_seed)
    longman = read_word_set(args.longman)
    ogden = read_word_set(args.ogden)
    norms = read_norms(args.norms)

    rows: list[dict[str, Any]] = []
    for entry in admission.get("admitted", []):
        aliases = [str(alias) for alias in entry.get("aliases", []) if str(alias)]
        if not aliases:
            continue
        primary = sorted(aliases, key=lambda item: (len(item), item))[0]
        alias_keys = {normalize_surface(alias) for alias in aliases}
        norm_row = best_norm_row(aliases, norms)
        tag_counts = entry.get("tag_counts", {})
        if not isinstance(tag_counts, dict):
            tag_counts = {}
        flags = flags_for(primary, aliases, tag_counts, norm_row)
        strict_lemma_seed = bool(alias_keys & strict_seeds)
        typed_sense_seed = str(entry.get("ic_id")) in typed_seed_ics
        in_longman = bool(alias_keys & longman)
        in_ogden = bool(alias_keys & ogden)
        high_frequency = (norm_row.get("frequency") or 0.0) >= 5.0
        early_aoa = (norm_row.get("age_of_acquisition") or 99.0) <= 6.0
        high_concreteness = (norm_row.get("concreteness") or 0.0) >= 4.0
        admitted_clean = not any(flag in flags for flag in ("numeric_form", "multiword", "artifact_reading_present", "technical_only"))
        clean_candidate = admitted_clean and (in_longman or in_ogden)
        count = evidence_count(
            admitted_clean=admitted_clean,
            strict_lemma_seed=strict_lemma_seed,
            typed_sense_seed=typed_sense_seed,
            longman=in_longman,
            ogden=in_ogden,
            high_frequency=high_frequency,
            early_aoa=early_aoa,
            high_concreteness=high_concreteness,
        )
        rows.append(
            {
                "ic_id": str(entry.get("ic_id")),
                "primary_alias": primary,
                "aliases": ";".join(sorted(aliases)),
                "decision": "admit",
                "evidence_count": count,
                "clean_candidate": clean_candidate,
                "admitted_clean": admitted_clean,
                "strict_lemma_seed": strict_lemma_seed,
                "typed_sense_seed": typed_sense_seed,
                "resolver_id": "legacy_typed_sense_seed_pre_p2",
                "longman": in_longman,
                "ogden": in_ogden,
                "high_frequency": high_frequency,
                "early_aoa": early_aoa,
                "high_concreteness": high_concreteness,
                "frequency": norm_row.get("frequency"),
                "age_of_acquisition": norm_row.get("age_of_acquisition"),
                "concreteness": norm_row.get("concreteness"),
                "sense_count": entry.get("sense_count", 0),
                "tag_counts": json.dumps(tag_counts, sort_keys=True),
                "fired_rules": ";".join(str(rule) for rule in entry.get("fired_rules", [])),
                "flags": ";".join(flags),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            not bool(row["clean_candidate"]),
            -int(row["evidence_count"]),
            not bool(row["longman"]),
            not bool(row["ogden"]),
            row["primary_alias"],
        ),
    )


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in CSV_FIELDS})


def render_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = []
        for field in fields:
            value = row.get(field)
            text = "" if value is None else str(value)
            values.append(text.replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, Any]], top: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flag_counts = Counter(flag for row in rows for flag in str(row["flags"]).split(";") if flag)
    lines = [
        "# Base English Candidate Workbench",
        "",
        "This is not a final Base English list. It is an agreement-filtered IC-level workbench built from existing admission, graph-seed, controlled-vocabulary, and psycholinguistic evidence. It deliberately avoids a composite score.",
        "",
        "## Summary",
        "",
        f"- Candidate IC rows: `{len(rows)}`",
        f"- Clean candidate rows: `{sum(1 for row in rows if row['clean_candidate'])}`",
        f"- Strict lemma-seed rows: `{sum(1 for row in rows if row['strict_lemma_seed'])}`",
        f"- Typed sense-seed rows: `{sum(1 for row in rows if row['typed_sense_seed'])}`",
        f"- Longman-supported rows: `{sum(1 for row in rows if row['longman'])}`",
        f"- Ogden-supported rows: `{sum(1 for row in rows if row['ogden'])}`",
        "",
        "## Clean Candidates",
        "",
    ]
    fields = [
        "primary_alias",
        "evidence_count",
        "strict_lemma_seed",
        "typed_sense_seed",
        "longman",
        "ogden",
        "high_frequency",
        "early_aoa",
        "high_concreteness",
        "frequency",
        "age_of_acquisition",
        "concreteness",
        "flags",
    ]
    clean_rows = [row for row in rows if row["clean_candidate"]]
    lines.extend(render_table(clean_rows[:top], fields))
    lines.extend(["", "## Flag Counts", ""])
    lines.extend(render_table([{"flag": flag, "count": count} for flag, count in flag_counts.most_common()], ["flag", "count"]))
    lines.extend(["", "## Flagged Rows Excluded From Clean Candidate View", ""])
    flagged = [row for row in rows if row["flags"]]
    lines.extend(render_table(flagged[:top], fields))
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the Base English candidate workbench from existing artifacts.")
    parser.add_argument("--admission", type=Path, default=Path("data/oewn-upgoer-admitted.json"))
    parser.add_argument("--seed-surfaces", type=Path, default=Path("data/english_seed_surfaces.csv"))
    parser.add_argument("--typed-seed", type=Path, default=Path("data/oewn-sense-strict-seed.json"))
    parser.add_argument("--longman", type=Path, default=Path("data/external-dictionaries/longman-defining-vocabulary.txt"))
    parser.add_argument("--ogden", type=Path, default=Path("data/external-dictionaries/ogden-basic-english-850.txt"))
    parser.add_argument(
        "--norms",
        type=Path,
        nargs="*",
        default=[
            Path("data/psycholinguistic/frequency.csv"),
            Path("data/psycholinguistic/age_of_acquisition.csv"),
            Path("data/psycholinguistic/concreteness.csv"),
        ],
    )
    parser.add_argument("--output", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/base-english-candidates.md"))
    parser.add_argument("--top", type=int, default=50)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_rows(args)
    write_csv(args.output, rows)
    write_report(args.report, rows, args.top)
    print(json.dumps({"rows": len(rows), "output": str(args.output), "report": str(args.report)}, indent=2))


if __name__ == "__main__":
    main()
