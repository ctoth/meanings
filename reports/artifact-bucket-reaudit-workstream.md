# Artifact Bucket Re-audit Workstream

Status: executable workstream, started 2026-05-16.

Parent: `reports/kaikki-obstruction-workstream.md` (Phase 5B).

Predecessor evidence: `reports/base-assembler-validation.md` — closure rate
at `closure_size <= 200` is 0.142 and artifact share is 0.635; top blockers
are common-English abstract nouns labelled `resource_artifact`
(`technical_term`).

## Why this workstream exists

The Phase 5A validator showed that the closure ceiling of the implicit base
(L0 + augmented layer = 326 ICs) is not bounded by missing primitives. It is
bounded by the pressure table's `resource_artifact` classifications. The top
40 blocking ICs include `act, amount, time, quality, capable, event, part,
energy, complete, force, power, life, regard, attention, force, purpose,
intensity, unit, satisfaction, strength` — many of these carry the
`resource_artifact` bucket via `typed_bucket = technical_term` from
`scripts/classify_seed_disagreement.py`. They are clearly common English used
pervasively in OEWN definitions, not technical vocabulary specific to a
register.

Until the classifier stops calling these technical_term, every later
expansion of the base (Phase 5C, Phase 6) measures itself against a falsifier
that is dominated by a misclassification.

## What this workstream does NOT do

- Does not add new primitive ICs. That is Phase 5C, queued behind this one.
- Does not author `data/base-assembler-rules.yaml`. The validator still runs
  on implicit defaults.
- Does not change the unfolding-index builder or the obstruction probe.
- Does not re-run the Kaikki staged seed.
- Does not redefine L0 or P2.

The single deliverable is a refined Kaikki seed disagreement classifier and
a rebuilt kernel pressure table, with an A/B comparison report showing what
moved and why.

## Non-negotiable boundaries

- Do not migrate any IC out of `resource_artifact` without a written rule
  applied to the classifier. No ad-hoc per-IC allowlists.
- Do not regress: any sense classified as `closed` under Phase 5A must
  remain `closed` after the rebuild. This is enforced as a hard gate.
- Do not collapse buckets that are semantically distinct. `taxon`,
  `proper_name`, `abbreviation_or_code`, and `morphology_register_artifact`
  remain unchanged.
- Do not promote ICs into the base in this workstream. The base derivation
  in `scripts/validate_assembler_definitions.py` stays exactly as it is.
- Do not delete the existing `data/kernel-pressure-table.csv` artifact
  before the rebuild succeeds and passes the regression gate.

## Phase 0: Baseline lock

Status: done by Phase 5A.

Inputs frozen for comparison:

- `data/kernel-pressure-table.csv` (current)
- `reports/base-assembler-validation.md` (current)
- `reports/base-assembler-validation.json` (current)

These are the pre-change snapshots. Phase 4 will diff against them.

## Phase 1: Inventory the suspect ICs

Status: queued.

Purpose: produce a deterministic list of ICs currently in
`resource_artifact` that the next phase will evaluate against new rules.
Read-only.

Tasks:

- Read `data/kernel-pressure-table.csv` and select rows where
  `pressure_bucket == "resource_artifact"`.
- Within that selection, group by `typed_bucket`.
- For each `typed_bucket`, attach blocker count from
  `reports/base-assembler-validation.json` (the
  `blocker_counts_by_ic` map for the augmented base).
- Sort by blocker count descending.

Artifacts:

- `scripts/audit_artifact_bucket.py`
- `reports/artifact-bucket-audit.md`
- `reports/artifact-bucket-audit.json`

Acceptance gate:

- The report enumerates every `resource_artifact` IC that blocks at least
  one admitted target. ICs with zero blocker counts are listed in an
  aggregate summary line, not row by row.
- The report does not propose changes. It only describes the state.

Falsifier:

- If the top 100 blockers do not concentrate in one or two `typed_bucket`
  values, the "abstract-noun-as-technical_term" theory was wrong and
  Phase 2 must reformulate the classifier change before proceeding.

## Phase 2: Author the classifier-change rules

Status: queued.

Purpose: write the smallest deterministic rule set that re-routes
abstract-noun common English out of `technical_term` without touching real
technical vocabulary.

