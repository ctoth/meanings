# Psycholinguistic-norm regression on the OEWN definition graph — findings

**Date:** 2026-05-12
**Type:** empirical adjudication (regression)
**Status:** complete; all four regressions + the Perron–Frobenius leg run on the
real `paper-wordnet` OEWN graph with the psycholinguistic norms now bundled in
`data/psycholinguistic/`.
**Closes:** the "blocked on missing data" item in
`reports/swanson-yoneda-harnad-findings.md` §4.3 and the psycholinguistic-overlay
leg of `reports/swanson-perron-frobenius-findings.md` §3f.
**Reproduce:** `uv run python scripts/psycholinguistic_regression.py` →
`reports/psycholinguistic-regression-output.json` (+ console log in
`reports/psycholinguistic-regression-run.log`).

---

## 0. TL;DR

- **Data join.** `paper-wordnet` OEWN (`oewn:2024`): 160,010 `lemma::pos` nodes,
  677,823 edges; Kernel 12,853 (8.0%), Core 288, Satellites 12,565, combinatorial
  seed (FVS / MinSet, `exact-small-greedy`) 2,370; kernel fully acyclicised
  (0 residual cyclic SCCs), 65-layer DAG. Joining all three norms (SUBTLEX-US
  Zipf frequency, Kuperman et al. AoA, Brysbaert et al. concreteness) keyed on
  the lemma part of each node: **27,356 nodes have all three** (17.1% of the
  graph; per-norm marginal coverage 29.0% / 21.4% / 24.1%). Inside the Kernel,
  all-three coverage is **53.7%** (6,899 nodes). Coverage is *mildly* lower in
  the deep layer band (L11+: 48.6% have all three vs ~58% for L1–10) but not
  catastrophically differential.
