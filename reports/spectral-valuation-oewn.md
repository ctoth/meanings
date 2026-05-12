# Spectral valuation of the OEWN definition digraph — the reverse-PageRank test

**Date:** 2026-05-12
**Type:** computation + verdict on a standing prediction
**Reproduce:** `uv run python scripts/spectral_report.py` → writes `reports/spectral-valuation-oewn.json`; numbers below are from that run (`reports/spectral-report-run.log`). Module: `src/meanings/spectral_analysis.py`. Graph: `build_paper_wordnet_graph()` on `oewn:2024` (the same surface the repo computes the combinatorial kernel/seed on).

> **Numbers refreshed after the `compute_kernel` self-loop fix (commit 7d12e64).** 3,413 gloss self-loops (words appearing in their own definition) are now kept in the Kernel as 1-node cycles, so the Kernel grew 12,853 → 18,151, the seed 2,370 → 5,044, etc. **The qualitative verdict is unchanged** — reverse-PageRank ≈ out-degree, both ≈ degree, ρ(reverse-PageRank, FVS-degree-key) ≈ 0.37 not > 0.6 — but several kernel-restricted Spearman ρ's shifted (notably ρ(reverse-PageRank, seed-membership) flipped sign, +0.11 → −0.18, and ρ(reverse-PageRank, layer-shallowness) collapsed +0.26 → ~0, because the enlarged seed/layer-0 is now dominated by low-centrality self-loop sink-leaves). Watch-word ranks on the full digraph and inside the 8,138-node SCC are untouched (those surfaces don't change). See `reports/self-loop-fix-impact.md` for the full before/after.

This report executes the open prediction in `reports/swanson-perron-frobenius-findings.md` §3g/§4b and Codex's "Independent Contribution 1" (Predictions A–D) in `reports/codex-swanson-review.md`. The standing claim under test:

> The combinatorial feedback-vertex seed is an *out-flow* object (`choose_feedback_vertex` maximises `internal_out + internal_in`), so the matching spectral object is **reverse-PageRank on the kernel** (PageRank on the transposed digraph), not authority-side PageRank. Predicted: reverse-PageRank ranks `small`/`large`/`white`/`plant`/`body`/`water` near the top, and Spearman ρ with the seed's degree-score > 0.6.

---

## 0. Verdict in one paragraph

