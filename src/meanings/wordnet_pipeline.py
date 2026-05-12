from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import wn

from meanings.annotations import AnnotationStore, annotation_coverage, component_annotation_summary, load_annotation_csvs
from meanings.graph_analysis import Adjacency, KernelAnalysis, analyze_kernel
from meanings.lexical_graph import LexicalGraphBuild
from meanings.normalize import content_tokens, extract_lemma_candidates, normalize_lemma


@dataclass(slots=True)
class LemmaGraphBuild:
    lexicon_id: str
    nodes: set[str]
    adjacency: Adjacency
    sense_count_by_lemma: dict[str, int]
    definition_count_by_lemma: dict[str, int]


@dataclass(slots=True)
class SynsetGraphBuild:
    lexicon_id: str
    nodes: set[str]
    adjacency: Adjacency
    labels: dict[str, str]
    pos_by_node: dict[str, str]
    resolution_stats: dict[str, int]


def load_lexicon(lexicon_id: str) -> wn.Wordnet:
    wn.download(lexicon_id)
    return wn.Wordnet(lexicon_id)


def truncate_text(text: str, limit: int = 72) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def synset_label(synset: wn.Synset) -> str:
    lemmas = [normalize_lemma(word.lemma()) for word in synset.words()]
    head = ", ".join(lemmas[:2]) if lemmas else synset.id
    if len(lemmas) > 2:
        head += ", ..."
    return f"{head} [{synset.pos}] :: {truncate_text(synset.definition() or synset.id)}"


def synset_signature(synset: wn.Synset) -> set[str]:
    signature = set(content_tokens(synset.definition() or ""))
    for word in synset.words():
        signature.update(normalize_lemma(word.lemma()).split("_"))
    return signature


def choose_best_candidate(
    candidate_nodes: set[str],
    context_tokens: set[str],
    signatures: dict[str, set[str]],
    blocked_tokens: set[str],
) -> str | None:
    filtered_context = context_tokens - blocked_tokens
    best_node: str | None = None
    best_score: tuple[int, int, str] | None = None
    second_best: tuple[int, int, str] | None = None
    for node in candidate_nodes:
        candidate_signature = signatures.get(node, set()) - blocked_tokens
        overlap = len(filtered_context & candidate_signature)
        signature_size = len(signatures.get(node, set()))
        score = (overlap, -signature_size, node)
        if best_score is None or score > best_score:
            second_best = best_score
            best_node = node
            best_score = score
        elif second_best is None or score > second_best:
            second_best = score
    if best_score is None or best_score[0] == 0:
        return None
    if second_best is not None and best_score[0] <= second_best[0]:
        return None
    return best_node


def top_degree_nodes(
    adjacency: Adjacency,
    limit: int,
    labels: dict[str, str] | None = None,
) -> dict[str, list[tuple[str, int]]]:
    indegree = {node: 0 for node in adjacency}
    for targets in adjacency.values():
        for target in targets:
            indegree[target] += 1
    outdegree = {node: len(targets) for node, targets in adjacency.items()}
    top_out = sorted(outdegree.items(), key=lambda item: (-item[1], item[0]))[:limit]
    top_in = sorted(indegree.items(), key=lambda item: (-item[1], item[0]))[:limit]
    if labels is None:
        return {"outdegree": top_out, "indegree": top_in}
    return {
        "outdegree": [(labels.get(node, node), degree) for node, degree in top_out],
        "indegree": [(labels.get(node, node), degree) for node, degree in top_in],
    }


def top_seed_nodes(
    seed_nodes: list[str],
    adjacency: Adjacency,
    limit: int,
    labels: dict[str, str] | None = None,
) -> list[tuple[str, int]]:
    indegree = {node: 0 for node in adjacency}
    for targets in adjacency.values():
        for target in targets:
            indegree[target] += 1
    ranked = sorted(
        ((node, indegree.get(node, 0) + len(adjacency.get(node, set()))) for node in seed_nodes),
        key=lambda item: (-item[1], item[0]),
    )[:limit]
    if labels is None:
        return ranked
    return [(labels.get(node, node), score) for node, score in ranked]


