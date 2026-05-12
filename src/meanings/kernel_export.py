from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from meanings.annotations import AnnotationStore, annotation_coverage, load_annotation_csvs
from meanings.graph_analysis import choose_core_nodes, induced_subgraph, source_sccs, strongly_connected_components
from meanings.wordnet_pipeline import build_paper_wordnet_graph


CSV_FIELDS = (
    "node_id",
    "lemma",
    "pos",
    "surface_word",
    "gloss",
    "component",
    "is_seed",
    "seed_method",
    "candidate_seed_id",
    "layer",
    "degree_score",
    "outdegree",
    "indegree",
    "frequency",
    "age_of_acquisition",
    "concreteness",
    "source_label",
)

SURFACE_FIELDS = (
    "lemma",
    "surface_word",
    "seed_node_count",
    "source_node_ids",
    "parts_of_speech",
    "max_degree_score",
    "best_frequency",
    "earliest_age_of_acquisition",
    "mean_concreteness",
)

DEFAULT_ANNOTATION_PATHS = (
    Path("data/psycholinguistic/frequency.csv"),
    Path("data/psycholinguistic/age_of_acquisition.csv"),
    Path("data/psycholinguistic/concreteness.csv"),
)


@dataclass(slots=True)
class ExportInputs:
    summary: dict[str, Any]
    layers: dict[str, Any]
    annotation_paths: list[Path]


@dataclass(slots=True)
class KernelMembership:
    layer_by_node: dict[str, int]
    seed_nodes: set[str]
    core_nodes: set[str]
    satellite_nodes: set[str]

    @property
    def kernel_nodes(self) -> set[str]:
        return set(self.layer_by_node)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_inputs(summary_path: Path, layers_path: Path, annotation_paths: list[Path]) -> ExportInputs:
    summary = read_json(summary_path)
    layers = read_json(layers_path)
    effective_annotations = annotation_paths or [path for path in DEFAULT_ANNOTATION_PATHS if path.exists()]
    return ExportInputs(summary=summary, layers=layers, annotation_paths=effective_annotations)


def validate_inputs(inputs: ExportInputs) -> None:
    summary = inputs.summary
    layers = inputs.layers
    summary_candidate = summary.get("candidate_seed_id")
    layers_candidate = layers.get("candidate_seed_id")
    if summary_candidate != layers_candidate:
        raise ValueError(
            "Summary/layers candidate_seed_id mismatch: "
            f"{summary_candidate!r} != {layers_candidate!r}"
        )
    if summary.get("residual_cyclic_scc_count") != 0:
        raise ValueError("Summary does not describe an acyclic residual seed result")
    if layers.get("residual_cyclic_scc_count") != 0:
        raise ValueError("Layers do not describe an acyclic residual seed result")
    layer_by_node = layers.get("layer_by_node")
    if not isinstance(layer_by_node, dict) or not layer_by_node:
        raise ValueError("Layers JSON must contain a non-empty layer_by_node object")


def split_node_id(node_id: str) -> tuple[str, str]:
    if "::" not in node_id:
        raise ValueError(f"Expected lemma::pos node id, got {node_id!r}")
    lemma, pos = node_id.rsplit("::", 1)
    return lemma, pos


def label_gloss(label: str) -> str:
    marker = " :: "
    if marker not in label:
        return ""
    return label.split(marker, 1)[1]


def compute_degrees(adjacency: dict[str, set[str]]) -> tuple[dict[str, int], dict[str, int]]:
    indegree = {node: 0 for node in adjacency}
    for targets in adjacency.values():
        for target in targets:
            if target in indegree:
                indegree[target] += 1
    outdegree = {node: len(targets) for node, targets in adjacency.items()}
    return indegree, outdegree


