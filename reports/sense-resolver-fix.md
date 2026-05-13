# Sense Resolver Fix — the IC-fallback and the edge-budget-controlled comparison

**Date:** 2026-05-13
**Owns:** audit finding #2 (`reports/audit-new-src.md`), synthesis sections 3/7/10 the "the sense-Kernel shrank partly because we dropped the edges that would have made the genus words cyclic" charge, and the IC-projection design decision (synthesis section 8).
**Reproducer:** `scripts/sense_resolver_comparison.py` -> `reports/sense-resolver-comparison.json` + `reports/sense-resolver-comparison-summary.md`.

---

## 1. The resolver change

### What the baseline does

`build_sense_level_paper_wordnet_graph` (audit-baseline behaviour, `polysemy_fallback=False`): for each gloss-token candidate, prefer same-POS senses; if there are multiple same-POS senses, run `choose_best_candidate` (signature overlap with tie-break). The tie-break returns `None` when overlap is zero or tied, and the resolver records `ambiguous_skipped` and emits *no edge*. Audit finding #2 showed this skip set is 54% of all candidate matches (499,860 of 925,283) and is structurally concentrated on the high-polysemy genus vocabulary (`line`, `head`, `break`, `take`, `make`, `set`, `run`, `point`) because the dominant resolution path `resolved_same_pos_unique` cannot fire for any word with >= 2 same-POS senses. Those words' senses therefore receive ~0 incoming gloss edges, have in-degree ~0, lie in no cycle, and are not in the Kernel.

### What the IC-fallback does

`build_sense_level_paper_wordnet_graph(..., polysemy_fallback=True)` (sibling wrapper: `build_sense_level_paper_wordnet_graph_with_ic_fallback`). Same as the baseline on the resolved/unique paths. On a same-POS overlap tie / zero-overlap, instead of recording `ambiguous_skipped`: pick a deterministic representative from the candidate set — the sense with the *lowest sense rank* in the OEWN `word.senses()` enumeration (which corresponds to sense frequency ordering — the most-common reading), tie-broken by sense id. Emit the edge and record it under `resolved_polysemy_fallback_same_pos` (or `..._global` for the global branch). All candidate senses of a single gloss-token resolve to one lemma and therefore to one identity cluster by construction, so the fallback never crosses ICs.

### Why this option

The audit's "Fix" section listed three options:
- (i) strengthen the synthesis hedge only (no code change).
- (ii) edge-budget-controlled comparison (the measurement).
- (iii) less conservative resolver: fall back to most-frequent sense on tie. Citable bias instead of invisible one.

The user's task spec explicitly preferred "the simplest principled option" and listed: edge to the IC if defined and shared, or to a chosen best representative, or distribute weight across candidates. The first two converge on (iii) because every candidate set of one gloss-word lookup is *by construction* a subset of one lemma's senses, hence a subset of one IC. The distribution option (B in my notes) requires changes to downstream FVS code which currently assumes simple set-valued adjacency. The synthetic-IC-node option (C) changes the node surface and would invalidate every downstream invariant the rest of the codebase keeps.

So the cleanest principled choice is (iii) plus the deterministic tie-break (lowest sense rank), with the new edge tagged in resolution stats so the bias is *visible* and the comparison stays measurable.

### Implementation

`src/meanings/wordnet_pipeline.py` (commit `61e4834`):
- Added `polysemy_fallback: bool = False` parameter on `build_sense_level_paper_wordnet_graph`. Default preserved, all 113 tests pass.
- Added `_representative(choices)` helper inside the builder closure.
- Captured `sense_rank_by_node` during the per-sense init loop via `enumerate(word.senses())`.
- Added two new `resolution_stats` keys: `resolved_polysemy_fallback_same_pos`, `resolved_polysemy_fallback_global`.
- Added a sibling wrapper `build_sense_level_paper_wordnet_graph_with_ic_fallback` calling the parameterized form with `polysemy_fallback=True`.

---

## 2. Edge-budget-controlled comparison

*The numbers are produced by `scripts/sense_resolver_comparison.py` -> `reports/sense-resolver-comparison.json`. See `reports/sense-resolver-comparison-summary.md` for the side-by-side table.*

The lemma-level reference is the published exact-small-greedy result: **nodes 160,010 / Kernel 18,151 / seed 5,044 / edges-per-node 4.24 / gloss self-loops 3,413** (`reports/oewn-paper-wordnet-kernel-summary.json`, baked into `scripts/sense_ingestion_rebuild.py` constants).

The baseline reference (audit-baseline resolver, before this fix) is **nodes 212,478 / Kernel 12,142 / seed 1,582 / edges-per-node 1.97 / gloss self-loops 0** (`reports/oewn-sense-ingestion-summary.json`).

