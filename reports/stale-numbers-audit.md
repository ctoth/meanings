# Stale-numbers audit — refresh after the `compute_kernel` self-loop fix (commit 7d12e64)

**Date:** 2026-05-12
**Trigger:** commit 7d12e64 ("Fix compute_kernel: treat a self-loop as a cycle") changed the OEWN `paper-wordnet` Kernel decomposition. Several reports still quoted the pre-fix figures; this pass updated them and regenerated the computations whose JSON outputs were stale.

## The number change, in one table

| quantity | pre-fix | post-fix | source |
|---|---:|---:|---|
| paper-wordnet nodes / edges | 160,010 / 677,823 | 160,010 / 677,823 | (unchanged) |
| gloss self-loops | — | 3,413 | `reports/self-loop-fix-impact.md` |
| Kernel | 12,853 | 18,151 | " |
| Core (`source-union`) | 288 | 510 | " |
| Satellites | 12,565 | 17,641 | " |
| Kernel SCCs | 3,841 | 9,139 (8,446 singletons; one giant SCC of 8,138) | `reports/perron-frobenius-oewn.json`, `reports/oewn-paper-wordnet-kernel-summary.json` |
| source SCCs | 286 | 508 | " |
| seed (`exact-small-greedy`) | 2,370 | 5,044 | " |
| seed (`bounded-scc`) | 733 | 3,620 (and `residual_cyclic_scc_count` = 1 → **no layer map**) | `reports/self-loop-fix-impact.md` |
| layered-DAG layers after seed (`exact-small-greedy`, residual 0) | 65 | 65 | `reports/oewn-paper-wordnet-layers.json` |
| giant kernel SCC / its dominant eigenvalue | 8,138 / λ*≈3.744 | 8,138 / λ*≈3.744 | (unchanged — the giant SCC never contained the stripped self-loop nodes) |

**Flag on the brief's premise:** the brief said the committed `reports/oewn-paper-wordnet-kernel-summary.json` "says 2,370, which predates both the self-loop fix and the MinSet-solver refactor." That is no longer true — the committed summary currently reads `kernel_node_count: 18151`, `core_node_count: 510`, `satellite_node_count: 17641`, `seed_node_count: 5044` (`seed_method: exact-small-greedy`), `solver_runtime_seconds ≈ 61.5` — i.e. it has already been regenerated against the fixed kernel and the new solver. So that file did **not** need updating in this pass.

## Report `.md` files edited