Tasks:

- Read `scripts/classify_seed_disagreement.py` and locate the current
  `technical_term` rule.
- Draft new buckets and rules. Candidate buckets:
  - `abstract_common`: high-frequency abstract nouns used pervasively in
    OEWN glosses (process, quality, state, condition, event, time, place,
    amount, kind, ...).
  - `bridging_helper`: connectives and light verbs whose semantic content
    is grammatical rather than lexical (`act, occur, happen, cause, make,
    take, give, do, ...`).
- The rules must be data-driven where possible: word-frequency thresholds,
  morphology checks, POS distribution. No hand-listed ICs unless a written
  rationale is attached in the rules file.
- Add new buckets to `ARTIFACT_BUCKETS` in
  `scripts/kernel_pressure_table.py` only if the new bucket really should
  count as artifact pressure. If the new bucket should NOT count as
  artifact, leave `ARTIFACT_BUCKETS` alone so that the pressure-bucket
  derivation routes those ICs to `candidate_background` or a new bucket of
  their own.
- Pressure-table bucket policy update may add a new top-level bucket
  (e.g. `abstract_helper`) to keep `resource_artifact` for genuine
  artifacts and `circular_dependency` for unsupported cyclic ICs. Document
  the decision in the rebuild report.

Artifacts:

- `scripts/classify_seed_disagreement.py` (edited)
- `scripts/kernel_pressure_table.py` (edited if buckets change)
- `reports/artifact-bucket-rules.md` describing each rule, its motivation,
  and one positive and one negative example.

Acceptance gate:

- Every rule has a one-paragraph rationale and at least two examples
  (one that the rule re-routes, one that the rule explicitly does not).
- No rule references a specific IC by hand. Rules must be testable
  features (frequency band, POS distribution, morphology signature).
- A pre-implementation Codex review is run via
  `protocols:external-agents` against `prompts/artifact-bucket-rules.md`
  and the report is committed to
  `reports/codex-artifact-bucket-rules-review.md`. If Codex's verdict is
  blocked or needs material change, do not implement until iterated.

Falsifier:

- If the rules require more than 10 hand-listed exceptions to avoid
  obvious misclassifications, the rules are not rule-derived and Phase 2
  fails. Iterate before proceeding.

## Phase 3: Rebuild the pressure table

Status: queued.

Purpose: regenerate `data/kernel-pressure-table.csv` with the new
classifier output, then regenerate `reports/kernel-pressure-table.md`.

Tasks:

- Re-run `scripts/classify_seed_disagreement.py` to regenerate
  `data/kaikki-seed-disagreement-typed.csv`.
- Re-run `scripts/kernel_pressure_table.py` to regenerate
  `data/kernel-pressure-table.csv`, `data/kernel-pressure-table.json`,
  and `reports/kernel-pressure-table.md`.

Acceptance gate:

- Row count in `kernel-pressure-table.csv` matches the pre-snapshot
  row count captured in Phase 0. Absolute numbers depend on the
  upstream graph build and may drift if the unfolding-index or
  staged-seed pipelines regenerate; this gate compares against the
  snapshot, not a fixed integer.
- Bucket counts reconcile against the new typed-bucket histogram in
  `reports/kaikki-seed-disagreement-typed.md`.

Falsifier:

- If the new pressure table loses any L0 IC or any
  `obstruction_core` IC, Phase 3 fails. The classifier change must not
  touch the obstruction surface.

## Phase 4: Re-run the Phase 5A validator and diff

Status: queued.

Purpose: measure the impact of the classifier change against the frozen
baseline.

Tasks:

- Run `scripts/validate_assembler_definitions.py` against the rebuilt
  pressure table.
- Diff `reports/base-assembler-validation.json` before and after.

Artifacts:

- `reports/base-assembler-validation.md` (rewritten)
- `reports/base-assembler-validation.json` (rewritten)
- `reports/artifact-bucket-reaudit-impact.md` — the A/B diff. Required.

Acceptance gate:

- The new `reports/base-assembler-validation.md` shows the same target
  selection count as the pre-snapshot's selection count. Absolute
  numbers depend on the unfolding index; this gate compares against
  the snapshot, not a fixed integer.
