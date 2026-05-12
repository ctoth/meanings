from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from meanings.graph_analysis import (
    Adjacency,
    compute_kernel,
    induced_subgraph,
    reverse_adjacency,
    strongly_connected_components,
)
from meanings.wordnet_pipeline import build_paper_wordnet_graph, build_synset_graph


@dataclass(slots=True)
class CondensationDiagnostics:
    node_count: int
    edge_count: int
    scc_count: int
    source_scc_count: int
    source_node_count: int
    sink_scc_count: int
    sink_node_count: int
    largest_scc_size: int
    largest_scc_indegree: int
    largest_scc_outdegree: int
    largest_scc_is_source: bool
    largest_scc_is_sink: bool
    top_source_scc_sizes: list[int]
    top_sink_scc_sizes: list[int]
    top_scc_sizes: list[int]


def edge_count(adjacency: Adjacency) -> int:
    return sum(len(targets) for targets in adjacency.values())


def condensation_diagnostics(nodes: set[str], adjacency: Adjacency) -> CondensationDiagnostics:
    components = strongly_connected_components(nodes, adjacency)
    index_of: dict[str, int] = {}
    for index, component in enumerate(components):
        for node in component:
            index_of[node] = index

    indegrees = [0] * len(components)
    outdegrees = [0] * len(components)
    for source, targets in adjacency.items():
        source_index = index_of[source]
        for target in targets:
            target_index = index_of[target]
            if source_index == target_index:
                continue
            outdegrees[source_index] += 1
            indegrees[target_index] += 1

    sizes = [len(component) for component in components]
    source_indices = [index for index, indegree in enumerate(indegrees) if indegree == 0]
    sink_indices = [index for index, outdegree in enumerate(outdegrees) if outdegree == 0]
    largest_index = max(range(len(components)), key=lambda index: sizes[index]) if components else -1

    return CondensationDiagnostics(
        node_count=len(nodes),
        edge_count=edge_count(adjacency),
        scc_count=len(components),
        source_scc_count=len(source_indices),
        source_node_count=sum(sizes[index] for index in source_indices),
        sink_scc_count=len(sink_indices),
        sink_node_count=sum(sizes[index] for index in sink_indices),
        largest_scc_size=sizes[largest_index] if largest_index >= 0 else 0,
        largest_scc_indegree=indegrees[largest_index] if largest_index >= 0 else 0,
        largest_scc_outdegree=outdegrees[largest_index] if largest_index >= 0 else 0,
        largest_scc_is_source=largest_index in source_indices,
        largest_scc_is_sink=largest_index in sink_indices,
        top_source_scc_sizes=sorted((sizes[index] for index in source_indices), reverse=True)[:10],
        top_sink_scc_sizes=sorted((sizes[index] for index in sink_indices), reverse=True)[:10],
        top_scc_sizes=sorted(sizes, reverse=True)[:10],
    )


def asdict(diagnostics: CondensationDiagnostics) -> dict[str, Any]:
    return {
        field: getattr(diagnostics, field)
        for field in CondensationDiagnostics.__dataclass_fields__
    }


def build_graph(graph_type: str, lexicon: str):
    if graph_type == "paper-wordnet":
        return build_paper_wordnet_graph(lexicon)
    if graph_type == "sense":
        return build_synset_graph(lexicon)
    raise ValueError(f"Unsupported graph type: {graph_type}")