def derive_membership(
    layer_by_node: dict[str, int],
    adjacency: dict[str, set[str]],
    core_policy: str,
) -> KernelMembership:
    kernel_nodes = set(layer_by_node)
    kernel_graph = induced_subgraph(kernel_nodes, adjacency)
    kernel_sccs = strongly_connected_components(kernel_nodes, kernel_graph)
    source_components = source_sccs(kernel_nodes, kernel_graph)
    core_nodes = choose_core_nodes(kernel_sccs, source_components, core_policy)
    return KernelMembership(
        layer_by_node=layer_by_node,
        seed_nodes={node for node, layer in layer_by_node.items() if layer == 0},
        core_nodes=core_nodes,
        satellite_nodes=kernel_nodes - core_nodes,
    )


def component_for(node: str, membership: KernelMembership) -> str:
    if node in membership.core_nodes:
        return "core"
    if node in membership.satellite_nodes:
        return "satellite"
    return "kernel"


def row_for_node(
    node: str,
    membership: KernelMembership,
    labels: dict[str, str],
    seed_method: str,
    candidate_seed_id: str,
    indegree: dict[str, int],
    outdegree: dict[str, int],
    annotations: AnnotationStore,
) -> dict[str, Any]:
    lemma, pos = split_node_id(node)
    label = labels.get(node, node)
    frequency = annotations.get(lemma, "frequency")
    age = annotations.get(lemma, "age_of_acquisition")
    concreteness = annotations.get(lemma, "concreteness")
    return {
        "node_id": node,
        "lemma": lemma,
        "pos": pos,
        "surface_word": lemma.replace("_", " "),
        "gloss": label_gloss(label),
        "component": component_for(node, membership),
        "is_seed": membership.layer_by_node[node] == 0,
        "seed_method": seed_method,
        "candidate_seed_id": candidate_seed_id,
        "layer": membership.layer_by_node[node],
        "degree_score": indegree.get(node, 0) + outdegree.get(node, 0),
        "outdegree": outdegree.get(node, 0),
        "indegree": indegree.get(node, 0),
        "frequency": frequency,
        "age_of_acquisition": age,
        "concreteness": concreteness,
        "source_label": label,
    }


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


def write_seed_surfaces_csv(path: Path, surfaces: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SURFACE_FIELDS)
        writer.writeheader()
        for surface in surfaces:
            writer.writerow(
                {
                    "lemma": surface["lemma"],
                    "surface_word": surface["surface_word"],
                    "seed_node_count": surface["seed_node_count"],
                    "source_node_ids": ";".join(surface["source_node_ids"]),
                    "parts_of_speech": ";".join(surface["parts_of_speech"]),
                    "max_degree_score": surface["max_degree_score"],
                    "best_frequency": csv_value(surface["best_frequency"]),
                    "earliest_age_of_acquisition": csv_value(surface["earliest_age_of_acquisition"]),
                    "mean_concreteness": csv_value(surface["mean_concreteness"]),
                }
            )


