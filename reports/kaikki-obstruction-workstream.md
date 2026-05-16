# Kaikki Obstruction To Base English Workstream

Status: executable workstream notes, started 2026-05-15.

## Work Log

- 2026-05-15: Pushed `../argumentation` branch `perf/iccma-python-profile-20260515` and pinned `formal-argumentation` at `8e7247fe8e9c89636b3753a0feac5545f131c853`.
- 2026-05-15: Ran `uv run pytest tests\test_argumentation_bridge.py tests\test_argumentation_dispatch.py`; result was `33 passed`.
- 2026-05-15: Ran `uv run python scripts\kaikki_argumentation_probe.py --mode both` on `data\kaikki-largest-scc.json`.
- 2026-05-15: Verified `reports\kaikki-argumentation-probe.json`: grounded extension size `0` in `1.362s`; stable extension complete in `90.766s`; stable exists `False`; SAT trace has one `unsat` stable check.

## What The Probe Teaches

The Kaikki largest SCC is not simply too large. It is too large for the exact-small-greedy FVS/MinSet path we tried, but it is tractable as a formal argumentation object under the pushed argumentation runtime.

The meaningful result is `stable_exists = False`. Under the attack reading, the whole SCC has no globally coherent stable extension: no accepted set is simultaneously conflict-free and able to attack every outside argument. Grounded semantics is also empty. This makes the SCC a semantic obstruction surface, not just a solver blocker.

The next move is not to claim a final primitive list from the stable-unsat result. The next move is to explain the unsatisfiability and join that explanation to the existing candidate surfaces: P2 OEWN seed, L0 candidates, Kaikki staged seed, clean candidates, admission policy, and unfolding closures.

## Swanson Move

Use formal argumentation to locate where the dictionary graph cannot assemble itself, then use lexical, psycholinguistic, and cross-resource evidence to decide which obstructions are primitive pressure points and which are artifacts.

In operational terms:

- FVS says which nodes can break recursive definition cycles.
- Stable-unsat says the full conflict surface has no coherent all-covering acceptance assignment.
- Obstruction extraction should tell us which clauses, arguments, attacks, or local subgraphs force that failure.
- Kernel pressure ranking should convert those failures into reviewable IC rows.
- Assembler rules should turn the reviewable rows into a testable controlled defining vocabulary.

## Non-Negotiable Boundaries

- Do not call the Kaikki staged seed optimal. It is acyclic and useful, but heuristic.
- Do not call stable-unsat a primitive list. It is an impossibility certificate target.
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

## Phase 1: Add Stable-Unsat Obstruction Extraction

Status: next implementation slice.

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

## Phase 2: Run Kaikki Obstruction Probe

Purpose: apply Phase 1 to `data\kaikki-largest-scc.json`.

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

## Phase 2B: Perturbation Witnesses If Unsat Cores Are Too Coarse

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

## Phase 3: Build Kernel Pressure Table

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

## Phase 4: Define The Assembler Rules

Purpose: turn candidate rows into a testable base-English assembly language.

Artifacts:

- `data/base-assembler-rules.yaml`
- `scripts/validate_assembler_definitions.py`
- `reports/base-assembler-rules.md`

Rule surfaces:

- allowed primitive ICs,
- allowed assembler/helper ICs,
- allowed definition operations,
- forbidden hidden dependencies,
- artifact exclusions,
- closure budget policy,
- exception policy with rationale references.

Validation command:

```powershell
uv run python scripts\validate_assembler_definitions.py `
  --rules data\base-assembler-rules.yaml `
  --unfolding data\sense-unfolding-index.json `
  --pressure-table data\kernel-pressure-table.csv `
  --report reports\base-assembler-rules.md
```

Acceptance gate:

- A definition either closes under the selected base or reports the missing ICs.
- The validator distinguishes primitive failure, assembler-helper failure, artifact failure, and graph-data failure.
- The report includes closure statistics and concrete failed examples.

Falsifier:

- If common target definitions require huge closures or many artifact exceptions, the assembly-language hypothesis is weakened and the report says so.

## Phase 5: External And Multilingual Stress Tests

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

Implement Phase 1 in `../argumentation`: expose a stable-unsat explanation API with tracked stable constraints, tests on small AFs, and a deterministic JSON-serializable result. Push that branch, then update the `formal-argumentation` pin in this repo. Only then implement `scripts/kaikki_obstruction_probe.py`.

This is the principled next slice because the current repo already knows that the Kaikki SCC is stable-unsat, but it does not yet know why.
