from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass

from meanings.minset import MinSetResult, solve_minset


Adjacency = dict[str, set[str]]


@dataclass(slots=True)
class KernelAnalysis:
    nodes: set[str]
    edges: int
    kernel_nodes: set[str]
    kernel_sccs: list[set[str]]
    source_sccs: list[set[str]]
    core_nodes: set[str]
    satellite_nodes: set[str]
    core_policy: str
    seed_nodes: list[str]
    seed_method: str
    minset_result: MinSetResult
    residual_cyclic_scc_count: int
    layer_histogram: dict[int, int]
    layer_by_node: dict[str, int]


def reverse_adjacency(nodes: set[str], adjacency: Adjacency) -> Adjacency:
    rev: Adjacency = {node: set() for node in nodes}
    for source, targets in adjacency.items():
        for target in targets:
            if target in rev:
                rev[target].add(source)
    return rev


def induced_subgraph(nodes: set[str], adjacency: Adjacency) -> Adjacency:
    return {node: {target for target in adjacency.get(node, set()) if target in nodes} for node in nodes}


def strongly_connected_components(nodes: set[str], adjacency: Adjacency) -> list[set[str]]:
    rev = reverse_adjacency(nodes, adjacency)
    seen: set[str] = set()
    finish_order: list[str] = []

    for start in nodes:
        if start in seen:
            continue
        stack: list[tuple[str, bool]] = [(start, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                finish_order.append(node)
                continue
            if node in seen:
                continue
            seen.add(node)
            stack.append((node, True))
            for target in adjacency.get(node, set()):
                if target not in seen:
                    stack.append((target, False))

    components: list[set[str]] = []
    assigned: set[str] = set()
    for start in reversed(finish_order):
        if start in assigned:
            continue
        stack = [start]
        component: set[str] = set()
        assigned.add(start)
        while stack:
            node = stack.pop()
            component.add(node)
            for source in rev.get(node, set()):
                if source not in assigned:
                    assigned.add(source)
                    stack.append(source)
        components.append(component)
    return components


def compute_kernel(nodes: set[str], adjacency: Adjacency) -> set[str]:
    rev = reverse_adjacency(nodes, adjacency)
    remaining = set(nodes)
    live_out = {
        node: sum(1 for target in adjacency.get(node, set()) if target != node and target in nodes)
        for node in nodes
    }
    queue = deque(node for node, out_degree in live_out.items() if out_degree == 0)
    while queue:
        node = queue.popleft()
        if node not in remaining:
            continue
        remaining.remove(node)
        for parent in rev.get(node, set()):
            if parent not in remaining:
                continue
            if parent != node and node in adjacency.get(parent, set()):
                live_out[parent] -= 1
                if live_out[parent] == 0:
                    queue.append(parent)
    return remaining


def source_sccs(nodes: set[str], adjacency: Adjacency) -> list[set[str]]:
    components = strongly_connected_components(nodes, adjacency)
    index_of: dict[str, int] = {}
    for index, component in enumerate(components):
        for node in component:
            index_of[node] = index
    indegree = [0] * len(components)
    for source, targets in adjacency.items():
        source_index = index_of[source]
        for target in targets:
            target_index = index_of[target]
            if source_index != target_index:
                indegree[target_index] += 1
    return [component for index, component in enumerate(components) if indegree[index] == 0]


def compute_layer_map(nodes: set[str], adjacency: Adjacency, seed_nodes: set[str]) -> dict[str, int]:
    rev = reverse_adjacency(nodes, adjacency)
    known_layers = {node: 0 for node in seed_nodes}
    remaining = nodes - seed_nodes
    unresolved = {node: sum(1 for source in rev.get(node, set()) if source in remaining) for node in remaining}
    ready = deque(node for node, count in unresolved.items() if count == 0)

    while ready:
        node = ready.popleft()
        predecessor_layers = [known_layers[source] for source in rev.get(node, set()) if source in known_layers]
        known_layers[node] = 1 + max(predecessor_layers, default=0)
        for target in adjacency.get(node, set()):
            if target in unresolved:
                unresolved[target] -= 1
                if unresolved[target] == 0:
                    ready.append(target)

    return known_layers


def layer_histogram(layer_by_node: dict[str, int]) -> dict[int, int]:
    histogram = Counter(layer_by_node.values())
    return dict(sorted(histogram.items()))


def choose_core_nodes(
    kernel_sccs: list[set[str]],
    source_components: list[set[str]],
    core_policy: str,
) -> set[str]:
    if core_policy == "source-union":
        return set().union(*source_components) if source_components else set()
    if core_policy == "largest-scc":
        return set(max(kernel_sccs, key=len)) if kernel_sccs else set()
    raise ValueError(f"Unsupported core policy: {core_policy}")


def analyze_kernel(
    nodes: set[str],
    adjacency: Adjacency,
    seed_method: str = "bounded-scc",
    core_policy: str = "source-union",
) -> KernelAnalysis:
    kernel_nodes = compute_kernel(nodes, adjacency)
    kernel_graph = induced_subgraph(kernel_nodes, adjacency)
    kernel_sccs = strongly_connected_components(kernel_nodes, kernel_graph)
    src_sccs = source_sccs(kernel_nodes, kernel_graph)
    core_nodes = choose_core_nodes(kernel_sccs, src_sccs, core_policy)
    satellite_nodes = kernel_nodes - core_nodes
    minset_result = solve_minset(kernel_nodes, kernel_graph, seed_method)
    seed_nodes = minset_result.nodes
    residual_cyclic_scc_count = minset_result.residual_cyclic_scc_count
    layers: dict[str, int] = {}
    if residual_cyclic_scc_count == 0 and seed_nodes:
        layers = compute_layer_map(kernel_nodes, kernel_graph, set(seed_nodes))
    edge_count = sum(len(targets) for targets in adjacency.values())
    return KernelAnalysis(
        nodes=nodes,
        edges=edge_count,
        kernel_nodes=kernel_nodes,
        kernel_sccs=kernel_sccs,
        source_sccs=src_sccs,
        core_nodes=core_nodes,
        satellite_nodes=satellite_nodes,
        core_policy=core_policy,
        seed_nodes=seed_nodes,
        seed_method=seed_method,
        minset_result=minset_result,
        residual_cyclic_scc_count=residual_cyclic_scc_count,
        layer_histogram=layer_histogram(layers),
        layer_by_node=layers,
    )