- **`reports/swanson-synthesis.md`** — §"The one real result with numbers" baseline line (12,853/288/12,565/2,370 → 18,151/510/17,641/5,044, + provenance note); "Authority PageRank is the wrong object" bullet (`large`/`body` ranks 145,194/134,011 → 145,193/134,010; "Core mean PageRank below uniform" → "≈ 1.17× uniform — still nowhere near the top"); "But the quantitative prediction fails" bullet (ρ 0.316 → 0.371; kernel-out-degree ρ 0.746 → 0.797); "Null-model caveat" bullet (edge-swap-null ρ 0.52 → 0.61; out-degree ρ 0.68 → 0.69); FVS-seed top-set list; "Controllability: a clean divergence" bullets (2,370-seed → 5,044; full-graph drivers∩seed 1,438/Jaccard 0.012 → 2,207/0.018; kernel drivers 2,785/21.7%/255-common/Jaccard 0.052/266-of-288-core → 3,916/21.6%/316-common/0.037/339-of-510); "Recommended next work" item 3 (rewritten from "Resolve `compute_kernel`'s self-loop handling" TODO to "resolved, commit 7d12e64" with the size deltas). The psycholinguistic-regression ΔR²/ΔAUC numbers were **not** touched — they come from `psycholinguistic-regression-output.json`, which the brief did not ask to regenerate, and the ΔR² conclusions are unaffected.
- **`reports/spectral-valuation-oewn.md`** — added a provenance banner under the header; §0 verdict paragraph (ρ 0.316 → 0.371; kernel-out-degree 0.746 → 0.797; added `act`/`part` watch-words at ranks 1/5; `situated` artefact note); §0-§1a graph/combinatorial baseline (Kernel/Core/Satellites/seed/SCC counts, singletons 3,148 → 8,446, nontrivial reverse SCCs 823 → 3,497, + pre-fix line); §1b the four-variants Spearman table (every row updated from the new JSON; reverse-PR-vs-seed-membership +0.106 → −0.183 sign flip; reverse-PR-vs-layer-shallowness +0.258 → ~0; forward-PR-vs-seed-membership +0.276 → +0.489; + a "what moved and why" paragraph); §1c watch-words table (FVS-degree-score-rank column rebased to /18,151, ranks shifted; added `act`/`part` rows; forward-PR `large` 14,442 → 14,433, `water` 36,047 → 36,046); §1d top-15 lists (FVS-degree-score list reordered with higher scores: `act` 305 → 383, etc.; forward-PR sinks now noted as in the enlarged seed; overlap@50 0.25 → 0.20); §1f null models (0.521/0.679/0.518 → 0.613/0.692/0.612; layer-vs-shuffled −0.0005 → −0.002); §1g (823 → 3,497 nontrivial reverse SCCs); §3 Predictions A–D (overlap@500 0.34 → 0.32; Core 288/286-SCCs → 510/508-SCCs; forward-PR-vs-Core −0.23 → −0.14; 823 → 3,497 per-block eigenvectors); §5 paper-implications items 1/3/4 (ρ 0.32 → 0.37; kernel-out-degree 0.75 → 0.80; edge-swap-null 0.52 → 0.61; 823 → 3,497); Appendix "what ran" (re-run note; 408,784 → 561,928 swaps; 18,151-node kernel). §1e (full-graph orientation contrast: 0.995 / −0.047 / 0.511 / 0.396 / −0.027) and §2 (qualitative orientation prose) were checked and need no change.
- **`reports/swanson-perron-frobenius-findings.md`** — §3a graph/combinatorial baseline (added a banner; Kernel 12,853 → 18,151, Kernel SCCs 3,841 → 9,139, source SCCs 286 → 508, Core 288 → 510, Satellites 12,565 → 17,641, seed 2,370 → 5,044, histogram singletons 3,148 → 8,446; + pre-fix line); §3c PageRank-on-full-digraph bullets ("only 2 of top 30 in kernel" → "all 30 in the enlarged kernel"; watch-word ranks refreshed: `large` 145,194 → 145,193, `body` 134,011 → 134,010, etc.; seed-rank percentiles refreshed: median 48,115 → 16,958, "232 of 2,370 in top 2,370" → "1,547 of 5,044 in top 5,044"; mean PageRank by component: Core 4.81e-06-below-uniform → 7.29e-06-≈1.17×-uniform, seed 8.86e-06 → 1.43e-05); §3e layer-vs-PageRank correlations (Pearson −0.13 → +0.10, both near-zero); §4a "the Rest (147,157)" → 141,859, "286 source SCCs" → 508; §4c "3,841 SCCs, 286 sources" → "9,139 SCCs, 508 sources". §0 executive summary, §3b/§3d (the 8,138-node SCC: top words, λ*, recall@k 0.60/0.52/0.505/0.398/0.329, internal-in-degree ρ 0.78 — all unchanged), §3f (psycholinguistic-leg-blocked, separate matter), and the closing appendix were checked and need no change.
- **`reports/swanson-controllability-findings.md`** — §0 TL;DR (2,370-seed/1.5% → 5,044/3.2%; 12,853-kernel → 18,151; 2,785-driver/21.7% → 3,916/21.6%; 255-common/Jaccard-0.052 → 316/0.037; + provenance note); §2.2 "kernel … matching deficiency 21.7% but FVS-seed fraction 18.4%, 255 of ~2.5–2.8k" → "21.6% but 27.8%, 316 of ~3.9k"; §3.2 the verbatim-from-JSON block (full-graph: drivers-in-kernel 9,775/76% → 12,591/69.4%, drivers-in-core 279/288 → 429/510, drivers∩seed 1,438/Jaccard 0.012 → 2,207/0.018; kernel subgraph: matching 10,068 → 14,235, drivers 2,785/21.67% → 3,916/21.57%, drivers-in-core 266/288 → 339/510, drivers-in-satellites 2,519 → 3,577, drivers∩seed 255/Jaccard 0.052 → 316/0.037; + pre-fix parentheticals); §3.3 the "in FVS-seed, not a driver" bullet (now notes the newly-prominent gloss-self-loop words `aah`/`aba`/`abaca`/`abelia` in the seed); §5 the "Self-loops" falsifier bullet (rewritten: the `target != node` filter "was fixed in commit 7d12e64; the §3 numbers were re-run against the fixed kernel"); §6 "Key result" (2,370/1.5% → 5,044/3.2%; 2,785-driver/255-common/0.052 → 3,916/316/0.037); "What I could not verify" item on the self-loop inconsistency (now: "since fixed, commit 7d12e64").

## `sibling-tools-connection.md` — checked, no change needed

`reports/sibling-tools-connection.md` already states the post-fix figures correctly ("the `compute_kernel` self-loop fix (commit 7d12e64) made the lemma-level Kernel *grow* (12,853 → 18,151), pulling in 3,413 gloss self-loops" — §7, and §1g's "a PageRank that turned out to be laundered out-degree" and §6's "reverse-PageRank ≈ out-degree" are conclusions, unchanged). It was already current; nothing was edited there.

