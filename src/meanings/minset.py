from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from time import perf_counter


Adjacency = dict[str, set[str]]


@dataclass(slots=True)
class SccMinSetResult:
    method: str
    component_size: int
    seed_count: int
    exact: bool
    lower_bound: int | None
    upper_bound: int
    residual_cyclic_scc_count: int


@dataclass(slots=True)
class MinSetResult:
    method: str
    nodes: list[str]
    exact: bool
    lower_bound: int | None
    upper_bound: int
    residual_cyclic_scc_count: int
    scc_results: list[SccMinSetResult]
    runtime_seconds: float

    @property
    def scc_exact_count(self) -> int:
        return sum(1 for result in self.scc_results if result.exact)

    @property
    def scc_heuristic_count(self) -> int:
        return sum(1 for result in self.scc_results if not result.exact)


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


def is_cyclic_component(component: set[str], adjacency: Adjacency) -> bool:
    if len(component) > 1:
        return True
    node = next(iter(component))
    return node in adjacency.get(node, set())


def cyclic_sccs(nodes: set[str], adjacency: Adjacency) -> list[set[str]]:
    return [
        component
        for component in strongly_connected_components(nodes, adjacency)
        if is_cyclic_component(component, adjacency)
    ]


def choose_feedback_vertex(component: set[str], adjacency: Adjacency, rev: Adjacency) -> str:
    internal_out = {
        node: sum(1 for target in adjacency.get(node, set()) if target in component and target != node)
        for node in component
    }
    internal_in = {
        node: sum(1 for source in rev.get(node, set()) if source in component and source != node)
        for node in component
    }
    return max(
        component,
        key=lambda node: (
            internal_out[node] + internal_in[node],
            internal_out[node],
            internal_in[node],
            node,
        ),
    )


def is_acyclic(nodes: set[str], adjacency: Adjacency) -> bool:
    subgraph = induced_subgraph(nodes, adjacency)
    return not cyclic_sccs(nodes, subgraph)


def find_directed_cycle(nodes: set[str], adjacency: Adjacency) -> list[str] | None:
    subgraph = induced_subgraph(nodes, adjacency)
    state = {node: 0 for node in nodes}
    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack_index[node] = len(stack)
        stack.append(node)
        for target in sorted(subgraph.get(node, set())):
            if target not in state:
                continue
            if state[target] == 0:
                cycle = visit(target)
                if cycle is not None:
                    return cycle
            elif state[target] == 1:
                return stack[stack_index[target] :].copy()
        stack.pop()
        stack_index.pop(node, None)
        state[node] = 2
        return None

    for start in sorted(nodes):
        if state[start] == 0:
            cycle = visit(start)
            if cycle is not None:
                return cycle
    return None


def bounded_cycle_hitting_set(nodes: set[str], adjacency: Adjacency, max_passes: int = 8) -> MinSetResult:
    started = perf_counter()
    active = set(nodes)
    seed: list[str] = []
    residual_cyclic_scc_count = 0
    scc_results: list[SccMinSetResult] = []
    for _ in range(max_passes):
        subgraph = induced_subgraph(active, adjacency)
        rev = reverse_adjacency(active, subgraph)
        cyclic_components = cyclic_sccs(active, subgraph)
        if not cyclic_components:
            return MinSetResult(
                method="bounded-scc",
                nodes=seed,
                exact=False,
                lower_bound=None,
                upper_bound=len(seed),
                residual_cyclic_scc_count=0,
                scc_results=scc_results,
                runtime_seconds=perf_counter() - started,
            )
        removals = [choose_feedback_vertex(component, subgraph, rev) for component in cyclic_components]
        for component, node in zip(cyclic_components, removals, strict=True):
            if node in active:
                active.remove(node)
                seed.append(node)
                scc_results.append(
                    SccMinSetResult(
                        method="bounded-scc",
                        component_size=len(component),
                        seed_count=1,
                        exact=False,
                        lower_bound=None,
                        upper_bound=1,
                        residual_cyclic_scc_count=0,
                    )
                )
        residual_cyclic_scc_count = len(cyclic_components)

    subgraph = induced_subgraph(active, adjacency)
    residual_cyclic_scc_count = len(cyclic_sccs(active, subgraph))
    return MinSetResult(
        method="bounded-scc",
        nodes=seed,
        exact=False,
        lower_bound=None,
        upper_bound=len(seed),
        residual_cyclic_scc_count=residual_cyclic_scc_count,
        scc_results=scc_results,
        runtime_seconds=perf_counter() - started,
    )


def exact_feedback_vertex_set(component: set[str], adjacency: Adjacency, max_size: int) -> list[str] | None:
    ordered = sorted(component)
    if len(ordered) > max_size:
        return None
    for size in range(len(ordered) + 1):
        for removed in combinations(ordered, size):
            remaining = component - set(removed)
            if is_acyclic(remaining, adjacency):
                return list(removed)
    return None


