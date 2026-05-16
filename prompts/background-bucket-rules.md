# Review Task: Background-bucket promotion rules (BG Phase 2)

## Context

The `meanings` repo's kernel pressure table now classifies 85,137 ICs
across seven buckets. After the artifact-bucket re-audit
(`reports/artifact-bucket-reaudit-workstream.md` closed at commit
`af4ecc0`), the closure-coverage scan
(`reports/base-assembler-validation.md`) shows failure status histogram
at `closure_size <= 200`:

- artifact 8,551
- background 3,664
- closed 2,119
- external 450
- circular 101

`background` is now the next-largest non-artifact bottleneck and is the
target of this workstream. A `background` failure means every blocker of
the failed admitted sense sits in `pressure_bucket =
candidate_background` - i.e. it is an admitted IC that is not L0, not
`primitive_candidate`, not `assembler_helper`, and not flagged as
artifact.

Phase 1 evidence
(`reports/background-bucket-audit.md`,
`reports/background-bucket-audit.json`):

- `candidate_background`: 4,101 of 46,155 rows block at least one
  admitted target. Top-100 frequency median 4.87 vs bottom-100 2.82
  (delta 2.04). Top-100 AOA median 6.32 vs bottom-100 10.42. Top-100
  has 98 P2-seed members, bottom-100 has 11.
- `external_substrate`: 3,258 of 35,321 rows block at least one
  admitted target. Top-100 frequency median 4.06 vs bottom-100 3.36
  (delta 0.70). 0 P2-seed members (by definition).

The norm contrast in `candidate_background` is strong; in
`external_substrate` it is modest. Promote-by-norms looks justified for
`candidate_background` and weakly justified for `external_substrate`.

Counts of `candidate_background` blockers carrying at least one norm
flag:

- `high_frequency` only: 181
- `early_aoa` only: 335
- `high_concreteness` only: 629
- all three (`HF` and `EA` and `HC`): 33

Top blockers concentrate in HF+EA: `time, mind, body, change, make,
give, over, full, together, different, small, especial(=special), great,
under, feeling`. Many have HC=False because abstract nouns have low
concreteness ratings. A rule that requires HC would miss most of these.

The workstream's hypothesis: the right next slice is to promote
high-norm P2-terminal ICs from `candidate_background` into the validator
base via a new `pressure_bucket` that the validator's
`PRIMITIVE_BUCKETS` set treats as part of the augmented layer.

## Proposed rules (you are reviewing)

### Rule R1 — `base_promotable_grounded_norms` promotion

In `scripts/kernel_pressure_table.py`, in `pressure_bucket(row)`, add
an override that runs before the `candidate_background` / `external_substrate`
fallthrough:

```python
if (
    bool(row.get("p2_seed"))
    and bool(row.get("high_frequency"))
    and bool(row.get("early_aoa"))
    and not bool(row.get("obstruction_core"))
):
    return "base_promotable_grounded_norms", "P2 seed plus HF plus EA"
```

The bucket is added to a new `BASE_PROMOTABLE_BUCKETS` set. The bucket
is NOT added to `ARTIFACT_BUCKETS`. The validator's `PRIMITIVE_BUCKETS`
set in `scripts/validate_assembler_definitions.py` is extended to
include `base_promotable_grounded_norms` so the augmented layer
automatically picks up these ICs.

The `not obstruction_core` guard is there because obstruction-core
high-frequency ICs already become `assembler_helper`; we do not want
this rule to duplicate that promotion.

**Why HF + EA, not HF + EA + HC.** Abstract nouns like `time, mind,
feeling, knowledge, change, ability, nature, condition, attention,
information` are common-English load-bearing definers and they
overwhelmingly satisfy HF + EA but NOT HC. Requiring HC would restrict
the rule to ~33 ICs (mostly concrete nouns) and miss the largest
fraction of blockers.

**Why P2 seed.** The unfolding index terminates at P2 ICs. An IC outside
P2 cannot serve as a closure terminal without further unfolding work
beyond this workstream's scope. We restrict promotion to P2-terminal ICs.

**Why not `external_substrate`.** Norm contrast is weaker and there is
no P2-seed support to anchor closure semantics. Out of scope for this
slice.

### Rule R2 — Validator base derivation update

In `scripts/validate_assembler_definitions.py`, change:

```python
PRIMITIVE_BUCKETS = frozenset({"primitive_candidate", "assembler_helper"})
```

to:

```python
PRIMITIVE_BUCKETS = frozenset({
    "primitive_candidate",
    "assembler_helper",
    "base_promotable_grounded_norms",
})
```

so the augmented layer automatically incorporates the new promotion
bucket without further validator changes.

## Falsifier check the rules must pass

Phase 4's falsifier requires closure rate at `closure_size <= 200` to
rise by at least 2 absolute percentage points after rebuild. The
promotion population is currently bounded by the intersection of P2
seed and HF and EA among `candidate_background` rows.

Phase 1 reports:

- Top-100 `candidate_background` blockers: 98 are P2 seed, AOA median
  6.32, freq median 4.87 - all qualify for the rule.
- All-blockers HF + EA among `candidate_background`: not directly
  computed in Phase 1 but bounded below by the top-100 number; needs
  Phase 2 implementation to confirm the actual rule footprint before
  the rebuild.

## Questions for you

1. **Is the rule shape (single conjunction with `not obstruction_core`
   guard) clean enough?** Or should obstruction-core HF+EA be a
   separate bucket?

2. **Is the bucket name `base_promotable_grounded_norms` right?** The
   workstream draft suggested it. Alternatives: `base_promoted_norms`,
   `grounded_common`, `terminal_common`. Naming matters because future
   workstreams will read this.

3. **Should the rule include or exclude HC?** I argue for exclude.
   Counter-argument welcome.

4. **Should the rule require admitted = True?** All current
   `candidate_background` blockers are admitted (since they are
   blockers of admitted targets), but the rule does not check this
   directly. Is that a safety hole?

5. **Should `external_substrate` get a parallel rule?** I propose no
   for this workstream. Counter-argument welcome.

6. **What is the falsifier risk?** The promotion population is bounded
   but not yet measured. If only ~50 ICs qualify, closure rate may not
   rise 2 pp. Should the rule be loosened (e.g. P2 + HF without EA) to
   widen the candidate pool?

7. **Validator-side risk: does extending `PRIMITIVE_BUCKETS` break
   anything?** I have read
   `scripts/validate_assembler_definitions.py` and the change is
   one-line, but you may catch something I missed.

## Files to read

- `reports/background-bucket-reaudit-workstream.md`
- `reports/background-bucket-audit.md`
- `reports/background-bucket-audit.json`
- `scripts/kernel_pressure_table.py`
- `scripts/validate_assembler_definitions.py`
- `reports/artifact-bucket-rules.md` for the style and shape of the
  prior workstream's rules report.

## Output

Write your review to `reports/codex-background-bucket-rules-review.md`
with:

- **Verdict** (one paragraph): proceed / proceed with changes /
  blocked.
- **Question-by-question answers** matching the numbered list.
- **Concrete edits** if you propose them.
- **Risks** I missed.

Be direct. No flattery, no preamble.