## Computations re-run / JSONs regenerated

All three scripts rebuild the graph fresh via `build_paper_wordnet_graph()` and call `analyze_kernel` / `compute_kernel`, so they pick up the post-fix Kernel automatically. Re-run via `uv run python scripts/<script>.py`:

- **`reports/perron-frobenius-oewn.json`** — regenerated (`scripts/perron_frobenius_oewn.py`). PageRank d=0.85 on the 160,010-node digraph + un-damped Perron on the 8,138-node giant kernel SCC + all the Spearman/Pearson comparisons. Console log: `reports/perron-frobenius-run.log`.
- **`reports/spectral-valuation-oewn.json`** + **`reports/spectral-report-run.log`** — regenerated (`scripts/spectral_report.py`). Forward + reverse damped PageRank on the full digraph; un-damped Perron on the 8,138-node SCC, both orientations; 3,497 per-block reverse eigenvectors; degree-preserving edge-swap null on the 18,151-node kernel (561,928 swaps); all comparisons.
- **`reports/maximum-matching-oewn.json`** — regenerated (`scripts/maximum_matching_oewn.py`). Hopcroft–Karp maximum matching on the full digraph and on the kernel subgraph; driver-node sets; overlaps vs the FVS-seed / kernel / core / satellites. Console log: `reports/maximum-matching-run.log`.

(The committed `reports/oewn-paper-wordnet-kernel-summary.json` / `-layers.json` / `-report.md` were already post-fix and were not regenerated. `reports/psycholinguistic-regression-output.json` was not regenerated — it is outside the scope of this pass and its ΔR² conclusions are unaffected by the kernel-size change.)

## Did any *conclusion* (not just a number) change?

**No.** Every load-bearing claim survives:
- *Reverse-PageRank ≈ out-degree, both ≈ degree* — ρ(reverse-PR, out-degree) is still 0.99 (full) / 0.80 (kernel); ρ(reverse-PR, FVS-degree-key) is still ≈ 0.37, still well below the predicted 0.6. Both objects are still "degree spectrally laundered."
- *Authority (forward) PageRank ranks definitional sinks, not foundational vocabulary* — top is still `magnificat`/`palaquium_gutta`/`niobe`/…; the FVS-seed hubs are still in the bottom decile of forward PageRank.
- *FVS-seed ≠ maximum-matching driver nodes* — still divergent by ~2 orders of magnitude on the full graph and ~90 % non-overlap on the kernel; the divergence is, if anything, marginally sharper (kernel Jaccard 0.052 → 0.037).
- *Frobenius normal form's value is structural, not rank-quality* — unchanged; the per-block eigenvectors still reproduce the Core/Satellite split by construction.
- *Codex Predictions A–D* — A confirmed, B confirmed (Core disjoint from the giant SCC), C confirmed (orientations orthogonal, ρ ≈ −0.03), D partly.

Two *quantities* flipped sign but only between near-zero values: ρ(reverse-PageRank, seed-membership) +0.11 → −0.18 and ρ(reverse-PageRank, layer-shallowness) +0.26 → ~0 — both because the enlarged seed/layer-0 now contains ~2,800 low-centrality gloss-self-loop sink-leaves, which reverse-PageRank ranks low. This *adds* a small observation (the self-loop nodes are seed members that reverse-PageRank does not surface) but contradicts nothing.

## Couldn't do / out of scope

- The psycholinguistic-regression numbers in `swanson-synthesis.md` §"Yoneda" and the "Recommended next work" item 2 are from `psycholinguistic-regression-output.json`, not from the three scripts this pass re-ran. The brief did not ask for that regression to be regenerated and its ΔR²/ΔAUC ≤ 0.01 conclusion is robust to the kernel-size change (membership features grew but the block-2-adds-nothing finding is qualitative), so it was left as-is. If a future pass wants exact numbers, re-run `uv run python scripts/psycholinguistic_regression.py`.
- The pre-fix watch-word forward-PageRank ranks in `spectral-valuation-oewn.md` §1c were stated to ~5-significant-figure precision in the old report; the new JSON gives the same values to within rounding (`large` 14,442 → 14,433, `water` 36,047 → 36,046) — kept the new figures.
- Per instruction, nothing was committed; `src/`, `minset.py`, `cli.py`, `pyproject.toml`, `workstreams/` were not touched.

## Verification

`uv run pytest` → all tests pass before and after this pass. (The collected count changed during the session — 24 at the start of the pass, 49 at the end — because the repo picked up commits, including 7d12e64's `tests/test_graph_analysis.py`, in parallel; this pass touched only report `.md` files and regenerated JSON outputs, none of which the test suite covers, so it has no effect on the count either way.)
