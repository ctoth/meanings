from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from meanings.graph_analysis import induced_subgraph, strongly_connected_components
from meanings.wordnet_pipeline import build_paper_wordnet_graph, build_synset_graph


def cyclic(component: set[str], adjacency: dict[str, set[str]]) -> bool:
    if len(component) > 1:
        return True
    node = next(iter(component))
    return node in adjacency.get(node, set())


def count_two_cycles(nodes: set[str], adjacency: dict[str, set[str]]) -> int:
    count = 0
    for source in nodes:
        for target in adjacency.get(source, set()):
            if source < target and source in adjacency.get(target, set()):
                count += 1
    return count


def count_three_cycles(nodes: set[str], adjacency: dict[str, set[str]], limit: int = 100000) -> tuple[int, bool]:
    cycles: set[tuple[str, str, str]] = set()
    for a in nodes:
        for b in adjacency.get(a, set()):
            if b not in nodes:
                continue
            for c in adjacency.get(b, set()):
                if c not in nodes or c == a or c == b:
                    continue
                if a in adjacency.get(c, set()):
                    cycles.add(tuple(sorted((a, b, c))))
                    if len(cycles) >= limit:
                        return len(cycles), True
    return len(cycles), False


def build_graph(graph_type: str, lexicon: str):
    if graph_type == "paper-wordnet":
        return build_paper_wordnet_graph(lexicon)
    if graph_type == "sense":
        build = build_synset_graph(lexicon)
        return build
    raise ValueError(f"Unsupported loop graph type: {graph_type}")


def write_loop_report(graph_type: str, lexicon: str, output: Path) -> None:
    build = build_graph(graph_type, lexicon)
    components = strongly_connected_components(build.nodes, build.adjacency)
    cyclic_components = [component for component in components if cyclic(component, build.adjacency)]
    size_histogram = Counter(len(component) for component in cyclic_components)
    largest = sorted((len(component) for component in cyclic_components), reverse=True)[:20]
    kernel_graph = induced_subgraph(build.nodes, build.adjacency)
    two_cycles = count_two_cycles(build.nodes, kernel_graph)
    three_cycles, three_truncated = count_three_cycles(build.nodes, kernel_graph)

    lines = [
        f"# Loop Ecology: {graph_type}",
        "",
        f"- Lexicon: `{lexicon}`",
        f"- Nodes: `{len(build.nodes)}`",
        f"- Edges: `{sum(len(targets) for targets in build.adjacency.values())}`",
        f"- SCC count: `{len(components)}`",
        f"- Cyclic SCC count: `{len(cyclic_components)}`",
        f"- 2-cycles: `{two_cycles}`",
        f"- 3-cycles: `{three_cycles}`" + (" (truncated)" if three_truncated else ""),
        "",
        "## Cyclic SCC Size Histogram",
        "",
    ]
    for size, count in sorted(size_histogram.items()):
        lines.append(f"- Size `{size}`: `{count}` SCCs")

    lines.extend(["", "## Largest Cyclic SCCs", ""])
    for index, size in enumerate(largest, start=1):
        lines.append(f"- SCC `{index}`: `{size}` nodes")

    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "- These loops are reported as structure, not discarded as errors.",
            "- Use this report before interpreting any seed as a semantic primitive set.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze dictionary loop ecology")
    parser.add_argument("--graph-type", choices=("paper-wordnet", "sense"), default="paper-wordnet")
    parser.add_argument("--lexicon", default="oewn:2024")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    write_loop_report(args.graph_type, args.lexicon, args.output)


if __name__ == "__main__":
    main()

