from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BUCKETS = (
    "abbreviation_or_code",
    "proper_name",
    "taxon",
    "technical_term",
    "morphology_register_artifact",
    "resource_specific_tail",
    "plausible_missing_primitive",
)

TECHNICAL_TOKENS = frozenset(
    {
        "acid",
        "algebra",
        "alkaline",
        "amide",
        "amine",
        "anatomy",
        "anemia",
        "application",
        "calculus",
        "carbonate",
        "cell",
        "chemical",
        "chemistry",
        "chromate",
        "cortex",
        "disease",
        "geometry",
        "gland",
        "hydroxide",
        "mathematics",
        "metal",
        "mineral",
        "muscle",
        "myosin",
        "oxide",
        "reactance",
        "series",
        "substance",
        "sulfate",
        "temperature",
        "theory",
        "vein",
    }
)

REGISTER_TOKENS = frozenset({"archaic", "dialect", "obsolete", "slang", "vulgar"})
PROPER_NAME_TOKENS = frozenset(
    {
        "abraham",
        "abelard",
        "aeneas",
        "agrippina",
        "athena",
        "bacchus",
        "balder",
        "barrymore",
        "beatrice",
        "boleyn",
        "bolivar",
        "christian",
        "god",
        "jesus",
        "mythology",
        "odin",
        "thor",
        "zeus",
    }
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def boolish(value: str) -> bool:
    return value.strip().lower() == "true"


def surface_for_ic(ic_id: str) -> str:
    return ic_id.removeprefix("ic:").lower()


def tokens_for(surface: str) -> list[str]:
    return [token for token in re.split(r"[_\W]+", surface.lower()) if token]


def read_l0(path: Path) -> set[str]:
    payload = read_json(path)
    return {str(row["ic_id"]) for row in payload.get("l0_candidates", []) if row.get("ic_id")}


def read_p2(path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    rows: dict[str, dict[str, Any]] = {}
    for row in payload.get("seed_ics", []):
        ic_id = row.get("ic_id")
        if ic_id:
            rows[str(ic_id)] = dict(row)
    return rows


def read_candidates(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {str(row["ic_id"]): row for row in csv.DictReader(handle)}


def bucket_for(
    ic_id: str,
    *,
    candidate: dict[str, str] | None,
    p2_row: dict[str, Any] | None,
    all_known_surfaces: set[str],
) -> tuple[str, list[str]]:
    surface = surface_for_ic(ic_id)
    tokens = tokens_for(surface)
    flags = set((candidate or {}).get("flags", "").split(";")) - {""}
    tag_counts = (candidate or {}).get("tag_counts", "")
    lexicality = str((p2_row or {}).get("lexicality", ""))
    reasons: list[str] = []

    if (
        lexicality in {"symbol-code", "abbreviation"}
        or "symbol-code" in tag_counts
        or "abbreviation" in tag_counts
        or "numeric_form" in flags
        or re.search(r"\d", surface)
        or surface.endswith(("_abbr", "_abbrev"))
        or len(surface.replace("_", "")) <= 3
    ):
        reasons.append("symbol/code/numeric/short-form signal")
        return "abbreviation_or_code", reasons

    if (
        lexicality == "proper-name"
        or "proper-name" in tag_counts
        or any(token in PROPER_NAME_TOKENS for token in tokens)
        or surface.endswith(("_legend", "_myth", "_mythology"))
    ):
        reasons.append("proper-name or mythic/name signal")
        return "proper_name", reasons

    if (
        lexicality == "taxon"
        or "taxon" in tag_counts
        or surface.endswith(("aceae", "idae", "inae", "ales", "phyta", "mycota", "opsida"))
        or any(token.endswith(("aceae", "idae", "inae", "ales", "phyta")) for token in tokens)
    ):
        reasons.append("taxonomic lexicality or suffix")
        return "taxon", reasons

    if (
        "technical_only" in flags
        or "technical-term" in tag_counts
        or any(token in TECHNICAL_TOKENS for token in tokens)
        or any(token.endswith(("ectomy", "emia", "itis", "ose", "ide", "ate")) for token in tokens)
    ):
        reasons.append("technical/domain signal")
        return "technical_term", reasons

    if candidate is None and p2_row is None:
        reasons.append("Kaikki-only row with no current OEWN candidate or P2 support")
        return "resource_specific_tail", reasons

    evidence_count = int((candidate or {}).get("evidence_count") or 0)
    if evidence_count <= 1 and p2_row is None:
        reasons.append("weak non-Kaikki support")
        return "resource_specific_tail", reasons

    if (
        any(token in REGISTER_TOKENS for token in tokens)
        or surface.endswith(("ed", "ing", "ness", "ly", "tion", "ment"))
        and stem_exists(surface, all_known_surfaces)
    ):
        reasons.append("derived/register form with known stem")
        return "morphology_register_artifact", reasons

    reasons.append("survives artifact filters")
    return "plausible_missing_primitive", reasons


def stem_exists(surface: str, all_known_surfaces: set[str]) -> bool:
    stems = []
    if surface.endswith("ing") and len(surface) > 5:
        stems.append(surface[:-3])
    if surface.endswith("ed") and len(surface) > 4:
        stems.append(surface[:-2])
    if surface.endswith("ness") and len(surface) > 6:
        stems.append(surface[:-4])
    if surface.endswith("ly") and len(surface) > 4:
        stems.append(surface[:-2])
    if surface.endswith("tion") and len(surface) > 6:
        stems.append(surface[:-4])
    if surface.endswith("ment") and len(surface) > 6:
        stems.append(surface[:-4])
    return any(stem in all_known_surfaces for stem in stems)


def build_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, int]]:
    staged = read_json(args.staged_seed)
    seed_ics = {str(ic_id) for ic_id in staged.get("seed_ics", [])}
    l0_ics = read_l0(args.l0)
    p2 = read_p2(args.p2_seed)
    candidates = read_candidates(args.candidates)
    seed_not_l0 = sorted(seed_ics - l0_ics, key=surface_for_ic)
    all_known_surfaces = {surface_for_ic(ic_id) for ic_id in seed_ics | l0_ics | set(p2) | set(candidates)}

    rows: list[dict[str, Any]] = []
    for ic_id in seed_not_l0:
        candidate = candidates.get(ic_id)
        p2_row = p2.get(ic_id)
        bucket, reasons = bucket_for(
            ic_id,
            candidate=candidate,
            p2_row=p2_row,
            all_known_surfaces=all_known_surfaces,
        )
        rows.append(
            {
                "ic_id": ic_id,
                "surface": surface_for_ic(ic_id),
                "bucket": bucket,
                "reason": "; ".join(reasons),
                "in_p2": ic_id in p2,
                "in_clean_candidates": bool(candidate and boolish(candidate.get("clean_candidate", ""))),
                "candidate_flags": "" if candidate is None else candidate.get("flags", ""),
                "p2_lexicality": "" if p2_row is None else str(p2_row.get("lexicality", "")),
                "evidence_count": "" if candidate is None else candidate.get("evidence_count", ""),
            }
        )
    counts = {
        "seed_ic_count": len(seed_ics),
        "l0_count": len(l0_ics),
        "seed_not_l0_count": len(seed_not_l0),
    }
    return rows, counts


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "ic_id",
        "surface",
        "bucket",
        "reason",
        "in_p2",
        "in_clean_candidates",
        "candidate_flags",
        "p2_lexicality",
        "evidence_count",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, Any]], counts: dict[str, int], top: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bucket_counts = Counter(row["bucket"] for row in rows)
    plausible_count = bucket_counts["plausible_missing_primitive"]
    falsifier = "pass"
    if plausible_count == 0:
        falsifier = "plausible bucket empty; classifier is probably too aggressive"
    elif plausible_count > len(rows) / 2:
        falsifier = "plausible bucket exceeds half of seed-not-L0; classifier is probably too weak"

    lines = [
        "# Kaikki Seed Disagreement Typed Buckets",
        "",
        "This is a deterministic review queue over Kaikki staged-seed ICs that are not in L0. It is not a final primitive list.",
        "",
        "## Summary",
        "",
        f"- Seed ICs: `{counts['seed_ic_count']}`",
        f"- L0 ICs: `{counts['l0_count']}`",
        f"- Seed-not-L0 rows classified: `{counts['seed_not_l0_count']}`",
        f"- Falsifier check: `{falsifier}`",
        "",
        "## Bucket Counts",
        "",
    ]
    lines.extend(render_table([{"bucket": bucket, "count": bucket_counts[bucket]} for bucket in BUCKETS], ["bucket", "count"]))
    fields = ["surface", "bucket", "reason", "in_p2", "in_clean_candidates", "p2_lexicality", "candidate_flags"]
    for bucket in BUCKETS:
        examples = [row for row in rows if row["bucket"] == bucket][:top]
        lines.extend(["", f"## {bucket}", ""])
        lines.extend(render_table(examples, fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify Kaikki staged-seed ICs not admitted into L0 into typed disagreement buckets.")
    parser.add_argument("--staged-seed", type=Path, default=Path("data/kaikki-staged-seed.json"))
    parser.add_argument("--l0", type=Path, default=Path("data/l0-grounded-primitives.json"))
    parser.add_argument("--p2-seed", type=Path, default=Path("data/oewn-sense-p2-ic-seed.json"))
    parser.add_argument("--candidates", type=Path, default=Path("data/base_english_candidates.csv"))
    parser.add_argument("--csv", type=Path, default=Path("data/kaikki-seed-disagreement-typed.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/kaikki-seed-disagreement-typed.md"))
    parser.add_argument("--top", type=int, default=50)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows, counts = build_rows(args)
    write_csv(args.csv, rows)
    write_report(args.report, rows, counts, args.top)
    print(
        json.dumps(
            {
                **counts,
                "bucket_counts": dict(Counter(row["bucket"] for row in rows)),
                "csv": str(args.csv),
                "report": str(args.report),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
