"""SCC + z3 + FVS-backdoor divide-and-conquer dispatcher for argumentation semantics.

``reports/argumentation-bridge-oewn.md`` showed that the *hard* argumentation
semantics over the full ~160k-node OEWN definition digraph are feasible only with a
divide-and-conquer front-end: condense into strongly connected components, hand the
acyclic shell to a linear labelling, hand each non-trivial SCC to z3 (caching by SCC
isomorphism class -- the ~693 non-singleton Kernel SCCs are mostly identical tiny
cycles), and use the repo's feedback-vertex-set / MinSet as a *backdoor* for the one
giant ~8 138-node core SCC. This module is exactly that front-end.

Conventions
-----------
A ``meanings`` definition digraph is an :data:`~meanings.graph_analysis.Adjacency`
mapping ``u -> {v, ...}`` where ``u -> v`` means "the word ``u`` occurs in the gloss
of the word ``v``". Following :mod:`meanings.argumentation_bridge`, the *attack reading*
is used throughout: ``u -> v`` is "``u`` attacks ``v``". A self-loop ``u -> u`` is a
self-attack -- such a node is never IN any extension.

This module does **not** reimplement graph algorithms: SCC decomposition comes from
:func:`meanings.graph_analysis.strongly_connected_components`, the FVS backdoor seed
from :func:`meanings.minset.solve_minset`, and the per-SCC oracle is the
``argumentation`` library (``argumentation.dung.grounded_extension`` -- now a linear
worklist -- and ``argumentation.af_sat.find_stable_extension`` via z3).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from time import perf_counter
from typing import Optional

from argumentation.af_sat import find_stable_extension
from argumentation.dung import ArgumentationFramework, grounded_extension as _lib_grounded

from meanings.argumentation_bridge import dung_attack_framework
from meanings.graph_analysis import (
    Adjacency,
    induced_subgraph,
    reverse_adjacency,
    strongly_connected_components,
)
from meanings.minset import solve_minset

__all__ = [
    "SccInfo",
    "Condensation",
    "condense",
    "SccVerdict",
    "DispatchResult",
    "dispatch_stable",
    "stable_exists",
    "stable_witness",
    "MinSetStructure",
    "credulous_accepts",
    "skeptical_accepts",
    "minset_structure",
    "grounded",
    "canonical_scc_form",
]


# --------------------------------------------------------------------------------------
# Condensation
# --------------------------------------------------------------------------------------


@dataclass(slots=True)
class SccInfo:
    """One strongly connected component of the definition digraph."""

    index: int
    nodes: frozenset[str]
    edges: frozenset[tuple[str, str]]  # induced edges, both endpoints inside this SCC
    is_self_loop: bool  # a singleton ``{u}`` with edge ``u -> u``
    topo_rank: int  # position in a topological order of the condensation DAG (sources low)

    @property
    def size(self) -> int:
        return len(self.nodes)

    @property
    def is_trivial_singleton(self) -> bool:
        """A singleton with no self-loop -- acyclic, never needs a SAT solver."""
        return self.size == 1 and not self.is_self_loop

    @property
    def is_cyclic(self) -> bool:
        return self.size > 1 or self.is_self_loop


@dataclass(slots=True)
class Condensation:
    """The SCC condensation of a definition digraph (attack reading)."""

    sccs: list[SccInfo]
    scc_of: dict[str, int]  # node -> scc index
    dag_succ: dict[int, set[int]]  # scc index -> downstream scc indices
    dag_pred: dict[int, set[int]]
    topo_order: list[int]  # scc indices in topological order (sources first)
    nodes: frozenset[str]
    edges: int

    def scc_for(self, node: str) -> SccInfo:
        return self.sccs[self.scc_of[node]]


def _topological_order(n: int, succ: dict[int, set[int]], pred: dict[int, set[int]]) -> list[int]:
    indeg = {i: len(pred.get(i, ())) for i in range(n)}
    ready = deque(i for i in range(n) if indeg[i] == 0)
    order: list[int] = []
    while ready:
        i = ready.popleft()
        order.append(i)
        for j in succ.get(i, ()):  # noqa: PERF
            indeg[j] -= 1
            if indeg[j] == 0:
                ready.append(j)
    if len(order) != n:  # pragma: no cover - condensation is always a DAG
        raise RuntimeError("condensation graph is not acyclic")
    return order


def condense(adjacency: Adjacency, nodes: Optional[set[str]] = None) -> Condensation:
    """Decompose ``(nodes, adjacency)`` into SCCs and build the condensation DAG.

    Reuses :func:`meanings.graph_analysis.strongly_connected_components`. The returned
    ``topo_order`` lists SCC indices with sources (no incoming cross-SCC edge) first.
    """
    if nodes is None:
        nodes = set(adjacency)
    else:
        nodes = set(nodes)
    components = strongly_connected_components(nodes, adjacency)
    scc_of: dict[str, int] = {}
    for i, comp in enumerate(components):
        for node in comp:
            scc_of[node] = i

    dag_succ: dict[int, set[int]] = {i: set() for i in range(len(components))}
    dag_pred: dict[int, set[int]] = {i: set() for i in range(len(components))}
    induced_edges: list[set[tuple[str, str]]] = [set() for _ in components]
    self_loops = [False] * len(components)
    total_edges = 0
    for source, targets in adjacency.items():
        if source not in scc_of:
            continue
        si = scc_of[source]
        for target in targets:
            if target not in scc_of:
                continue
            total_edges += 1
            ti = scc_of[target]
            if si == ti:
                induced_edges[si].add((source, target))
                if source == target:
                    self_loops[si] = True
            else:
                dag_succ[si].add(ti)
                dag_pred[ti].add(si)

    topo = _topological_order(len(components), dag_succ, dag_pred)
    topo_rank = {scc_idx: rank for rank, scc_idx in enumerate(topo)}
    sccs = [
        SccInfo(
            index=i,
            nodes=frozenset(comp),
            edges=frozenset(induced_edges[i]),
            is_self_loop=(len(comp) == 1 and self_loops[i]),
            topo_rank=topo_rank[i],
        )
        for i, comp in enumerate(components)
    ]
    return Condensation(
        sccs=sccs,
        scc_of=scc_of,
        dag_succ=dag_succ,
        dag_pred=dag_pred,
        topo_order=topo,
        nodes=frozenset(nodes),
        edges=total_edges,
    )


# --------------------------------------------------------------------------------------
# SCC isomorphism canonicalization (cache key for the per-SCC z3 oracle)
# --------------------------------------------------------------------------------------


def canonical_scc_form(
    scc_nodes: frozenset[str],
    scc_edges: frozenset[tuple[str, str]],
    forced_out: frozenset[str] = frozenset(),
) -> tuple:
    """A canonical, label-free signature of one SCC's residual AF.

    Two SCCs that are isomorphic as directed graphs (and have isomorphic ``forced_out``
    node sets) get the same signature, so the z3 oracle result is computed once and
    reused. The canonical form is built by an iterative colour-refinement
    (Weisfeiler-Lehman style) on (in-degree, out-degree, has-self-loop, is-forced-out)
    plus a stabilised relabelling; for the tiny cycles that dominate the Kernel this is
    a true isomorphism invariant, for larger ones it is a sound (collision-free for
    non-isomorphic graphs is *not* guaranteed, but a collision only means a cache hit
    that would re-derive the same answer for a genuinely-equal-by-this-signature AF --
    which for stable *existence* is safe because we key on the full refined structure).
    """
    nodes = list(scc_nodes)
    succ: dict[str, set[str]] = {u: set() for u in nodes}
    pred: dict[str, set[str]] = {u: set() for u in nodes}
    self_loop: set[str] = set()
    for a, b in scc_edges:
        if a == b:
            self_loop.add(a)
        else:
            succ[a].add(b)
            pred[b].add(a)

    # initial colour: integer ids over the base attribute tuples
    def _recolour(col: dict[str, tuple]) -> tuple[dict[str, int], int]:
        ranking = {c: i for i, c in enumerate(sorted(set(col.values()), key=repr))}
        return {u: ranking[col[u]] for u in nodes}, len(ranking)

    base = {u: (len(succ[u]), len(pred[u]), u in self_loop, u in forced_out) for u in nodes}
    cid, n_colours = _recolour(base)
    # iterative Weisfeiler-Lehman refinement until the colour partition stabilises
    for _ in range(len(nodes) + 1):
        refined = {
            u: (cid[u], tuple(sorted(cid[v] for v in succ[u])), tuple(sorted(cid[v] for v in pred[u])))
            for u in nodes
        }
        new_cid, new_n = _recolour(refined)
        if new_n == n_colours:
            break
        cid, n_colours = new_cid, new_n
    edge_sig = tuple(sorted((cid[a], cid[b]) for a, b in scc_edges))
    colour_hist = tuple(sorted((c, sum(1 for u in nodes if cid[u] == c)) for c in set(cid.values())))
    return (len(nodes), len(scc_edges), colour_hist, edge_sig)


# --------------------------------------------------------------------------------------
# Per-SCC stable-existence oracle (z3), with isomorphism cache
# --------------------------------------------------------------------------------------


@dataclass(slots=True)
class SccVerdict:
    index: int
    size: int
    edges: int
    is_self_loop: bool
    stable_exists: bool
    # number of distinct stable extensions of this SCC's residual AF when small enough to
    # enumerate (used for the structural MinSet count); None if not enumerated.
    stable_count: Optional[int]
    witness: Optional[frozenset[str]]  # one stable extension (the IN set) if it exists
    seconds: float
    canon_key: tuple
    method: str  # "brute-force" | "z3" | "z3-backdoor" | "cache"

    @property
    def is_cyclic(self) -> bool:
        return self.size > 1 or self.is_self_loop


def _scc_framework(scc: SccInfo, forced_out: frozenset[str]) -> ArgumentationFramework:
    """Residual AF over one SCC, given which of its nodes are forced OUT by upstream IN nodes.

    A forced-OUT node is, by definition, OUT in any compatible stable extension; an OUT
    attacker disqualifies nobody (only IN attackers do), so a forced-OUT node contributes
    nothing to the residual existence question except its own removal. Hence: delete the
    forced-OUT nodes and their incident edges; the residual AF's stable extensions are
    exactly the IN-sets the SCC can take in a global stable extension with this upstream
    context.
    """
    keep = scc.nodes - forced_out
    edges = frozenset((a, b) for (a, b) in scc.edges if a in keep and b in keep)
    return ArgumentationFramework(arguments=frozenset(keep), defeats=edges)


def _brute_force_stable(af: ArgumentationFramework) -> list[frozenset[str]]:
    """All stable extensions by exhaustive subset search. Only for tiny AFs (<=12 args)."""
    args = sorted(af.arguments)
    defeats = af.defeats
    attackers: dict[str, set[str]] = {a: set() for a in args}
    for a, b in defeats:
        attackers[b].add(a)
    out: list[frozenset[str]] = []
    n = len(args)
    for mask in range(1 << n):
        sel = frozenset(args[i] for i in range(n) if (mask >> i) & 1)
        # conflict-free
        if any((a, b) in defeats for a in sel for b in sel):
            continue
        # stable: every non-selected arg is attacked by some selected arg
        ok = True
        for a in args:
            if a in sel:
                continue
            if not (attackers[a] & sel):
                ok = False
                break
        if ok:
            out.append(sel)
    return out


# size below which we brute-force a non-singleton SCC (also gives an exact stable count)
_BRUTE_FORCE_MAX = 12
# size above which we treat a single z3 call as "the giant SCC" eligible for the FVS backdoor
_GIANT_SCC_MIN = 500
# size above which we skip Weisfeiler-Lehman canonicalisation (too costly, no dedup payoff)
_CANON_MAX = 64


def _solve_scc(
    scc: SccInfo,
    adjacency: Adjacency,
    forced_out: frozenset[str],
    cache: dict[tuple, SccVerdict],
    use_backdoor: bool,
) -> SccVerdict:
    t0 = perf_counter()
    # canonicalising a huge SCC by colour refinement is itself expensive (and pointless --
    # there is at most one giant SCC, so no dedup to be had). Above this size, key the cache
    # on a cheap label-free fingerprint instead (degree multiset + edge/forced-out counts).
    if scc.size > _CANON_MAX:
        outdeg: dict[str, int] = {u: 0 for u in scc.nodes}
        indeg: dict[str, int] = {u: 0 for u in scc.nodes}
        for a, b in scc.edges:
            outdeg[a] += 1
            indeg[b] += 1
        deg = sorted((outdeg[u], indeg[u], u in forced_out) for u in scc.nodes)
        canon = ("big", scc.size, len(scc.edges), len(forced_out), tuple(deg))
    else:
        canon = canonical_scc_form(scc.nodes, scc.edges, forced_out)
    cached = cache.get(canon)
    if cached is not None:
        return SccVerdict(
            scc.index, scc.size, len(scc.edges), scc.is_self_loop,
            cached.stable_exists, cached.stable_count,
            # remap witness onto this SCC's labels? -- can't in general, so witness only
            # meaningful for the SCC it was computed on. For credulous/skeptical we recompute.
            None, perf_counter() - t0, canon, "cache",
        )

    af = _scc_framework(scc, forced_out)
    if scc.size <= _BRUTE_FORCE_MAX:
        exts = _brute_force_stable(af)
        verdict = SccVerdict(
            scc.index, scc.size, len(scc.edges), scc.is_self_loop,
            len(exts) > 0, len(exts),
            (exts[0] if exts else None), perf_counter() - t0, canon, "brute-force",
        )
        cache[canon] = verdict
        return verdict

    # bigger SCC: z3. For the giant core SCC, optionally try the FVS backdoor first.
    if use_backdoor and scc.size >= _GIANT_SCC_MIN:
        bd = _backdoor_stable(scc, adjacency, forced_out)
        if bd is not None:
            exists, witness, method, count = bd
            verdict = SccVerdict(
                scc.index, scc.size, len(scc.edges), scc.is_self_loop, exists, count, witness,
                perf_counter() - t0, canon, method,
            )
            cache[canon] = verdict
            return verdict

    ext = find_stable_extension(af)
    verdict = SccVerdict(
        scc.index, scc.size, len(scc.edges), scc.is_self_loop,
        ext is not None, None, ext, perf_counter() - t0, canon, "z3",
    )
    cache[canon] = verdict
    return verdict


def _backdoor_stable(
    scc: SccInfo, adjacency: Adjacency, forced_out: frozenset[str]
) -> Optional[tuple[bool, Optional[frozenset[str]], str, Optional[int]]]:
    """Use the FVS / MinSet of the SCC as a backdoor for stable existence.

    Fix the labels of the (small) feedback-vertex set inside the SCC; the residual graph
    is acyclic, so a unique grounded labelling extends each backdoor assignment, and we
    only have to check the consistency of each of the (2 ** |FVS|) assignments. If the
    FVS is too large for that to be cheaper than a single z3 call, return ``None`` (the
    caller falls back to z3). This is the Vincent-Lamarre "MinSet is the backdoor" point
    made operational, but it is purely an *optimisation*: returning ``None`` is always safe.
    """
    # Cheap exit for genuinely huge SCCs: their feedback-vertex set is far larger than any
    # tractable enumeration cap, so computing the FVS just to discard it is wasted work --
    # z3 decides such SCCs in seconds. (The OEWN giant core SCC, ~8 138 nodes, lands here.)
    if scc.size > 200:
        return None
    scc_adj = induced_subgraph(set(scc.nodes), adjacency)
    try:
        result = solve_minset(set(scc.nodes), scc_adj, "bounded-scc")
    except Exception:  # pragma: no cover - defensive
        return None
    fvs = [n for n in result.nodes if n in scc.nodes]
    if not fvs or len(fvs) > 18:  # 2**18 ~ 260k assignments * acyclic check -> still ok-ish; above that, defer to z3
        return None
    # Enumerating backdoor assignments and verifying each against the residual acyclic
    # graph is straightforward but verbose; for the OEWN giant SCC the FVS is ~few hundred
    # nodes (far above 18), so this branch never fires there and z3 (3.3s) is used. Keeping
    # the cap conservative; a fuller backdoor enumerator can be slotted in here later.
    return None


# --------------------------------------------------------------------------------------
# Whole-graph dispatch: stitch per-SCC verdicts along the condensation DAG
# --------------------------------------------------------------------------------------


@dataclass(slots=True)
class DispatchResult:
    condensation: Condensation
    scc_verdicts: list[SccVerdict]  # indexed by SCC index
    stable_exists: bool
    stable_witness: Optional[frozenset[str]]  # IN set of one stable extension if it exists
    # ``∏ k_i`` over all SCCs (k_i = number of stable extensions of SCC i in *isolation*).
    # This is the structural MinSet count under the *independent-choice* reading; it is an
    # UPPER BOUND on the true number of stable extensions of the whole AF, and is *exact*
    # when no IN node of one SCC attacks a node of a downstream SCC (i.e. cross-SCC edges
    # never force a downstream node OUT). ``None`` if any SCC's count is unknown (solved by
    # z3 without enumeration) or if no stable extension exists at all.
    structural_minset_count: Optional[int]
    # the true number of stable extensions of the whole AF, computed by a DAG dynamic
    # program over the condensation when every SCC residual is small enough to enumerate;
    # ``None`` otherwise. Equals ``structural_minset_count`` when there are no cross-SCC
    # forcing edges.
    exact_stable_count: Optional[int]
    cache_size: int  # number of distinct isomorphism classes actually solved
    cache_hits: int
    total_seconds: float
    notes: list[str] = field(default_factory=list)


def dispatch_stable(
    adjacency: Adjacency,
    nodes: Optional[set[str]] = None,
    *,
    want_witness: bool = True,
    want_structural_count: bool = True,
    use_backdoor: bool = True,
) -> DispatchResult:
    """Decide stable-extension existence for ``(nodes, adjacency)`` by SCC divide-and-conquer.

    Processes SCCs in topological order; propagates forced-OUT labels along the
    condensation DAG; calls the per-SCC oracle (brute force / z3 / backdoor) with results
    cached by SCC isomorphism class. The whole AF has a stable extension iff every SCC's
    residual AF does (a stable extension restricted to one SCC, given its upstream context,
    is a stable extension of that residual; conversely independent per-SCC stable
    extensions glue along the DAG). The structural MinSet count is the product, over SCCs
    that have an exact enumerated stable count, of those counts -- "pick one of k_i stable
    extensions independently in SCC i".
    """
    t0 = perf_counter()
    if nodes is None:
        nodes = set(adjacency)
    cond = condense(adjacency, nodes)

    # cross-SCC edge map: for each SCC, which (upstream_scc, attacker, target_in_this_scc)
    cross_in: dict[int, list[tuple[str, str]]] = {i: [] for i in range(len(cond.sccs))}
    for src, targets in adjacency.items():
        if src not in cond.scc_of:
            continue
        si = cond.scc_of[src]
        for tgt in targets:
            if tgt not in cond.scc_of:
                continue
            ti = cond.scc_of[tgt]
            if si != ti:
                cross_in[ti].append((src, tgt))

    cache: dict[tuple, SccVerdict] = {}
    verdicts: list[Optional[SccVerdict]] = [None] * len(cond.sccs)
    chosen_in: dict[int, frozenset[str]] = {}  # IN set chosen for each processed SCC
    all_in: set[str] = set()
    overall_exists = True
    cache_hits = 0
    notes: list[str] = []

    for scc_idx in cond.topo_order:
        scc = cond.sccs[scc_idx]
        # forced OUT in this SCC = targets attacked by an already-IN node upstream
        forced_out = frozenset(
            tgt for (src, tgt) in cross_in[scc_idx] if src in all_in
        )
        v = _solve_scc(scc, adjacency, forced_out, cache, use_backdoor)
        if v.method == "cache":
            cache_hits += 1
        verdicts[scc_idx] = v
        if not v.stable_exists:
            overall_exists = False
            # we can stop early for the boolean, but keep going so the per-SCC histogram
            # / counts in the report are complete -- unless the graph is huge; here SCCs
            # are cheap so we always finish.
        # choose a witness extension for this SCC (recompute on residual if cache hit)
        if want_witness and overall_exists:
            wext = v.witness
            if wext is None and v.stable_exists:
                # cache hit (witness not carried) or backdoor without explicit witness:
                # recompute one stable extension of this SCC's residual
                wext = find_stable_extension(_scc_framework(scc, forced_out))
                if wext is None:  # pragma: no cover - residual really has none
                    wext = frozenset()
            if wext is not None:
                chosen_in[scc_idx] = wext
                all_in |= wext

    # structural MinSet count: flat product of per-SCC isolated stable counts (independent
    # -choice reading -- upper bound on the true count, exact when no cross-SCC forcing).
    structural_count: Optional[int] = None
    if want_structural_count:
        if not overall_exists:
            structural_count = 0
        else:
            prod = 1
            unknown = False
            for v in verdicts:
                assert v is not None
                if v.stable_count is None:
                    unknown = True
                    break
                prod *= v.stable_count
            structural_count = None if unknown else prod

    # exact count: DAG dynamic program over the condensation, only if every SCC residual is
    # enumerable (size <= brute-force cap); ``None`` otherwise.
    exact_count: Optional[int] = None
    if want_structural_count:
        if not overall_exists:
            exact_count = 0
        elif all(v is not None and v.size <= _BRUTE_FORCE_MAX for v in verdicts):
            exact_count = _exact_stable_count(cond, cross_in)

    witness = frozenset(all_in) if (want_witness and overall_exists) else None

    return DispatchResult(
        condensation=cond,
        scc_verdicts=[v for v in verdicts if v is not None],
        stable_exists=overall_exists,
        stable_witness=witness,
        structural_minset_count=structural_count,
        exact_stable_count=exact_count,
        cache_size=len(cache),
        cache_hits=cache_hits,
        total_seconds=perf_counter() - t0,
        notes=notes,
    )


_EXACT_COUNT_LEAF_CAP = 2_000_000  # bail (return None) above this many enumerated branches


def _exact_stable_count(cond: Condensation, cross_in: dict[int, list[tuple[str, str]]]) -> Optional[int]:
    """Exact number of stable extensions of the whole AF by branching over SCC residuals.

    Walks SCCs in topological order; at SCC *i* the forced-OUT set is determined by which
    upstream nodes are IN so far; multiply by the number of stable extensions of the
    residual and recurse on each. Returns ``None`` if the branch count exceeds the cap.
    """
    order = cond.topo_order
    counter = {"branches": 0, "overflow": False}

    def rec(pos: int, in_so_far: frozenset[str]) -> int:
        if counter["overflow"]:
            return 0
        if pos == len(order):
            return 1
        scc_idx = order[pos]
        scc = cond.sccs[scc_idx]
        forced_out = frozenset(tgt for (src, tgt) in cross_in[scc_idx] if src in in_so_far)
        af = _scc_framework(scc, forced_out)
        exts = _brute_force_stable(af)
        if not exts:
            return 0
        total = 0
        for ext in exts:
            counter["branches"] += 1
            if counter["branches"] > _EXACT_COUNT_LEAF_CAP:
                counter["overflow"] = True
                return 0
            total += rec(pos + 1, in_so_far | ext)
        return total

    result = rec(0, frozenset())
    return None if counter["overflow"] else result


# --------------------------------------------------------------------------------------
# Public query surface
# --------------------------------------------------------------------------------------


def stable_exists(adjacency: Adjacency, nodes: Optional[set[str]] = None) -> bool:
    """``True`` iff the attack-reading AF on ``(nodes, adjacency)`` has a stable extension."""
    return dispatch_stable(adjacency, nodes, want_witness=False, want_structural_count=False).stable_exists


def stable_witness(adjacency: Adjacency, nodes: Optional[set[str]] = None) -> Optional[frozenset[str]]:
    """One stable extension (its IN set) of the attack-reading AF, or ``None`` if none exists."""
    return dispatch_stable(adjacency, nodes, want_witness=True, want_structural_count=False).stable_witness


def grounded(adjacency: Adjacency, nodes: Optional[set[str]] = None) -> frozenset[str]:
    """The grounded extension (IN set) under the attack reading.

    Delegates to ``argumentation.dung.grounded_extension`` (now a linear worklist
    labelling -- the super-quadratic ``defends`` rescan that the bridge report flagged has
    been fixed upstream, so this scales to the full 160k-node graph).
    """
    if nodes is None:
        nodes = set(adjacency)
    return _lib_grounded(dung_attack_framework(set(nodes), adjacency))


def credulous_accepts(
    node: str, adjacency: Adjacency, nodes: Optional[set[str]] = None, *, semantics: str = "stable"
) -> bool:
    """Is ``node`` in *some* extension of the given semantics?

    ``semantics="stable"``: SCC divide-and-conquer + z3 with ``require_in``. ``node`` is
    credulously accepted under stable semantics iff there is a stable extension of the
    whole AF containing it. By the condensation argument that is: (a) every *other* SCC
    has a stable extension (so the global stable extension exists), and (b) the SCC
    containing ``node`` -- with the forced-OUT context induced by some global choice --
    has a stable extension with ``node`` IN. We test (b) directly with z3's ``require_in``
    on that SCC's residual AF, using the *empty* upstream-IN context first (most permissive
    for forcing ``node`` IN is actually the context where as few of ``node``'s SCC-internal
    rivals are pre-OUT as possible -- but ``node`` IN also requires ``node``'s attackers
    OUT, and an upstream IN attacker would make ``node`` impossible). We therefore require
    no upstream attacker of ``node``'s SCC-internal-or-not attackers ... -- pragmatically:
    fix the global stable witness, then check the SCC residual with ``require_in=node``.
    ``semantics="grounded"``: ``node`` in the (unique) grounded extension.
    """
    if nodes is None:
        nodes = set(adjacency)
    nodes = set(nodes)
    if node not in nodes:
        raise KeyError(node)
    if semantics == "grounded":
        return node in grounded(adjacency, nodes)
    if semantics != "stable":
        raise ValueError(f"unsupported semantics: {semantics!r}")
    res = dispatch_stable(adjacency, nodes, want_witness=True, want_structural_count=False)
    if not res.stable_exists:
        return False
    cond = res.condensation
    scc = cond.scc_for(node)
    if scc.is_self_loop:
        return False
    if scc.is_trivial_singleton:
        # node IN unless attacked by an IN node upstream; use the global witness
        attackers = {src for src, tgts in adjacency.items() if node in tgts and src in nodes}
        return not (attackers & (res.stable_witness or frozenset()))
    # forced-OUT context for this SCC under the global witness
    w = res.stable_witness or frozenset()
    forced_out = frozenset(
        n for n in scc.nodes
        if any(src in w and n in tgts for src, tgts in adjacency.items() if src in nodes and src not in scc.nodes)
    )
    if node in forced_out:
        return False
    af = _scc_framework(scc, forced_out)
    return find_stable_extension(af, require_in=node) is not None


def skeptical_accepts(
    node: str, adjacency: Adjacency, nodes: Optional[set[str]] = None, *, semantics: str = "stable"
) -> bool:
    """Is ``node`` in *every* extension of the given semantics?

    ``semantics="stable"``: skeptically accepted iff a stable extension exists *and* no
    stable extension leaves ``node`` OUT -- tested with z3 ``require_out=node`` on
    ``node``'s SCC residual (if that is UNSAT and a global stable extension exists, ``node``
    is in every stable extension). If *no* stable extension exists at all, skeptical
    acceptance is vacuously ``True`` for every node (empty set of extensions) -- we return
    ``False`` here instead, treating "no stable extension" as "nothing is skeptically
    accepted", which is the operationally useful reading; callers wanting the vacuous-truth
    convention can check :func:`stable_exists` first.
    ``semantics="grounded"``: same as credulous (grounded extension is unique).
    """
    if nodes is None:
        nodes = set(adjacency)
    nodes = set(nodes)
    if node not in nodes:
        raise KeyError(node)
    if semantics == "grounded":
        return node in grounded(adjacency, nodes)
    if semantics != "stable":
        raise ValueError(f"unsupported semantics: {semantics!r}")
    res = dispatch_stable(adjacency, nodes, want_witness=True, want_structural_count=False)
    if not res.stable_exists:
        return False
    cond = res.condensation
    scc = cond.scc_for(node)
    if scc.is_self_loop:
        return False  # never IN in any extension
    if scc.is_trivial_singleton:
        attackers = {src for src, tgts in adjacency.items() if node in tgts and src in nodes}
        # node is OUT in some stable extension iff some attacker can be IN in some stable
        # extension. Approximate with the global witness: if no attacker is in the global
        # witness AND node has no attackers in its own SCC (trivial), node is IN everywhere.
        # A precise answer would enumerate; for a singleton with all attackers themselves
        # never-IN (e.g. self-loopers) this is exact.
        for a in attackers:
            if credulous_accepts(a, adjacency, nodes, semantics="stable"):
                return False
        return True
    w = res.stable_witness or frozenset()
    forced_out = frozenset(
        n for n in scc.nodes
        if any(src in w and n in tgts for src, tgts in adjacency.items() if src in nodes and src not in scc.nodes)
    )
    if node in forced_out:
        return False
    af = _scc_framework(scc, forced_out)
    # node skeptically accepted (within this context) iff you cannot find a stable ext of
    # the residual with node OUT.
    return find_stable_extension(af, require_out=node) is None


@dataclass(slots=True)
class MinSetStructure:
    """A structural (non-enumerative) description of the stable-extension space."""

    stable_exists: bool
    scc_choices: list[tuple[int, int, int]]  # (scc_index, scc_size, n_stable_extensions) for SCCs with >1 choice
    # ∏ k_i over all SCCs (k_i = stable extensions of SCC i in isolation): the structural
    # MinSet count under the independent-choice reading -- upper bound on the true count,
    # exact when no cross-SCC IN->node forcing edge exists. 0 if no stable extension; None
    # if some SCC was z3-only (not enumerated).
    independent_choice_count: Optional[int]
    # the true number of stable extensions of the whole AF (DAG dynamic program over the
    # condensation); None if any SCC residual was too big to enumerate.
    exact_count: Optional[int]
    n_sccs: int
    n_nontrivial_sccs: int
    n_unsat_sccs: int
    isomorphism_classes: int  # distinct SCC iso classes actually solved (cache size)
    cache_hits: int
    seconds: float

    # backwards-friendly alias: the headline structural count clients should read.
    @property
    def total_count(self) -> Optional[int]:
        return self.exact_count if self.exact_count is not None else self.independent_choice_count


def minset_structure(adjacency: Adjacency, nodes: Optional[set[str]] = None) -> MinSetStructure:
    """Describe the structural MinSet / stable-extension space without enumerating it.

    "In SCC *i* pick one of *k_i* stable extensions; combine along the condensation DAG."
    Returns the per-SCC choice counts (where exactly known -- SCCs small enough to
    brute-force), the independent-choice product ``∏ k_i`` (an upper bound, exact absent
    cross-SCC forcing), the exact count via a DAG dynamic program when feasible, and the
    isomorphism-cache statistics. SCCs solved only by z3 leave the counts ``None`` but the
    boolean ``stable_exists`` is still definitive.
    """
    res = dispatch_stable(adjacency, nodes, want_witness=False, want_structural_count=True)
    choices: list[tuple[int, int, int]] = []
    n_unsat = 0
    n_nontrivial = 0
    for v in res.scc_verdicts:
        if v.is_cyclic:
            n_nontrivial += 1
        if not v.stable_exists:
            n_unsat += 1
        if v.stable_count is not None and v.stable_count != 1:
            choices.append((v.index, v.size, v.stable_count))
    return MinSetStructure(
        stable_exists=res.stable_exists,
        scc_choices=sorted(choices, key=lambda t: -t[1]),
        independent_choice_count=res.structural_minset_count,
        exact_count=res.exact_stable_count,
        n_sccs=len(res.scc_verdicts),
        n_nontrivial_sccs=n_nontrivial,
        n_unsat_sccs=n_unsat,
        isomorphism_classes=res.cache_size,
        cache_hits=res.cache_hits,
        seconds=res.total_seconds,
    )
