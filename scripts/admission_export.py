"""Export the human Up-Goer vocabulary as the admitted extension of the
defeasible admission policy in ``meanings.admission``.

This supersedes ``scripts/sense_ingestion_rebuild.py``'s ``HUMAN_ADMITTED_TAGS``
lexicality-tag filter (which ``reports/synthesis-review-codex.md`` §5 correctly
called "a lexicality filter dressed in the language of admission"). Here every
IC's admission is the verdict of an ordered, superiority-bearing rule set; the
output records the per-IC rationale (the fired/defeated rules and the conditions
that held), the admitted aliases, and the exclusions.

Run::

    uv run python scripts/admission_export.py

Writes ``data/oewn-upgoer-admitted.json`` (the admitted vocabulary + the
quarantine and uncertain lists) and ``reports/admission-policy.json`` (the
policy + the bucket counts + ~20 example ICs per bucket).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from meanings.admission import (
    AdmissionDecision,
    AdmissionVerdict,
    default_policy,
    evaluate_collection,
    ic_records_from_node_metadata,
)
from meanings.identity_clusters import spelling_variant_index
from meanings.wordnet_pipeline import build_sense_level_paper_wordnet_graph

# the old lexicality-tag filter's headline number (reports/oewn-sense-ingestion-summary.json)
OLD_LEXICALITY_FILTER_ADMITTED_IC_COUNT = 121375

# ICs we want to surface in the report no matter which bucket they land in.
SPOTLIGHT_ICS = ["ic:no", "ic:s", "ic:a", "ic:color", "ic:colour", "ic:e", "ic:g"]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def merge_rationales_by_ic() -> dict[str, str]:
    out: dict[str, str] = {}
    for view in spelling_variant_index().values():
        out.setdefault(view.ic_id, view.rationale)
    return out


def verdict_brief(v: AdmissionVerdict, *, full_rationale: bool = False) -> dict[str, object]:
    d = {
        "ic_id": v.ic_id,
        "decision": v.decision.value,
        "aliases": list(v.aliases),
        "tag_counts": dict(v.facts.tag_counts),
        "sense_count": v.facts.sense_count,
        "fired_rules": [f.rule_id for f in v.fired],
        "defeated_rules": [f.rule_id for f in v.defeated],
        "rationale": list(v.rationale) if full_rationale else list(v.rationale[:6]),
        "excluded_sense_ids": list(v.excluded_sense_ids[:8]),
    }
    return d


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the admitted human Up-Goer vocabulary")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument("--admitted", default="data/oewn-upgoer-admitted.json")
    parser.add_argument("--summary", default="reports/admission-policy.json")
    parser.add_argument(
        "--expanded", action="store_true",
        help="enable r_admit_phrase_idiom (the expanded list including phrases/idioms)",
    )
    parser.add_argument("--examples", type=int, default=20)
    args = parser.parse_args()

    policy = default_policy(admit_phrases_and_idioms=args.expanded)

    print(f"[admission_export] building sense-level graph over {args.lexicon} ...")
    build = build_sense_level_paper_wordnet_graph(args.lexicon)
    print(f"[admission_export] {len(build.node_metadata)} sense nodes; grouping into ICs ...")
    ics = ic_records_from_node_metadata(
        build.node_metadata, merge_rationale_by_ic=merge_rationales_by_ic()
    )
    print(f"[admission_export] {len(ics)} ICs; running admission policy ...")
    verdicts = evaluate_collection(ics, policy)

    by_decision: dict[str, list[AdmissionVerdict]] = {d.value: [] for d in AdmissionDecision}
    for v in verdicts:
        by_decision[v.decision.value].append(v)
    counts = {k: len(v) for k, v in by_decision.items()}
    counts_total = sum(counts.values())
    print(f"[admission_export] decisions: {counts} (total {counts_total})")

    admitted = sorted(by_decision["admit"], key=lambda v: v.ic_id)
    quarantined = sorted(by_decision["quarantine"], key=lambda v: v.ic_id)
    excluded = sorted(by_decision["exclude"], key=lambda v: v.ic_id)
    uncertain = sorted(by_decision["uncertain"], key=lambda v: v.ic_id)

    # --- the admitted vocabulary file ------------------------------------
    admitted_payload = {
        "surface": "human_up_goer_vocabulary",
        "definition": "the admitted extension of the defeasible admission policy in meanings.admission",
        "policy": policy.to_json(),
        "lexicon_id": build.lexicon_id,
        "expanded_list": bool(args.expanded),
        "counts": counts,
        "old_lexicality_filter_admitted_ic_count": OLD_LEXICALITY_FILTER_ADMITTED_IC_COUNT,
        "delta_vs_old_filter": len(admitted) - OLD_LEXICALITY_FILTER_ADMITTED_IC_COUNT,
        "admitted": [
            {
                "ic_id": v.ic_id,
                "aliases": list(v.aliases),
                "excluded_sense_ids": list(v.excluded_sense_ids),
                "tag_counts": dict(v.facts.tag_counts),
                "sense_count": v.facts.sense_count,
                "fired_rules": [f.rule_id for f in v.fired],
                "rationale": list(v.rationale),
            }
            for v in admitted
        ],
        "quarantined": [verdict_brief(v, full_rationale=True) for v in quarantined],
        "uncertain": [verdict_brief(v, full_rationale=True) for v in uncertain],
        "excluded_count": len(excluded),
    }
    write_json(Path(args.admitted), admitted_payload)
    print(f"[admission_export] wrote {args.admitted}")

    # --- the summary report (json) ---------------------------------------
    n = args.examples
    by_ic = {v.ic_id: v for v in verdicts}
    spotlight = [verdict_brief(by_ic[i], full_rationale=True) for i in SPOTLIGHT_ICS if i in by_ic]
    fired_combo_counts = Counter(",".join(sorted(f.rule_id for f in v.fired)) for v in verdicts)
    summary_payload = {
        "policy": policy.to_json(),
        "lexicon_id": build.lexicon_id,
        "expanded_list": bool(args.expanded),
        "counts": counts,
        "ic_total": counts_total,
        "old_lexicality_filter_admitted_ic_count": OLD_LEXICALITY_FILTER_ADMITTED_IC_COUNT,
        "delta_admitted_vs_old_filter": len(admitted) - OLD_LEXICALITY_FILTER_ADMITTED_IC_COUNT,
        "fired_rule_histogram": dict(fired_combo_counts.most_common()),
        "examples": {
            "admitted": [verdict_brief(v) for v in admitted[:n]],
            "quarantined": [verdict_brief(v, full_rationale=True) for v in quarantined[:n]],
            "excluded": [verdict_brief(v) for v in excluded[:n]],
            "uncertain": [verdict_brief(v, full_rationale=True) for v in uncertain[:n]],
        },
        "spotlight_ics": spotlight,
    }
    write_json(Path(args.summary), summary_payload)
    print(f"[admission_export] wrote {args.summary}")


if __name__ == "__main__":
    main()
