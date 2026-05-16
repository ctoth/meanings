# Verdict

Proceed with changes. The HF+EA+P2 rule is a clean Phase 2 slice and should not include HC or `external_substrate`, but the implementation should place the promotion after the current artifact, obstruction, and external-substrate branches so it only promotes rows that would otherwise fall to `candidate_background`. I would also rename the bucket away from `grounded_norms` unless "grounded" is explicitly defined as P2-terminal support, and the validator report text must be updated along with `PRIMITIVE_BUCKETS`.

## Question-by-question answers

1. The single conjunction is clean enough: P2 seed plus high frequency plus early AOA is a defensible deterministic feature rule. Do not split obstruction-core HF+EA into a separate bucket for this workstream. Obstruction-core rows already have a different semantic route: high-frequency obstruction-core rows become `assembler_helper`, and non-helper obstruction-core rows remain circular-pressure evidence. Adding another obstruction-core bucket would mix two review questions.

2. `base_promotable_grounded_norms` is acceptable only if "grounded" means "P2-terminal anchored", not concreteness-grounded. Because the proposed rule intentionally excludes HC, the name reads slightly misleading. I prefer `base_promotable_terminal_common`: it states the two real claims, terminal support and common-English norms, without implying concreteness. `base_promoted_norms` hides the P2-terminal condition, `grounded_common` is too vague, and `terminal_common` is good but loses the local `base_promotable_` convention.

3. Exclude HC. The audit supports that choice. In `candidate_background`, top blockers are more frequent and earlier-AOA than the bottom blockers, but not more concrete in a useful way: top-100 concreteness median is 2.740 vs bottom-100 2.480, while the top-100 has only 10 high-concreteness rows. The proposed HF+EA+P2 rule matches 121 current `candidate_background` rows; adding HC would reduce that to 32 and would miss load-bearing abstract/common definers such as `time`, `mind`, `feeling`, `change`, `make`, `give`, `over`, `together`, and `different`.

4. Do not add a `strict_admission` guard unless the workstream deliberately wants to recut the rule. The prompt's admission premise is not true if "admitted" means the pressure-table `strict_admission` column: 33 of the 121 HF+EA+P2 `candidate_background` matches have `strict_admission=false`, including high-containment rows such as `time`, `change`, `number`, `cause`, `water`, `right`, `about`, and `move`. Adding `strict_admission` would cut the containment sum from 43,913 to 33,298 and would remove several of the motivating examples. The safer implementation constraint is placement: run the rule only after artifact/resource, obstruction-core, and external-substrate routing, immediately before the final `candidate_background` return.

5. Do not add a parallel `external_substrate` rule in this workstream. The JSON audit shows `external_substrate` has zero P2-seed rows, weaker frequency contrast, and no P2-terminal closure anchor. A parallel rule would be a different semantic claim, not a mirror of R1.

6. Falsifier risk is medium. The rule is not only about 50 ICs: the current audit gives 121 HF+EA+P2 `candidate_background` matches, all with positive admitted containment, and their containment sum is 43,913. However, the prompt's "top-100 all qualify" implication is wrong: only 31 of the top 100 `candidate_background` rows satisfy P2+HF+EA. Containment references are also not the same as newly closed target rows; if many remaining closures still contain unpromoted background/artifact blockers, the closure-rate gain may miss the 2 pp gate. Do not loosen to P2+HF before the first rebuild. P2+HF would widen the current match set only to 164 rows and would weaken the early-acquisition rationale; measure R1 first, then loosen only if the Phase 4 falsifier trips.

7. Extending `PRIMITIVE_BUCKETS` is the right validator hook and the core logic is localized: `build_bases()` is the only code path using the set. The missed risk is report correctness. `scripts/validate_assembler_definitions.py` hardcodes "L0 + primitive_candidate + assembler_helper" in the report and hardcodes "13 augmented-layer ICs" in the marginal-usage section. Those strings must become derived from the actual primitive bucket set and augmented-layer size, or Phase 4's report will be misleading even if the computation is correct.

## Concrete edits

In `scripts/kernel_pressure_table.py`, add the new bucket name as a constant and place the rule after the existing external-substrate branch, immediately before the final `candidate_background` return:

```python
BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})

...

if typed_bucket == "resource_specific_tail" or (
    bool(row["kaikki_staged_seed"]) and not bool(row["p2_seed"])
):
    return "external_substrate", "Kaikki-only or resource-tail signal"
if (
    bool(row.get("p2_seed"))
    and bool(row.get("high_frequency"))
    and bool(row.get("early_aoa"))
    and not bool(row.get("obstruction_core"))
):
    return "base_promotable_terminal_common", "P2 terminal plus high frequency plus early AOA"
return "candidate_background", "known candidate surface without current obstruction pressure"
```

If you keep the original bucket name, use it consistently in the same placement and document that "grounded" means P2-terminal anchored, not high-concreteness.

In `scripts/validate_assembler_definitions.py`, extend the primitive set and remove the stale hardcoded report text:

```python
BASE_PROMOTABLE_BUCKETS = frozenset({"base_promotable_terminal_common"})
PRIMITIVE_BUCKETS = (
    frozenset({"primitive_candidate", "assembler_helper"})
    | BASE_PROMOTABLE_BUCKETS
)
```

Then derive the report label from `PRIMITIVE_BUCKETS` and replace "13 augmented-layer ICs" with `len(base_aug - base_l0)`.

In `reports/background-bucket-rules.md`, include at least these examples:

- Positive: `ic:mind` or `ic:body` -> promoted by P2+HF+EA.
- Negative: `ic:amount` -> stays `candidate_background` because it is P2 but not HF+EA.
- Negative for HC: `ic:time` or `ic:feeling` -> promoted despite low concreteness; this is intentional.
- Negative for external: `ic:intended` -> stays `external_substrate` because it has no P2 anchor.

## Risks

The biggest risk is semantic drift around "admitted". The pressure table has `strict_admission=false` for several motivating HF+EA+P2 blockers, so the rules report must state why P2-terminal support is the admission anchor for this promotion.

The second risk is over-reading containment counts. The 43,913 containment sum is strong evidence that the selected ICs are load-bearing, but the Phase 4 closure-rate gain depends on complete missing-set coverage per target, not raw blocker frequency.

The third risk is stale validator documentation. If the report text still says the augmented layer is only `primitive_candidate + assembler_helper`, the artifacts will contradict the implementation.