def exact_lazy_cycle_feedback_vertex_set(
    component: set[str],
    adjacency: Adjacency,
    max_size: int,
) -> list[str] | None:
    if len(component) > max_size:
        return None

    best: list[str] | None = None
    degree = {
        node: sum(1 for target in adjacency.get(node, set()) if target in component and target != node)
        + sum(1 for source, targets in adjacency.items() if source in component and node in targets and source != node)
        for node in component
    }

    def search(removed: set[str]) -> None:
        nonlocal best
        if best is not None and len(removed) >= len(best):
            return
        remaining = component - removed
        cycle = find_directed_cycle(remaining, adjacency)
        if cycle is None:
            best = sorted(removed)
            return
        for node in sorted(cycle, key=lambda item: (-degree[item], item)):
            search(removed | {node})

    search(set())
    return best


def exact_small_greedy_cycle_hitting_set(
    nodes: set[str],
    adjacency: Adjacency,
    exact_limit: int = 12,
) -> MinSetResult:
    started = perf_counter()
    active = set(nodes)
    seed: list[str] = []
    scc_results: list[SccMinSetResult] = []
    lower_bound = 0
    while True:
        subgraph = induced_subgraph(active, adjacency)
        rev = reverse_adjacency(active, subgraph)
        cyclic_components = cyclic_sccs(active, subgraph)
        if not cyclic_components:
            exact = all(result.exact for result in scc_results)
            return MinSetResult(
                method="exact-small-greedy",
                nodes=seed,
                exact=exact,
                lower_bound=lower_bound if exact else None,
                upper_bound=len(seed),
                residual_cyclic_scc_count=0,
                scc_results=scc_results,
                runtime_seconds=perf_counter() - started,
            )

        changed = False
        for component in cyclic_components:
            exact = exact_feedback_vertex_set(component, subgraph, exact_limit)
            if exact is None:
                chosen = [choose_feedback_vertex(component, subgraph, rev)]
                result_exact = False
                result_lower = None
            else:
                chosen = exact
                result_exact = True
                result_lower = len(chosen)
                lower_bound += len(chosen)
            removed_now = 0
            for node in chosen:
                if node in active:
                    active.remove(node)
                    seed.append(node)
                    changed = True
                    removed_now += 1
            scc_results.append(
                SccMinSetResult(
                    method="exact-small" if result_exact else "greedy",
                    component_size=len(component),
                    seed_count=removed_now,
                    exact=result_exact,
                    lower_bound=result_lower,
                    upper_bound=removed_now,
                    residual_cyclic_scc_count=0,
                )
            )
        if not changed:
            return MinSetResult(
                method="exact-small-greedy",
                nodes=seed,
                exact=False,
                lower_bound=None,
                upper_bound=len(seed),
                residual_cyclic_scc_count=len(cyclic_components),
                scc_results=scc_results,
                runtime_seconds=perf_counter() - started,
            )


def exact_cutting_cycle_hitting_set(
    nodes: set[str],
    adjacency: Adjacency,
    exact_limit: int = 18,
) -> MinSetResult:
    started = perf_counter()
    active = set(nodes)
    seed: list[str] = []
    scc_results: list[SccMinSetResult] = []
    lower_bound = 0
    subgraph = induced_subgraph(active, adjacency)
    rev = reverse_adjacency(active, subgraph)
    initial_components = cyclic_sccs(active, subgraph)

    for component in initial_components:
        exact = exact_lazy_cycle_feedback_vertex_set(component, subgraph, exact_limit)
        if exact is None:
            chosen = [choose_feedback_vertex(component, subgraph, rev)]
            result_exact = False
            result_lower = None
        else:
            chosen = exact
            result_exact = True
            result_lower = len(chosen)
            lower_bound += len(chosen)
        removed_now = 0
        for node in chosen:
            if node in active:
                active.remove(node)
                seed.append(node)
                removed_now += 1
        scc_results.append(
            SccMinSetResult(
                method="exact-cutting" if result_exact else "greedy",
                component_size=len(component),
                seed_count=removed_now,
                exact=result_exact,
                lower_bound=result_lower,
                upper_bound=removed_now,
                residual_cyclic_scc_count=0,
            )
        )

    residual = len(cyclic_sccs(active, induced_subgraph(active, adjacency)))
    exact = residual == 0 and all(result.exact for result in scc_results)
    return MinSetResult(
        method="exact-cutting",
        nodes=seed,
        exact=exact,
        lower_bound=lower_bound if exact else None,
        upper_bound=len(seed),
        residual_cyclic_scc_count=residual,
        scc_results=scc_results,
        runtime_seconds=perf_counter() - started,
    )


def solve_minset(
    nodes: set[str],
    adjacency: Adjacency,
    method: str,
) -> MinSetResult:
    if method == "bounded-scc":
        return bounded_cycle_hitting_set(nodes, adjacency)
    if method == "exact-small-greedy":
        return exact_small_greedy_cycle_hitting_set(nodes, adjacency)
    if method == "exact-cutting":
        return exact_cutting_cycle_hitting_set(nodes, adjacency)
    raise ValueError(f"Unsupported seed method: {method}")