See the comparison summary (`reports/sense-resolver-comparison-summary.md`) for:
- side-by-side: baseline vs ic_fallback vs lemma-level (nodes, edges, edges/node, self-loops, Kernel, Core, Satellites, seed, residual cyclic SCCs)
- genus victims: for each of `line / head / break / take / make / set / run / point`, the number of senses in the Kernel + total in-degree under each builder
- verdict (i/ii/iii)

---

## 3. IC-projection decision (synthesis section 8)

Two ways to derive the strict-seed surface from the sense-level graph:

- **P1 — IC-projected graph then FVS.** Collapse each IC to one node; project edges across IC boundaries; drop intra-IC self-loops; run `analyze_kernel` on the IC graph. The strict seed = the IC graph's FVS, lifted back to representative senses at export.
- **P2 — Sense graph FVS then restrict at export.** Run `analyze_kernel` on the sense graph as-is; then, at strict-seed export, pick one representative sense per IC from the seed (one IC = one referential unit, even if the FVS picked multiple of its senses).

The numbers from `scripts/sense_resolver_comparison.py` give P1 vs P2 seed sizes, the symmetric difference (ICs P1 chose that P2 didn't and vice versa), and a recommendation derived from whether either path has residual cyclic SCCs and which produces a tighter seed. See `reports/sense-resolver-comparison-summary.md`.

The chosen path is wired into `scripts/sense_ingestion_rebuild.py` via the `--polysemy-fallback` flag (already added in this round). The IC-projection step itself remains in the comparison script for now; if the recommendation is P1, the rebuild driver gets a sibling flag in a follow-up.

---

## 4. Prediction check: do literal gloss self-loops survive the resolver fix?

Synthesis section 3 prediction: "near-zero on the sense graph" — explicit caveat that the zero count was an adjacency fact under a skip-on-self resolver, not a validated WSD result. The IC-fallback never resolves a candidate to the target node (`same_pos_choices - {target_node}`, `all_choices - {target_node}`), so a same-form self-reference is still excluded from the candidate set before the fallback runs. The self-loop count is therefore expected to remain at 0 under the IC-fallback as well — see the comparison summary for the measurement.

If a self-loop count appears, it would be from intra-IC fallback to a *different* sense of the same form within the head's IC, which is *not* a literal self-loop (it's an edge to a different sense node). The literal-self-loop story holds.

---

## 5. Honest verdict — does the audit's "the Kernel shrank because we dropped edges" charge survive?

See `reports/sense-resolver-comparison-summary.md` for the i/ii/iii verdict statement. The size delta between the IC-fallback sense-Kernel and the lemma-level Kernel is the load-bearing number; the genus victims' Kernel membership table is the diagnostic.

The defensible claims after this round, by verdict:
- **(i) the new sense-Kernel is materially smaller than the lemma-Kernel** -> artifact-dissolution survives the control. Synthesis section 3 caveat can be tightened to "the size comparison is defensible after the edge-budget control."
- **(ii) the new sense-Kernel is about the same size as the lemma-Kernel** -> the audit's charge is correct. The original 12,142 was substantially "we dropped the edges that would have made the genus words cyclic," not artifact dissolution. Synthesis section 3's load-bearing claim narrows to "literal self-loops are eliminable" + "acyclic closure holds at a non-trivial seed"; the Kernel size comparison should not be cited as evidence of artifact dissolution.
- **(iii) the new sense-Kernel is materially larger than the lemma-Kernel** -> the comparison is non-apples-to-apples by construction (sense-level rivalry over the genus words creates more / different cycles than lemma-level collapse). Synthesis section 3 should drop the Kernel-size comparison entirely and rephrase to the qualitative claim (the artifacts are *different*, not larger or smaller).

The verdict is in the JSON output.

---

## 6. Files touched

- `src/meanings/wordnet_pipeline.py` — added `polysemy_fallback` parameter + sibling wrapper.
- `scripts/sense_resolver_comparison.py` — new, the comparison driver.
- `scripts/sense_ingestion_rebuild.py` — exposed the `--polysemy-fallback` flag.
- `reports/sense-resolver-fix.md` — this file.
- `reports/sense-resolver-comparison.json` + `reports/sense-resolver-comparison-summary.md` — produced by the comparison run.
- `reports/oewn-sense-ingestion-summary.json` + `reports/sense-ingestion-rebuild.md` + `data/oewn-sense-strict-seed.json` — re-run downstream of the resolver fix (see commit log).
- `notes/upgoer-identity-clusters.md` — appended a short subsection on the IC-projection decision (does not rewrite the original note).

Not touched: `lexicality.py`, `lexicality_model.py`, `identity_clusters.py` (read-only — the IC lookup is consumed via `identity_cluster_for_form` only), `admission.py`, `minset.py`, `graph_analysis.py`, `cli.py`, `argumentation_*`, `pyproject.toml`, `workstreams/`. Fix wave A is concurrently editing `lexicality.py` + `admission.py`; the work in this report does not overlap.
