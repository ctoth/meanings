# Kaikki Obstruction To Base English Workstream

Status: executable workstream notes, started 2026-05-15.

## Work Log

- 2026-05-15: Pushed `../argumentation` branch `perf/iccma-python-profile-20260515` and pinned `formal-argumentation` at `8e7247fe8e9c89636b3753a0feac5545f131c853`.
- 2026-05-15: Ran `uv run pytest tests\test_argumentation_bridge.py tests\test_argumentation_dispatch.py`; result was `33 passed`.
- 2026-05-15: Ran `uv run python scripts\kaikki_argumentation_probe.py --mode both` on `data\kaikki-largest-scc.json`.
- 2026-05-15: Verified `reports\kaikki-argumentation-probe.json`: grounded extension size `0` in `1.362s`; stable extension complete in `90.766s`; stable exists `False`; SAT trace has one `unsat` stable check.
- 2026-05-15: Claude architectural critique corrected the interpretation: the raw Dung attack reading on a large SCC with self-attacks is a useful tractability/null-baseline result, but it is not yet a rich obstruction explanation.

## What The Probe Teaches

The Kaikki largest SCC is not simply too large. It is too large for the exact-small-greedy FVS/MinSet path we tried, but it is tractable under the pushed argumentation runtime for the raw Dung attack-reading probe.

The result is a baseline negative, not a full explanation. Under the attack reading, every definition edge becomes an attack; in a strongly connected definition mesh with self-attacks, empty grounded semantics and stable-unsat are not surprising. The probe proves the runtime can decide this 93,905-node object quickly, but it does not by itself tell us which English words are primitives.

The next move is therefore not to mine the raw stable-unsat result as if it were a primitive list. The next move is to mine the already-produced disagreement queues into typed buckets, then add a richer obstruction layer that distinguishes support, ambiguity, conflict, and artifact pressure before joining it to P2 OEWN seed, L0 candidates, Kaikki staged seed, clean candidates, admission policy, and unfolding closures.

## Swanson Move

Use graph control and formal argumentation as measuring instruments, not as the base language itself. First classify what the Kaikki staged seed disagrees with. Then locate where the dictionary graph cannot assemble itself without ambiguity or artifact pressure. Finally use lexical, psycholinguistic, and cross-resource evidence to decide which pressure points are primitive candidates and which are resource artifacts.

In operational terms:

- FVS says which nodes can break recursive definition cycles.
- Raw stable-unsat is a null baseline for the all-edges-as-attacks reading.
- Typed disagreement buckets tell us what kind of objects the heuristic Kaikki seed is adding beyond L0/P2.
- Obstruction extraction should then work on a richer support/obstruction surface, not pretend that the raw Dung SCC result already explains meaning.
- Kernel pressure ranking should convert those failures into reviewable IC rows.
- Assembler rules should turn the reviewable rows into a testable controlled defining vocabulary.

## Non-Negotiable Boundaries

- Do not call the Kaikki staged seed optimal. It is acyclic and useful, but heuristic.
- Do not call stable-unsat a primitive list. On the raw SCC it is a tractable null baseline, not a semantic primitive detector.
- Do not collapse graph correctness and human cleaning. A graph seed can be correct and still ugly as English.
- Do not claim sense-level or lemma-level norms are sense-grounded; current norms are blunt alias-level evidence.
- Do not pin `meanings` to a local `../argumentation` checkout. Push argumentation first, then pin a remote SHA.

## Phase 0: Lock The Result

Status: done for the initial probe.

Purpose: make the tractability result durable and repeatable.

Artifacts:

- `scripts/kaikki_argumentation_probe.py`
- `reports/kaikki-argumentation-probe.json`
- `reports/kaikki-argumentation-probe.md`

Command:

```powershell
uv run python scripts\kaikki_argumentation_probe.py --mode both
```

Acceptance gate:

- The runner uses a lock file and timestamped progress log.
- JSON records node count, edge count, argumentation pin, grounded result, stable result, and SAT trace.
- Stable check completes or times out under a stated timeout; no partial success is reported as completion.

