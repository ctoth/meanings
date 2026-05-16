# Background Bucket Re-audit Workstream

Status: queued, drafted 2026-05-16.

Parent: `reports/kaikki-obstruction-workstream.md` (Phase 5D).
Predecessor: `reports/artifact-bucket-reaudit-workstream.md` closed by
Phase 4 falsifier passing.

Predecessor evidence: `reports/artifact-bucket-reaudit-impact.md` shows
that after the artifact-bucket rebuild, `closure_size <= 200` failures
break down as:

- `artifact` 8,551
- `background` 3,664
- `external` 450
- `circular` 101

Artifact pressure is still the largest bucket, but the artifact
classifier change has hit its diminishing return on the current ruleset.
The next largest bottleneck under the validator's status-precedence
metric is `background` - admitted target rows whose missing ICs sit in
`pressure_bucket = candidate_background`, i.e. ICs that are not L0, not
primitive_candidate, not assembler_helper, and not flagged as artifact.

## Why this workstream exists

The validator marks a sense `background` when its blockers are all
`candidate_background` ICs. These are admitted ICs we are not currently
promoting into the base. The question this workstream asks: of the
~3,664 background-blocked failures at `closure_size <= 200`, how many
are blocked by ICs that should plausibly be base (more L0-style
primitives, more assembler helpers, more `common_vocabulary` after
R2-style rules), and how many are blocked by ICs that are correctly
non-base but require their own definition to assemble?

The mirrored hypothesis: most background blockers are admitted P2 ICs
that are themselves never expanded under the unfolding index because the
index terminates at P2 terminals. They look like blockers only because
our base is smaller than P2. A rule that promotes P2 terminals with high
frequency / early AOA / high concreteness into the base could close
many of these failures without hand-authoring a YAML.

## What this workstream does NOT do

- Does not author `data/base-assembler-rules.yaml`. The validator still
  runs on implicit defaults.
- Does not change the unfolding-index builder.
- Does not re-run the Kaikki staged seed.
- Does not redefine L0 or P2.
- Does not re-litigate the artifact-bucket rebuild from
  `reports/artifact-bucket-reaudit-workstream.md`. That work is closed.

## Non-negotiable boundaries

- Do not promote any IC into the base by hand. Promotion must come from
  a written rule applied in `scripts/kernel_pressure_table.py` or the
  validator.
- Do not regress: any sense classified `closed` under the current
  post-Phase-4 validator must remain `closed`. Enforced as a hard gate.
- Do not collapse `candidate_background` and `external_substrate` into
  a single bucket. Their semantics remain distinct.
- Do not delete existing pressure-table or validator artifacts before
  the rebuild succeeds and passes the regression gate.

## Phase 0: Baseline lock

Status: done at `af4ecc0`.

Inputs frozen for comparison:

- `data/kernel-pressure-table.csv` (post-artifact-rebuild).
- `reports/base-assembler-validation.{md,json}` (post-artifact-rebuild).
- `reports/artifact-bucket-reaudit-impact.{md,json,-per-sense.csv}`.

## Phase 1: Inventory background blockers

Status: queued. Read-only.

Purpose: produce a deterministic list of `candidate_background` ICs that
block at least one admitted target, with frequency / AOA / concreteness
profile and a separate count for `external_substrate`. Read-only.

Tasks:

- Read `data/kernel-pressure-table.csv`.
- Select rows with `pressure_bucket in {"candidate_background",
  "external_substrate"}`.
- Compute containment counts over admitted, non-truncated unfolding
  rows (same metric as `scripts/audit_artifact_bucket.py`).
- Group by `pressure_bucket` and report the top 100 blockers per
  bucket.

Artifacts:

- `scripts/audit_background_bucket.py`
- `reports/background-bucket-audit.md`
- `reports/background-bucket-audit.json`

Acceptance gate:

- The report enumerates every `candidate_background` and
  `external_substrate` IC that blocks at least one admitted target.
