"""Build the IC-merge table over OEWN and write reports/ic-merge-method.json.

Usage:
    uv run python scripts/build_ic_table.py [--lexicon oewn:2024] [--edit-cap 1]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import wn

from meanings.identity_clusters import (
    ORIGINAL_REGRESSION_PAIRS,
    build_identity_clusters,
    dump_table_json,
)

_REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lexicon", default="oewn:2024")
    ap.add_argument("--edit-cap", type=int, default=1)
    ap.add_argument("--spot", type=int, default=40)
    args = ap.parse_args()

    wn.download(args.lexicon)
    lexicon = wn.Wordnet(args.lexicon)
    result = build_identity_clusters(lexicon, edit_distance_cap=args.edit_cap)
    dump_table_json(result)

    stats = result["stats"]
    clusters = result["clusters"]
    merges = result["merge_records"]
    rejected = result["rejected"]
    form_to_ic = result["form_to_ic"]

    # regression check
    missed = []
    for a, b in ORIGINAL_REGRESSION_PAIRS:
        if form_to_ic.get(a) is None or form_to_ic.get(a) != form_to_ic.get(b):
            missed.append((a, b))

    # spot-check sample of merges
    rng = random.Random(20260512)
    sample = rng.sample(merges, min(args.spot, len(merges)))
    spot = [
        {
            "forms": sorted(m.contributing_forms),
            "rule_id": m.rule_id,
            "gloss_score": round(m.gloss_score, 3),
            "pos": m.pos,
            "matched_senses": list(m.matched_sense_pair),
        }
        for m in sample
    ]

    # cluster-size distribution
    size_hist: dict[int, int] = {}
    for c in clusters:
        size_hist[len(c.forms)] = size_hist.get(len(c.forms), 0) + 1

    summary = {
        "stats": stats,
        "baseline_pairs": 7,
        "baseline_forms": 14,
        "regression_missed": missed,
        "cluster_size_histogram": dict(sorted(size_hist.items())),
        "rejected_examples": [
            {"forms": [f1, f2], "rule_ids": rids, "best_gloss_score": round(s, 3)}
            for (f1, f2, rids, s) in rejected[:60]
        ],
        "spot_sample": spot,
    }
    out = _REPO / "reports" / "ic-merge-method.summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "spot_sample"}, indent=2))
    print("\n--- spot sample ---")
    for s in spot:
        print(s)
    print(f"\nregression missed: {missed}")
    print("wrote: reports/ic-merge-method.json, reports/ic-merge-method.summary.json")


if __name__ == "__main__":
    main()