def build_lemma_graph(lexicon_id: str = "oewn:2024") -> LemmaGraphBuild:
    lexicon = load_lexicon(lexicon_id)
    nodes = {normalize_lemma(word.lemma()) for word in lexicon.words()}
    adjacency: Adjacency = {node: set() for node in nodes}
    sense_count_by_lemma: dict[str, int] = {}
    definition_count_by_lemma: dict[str, int] = {}

    for word in lexicon.words():
        lemma = normalize_lemma(word.lemma())
        synsets = list(word.synsets())
        definitions = {synset.definition() for synset in synsets if synset.definition()}
        sense_count_by_lemma[lemma] = sense_count_by_lemma.get(lemma, 0) + len(synsets)
        definition_count_by_lemma[lemma] = definition_count_by_lemma.get(lemma, 0) + len(definitions)
        for definition in definitions:
            for source in extract_lemma_candidates(definition, nodes):
                adjacency[source].add(lemma)

    return LemmaGraphBuild(
        lexicon_id=lexicon_id,
        nodes=nodes,
        adjacency=adjacency,
        sense_count_by_lemma=sense_count_by_lemma,
        definition_count_by_lemma=definition_count_by_lemma,
    )


def build_synset_graph(lexicon_id: str = "oewn:2024") -> SynsetGraphBuild:
    lexicon = load_lexicon(lexicon_id)
    nodes: set[str] = set()
    adjacency: Adjacency = {}
    labels: dict[str, str] = {}
    pos_by_node: dict[str, str] = {}
    definition_by_node: dict[str, str] = {}
    signature_by_node: dict[str, set[str]] = {}
    context_by_node: dict[str, set[str]] = {}
    lemma_index: dict[str, set[str]] = {}
    lemma_pos_index: dict[tuple[str, str], set[str]] = {}

    for synset in lexicon.synsets():
        definition = synset.definition()
        if not definition:
            continue
        node = synset.id
        nodes.add(node)
        adjacency[node] = set()
        labels[node] = synset_label(synset)
        pos_by_node[node] = synset.pos
        definition_by_node[node] = definition
        signature_by_node[node] = synset_signature(synset)
        context_by_node[node] = set(content_tokens(definition))
        for word in synset.words():
            lemma = normalize_lemma(word.lemma())
            lemma_index.setdefault(lemma, set()).add(node)
            lemma_pos_index.setdefault((lemma, synset.pos), set()).add(node)

    resolution_stats = {
        "candidate_matches": 0,
        "resolved_same_pos_unique": 0,
        "resolved_global_unique": 0,
        "resolved_same_pos_overlap": 0,
        "resolved_global_overlap": 0,
        "ambiguous_skipped": 0,
        "self_only_skipped": 0,
        "unresolved_skipped": 0,
    }

    lemma_set = set(lemma_index)
    for target_node, definition in definition_by_node.items():
        target_pos = pos_by_node[target_node]
        target_context = context_by_node[target_node]
        for candidate in extract_lemma_candidates(definition, lemma_set):
            resolution_stats["candidate_matches"] += 1
            blocked_tokens = set(candidate.split("_"))
            same_pos_choices = lemma_pos_index.get((candidate, target_pos), set()) - {target_node}
            if len(same_pos_choices) == 1:
                source_node = next(iter(same_pos_choices))
                adjacency[source_node].add(target_node)
                resolution_stats["resolved_same_pos_unique"] += 1
                continue
            if len(same_pos_choices) > 1:
                source_node = choose_best_candidate(
                    same_pos_choices,
                    target_context,
                    signature_by_node,
                    blocked_tokens,
                )
                if source_node is not None:
                    adjacency[source_node].add(target_node)
                    resolution_stats["resolved_same_pos_overlap"] += 1
                    continue
                resolution_stats["ambiguous_skipped"] += 1
                continue

            all_choices = lemma_index.get(candidate, set()) - {target_node}
            if len(all_choices) == 1:
                source_node = next(iter(all_choices))
                adjacency[source_node].add(target_node)
                resolution_stats["resolved_global_unique"] += 1
            elif all_choices:
                source_node = choose_best_candidate(
                    all_choices,
                    target_context,
                    signature_by_node,
                    blocked_tokens,
                )
                if source_node is not None:
                    adjacency[source_node].add(target_node)
                    resolution_stats["resolved_global_overlap"] += 1
                else:
                    resolution_stats["ambiguous_skipped"] += 1
            else:
                resolution_stats["self_only_skipped"] += 1

    return SynsetGraphBuild(
        lexicon_id=lexicon_id,
        nodes=nodes,
        adjacency=adjacency,
        labels=labels,
        pos_by_node=pos_by_node,
        resolution_stats=resolution_stats,
    )


