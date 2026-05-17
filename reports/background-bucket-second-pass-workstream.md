# Background Bucket Second-Pass Workstream

Status: queued, drafted 2026-05-16.

Parent: `reports/kaikki-obstruction-workstream.md` (Phase 5E).
Predecessor: `reports/background-bucket-reaudit-workstream.md` closed
at commit `a880bd3` with the BR1 (HF+EA+P2) promotion delivering
`+6.21 pp` closure-rate gain and `+925` newly closed senses under
augmented base.

Predecessor evidence:
`reports/background-bucket-reaudit-impact.md`, plus the original
`reports/background-bucket-audit.{md,json}` for the per-bucket
psycholinguistic profiles.

## Why this workstream exists

BR1 promoted `121` of `1,668` P2-seed `candidate_background` blockers
into the validator base. That is `7%` of the eligible cohort. The
remaining `1,547` P2-seed blockers fail BR1 because they lack either
the `high_frequency` flag or the `early_aoa` flag (or both).

Status histogram at `closure_size <= 200` after BR1:

- `artifact` 7,912
- `background` 3,174 (was 3,664, dropped `-490`)
- `closed` 3,044 (was 2,119, rose `+925`)
- `external` 685 (was 450)
- `circular` 99 (was 101)

`background` is still the second-largest bucket. A loosened promotion
rule could capture more of the residual blockers. The mirrored
hypothesis: a `high_frequency`-only rule (drop EA) is the natural
loosening because top blockers carry HF more reliably than EA in the
psycholinguistic data the project ships.

The risk: looser rules may promote ICs that are themselves
under-defined in OEWN, leading to spurious closures whose recursive
closure would not actually ground. The hard regression gate catches
this; the workstream's secondary acceptance gate (no regression of
prior-workstream closed senses) keeps the loosening safe.

## What this workstream does NOT do

- Does not author `data/base-assembler-rules.yaml`.
- Does not change the unfolding-index builder.
- Does not redefine L0 or P2.
- Does not re-litigate prior workstreams' rules. BR1 is preserved.
- Does not promote any IC outside `candidate_background` /
  `external_substrate`.

## Non-negotiable boundaries

- The new rule must be additive: it extends `BASE_PROMOTABLE_BUCKETS`
  or routes the same bucket via a looser feature conjunction, not by
  weakening BR1's conditions in place.
- Hard regression gate: no sense closed before this workstream may
  regress.
- Cumulative regression: no sense closed under the post-BR1 baseline
  may regress under the post-loosening base.

## Phase 0: Baseline lock

Inputs frozen at commit `a880bd3`:

- `data/kernel-pressure-table.csv` (post-BR1).
- `reports/base-assembler-validation.{md,json}`.
- `reports/background-bucket-reaudit-impact.{md,json,-per-sense.csv}`.

## Phase 1: Profile loosening candidates

Status: queued. Read-only.

Purpose: compute the would-be footprint and norm profile of three
candidate loosenings.

Tasks:

- Variant A: P2-seed AND HF (drop EA).
- Variant B: P2-seed AND EA (drop HF).
- Variant C: P2-seed AND `age_of_acquisition <= 8` (relax EA bound).

For each variant, compute:

- IC count that would be newly promoted (delta over BR1).
- Sum of admitted containment over newly promoted ICs.
- Median frequency / AOA / concreteness of newly promoted ICs.
- Overlap with current `assembler_helper` and L0.

Artifacts:

- `scripts/profile_background_loosening.py`
- `reports/background-loosening-profile.{md,json}`

Acceptance gate:

- Each variant produces concrete counts and norm profiles.
- The report names the variant with the best estimated yield per
  added IC (closures-per-IC inferred from containment).

Falsifier:

- If no variant produces a candidate pool with strictly higher mean
  containment than the lowest-decile of BR1's promoted ICs, the
  loosening hypothesis is weak and the workstream flips to circular
  re-audit or to deeper validator extension.

## Phase 2: Author the loosened rule (Codex review)

Status: queued.

Purpose: write the rule for the variant Phase 1 recommended, with a
Codex pre-implementation review.

Mandatory pre-implementation artifact: `prompts/background-loosening-rules.md`
and resulting `reports/codex-background-loosening-rules-review.md`.

Implementation hook: introduce a new pressure_bucket
`base_promotable_extended` or similar (name to be decided after Phase
1). Add to `BASE_PROMOTABLE_BUCKETS`. The validator's `PRIMITIVE_BUCKETS`
extension already picks up new buckets in that set without further
edits.

## Phase 3: Rebuild

Status: queued. Standard.

## Phase 4: Re-run validator and diff with cumulative regression gate

Status: queued.

The regression gate now checks two baselines:

- Original pre-BR1 closed set (artifact-bucket workstream's
  post-rebuild closures).
- Post-BR1 closed set (this workstream's predecessor).

Both must be preserved.

Falsifier:

- If closure rate at `closure_size <= 200` does not rise by at least
  another 2 pp on top of BR1's gains, the loosening did not move the
  needle proportionally to its footprint, and the workstream
  recommendation is to stop loosening and pivot to circular_dependency
  re-audit or deeper validator extension.

## Phase 5: Decide what comes next

If the falsifier closes, the next workstream is the validator-side
extension: unfolding-index beyond P2 terminals via per-IC closure
backtracking, which is the only remaining lever after the
norm-promotion ladder.

If the falsifier trips, the workstream's recommendation is to
hand-author `data/base-assembler-rules.yaml` informed by the joint
failure histogram from all four prior workstreams. This is the
classical "rules YAML" Phase 5C originally queued behind 5A.

## Immediate commit-sized slice

Phase 1: write `scripts/profile_background_loosening.py`, generate
`reports/background-loosening-profile.{md,json}`. Read-only over
existing inputs.
