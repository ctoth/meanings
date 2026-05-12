"""Psycholinguistic-norm regression on the OEWN paper-wordnet definition graph.

Reproduces ``reports/psycholinguistic-regression-findings.md``.

What it does
------------
1. Builds the ``paper-wordnet`` OEWN graph (``oewn:2024``, local via ``wn``).
2. Runs the repo kernel analysis (``exact-small-greedy`` seed, ``source-union``
   Core) -> layer index, Kernel / Core / Satellite membership, combinatorial
   seed (FVS / MinSet) membership.
3. Computes structural features per node: in-degree, out-degree, SCC size,
   cycle participation (is the node in a nontrivial SCC of the full digraph),
   forward (authority) PageRank, reverse (hub / definitional-productivity)
   PageRank -- the last two via :func:`meanings.spectral_analysis.perron_scores`.
4. Joins the three psycholinguistic norm CSVs from ``data/psycholinguistic/``
   (frequency = SUBTLEX-US Zipf; age_of_acquisition = Kuperman et al.;
   concreteness = Brysbaert et al.) keyed on the lemma part of each ``lemma::pos``
   node, via :func:`meanings.annotations.load_annotation_csvs`.
5. Fits nested models -- structural block (block 1) then + psycholinguistic
   block (block 2) -- for four outcomes:
     (a) Kernel membership (logistic, AUC + McFadden pseudo-R^2)
     (b) Core vs Satellite among Kernel nodes (logistic)
     (c) seed / MinSet membership (logistic)
     (d) layer index among Kernel nodes (OLS on log1p(layer), Poisson on layer)
   and reports the *incremental* (partial) R^2 / pseudo-R^2 / AUC of block 2
   over block 1, plus standardized block-2 coefficients with signs.
6. PF-leg test: does reverse-PageRank (and the FVS seed) predict AoA /
   concreteness / frequency *better than raw out-degree does*? Reports the
   incremental-over-out-degree R^2 for each norm.
7. Writes ``reports/psycholinguistic-regression-output.json`` and prints a
   summary.

Run: ``uv run python scripts/psycholinguistic_regression.py``
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import roc_auc_score

from meanings.annotations import load_annotation_csvs
from meanings.graph_analysis import (
    analyze_kernel,
    induced_subgraph,
    strongly_connected_components,
)
from meanings.spectral_analysis import perron_scores
from meanings.wordnet_pipeline import build_paper_wordnet_graph

REPO = Path(__file__).resolve().parents[1]
PSYCH_DIR = REPO / "data" / "psycholinguistic"
OUT_JSON = REPO / "reports" / "psycholinguistic-regression-output.json"

PSYCH_FIELDS = ("frequency", "age_of_acquisition", "concreteness")
SEED_METHOD = "exact-small-greedy"
CORE_POLICY = "source-union"


# --------------------------------------------------------------------------- #
# small stats helpers
# --------------------------------------------------------------------------- #
def zscore(col: np.ndarray) -> np.ndarray:
    mu = col.mean()
    sd = col.std()
    if sd == 0:
        return col - mu
    return (col - mu) / sd


def ols_r2(X: np.ndarray, y: np.ndarray) -> float:
    """In-sample R^2 of an OLS fit with intercept (X is the design WITHOUT intercept col)."""
    if X.shape[1] == 0:
        # intercept-only model: R^2 = 0
        return 0.0
    model = LinearRegression().fit(X, y)
    pred = model.predict(X)
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def logit_fit(X: np.ndarray, y: np.ndarray):
    """statsmodels Logit with intercept; returns (result_or_None, auc, mcfadden_r2).

    Falls back to sklearn (very mild L2) if statsmodels does not converge / is
    singular; AUC is always in-sample.
    """
    Xc = sm.add_constant(X, has_constant="add")
    auc = float("nan")
    mcf = float("nan")
    res = None
    try:
        res = sm.Logit(y, Xc).fit(disp=0, maxiter=200)
        p = res.predict(Xc)
        auc = roc_auc_score(y, p)
        # McFadden pseudo R^2
        ll_full = res.llf
        ll_null = sm.Logit(y, np.ones((len(y), 1))).fit(disp=0).llf
        mcf = 1.0 - ll_full / ll_null if ll_null != 0 else float("nan")
        return res, float(auc), float(mcf)
    except Exception:
        pass
    # fallback
    clf = LogisticRegression(max_iter=2000, C=1e6, solver="lbfgs")
    if X.shape[1] == 0:
        # intercept-only: predict base rate
        p = np.full(len(y), y.mean())
    else:
        clf.fit(X, y)
        p = clf.predict_proba(X)[:, 1]
    try:
        auc = roc_auc_score(y, p)
    except Exception:
        auc = float("nan")
    # McFadden via log-loss
    eps = 1e-12
    p = np.clip(p, eps, 1 - eps)
    ll_full = float((y * np.log(p) + (1 - y) * np.log(1 - p)).sum())
    pb = float(np.clip(y.mean(), eps, 1 - eps))
    ll_null = float((y * np.log(pb) + (1 - y) * np.log(1 - pb)).sum())
    mcf = 1.0 - ll_full / ll_null if ll_null != 0 else float("nan")
    return None, float(auc), float(mcf)


def poisson_pseudo_r2(X: np.ndarray, y: np.ndarray):
    """statsmodels Poisson GLM; returns (deviance pseudo-R^2, result_or_None)."""
    Xc = sm.add_constant(X, has_constant="add")
    try:
        res = sm.GLM(y, Xc, family=sm.families.Poisson()).fit()
        null = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Poisson()).fit()
        pr2 = 1.0 - res.deviance / null.deviance if null.deviance > 0 else float("nan")
        return float(pr2), res
    except Exception:
        return float("nan"), None


def block_design(rows, feature_names, standardize=True):
    """Stack named features into an (n, k) float matrix; one-hot POS if 'pos' present."""
    cols = []
    names = []
    for fn in feature_names:
        if fn == "pos":
            pos_vals = sorted({r["pos"] for r in rows})
            # drop one level (reference) to avoid collinearity with intercept
            for pv in pos_vals[1:]:
                cols.append(np.array([1.0 if r["pos"] == pv else 0.0 for r in rows]))
                names.append(f"pos={pv}")
        else:
            col = np.array([float(r[fn]) for r in rows])
            if standardize:
                col = zscore(col)
            cols.append(col)
            names.append(fn)
    if not cols:
        return np.empty((len(rows), 0)), []
    return np.column_stack(cols), names


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    print("building paper-wordnet graph (oewn:2024)...")
    build = build_paper_wordnet_graph("oewn:2024")
    nodes = set(build.nodes)
    adj = build.adjacency
    edges = sum(len(v) for v in adj.values())
    print(f"  nodes={len(nodes)} edges={edges}")

    print(f"kernel analysis (seed={SEED_METHOD}, core={CORE_POLICY})...")
    analysis = analyze_kernel(nodes, adj, seed_method=SEED_METHOD, core_policy=CORE_POLICY)
    kernel = analysis.kernel_nodes
    core = analysis.core_nodes
    sats = analysis.satellite_nodes
    seed = set(analysis.seed_nodes)
    layer_by_node = dict(analysis.layer_by_node)  # kernel nodes; seed at layer 0
    print(f"  kernel={len(kernel)} core={len(core)} sats={len(sats)} seed={len(seed)} "
          f"layers_defined_for={len(layer_by_node)} residual_cyclic_scc={analysis.residual_cyclic_scc_count}")

    # structural features ---------------------------------------------------- #
    print("degrees + SCC sizes + cycle participation...")
    indeg = {n: 0 for n in nodes}
    for ts in adj.values():
        for t in ts:
            if t in indeg:
                indeg[t] += 1
    outdeg = {n: len(adj.get(n, ())) for n in nodes}
    sccs = strongly_connected_components(nodes, adj)
    scc_size = {}
    in_cycle = {}
    for comp in sccs:
        loop = len(comp) > 1 or any(u in adj.get(u, ()) for u in comp)
        for u in comp:
            scc_size[u] = len(comp)
            in_cycle[u] = 1 if loop else 0

    print("forward (authority) PageRank, full graph, damped...")
    pr_fwd = perron_scores(adj, nodes, orientation="forward", component_policy="damped-full",
                           damping=0.85, iters=300, tol=1e-11).scores
    print("reverse (hub / definitional-productivity) PageRank, full graph, damped...")
    pr_rev = perron_scores(adj, nodes, orientation="reverse", component_policy="damped-full",
                           damping=0.85, iters=300, tol=1e-11).scores

    # psycholinguistic join -------------------------------------------------- #
    print("loading psycholinguistic norm CSVs...")
    csv_paths = [PSYCH_DIR / f"{f}.csv" for f in PSYCH_FIELDS]
    ann = load_annotation_csvs(csv_paths)
    print(f"  sources={ann.sources}")

    def lemma_of(node: str) -> str:
        return node.split("::", 1)[0]

    # coverage
    coverage = {}
    for f in PSYCH_FIELDS:
        present_all = sum(1 for n in nodes if ann.get(lemma_of(n), f) is not None)
        present_kernel = sum(1 for n in kernel if ann.get(lemma_of(n), f) is not None)
        coverage[f] = {
            "all_nodes": present_all, "all_total": len(nodes),
            "all_frac": present_all / len(nodes),
            "kernel_nodes": present_kernel, "kernel_total": len(kernel),
            "kernel_frac": present_kernel / len(kernel),
        }
    # all-three coverage
    cov_all3_full = sum(1 for n in nodes if all(ann.get(lemma_of(n), f) is not None for f in PSYCH_FIELDS))
    cov_all3_kernel = sum(1 for n in kernel if all(ann.get(lemma_of(n), f) is not None for f in PSYCH_FIELDS))
    coverage["all_three"] = {
        "full": cov_all3_full, "full_total": len(nodes), "full_frac": cov_all3_full / len(nodes),
        "kernel": cov_all3_kernel, "kernel_total": len(kernel), "kernel_frac": cov_all3_kernel / len(kernel),
    }

    # differential-missingness check: among nodes WITH a layer, does coverage vary by layer band?
    layer_cov = {}
    if layer_by_node:
        bands = {"L0": lambda l: l == 0, "L1-3": lambda l: 1 <= l <= 3,
                 "L4-10": lambda l: 4 <= l <= 10, "L11+": lambda l: l >= 11}
        for bname, pred in bands.items():
            band_nodes = [n for n, l in layer_by_node.items() if pred(l)]
            if not band_nodes:
                continue
            has3 = sum(1 for n in band_nodes if all(ann.get(lemma_of(n), f) is not None for f in PSYCH_FIELDS))
            layer_cov[bname] = {"n": len(band_nodes), "all3_frac": has3 / len(band_nodes)}

    # build the row table --------------------------------------------------- #
    def make_row(n: str) -> dict | None:
        lm = lemma_of(n)
        vals = {f: ann.get(lm, f) for f in PSYCH_FIELDS}
        if any(v is None for v in vals.values()):
            return None
        return {
            "node": n,
            "pos": build.pos_by_node.get(n, "?"),
            "indeg": indeg[n],
            "outdeg": outdeg[n],
            "log_indeg": math.log1p(indeg[n]),
            "log_outdeg": math.log1p(outdeg[n]),
            "scc_size": scc_size[n],
            "log_scc_size": math.log1p(scc_size[n]),
            "in_cycle": in_cycle[n],
            "pr_fwd": pr_fwd[n],
            "pr_rev": pr_rev[n],
            "log_pr_fwd": math.log(pr_fwd[n]) if pr_fwd[n] > 0 else math.log(1e-12),
            "log_pr_rev": math.log(pr_rev[n]) if pr_rev[n] > 0 else math.log(1e-12),
            "is_kernel": 1 if n in kernel else 0,
            "is_core": 1 if n in core else 0,
            "is_seed": 1 if n in seed else 0,
            "layer": layer_by_node.get(n),  # None unless kernel
            "frequency": vals["frequency"],
            "age_of_acquisition": vals["age_of_acquisition"],
            "concreteness": vals["concreteness"],
        }

    all_rows = [r for n in nodes if (r := make_row(n)) is not None]
    kernel_rows = [r for r in all_rows if r["is_kernel"] == 1]
    layered_rows = [r for r in kernel_rows if r["layer"] is not None]
    core_sat_rows = kernel_rows  # within kernel: is_core vs not
    print(f"  joined rows: all={len(all_rows)} kernel={len(kernel_rows)} layered={len(layered_rows)}")

    STRUCT = ["log_indeg", "log_outdeg", "log_scc_size", "in_cycle", "log_pr_fwd", "log_pr_rev", "pos"]
    PSYCH = ["frequency", "age_of_acquisition", "concreteness"]

    out: dict = {
        "config": {"lexicon": "oewn:2024", "seed_method": SEED_METHOD, "core_policy": CORE_POLICY,
                   "structural_block": STRUCT, "psycholinguistic_block": PSYCH},
        "graph": {"nodes": len(nodes), "edges": edges, "kernel": len(kernel), "core": len(core),
                  "satellites": len(sats), "seed": len(seed), "residual_cyclic_scc": analysis.residual_cyclic_scc_count},
        "coverage": coverage,
        "coverage_by_layer_band": layer_cov,
        "join_counts": {"all_rows": len(all_rows), "kernel_rows": len(kernel_rows),
                        "layered_rows": len(layered_rows)},
        "models": {},
    }

    # ---- (a) Kernel membership over ALL joined nodes ---------------------- #
    print("model (a): Kernel membership ~ struct + psych ...")
    y = np.array([r["is_kernel"] for r in all_rows], dtype=float)
    X1, n1 = block_design(all_rows, STRUCT)
    X2_only, n2 = block_design(all_rows, PSYCH)
    X12 = np.column_stack([X1, X2_only]) if X1.size and X2_only.size else (X1 if X1.size else X2_only)
    _, auc1, mcf1 = logit_fit(X1, y)
    res12, auc12, mcf12 = logit_fit(X12, y)
    _, auc2, mcf2 = logit_fit(X2_only, y)
    psych_coefs_a = {}
    if res12 is not None:
        # block-2 coefs are the last len(n2) params (after const + n1)
        params = res12.params
        pvals = res12.pvalues
        offset = 1 + len(n1)
        for i, name in enumerate(n2):
            psych_coefs_a[name] = {"std_coef": float(params[offset + i]), "p": float(pvals[offset + i])}
    out["models"]["a_kernel_membership"] = {
        "n": len(all_rows), "base_rate": float(y.mean()),
        "block1_struct": {"auc": auc1, "mcfadden_r2": mcf1, "features": n1},
        "block2_psych_only": {"auc": auc2, "mcfadden_r2": mcf2, "features": n2},
        "block1+2": {"auc": auc12, "mcfadden_r2": mcf12},
        "incremental_block2": {"delta_auc": auc12 - auc1, "delta_mcfadden_r2": mcf12 - mcf1},
        "block2_standardized_coefs_given_block1": psych_coefs_a,
    }

    # ---- (b) Core vs Satellite among Kernel nodes ------------------------- #
    print("model (b): Core vs Satellite among kernel nodes ~ struct + psych ...")
    if len(core_sat_rows) > 30 and 0 < sum(r["is_core"] for r in core_sat_rows) < len(core_sat_rows):
        y = np.array([r["is_core"] for r in core_sat_rows], dtype=float)
        X1, n1 = block_design(core_sat_rows, STRUCT)
        X2_only, n2 = block_design(core_sat_rows, PSYCH)
        X12 = np.column_stack([X1, X2_only]) if X1.size and X2_only.size else (X1 if X1.size else X2_only)
        _, auc1, mcf1 = logit_fit(X1, y)
        res12, auc12, mcf12 = logit_fit(X12, y)
        _, auc2, mcf2 = logit_fit(X2_only, y)
        psych_coefs_b = {}
        if res12 is not None:
            params, pvals = res12.params, res12.pvalues
            offset = 1 + len(n1)
            for i, name in enumerate(n2):
                psych_coefs_b[name] = {"std_coef": float(params[offset + i]), "p": float(pvals[offset + i])}
        out["models"]["b_core_vs_satellite"] = {
            "n": len(core_sat_rows), "base_rate_core": float(y.mean()),
            "block1_struct": {"auc": auc1, "mcfadden_r2": mcf1},
            "block2_psych_only": {"auc": auc2, "mcfadden_r2": mcf2},
            "block1+2": {"auc": auc12, "mcfadden_r2": mcf12},
            "incremental_block2": {"delta_auc": auc12 - auc1, "delta_mcfadden_r2": mcf12 - mcf1},
            "block2_standardized_coefs_given_block1": psych_coefs_b,
        }
    else:
        out["models"]["b_core_vs_satellite"] = {"skipped": "too few core or satellite rows in join"}

    # ---- (c) seed / MinSet membership over ALL joined nodes --------------- #
    print("model (c): seed/MinSet membership ~ struct + psych ...")
    y = np.array([r["is_seed"] for r in all_rows], dtype=float)
    X1, n1 = block_design(all_rows, STRUCT)
    X2_only, n2 = block_design(all_rows, PSYCH)
    X12 = np.column_stack([X1, X2_only]) if X1.size and X2_only.size else (X1 if X1.size else X2_only)
    _, auc1, mcf1 = logit_fit(X1, y)
    res12, auc12, mcf12 = logit_fit(X12, y)
    _, auc2, mcf2 = logit_fit(X2_only, y)
    psych_coefs_c = {}
    if res12 is not None:
        params, pvals = res12.params, res12.pvalues
        offset = 1 + len(n1)
        for i, name in enumerate(n2):
            psych_coefs_c[name] = {"std_coef": float(params[offset + i]), "p": float(pvals[offset + i])}
    out["models"]["c_seed_membership"] = {
        "n": len(all_rows), "base_rate": float(y.mean()),
        "block1_struct": {"auc": auc1, "mcfadden_r2": mcf1},
        "block2_psych_only": {"auc": auc2, "mcfadden_r2": mcf2},
        "block1+2": {"auc": auc12, "mcfadden_r2": mcf12},
        "incremental_block2": {"delta_auc": auc12 - auc1, "delta_mcfadden_r2": mcf12 - mcf1},
        "block2_standardized_coefs_given_block1": psych_coefs_c,
    }

    # ---- (d) layer index among kernel nodes ------------------------------- #
    print("model (d): layer index among kernel nodes ~ struct + psych ...")
    if len(layered_rows) > 30:
        y_log = np.array([math.log1p(r["layer"]) for r in layered_rows], dtype=float)
        y_cnt = np.array([r["layer"] for r in layered_rows], dtype=float)
        X1, n1 = block_design(layered_rows, STRUCT)
        X2_only, n2 = block_design(layered_rows, PSYCH)
        X12 = np.column_stack([X1, X2_only]) if X1.size and X2_only.size else (X1 if X1.size else X2_only)
        r2_1 = ols_r2(X1, y_log)
        r2_12 = ols_r2(X12, y_log)
        r2_2 = ols_r2(X2_only, y_log)
        pr2_1, _ = poisson_pseudo_r2(X1, y_cnt)
        pr2_12, res_p12 = poisson_pseudo_r2(X12, y_cnt)
        pr2_2, _ = poisson_pseudo_r2(X2_only, y_cnt)
        # standardized psych coefs from the OLS-on-log1p model (interpretable signs)
        lin = LinearRegression().fit(X12, y_log)
        psych_coefs_d = {}
        offset = len(n1)
        for i, name in enumerate(n2):
            psych_coefs_d[name] = {"std_coef_ols_log1p_layer": float(lin.coef_[offset + i])}
        out["models"]["d_layer_index"] = {
            "n": len(layered_rows),
            "ols_log1p_layer": {"r2_block1": r2_1, "r2_block2_only": r2_2, "r2_block1+2": r2_12,
                                "incremental_block2_r2": r2_12 - r2_1},
            "poisson_layer": {"pseudo_r2_block1": pr2_1, "pseudo_r2_block2_only": pr2_2,
                              "pseudo_r2_block1+2": pr2_12, "incremental_block2_pseudo_r2": pr2_12 - pr2_1},
            "block2_standardized_coefs_given_block1": psych_coefs_d,
        }
    else:
        out["models"]["d_layer_index"] = {"skipped": "too few layered kernel rows in join"}

    # ---- PF leg: reverse-PageRank / seed vs out-degree predicting norms --- #
    print("PF leg: reverse-PageRank & seed vs out-degree predicting AoA/concreteness/frequency ...")
    pf = {}
    rows_pf = all_rows
    for norm in PSYCH_FIELDS:
        y = np.array([r[norm] for r in rows_pf], dtype=float)
        # baseline: log out-degree (+ in-degree as a fuller "degree" baseline variant)
        Xo = block_design(rows_pf, ["log_outdeg"])[0]
        Xdeg = block_design(rows_pf, ["log_outdeg", "log_indeg"])[0]
        # add reverse-PageRank
        Xo_rev = block_design(rows_pf, ["log_outdeg", "log_pr_rev"])[0]
        Xdeg_rev = block_design(rows_pf, ["log_outdeg", "log_indeg", "log_pr_rev"])[0]
        # add seed membership (FVS)
        Xo_seed = block_design(rows_pf, ["log_outdeg"])[0]
        Xo_seed = np.column_stack([Xo_seed, np.array([r["is_seed"] for r in rows_pf], dtype=float)])
        # also forward-PageRank for completeness
        Xo_fwd = block_design(rows_pf, ["log_outdeg", "log_pr_fwd"])[0]
        r2_out = ols_r2(Xo, y)
        r2_deg = ols_r2(Xdeg, y)
        r2_out_rev = ols_r2(Xo_rev, y)
        r2_deg_rev = ols_r2(Xdeg_rev, y)
        r2_out_seed = ols_r2(Xo_seed, y)
        r2_out_fwd = ols_r2(Xo_fwd, y)
        # raw correlations (sign matters)
        def pearson(a, b):
            a = np.asarray(a, float); b = np.asarray(b, float)
            if a.std() == 0 or b.std() == 0:
                return float("nan")
            return float(np.corrcoef(a, b)[0, 1])
        pf[norm] = {
            "n": len(rows_pf),
            "r2_log_outdeg_only": r2_out,
            "r2_log_outdeg_plus_indeg": r2_deg,
            "r2_log_outdeg_plus_revPR": r2_out_rev,
            "incremental_revPR_over_outdeg_r2": r2_out_rev - r2_out,
            "incremental_revPR_over_degree_r2": r2_deg_rev - r2_deg,
            "r2_log_outdeg_plus_seed": r2_out_seed,
            "incremental_seed_over_outdeg_r2": r2_out_seed - r2_out,
            "r2_log_outdeg_plus_fwdPR": r2_out_fwd,
            "pearson_outdeg_norm": pearson([r["log_outdeg"] for r in rows_pf], y),
            "pearson_revPR_norm": pearson([r["log_pr_rev"] for r in rows_pf], y),
            "pearson_fwdPR_norm": pearson([r["log_pr_fwd"] for r in rows_pf], y),
            "pearson_indeg_norm": pearson([r["log_indeg"] for r in rows_pf], y),
            "mean_norm_seed": float(np.mean([r[norm] for r in rows_pf if r["is_seed"]])) if any(r["is_seed"] for r in rows_pf) else None,
            "mean_norm_nonseed": float(np.mean([r[norm] for r in rows_pf if not r["is_seed"]])),
            "mean_norm_kernel": float(np.mean([r[norm] for r in rows_pf if r["is_kernel"]])),
            "mean_norm_rest": float(np.mean([r[norm] for r in rows_pf if not r["is_kernel"]])),
        }
        # layer vs norm among kernel
        if layered_rows:
            ly = np.array([r["layer"] for r in layered_rows], float)
            ny = np.array([r[norm] for r in layered_rows], float)
            pf[norm]["pearson_layer_norm_kernel"] = pearson(ly, ny)
    out["pf_leg"] = pf

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT_JSON}")
    # short console summary
    a = out["models"]["a_kernel_membership"]
    c = out["models"]["c_seed_membership"]
    d = out["models"].get("d_layer_index", {})
    print("\n=== SUMMARY ===")
    print(f"(a) Kernel membership: block1 AUC={a['block1+2']['auc']:.3f} from "
          f"{a['block1_struct']['auc']:.3f}; deltaAUC(block2)={a['incremental_block2']['delta_auc']:+.4f} "
          f"deltaMcFadden={a['incremental_block2']['delta_mcfadden_r2']:+.4f}")
    print(f"(c) seed membership: deltaAUC(block2)={c['incremental_block2']['delta_auc']:+.4f} "
          f"deltaMcFadden={c['incremental_block2']['delta_mcfadden_r2']:+.4f}")
    if "ols_log1p_layer" in d:
        print(f"(d) layer: OLS R2 block1={d['ols_log1p_layer']['r2_block1']:.4f} "
              f"-> block1+2={d['ols_log1p_layer']['r2_block1+2']:.4f} "
              f"(incremental={d['ols_log1p_layer']['incremental_block2_r2']:+.4f})")
    for norm in PSYCH_FIELDS:
        p = out["pf_leg"][norm]
        print(f"PF {norm}: R2(outdeg)={p['r2_log_outdeg_only']:.4f}  "
              f"+revPR -> {p['r2_log_outdeg_plus_revPR']:.4f} (incr {p['incremental_revPR_over_outdeg_r2']:+.4f}); "
              f"+seed -> {p['r2_log_outdeg_plus_seed']:.4f} (incr {p['incremental_seed_over_outdeg_r2']:+.4f})")


if __name__ == "__main__":
    main()
