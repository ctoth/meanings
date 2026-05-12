
## 2026-05-12 — agent run (self-loop fix #7d12e64 number refresh)

State: pytest baseline 24 passed. Scoped report files:
- swanson-synthesis.md: lines 19, 33, 34 quote 12,853 / 288 / 12,565 / 2,370 / 8,138 — need update.
- spectral-valuation-oewn.md: heavy — every kernel-derived figure (12,853, 3,841 SCCs, 8,138 giant, 288/12,565, 2,370 seed, 286 source SCCs, 823 nontrivial reverse SCCs, all Spearman ρ, watch-word ranks, overlap@k, null ρ). Must regen reports/spectral-valuation-oewn.json + reports/spectral-report-run.log first.
- swanson-perron-frobenius-findings.md: heavy — §3 describes a run with kernel-derived numbers, top-30 lists, ranks, ρ. Must regen reports/perron-frobenius-oewn.json first.
- sibling-tools-connection.md: ALREADY uses post-fix figures (12,853→18,151, 3,413 self-loops). NO CHANGE NEEDED.
- swanson-controllability-findings.md (task 3): kernel-subgraph matching numbers + §5 line 110 obsolete self-loop-filter note. Regen reports/maximum-matching-oewn.json first.

Note: committed reports/oewn-paper-wordnet-kernel-summary.json ALREADY shows post-fix (18,151/510/17,641, seed 5,044 exact-small-greedy) — brief's claim it "says 2,370" is itself stale. Flag in audit.

Blocker: 3 bg scripts (perron_frobenius_oewn.py, spectral_report.py, maximum_matching_oewn.py) running, regenerating JSONs; not done yet (~5min in). All rebuild graph fresh so will pick up post-fix kernel. Monitor task bj1nszbny waits for all 3 JSON mtimes to change.
- 15:13 still waiting; 3 bg python scripts running ~10min, JSONs not yet rewritten. No new findings.
- 15:14 STILL waiting on 3 bg JSON regens (perron/spectral/matching), ~11min elapsed. Monitor bj1nszbny armed. Stop polling; act on monitor event.
- 15:15 STILL blocked on 3 bg regens. No changes. Will act ONLY on monitor bj1nszbny event. Stop polling.

## 15:17 — perron JSON regenerated, key new figures
- Kernel 18,151 (11.34%); Core 510; Satellites 17,641; seed 5,044 (3.15%/27.8% of kernel); largest kernel SCC 8,138 (UNCHANGED); λ*≈3.744 (UNCHANGED)
- Kernel SCCs 9,139 (was 3,841); source SCCs 508 (was 286); hist: 8138×1,11×1,10×1,6×3,5×7,4×23,3×87,2×570,1×8446 singletons
- layers JSON: still 65 layers (0-64), layer0=seed=5044, residual_cyclic_scc_count=0
- top30 global PageRank: ALL 30 now in_kernel (was "only 2 of 30"); 0 in Core; 28 in seed. Watch ranks ~unchanged (full-graph PR): small 152871, large 145193, part 145244, body 134010, white 63179, plant 142195, act 77118
- mean PR by component: seed 1.43e-5 (~2.3x uniform), kernel 8.25e-6, Core 7.29e-6 (~1.17x uniform — was BELOW uniform pre-fix, now slightly above; conclusion unchanged), satellites 8.28e-6
- seed PR rank pctiles: median 16958, p25 2401, p75 60143; 1547 of 5044 in top-5000 (30.9%)
- perron_topK_in_seed (giant SCC): 50→0.60,100→0.52,200→0.505,500→0.398,1000→0.329 (UNCHANGED — SCC unchanged)
- perron_scc vs indeg_scc 0.78, vs pagerank_scc 0.56, vs pagerank_full 0.30; pagerank vs indeg full 0.40, vs outdeg 0.18 (~unchanged)
- layer_vs_neglog_pagerank_pearson_kernel 0.104; layer_vs_pagerank_spearman_kernel 0.151 (was ~-0.13/~-0.15, sign noise, "uncorrelated" unchanged)
- committed oewn-paper-wordnet-kernel-summary.json already post-fix (18151/510/17641, seed 5044). Brief's "2,370" claim is stale; flag in audit.

DONE: swanson-synthesis.md line 19 updated.
TODO: spectral-valuation-oewn.md (waiting on spectral JSON), swanson-perron-frobenius-findings.md §3 (have data, partially), swanson-controllability-findings.md (waiting matching JSON), swanson-synthesis.md lines 33-34 (waiting matching JSON), stale-numbers-audit.md report.
Blocker: spectral_report.py + maximum_matching_oewn.py still running (~16min). Monitor bj1nszbny armed.

## 15:19 — swanson-perron-frobenius-findings.md updated
- §3a baseline numbers, §3c PageRank/seed/mean-PR, §3e layer corr, §4a Rest size + source SCCs, §4c SCC counts — all updated with post-fix figures + provenance notes. §3b/§3d (giant SCC) unchanged. Conclusions unchanged (Core not what PageRank ranks; reverse-PageRank prediction; FVS≠driver).
DONE: swanson-synthesis.md L19, swanson-perron-frobenius-findings.md.
TODO: swanson-synthesis.md L24-25,L33-34 (need spectral+matching JSON), spectral-valuation-oewn.md (need spectral JSON), swanson-controllability-findings.md (need matching JSON), stale-numbers-audit.md report.
Blocker: spectral_report.py + maximum_matching_oewn.py still running, JSONs not regenerated. Monitor bj1nszbny armed.