## Phase 1: Classify Kaikki Seed Disagreements

Status: done for the first deterministic slice.

Purpose: convert the current disagreement report into typed review queues before adding new semantics.

Inputs:

- `reports/kaikki-seed-disagreement.md`
- `data/kaikki-staged-seed.json`
- `data/l0-grounded-primitives.json`
- `data/oewn-sense-p2-ic-seed.json`
- `data/base_english_candidates.csv`

Artifacts:

- `scripts/classify_seed_disagreement.py`
- `data/kaikki-seed-disagreement-typed.csv`
- `reports/kaikki-seed-disagreement-typed.md`

Buckets:

- `abbreviation_or_code`
- `proper_name`
- `taxon`
- `technical_term`
- `morphology_register_artifact`
- `resource_specific_tail`
- `plausible_missing_primitive`

Command:

```powershell
uv run python scripts\classify_seed_disagreement.py
```

Acceptance gate:

- Every IC in the seed-not-L0 queue is assigned exactly one bucket.
- Bucket counts sum to the seed-not-L0 count from `reports\kaikki-seed-disagreement.md`.
- The report includes examples for each bucket and a focused `plausible_missing_primitive` sample.
- The classifier is deterministic and rule-based; no learned model or hidden scoring is introduced.

Falsifier:

- If `plausible_missing_primitive` is empty, the classifier is probably too aggressive.
- If `plausible_missing_primitive` is more than half of seed-not-L0, the classifier is probably too weak.
- Kaikki-only rows with no current OEWN candidate or P2 support should go to `resource_specific_tail`, not `plausible_missing_primitive`.

Result:

- Implemented `scripts/classify_seed_disagreement.py`.
- Generated `data/kaikki-seed-disagreement-typed.csv`.
- Generated `reports/kaikki-seed-disagreement-typed.md`.
- Classified seed-not-L0 rows: `39,767`.
- Bucket counts:
  - `resource_specific_tail`: `31,212`
  - `plausible_missing_primitive`: `4,258`
  - `technical_term`: `2,119`
  - `abbreviation_or_code`: `1,114`
  - `proper_name`: `791`
  - `morphology_register_artifact`: `237`
  - `taxon`: `36`
- Falsifier check: `pass`.

Interpretation:

The main Kaikki disagreement is not a hidden primitive bonanza. Most of the seed-not-L0 queue is Kaikki-only/resource-specific tail under current OEWN/P2/candidate evidence. The plausible residue is still large enough to be scientifically useful, but small enough to review and cross-check.

## Phase 2: Add Stable-Unsat Obstruction Extraction

Status: done for the first tracked-clause API slice.

Purpose: turn `stable_exists = False` into an explanatory object.

Primary implementation target is `../argumentation`, then push and repin here. The existing `argumentation.af_sat.find_stable_extension` returns `None` plus telemetry, but it does not expose an unsat core or minimal obstruction certificate.

Tasks:

- Add a stable-unsat explanation API in `../argumentation`, for example `explain_stable_unsat(framework, granularity=...)`.
- Encode stable constraints with tracked groups:
  - conflict-free clauses from attacks,
  - coverage clauses per argument,
  - optional requirement clauses from `require_in` / `require_out`.
- Return a deterministic certificate with:
  - `status`,
  - `argument_count`,
  - `attack_count`,
  - `core_argument_ids`,
  - `core_attack_ids`,
  - `coverage_argument_ids`,
  - `clause_group_count`,
  - `runtime_seconds`,
  - `solver_metadata`.
- Add tests in `../argumentation` for an odd cycle, a self-loop, a satisfiable even cycle, and a context-dependent example where a local odd cycle can be unblocked by upstream forcing.
- Push the argumentation branch before updating `pyproject.toml` and `uv.lock` in this repo.

Candidate command sequence:

```powershell
Set-Location ..\argumentation
uv run pytest tests\test_solver_encoding.py
git push

Set-Location ..\meanings
uv lock --upgrade-package formal-argumentation
uv run pytest tests\test_argumentation_bridge.py tests\test_argumentation_dispatch.py
```

