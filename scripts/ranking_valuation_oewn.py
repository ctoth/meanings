"""Ranking-based-semantics valuation of the OEWN definition digraph.

Connection #6 from ``reports/sibling-tools-connection.md``: the non-degenerate
replacement for the reverse-PageRank attempt that collapsed to out-degree
(``reports/spectral-valuation-oewn.md``). Run the gradual / ranking-based
semantics from ``argumentation.ranking`` over the ``paper-wordnet`` definition
digraph (as a Dung attack framework, both orientations) and ask: does any
ranking semantics add real signal *over* ``log(out-degree)`` for predicting the
psycholinguistic norms?

Edge convention in the meanings digraph: ``u -> v`` = "u occurs in the
definition (gloss) of v".

Two orientations, mirroring the spectral report:

* **forward / "definability"** -- attack reading ``u -> v`` = "u attacks v".
  Then ``attackers[v]`` = the words occurring in v's gloss (in-neighbours). A
  ranking semantics here rewards words with FEW / weak definiens: "how
  self-contained is this word's definition". This is the in-degree side.
* **reverse / "foundational productivity"** -- attack reading on the TRANSPOSE,
  i.e. ``v -> u`` = "v attacks u" so ``attackers[u]`` = the words u occurs in
  (out-neighbours). A ranking semantics here rewards words that are USED in many
  / important glosses: "how foundational is this word". This is the out-degree
  side -- the orientation reverse-PageRank used, and the one to put against
  ``log(out-degree)``.

Semantics run: h-categoriser, categoriser (Besnard-Hunter), burden numbers,
counting (damped). h-categoriser and burden are the ones the task named first.

Outputs ``reports/ranking-valuation-oewn.json`` and a console summary; the
companion writeup is ``reports/ranking-valuation-oewn.md``.

Run: ``uv run python scripts/ranking_valuation_oewn.py``
"""
from __future__ import annotations

import json
import math
import os
import pickle
import time
from pathlib import Path

from argumentation.dung import ArgumentationFramework
from argumentation.ranking import (
    burden_numbers,
    categoriser_scores,
    counting_ranking,
    h_categoriser_ranking,
)

from meanings.annotations import load_annotation_csvs
from meanings.graph_analysis import analyze_kernel, induced_subgraph
from meanings.wordnet_pipeline import build_paper_wordnet_graph

REPO = Path(__file__).resolve().parents[1]
PSYCH_DIR = REPO / "data" / "psycholinguistic"
OUT_JSON = REPO / "reports" / "ranking-valuation-oewn.json"
CACHE = REPO / "scratch" / "ranking_valuation_graph_cache.pkl"

PSYCH_FIELDS = ("frequency", "age_of_acquisition", "concreteness")
SEED_METHOD = "exact-small-greedy"
CORE_POLICY = "source-union"
LEXICON = "oewn:2024"

# ranking semantics are O(edges) per iteration in pure Python; on the 678k-edge
# full digraph one iteration is several seconds, and h-categoriser / counting can
# need O(diameter) iterations to hit tol 1e-9, which is impractical here. We CAP
# the iteration count on the full graph and let the library's ``converged=False``
# flag carry the truth; the kernel subgraph (~18k nodes) we run to convergence.
# (The cap is generous: by 60 iterations the categoriser family has long since
# stabilised at the precision that matters for a ranking.)
H_MAX_ITER_FULL = 25
COUNTING_MAX_ITER_FULL = 25
H_MAX_ITER_KERNEL = 5000
COUNTING_MAX_ITER_KERNEL = 5000
BURDEN_ITERS = 30
SKIP_FULL = bool(os.environ.get("RV_SKIP_FULL"))


# --------------------------------------------------------------------------- #
# stats helpers (pure python; the project venv has numpy but we keep this leaf
# dependency-light and consistent with spectral_analysis.spearman)
# --------------------------------------------------------------------------- #
def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        return float("nan")
    ra, rb = _ranks(a), _ranks(b)
    n = len(ra)
    ma = sum(ra) / n
    mb = sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    if da == 0 or db == 0:
        return float("nan")
    return num / (da * db)


def pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        return float("nan")
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return float("nan")
    return num / (da * db)