## 15:22 — ALL THREE JSONs regenerated. matching figures:
- full graph: matching 41266 (UNCHANGED), drivers 118744 (74.21% UNCHANGED), drivers_in_kernel 12591 (69.4%; was 9775/76%), drivers_in_core 429/510 (was 279/288), ∩seed 2207 (was 1438), Jaccard 0.018 (was 0.012), pure sources 3329 (UNCHANGED)
- kernel subgraph (18151): matching 14235, drivers 3916 (21.57%; was 2785/21.7%), drivers_in_core 339/510 (was 266/288), ∩seed 316 (was 255), Jaccard 0.037 (was 0.052), drivers\seed 3600, seed\drivers 4728
- new sample_seed_not_driver leads with self-loop words (aah/aba/abaca/abelard/abelia)
DONE: swanson-synthesis.md L19; swanson-perron-frobenius-findings.md §3a/§3c/§3e/§4a/§4c; swanson-controllability-findings.md §0/§2.2/§3.2/§3.3.
TODO: swanson-controllability-findings.md §5 (line ~110 self-loop-filter note now obsolete) + §6 key-result line; swanson-synthesis.md L24-25 (spectral ρ over kernel) + L33-34 (matching); spectral-valuation-oewn.md (full rewrite of numbers from new spectral JSON); stale-numbers-audit.md report; pytest after.
Spectral JSON now available — read it next.

## 15:25 — spectral JSON read; new key figures
- kernel 18151/core510/sat17641/seed5044, SCCs 9139, source508, giant 8138, λ 3.744, nontrivial_kernel_sccs_reverse 3497 (was 823); n_layers 65
- comparisons_on_kernel:
  - reverse_pagerank_full: vs_fvs_deg 0.371(was0.316), vs_seed_mem -0.183(was+0.106 SIGN FLIP), vs_core 0.073, vs_indeg -0.209, vs_outdeg 0.797(was0.746), vs_layer_shallow 0.004(was0.258 COLLAPSE), overlap@500 0.319(was0.34), seed_recall@2370 0.173(was0.368)
  - forward_pagerank_full: vs_fvs 0.004(was0.249), vs_seed 0.489(was0.276), vs_core -0.144, vs_indeg 0.430, vs_outdeg -0.441, vs_layer 0.141, overlap@500 0.0, seed_recall@2370 0.359
  - perron_largest_scc_reverse: vs_fvs 0.397(was0.404), vs_seed 0.274, vs_indeg -0.031, vs_outdeg 0.405, vs_layer 0.284, overlap@500 0.292, seed_recall@2370 0.160(was0.341)
  - perron_largest_scc_forward: vs_fvs 0.395(was0.445), vs_seed 0.119, vs_indeg 0.761, vs_outdeg 0.055, vs_layer -0.168, overlap@500 0.058, seed_recall@2370 0.116
- full_graph: rev vs outdeg 0.995, rev vs indeg -0.047, rev vs total 0.511, fwd vs indeg 0.396, rev vs fwd -0.027 (~unchanged)
- null_models: rev real vs randomized_edge 0.613(was0.521), real vs total_deg 0.692(was0.679), randomized vs total 0.612(was0.518), layer real vs shuffled -0.0024
- watch reverse PR full ranks: act1 part5 large27 body29 small66 water132 form136 plant151 white472 born125 various261 english342 (full-graph; ~unchanged from old)
- watch perron reverse SCC: small345/8138 large29 white2309 plant259 body21 water232 part6 form16 act1 (UNCHANGED-SCC unchanged)
- fvs_degree_score_kernel ranks (/18151): act0 small2 various3 part4 large5 body6 plant8 form10 water11 white15 born93 english230 (was small4 large7 white27 plant14 body2 water6 — slight reorder, still all top)
- top30 reverse PR full: situated::a(outdeg124), act, degree, time, ... (unchanged); small_scc_examples: eighth/ninth, basidiomycota, cucurbitaceae, niobite/tantalum, zinc_sulfide (unchanged)
DONE: swanson-synthesis L19; swanson-perron-frobenius-findings §3a/3c/3e/4a/4c; swanson-controllability §0/2.2/3.2/3.3; spectral-valuation-oewn intro+§0verdict+§0para1.
TODO: spectral §1a/1b/1c/1d/1e/1f/1g, §2/§3 prediction outcomes; swanson-controllability §5(self-loop note)+§6; swanson-synthesis L24-25,L33-34; stale-numbers-audit.md report; pytest.
- 15:28 spectral-valuation-oewn.md: intro+§0verdict+§0para1+§1a+§1b+§1c+§1d+§1f+§1g done. §1e unchanged. TODO: §2 (no kernel nums?), §3 prediction outcomes A-D (overlap@500, seed recall, ρ values quoted), §5 (kernel nums), then swanson-controllability §5/§6, swanson-synthesis L24-25/L33-34, audit report, pytest.
- 15:31 edge-swap count new: 561928 (was 408784). spectral-valuation-oewn.md §0/§1a-d/§1f/§1g/§3A-D/§5 done. TODO: spectral §2 (check kernel nums - has 'magnificat/niobe/laocoon' only, ok), appendix swap count. Then swanson-controllability §5/§6, swanson-synthesis L24-25/L33-34, audit report, pytest.
- 15:35 COMPLETE. All 4 task-1 reports + controllability updated; 3 JSONs + 3 run logs regenerated; reports/stale-numbers-audit.md written. pytest 49 passed. No conclusions changed. Nothing committed.
