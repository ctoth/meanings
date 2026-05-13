"""Smoke tests for :mod:`meanings.argumentation_dispatch`.

Tiny graphs with obvious answers; the dispatcher's verdicts are also checked against
the ``argumentation`` library run directly (``stable_extensions`` / ``grounded_extension``).
"""

from __future__ import annotations

from argumentation.dung import grounded_extension as lib_grounded, stable_extensions as lib_stable

from meanings.argumentation_bridge import dung_attack_framework
from meanings.argumentation_dispatch import (
    canonical_scc_form,
    condense,
    credulous_accepts,
    dispatch_stable,
    grounded,
    minset_structure,
    skeptical_accepts,
    stable_exists,
    stable_witness,
)


def _lib_has_stable(adj):
    nodes = set(adj)
    return len(list(lib_stable(dung_attack_framework(nodes, adj)))) > 0


def _lib_stable_count(adj):
    nodes = set(adj)
    return len(list(lib_stable(dung_attack_framework(nodes, adj))))


# --- the graphs -------------------------------------------------------------------

DAG = {"a": {"b"}, "b": {"c"}, "c": set()}  # acyclic chain a->b->c
TWO_CYCLE = {"x": {"y"}, "y": {"x"}}  # even cycle: two stable extensions {x},{y}
THREE_CYCLE = {"p": {"q"}, "q": {"r"}, "r": {"p"}}  # odd cycle: no stable extension
TWO_SCCS_CHAIN = {"a": {"b"}, "b": {"a"}, "a2": {"b2"}, "b2": {"a2"}, "a": {"a2", "b"}}  # built below
SELF_LOOP = {"s": {"s"}}  # word in its own gloss


def two_sccs_chain():
    # SCC1 = {a,b} 2-cycle; SCC2 = {c,d} 2-cycle; cross edge a -> c.
    return {"a": {"b", "c"}, "b": {"a"}, "c": {"d"}, "d": {"c"}}


# --- condensation -----------------------------------------------------------------


def test_condense_dag_all_singletons():
    cond = condense(DAG)
    assert len(cond.sccs) == 3
    assert all(s.size == 1 for s in cond.sccs)
    assert all(s.is_trivial_singleton for s in cond.sccs)
    # topological order: a before b before c
    rank = {n: cond.scc_for(n).topo_rank for n in DAG}
    assert rank["a"] < rank["b"] < rank["c"]


def test_condense_two_cycle_is_one_scc():
    cond = condense(TWO_CYCLE)
    assert len(cond.sccs) == 1
    assert cond.sccs[0].size == 2
    assert not cond.sccs[0].is_self_loop


def test_condense_self_loop():
    cond = condense(SELF_LOOP)
    assert len(cond.sccs) == 1
    assert cond.sccs[0].is_self_loop
    assert not cond.sccs[0].is_trivial_singleton


def test_condense_two_sccs_chain():
    cond = condense(two_sccs_chain())
    assert len(cond.sccs) == 2
    sizes = sorted(s.size for s in cond.sccs)
    assert sizes == [2, 2]
    # SCC of {a,b} is upstream of SCC of {c,d}
    assert cond.scc_for("a").topo_rank < cond.scc_for("c").topo_rank


# --- stable existence -------------------------------------------------------------


def test_stable_dag():
    # acyclic: unique stable extension exists (= grounded), so stable_exists True
    assert stable_exists(DAG) is True
    assert _lib_has_stable(DAG) is True
    w = stable_witness(DAG)
    assert w == frozenset({"a", "c"})  # a IN, b OUT, c IN
    assert frozenset(w) in set(lib_stable(dung_attack_framework(set(DAG), DAG)))


def test_stable_two_cycle():
    assert stable_exists(TWO_CYCLE) is True
    assert _lib_has_stable(TWO_CYCLE) is True
    w = stable_witness(TWO_CYCLE)
    assert w in (frozenset({"x"}), frozenset({"y"}))


def test_stable_three_cycle_none():
    assert stable_exists(THREE_CYCLE) is False
    assert _lib_has_stable(THREE_CYCLE) is False
    assert stable_witness(THREE_CYCLE) is None


def test_stable_self_loop_none():
    assert stable_exists(SELF_LOOP) is False
    assert _lib_has_stable(SELF_LOOP) is False