def write_seed_words(path: Path, surfaces: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for surface in surfaces:
            handle.write(str(surface["surface_word"]))
            handle.write("\n")


def collapse_seed_surfaces(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["is_seed"]:
            grouped.setdefault(row["lemma"], []).append(row)

    surfaces: list[dict[str, Any]] = []
    for lemma, seed_rows in grouped.items():
        degree = max(int(row["degree_score"]) for row in seed_rows)
        frequency_values = [row["frequency"] for row in seed_rows if row["frequency"] is not None]
        age_values = [row["age_of_acquisition"] for row in seed_rows if row["age_of_acquisition"] is not None]
        concrete_values = [row["concreteness"] for row in seed_rows if row["concreteness"] is not None]
        surfaces.append(
            {
                "lemma": lemma,
                "surface_word": lemma.replace("_", " "),
                "seed_node_count": len(seed_rows),
                "source_node_ids": sorted(row["node_id"] for row in seed_rows),
                "parts_of_speech": sorted({row["pos"] for row in seed_rows}),
                "max_degree_score": degree,
                "best_frequency": max(frequency_values) if frequency_values else None,
                "earliest_age_of_acquisition": min(age_values) if age_values else None,
                "mean_concreteness": sum(concrete_values) / len(concrete_values) if concrete_values else None,
            }
        )
    return sorted(
        surfaces,
        key=lambda row: (
            row["best_frequency"] is None,
            -(row["best_frequency"] or 0.0),
            row["earliest_age_of_acquisition"] is None,
            row["earliest_age_of_acquisition"] or 999.0,
            -row["max_degree_score"],
            row["lemma"],
        ),
    )


def suspicion_reasons(row: dict[str, Any], adjacency: dict[str, set[str]]) -> list[str]:
    reasons: list[str] = []
    lemma = str(row["lemma"])
    gloss = str(row["gloss"]).lower()
    if "_" in lemma:
        reasons.append("multiword")
    if row["frequency"] is None:
        reasons.append("missing_frequency")
    if row["age_of_acquisition"] is None:
        reasons.append("missing_age_of_acquisition")
    if row["concreteness"] is None:
        reasons.append("missing_concreteness")
    if row["node_id"] in adjacency.get(str(row["node_id"]), set()):
        reasons.append("self_loop")
    if any(marker in gloss for marker in ("genus", "family", "taxonomic", "city", "province")):
        reasons.append("domain_or_named_entity_like")
    return reasons


def ranked_suspicious_seed_rows(rows: list[dict[str, Any]], adjacency: dict[str, set[str]], limit: int) -> list[dict[str, Any]]:
    suspicious: list[dict[str, Any]] = []
    for row in rows:
        if not row["is_seed"]:
            continue
        reasons = suspicion_reasons(row, adjacency)
        if reasons:
            payload = dict(row)
            payload["suspicion_reasons"] = reasons
            suspicious.append(payload)
    return sorted(
        suspicious,
        key=lambda row: (
            -len(row["suspicion_reasons"]),
            -int(row["degree_score"]),
            str(row["node_id"]),
        ),
    )[:limit]


def ranked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            int(row["layer"]),
            row["frequency"] is None,
            -(row["frequency"] or 0.0),
            row["age_of_acquisition"] is None,
            row["age_of_acquisition"] or 999.0,
            -int(row["degree_score"]),
            str(row["node_id"]),
        ),
    )


def rows_for_layer(rows: list[dict[str, Any]], layer: int, limit: int) -> list[dict[str, Any]]:
    layer_rows = [row for row in rows if row["layer"] == layer]
    return ranked_rows(layer_rows)[:limit]


def coverage_for(rows: list[dict[str, Any]], field: str) -> dict[str, float | int]:
    count = sum(1 for row in rows if row[field] is not None)
    total = len(rows)
    return {"count": count, "total": total, "fraction": count / total if total else 0.0}