Acceptance gate:

- Unsat explanation is not just `stable_exists = False`; it names at least the tracked clause groups responsible for the unsat result.
- The API returns `None` or a clear `not_supported` status on solvers/configurations that cannot produce cores.
- Tests prove satisfiable cases do not produce fake obstruction cores.
- The dependency pin in this repo resolves from the pushed remote SHA.

Falsifier:

- If tracked cores on the Kaikki SCC are too large to interpret, the phase still succeeds only if it reports that fact and provides a coarser aggregation that is deterministic and reviewable.

Result:

- Implemented `argumentation.af_sat.StableUnsatExplanation`.
- Implemented `argumentation.af_sat.explain_stable_unsat`.
- Added focused argumentation tests for:
  - odd-cycle UNSAT,
  - self-loop UNSAT,
  - even-cycle SAT,
  - context-dependent odd-cycle unblocking.
- Verification in `../argumentation`:
  - `uv run pytest tests\test_solver_encoding.py -q`: `61 passed`.
  - `uv run pyright src\argumentation\af_sat.py`: `0 errors`.
- Pushed `../argumentation` commit `9a9f4c553c7fde3ff30ef15e062c6d4ef8e672ac`.
- Updated `meanings` dependency pin and `uv.lock`.
- Verification in this repo:
  - `uv run pytest tests\test_argumentation_bridge.py tests\test_argumentation_dispatch.py`: `33 passed`.

## Phase 3: Run Kaikki Obstruction Probe

Status: done for the raw SCC tracked-core slice.

Purpose: apply Phase 2 to `data\kaikki-largest-scc.json`.

Artifacts:

- `scripts/kaikki_obstruction_probe.py`
- `reports/kaikki-obstruction-probe.json`
- `reports/kaikki-obstruction-probe.md`
- `reports/kaikki-obstruction-probe.progress.log` as diagnostic output
- `reports/kaikki-obstruction-probe.lock`

Command:

```powershell
uv run python scripts\kaikki_obstruction_probe.py `
  --input data\kaikki-largest-scc.json `
  --json reports\kaikki-obstruction-probe.json `
  --report reports\kaikki-obstruction-probe.md