- **Yoneda/Harnad verdict — block 2 adds essentially nothing given block 1.**
  Structural features (log in-degree, log out-degree, log SCC size, cycle
  participation, log forward-PageRank, log reverse-PageRank, POS) already
  predict the layering/membership outcomes very well; the psycholinguistic block
  adds **partial R²/AUC in the 0.0001–0.01 range** in every case:
  - **Kernel membership:** block-1 AUC = 0.984 (McFadden R² 0.784); adding the
    psych block: ΔAUC = **+0.00004**, ΔMcFadden = **+0.0005**.
  - **Core vs Satellite among Kernel nodes:** block-1 AUC = 1.00 (perfect
    separation — Core is a deterministic graph property); psych block ΔAUC = 0.
  - **seed/MinSet membership:** block-1 AUC = 0.961 (McFadden 0.512); psych
    block ΔAUC = **+0.0004**, ΔMcFadden = **+0.003**.
  - **layer index** (kernel nodes, OLS on log1p(layer)): block-1 R² = 0.238 →
    block-1+2 R² = 0.245, **incremental = +0.0066** (Poisson pseudo-R²
    incremental = +0.010).
  Per the pre-registered decision rule in §4.3 of the Yoneda/Harnad report
  (residue > ~0.05 ⇒ Harnad thumb; < ~0.01 ⇒ pro-Yoneda; in between ⇒ "graded
  grounding"), **every outcome lands in the < 0.01 "pro-Yoneda / the
  psycholinguistic signal *is* the structural signal" regime.** The dictionary
  graph's own carving absorbs the concreteness/AoA/frequency signal almost
  entirely; what is left over is a sliver. **This is empirical weight *against*
  "meaning has a large non-relational residue" — but a weak instrument for the
  philosophy** (see §6: the graph isn't a category, layer is itself structural,
  and the confound below).
- **PF-leg verdict — reverse-PageRank does *not* beat out-degree in a way that
  rescues "FVS seed = soft grounding vocabulary".** Predicting each norm from
  log out-degree alone vs + reverse-PageRank: incremental R² = **+0.009**
  (frequency), **+0.002** (AoA), **+0.031** (concreteness — and that one is a
  *suppression artifact*, see §5). Predicting from log out-degree alone vs +
  seed-membership: incremental R² = **+0.006 / +0.003 / +0.0001** — i.e. the
  FVS seed contributes almost nothing over raw out-degree. **Codex's point holds
  head-on: degree explains most of it.** Out-degree by itself gives Pearson 0.47
  with log-frequency, −0.28 with AoA; reverse-PageRank gives 0.46 / −0.27 — a
  near-perfect re-skin of out-degree, not an improvement. Forward (authority)
  PageRank is near-zero-correlated with all three norms (Pearson 0.01 / −0.01 /
  0.13), confirming the prior finding that authority-PageRank is the wrong
  eigenvector for "foundationalness".
- **Confound (Codex Brief 4/5).** Graph position is itself shaped by the fact
  that OEWN lexicographers write definitions for human learners — concrete,
  early-acquired, frequent words get reused as definers, which *creates* the
  structural features. So the regression **cannot distinguish** "structure
  screens off psycholinguistics because meaning is relational" from "structure
  screens off psycholinguistics because the structure was *built from*
  psycholinguistic salience". Both predict exactly the result observed. The
  regression refutes only a *strong* version of the residue claim (a large
  *independent* extra-graph signal) and is silent on the causal direction.

---

## 1. Data join and coverage

**Graph.** `meanings.wordnet_pipeline.build_paper_wordnet_graph("oewn:2024")` —
one node per `lemma::pos` with the first available representative synset
definition; edge `definer::pos -> defined::pos` for each content-word lemma in
the definition (same-POS preferred, else unambiguous-POS). 160,010 nodes;
677,823 directed edges. Kernel/Core/Satellite/seed from
`meanings.graph_analysis.analyze_kernel(..., seed_method="exact-small-greedy",
core_policy="source-union")`: Kernel 12,853 (8.03%), Kernel SCCs 3,841, source
SCCs 286, Core (union of source SCCs) 288, Satellites 12,565, seed (FVS /
MinSet) 2,370 (1.48% of all nodes, 18.4% of Kernel), residual cyclic SCCs 0 →
65-layer DAG over the Kernel with the seed at layer 0. (Matches
`reports/oewn-paper-wordnet-kernel-summary.json` / `…-layers.json`.)

**Norms.** From `data/psycholinguistic/{frequency,age_of_acquisition,concreteness}.csv`,
loaded with `meanings.annotations.load_annotation_csvs`, joined on the lemma part
of each `lemma::pos` node (so all POS senses of a lemma share the lemma's norm
value — a deliberate limitation, since the norms are lemma-level):

| Norm | Source | Nodes with value | % of 160,010 | % of Kernel (of 12,853) |
|---|---|---:|---:|---:|
| frequency | SUBTLEX-US Zipf | 46,386 | 29.0% | 73.7% |
| age_of_acquisition | Kuperman et al. 2012 | 34,314 | 21.4% | 56.9% |
| concreteness | Brysbaert et al. 2014 | 38,572 | 24.1% | 65.5% |
| **all three** | (intersection) | **27,356** | **17.1%** | **53.7% (6,899)** |

So the regression sample is **27,356 nodes** (all-three) for the all-graph
models (a Kernel membership, c seed membership, PF leg) and **6,899 Kernel
nodes** for the within-Kernel models (b Core-vs-Satellite, d layer index). The
Kernel is far better covered than the tail (53.7% vs 17.1%) — as expected, the
tail is heavy with multiword terms, proper nouns, and technical vocabulary that
the norm databases don't include.

**Differential-missingness check** (all-three coverage by layer band, among
nodes that have a layer): L0 (seed) 51.9%, L1–3 58.2%, L4–10 58.2%, **L11+
48.6%**. Coverage dips ~10 points in the deepest band — the deep tail is more
technical/multiword — so the within-Kernel layer model (d) is *mildly* biased
toward the better-covered shallow-to-mid layers. Not enough to overturn the
verdict (the incremental R² is 0.007, an order of magnitude below the 0.05
threshold), but worth noting.

---

## 2. Model specifications

All features standardized (z-scored) before entry; POS entered as one-hot with
one reference level dropped. Block 1 = structural; block 2 = psycholinguistic;
nested comparison reports block-2's *incremental* fit over block-1.

- **Structural block (block 1):** `log_indeg = log(1+in-degree)`,
  `log_outdeg = log(1+out-degree)`, `log_scc_size = log(1+|SCC|)` (size of the
  full-digraph strongly connected component the node is in), `in_cycle` (1 if
  that SCC is nontrivial), `log_pr_fwd = log(forward/authority PageRank)`,
  `log_pr_rev = log(reverse/hub PageRank)` — both damped (d = 0.85) over the
  full 160,010-node digraph, via `meanings.spectral_analysis.perron_scores`;
  plus POS one-hot.
- **Psycholinguistic block (block 2):** `frequency` (SUBTLEX-US Zipf),
  `age_of_acquisition` (years), `concreteness` (1–5).
- **Outcomes / estimators:**
  - (a) `is_kernel` over the 27,356 all-three nodes — logistic; report AUC
    (in-sample) and McFadden pseudo-R².
  - (b) `is_core` among the 6,899 covered Kernel nodes (Core vs Satellite) —
    logistic; AUC + McFadden. (Note: Core base rate is only 1.96% of covered
    Kernel nodes, and Core is a *deterministic* graph property given the SCC
    structure, so block 1 separates perfectly — see §3.)
  - (c) `is_seed` over the 27,356 all-three nodes — logistic; AUC + McFadden.
  - (d) `layer` among the 6,899 covered Kernel nodes — OLS on `log1p(layer)`
    (report R²) **and** Poisson GLM on `layer` (report deviance pseudo-R²,
    since layer is over-dispersed count).
- **PF leg:** for each norm, OLS regressions with: {`log_outdeg`}, {`log_outdeg`,
  `log_indeg`}, {`log_outdeg`, `log_pr_rev`}, {`log_outdeg`, `log_indeg`,
  `log_pr_rev`}, {`log_outdeg`, `is_seed`}, {`log_outdeg`, `log_pr_fwd`} — to
  isolate the *incremental-over-degree* contribution of reverse-PageRank and of
  seed membership. Plus raw Pearson correlations of each predictor with each
  norm (sign matters), and norm means by component.

All numbers below are in `reports/psycholinguistic-regression-output.json`.

**Caveat on the logistic fits.** statsmodels' Logit raised
`ConvergenceWarning`/overflow on the near-separable models (Kernel membership,
Core-vs-Satellite, seed membership) — unsurprising, since structural features
nearly determine these graph properties. AUC and the incremental numbers are
robust to this (AUC just reads off the predicted scores); the
Core-vs-Satellite block-2 coefficient table is empty because the perfectly-
separated fit didn't return usable standard errors. None of this changes the
qualitative verdict (block 2 adds ~nothing).

---

## 3. Results — the four models

### (a) Kernel membership ~ structural (block 1) + psycholinguistic (block 2)
n = 27,356; base rate (is_kernel) = 25.2%.
- Block 1 (structural): AUC = **0.984**, McFadden R² = **0.784**.
- Block 2 alone (psych only): AUC = 0.735, McFadden R² = 0.116. (So
  psycholinguistic features *do* carry kernel-membership signal on their own —
  concrete/early/frequent words skew kernel-ward — but it's a weak model.)
- Block 1 + 2: AUC = **0.984**, McFadden R² = **0.785**.
- **Incremental block 2: ΔAUC = +0.00004, ΔMcFadden R² = +0.0005.**
- Block-2 standardized coefficients *after* block 1: frequency −0.019 (p = 0.71),
  age_of_acquisition +0.091 (p = 0.06), concreteness −0.064 (p = 0.11). None
  significant at 0.05; the signs are not even uniformly in the "Harnad" direction.

### (b) Core vs Satellite among Kernel nodes
n = 6,899 covered Kernel nodes; Core base rate = 1.96%.
- Block 1: AUC = **1.00**, McFadden R² ≈ 0.998 — *perfect separation*. Core =
  union of source SCCs is a deterministic function of the digraph's SCC
  structure, so the structural block (which includes SCC size and cycle
  participation) reconstructs it exactly.
- Block 2 alone: AUC = 0.576 — barely above chance.
- Block 1 + 2: AUC = **1.00**. **Incremental block 2: ΔAUC = 0.**
- Block-2 coefficients unavailable (separated fit). Verdict: the
  Core/Satellite split is 100% structural; psycholinguistics adds nothing.

### (c) seed / MinSet membership ~ structural + psycholinguistic
n = 27,356; base rate (is_seed) = 4.50%.
- Block 1: AUC = **0.961**, McFadden R² = **0.512**.
- Block 2 alone: AUC = 0.804, McFadden R² = 0.146. (Seed nodes — the FVS — are
  on average more frequent: mean Zipf 4.18 vs 3.04 for non-seed; earlier
  acquired: mean AoA 7.75 vs 9.90. So on their own the norms predict
  seed-membership decently.)
- Block 1 + 2: AUC = **0.961**, McFadden R² = **0.515**.
- **Incremental block 2: ΔAUC = +0.0004, ΔMcFadden R² = +0.003.**
- Block-2 standardized coefficients after block 1: frequency **+0.238**
  (p = 6e-5 — survives!), age_of_acquisition +0.020 (p = 0.75), concreteness
  −0.013 (p = 0.78). So *one* psycholinguistic variable (frequency) keeps a
  non-trivial standardized coefficient after structure is partialled out — but
  the *incremental fit* it buys is still only ΔMcFadden 0.003, because frequency
  is itself ~0.47-correlated with out-degree, so most of its signal is already
  in block 1. (Concreteness/AoA contribute nothing once frequency and structure
  are present.)

### (d) layer index among Kernel nodes
n = 6,899; layer ranges 0–64, over-dispersed.
- OLS on log1p(layer): R² block 1 = **0.238**, block 2 alone = 0.069, block 1+2
  = **0.245** → **incremental block 2 R² = +0.0066**.
- Poisson on layer: pseudo-R² block 1 = 0.228, block 2 alone = 0.080, block 1+2
  = 0.238 → **incremental block 2 pseudo-R² = +0.0098**.
- Block-2 standardized coefficients (OLS on log1p(layer), after block 1):
  frequency **−0.101** (more frequent → shallower layer — the expected sign,
  and the largest psych effect here), age_of_acquisition +0.009 (essentially
  zero — the Vincent-Lamarre "deeper = later acquired" effect *does not survive*
  controlling for structure), concreteness +0.070 (more concrete → slightly
  *deeper*, the "wrong" sign for a naive grounding story, and small).
- So: structure explains ~24% of (log) layer variance; the psycholinguistic
  block adds ~0.7–1.0 percentage points on top. Below the 0.05 threshold.

**Across (a)–(d): incremental block-2 R²/pseudo-R²/AUC ∈ [0.0001, 0.010].**

---

## 4. The Yoneda / Harnad verdict

**Verdict: empirical weight *against* a large non-relational residue —
i.e. mildly pro-"Yoneda-completeness" — but a weak instrument, exactly as the
prior report ( `swanson-yoneda-harnad-findings.md` §4.4) warned.**

Per the pre-registered decision rule (§4.3 of that report): incremental
extra-graph R² **> ~0.05** ⇒ thumb for Harnad / against Yoneda-completeness;
**< ~0.01** ⇒ pro-Yoneda (the psycholinguistic signal *is* the structural
signal, screened off by degree/PageRank/SCC structure); in between ⇒ "graded
grounding". **Every outcome lands in the < 0.01 regime.** Kernel membership and
Core/Satellite are essentially *deterministic* graph properties (AUC 0.98–1.00
from structure alone); seed-membership and layer-depth leave ~0.5–1.0 percentage
points of variance for the psycholinguistic block, and even there it's mostly
frequency, which is ~half-redundant with out-degree.

So: **the variance in "which layer / which membership class a word lands in" is
almost entirely recoverable from the relational structure.** A structuralist /
inferential-role-semantics reading of the dictionary graph is *consistent* with
this. A "meaning has a big sensorimotor residue the relations miss" reading
predicts a residue the data doesn't show — *at the scale of this graph and these
norms*.

**But this is light evidence, for the reasons in §6 — and crucially because of
the confound in §6.3.** The result does **not** show "meaning is Yoneda-complete";
it shows "a definitional digraph plus three lexical norms leaves no large
*independent* extra-graph signal for definitional depth", which is a much
narrower claim and is exactly what Resolution A ("grounding = constructing the
base category; Yoneda applies inside it; the only residue is the
category-selection residue, not an object-identity-within-the-category residue")
predicts. The verdict therefore confirms Resolution A's framing without moving
the needle on the philosophical dispute.

---

## 5. The Perron–Frobenius leg

**Question (`swanson-perron-frobenius-findings.md` §3f):** does reverse-PageRank
(the hub-side eigenvector — the one the prior report *predicted* would track the
combinatorial seed) or the FVS seed itself predict AoA / concreteness /
frequency *better than raw out-degree does*? Codex's point to address head-on:
degree explains most of it.

**Answer: no — reverse-PageRank is a near-perfect re-skin of out-degree, and the
FVS seed adds almost nothing over out-degree.**

| Norm | R²(log_outdeg) | +log_indeg | +revPR | **incr revPR over outdeg** | **incr revPR over (out+in)deg** | +seed | **incr seed over outdeg** |
|---|---:|---:|---:|---:|---:|---:|---:|
| frequency (Zipf) | 0.2252 | 0.2253 | 0.2345 | **+0.0093** | +0.0092 | 0.2310 | **+0.0058** |
| age_of_acquisition | 0.0797 | 0.0800 | 0.0820 | **+0.0023** | +0.0022 | 0.0826 | **+0.0029** |
| concreteness | 0.0019 | 0.0302 | 0.0326 | **+0.0307** | +0.0253 | 0.0019 | **+0.0001** |

Raw Pearson with each norm: out-degree 0.475 / −0.282 / 0.043; reverse-PageRank
0.465 / −0.272 / −0.044; forward (authority) PageRank 0.013 / −0.007 / 0.125;
in-degree 0.041 / −0.015 / 0.172. So:
- **Out-degree is the workhorse.** "How many definitions a word appears in" is a
  good frequency proxy (r = 0.47) and a moderate AoA proxy (r = −0.28). This is
  Codex's point, confirmed.
- **Reverse-PageRank ≈ out-degree.** Its Pearson with every norm is within 0.01
  of out-degree's. Its incremental R² over out-degree is +0.009 / +0.002 for
  frequency / AoA — i.e. a rounding error. **So the prior report's prediction
  that reverse-PageRank would "approximately recover the combinatorial seed
  ordering" is true (both are out-flow objects), but it buys essentially nothing
  *extra* as a psycholinguistic predictor — it's the same signal out-degree
  already had.**
- **The FVS seed adds ~nothing over out-degree** as a predictor of any norm
  (incremental R² 0.0001–0.006). Seed nodes *are* more frequent / earlier
  acquired on average (Zipf 4.18 vs 3.04; AoA 7.75 vs 9.90), but that's because
  high-out-degree words are both (a) chosen by the FVS heuristic and (b)
  frequent/early — the seed membership carries no independent signal.
- **The concreteness "+0.031" is a suppression artifact, not a finding.**
  Out-degree alone explains ~0.2% of concreteness variance; in-degree explains
  ~3% (concrete things are pointed *at* by many definitions, r = 0.17); revPR is
  −0.044-correlated with concreteness on its own. The 0.031 increment when
  revPR is added *to out-degree* comes from revPR partially proxying in-degree
  (revPR is the eigenvector of out+in flow), letting the pair pick up the
  in-degree signal — incremental-over-(out+in)-degree it's only +0.025, and the
  honest statement is "concreteness tracks *in*-degree (being a definitional
  target), not out-degree or revPR". So even the one place revPR "wins", it's
  not winning *as* a hub measure.

**PF-leg verdict:** the Perron–Frobenius / reverse-PageRank object **does not**
beat raw out-degree as a "soft foundationalness" signal that tracks
psycholinguistic norms; it *is* raw out-degree, spectrally laundered. The
combinatorial FVS seed likewise adds nothing over out-degree. **Codex's
"degree explains most of it" is correct and the spectral machinery does not
overturn it.** What survives is the structural-vs-flow distinction (out-flow
measures — out-degree, reverse-PageRank, FVS seed — all track frequency/AoA;
authority-PageRank doesn't), and the descriptive component means (seed and
Kernel words are more frequent, earlier acquired, but *not* more concrete:
mean concreteness is essentially flat across seed/Kernel/Rest, 3.18–3.28).

(Layer vs norm among Kernel nodes, for completeness: Pearson(layer, frequency) =
−0.167 (deeper → less frequent — the expected sign), Pearson(layer, AoA) =
+0.087 (deeper → slightly later acquired — the Vincent-Lamarre direction, weak),
Pearson(layer, concreteness) = +0.178 (deeper → *more* concrete — opposite the
naive prediction; deep-tail technical nouns like chemical compounds are
concrete). These are *bivariate* — once structure is partialled out (model d),
the AoA effect vanishes and frequency stays small.)

---

## 6. What the regression can and cannot conclude — the confounds

### 6.1 The graph isn't a category
Yoneda is a theorem about categories (objects, morphisms, composition,
identities, functoriality). The OEWN definition digraph has none of that — it's
"lemma X's definition mentions lemma Y". So "the regression adjudicates Yoneda"
is, strictly, a category error (Codex Brief 4: "treating a theorem about
mathematical representation as if it were a thesis about cognitive semantics").
The most the regression can say is about the *digraph*: how much of definitional
depth is internal to the digraph vs. predictable from outside it.

### 6.2 "Layer" and "membership" are themselves structural
Layer index = definitional distance from the seed *in the digraph*. Kernel/Core/
Satellite membership = SCC-structure properties. So "do structural features
predict layer/membership" is close to tautological for some of these (Core is
*defined* by SCC structure → AUC 1.00). The only non-trivial version is the
*residual* one — "after the obvious structural predictors, is there extra-graph
signal?" — which is what we ran (the partial-R² of block 2). It's small. But the
near-tautology means the *level* of block-1 fit (0.98 AUC etc.) is not itself
evidence of anything; only the *increment* is informative, and the increment is
~0.

### 6.3 The decisive confound: the structure was built *for* learners
This is Codex's Brief 4/5 caveat and it is the binding one. OEWN definitions are
written by lexicographers *for human learners*. A concrete, early-acquired,
frequent word gets used as a definer precisely *because* the lexicographer
expects the reader to know it — which gives it high out-degree and a shallow
layer. So the structural features are **not independent of** the psycholinguistic
features; they are (partly) *caused by* them. Therefore:

- "Block 2 adds nothing over block 1" is **equally consistent with** (i) "word
  meaning is relational, so once you have the relations there's nothing left"
  *and* (ii) "the relations were *constructed from* psycholinguistic salience,
  so of course they screen it off — the salience is *in* the structure, not
  *missing* from it". These are causally opposite stories with the same
  regression signature.
- The regression therefore **cannot** support "meaning is Yoneda-complete". It
  can only refute a *strong* Harnad-flavoured claim: "there is a large
  *independent* extra-graph (sensorimotor) signal that the definitional
  relations fail to capture". That strong claim predicts incremental R² ≫ 0.05;
  we see ≤ 0.01. So the *strong* residue claim is not supported by *this*
  artifact. The *weak* claim ("the digraph under-describes word meaning in ways
  these three lexical norms can't detect") is untouched, and is in fact what
  everyone — Harnad included — already grants.
- A clean test would need an extra-graph signal that is **plausibly causally
  upstream of, not downstream of, the lexicographic process** — e.g. raw
  perceptual/sensorimotor ratings (Lancaster sensorimotor norms; sensory-
  experience ratings) used as an *instrument*, or a comparison across
  dictionaries written under different editorial policies. We don't have that
  here.

### 6.4 Other limitations
- Norms are **lemma-level**; we attach a lemma's value to all its `lemma::pos`
  senses. Polysemy is collapsed at the value level.
- Coverage is **non-random** (53.7% of Kernel, 17.1% of all nodes; the missing
  are disproportionately multiword/proper-noun/technical, which are also
  disproportionately deep-layer Satellites). The within-Kernel models (b, d) are
  biased toward better-covered shallow/mid layers; coverage in L11+ is ~10
  points below L1–10.
- In-sample R²/AUC (no held-out split). For a partial-R²-of-0.007 result the
  optimism bias is irrelevant to the verdict (it would only inflate, not
  deflate, block 2's apparent contribution — and it's still ~0).
- Logistic fits hit separation on the near-deterministic outcomes; AUC and
  increments are robust, coefficient SEs on the separated Core model are not
  (table omitted).

---

## 7. What would change the conclusion

- **Incremental block-2 R² > ~0.05 on layer/seed-membership with a
  causally-upstream sensorimotor norm** (Lancaster sensorimotor; SER; a
  perceptual-strength composite used as an instrument, not just AoA/concreteness
  which are themselves lexicographer-visible) → genuine thumb for Harnad. We
  don't have such a norm joined here; this is the single highest-value follow-up.
- **A within-Kernel result where, after structure, concreteness keeps a large
  *and correctly-signed* standardized coefficient** (more concrete → shallower).
  We see +0.070 (wrong sign) for layer; if a better-disambiguated graph or
  sense-level norms flipped that to a sizable negative, the picture changes.
- **A cross-dictionary comparison** (OEWN vs a dictionary written under a
  different controlled-defining-vocabulary policy, e.g. Longman LDOCE's 2,000-
  word defining vocabulary): if the "structure screens off psycholinguistics"
  result *disappears* when the defining vocabulary isn't hand-tuned for
  learners, that would show the screening-off was an artifact of editorial
  policy (confound 6.3 confirmed) rather than evidence about meaning.
- **For the PF leg:** reverse-PageRank or the FVS seed showing incremental R² ≫
  the +0.009 / +0.006 we got, over the full degree baseline (out + in), on
  *frequency or AoA* — that would resurrect "soft grounding vocabulary". It
  didn't here; the spectral object is degree in a fancy hat.
- A held-out / cross-validated version (folds over lemmas) confirming the
  in-sample increments aren't even *that* big — expected to make block 2's
  contribution shrink further, not grow.

---

## Appendix: files

- `scripts/psycholinguistic_regression.py` — reproduces everything below.
- `reports/psycholinguistic-regression-output.json` — full numeric output
  (coverage, all four models with coefficients/AUC/pseudo-R², the PF leg, norm
  means by component).
- `reports/psycholinguistic-regression-run.log` — console log of the run.
- Inputs (read-only here): `data/psycholinguistic/{frequency,age_of_acquisition,concreteness}.csv`;
  graph + kernel via `meanings.wordnet_pipeline.build_paper_wordnet_graph` and
  `meanings.graph_analysis.analyze_kernel` (`exact-small-greedy`, `source-union`);
  PageRank via `meanings.spectral_analysis.perron_scores`.
- Dependencies added: `scikit-learn`, `statsmodels` (+ scipy, patsy, joblib —
  all in `pyproject.toml` / `uv.lock`).
- `pytest`: 10 passed before and after.
