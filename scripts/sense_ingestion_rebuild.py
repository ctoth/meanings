from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from meanings.graph_analysis import analyze_kernel
from meanings.identity_clusters import HIGH_CONFIDENCE_SPELLING_VARIANTS
from meanings.wordnet_pipeline import (
    SenseLevelGraphBuild,
    candidate_seed_id,
    build_sense_level_paper_wordnet_graph,
    minset_json_summary,
)


LEXICAL_TAG = "lexical-word"
HUMAN_ADMITTED_TAGS = {"lexical-word", "phrase", "idiom"}
LEMMA_LEVEL_SELF_LOOPS = 3413
LEMMA_LEVEL_EXACT_SMALL_GREEDY = {
    "kernel": 18151,
    "core": 510,
    "satellites": 17641,
    "seed": 5044,
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def variant_aliases_by_ic() -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    for record in HIGH_CONFIDENCE_SPELLING_VARIANTS:
        aliases[record.ic_id].update(record.forms)
    return aliases


def self_loop_count(build: SenseLevelGraphBuild) -> int:
    return sum(1 for node, targets in build.adjacency.items() if node in targets)


def export_strict_seed(build: SenseLevelGraphBuild, seed_nodes: list[str], path: Path) -> dict[str, Any]:
    aliases_by_ic = variant_aliases_by_ic()
    seed_senses: list[dict[str, object]] = []
    seed_ics: dict[str, dict[str, object]] = {}
    for node in seed_nodes:
        metadata = build.node_metadata[node]
        if metadata["lexicality"] != LEXICAL_TAG:
            continue
        ic_id = str(metadata["ic_id"])
        lemma = str(metadata["lemma"])
        aliases_by_ic[ic_id].add(lemma)
        seed_senses.append(
            {
                "sense_id": metadata["sense_id"],
                "ic_id": ic_id,
                "lemma": lemma,
                "pos": metadata["pos"],
                "source_synset": metadata["source_synset"],
                "lexicality": metadata["lexicality"],
            }
        )
        seed_ics.setdefault(
            ic_id,
            {
                "ic_id": ic_id,
                "aliases": set(),
                "seed_sense_ids": [],
                "node_type": "identity-cluster",
            },
        )
        seed_ics[ic_id]["aliases"].add(lemma)
        seed_ics[ic_id]["seed_sense_ids"].append(metadata["sense_id"])

    payload_seed_ics = []
    for ic_id, record in sorted(seed_ics.items()):
        aliases = set(record["aliases"]) | aliases_by_ic.get(ic_id, set())
        payload_seed_ics.append(
            {
                "ic_id": ic_id,
                "aliases": sorted(aliases),
                "seed_sense_ids": sorted(record["seed_sense_ids"]),
                "node_type": record["node_type"],
            }
        )

    payload = {
        "surface": "strict_graph_seed_typed_sense_ic",
        "policy": "feedback vertex result restricted to lexical-word sense nodes, then grouped by IC",
        "seed_sense_count": len(seed_senses),
        "seed_ic_count": len(payload_seed_ics),
        "seed_senses": sorted(seed_senses, key=lambda item: str(item["sense_id"])),
        "seed_ics": payload_seed_ics,
    }
    write_json(path, payload)
    return payload


def export_human_vocabulary(build: SenseLevelGraphBuild, path: Path) -> dict[str, Any]:
    aliases_by_ic = variant_aliases_by_ic()
    records: dict[str, dict[str, Any]] = {}
    exclusions_by_ic: dict[str, Counter[str]] = defaultdict(Counter)
    excluded_forms_by_ic: dict[str, set[str]] = defaultdict(set)

    for metadata in build.node_metadata.values():
        ic_id = str(metadata["ic_id"])
        lemma = str(metadata["lemma"])
        tag = str(metadata["lexicality"])
        aliases_by_ic[ic_id].add(lemma)
        if tag in HUMAN_ADMITTED_TAGS:
            record = records.setdefault(
                ic_id,
                {
                    "ic_id": ic_id,
                    "aliases": set(),
                    "admitted_lexicalities": set(),
                    "admitted_sense_count": 0,
                    "source_synsets": set(),
                },
            )
            record["aliases"].add(lemma)
            record["admitted_lexicalities"].add(tag)
            record["admitted_sense_count"] += 1
            record["source_synsets"].add(metadata["source_synset"])
        else:
            exclusions_by_ic[ic_id][tag] += 1
            excluded_forms_by_ic[ic_id].add(lemma)

    payload_records = []
    for ic_id, record in sorted(records.items()):
        aliases = set(record["aliases"]) | aliases_by_ic.get(ic_id, set())
        payload_records.append(
            {
                "ic_id": ic_id,
                "aliases": sorted(aliases),
                "admitted_lexicalities": sorted(record["admitted_lexicalities"]),
                "admitted_sense_count": record["admitted_sense_count"],
                "source_synset_count": len(record["source_synsets"]),
                "exclusions": dict(sorted(exclusions_by_ic.get(ic_id, Counter()).items())),
                "excluded_forms": sorted(excluded_forms_by_ic.get(ic_id, set())),
            }
        )

    excluded_only = sorted(set(exclusions_by_ic) - set(records))
    payload = {
        "surface": "human_up_goer_vocabulary",
        "policy": "admit ICs with at least one lexical-word, phrase, or idiom sense; retain aliases; record excluded nonhuman senses",
        "admitted_ic_count": len(payload_records),
        "excluded_only_ic_count": len(excluded_only),
        "records": payload_records,
        "excluded_only_ics_sample": excluded_only[:200],
    }
    write_json(path, payload)
    return payload


def render_report(
    build: SenseLevelGraphBuild,
    analysis: object,
    strict_seed: dict[str, Any],
    vocabulary: dict[str, Any],
    summary_path: Path,
    report_path: Path,
) -> None:
    loop_count = self_loop_count(build)
    lexicality_counts = Counter(str(meta["lexicality"]) for meta in build.node_metadata.values())
    short_artifact_counts = Counter(
        str(meta["lexicality"])
        for meta in build.node_metadata.values()
        if len(str(meta["lemma"]).replace("_", "")) <= 3 and meta["lexicality"] != LEXICAL_TAG
    )
    merged_variant_form_count = sum(len(record.forms) for record in HIGH_CONFIDENCE_SPELLING_VARIANTS)
    merged_variant_ic_count = len(HIGH_CONFIDENCE_SPELLING_VARIANTS)
    acyclic_closure = analysis.residual_cyclic_scc_count == 0
    kernel_shrank = len(analysis.kernel_nodes) < LEMMA_LEVEL_EXACT_SMALL_GREEDY["kernel"]
    self_loops_shrank = loop_count < LEMMA_LEVEL_SELF_LOOPS

    summary = {
        "lexicon_id": build.lexicon_id,
        "graph_type": "sense_level_paper_wordnet",
        "node_count": len(build.nodes),
        "edge_count": analysis.edges,
        "self_loop_count": loop_count,
        "lemma_level_self_loop_baseline": LEMMA_LEVEL_SELF_LOOPS,
        "kernel_node_count": len(analysis.kernel_nodes),
        "core_node_count": len(analysis.core_nodes),
        "satellite_node_count": len(analysis.satellite_nodes),
        "seed_node_count": len(analysis.seed_nodes),
        "kernel_scc_count": len(analysis.kernel_sccs),
        "source_scc_count": len(analysis.source_sccs),
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "acyclic_definitional_closure": acyclic_closure,
        "candidate_seed_id": candidate_seed_id(analysis),
        "resolution_stats": build.resolution_stats,
        "lexicality_counts": dict(sorted(lexicality_counts.items())),
        "short_artifact_counts": dict(sorted(short_artifact_counts.items())),
        "strict_seed_sense_count": strict_seed["seed_sense_count"],
        "strict_seed_ic_count": strict_seed["seed_ic_count"],
        "admitted_ic_count": vocabulary["admitted_ic_count"],
        "excluded_only_ic_count": vocabulary["excluded_only_ic_count"],
        "merged_variant_ic_count": merged_variant_ic_count,
        "merged_variant_form_count": merged_variant_form_count,
        "prediction": {
            "kernel_shrank_vs_lemma_level": kernel_shrank,
            "self_loops_shrank_vs_lemma_level": self_loops_shrank,
        },
    }
    summary.update(minset_json_summary(analysis))
    write_json(summary_path, summary)

    lines = [
        "# Sense Ingestion Rebuild",
        "",
        "## Workflow Used",
        "",
        "- Built the new `build_sense_level_paper_wordnet_graph` surface over OEWN sense nodes.",
        "- Classified each sense at ingestion time with lexicality tags.",
        "- Merged high-confidence spelling variants into IC ids while keeping all forms.",
        "- Ran `analyze_kernel` with `exact-small-greedy` on the sense-level graph.",
        "- Exported a strict lexical seed surface and a human Up-Goer IC vocabulary surface.",
        "",
        "## Kernel Numbers",
        "",
        f"- Sense nodes: `{len(build.nodes)}`",
        f"- Edges: `{analysis.edges}`",
        f"- Kernel: `{len(analysis.kernel_nodes)}`",
        f"- Core: `{len(analysis.core_nodes)}`",
        f"- Satellites: `{len(analysis.satellite_nodes)}`",
        f"- Seed: `{len(analysis.seed_nodes)}`",
        f"- Kernel SCCs: `{len(analysis.kernel_sccs)}`",
        f"- Source SCCs: `{len(analysis.source_sccs)}`",
        f"- Residual cyclic SCCs after seed: `{analysis.residual_cyclic_scc_count}`",
        f"- Acyclic definitional closure: `{'yes' if acyclic_closure else 'no'}`",
        "",
        "## Lemma-Level Baseline",
        "",
        f"- Lemma-level exact-small-greedy Kernel: `{LEMMA_LEVEL_EXACT_SMALL_GREEDY['kernel']}`",
        f"- Lemma-level exact-small-greedy Core: `{LEMMA_LEVEL_EXACT_SMALL_GREEDY['core']}`",
        f"- Lemma-level exact-small-greedy Satellites: `{LEMMA_LEVEL_EXACT_SMALL_GREEDY['satellites']}`",
        f"- Lemma-level exact-small-greedy Seed: `{LEMMA_LEVEL_EXACT_SMALL_GREEDY['seed']}`",
        f"- Lemma-level gloss self-loops: `{LEMMA_LEVEL_SELF_LOOPS}`",
        "",
        "## Artifact Results",
        "",
        f"- Surviving sense-level self-loops: `{loop_count}`",
        f"- Self-loop shrinkage vs lemma-level: `{'yes' if self_loops_shrank else 'no'}`",
        f"- Short non-lexical artifacts quarantined/excluded: `{sum(short_artifact_counts.values())}`",
        f"- Spelling-variant IC merges: `{merged_variant_ic_count}` ICs over `{merged_variant_form_count}` forms",
        f"- Strict lexical seed ICs exported: `{strict_seed['seed_ic_count']}`",
        f"- Human vocabulary admitted ICs exported: `{vocabulary['admitted_ic_count']}`",
        f"- Excluded-only ICs: `{vocabulary['excluded_only_ic_count']}`",
        "",
        "## Lexicality Counts",
        "",
    ]
    for tag, count in sorted(lexicality_counts.items()):
        lines.append(f"- `{tag}`: `{count}`")
    lines.extend(
        [
            "",
            "## Resolution Stats",
            "",
        ]
    )
    for key, value in build.resolution_stats.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Prediction Check",
            "",
            f"- Kernel shrank vs lemma-level artifact-inflated Kernel: `{'yes' if kernel_shrank else 'no'}`",
            f"- Gloss self-loops shrank vs `3,413`: `{'yes' if self_loops_shrank else 'no'}`",
            "",
            "The self-loop prediction passed if the target is self-loop dissolution. The Kernel-size prediction is measured separately because this graph has a different node surface: every OEWN sense node is retained instead of collapsing to one `lemma::pos` node.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sense-level ingestion exports")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument("--strict-seed", default="data/oewn-sense-strict-seed.json")
    parser.add_argument("--vocabulary", default="data/oewn-upgoer-sense-vocabulary.json")
    parser.add_argument("--summary", default="reports/oewn-sense-ingestion-summary.json")
    parser.add_argument("--report", default="reports/sense-ingestion-rebuild.md")
    parser.add_argument(
        "--polysemy-fallback",
        action="store_true",
        help=(
            "Resolve ambiguous high-polysemy gloss tokens to the lowest-rank "
            "(most-frequent) candidate sense within the candidate identity "
            "cluster instead of skipping. The audit (reports/audit-new-src.md "
            "finding #2) showed the default skip behaviour is structurally "
            "concentrated on the genus vocabulary and biases the sense-Kernel "
            "smaller; this flag enables the resolver fix."
        ),
    )
    args = parser.parse_args()

    build = build_sense_level_paper_wordnet_graph(
        args.lexicon, polysemy_fallback=args.polysemy_fallback
    )
    analysis = analyze_kernel(build.nodes, build.adjacency, seed_method="exact-small-greedy")
    strict_seed = export_strict_seed(build, analysis.seed_nodes, Path(args.strict_seed))
    vocabulary = export_human_vocabulary(build, Path(args.vocabulary))
    render_report(build, analysis, strict_seed, vocabulary, Path(args.summary), Path(args.report))


if __name__ == "__main__":
    main()
