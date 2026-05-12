from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REFERENCE_WORDNET = {
    "label": "Vincent-Lamarre WordNet",
    "node_count": 132477,
    "kernel_node_count": 9802,
    "kernel_fraction": 0.12,
    "core_node_count": 6392,
    "satellite_node_count": 3410,
    "seed_node_count": 1094,
}


METRICS = (
    "node_count",
    "edge_count",
    "kernel_node_count",
    "kernel_fraction",
    "kernel_scc_count",
    "source_scc_count",
    "core_node_count",
    "satellite_node_count",
    "seed_node_count",
    "seed_fraction_total",
    "seed_fraction_kernel",
    "residual_cyclic_scc_count",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_comparison(left_path: Path, right_path: Path, output_path: Path) -> None:
    left = load_json(left_path)
    right = load_json(right_path)
    left_label = left.get("graph_type", left_path.stem)
    right_label = right.get("graph_type", right_path.stem)

    lines = [
        "# OEWN Kernel Model Comparison",
        "",
        f"- Left: `{left_label}` from `{left_path}`",
        f"- Right: `{right_label}` from `{right_path}`",
        "- Reference: `Vincent-Lamarre WordNet` values from the paper notes",
        "",
        "| Metric | Paper Reference | Left | Right |",
        "|---|---:|---:|---:|",
    ]
    for metric in METRICS:
        lines.append(
            f"| `{metric}` | {fmt(REFERENCE_WORDNET.get(metric))} | {fmt(left.get(metric))} | {fmt(right.get(metric))} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The paper reference is not expected to match exactly because OEWN 2024 and our builders differ from the WordNet resource and preprocessing used in Vincent-Lamarre.",
            "- Large deviations are interpretation prompts, not automatic failures.",
            "- The paper-faithful baseline is the measuring stick; the synset graph is experimental.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare kernel summary JSON files")
    parser.add_argument("--left", required=True, type=Path)
    parser.add_argument("--right", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    write_comparison(args.left, args.right, args.output)


if __name__ == "__main__":
    main()