def overlap_at_k(score_a: dict[str, float], score_b: dict[str, float], k: int,
                 a_high_is_better: bool, b_high_is_better: bool) -> float:
    keys = set(score_a) & set(score_b)
    sa = sorted(keys, key=lambda x: score_a[x], reverse=a_high_is_better)[:k]
    sb = sorted(keys, key=lambda x: score_b[x], reverse=b_high_is_better)[:k]
    inter = len(set(sa) & set(sb))
    union = len(set(sa) | set(sb))
    return inter / union if union else 0.0


def ols_r2(X: list[list[float]], y: list[float]) -> float:
    """In-sample R^2 of OLS with intercept. X is rows of feature vectors (no
    intercept column). Pure-python normal-equation solve via Gaussian elim."""
    n = len(y)
    if n == 0:
        return 0.0
    k = len(X[0]) if X and X[0] else 0
    # design with intercept
    D = [[1.0] + list(row) for row in X] if k else [[1.0] for _ in range(n)]
    p = k + 1
    # normal equations: (D^T D) beta = D^T y
    A = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for i in range(n):
        di = D[i]
        yi = y[i]
        for r in range(p):
            b[r] += di[r] * yi
            for c in range(p):
                A[r][c] += di[r] * di[c]
    # solve A beta = b
    for col in range(p):
        # pivot
        piv = max(range(col, p), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            continue
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        pv = A[col][col]
        for c in range(col, p):
            A[col][c] /= pv
        b[col] /= pv
        for r in range(p):
            if r == col:
                continue
            f = A[r][col]
            if f == 0:
                continue
            for c in range(col, p):
                A[r][c] -= f * A[col][c]
            b[r] -= f * b[col]
    beta = b
    ss_res = 0.0
    ymean = sum(y) / n
    ss_tot = sum((yi - ymean) ** 2 for yi in y)
    for i in range(n):
        pred = sum(beta[j] * D[i][j] for j in range(p))
        ss_res += (y[i] - pred) ** 2
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


# --------------------------------------------------------------------------- #
def transpose(adj: dict[str, set[str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for u, ts in adj.items():
        out.setdefault(u, set())
        for t in ts:
            out.setdefault(t, set()).add(u)
    return out


def edges_of(adj: dict[str, set[str]], nodes: set[str]) -> frozenset[tuple[str, str]]:
    return frozenset(
        (u, v) for u, ts in adj.items() if u in nodes for v in ts if v in nodes
    )


def make_af(nodes: set[str], adj: dict[str, set[str]]) -> ArgumentationFramework:
    """Dung AF under attack reading: edge (u,v) in adj == "u attacks v"."""
    return ArgumentationFramework(arguments=frozenset(nodes), defeats=edges_of(adj, nodes))


def run_semantics(af: ArgumentationFramework, label: str, *, h_iter: int, counting_iter: int) -> dict[str, dict]:
    out: dict[str, dict] = {}
    n_args = len(af.arguments)
    n_atk = len(af.defeats)
    print(f"  [{label}] AF: {n_args} args, {n_atk} attacks", flush=True)

    t = time.time()
    r = h_categoriser_ranking(af, max_iterations=h_iter)
    out["h_categoriser"] = {"scores": r.scores, "converged": r.converged,
                            "iterations": r.iterations, "higher_is_better": True}
    print(f"  [{label}] h_categoriser: {time.time()-t:.1f}s conv={r.converged} iter={r.iterations}", flush=True)

    t = time.time()
    r = categoriser_scores(af, max_iterations=h_iter)
    out["categoriser"] = {"scores": r.scores, "converged": r.converged,
                          "iterations": r.iterations, "higher_is_better": True}
    print(f"  [{label}] categoriser: {time.time()-t:.1f}s conv={r.converged} iter={r.iterations}", flush=True)

    t = time.time()
    r = burden_numbers(af, iterations=BURDEN_ITERS)
    # burden: lower is more acceptable
    out["burden"] = {"scores": r.scores, "converged": r.converged,
                     "iterations": r.iterations, "higher_is_better": False}
    print(f"  [{label}] burden: {time.time()-t:.1f}s iter={r.iterations}", flush=True)

    t = time.time()
    r = counting_ranking(af, damping=0.98, max_iterations=counting_iter)
    out["counting"] = {"scores": r.scores, "converged": r.converged,
                       "iterations": r.iterations, "higher_is_better": True}
    print(f"  [{label}] counting: {time.time()-t:.1f}s conv={r.converged} iter={r.iterations}", flush=True)
    return out


def topk_words(scores: dict[str, float], higher_is_better: bool, k: int = 20) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=higher_is_better)[:k]


def _build_and_analyze():
    """Build the paper-wordnet graph + kernel analysis; cache to disk so reruns
    of the (slow) semantics part don't pay the ~5min graph build again."""
    if CACHE.exists():
        print(f"loading cached graph + analysis from {CACHE} ...", flush=True)
        with CACHE.open("rb") as fh:
            return pickle.load(fh)
    print(f"building paper-wordnet graph ({LEXICON})...", flush=True)
    t = time.time()
    build = build_paper_wordnet_graph(LEXICON)
    nodes = set(build.nodes)
    adj = {u: set(ts) for u, ts in build.adjacency.items()}
    for n in nodes:
        adj.setdefault(n, set())
    print(f"  nodes={len(nodes)} edges={sum(len(v) for v in adj.values())}  ({time.time()-t:.0f}s)", flush=True)
    print(f"kernel analysis (seed={SEED_METHOD}, core={CORE_POLICY})...", flush=True)
    t = time.time()
    analysis = analyze_kernel(nodes, adj, seed_method=SEED_METHOD, core_policy=CORE_POLICY)
    print(f"  kernel={len(analysis.kernel_nodes)} core={len(analysis.core_nodes)} "
          f"sats={len(analysis.satellite_nodes)} seed={len(analysis.seed_nodes)} "
          f"layers_for={len(analysis.layer_by_node)} residual_cyclic_scc={analysis.residual_cyclic_scc_count} "
          f"({time.time()-t:.0f}s)", flush=True)
    payload = {
        "nodes": nodes, "adj": adj,
        "kernel": analysis.kernel_nodes, "core": analysis.core_nodes,
        "seed": set(analysis.seed_nodes), "layer_by_node": dict(analysis.layer_by_node),
        "satellites": analysis.satellite_nodes,
        "residual_cyclic_scc_count": analysis.residual_cyclic_scc_count,
        "pos_by_node": dict(getattr(build, "pos_by_node", {}) or {}),
    }
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE.open("wb") as fh:
        pickle.dump(payload, fh)
    print(f"  cached -> {CACHE}", flush=True)
    return payload


def main() -> None:
    t0 = time.time()
    payload = _build_and_analyze()
    nodes = payload["nodes"]
    adj = payload["adj"]
    edges = sum(len(v) for v in adj.values())
    radj = transpose(adj)
    kernel = payload["kernel"]
    core = payload["core"]
    seed = payload["seed"]
    layer_by_node = payload["layer_by_node"]
    satellites = payload["satellites"]
    residual_cyclic_scc_count = payload["residual_cyclic_scc_count"]
    print(f"  graph: nodes={len(nodes)} edges={edges}; kernel={len(kernel)} core={len(core)} "
          f"sats={len(satellites)} seed={len(seed)} layers_for={len(layer_by_node)} "
          f"residual_cyclic_scc={residual_cyclic_scc_count}  ({time.time()-t0:.0f}s)", flush=True)

    kernel_adj = induced_subgraph(kernel, adj)
    for n in kernel:
        kernel_adj.setdefault(n, set())
    kernel_radj = transpose(kernel_adj)

    # baseline / comparison features ----------------------------------------- #
    indeg = {n: 0 for n in nodes}
    for ts in adj.values():
        for t_ in ts:
            indeg[t_] = indeg.get(t_, 0) + 1
    outdeg = {n: len(adj.get(n, ())) for n in nodes}
    # FVS heuristic key: internal_out + internal_in on the KERNEL induced subgraph
    k_indeg = {n: 0 for n in kernel}
    for ts in kernel_adj.values():
        for t_ in ts:
            if t_ in k_indeg:
                k_indeg[t_] += 1
    k_outdeg = {n: len(kernel_adj.get(n, ())) for n in kernel}
    fvs_key = {n: k_outdeg.get(n, 0) + k_indeg.get(n, 0) for n in kernel}

    # psycholinguistic norms ------------------------------------------------- #
    print("loading psycholinguistic norm CSVs...")
    csv_paths = [PSYCH_DIR / f"{f}.csv" for f in PSYCH_FIELDS]
    ann = load_annotation_csvs(csv_paths)
    print(f"  sources={ann.sources}")

    def lemma_of(node: str) -> str:
        return node.split("::", 1)[0]

    def norms_of(node: str) -> dict[str, float] | None:
        lm = lemma_of(node)
        vals = {f: ann.get(lm, f) for f in PSYCH_FIELDS}
        if any(v is None for v in vals.values()):
            return None
        return vals

    psych_nodes = {n: v for n in nodes if (v := norms_of(n)) is not None}
    psych_kernel = {n: v for n, v in psych_nodes.items() if n in kernel}
    print(f"  psych-joined: all={len(psych_nodes)} kernel={len(psych_kernel)}")

    # ----------------------------------------------------------------------- #
    # precompute comparison features once
    # ----------------------------------------------------------------------- #
    SEMS = ["h_categoriser", "categoriser", "burden", "counting"]
    log_outdeg = {n: math.log1p(outdeg[n]) for n in nodes}
    log_indeg = {n: math.log1p(indeg[n]) for n in nodes}

    pj_nodes = sorted(psych_nodes)
    base_r2 = {}
    for f in PSYCH_FIELDS:
        yf = [psych_nodes[n][f] for n in pj_nodes]
        base_r2[f] = {
            "r2_log_outdeg": ols_r2([[log_outdeg[n]] for n in pj_nodes], yf),
            "r2_log_outdeg_plus_log_indeg": ols_r2([[log_outdeg[n], log_indeg[n]] for n in pj_nodes], yf),
            "pearson_log_outdeg": pearson([log_outdeg[n] for n in pj_nodes], yf),
            "pearson_log_indeg": pearson([log_indeg[n] for n in pj_nodes], yf),
        }

    out: dict = {
        "config": {
            "lexicon": LEXICON, "seed_method": SEED_METHOD, "core_policy": CORE_POLICY,
            "h_max_iter_full": H_MAX_ITER_FULL, "h_max_iter_kernel": H_MAX_ITER_KERNEL,
            "counting_max_iter_full": COUNTING_MAX_ITER_FULL, "counting_max_iter_kernel": COUNTING_MAX_ITER_KERNEL,
            "burden_iters": BURDEN_ITERS, "skip_full": SKIP_FULL,
            "note_on_full_graph": "full-graph categoriser-family scores are iteration-capped (per-block converged flag); kernel-scope scores run to convergence. The full-graph cap is small because pure-python iteration over 678k edges is expensive; at this cap the ranking ORDER is already stable even where the absolute scores are not.",
            "psych_fields": list(PSYCH_FIELDS),
            "edge_convention": "u -> v means u occurs in the gloss of v",
            "orientations": {
                "forward": "attack reading u->v; attackers[v] = v's definiens (in-neighbours) -> 'definability'",
                "reverse": "attack reading on transpose; attackers[u] = words u occurs in (out-neighbours) -> 'foundational productivity'; the orientation reverse-PageRank used",
            },
        },
        "graph": {
            "nodes": len(nodes), "edges": edges,
            "kernel": len(kernel), "core": len(core), "satellites": len(satellites),
            "seed": len(seed), "layers_defined_for": len(layer_by_node),
            "residual_cyclic_scc_count": residual_cyclic_scc_count,
            "note": "post self-loop fix (commit 7d12e64): kernel/core/seed larger than the spectral report's older numbers (12853/288/2370)",
        },
        "psych_join": {"all_nodes": len(psych_nodes), "kernel_nodes": len(psych_kernel),
                       "all_total": len(nodes), "kernel_total": len(kernel)},
        "psych_prediction": {"baselines_full_join": {"n": len(pj_nodes), **base_r2}},
        "rankings": {},
        "headline": {},
    }
    best_incremental = {"value": -1.0, "where": None, "details": None}

    def comparison_block(scope_orient: str, sem_dict: dict[str, dict]) -> dict:
        nonlocal best_incremental
        scope = "kernel" if scope_orient.startswith("kernel") else "full"
        node_set = kernel if scope == "kernel" else nodes
        cmp_nodes = sorted(node_set)
        v_outdeg = [outdeg[n] for n in cmp_nodes]
        v_indeg = [indeg[n] for n in cmp_nodes]
        v_seed = [1.0 if n in seed else 0.0 for n in cmp_nodes]
        v_core = [1.0 if n in core else 0.0 for n in cmp_nodes]
        layer_nodes = [n for n in cmp_nodes if n in layer_by_node]
        v_layer = [layer_by_node[n] for n in layer_nodes]
        fvs_nodes = [n for n in cmp_nodes if n in fvs_key]
        v_fvs = [fvs_key[n] for n in fvs_nodes]
        pj = [n for n in cmp_nodes if n in psych_nodes]
        block: dict = {}
        for sem in SEMS:
            sc = sem_dict[sem]["scores"]
            hib = sem_dict[sem]["higher_is_better"]
            v_sc = [sc[n] for n in cmp_nodes]
            cmp = {
                "converged": sem_dict[sem]["converged"],
                "iterations": sem_dict[sem]["iterations"],
                "higher_is_better": hib,
                "rho_vs_outdeg": spearman(v_sc, v_outdeg),
                "rho_vs_indeg": spearman(v_sc, v_indeg),
                "rho_vs_seed_membership": spearman(v_sc, v_seed),
                "rho_vs_core_membership": spearman(v_sc, v_core),
                "rho_vs_fvs_degree_key": spearman([sc[n] for n in fvs_nodes], v_fvs) if fvs_nodes else None,
                "rho_vs_layer_index": spearman([sc[n] for n in layer_nodes], v_layer) if layer_nodes else None,
                "overlap_at_500_with_fvs_key": (
                    overlap_at_k({n: sc[n] for n in fvs_nodes}, {n: fvs_key[n] for n in fvs_nodes},
                                 500, hib, True) if fvs_nodes else None),
                "top20_words": [[n, sc[n]] for n, _ in topk_words(sc, hib, 20)],
            }
            if len(pj) >= 30:
                signed = [sc[n] if hib else -sc[n] for n in pj]
                psych_block: dict = {"n_psych": len(pj)}
                X0 = [[log_outdeg[n]] for n in pj]
                Xd0 = [[log_outdeg[n], log_indeg[n]] for n in pj]
                for f in PSYCH_FIELDS:
                    yf = [psych_nodes[n][f] for n in pj]
                    X1 = [[log_outdeg[n], signed[i]] for i, n in enumerate(pj)]
                    Xd1 = [[log_outdeg[n], log_indeg[n], signed[i]] for i, n in enumerate(pj)]
                    r2_0 = ols_r2(X0, yf); r2_1 = ols_r2(X1, yf)
                    r2_d0 = ols_r2(Xd0, yf); r2_d1 = ols_r2(Xd1, yf)
                    incr = r2_1 - r2_0
                    psych_block[f] = {
                        "pearson_score_norm": pearson(signed, yf),
                        "r2_log_outdeg": r2_0, "r2_log_outdeg_plus_score": r2_1,
                        "incremental_score_over_log_outdeg_r2": incr,
                        "r2_log_outdeg_plus_log_indeg": r2_d0,
                        "r2_log_outdeg_plus_log_indeg_plus_score": r2_d1,
                        "incremental_score_over_degree_r2": r2_d1 - r2_d0,
                    }
                    if incr > best_incremental["value"]:
                        best_incremental = {"value": incr, "where": f"{scope_orient}/{sem}/{f}",
                                            "details": {"scope_orient": scope_orient, "semantics": sem,
                                                        "norm": f, "r2_log_outdeg": r2_0, "r2_with_score": r2_1,
                                                        "n": len(pj)}}
                cmp["psych_prediction"] = psych_block
            block[sem] = cmp
        return block

    def write_partial(label: str) -> None:
        out["headline"] = {
            "question": "Does any ranking semantics add real signal over log(out-degree) for predicting the psycholinguistic norms?",
            "best_incremental_R2_over_log_outdeg": best_incremental,
            "interpretation_hint": (
                "Compare best_incremental_R2_over_log_outdeg.value to the spectral report's reverse-PageRank "
                "incremental-over-out-degree numbers (which were ~0). A value near 0 means 'another principled "
                "score that also collapses to degree' (negative result); a clearly positive value means it adds signal."
            ),
            "scopes_present": sorted(out["rankings"].keys()),
        }
        OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"  -> wrote partial {OUT_JSON} after {label}  ({time.time()-t0:.0f}s)", flush=True)

    # ----------------------------------------------------------------------- #
    # run ranking semantics (kernel first; persist after every scope)
    # ----------------------------------------------------------------------- #
    print("\n=== KERNEL SUBGRAPH (run to convergence) ===", flush=True)
    af_k_fwd = make_af(kernel, kernel_adj)
    r = run_semantics(af_k_fwd, "kernel/fwd", h_iter=H_MAX_ITER_KERNEL, counting_iter=COUNTING_MAX_ITER_KERNEL)
    del af_k_fwd
    out["rankings"]["kernel_forward"] = comparison_block("kernel_forward", r)
    write_partial("kernel/fwd")

    af_k_rev = make_af(kernel, kernel_radj)
    r = run_semantics(af_k_rev, "kernel/rev", h_iter=H_MAX_ITER_KERNEL, counting_iter=COUNTING_MAX_ITER_KERNEL)
    del af_k_rev
    out["rankings"]["kernel_reverse"] = comparison_block("kernel_reverse", r)
    write_partial("kernel/rev")

    if not SKIP_FULL:
        print(f"\n=== FULL DIGRAPH (iteration-capped at {H_MAX_ITER_FULL}) ===", flush=True)
        af_rev = make_af(nodes, radj)  # reverse first: it's the headline orientation
        r = run_semantics(af_rev, "full/rev", h_iter=H_MAX_ITER_FULL, counting_iter=COUNTING_MAX_ITER_FULL)
        del af_rev
        out["rankings"]["full_reverse"] = comparison_block("full_reverse", r)
        write_partial("full/rev")

        af_fwd = make_af(nodes, adj)
        r = run_semantics(af_fwd, "full/fwd", h_iter=H_MAX_ITER_FULL, counting_iter=COUNTING_MAX_ITER_FULL)
        del af_fwd
        out["rankings"]["full_forward"] = comparison_block("full_forward", r)
        write_partial("full/fwd")
    else:
        print("\n(RV_SKIP_FULL set -- skipping full-graph semantics)", flush=True)

    write_partial("FINAL")
    print(f"\nall done ({time.time()-t0:.0f}s total)", flush=True)

    # console summary
    print("\n=== SUMMARY ===")
    print(f"graph: {len(nodes)} nodes, {edges} edges; kernel {len(kernel)}, seed {len(seed)}; psych join {len(psych_nodes)}")
    print("baseline R2(log_outdeg) for norms: " + ", ".join(f"{f}={base_r2[f]['r2_log_outdeg']:.4f}" for f in PSYCH_FIELDS))
    for so in out["rankings"]:
        print(f"\n[{so}]")
        for sem in SEMS:
            c = out["rankings"][so][sem]
            line = (f"  {sem:14s} conv={c['converged']!s:5s} rho(outdeg)={c['rho_vs_outdeg']:+.3f} "
                    f"rho(indeg)={c['rho_vs_indeg']:+.3f} rho(seed)={c['rho_vs_seed_membership']:+.3f}")
            if c["rho_vs_fvs_degree_key"] is not None:
                line += f" rho(fvs_key)={c['rho_vs_fvs_degree_key']:+.3f}"
            if c["rho_vs_layer_index"] is not None:
                line += f" rho(layer)={c['rho_vs_layer_index']:+.3f}"
            print(line)
            if "psych_prediction" in c:
                for f in PSYCH_FIELDS:
                    p = c["psych_prediction"][f]
                    print(f"    {f:18s} incr R2 over log_outdeg = {p['incremental_score_over_log_outdeg_r2']:+.5f}  "
                          f"(R2: {p['r2_log_outdeg']:.4f} -> {p['r2_log_outdeg_plus_score']:.4f}); "
                          f"pearson(score,norm)={p['pearson_score_norm']:+.3f}")
            print(f"    top: {', '.join(n for n, _ in c['top20_words'][:12])}")
    bi = best_incremental
    print(f"\nHEADLINE: best incremental R2 over log(out-degree) = {bi['value']:+.5f} at {bi['where']}")


if __name__ == "__main__":
    main()
