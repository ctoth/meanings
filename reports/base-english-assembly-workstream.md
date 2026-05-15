# Base English Assembly Workstream

Status: running notes, started 2026-05-15.

## Literal Target

Build a useful, sense-aware base English: the "assembly language" beneath ordinary definitions. The target is not merely the mathematically smallest feedback vertex set, and not a learner word list by itself. It is a layered, executable bridge from grounded primitives to a controlled defining vocabulary and then outward to dictionary-scale English.

## Initial Grounding Notes

- The existing kernel machinery establishes recursive lexical necessity: feedback vertex sets break definitional cycles, and the residual graph unfolds acyclically.
- The existing reports also show that a raw MinSet is not yet a human base vocabulary. It admits graph artifacts unless filtered through sense, identity-cluster, lexicality, and admission layers.
- The strongest current evidence says the seed budget is structurally stable across dictionaries, while exact membership is resource-specific and polluted by editorial/parsing artifacts.
- Harnad remains the guardrail: recursive definability is not grounding. A base English must mark which primitives are grounded externally and which are introduced as lexical molecules.
- The likely next object is a layered base, with explicit dependency order and admission rationale per sense/identity cluster.

## Open Work Queue

- Read the remaining reports and notes for the live state after round 8. Done for the core synthesis, executable-workstream, graph-object, cross-language, admission, lexicality, sense-resolver, IC, cross-dictionary, kernel export, and current data artifacts.
- Get independent subagent summaries for kernel/philosophy, pipeline/data, and multilingual/resources. Done.
- Ask Claude for an adversarial architectural critique. Done, including adversarial follow-up.
- Synthesize the next direction into an executable workstream with gates, data inputs, scripts, and artifacts.
- Commit this document whenever it is materially updated.

## 2026-05-15 Notes

### What Converged

- The raw graph seed is a pressure surface, not the base language.
- The project's real next question is whether structural necessity can be separated from editorial and psycholinguistic construction.
- Multilingual comparison should constrain interfaces now, but it is not the first empirical gate. A cleaner English cross-resource base comes first.
- The first executable artifact should be an IC-level candidate workbench, not a final word list.

### Current Build Result

Implemented `scripts/base_english_candidates.py`.

Generated:

- `data/base_english_candidates.csv`
- `reports/base-english-candidates.md`

Current workbench summary:

- Candidate admitted IC rows: `58,099`
- Strict lemma-seed supported rows: `2,884`
- Typed sense-seed supported rows: `759`
- Longman-supported rows: `1,832`
- Ogden-supported rows: `741`

The top rows are plausible base candidates (`water`, `coat`, `give`, `bread`, `play`, `yellow`, `ball`, `place`, `school`, `father`) but the report also exposes flags such as `artifact_reading_present`, `numeric_form`, and missing norm coverage. This is the correct shape: a review bench, not an answer.

### Directional Decision

Next architecture should be:

- `Base candidate workbench`: one row per admitted IC with graph, norm, and cross-list evidence.
- `L0 derivation`: a small grounded-primitives candidate set derived by independent evidence channels.
- `Unfolding index`: sense/IC definitions unfolded against the selected base, with closure sizes and failed closures reported.
- `External resource gate`: add a non-OEWN substrate before making stronger claims about English.

### Immediate Risks

- The first candidate score was a heuristic rank, not a statistical model. The script was revised to remove the composite score and use agreement flags plus a clean-candidate filter instead.
- Current typed sense seed data predates the full P2 export recommendation; the workbench records it as current evidence, not final truth.
- Current psycholinguistic norms are lemma-level, so polysemous ICs inherit blunt scores.
- The `artifact_reading_present` flag is intentionally noisy: it marks mixed ICs like `water` and `no`, not necessarily bad candidates.

### Adversarial Follow-Up Result

Claude's follow-up critique identified the main problem in the first generated workbench: the additive score stacked correlated signals and risked presenting a calibrated Base English ranking where we only had an evidence-agreement surface.

Corrections made:

- Removed the composite `score`.
- Added `evidence_count`, `clean_candidate`, `admitted_clean`, and threshold indicators.
- Added a visible `resolver_id` for typed-sense-seed provenance.
- Excluded `numeric_form`, `multiword`, `artifact_reading_present`, and `technical_only` rows from the clean-candidate view instead of down-weighting them.
- Regenerated `data/base_english_candidates.csv` and `reports/base-english-candidates.md`.

Corrected workbench summary:

- Candidate admitted IC rows: `58,099`
- Clean candidate rows: `1,476`
- Strict lemma-seed supported rows: `2,884`
- Typed sense-seed supported rows: `759`
- Longman-supported rows: `1,832`
- Ogden-supported rows: `741`

This is now a defensible first bench: descriptive, filter-based, and explicit about unresolved provenance. It is still not L0.

## Executable Workstream

### Phase 0: Candidate Workbench

Status: done for the first slice.

Purpose: put all existing evidence on one IC-level surface without claiming a final base list.

Artifacts:

- `scripts/base_english_candidates.py`
- `data/base_english_candidates.csv`
- `reports/base-english-candidates.md`

Command:

```powershell
uv run python scripts\base_english_candidates.py
```

Acceptance gate:

- The report avoids a composite score.
- The clean-candidate view excludes numeric, multiword, artifact-mixed, and technical-only rows.
- The report records the typed-sense seed provenance as `legacy_typed_sense_seed_pre_p2`.

### Phase 1: Stabilize The Strict Sense/IC Seed

Status: done for the first slice.

Purpose: replace legacy typed-sense-seed evidence with the round-8 P2 result: sense-graph FVS first, then one representative IC at export.

Tasks:

- Find or add the direct export path for the P2 seed from `scripts/sense_resolver_comparison.py`.
- Emit `data/oewn-sense-p2-ic-seed.json`.
- Record resolver policy, graph node count, edge count, kernel count, seed count, and residual cyclic SCC count.
- Update `scripts/base_english_candidates.py` to read the P2 seed and set `resolver_id` accordingly.

Commands:

```powershell
uv run python scripts\sense_resolver_comparison.py
uv run python scripts\base_english_candidates.py
```

Acceptance gate:

- No row sourced from the sense graph has hidden resolver provenance.
- The candidate report distinguishes old typed seed, P1, and P2 if more than one exists.
- Genus-victim rows (`line`, `head`, `break`, `take`, `make`, `set`, `run`, `point`) are called out if their seed membership changes.

Artifacts:

- `data/oewn-sense-p2-ic-seed.json`
- `reports/sense-resolver-comparison.json`
- `reports/sense-resolver-comparison-summary.md`
- `reports/sense-resolver-comparison.progress.log` (diagnostic, not committed)

Result:

- IC-fallback sense graph: `212,478` nodes, `910,355` edges, `0` self-loops.
- Kernel: `20,744`
- Sense seed: `3,040`
- P2 IC seed: `2,739`
- Candidate workbench now uses resolver id `ic_fallback_polysemy_true__sense_fvs__ic_export_p2`.
- P2-backed typed sense-seed rows in admitted candidates: `1,901`.

Tasks completed:

- Added full P2 export with per-IC representative sense provenance.
- Added timestamped progress logging and a run lock to the resolver comparison runner.
- Regenerated the candidate workbench from the P2 artifact.

### Phase 2: Derive L0 Candidates

Status: done for the first slice.

Purpose: produce the first explicit candidate set for grounded primitives, not by score but by independent evidence channels.

Candidate channels:

- Strict admission: admitted under the current defeasible policy.
- Structural: in P2 sense/IC seed or strict lemma seed.
- Cross-list: in at least two of Longman, Ogden, OEWN seed, GCIDE seed.
- Human-grounding proxy: early AoA, high concreteness, or sensorimotor strength when Lancaster data is added.

Artifacts:

- `scripts/derive_l0.py`
- `data/l0-grounded-primitives.json`
- `reports/l0-derivation.md`

Acceptance gate:

- Report counts each channel separately and at the intersection.
- Report includes near-misses, not only admitted rows.
- Report states whether L0 mostly collapses to Ogden/Longman; if so, the strong emergent-primitives claim fails.
- No single channel is allowed to imply L0 membership by itself.

Result:

- Implemented `scripts/derive_l0.py`.
- Generated `data/l0-grounded-primitives.json` and `reports/l0-derivation.md`.
- Input rows: `58,099`
- L0 candidate rows: `317`
- Near misses: `1,155`
- Channel counts: strict admission `55,344`, structural `3,539`, cross-list `1,020`, grounding proxy `6,973`.
- GCIDE and sensorimotor channels are explicitly unavailable in this slice; they are not silently imputed.

Interpretation:

- This is the first actual L0 candidate surface, not a final primitive set.
- It still leans on Longman/Ogden/OEWN agreement and lemma-level AoA/concreteness, so the lexicographer's confound remains active.
- The next hardening step is either GCIDE membership export or sensorimotor norms before making any strong claim about grounded primitives.

### Phase 3: Build The Unfolding Index

Purpose: test whether admitted/base ICs actually act like an assembly language by measuring definition closures.

Artifacts:

- `scripts/build_unfolding_index.py`
- `data/sense-unfolding-index.json`
- `reports/unfolding-index.md`

Fields:

- `sense_id`
- `ic_id`
- `layer`
- `direct_definiens_ic_ids`
- `transitive_closure_ic_ids`
- `closure_size`
- `seed_ics_in_closure`
- `admission_decision`
- `rationale_ref`

Acceptance gate:

- Median and tail closure sizes are reported.
- Failed or huge closures are not hidden.
- If most closures require thousands of ICs, the assembly-language metaphor is weakened or dead for that graph.

### Phase 4: Add A Stronger External Substrate

Purpose: attack the lexicographer's confound with a third full-definition source, not another prescribed learner list.

Preferred first source:

- Kaikki/Wiktextract English Wiktionary JSONL. Current raw data page: https://kaikki.org/dictionary/rawdata.html

Alternative / later source:

- OpenGloss, if the resource is locally obtainable with license/provenance intact.

Tasks:

- Add a resource adapter that emits `LexicalGraphBuild`.
- Keep resource-specific parsing outside `graph_analysis.py`.
- Produce a cross-resource membership comparison, not only a seed-size comparison.

Acceptance gate:

- Parser provenance and license are documented.
- Edge density and ambiguous-resolution rate are reported.
- Cross-resource agreement is measured against clean candidates and L0, not raw MinSet only.

### Phase 5: Add Better Grounding Evidence

Purpose: add a signal that is less reducible to dictionary editorial practice.

Data:

- Lancaster Sensorimotor Norms, official site: https://www.lancaster.ac.uk/psychology/lsnorms/index.php
- CHILDES/TalkBank for child-directed and acquisition evidence, access/citation rules: https://talkbank.org/childes/access/index.html

Tasks:

- Add `data/psycholinguistic/sensorimotor.csv` with provenance.
- Extend annotations to include sensorimotor max/composite scores.
- Re-run L0 derivation with and without sensorimotor evidence.

Acceptance gate:

- Sensorimotor evidence changes some boundary decisions; if it does not, report that plainly.
- CHILDES-derived frequency is kept separate from adult subtitle/web frequency.

### Phase 6: Multilingual Check

Purpose: test whether the English base is an English artifact or a reusable bridge surface.

Timing: after Phases 1-4. Multilingual is a design constraint now and an empirical test later.

Tasks:

- Add an Open Multilingual WordNet/aligned-wordnet adapter.
- Compare aligned synset/ILI kernel participation across languages.
- Test whether high-agreement English L0 ICs map to stable cross-language anchors.

Acceptance gate:

- Node policy, sense granularity, POS policy, and edge policy are documented per language.
- No cross-language claim is made from resources with incompatible graph construction policies.

## Current Next Commit-Sized Slice

Implement Phase 1: emit the P2 IC seed as a first-class artifact and replace the legacy typed-sense-seed input in `scripts/base_english_candidates.py`.