def diagnose(graph_type: str, lexicon: str) -> dict[str, Any]:
    build = build_graph(graph_type, lexicon)
    kernel_nodes = compute_kernel(build.nodes, build.adjacency)
    kernel_graph = induced_subgraph(kernel_nodes, build.adjacency)

    reversed_graph = reverse_adjacency(build.nodes, build.adjacency)
    reversed_kernel_nodes = compute_kernel(build.nodes, reversed_graph)
    reversed_kernel_graph = induced_subgraph(reversed_kernel_nodes, reversed_graph)

    reversed_kernel_same_nodes = reverse_adjacency(kernel_nodes, kernel_graph)

    return {
        "graph_type": graph_type,
        "lexicon": lexicon,
        "paper_claims": {
            "edge_orientation": "defining word -> defined word",
            "wordnet_word_meanings": 132477,
            "wordnet_kernel": 9802,
            "wordnet_core": 6392,
            "wordnet_satellites": 3410,
            "core_definition": "largest/source SCC inside Kernel after preprocessing",
        },
        "full_graph": {
            "node_count": len(build.nodes),
            "edge_count": edge_count(build.adjacency),
        },
        "kernel_original_orientation": asdict(condensation_diagnostics(kernel_nodes, kernel_graph)),
        "same_kernel_reversed_orientation": asdict(
            condensation_diagnostics(kernel_nodes, reversed_kernel_same_nodes)
        ),
        "reversed_full_graph_kernel": asdict(
            condensation_diagnostics(reversed_kernel_nodes, reversed_kernel_graph)
        ),
    }


def render_markdown(payloads: list[dict[str, Any]], output: Path) -> None:
    lines = [
        "# Core Mismatch Diagnostics",
        "",
        "## Paper Target",
        "",
        "- Edges point from defining word to defined word.",
        "- WordNet reference from Vincent-Lamarre: `132,477` word meanings, Kernel `9,802`, Core `6,392`, Satellites `3,410`.",
        "- Core should be the largest/source SCC inside the Kernel after the paper preprocessing.",
        "",
    ]

    for payload in payloads:
        lines.extend(
            [
                f"## {payload['graph_type']}",
                "",
                f"- Full nodes: `{payload['full_graph']['node_count']}`",
                f"- Full edges: `{payload['full_graph']['edge_count']}`",
                "",
            ]
        )
        for title, key in (
            ("Original Orientation Kernel", "kernel_original_orientation"),
            ("Same Kernel, Reversed Orientation", "same_kernel_reversed_orientation"),
            ("Reversed Full Graph Kernel", "reversed_full_graph_kernel"),
        ):
            stats = payload[key]
            lines.extend(
                [
                    f"### {title}",
                    "",
                    f"- Kernel nodes: `{stats['node_count']}`",
                    f"- Kernel edges: `{stats['edge_count']}`",
                    f"- SCC count: `{stats['scc_count']}`",
                    f"- Source SCCs: `{stats['source_scc_count']}` / `{stats['source_node_count']}` nodes",
                    f"- Sink SCCs: `{stats['sink_scc_count']}` / `{stats['sink_node_count']}` nodes",
                    f"- Largest SCC: `{stats['largest_scc_size']}` nodes",
                    f"- Largest SCC indegree/outdegree: `{stats['largest_scc_indegree']}` / `{stats['largest_scc_outdegree']}`",
                    f"- Largest SCC is source: `{stats['largest_scc_is_source']}`",
                    f"- Largest SCC is sink: `{stats['largest_scc_is_sink']}`",
                    f"- Top source SCC sizes: `{stats['top_source_scc_sizes']}`",
                    f"- Top sink SCC sizes: `{stats['top_sink_scc_sizes']}`",
                    f"- Top SCC sizes: `{stats['top_scc_sizes']}`",
                    "",
                ]
            )

    lines.extend(
        [
            "## Initial Verdict",
            "",
            "- If the largest SCC is source only after reversing the same kernel, the mismatch is primarily edge-orientation terminology.",
            "- If the largest SCC is neither source nor sink under the paper orientation, the mismatch is in preprocessing or sense/lemma mapping.",
            "- If the reversed full graph kernel size changes radically, reversing edges is not a valid reproduction of the paper pipeline.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose Core/Satellite mismatches")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument(
        "--graph-type",
        action="append",
        choices=("paper-wordnet", "sense"),
        default=[],
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    graph_types = args.graph_type or ["paper-wordnet"]
    payloads = [diagnose(graph_type, args.lexicon) for graph_type in graph_types]
    render_markdown(payloads, args.output)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payloads, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