```

Report sections:

- SCC facts: node count, edge count, degree quantiles.
- Stable-unsat certificate summary.
- Top coverage obligations in the unsat core.
- Top attack/conflict groups in the unsat core.
- Overlap with L0, clean candidates, P2 seed, and Kaikki staged seed.
- Examples by bucket: likely primitive, assembler/helper, circular dependency, technical/taxon/proper-name, morphology/register artifact.

Acceptance gate:

- The runner has a lock, progress log, JSON output, Markdown output, and explicit timeout discipline.
- It records the exact argumentation pin used.
- It never emits a full 90k-node core dump into Markdown; full details go to JSON only if bounded.
- It says plainly whether the result is an exact unsat core, a non-minimal solver core, or a deterministic aggregation.

Falsifier:

- If the solver returns no useful core, the report must say `no useful core extracted` and fall back to deterministic perturbation/aggregation as a separate Phase 2B, not as a fake core.

Result:

- Implemented `scripts/kaikki_obstruction_probe.py`.
- Generated `reports/kaikki-obstruction-probe.json`.
- Generated `reports/kaikki-obstruction-probe.md`.
- Full SCC run:
  - Nodes: `93,905`
  - Edges: `956,937`
  - Tracked clause groups: `1,050,842`
  - Runtime seconds: `131.163`
  - Status: `unsat`
  - Stable exists: `False`
  - Core arguments: `3`
  - Core attacks: `3`
  - Coverage arguments: `1`
  - Core ICs: `ic:ablative`, `ic:ablative_case`, `ic:material`

Interpretation:

The raw stable-unsat result is even more clearly a null baseline than a semantic obstruction theory. A three-argument self-loop core can certify UNSAT for the entire raw Dung SCC. This is useful because it tells us the next scientific move is self-loop/artifact decomposition and richer support/obstruction modeling, not treating the raw SCC core as a primitive-pressure map.

## Phase 3B: Perturbation Witnesses If Unsat Cores Are Too Coarse

Status: done for the first self-loop-stripped slice.

Purpose: get explanatory pressure when SAT cores are too broad.

Tasks:

- Sample candidate removals or forced decisions over high-interest IC groups.
- Check whether stable existence changes under bounded perturbations:
  - remove one candidate group,
  - require one candidate in,
  - require one candidate out,
  - remove a small attack neighborhood.
- Prioritize groups from L0, clean candidates, P2, Kaikki staged seed, and high-degree obstruction-core nodes.

Artifact:

- `reports/kaikki-obstruction-perturbations.json`
- `reports/kaikki-obstruction-perturbations.md`

Acceptance gate:

- Every perturbation records what changed, why it was selected, runtime, and result.
- Perturbation results are labeled as causal probes, not proofs of minimality.

Self-loop-stripped result:

- Added `--drop-self-loops` to `scripts/kaikki_obstruction_probe.py`.
- Generated `reports/kaikki-obstruction-probe-no-self-loops.json`.
- Generated `reports/kaikki-obstruction-probe-no-self-loops.md`.
- Dropped self-loops: `10,413`.
- Residual edges: `946,524`.
- Tracked clause groups: `1,040,429`.
- Runtime seconds: `131.423`.
- Status: `unsat`.
- Stable exists: `False`.
- Core arguments: `86`.
- Core attacks: `53`.
- Coverage arguments: `40`.
- Core bucket counts:
  - `not_in_seed_not_l0`: `29`
  - `resource_specific_tail`: `23`
  - `plausible_missing_primitive`: `16`
  - `technical_term`: `8`
  - `abbreviation_or_code`: `6`
  - `proper_name`: `4`

Interpretation:

The self-loop artifacts were not the whole story. After removing `10,413` self-loops, stable-unsat persists and the core grows into an interpretable 86-IC obstruction surface. This surface is mixed: it contains real base-like terms (`animal`, `ask`, `good`, `helpful`, `place`, `put`, `useful`) but also grammar/parser and resource artifacts (`plural`, `past_participle`, `simple_past`, `see_also`, `than`, `hundred_thousand`). This is exactly the kind of queue the kernel pressure table should consume.

## Phase 4: Build Kernel Pressure Table

Status: done for the first obstruction-backed slice.

Purpose: convert graph/argumentation results into a reviewable IC-level workbench.

Artifacts:

- `scripts/kernel_pressure_table.py`
- `data/kernel-pressure-table.csv`
- `data/kernel-pressure-table.json`
- `reports/kernel-pressure-table.md`

Inputs:

- `data/base_english_candidates.csv`
- `data/l0-grounded-primitives.json`
- `data/oewn-sense-p2-ic-seed.json`
- `data/kaikki-staged-seed.json`
- `data/kaikki-seed-disagreement-typed.csv`
- `reports/kaikki-obstruction-probe.json`
- `data/oewn-upgoer-admitted.json`
- optional psycholinguistic norm columns already joined into the candidate workbench

Rows:

- one row per IC seen in any candidate, seed, obstruction, or clean-candidate surface.

Columns:

- `ic_id`
- `primary_alias`
- `l0_candidate`
- `clean_candidate`
- `p2_seed`
- `kaikki_staged_seed`
- `obstruction_core`
- `obstruction_coverage`
- `obstruction_conflict`
- `strict_admission`
- `evidence_count`
- `frequency`
- `age_of_acquisition`
- `concreteness`
- `flags`
- `pressure_bucket`
- `review_reason`

Bucket policy:

- `primitive_candidate`: L0 or clean candidate with obstruction pressure and no artifact flag.
- `assembler_helper`: high-frequency abstract/helper term with structural pressure.
- `circular_dependency`: strong obstruction pressure but weak human-grounding evidence.
- `resource_artifact`: abbreviation, code, proper name, taxon, numeric, morphology/register artifact, or technical-only row.
- `external_substrate`: strong Kaikki-only signal not supported by OEWN/L0 yet.

Command:

```powershell
uv run python scripts\kernel_pressure_table.py
```

Acceptance gate:

- No composite score is presented as calibrated truth.
- Buckets are rule-derived and reviewable.
- The report includes top rows and disagreement queues, not only pretty candidates.
- Counts reconcile against every input artifact.

Result:

- Implemented `scripts/kernel_pressure_table.py`.
- Generated `data/kernel-pressure-table.csv`.
- Generated `data/kernel-pressure-table.json`.
- Generated `reports/kernel-pressure-table.md`.
- Rows: `85,137`.
- Obstruction-core rows: `86`.
- L0 rows: `317`.
- Clean candidate rows: `1,476`.
- Pressure bucket counts:
  - `candidate_background`: `46,152`
  - `external_substrate`: `34,541`
  - `resource_artifact`: `4,376`
  - `circular_dependency`: `55`
  - `primitive_candidate`: `11`
  - `assembler_helper`: `2`
- Obstruction-core bucket counts:
  - `circular_dependency`: `55`
  - `resource_artifact`: `18`
  - `primitive_candidate`: `11`
  - `assembler_helper`: `2`

Interpretation:

The first pressure table gives us a real review bench. The obstruction core is not purely artifact and not purely primitive: it contains a small primitive-candidate slice (`animal`, `answer`, `certain`, `desire`, `express`, `helpful`, `name`, `place`, `plural`, `request`, `useful`), two assembler-helper candidates (`giving`, `office`), and a larger circular/resource queue. The next work should validate whether the primitive/helper rows actually reduce closure failures rather than just looking plausible.

## Phase 5: Define The Assembler Rules

Status: done for the first closure-coverage scan; no YAML committed yet by design.

Purpose: turn candidate rows into a testable base-English assembly language. The
first commit is a measurement instrument: the implicit base is derived from
existing pressure-table CSV columns (L0 ∪ `primitive_candidate` ∪
`assembler_helper`), not from a hand-authored YAML. A YAML can be drafted later
from the failure histogram, when there is evidence that this base is worth
freezing.

Phase 5A: implicit-base validator (done 2026-05-16).

Artifacts:

- `scripts/validate_assembler_definitions.py`
- `reports/base-assembler-validation.md`
- `reports/base-assembler-validation.json`
- `reports/base-assembler-validation.progress.log`
- `reports/base-assembler-validation.lock`

External-agent review of the slice before implementation:

- `prompts/next-assembler-step.md`
- `reports/codex-next-assembler-step-report.md`
- `reports/gemini-next-assembler-step-report.md`

Validation command:

```powershell
uv run python scripts\validate_assembler_definitions.py `
  --unfolding data\sense-unfolding-index.json `
  --pressure-table data\kernel-pressure-table.csv `
  --report reports\base-assembler-validation.md `
  --json reports\base-assembler-validation.json `
  --target admitted `
  --max-closure-size 200