def node_key(lemma: str, pos: str) -> str:
    return f"{lemma}::{pos}"


def build_paper_wordnet_graph(lexicon_id: str = "oewn:2024") -> LexicalGraphBuild:
    lexicon = load_lexicon(lexicon_id)
    representative_definition: dict[str, str] = {}
    labels: dict[str, str] = {}
    pos_by_node: dict[str, str] = {}
    lemma_to_nodes: dict[str, set[str]] = {}

    for word in lexicon.words():
        lemma = normalize_lemma(word.lemma())
        pos = word.pos
        key = node_key(lemma, pos)
        if key in representative_definition:
            continue
        synset = next((candidate for candidate in word.synsets() if candidate.definition()), None)
        if synset is None:
            continue
        representative_definition[key] = synset.definition()
        labels[key] = f"{lemma} [{pos}] :: {truncate_text(synset.definition())}"
        pos_by_node[key] = pos
        lemma_to_nodes.setdefault(lemma, set()).add(key)

    nodes = set(representative_definition)
    adjacency: Adjacency = {node: set() for node in nodes}
    lemma_set = set(lemma_to_nodes)
    stats = {
        "definition_count": len(representative_definition),
        "candidate_matches": 0,
        "resolved_same_pos": 0,
        "resolved_unambiguous_pos": 0,
        "ambiguous_skipped": 0,
        "missing_skipped": 0,
    }

    for target_node, definition in representative_definition.items():
        target_pos = pos_by_node[target_node]
        for candidate in extract_lemma_candidates(definition, lemma_set):
            stats["candidate_matches"] += 1
            same_pos = node_key(candidate, target_pos)
            if same_pos in nodes:
                adjacency[same_pos].add(target_node)
                stats["resolved_same_pos"] += 1
                continue
            choices = lemma_to_nodes.get(candidate, set())
            if len(choices) == 1:
                source = next(iter(choices))
                adjacency[source].add(target_node)
                stats["resolved_unambiguous_pos"] += 1
            elif choices:
                stats["ambiguous_skipped"] += 1
            else:
                stats["missing_skipped"] += 1

    return LexicalGraphBuild(
        lexicon_id=lexicon_id,
        graph_type="paper_wordnet",
        nodes=nodes,
        adjacency=adjacency,
        labels=labels,
        pos_by_node=pos_by_node,
        metadata={
            "language": "en",
            "resource_id": "oewn",
            "construction": "lemma_pos_first_representative_synset_content_words",
            "reference": {
                "source": "Vincent-Lamarre 2014 WordNet",
                "node_count": 132477,
                "kernel_node_count": 9802,
                "kernel_fraction": 0.12,
                "core_node_count": 6392,
                "satellite_node_count": 3410,
                "seed_node_count": 1094,
            },
            "resolution_stats": stats,
        },
    )