def test_stable_two_sccs_chain():
    g = two_sccs_chain()
    assert stable_exists(g) is True
    assert _lib_has_stable(g) is True
    w = stable_witness(g)
    # w must be a genuine stable extension per the library
    assert frozenset(w) in set(lib_stable(dung_attack_framework(set(g), g)))


# --- grounded ---------------------------------------------------------------------


def test_grounded_matches_library():
    for g in (DAG, TWO_CYCLE, THREE_CYCLE, SELF_LOOP, two_sccs_chain()):
        assert grounded(g) == lib_grounded(dung_attack_framework(set(g), g))


def test_grounded_dag_value():
    assert grounded(DAG) == frozenset({"a", "c"})


def test_grounded_cycles_empty():
    assert grounded(TWO_CYCLE) == frozenset()
    assert grounded(THREE_CYCLE) == frozenset()
    assert grounded(SELF_LOOP) == frozenset()


# --- credulous / skeptical --------------------------------------------------------


def test_credulous_grounded():
    assert credulous_accepts("a", DAG, semantics="grounded") is True
    assert credulous_accepts("b", DAG, semantics="grounded") is False
    assert credulous_accepts("c", DAG, semantics="grounded") is True


def test_credulous_stable_two_cycle():
    # both x and y are credulously (but not skeptically) accepted
    assert credulous_accepts("x", TWO_CYCLE, semantics="stable") is True
    assert credulous_accepts("y", TWO_CYCLE, semantics="stable") is True
    assert skeptical_accepts("x", TWO_CYCLE, semantics="stable") is False
    assert skeptical_accepts("y", TWO_CYCLE, semantics="stable") is False


def test_credulous_stable_three_cycle_all_false():
    for n in THREE_CYCLE:
        assert credulous_accepts(n, THREE_CYCLE, semantics="stable") is False
        assert skeptical_accepts(n, THREE_CYCLE, semantics="stable") is False


def test_self_loop_never_accepted():
    assert credulous_accepts("s", SELF_LOOP, semantics="stable") is False
    assert skeptical_accepts("s", SELF_LOOP, semantics="stable") is False


def test_skeptical_dag_chain():
    # unique stable extension {a, c}; so a and c skeptically accepted, b not.
    assert skeptical_accepts("a", DAG, semantics="stable") is True
    assert skeptical_accepts("c", DAG, semantics="stable") is True
    assert skeptical_accepts("b", DAG, semantics="stable") is False


# --- structural MinSet count ------------------------------------------------------


def test_minset_structure_two_cycle():
    ms = minset_structure(TWO_CYCLE)
    assert ms.stable_exists is True
    assert ms.total_count == 2 == _lib_stable_count(TWO_CYCLE)
    assert any(size == 2 and k == 2 for (_, size, k) in ms.scc_choices)


def test_minset_structure_two_independent_cycles():
    # two disjoint 2-cycles -> 2 * 2 = 4 stable extensions
    g = {"a": {"b"}, "b": {"a"}, "c": {"d"}, "d": {"c"}}
    ms = minset_structure(g)
    assert ms.stable_exists is True
    assert ms.total_count == 4 == _lib_stable_count(g)


def test_minset_structure_dag_only_one():
    ms = minset_structure(DAG)
    assert ms.stable_exists is True
    assert ms.total_count == 1 == _lib_stable_count(DAG)


def test_minset_structure_unsat():
    ms = minset_structure(THREE_CYCLE)
    assert ms.stable_exists is False
    assert ms.total_count == 0
    assert ms.exact_count == 0
    assert ms.n_unsat_sccs >= 1


def test_minset_structure_chain_of_sccs():
    g = two_sccs_chain()
    ms = minset_structure(g)
    assert ms.stable_exists is True
    # the dispatcher's product should equal the library's actual stable-extension count
    assert ms.total_count == _lib_stable_count(g)


# --- isomorphism canonical form ---------------------------------------------------


def test_canonical_form_two_cycles_match():
    a = condense({"a": {"b"}, "b": {"a"}}).sccs[0]
    b = condense({"p": {"q"}, "q": {"p"}}).sccs[0]
    assert canonical_scc_form(a.nodes, a.edges) == canonical_scc_form(b.nodes, b.edges)


def test_canonical_form_distinguishes_2_and_3_cycles():
    a = condense({"a": {"b"}, "b": {"a"}}).sccs[0]
    c = condense({"p": {"q"}, "q": {"r"}, "r": {"p"}}).sccs[0]
    assert canonical_scc_form(a.nodes, a.edges) != canonical_scc_form(c.nodes, c.edges)


