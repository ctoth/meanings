from __future__ import annotations

import argparse
from pathlib import Path

from meanings.wordnet_pipeline import run_analysis


def default_report_path(graph_type: str) -> str:
    if graph_type == "lemma":
        return "reports/oewn-lemma-kernel-report.md"
    if graph_type == "paper-wordnet":
        return "reports/oewn-paper-wordnet-kernel-report.md"
    return "reports/oewn-synset-kernel-report.md"


def default_json_path(graph_type: str) -> str:
    if graph_type == "lemma":
        return "reports/oewn-lemma-kernel-summary.json"
    if graph_type == "paper-wordnet":
        return "reports/oewn-paper-wordnet-kernel-summary.json"
    return "reports/oewn-synset-kernel-summary.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dictionary kernel tooling")
    parser.add_argument("--lexicon", default="oewn:2024", help="WordNet lexicon id to analyze")
    parser.add_argument(
        "--graph-type",
        choices=("lemma", "sense", "paper-wordnet"),
        default="sense",
        help="Graph surface to analyze",
    )
    parser.add_argument(
        "--seed-method",
        choices=("bounded-scc", "exact-small-greedy", "exact-cutting"),
        default="bounded-scc",
        help="Candidate seed extraction method",
    )
    parser.add_argument(
        "--core-policy",
        choices=("source-union", "largest-scc"),
        default="source-union",
        help="How to define Core inside the Kernel",
    )
    parser.add_argument(
        "--annotations",
        nargs="*",
        default=[],
        help="Optional psycholinguistic annotation CSV files",
    )
    parser.add_argument("--export-layers", help="Optional JSON node-to-layer export path")
    parser.add_argument("--report", help="Markdown report output path")
    parser.add_argument("--json", help="JSON summary output path")
    parser.add_argument("--top", type=int, default=25, help="How many top nodes to list in reports")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report_path = Path(args.report or default_report_path(args.graph_type))
    json_path = Path(args.json or default_json_path(args.graph_type))
    run_analysis(
        lexicon_id=args.lexicon,
        report_path=report_path,
        json_path=json_path,
        top_n=args.top,
        graph_type=args.graph_type,
        seed_method=args.seed_method,
        core_policy=args.core_policy,
        annotation_paths=[Path(path) for path in args.annotations],
        export_layers_path=Path(args.export_layers) if args.export_layers else None,
    )


if __name__ == "__main__":
    main()
