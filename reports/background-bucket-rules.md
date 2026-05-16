# Background Bucket Re-audit Rules

BG Phase 2 of `reports/background-bucket-reaudit-workstream.md`.
Implementation follows the pre-implementation Codex review at
`reports/codex-background-bucket-rules-review.md`.

This document records the rules applied in the BG rebuild. The rebuild
itself is BG Phase 3; the validator re-run is BG Phase 4.

## Rule BR1 — `base_promotable_terminal_common` promotion bucket

**File:** `scripts/kernel_pressure_table.py`, `pressure_bucket(row)`.

**Rule:** placed in the cascade AFTER the artifact-flag clause, the
obstruction-core clauses, and the `external_substrate` clause,
immediately before the final `candidate_background` return:

```python
if (
    bool(row.get("p2_seed"))
    and bool(row.get("high_frequency"))
    and bool(row.get("early_aoa"))
    and not bool(row.get("obstruction_core"))
):
    return "base_promotable_terminal_common", "P2 terminal plus high frequency plus early AOA"
```

A new module-level constant
`BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})`
records the bucket. The bucket is NOT added to `ARTIFACT_BUCKETS` or
`COMMON_VOCABULARY_ELIGIBLE`.

**Rationale.** The Phase 1 audit
(`reports/background-bucket-audit.md`) showed `candidate_background`
top-100 blockers have frequency median 4.87 vs bottom-100 2.82, AOA
median 6.32 vs 10.42, and 98/100 P2-seed membership vs 11/100. This
contrast supports a promote-by-norms rule. The rule's three feature
conjuncts encode three real claims:

- `p2_seed`: the IC is a P2 terminal under the unfolding index; using
  it as a base IC is consistent with the index's terminal semantics.
- `high_frequency`: SUBTLEX zipf >= 5.0; the IC is common English.
- `early_aoa`: Kuperman AOA <= 6.0; the IC is acquired early and
  belongs to basic vocabulary.

The `not obstruction_core` guard avoids duplicating the
`assembler_helper` promotion that already covers high-frequency
obstruction-core ICs.

**HC is excluded** by design. Top blockers like `time, mind, change,
feeling, knowledge, ability, knowledge, attention` are abstract nouns
with concreteness < 4.0; requiring HC would drop the rule's footprint
from 121 to 32 ICs and miss the load-bearing abstract definers. The
audit's per-bucket concreteness contrast (top-100 conc median 2.74 vs
bottom-100 2.48) does not support HC as a useful filter for this
slice.

**`strict_admission` is NOT a guard.** Of the 121 HF+EA+P2
`candidate_background` matches Codex measured, 33 have
`strict_admission=False` including `time, change, number, cause,
water, right, about, move`. Adding the guard would cut the footprint
by 27% and remove motivating examples. P2-terminal status is the
admission anchor for this promotion.

**Positive examples.** Rule fires:

- `ic:mind` (P2, frequency 5.69, AOA 5.37) -> `base_promotable_terminal_common`.
- `ic:body` (P2, frequency 5.29, AOA 4.28) -> `base_promotable_terminal_common`.

**Negative examples.** Rule does not fire:

- `ic:amount` (P2 but frequency 4.39, AOA missing) -> stays
  `candidate_background`. Not HF.
- `ic:intended` (not P2, frequency 4.07) -> stays `external_substrate`.
- `ic:hypertensin` (not P2, low frequency) -> stays `resource_artifact`.

**Intentional HC misses.** Rule does fire on low-concreteness ICs:

- `ic:feeling` (P2, freq 5.23, AOA 5.31, conc 1.68) -> promoted.
- `ic:time` (P2, freq 6.29, AOA 5.16, conc 3.07) -> promoted.

These are correct: HC is not required.

## Rule BR2 — Validator base derivation update

**File:** `scripts/validate_assembler_definitions.py`.

**Rule:** extend the constants block:

```python
BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})
PRIMITIVE_BUCKETS = (
    frozenset({"primitive_candidate", "assembler_helper"}) | BASE_PROMOTABLE_BUCKETS
)
```

`build_bases()` is unchanged: it derives the augmented layer by
filtering `pressure_bucket in PRIMITIVE_BUCKETS`, so the new bucket is
picked up automatically.

The hardcoded report strings
`"L0 + primitive_candidate + assembler_helper"` and
`"13 augmented-layer ICs"` are replaced with derivations from
`PRIMITIVE_BUCKETS` and `len(base_aug - base_l0)` respectively, per
Codex's observation that stale documentation strings would silently
contradict the implementation.

**Rationale.** The validator's augmented-layer construction is the
single hook this workstream needs to touch. Codex's "preferred shape:
let the promotion bucket flow through `PRIMITIVE_BUCKETS`" was
adopted.

**Positive example.** With BR1 and BR2 applied, an IC at
`pressure_bucket = base_promotable_terminal_common` is part of the
augmented base derived by `build_bases()`, so the validator's closure
fixpoint admits it as base.

**Negative example.** An IC remaining at `candidate_background`
continues to act as a non-base IC; the validator's closure fixpoint
still requires the IC to be groundable via at least one of its
senses' direct-definiens being already groundable.

## Falsifier discipline

BG Phase 4 trips the workstream's falsifier if the rebuild's closure
rate at `closure_size <= 200` does not rise by >= 2 absolute percentage
points. Codex measured the rule's `candidate_background` footprint at
121 ICs with containment sum 43,913 over admitted targets. That
containment is necessary but not sufficient for the 2 pp gate; a
target only closes when its full closure set is groundable, not when
some of its closure is groundable. Phase 4's per-band breakdown will
show whether the 121-IC promotion converts many partial-coverage
failures into full closures.

If Phase 4 trips the gate, the next decision is not to loosen BR1
preemptively but to inspect which target closures are still
incomplete after promotion, and to decide whether to widen the rule
(e.g. drop EA) or shift to hand-authored YAML.

## Hand-list count

Zero. BR1 is a four-feature conjunction over existing norm columns.
BR2 is a one-line set extension.