def write_json(
    path: Path,
    inputs: ExportInputs,
    rows: list[dict[str, Any]],
    human_seed_surfaces: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "lexicon_id": inputs.summary.get("lexicon_id"),
            "graph_type": inputs.summary.get("graph_type"),
            "seed_method": inputs.layers.get("seed_method"),
            "seed_exact": inputs.layers.get("seed_exact"),
            "seed_lower_bound": inputs.layers.get("seed_lower_bound"),
            "seed_upper_bound": inputs.layers.get("seed_upper_bound"),
            "candidate_seed_id": inputs.layers.get("candidate_seed_id"),
            "residual_cyclic_scc_count": inputs.layers.get("residual_cyclic_scc_count"),
            "kernel_node_count": len(rows),
            "strict_graph_seed_count": sum(1 for row in rows if row["is_seed"]),
            "human_seed_surface_count": len(human_seed_surfaces),
            "kernel_surface_count": len({row["lemma"] for row in rows}),
            "annotation_sources": [str(path) for path in inputs.annotation_paths],
        },
        "human_seed_surfaces": human_seed_surfaces,
        "kernel_rows": rows,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def render_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = []
        for field in fields:
            value = row.get(field)
            if isinstance(value, list):
                text = ", ".join(str(item) for item in value)
            elif value is None:
                text = ""
            else:
                text = str(value)
            values.append(text.replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    path: Path,
    inputs: ExportInputs,
    rows: list[dict[str, Any]],
    human_seed_surfaces: list[dict[str, Any]],
    adjacency: dict[str, set[str]],
    top: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    seed_rows = [row for row in rows if row["is_seed"]]
    layer_counts = Counter(int(row["layer"]) for row in rows)
    deepest_layer = max(layer_counts)
    suspicious = ranked_suspicious_seed_rows(rows, adjacency, top)
    component_counts = Counter(str(row["component"]) for row in rows)

    lines = [
        "# Up-Goer Five Kernel Export",
        "",
        "This is the current executable Up-Goer candidate: the strict graph seed is the set of graph nodes removed to make the OEWN definition kernel acyclic; the human seed surface is that seed collapsed from `lemma::pos` nodes to lemmas.",
        "",
        "## Summary",
        "",
        f"- Candidate seed id: `{inputs.layers.get('candidate_seed_id')}`",
        f"- Seed method: `{inputs.layers.get('seed_method')}`",
        f"- Seed exact: `{inputs.layers.get('seed_exact')}`",
        f"- Strict graph seed nodes: `{len(seed_rows)}`",
        f"- Human seed surfaces: `{len(human_seed_surfaces)}`",
        f"- Kernel nodes exported: `{len(rows)}`",
        f"- Kernel surfaces exported: `{len({row['lemma'] for row in rows})}`",
        f"- Residual cyclic SCCs after seed removal: `{inputs.layers.get('residual_cyclic_scc_count')}`",
        f"- Deepest definitional layer: `{deepest_layer}`",
        f"- Components: `{dict(sorted(component_counts.items()))}`",
        f"- Annotation sources: `{[str(path) for path in inputs.annotation_paths]}`",
        "",
        "## Annotation Coverage",
        "",
    ]
    coverage_rows = []
    for field in ("frequency", "age_of_acquisition", "concreteness"):
        seed_coverage = coverage_for(seed_rows, field)
        kernel_coverage = coverage_for(rows, field)
        coverage_rows.append(
            {
                "field": field,
                "seed_count": seed_coverage["count"],
                "seed_total": seed_coverage["total"],
                "seed_fraction": round(float(seed_coverage["fraction"]), 4),
                "kernel_count": kernel_coverage["count"],
                "kernel_total": kernel_coverage["total"],
                "kernel_fraction": round(float(kernel_coverage["fraction"]), 4),
            }
        )
    lines.extend(render_table(coverage_rows, ["field", "seed_count", "seed_total", "seed_fraction", "kernel_count", "kernel_total", "kernel_fraction"]))
    lines.extend(["", "## Layer Histogram", ""])
    histogram_rows = [{"layer": layer, "count": count} for layer, count in sorted(layer_counts.items())]
    lines.extend(render_table(histogram_rows, ["layer", "count"]))

    lines.extend(["", "## Top Human Seed Surfaces", ""])
    lines.extend(
        render_table(
            human_seed_surfaces[:top],
            ["lemma", "surface_word", "seed_node_count", "parts_of_speech", "best_frequency", "earliest_age_of_acquisition", "max_degree_score"],
        )
    )

    for title, layer in (("Layer 1 Samples", 1), ("Layer 2 Samples", 2), ("Deepest Layer Samples", deepest_layer)):
        lines.extend(["", f"## {title}", ""])
        lines.extend(
            render_table(
                rows_for_layer(rows, layer, min(top, 25)),
                ["node_id", "surface_word", "pos", "degree_score", "frequency", "age_of_acquisition", "gloss"],
            )
        )

    lines.extend(["", "## Suspicious Seed Senses", ""])
    lines.extend(
        render_table(
            suspicious,
            ["node_id", "surface_word", "pos", "degree_score", "suspicion_reasons", "gloss"],
        )
    )

    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def export_kernel_wordlist(
    *,
    lexicon: str,
    summary_path: Path,
    layers_path: Path,
    annotation_paths: list[Path],
    wordlist_path: Path,
    json_path: Path,
    report_path: Path,
    seed_surfaces_path: Path,
    seed_words_path: Path,
    top: int,
) -> None:
    inputs = load_inputs(summary_path, layers_path, annotation_paths)
    validate_inputs(inputs)
    build = build_paper_wordnet_graph(lexicon)
    annotations = load_annotation_csvs(inputs.annotation_paths)
    layer_by_node = {str(node): int(layer) for node, layer in inputs.layers["layer_by_node"].items()}
    missing_nodes = set(layer_by_node) - build.nodes
    if missing_nodes:
        sample = ", ".join(sorted(missing_nodes)[:10])
        raise ValueError(f"Layer file contains nodes absent from rebuilt graph, sample: {sample}")

    membership = derive_membership(layer_by_node, build.adjacency, str(inputs.summary.get("core_policy", "source-union")))
    indegree, outdegree = compute_degrees(build.adjacency)
    rows = [
        row_for_node(
            node=node,
            membership=membership,
            labels=build.labels,
            seed_method=str(inputs.layers.get("seed_method")),
            candidate_seed_id=str(inputs.layers.get("candidate_seed_id")),
            indegree=indegree,
            outdegree=outdegree,
            annotations=annotations,
        )
        for node in sorted(membership.kernel_nodes)
    ]
    rows = ranked_rows(rows)
    seed_count = sum(1 for row in rows if row["is_seed"])
    if seed_count != int(inputs.summary.get("seed_node_count", seed_count)):
        raise ValueError(f"Seed count mismatch: exported {seed_count}, summary {inputs.summary.get('seed_node_count')}")
    if len(rows) != int(inputs.summary.get("kernel_node_count", len(rows))):
        raise ValueError(f"Kernel count mismatch: exported {len(rows)}, summary {inputs.summary.get('kernel_node_count')}")

    human_seed_surfaces = collapse_seed_surfaces(rows)
    write_csv(wordlist_path, rows)
    write_seed_surfaces_csv(seed_surfaces_path, human_seed_surfaces)
    write_seed_words(seed_words_path, human_seed_surfaces)
    write_json(json_path, inputs, rows, human_seed_surfaces)
    write_report(report_path, inputs, rows, human_seed_surfaces, build.adjacency, top)

    seed_nodes = {row["node_id"] for row in rows if row["is_seed"]}
    seed_coverage = annotation_coverage(seed_nodes, annotations)
    print(
        json.dumps(
            {
                "wordlist": str(wordlist_path),
                "seed_surfaces": str(seed_surfaces_path),
                "seed_words": str(seed_words_path),
                "json": str(json_path),
                "report": str(report_path),
                "kernel_node_count": len(rows),
                "strict_graph_seed_count": seed_count,
                "human_seed_surface_count": len(human_seed_surfaces),
                "seed_annotation_coverage": seed_coverage,
            },
            indent=2,
            sort_keys=True,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export the current OEWN Up-Goer/kernel wordlist.")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument("--summary", type=Path, default=Path("reports/oewn-paper-wordnet-kernel-summary.json"))
    parser.add_argument("--layers", type=Path, default=Path("reports/oewn-paper-wordnet-layers.json"))
    parser.add_argument("--annotations", type=Path, nargs="*", default=[])
    parser.add_argument("--wordlist", type=Path, default=Path("data/english_kernel_wordlist.csv"))
    parser.add_argument("--seed-surfaces", type=Path, default=Path("data/english_seed_surfaces.csv"))
    parser.add_argument("--seed-words", type=Path, default=Path("data/up_goer_seed_words.txt"))
    parser.add_argument("--json", type=Path, default=Path("data/english_kernel_wordlist.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/up-goer-five-kernel.md"))
    parser.add_argument("--top", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    export_kernel_wordlist(
        lexicon=args.lexicon,
        summary_path=args.summary,
        layers_path=args.layers,
        annotation_paths=list(args.annotations),
        wordlist_path=args.wordlist,
        json_path=args.json,
        report_path=args.report,
        seed_surfaces_path=args.seed_surfaces,
        seed_words_path=args.seed_words,
        top=args.top,
    )


if __name__ == "__main__":
    main()