**Half confirmed, half not — and the failing half is informative.** The *top-words* half of the prediction holds emphatically: reverse-PageRank on the full digraph ranks `act` at percentile **0.001 %** (rank 1 / 160 010), `part` **0.003 %** (5), `large` **0.017 %** (27), `body` **0.018 %** (29), `small` **0.041 %** (66), `water` **0.082 %** (132), `form` **0.085 %** (136), `plant` **0.094 %** (151), `white` **0.295 %** (472) — every combinatorial-seed hub the prior report named is in the top **0.3 %**, most in the top **0.05 %**. Its top-15 is `situated*, act, degree, time, event, part, place, can, quality, quantity, extent, point, relation, things, distinguished, …` — the abstract genus vocabulary, exactly what the FVS heuristic picks. **But** Spearman ρ(reverse-PageRank, FVS degree-score) over the kernel is only **0.371**, not > 0.6. The reason is visible: on this graph reverse-PageRank ≈ pure out-degree (ρ with out-degree = **0.995** on the full graph, **0.797** on the kernel; ρ with in-degree ≈ **−0.05 / −0.21**), whereas the FVS key is `internal_out + internal_in` — it also rewards in-degree. So the two objects **agree at the very top** (the mega-hubs that dominate both out-flow and total degree) and **diverge in the long tail** (where a node's in-degree contribution to the FVS score has no analogue in reverse-PageRank). The honest restatement: **reverse-PageRank is the eigenvector relaxation of the *out-flow* component of the FVS heuristic — and that component dominates at the top — but it is not a rank-faithful proxy for the full `out+in` heuristic across the whole kernel.** Authority-side (forward) PageRank remains a non-starter for this question (its top is sink-like proper-noun leaves: `magnificat, palaquium_gutta, coelogyne, niobe, crusade(v), laocoon`; `small` sits at percentile **49 %**). (`situated::a` has out-degree 124 from a prolific gloss template — a mild artefact; the rest of the top is exactly the abstract genus vocabulary. Pre-fix the kernel ρ(reverse-PageRank, FVS) read 0.316 / out-degree 0.746 — the post-fix figures are 0.371 / 0.797; conclusion unchanged.)

---

## 1. The numbers

### 1a. Graph / combinatorial baseline (re-confirmed this run, post the self-loop fix)
- Nodes (lemma::pos): **160 010** · directed edges: **677 823** (`u → v` = "u occurs in the definition of v").
- Kernel: **18 151** · kernel SCCs: **9 139** (one giant SCC of **8 138** — unchanged — then 1×11, 1×10, 3×6, 7×5, 23×4, 87×3, 570×2, **8 446 singletons** — the singleton count jumps from 3,148 because the self-loop nodes are now 1-node cyclic SCCs) · source SCCs: **508**.
- Core (union of source SCCs): **510** · Satellites: **17 641** · combinatorial seed (`exact-small-greedy`): **5 044**; residual cyclic SCCs after the seed: **0**; layers in the seeded-kernel DAG: **65**.
- Un-damped dominant eigenvalue of the 8 138-node SCC adjacency matrix: **λ\* ≈ 3.744** (same forward and reverse — λ(A) = λ(Aᵀ)).
- Nontrivial SCCs of the *reverse-oriented* kernel: **3 497** (these are the small loops + the self-loop singletons that get their own per-block Perron eigenvector; pre-fix the count was 823).
- (Pre-fix baseline for the lines above: Kernel 12,853, kernel SCCs 3,841 with 3,148 singletons, source SCCs 286, Core 288, Satellites 12,565, seed 2,370.)

### 1b. The four spectral variants vs the baselines (Spearman ρ over the **kernel**, 18 151 nodes)

| spectral score | vs FVS degree-score `out+in` | vs seed membership | vs Core membership | vs in-degree | vs out-degree | vs layer-shallowness | overlap@500 with FVS top | seed recall@2370 |
|---|---|---|---|---|---|---|---|---|
| **reverse PageRank, full graph** | **0.371** | −0.183 | 0.073 | −0.209 | **0.797** | 0.004 | 0.319 | 0.173 |
| forward (authority) PageRank, full graph | 0.004 | 0.489 | −0.144 | 0.430 | −0.441 | 0.141 | 0.000 | 0.359 |
| un-damped Perron, largest kernel SCC, **reverse** | **0.397** | 0.274 | — (Core ∉ SCC) | −0.031 | 0.405 | 0.284 | 0.292 | 0.160 |
| un-damped Perron, largest kernel SCC, forward | 0.395 | 0.119 | — | **0.761** | 0.055 | −0.168 | 0.058 | 0.116 |

(Core membership ρ is undefined for the largest-SCC scores because the Core — the 508 source SCCs — is disjoint from the giant SCC by construction; that is itself Codex's Prediction B coming true: under `source-union` Core policy the Core does *not* sit at the top of the giant block.)

Pre-fix (12,853-node kernel) the table read: reverse-PR 0.316 / +0.106 / 0.044 / −0.194 / 0.746 / 0.258 / 0.340 / 0.368; forward-PR 0.249 / 0.276 / −0.229 / 0.530 / −0.282 / −0.157 / 0.006 / 0.388; Perron-rev 0.404 / 0.274 / — / −0.031 / 0.405 / 0.284 / 0.312 / 0.341; Perron-fwd 0.445 / 0.119 / — / 0.761 / 0.055 / −0.168 / 0.065 / 0.247. **What moved (and why):** reverse-PR-vs-seed-membership flipped +0.11 → **−0.18**, and reverse-PR-vs-layer-shallowness collapsed +0.26 → **~0**, because the enlarged seed (= layer 0) now contains the ~2,800 low-centrality gloss-self-loop sink-leaves that reverse-PageRank scores *low* — so "being in the seed" / "being shallow" now anti-correlates slightly with reverse-PageRank. forward-PR-vs-seed-membership *rose* (+0.28 → +0.49) for the mirror reason: forward PageRank ranks those sink-leaves *high*, and they're now in the seed. The ρ-with-degree, ρ-with-FVS-key, and overlap@k figures barely moved — the headline conclusion (reverse-PR ≈ out-degree at the top, ρ(reverse-PR, FVS-key) ≈ 0.37 ≪ 0.6) is unchanged. (Pre-fix `seed recall@2370` was over the then-2,370-node seed; now it's over the 5,044-node seed, so the recall *denominator* changed too — the numbers aren't directly comparable.)

### 1c. Where the watch-words land

| word | reverse PageRank (rank / 160 010) | forward PageRank | reverse-Perron on 8 138-SCC (rank / 8 138) | FVS degree-score (rank / 18 151, reference) |
|---|---|---|---|---|
| `small`  | **66**  (p0.04 %) | 78 880 (p49 %)  | 345  (p4.2 %) | **2** |
| `large`  | **27**  (p0.02 %) | 14 433 (p9 %)   | 29   (p0.4 %) | **5** |
| `white`  | 472     (p0.30 %) | 9 998  (p6 %)   | 2 309 (p28 %) | 15 |
| `plant`  | **151** (p0.09 %) | 109 189 (p68 %) | 259  (p3.2 %) | **8** |
| `body`   | **29**  (p0.02 %) | 70 257 (p44 %)  | 21   (p0.3 %) | **6** |
| `water`  | **132** (p0.08 %) | 36 046 (p23 %)  | 232  (p2.9 %) | **11** |
| `act`    | **1**   (p0.001 %)| 77 118 (p48 %)  | 1    (p0.01 %)| **0** (top) |
| `part`   | **5**   (p0.003 %)| 127 926 (p80 %) | 6    (p0.07 %)| **4** |

(reverse-PageRank and reverse-Perron ranks are on surfaces the self-loop fix doesn't touch — full digraph / the 8,138-node SCC — so they're identical to the pre-fix run. The FVS-degree-score column moved a little because the kernel's node ordering by `out+in` shifted slightly with the enlarged kernel — pre-fix: small 4, large 7, white 27, plant 14, body 2, water 6. `act`/`part` are still pinned at the top under every measure.)

### 1d. Top-15 lists (qualitative — unchanged in character from the pre-fix run)
- **reverse PageRank, full graph:** `situated(a)`*, `act(n)`, `degree(n)`, `time(n)`, `event(n)`, `part(n)`, `place(n)`, `can(n)`, `quality(n)`, `quantity(n)`, `extent(n)`, `point(n)`, `relation(n)`, `things(n)`, `distinguished(a)`. (* `situated` has out-degree 124 from one prolific gloss template — a mild artefact; the rest are exactly the abstract genus vocabulary.)
- **un-damped Perron, largest SCC, reverse:** `can(n)`, `act(n)`, `degree(n)`, `extent(n)`, `quantity(n)`, `things(n)`, `part(n)`, `quality(n)`, `energy(n)`, `amount(n)`.
- **FVS degree-score, kernel (the heuristic's own key):** `act(n)` 383, `trade_name(n)` 261, `small(n)` 259, `various(a)` 239, `part(n)` 231, `large(n)` 221, `body(n)` 215, `can(n)` 212, `plant(n)` 199, `make(v)` 197, `form(n)` 192, `water(n)` 184. (Pre-fix the list was `act` 305, `part` 199, `body` 176, `can` 171, `small` 162, `form` 152, `water` 144, `large` 132, `various` 122, `substance` 120 — same vocabulary, slightly higher scores and a reorder because the bigger kernel adds more internal edges.)
- **forward (authority) PageRank, full graph:** `magnificat(n)` (in 5/out 1), `palaquium_gutta(n)`, `coelogyne(n)`, `niobe(n)`, `crusade(v)`, `laocoon(n)`, `regression_coefficient(n)`, `kwell(n)`, `barber(v)`, `brattice(v)` — definitional **sinks**, out-degree 1; now *in* the enlarged seed (each is a 1-node self-loop), but still the wrong words for "how foundational."
- **un-damped Perron, largest SCC, forward:** `potassium`, `alkali_metal`/`alkaline_metal`, `rubidium`, `kainite`, `pitressin`/`vasopressin`, `vasoconstrictor`, `stops`(card game), `sodium`, `magnesium`, … — dense technical micro-cliques, **not** foundational vocabulary (eigenvector localisation; ρ with SCC-internal in-degree = 0.76, so largely a re-skin of in-degree on that block).

So qualitatively reverse-PageRank ≈ FVS-seed *at the top*; the modest ρ is a tail effect, not a top effect. The overlap@k between reverse-PageRank and the FVS top grows from 0.20 @50 to 0.37 @2370 (pre-fix 0.25 → 0.37) — consistent with "they're picking the same hubs but in a different bulk order."

### 1e. Orientation contrast (full graph, all 160 010 nodes)
- reverse PageRank vs **out-degree**: ρ = **0.995**; vs in-degree: ρ = −0.047; vs total degree: ρ = 0.511.
- forward PageRank vs **in-degree**: ρ = **0.396**; vs out-degree: ρ = −0.028.
- reverse PageRank vs forward PageRank: ρ = **−0.027** — the two orientations are essentially **orthogonal**.

### 1f. Null models (on the kernel, reverse orientation)
- reverse-PageRank(real kernel) vs reverse-PageRank(degree-preserving edge-swapped kernel): ρ = **0.613** (pre-fix 0.521).
- reverse-PageRank(real) vs total-degree: ρ = **0.692** (pre-fix 0.679).
- edge-swapped-null vs total-degree: ρ = **0.612** (pre-fix 0.518).
- Reading: the real reverse-PageRank ranking is *mostly* recoverable from degree alone (ρ 0.69), and the degree-preserving null reproduces ≈ 0.61 of it — i.e. the structural signal beyond degree is small. This is Codex's null-model warning landing: **reverse-PageRank here adds little over out-degree.** That does *not* refute the "matching object" claim — the FVS heuristic *also* adds little over `out+in` degree, by construction — but it does mean neither object is a deep spectral discovery; both are degree dressed up. (The null-vs-degree ρ rose post-fix mainly because the enlarged kernel has many more low-degree singleton-SCC nodes, on which both the real ranking and the null collapse to "degree" more tightly.)
- Layer index vs label-shuffled layer index: ρ = **−0.002** (sanity check that the layer-shuffle null is a real null).

### 1g. Small-SCC eigenvectors (the per-block Perron vectors, reverse orientation)
3 497 nontrivial reverse-oriented kernel SCCs (pre-fix 823 — the increase is mostly the gloss-self-loop singletons). Examples (top members by within-block score; unchanged from the pre-fix run):
- size 11, λ ≈ 1.93: `eighth/ninth/seventh/tenth/sixth/fifth (a)` — the ordinal-adjective loop.
- size 10, λ ≈ 1.47: `subdivision_basidiomycota/gasteromycetes/basidium/hymenomycetes/stinkhorn/basidiomycetes (n)` — mycology.
- size 6, λ ≈ 2.04: `niobite/tantalum/niobium/fergusonite/tantalite/columbium (n)` — mineralogy.
- size 6, λ ≈ 1.80: `zinc_sulfide/sphalerite/wurtzite/zinc/zinc_blende/zinc_sulphide (n)`.
- size 6, λ ≈ 1.22: `cucurbitaceae/cucumber/squash/cucurbita/melon_vine/cucurbitaceous`.

These are "small-SCC specialists" (Codex Prediction B): high within-block centrality, negligible global centrality — domain micro-vocabularies, not grounding vocabulary.

---

## 2. The two orientations, named (Codex Prediction C)

Edge convention `u → v` = "u occurs in the definition of v". The two dominant eigenvectors answer different questions and are nearly orthogonal here (ρ ≈ −0.03):

- **Forward / authority PageRank** (`defining → defined`): score flows *toward* the words you help define. A node scores high when it is *pointed at by important nodes* — on this digraph that means it is a **definitional sink** (out-degree ≈ 1: it appears in essentially no other gloss, mass pools there). Substantively this is **"dependency on already-important definers"** — and its top is rare technical proper nouns (`magnificat`, `niobe`, `laocoon`). It is the *wrong* eigenvector for "how foundational is this word."
- **Reverse PageRank** (`defined → defining`, i.e. PageRank on the transpose): score flows *back to* the words that define you. A node scores high when it *occurs in the definitions of many / important words* — i.e. high **definitional productivity / downstream use**. Its top *is* the abstract genus vocabulary (`act, degree, time, part, place, can, quality, quantity, …`, plus `small/large/body/plant/water/white` all in the top 0.3 %). This is the eigenvector relaxation of the *out-flow* half of the FVS heuristic, and the half that dominates at the top.

A report that uses only one of these "smuggles in a theory of importance through edge orientation" (Codex's phrasing). The grounding question wants the **reverse** orientation; the spectral-citation lineage (authority PageRank, HITS authorities) is the **forward** one — which is one reason the naive "Perron eigenvector = soft grounding vocabulary" import fails: it imported the wrong orientation along with the algebra.

---

## 3. Predictions A–D — outcomes

- **A (Perron rank ∩ FVS membership: overlap, not coincidence): CONFIRMED.** Reverse-PageRank's overlap@500 with the FVS top = 0.32 (and overlap@2370 = 0.37); the seed-recall figures aren't directly comparable to the pre-fix run because the seed grew (2,370 → 5,044), but the *top overlap* is substantial and far from identity. The exact-small-greedy seed *also* contains low-centrality cycle-bottleneck nodes (it must hit the thousands of small / 1-node loops, whose members are globally peripheral), which is why the overlap with the spectral top stays around 0.3–0.37.
- **B (Core/Satellite splits by spectral role): CONFIRMED.** Under `source-union` Core policy the Core (508 source SCCs, 510 nodes) is *disjoint* from the 8 138-node giant block, so it cannot be at the top of the giant block's Perron vector (ρ undefined there); forward PageRank ρ with Core membership is *negative* (−0.14). Satellites split into peripheral low-score nodes and the small-SCC specialists of §1g.
- **C (orientation exposes two foundationalnesses): CONFIRMED and computed both** — §2; the two are ρ ≈ −0.03 orthogonal.
- **D (damping less informative than Frobenius normal form): PARTLY.** The condensation/per-block view *is* the principled object (and we computed per-block eigenvectors for all 3,497 nontrivial SCCs + the giant one). But the headline finding is that *neither* the damped full-graph PageRank *nor* the un-damped giant-block eigenvector recovers grounding vocabulary on the **forward** orientation; only the **reverse** orientation does, and on the reverse orientation the damped full-graph version actually works *better* for the watch-words than the un-damped largest-SCC version (`small` p0.04 % vs p4.2 %, `plant` p0.09 % vs p3.2 %), because restricting to the 8 138-node SCC drops the satellite hubs that the seed also names. So "Frobenius normal form > damping" is not borne out *as a ranking-quality claim*; what is borne out is "Frobenius normal form tells you *where Perron–Frobenius is licensed*" — a structural, not a ranking, advantage.

---

## 4. What `src/meanings/spectral_analysis.py` provides

- `perron_scores(adjacency, nodes, *, orientation, component_policy, damping=0.85, iters, tol) -> SpectralResult` — the spec'd entry point. `orientation ∈ {"forward","reverse"}`; `component_policy ∈ {"damped-full","largest-scc","scc-local","raw"}`. `damped-full` = teleported PageRank over the whole node set; `largest-scc` = un-damped power iteration on the largest SCC of the oriented graph (a genuine Perron eigenvector of an irreducible block, with `dominant_eigenvalue`); `scc-local` = union of per-block un-damped eigenvectors for every nontrivial SCC; `raw` = un-damped over the whole (possibly reducible) graph, for diagnostics only. `SpectralResult` carries `scores`, `orientation`, `component_policy`, `damping`, `dominant_eigenvalue`, `converged`, `iterations`, `scope_nodes`, `notes`.
- `scc_local_eigenvectors(adjacency, nodes, *, min_size=2, iters, tol)` — list of `{scores, dominant_eigenvalue, size, converged, iterations}` per nontrivial SCC, largest first; cross-block magnitudes explicitly non-comparable.
- Null models: `degree_rank_scores(adjacency, nodes, *, mode∈{in,out,total})`; `randomized_edge_null(...)` — degree-preserving directed double-edge-swap rewiring then re-run `perron_scores` (preserves every node's in- and out-degree exactly); `label_shuffled_layers(layer_by_node, *, seed)` — permutes layer labels, preserving the layer-size histogram.
- Comparison helpers: `spearman` (tie-correct, Pearson-on-ranks form), `overlap_at_k` (Jaccard of top-k over common keys), `rank_positions`.
- All pure-Python (the environment has no numpy); reuses `meanings.graph_analysis` for SCCs / reverse-adjacency / induced subgraphs and `meanings.wordnet_pipeline.build_paper_wordnet_graph` for the graph (no reimplementation).
- `scripts/spectral_report.py` is the CLI hook: builds the graph, runs all four variants + the edge-swap null, emits `reports/spectral-valuation-oewn.json` and a console summary with the explicit reverse-PageRank verdict.
- Tests: the repo had **no test suite** before (`uv run pytest` collected 0 items; the project venv does not even bundle pytest — `uv run pytest` resolves to a global one). Added `conftest.py` (puts `src/` on `sys.path` so an external pytest can import `meanings`) and `tests/test_spectral_analysis.py` (7 smoke tests: orientation flag, forward≠reverse rankings, symmetric-cycle Perron vector is uniform with λ≈1, `scc_local_eigenvectors` finds the cycle, degree null + overlap helpers, Spearman ±1 extremes, edge-swap null preserves degrees). `uv run pytest` → **7 passed**. Nothing else exists to break.

---

## 5. What this means for the "Discrete Grounding and Spectral Valuation" paper

1. **State the link in the reverse orientation, and weakly.** The correct statement is *not* "reverse-PageRank is the continuous tie-free relaxation of the FVS seed" (ρ = 0.37 says it isn't, rank-faithfully). It is: **"reverse-PageRank is the eigenvector relaxation of the *out-flow* component of the FVS heuristic; that component dominates at the top, so the two methods agree on *which words are foundational genus terms* (`act, part, body, can, small, form, water, large, …`) while disagreeing on their precise ordering."** The headline figure is the scatter: x = FVS degree-score (kernel), y = reverse-PageRank rank — a tight elbow at the top (the shared hubs), fanning out below; with the forward-PageRank panel beside it showing the seed hubs piled in the bottom-right (high FVS score, near-worst authority rank), the contrast Codex asked for.
2. **The orientation point is the real contribution to the spectral-citation literature.** Authority PageRank / HITS authorities are the *forward* eigenvector; the dictionary-grounding question wants the *reverse* one; the two are orthogonal on OEWN. The naive "import PageRank as a grounding anchor" move silently imported the wrong orientation. That is a clean, citable observation and it generalises to any "what's foundational in this definitional/dependency graph" question.
3. **Both objects are degree in a thin disguise — say so.** Reverse-PageRank ρ with out-degree = 0.99 (full) / 0.80 (kernel); the degree-preserving edge-swap null recovers ρ ≈ 0.61 of the real ranking. The FVS heuristic key *is* literally a degree sum. So the honest framing is "two complementary *degree-based* foundationalness scores — one discrete (a cycle-hitting set), one continuous (an eigenvector) — that coincide at the top because mega-hubs dominate both," not "a deep spectral law of dictionaries." The incremental-value-over-degree bar (Codex) is **not cleared** by either method; that's a finding, not a gap to paper over.
4. **Frobenius normal form's value is structural, not rank-quality.** Per-block Perron eigenvectors (3,497 nontrivial kernel SCCs + the 8 138-node giant block, all computed) tell you *where Perron–Frobenius is licensed* and reproduce the Core/Satellite split by construction — a consistency result, not a better ranking. On the reverse orientation the *damped full-graph* PageRank actually ranks the watch-words better than the largest-SCC eigenvector (it keeps the satellite hubs the seed also names). So "use the condensation, not damping" survives only as "use the condensation to know what's licensed," not as "the condensation gives a better grounding score."
5. **Forward-Perron localisation is a cautionary tale worth one paragraph.** The un-damped dominant eigenvector of the 8 138-node SCC (forward) localises on `potassium/alkali_metal/rubidium…` and `vasoconstrictor/vasopressin/angiotensin…` — dense technical micro-cliques (ρ 0.76 with internal in-degree). This is textbook eigenvector-centrality localisation and is *direct evidence against* using the dominant eigenvector as a global semantic-foundationalness signal — exactly the non-backtracking-centrality warning literature Codex flagged.

---

## Appendix: what ran / what didn't

- **Ran (re-run post the `compute_kernel` self-loop fix, commit 7d12e64):** `scripts/spectral_report.py` on `oewn:2024` (locally cached via `wn`): forward + reverse damped PageRank on the 160 010-node digraph (converged, tol 1e-12); un-damped Perron on the 8 138-node giant kernel SCC, both orientations (λ ≈ 3.744); 3,497 per-block reverse eigenvectors; degree-preserving edge-swap null on the (now 18,151-node) kernel (561 928 swaps); all Spearman/overlap comparisons; full output in `reports/spectral-valuation-oewn.json` (regenerated), console log in `reports/spectral-report-run.log` (regenerated).
- **Didn't run / couldn't:** psycholinguistic overlay — still no annotation CSVs bundled (`reports/annotation-sources.md`; coverage 0/160 010). `spectral_analysis.py` exposes everything needed to join such data when present, but it isn't here. Used in-/out-degree as the only available null/proxy, as before.
- **Not committed** (per instruction).
