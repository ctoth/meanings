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
- Ask Claude for an adversarial architectural critique. First pass done; adversarial follow-up running.
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

- The candidate score is a heuristic rank, not a statistical model.
- Current typed sense seed data predates the full P2 export recommendation; the workbench records it as current evidence, not final truth.
- Current psycholinguistic norms are lemma-level, so polysemous ICs inherit blunt scores.
- The `artifact_reading_present` flag is intentionally noisy: it marks mixed ICs like `water` and `no`, not necessarily bad candidates.