```

Acceptance gate:

- Every non-truncated admitted target row is classified as
  `closed / artifact / circular / external / background`. Truncated-closure
  rows are reported as `graph_data` and excluded from the closure-rate
  denominator.
- Per-base-IC marginal usage and per-blocking-IC blocked-target counts are
  emitted so the failure histogram drives any later rules YAML.
- The report respects the polysemy OR-junction: an IC is groundable if any of
  its kernel senses has every direct definiens already groundable; a fixpoint
  iteration over the unfolding-index rows computes the closure.

Three-pronged falsifier:

- Closure rate under L0 + augmented layer at `closure_size <= 200` below 0.60.
- Artifact-blocked share at `closure_size <= 200` above 0.10.
- Marginal Grounding Yield of the augmented layer below 1.0 closure per added
  base IC.

If any threshold trips, the assembly-language-under-this-base hypothesis is
weakened and the report says so.

Result:

- Implemented `scripts/validate_assembler_definitions.py`.
- Generated `reports/base-assembler-validation.json`.
- Generated `reports/base-assembler-validation.md`.
- L0 base size: `317`.
- Augmented base size: `326`.
- Augmented layer size: `9` (`certain, desire, express, giving, helpful,
  office, plural, request, useful`; the other four candidates - `animal,
  answer, name, place` - were already in L0).
- Selected admitted target rows: `15,872`.
- Closure rate at `closure_size <= 200`: L0 `0.1366`, augmented `0.1418`.
- Status histogram at `closure_size <= 200` (augmented): artifact `9,445`,
  background `3,048`, closed `2,110`, external `205`, circular `77`.
- Marginal Grounding Yield: `8.56` new closures per added base IC.
- Falsifier verdict: `weakened` - closure rate `0.142` < `0.60` and artifact
  share `0.635` > `0.10` both tripped; MGY passes.

Interpretation:

The augmented layer is not deadweight: 9 added ICs produce 77 new closures
(MGY 8.56). But three of the nine (`express, helpful, request`) contribute
zero closed targets, so the load-bearing additions are `certain (13), desire
(8), office (5), giving (4), plural (3), useful (1)`.

The 60% closure-rate gate was never reachable: the unfolding index terminates
at the 2,739-IC P2 seed, while our base is 326 ICs, so most admitted senses
fail with `closure_size = 1` because the target IC is itself a P2 terminal
that we chose not to promote into the base.

The decisive finding is the artifact share. `0.635` of `closure_size <= 200`
failures hit ICs labelled `resource_artifact`, and the top blockers - `act,
quality, part, event, time, energy, complete, force, power, life` - are
clearly common English, not technical_term artifacts. The
`scripts/classify_seed_disagreement.py` classifier appears to be too
aggressive in marking abstract-noun common-English as `technical_term`. The
next workstream gate is not "add more primitives" - it is
**artifact-bucket re-audit** of the pressure table.

## Phase 5B: Re-audit `resource_artifact` Classifications

Status: done 2026-05-16. Spun out to
`reports/artifact-bucket-reaudit-workstream.md`. Falsifier closed:
artifact share at `closure_size <= 200` dropped `-6.01 pp`,
`regressed_count = 0`. Three data-driven rules shipped: direct norms
join in the pressure table, `common_vocabulary` high-frequency
override (excluding taxon), tightened short-form abbreviation
detection.

## Phase 5D: Re-audit `candidate_background` and `external_substrate`

Status: queued at `reports/background-bucket-reaudit-workstream.md`,
drafted 2026-05-16. The next-largest blocker bucket after Phase 5B
closed.

Purpose: of the 3,664 `candidate_background` blockers and 450
`external_substrate` blockers at `closure_size <= 200`, identify
which are admitted high-quality terminal ICs that should be promoted
into the base via a data-driven rule rather than hand-authored YAML.

The child workstream follows the same five-phase shape as Phase 5B
(inventory, Codex-reviewed rules, rebuild, validator diff with hard
regression gate, decide).

## Phase 6: External And Multilingual Stress Tests

Purpose: test whether the base is English/OEWN-specific or resource-stable.

Order:

1. Strengthen the English external substrate first.
2. Add OpenGloss or another full-definition English source if provenance and license are clean.
3. Then add aligned multilingual WordNet/ILI comparison.

Artifacts:

- resource adapter emitting `LexicalGraphBuild`,
- resource provenance README,
- per-resource kernel/obstruction reports,
- cross-resource pressure comparison report.

Acceptance gate:

- Node policy, sense granularity, POS policy, and edge policy are documented per resource.
- No cross-language claim is made from incompatible graph policies.

## Immediate Commit-Sized Slice

Execute Phase 1 of `reports/background-bucket-reaudit-workstream.md`:
write `scripts/audit_background_bucket.py`, generate
`reports/background-bucket-audit.{md,json}`. Read-only inventory over the
current post-rebuild pressure table.