def render_lemma_markdown_report(
    build: LemmaGraphBuild,
    analysis: KernelAnalysis,
    report_path: Path,
    top_n: int = 25,
) -> None:
    total_nodes = len(build.nodes)
    kernel_size = len(analysis.kernel_nodes)
    seed_size = len(analysis.seed_nodes)
    source_scc_count = len(analysis.source_sccs)
    top_degrees = top_degree_nodes(build.adjacency, top_n)
    top_seeds = top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n)
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]

    lines = [
        "# Open English WordNet Lemma-Kernel Report",
        "",
        f"- Lexicon: `{build.lexicon_id}`",
        "- Graph type: lemma-level proxy over Open English WordNet glosses",
        "- Node policy: collapse all senses and parts of speech into normalized lemmas",
        "- Edge policy: add `defining_lemma -> defined_lemma` when a gloss contains a matched lexicon lemma",
        "- Gloss parsing: longest-match n-gram scan up to width 3 with tightened gloss-glue and taxonomy filtering",
        "",
        "## Summary",
        "",
        f"- Total lemma nodes: `{total_nodes}`",
        f"- Total directed edges: `{analysis.edges}`",
        f"- Kernel nodes: `{kernel_size}` ({kernel_size / total_nodes:.2%})",
        f"- Kernel SCC count: `{len(analysis.kernel_sccs)}`",
        f"- Source SCCs inside kernel: `{source_scc_count}`",
        f"- Core size (union of source SCCs): `{len(analysis.core_nodes)}`",
        f"- Satellite size (kernel minus source-SCC Core): `{len(analysis.satellite_nodes)}`",
        f"- Fast cycle-hitting seed size: `{seed_size}` ({seed_size / total_nodes:.2%}; {seed_size / max(kernel_size, 1):.2%} of kernel)",
        f"- Residual cyclic SCCs after bounded heuristic: `{analysis.residual_cyclic_scc_count}`",
        "",
        "## Largest Kernel SCCs",
        "",
    ]
    for index, size in enumerate(largest_sccs, start=1):
        lines.append(f"- SCC `{index}`: `{size}` nodes")

    lines.extend(["", "## Layer Histogram", ""])
    if analysis.layer_histogram:
        for layer, count in analysis.layer_histogram.items():
            lines.append(f"- Layer `{layer}`: `{count}` nodes")
    else:
        lines.append("- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.")

    lines.extend(["", "## Top Fast Seed Candidates", ""])
    for lemma, score in top_seeds:
        lines.append(f"- `{lemma}` (degree score `{score}`)")

    lines.extend(["", "## Highest Outdegree Lemmas", ""])
    for lemma, degree in top_degrees["outdegree"]:
        lines.append(f"- `{lemma}`: `{degree}`")

    lines.extend(["", "## Highest Indegree Lemmas", ""])
    for lemma, degree in top_degrees["indegree"]:
        lines.append(f"- `{lemma}`: `{degree}`")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- This is a real lexicon but still a first-pass proxy, not the final sense-disambiguated graph from the papers.",
            "- Polysemy is collapsed at the lemma level, so cycles and kernel sizes are only approximations to the meaning-level structures described by `Massé`, `Picard`, and `Vincent-Lamarre`.",
            "- The reported seed is a named candidate method; it is only an exact `MinSet` when the method and residual-cycle count justify that claim.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_lemma_json_summary(
    build: LemmaGraphBuild,
    analysis: KernelAnalysis,
    json_path: Path,
    top_n: int = 25,
) -> None:
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]
    payload = {
        "lexicon_id": build.lexicon_id,
        "graph_type": "lemma_level_proxy",
        "node_count": len(build.nodes),
        "edge_count": analysis.edges,
        "kernel_node_count": len(analysis.kernel_nodes),
        "kernel_fraction": len(analysis.kernel_nodes) / len(build.nodes),
        "kernel_scc_count": len(analysis.kernel_sccs),
        "source_scc_count": len(analysis.source_sccs),
        "core_node_count": len(analysis.core_nodes),
        "satellite_node_count": len(analysis.satellite_nodes),
        "seed_node_count": len(analysis.seed_nodes),
        "seed_fraction_total": len(analysis.seed_nodes) / len(build.nodes),
        "seed_fraction_kernel": len(analysis.seed_nodes) / max(len(analysis.kernel_nodes), 1),
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "largest_kernel_scc_sizes": largest_sccs,
        "layer_histogram": analysis.layer_histogram,
        "top_seed_nodes": top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n),
        "top_degrees": top_degree_nodes(build.adjacency, top_n),
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def render_paper_wordnet_markdown_report(
    build: LexicalGraphBuild,
    analysis: KernelAnalysis,
    report_path: Path,
    top_n: int = 25,
    annotations: AnnotationStore | None = None,
) -> None:
    total_nodes = len(build.nodes)
    kernel_size = len(analysis.kernel_nodes)
    seed_size = len(analysis.seed_nodes)
    top_degrees = top_degree_nodes(build.adjacency, top_n, labels=build.labels)
    top_seeds = top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n, labels=build.labels)
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]
    reference = build.metadata["reference"]
    resolution_stats = build.metadata["resolution_stats"]

    lines = [
        "# Open English WordNet Paper-Baseline Kernel Report",
        "",
        f"- Lexicon: `{build.lexicon_id}`",
        "- Graph type: paper-faithful WordNet approximation",
        "- Node policy: one normalized `lemma::pos` node with the first available representative synset definition",
        "- Edge policy: content-word `defining_lemma::pos -> defined_lemma::pos`, preferring same POS and otherwise unambiguous POS",
        f"- Seed method: `{analysis.seed_method}`",
        f"- Core policy: `{analysis.core_policy}`",
        "",
        "## Summary",
        "",
        f"- Total lemma/POS nodes: `{total_nodes}`",
        f"- Total directed edges: `{analysis.edges}`",
        f"- Kernel nodes: `{kernel_size}` ({kernel_size / total_nodes:.2%})",
        f"- Kernel SCC count: `{len(analysis.kernel_sccs)}`",
        f"- Source SCCs inside kernel: `{len(analysis.source_sccs)}`",
        f"- Core size (union of source SCCs): `{len(analysis.core_nodes)}`",
        f"- Satellite size (kernel minus source-SCC Core): `{len(analysis.satellite_nodes)}`",
        f"- Candidate seed size: `{seed_size}` ({seed_size / total_nodes:.2%}; {seed_size / max(kernel_size, 1):.2%} of kernel)",
        f"- Residual cyclic SCCs after seed method: `{analysis.residual_cyclic_scc_count}`",
        "",
        "## Vincent-Lamarre WordNet Reference",
        "",
        f"- Word meanings: `{reference['node_count']}`",
        f"- Kernel: `{reference['kernel_node_count']}` ({reference['kernel_fraction']:.0%})",
        f"- Core: `{reference['core_node_count']}`",
        f"- Satellites: `{reference['satellite_node_count']}`",
        f"- MinSet: `{reference['seed_node_count']}`",
        "",
        "## Resolution Stats",
        "",
    ]
    for key, value in resolution_stats.items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Largest Kernel SCCs", ""])
    for index, size in enumerate(largest_sccs, start=1):
        lines.append(f"- SCC `{index}`: `{size}` nodes")

    lines.extend(["", "## Layer Histogram", ""])
    if analysis.layer_histogram:
        for layer, count in analysis.layer_histogram.items():
            lines.append(f"- Layer `{layer}`: `{count}` nodes")
    else:
        lines.append("- Layering skipped because the selected seed did not fully acyclicize the kernel.")

    lines.extend(["", "## Top Candidate Seed Nodes", ""])
    for label, score in top_seeds:
        lines.append(f"- `{label}` (degree score `{score}`)")

    lines.extend(["", "## Highest Outdegree Nodes", ""])
    for label, degree in top_degrees["outdegree"]:
        lines.append(f"- `{label}`: `{degree}`")

    lines.extend(["", "## Highest Indegree Nodes", ""])
    for label, degree in top_degrees["indegree"]:
        lines.append(f"- `{label}`: `{degree}`")

    if annotations is not None:
        coverage = annotation_coverage(build.nodes, annotations)
        lines.extend(["", "## Annotation Coverage", ""])
        for field, stats in coverage.items():
            lines.append(f"- `{field}`: `{stats['count']}` / `{stats['total']}` ({stats['fraction']:.2%})")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- This is a paper-faithful approximation, not an exact reproduction of Vincent-Lamarre's original WordNet preprocessing.",
            "- Differences can come from OEWN 2024, representative-sense ordering, token filtering, and POS resolution policy.",
            "- Candidate seed sizes are heuristic unless the selected seed method reports exact coverage for all cyclic SCCs.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_paper_wordnet_json_summary(
    build: LexicalGraphBuild,
    analysis: KernelAnalysis,
    json_path: Path,
    top_n: int = 25,
    annotations: AnnotationStore | None = None,
) -> None:
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]
    components = {
        "rest": build.nodes - analysis.kernel_nodes,
        "kernel": analysis.kernel_nodes,
        "core": analysis.core_nodes,
        "satellites": analysis.satellite_nodes,
        "seed": set(analysis.seed_nodes),
    }
    payload = {
        "lexicon_id": build.lexicon_id,
        "graph_type": build.graph_type,
        "language": build.language,
        "resource_id": build.resource_id,
        "node_count": len(build.nodes),
        "edge_count": analysis.edges,
        "kernel_node_count": len(analysis.kernel_nodes),
        "kernel_fraction": len(analysis.kernel_nodes) / len(build.nodes),
        "kernel_scc_count": len(analysis.kernel_sccs),
        "source_scc_count": len(analysis.source_sccs),
        "core_node_count": len(analysis.core_nodes),
        "satellite_node_count": len(analysis.satellite_nodes),
        "core_policy": analysis.core_policy,
        "seed_method": analysis.seed_method,
        "seed_node_count": len(analysis.seed_nodes),
        "seed_fraction_total": len(analysis.seed_nodes) / len(build.nodes),
        "seed_fraction_kernel": len(analysis.seed_nodes) / max(len(analysis.kernel_nodes), 1),
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "largest_kernel_scc_sizes": largest_sccs,
        "layer_histogram": analysis.layer_histogram,
        "resolution_stats": build.metadata["resolution_stats"],
        "paper_reference": build.metadata["reference"],
        "top_seed_nodes": top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n, labels=build.labels),
        "top_degrees": top_degree_nodes(build.adjacency, top_n, labels=build.labels),
    }
    if annotations is not None:
        payload["annotation_sources"] = annotations.sources
        payload["annotation_coverage"] = annotation_coverage(build.nodes, annotations)
        payload["component_annotation_summary"] = component_annotation_summary(components, annotations)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def render_synset_markdown_report(
    build: SynsetGraphBuild,
    analysis: KernelAnalysis,
    report_path: Path,
    top_n: int = 25,
    annotations: AnnotationStore | None = None,
) -> None:
    total_nodes = len(build.nodes)
    kernel_size = len(analysis.kernel_nodes)
    seed_size = len(analysis.seed_nodes)
    source_scc_count = len(analysis.source_sccs)
    top_degrees = top_degree_nodes(build.adjacency, top_n, labels=build.labels)
    top_seeds = top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n, labels=build.labels)
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]

    lines = [
        "# Open English WordNet Synset-Kernel Report",
        "",
        f"- Lexicon: `{build.lexicon_id}`",
        "- Graph type: experimental synset-level gloss graph",
        "- Node policy: one node per defined synset",
        "- Edge policy: add `defining_synset -> defined_synset` when a gloss lemma resolves uniquely or wins a strict overlap tie-break",
        "- Sense resolution: prefer same-POS candidates; for ambiguous cases require positive overlap after removing the candidate lemma itself and require the best score to beat the runner-up",
        f"- Seed method: `{analysis.seed_method}`",
        f"- Core policy: `{analysis.core_policy}`",
        "",
        "## Summary",
        "",
        f"- Total synset nodes: `{total_nodes}`",
        f"- Total directed edges: `{analysis.edges}`",
        f"- Kernel nodes: `{kernel_size}` ({kernel_size / total_nodes:.2%})",
        f"- Kernel SCC count: `{len(analysis.kernel_sccs)}`",
        f"- Source SCCs inside kernel: `{source_scc_count}`",
        f"- Core size (union of source SCCs): `{len(analysis.core_nodes)}`",
        f"- Satellite size (kernel minus source-SCC Core): `{len(analysis.satellite_nodes)}`",
        f"- Fast cycle-hitting seed size: `{seed_size}` ({seed_size / total_nodes:.2%}; {seed_size / max(kernel_size, 1):.2%} of kernel)",
        f"- Residual cyclic SCCs after bounded heuristic: `{analysis.residual_cyclic_scc_count}`",
        "",
        "## Resolution Stats",
        "",
        f"- Candidate gloss matches: `{build.resolution_stats['candidate_matches']}`",
        f"- Resolved by unique same-POS match: `{build.resolution_stats['resolved_same_pos_unique']}`",
        f"- Resolved by unique global match: `{build.resolution_stats['resolved_global_unique']}`",
        f"- Resolved by overlap within same POS: `{build.resolution_stats['resolved_same_pos_overlap']}`",
        f"- Resolved by overlap across POS: `{build.resolution_stats['resolved_global_overlap']}`",
        f"- Ambiguous matches skipped: `{build.resolution_stats['ambiguous_skipped']}`",
        f"- Self-only matches skipped: `{build.resolution_stats['self_only_skipped']}`",
        f"- Unresolved matches skipped: `{build.resolution_stats['unresolved_skipped']}`",
        "",
        "## Largest Kernel SCCs",
        "",
    ]
    for index, size in enumerate(largest_sccs, start=1):
        lines.append(f"- SCC `{index}`: `{size}` nodes")

    lines.extend(["", "## Layer Histogram", ""])
    if analysis.layer_histogram:
        for layer, count in analysis.layer_histogram.items():
            lines.append(f"- Layer `{layer}`: `{count}` nodes")
    else:
        lines.append("- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.")

    lines.extend(["", "## Top Fast Seed Candidates", ""])
    for label, score in top_seeds:
        lines.append(f"- `{label}` (degree score `{score}`)")

    lines.extend(["", "## Highest Outdegree Synsets", ""])
    for label, degree in top_degrees["outdegree"]:
        lines.append(f"- `{label}`: `{degree}`")

    lines.extend(["", "## Highest Indegree Synsets", ""])
    for label, degree in top_degrees["indegree"]:
        lines.append(f"- `{label}`: `{degree}`")

    if annotations is not None:
        coverage = annotation_coverage(build.nodes, annotations)
        lines.extend(["", "## Annotation Coverage", ""])
        for field, stats in coverage.items():
            lines.append(f"- `{field}`: `{stats['count']}` / `{stats['total']}` ({stats['fraction']:.2%})")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- This is the experimental synset graph, not the paper-faithful baseline.",
            "- Ambiguous gloss lemmas are only resolved when a strict overlap test separates one candidate from the others; unresolved ties are still skipped.",
            "- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_synset_json_summary(
    build: SynsetGraphBuild,
    analysis: KernelAnalysis,
    json_path: Path,
    top_n: int = 25,
    annotations: AnnotationStore | None = None,
) -> None:
    largest_sccs = sorted((len(component) for component in analysis.kernel_sccs), reverse=True)[:10]
    payload = {
        "lexicon_id": build.lexicon_id,
        "graph_type": "synset_level_gloss_graph",
        "resolution_mode": "strict_overlap_same_pos_preferred",
        "node_count": len(build.nodes),
        "edge_count": analysis.edges,
        "kernel_node_count": len(analysis.kernel_nodes),
        "kernel_fraction": len(analysis.kernel_nodes) / len(build.nodes),
        "kernel_scc_count": len(analysis.kernel_sccs),
        "source_scc_count": len(analysis.source_sccs),
        "core_node_count": len(analysis.core_nodes),
        "satellite_node_count": len(analysis.satellite_nodes),
        "core_policy": analysis.core_policy,
        "seed_method": analysis.seed_method,
        "seed_node_count": len(analysis.seed_nodes),
        "seed_fraction_total": len(analysis.seed_nodes) / len(build.nodes),
        "seed_fraction_kernel": len(analysis.seed_nodes) / max(len(analysis.kernel_nodes), 1),
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "largest_kernel_scc_sizes": largest_sccs,
        "layer_histogram": analysis.layer_histogram,
        "resolution_stats": build.resolution_stats,
        "top_seed_nodes": top_seed_nodes(analysis.seed_nodes, build.adjacency, top_n, labels=build.labels),
        "top_degrees": top_degree_nodes(build.adjacency, top_n, labels=build.labels),
    }
    candidate_matches = max(build.resolution_stats["candidate_matches"], 1)
    resolved = (
        build.resolution_stats["resolved_same_pos_unique"]
        + build.resolution_stats["resolved_global_unique"]
        + build.resolution_stats["resolved_same_pos_overlap"]
        + build.resolution_stats["resolved_global_overlap"]
    )
    payload["resolution_rates"] = {
        "resolved_fraction": resolved / candidate_matches,
        "ambiguous_skipped_fraction": build.resolution_stats["ambiguous_skipped"] / candidate_matches,
    }
    if annotations is not None:
        components = {
            "rest": build.nodes - analysis.kernel_nodes,
            "kernel": analysis.kernel_nodes,
            "core": analysis.core_nodes,
            "satellites": analysis.satellite_nodes,
            "seed": set(analysis.seed_nodes),
        }
        payload["annotation_sources"] = annotations.sources
        payload["annotation_coverage"] = annotation_coverage(build.nodes, annotations)
        payload["component_annotation_summary"] = component_annotation_summary(components, annotations)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def run_analysis(
    lexicon_id: str,
    report_path: Path,
    json_path: Path,
    top_n: int,
    graph_type: str = "sense",
    seed_method: str = "bounded-scc",
    core_policy: str = "source-union",
    annotation_paths: list[Path] | None = None,
    export_layers_path: Path | None = None,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    annotations = load_annotation_csvs(annotation_paths or [])
    if graph_type == "lemma":
        build = build_lemma_graph(lexicon_id)
        analysis = analyze_kernel(
            build.nodes,
            build.adjacency,
            seed_method=seed_method,
            core_policy=core_policy,
        )
        render_lemma_markdown_report(build, analysis, report_path, top_n=top_n)
        write_lemma_json_summary(build, analysis, json_path, top_n=top_n)
        write_layers(export_layers_path, analysis)
        return

    if graph_type == "paper-wordnet":
        build = build_paper_wordnet_graph(lexicon_id)
        analysis = analyze_kernel(
            build.nodes,
            build.adjacency,
            seed_method=seed_method,
            core_policy=core_policy,
        )
        render_paper_wordnet_markdown_report(
            build,
            analysis,
            report_path,
            top_n=top_n,
            annotations=annotations,
        )
        write_paper_wordnet_json_summary(
            build,
            analysis,
            json_path,
            top_n=top_n,
            annotations=annotations,
        )
        write_layers(export_layers_path, analysis)
        return

    if graph_type == "sense":
        build = build_synset_graph(lexicon_id)
        analysis = analyze_kernel(
            build.nodes,
            build.adjacency,
            seed_method=seed_method,
            core_policy=core_policy,
        )
        render_synset_markdown_report(build, analysis, report_path, top_n=top_n, annotations=annotations)
        write_synset_json_summary(build, analysis, json_path, top_n=top_n, annotations=annotations)
        write_layers(export_layers_path, analysis)
        return

    raise ValueError(f"Unsupported graph type: {graph_type}")


def write_layers(export_layers_path: Path | None, analysis: KernelAnalysis) -> None:
    if export_layers_path is None:
        return
    export_layers_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "seed_method": analysis.seed_method,
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "layer_histogram": analysis.layer_histogram,
        "layer_by_node": dict(sorted(analysis.layer_by_node.items())),
    }
    export_layers_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