# --- context-dependent (regression for audit finding 1) --------------------------


# upstream 2-cycle a<->b (stable exts {a},{b}); downstream 3-cycle x->y->z->x (UNSAT in
# isolation); cross edge b->x. The whole AF IS stable-SAT: choosing {b} forces x OUT, the
# residual 2-path y->z is SAT ({y}), giving global stable {b,y}. The greedy sweep may pick
# {a} first (x not forced out -> residual 3-cycle UNSAT) -- the dispatcher must NOT clamp to
# UNSAT but fall through to the exact DAG-DP.
CONTEXT_DEP_SAT = {"a": {"b"}, "b": {"a", "x"}, "x": {"y"}, "y": {"z"}, "z": {"x"}}
# same upstream/downstream but NO cross edge into the cycle -> genuinely UNSAT.
CONTEXT_DEP_UNSAT = {"a": {"b"}, "b": {"a"}, "x": {"y"}, "y": {"z"}, "z": {"x"}}
# two upstream 2-cycles; downstream 3-cycle; either b or d (cross b->x, d->x) unblocks -> SAT.
CONTEXT_DEP_EITHER = {
    "a": {"b"}, "b": {"a", "x"}, "c": {"d"}, "d": {"c", "x"},
    "x": {"y"}, "y": {"z"}, "z": {"x"},
}


def _is_stable_ext(adj, S):
    nodes = set(adj)
    for t in adj.values():
        nodes |= set(t)
    defeats = {(a, b) for a, tg in adj.items() for b in tg}
    if any((a, b) in defeats for a in S for b in S):
        return False
    return all(any((a, x) in defeats for a in S) for x in nodes if x not in S)


def test_context_dependent_stable_sat():
    # ground truth via the library
    assert _lib_has_stable(CONTEXT_DEP_SAT) is True
    assert stable_exists(CONTEXT_DEP_SAT) is True
    w = stable_witness(CONTEXT_DEP_SAT)
    assert w is not None and _is_stable_ext(CONTEXT_DEP_SAT, set(w))
    assert frozenset(w) in set(lib_stable(dung_attack_framework(set(CONTEXT_DEP_SAT), CONTEXT_DEP_SAT)))
    res = dispatch_stable(CONTEXT_DEP_SAT)
    assert res.stable_exists is True
    assert res.exact_stable_count == _lib_stable_count(CONTEXT_DEP_SAT)


def test_context_dependent_stable_genuinely_unsat():
    assert _lib_has_stable(CONTEXT_DEP_UNSAT) is False
    assert stable_exists(CONTEXT_DEP_UNSAT) is False
    assert stable_witness(CONTEXT_DEP_UNSAT) is None
    assert dispatch_stable(CONTEXT_DEP_UNSAT).exact_stable_count == 0


def test_context_dependent_either_unblocks():
    assert stable_exists(CONTEXT_DEP_EITHER) is True
    w = stable_witness(CONTEXT_DEP_EITHER)
    assert w is not None and _is_stable_ext(CONTEXT_DEP_EITHER, set(w))
    assert dispatch_stable(CONTEXT_DEP_EITHER).exact_stable_count == _lib_stable_count(CONTEXT_DEP_EITHER)


def test_context_dependent_credulous_skeptical_match_library():
    for adj in (CONTEXT_DEP_SAT, CONTEXT_DEP_UNSAT, CONTEXT_DEP_EITHER):
        exts = set(lib_stable(dung_attack_framework(set(adj), adj)))
        nodes = set(adj)
        for t in adj.values():
            nodes |= set(t)
        for n in nodes:
            cred_expected = any(n in e for e in exts)
            skept_expected = bool(exts) and all(n in e for e in exts)
            assert credulous_accepts(n, adj, semantics="stable") is cred_expected, (adj, n)
            assert skeptical_accepts(n, adj, semantics="stable") is skept_expected, (adj, n)


def test_iso_cache_dedup_in_dispatch():
    # four identical disjoint 2-cycles -> one iso class solved, three cache hits
    g = {}
    for i in range(4):
        g[f"x{i}"] = {f"y{i}"}
        g[f"y{i}"] = {f"x{i}"}
    res = dispatch_stable(g)
    assert res.stable_exists is True
    assert res.cache_size == 1
    assert res.cache_hits == 3
    assert res.structural_minset_count == 2 ** 4