- The report includes the psycholinguistic profile of each top
  blocker.

Falsifier:

- If the top 100 background blockers do not have meaningfully higher
  frequency / earlier AOA / higher concreteness than the bottom 100,
  the "promote-by-norms" hypothesis fails and Phase 2 must propose a
  different rule.

## Phase 2: Author the promotion rules (Codex review)

Status: queued.

Purpose: write the smallest deterministic rule set that promotes
high-quality P2-terminal ICs from `candidate_background` to the base.

Candidate rules to consider:

- Promote `candidate_background` ICs with `high_frequency = True` and
  `high_concreteness = True` to a new pressure_bucket
  `base_promotable_common`, which the validator treats as part of the
  augmented layer.
- Promote `candidate_background` ICs that are admitted and have
  high containment over the unfolding index (top-N blockers) into a
  new pressure_bucket `base_promotable_load_bearing`.
- Promote ICs already in P2 seed AND with `high_frequency` AND
  `early_aoa` AND `high_concreteness` into a new pressure_bucket
  `base_promotable_grounded_norms`.

All rules must be data-driven feature conjunctions, not per-IC lists.

Artifacts:

- `prompts/background-bucket-rules.md`
- `reports/codex-background-bucket-rules-review.md`
- `scripts/kernel_pressure_table.py` (edited)
- `scripts/validate_assembler_definitions.py` (edited only if the
  validator's base derivation needs to add new bucket names; the
  preferred shape is for the promotion bucket to flow through the
  existing `PRIMITIVE_BUCKETS` set)
- `reports/background-bucket-rules.md` documenting rationale and
  positive/negative examples per rule.

Acceptance gate:

- Every rule has rationale plus two examples (one positive, one
  negative). Hand-list count is zero.
- Codex pre-implementation review is run and committed to
  `reports/codex-background-bucket-rules-review.md`. Implementation
  follows only after a "proceed" or "proceed with changes" verdict.

Falsifier:

- If the rules require more than ten hand-listed exceptions, Phase 2
  fails and the rules must be redesigned.

## Phase 3: Rebuild

Status: queued.

Purpose: regenerate `data/kernel-pressure-table.{csv,json}` and
`reports/kernel-pressure-table.md` with the new rules.

Acceptance gate:

- Row count unchanged at `85,137`.
- Zero L0 ICs lost.
- Zero obstruction_core ICs lost.

Falsifier:

- Loss of any L0 or obstruction_core IC fails Phase 3 immediately.

## Phase 4: Re-run validator and diff

Status: queued.

Purpose: measure the impact.

Artifacts:

- `reports/base-assembler-validation.{md,json}` (rewritten).
- `reports/background-bucket-reaudit-impact.{md,json,-per-sense.csv}`
  produced by a new `scripts/background_bucket_reaudit_impact.py`
  (mirrors `scripts/artifact_bucket_reaudit_impact.py`).

Acceptance gate:

- Same target selection count (`15,872` admitted rows).
- Per-IC bucket migration enumerated.
- Hard regression gate: `regressed_count = 0`.

Falsifier:

- If closure rate at `closure_size <= 200` does not rise by at least
  2 absolute percentage points, the background-bucket promotion rules
  did not move the needle. The workstream then flips to Phase 5E:
  hand-author `data/base-assembler-rules.yaml` informed by the joint
  failure histogram.

## Phase 5: Decide what comes next

Status: queued, dependent on Phase 4.

If the closure-rate falsifier closes (>= 2 pp rise), queue a similar
mirrored re-audit on `circular_dependency` or a deeper validator-side
extension (P2-terminal promotion via norms alone).

If the closure-rate falsifier trips, flip to hand-authored
`data/base-assembler-rules.yaml` informed by the failure histogram now
available across three workstreams' worth of evidence.

## Immediate commit-sized slice

Phase 1: write `scripts/audit_background_bucket.py`, generate
`reports/background-bucket-audit.{md,json}`. Read-only over existing
inputs.