- The augmented-layer size may change only via R1's norm-join correction
  (high-frequency obstruction-core ICs newly receive frequency data and
  legitimately migrate into `assembler_helper`). The impact report must
  enumerate every IC added to or removed from the augmented layer so the
  change is reviewable.
- `reports/artifact-bucket-reaudit-impact.md` reports closed-count before
  and after, artifact-share before and after, MGY before and after, and
  the list of ICs that changed bucket.

Hard regression gate:

- Every `sense_id` classified `closed` in the pre-change validator output
  must still be `closed` after. The impact report must include a
  `regressed_count` field; if it is non-zero, the workstream fails until
  the regression is investigated.

Falsifier:

- If the artifact share at `closure_size <= 200` does not drop by at
  least 5 absolute percentage points, the classifier change failed to
  address the bottleneck. The workstream concludes that the bottleneck
  is not artifact mislabelling but base-too-small, and the next
  recommendation flips to Phase 5C (rules YAML or base expansion).

Result (2026-05-16):

- Implemented `scripts/artifact_bucket_reaudit_impact.py`.
- Re-ran `scripts/validate_assembler_definitions.py` against the rebuilt
  pressure table to refresh `reports/base-assembler-validation.{md,json}`.
- Generated `reports/artifact-bucket-reaudit-impact.{md,json}` plus
  `reports/artifact-bucket-reaudit-impact-per-sense.csv`.
- Hard regression gate: `regressed_count = 0`. PASS.
- Falsifier: artifact share at `closure_size <= 200` dropped from
  `0.6345` to `0.5745`, delta `-6.01 pp`. PASS (threshold 5 pp).
- Closure rate at `closure_size <= 200`: `0.1418` -> `0.1424`,
  delta `+0.06 pp`. Closed count under augmented base: `2,110` -> `2,119`.
- Augmented-layer size: `9` -> `14`. Added by R1: `ic:ask, ic:called,
  ic:do, ic:has, ic:than` (five obstruction-core ICs that previously had
  empty frequency cells; the norm join filled them and they correctly
  reclassified into `assembler_helper`).
- Bucket transitions: 953 ICs changed pressure bucket. `resource_artifact ->
  external_substrate` 780, `resource_artifact -> common_vocabulary` 165,
  `resource_artifact -> assembler_helper` 3, `resource_artifact ->
  candidate_background` 3, `circular_dependency -> assembler_helper` 2.
- Known side effect: single-letter / very-short surfaces with high SUBTLEX
  frequencies (`ic:s, ic:t, ic:m, ic:re, ic:no, ic:if, ic:oh`) migrated to
  `common_vocabulary`. These are mixed - some are genuine abbreviations
  (s, t, m, re) and some are real high-frequency content words (no, if,
  oh). Documented in the impact report for the next workstream to refine.

## Phase 5: Decide what comes next

Status: done 2026-05-16.

Phase 4 closed the falsifier:

- Artifact share at `closure_size <= 200` dropped `-6.01 pp` (threshold
  was 5 pp).
- Closure rate at `closure_size <= 200` rose `+0.06 pp`. The rise is
  marginal but real; the principal win is the bucket migration.
- Hard regression gate: `regressed_count = 0`.

Per the workstream's own decision rule, the next workstream is the
mirrored re-audit on `candidate_background` and `external_substrate`,
which are now the two largest non-artifact blocker buckets at
`closure_size <= 200`:

- `background` blockers: `3,664`.
- `artifact` blockers: `8,551` (still the largest, but a re-audit of
  the post-rebuild artifact ICs is a refinement of the same
  hypothesis - the next blow against the closure ceiling is on the
  non-artifact side).
- `external` blockers: `450`.

The next workstream is filed at
`reports/background-bucket-reaudit-workstream.md`. Its design mirrors
this one: inventory the suspect ICs, author classifier or
pressure-bucket rules under Codex review, rebuild, re-run the
validator, diff with the hard regression gate.

## Workstream complete

This workstream is closed. The downstream commit-sized slice belongs
to `reports/background-bucket-reaudit-workstream.md`, Phase 1.
