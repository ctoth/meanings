# Next Assembler Step Report - Gemini

## Summary Verdict
Proceed with Phase 5 as-stated, but implement the validator to support a "dry-run" mode that uses the `kernel-pressure-table.csv` buckets directly before committing to the final `base-assembler-rules.yaml`. This ensures the first commit provides immediate feedback on the 11+2 candidate set's grounding power without hardcoding a potentially flawed base too early.

## Question-by-Question Answers

1. **Is Phase 5 the right next slice?** Yes. It transitions from "identifying candidates" to "measuring impact." Widening the base now (option a) would be speculative; we need the validator to quantify the "grounding yield" of the current 13-IC set first. Option (b) is essentially Phase 5 itself.

2. **Smallest correct first commit?** The script `scripts/validate_assembler_definitions.py` and a minimal `data/base-assembler-rules.yaml` should be committed together. The YAML should explicitly list the L0 base (317 ICs) and the 13 new candidates. This creates a falsifiable "hypothesis" (this specific base can ground X% of the kernel).

3. **What is the falsifier?** The primary falsifier should be a **Marginal Grounding Yield (MGY)** threshold. If adding the 13 candidates to the L0 base increases the total number of closed kernel senses by less than 5%, the "obstruction-core-as-primitive" hypothesis is considered weak. A high MGY confirms these specific 13 ICs are indeed the "linchpins" of the dictionary's circularity.

4. **Plausibility of the 11+2 set?** `plural` is the most suspect—it likely reflects a morphology/parser artifact where "plural of X" edges were not properly collapsed. `certain` and `express` are common in definitions but abstract. The right move is to run the validator raw; the "Failed ICs" report will naturally surface if `plural` is being used as a structural crutch or a genuine semantic primitive. Overrides should be supported via an `exclusions` list in the YAML.

5. **Gaps in the workstream?** The current plan doesn't explicitly handle the **Polysemy Grounding Logic**: if sense $S$ depends on IC $W$, $S$ is grounded if $W \in \text{Base}$ OR if **at least one** sense of $W$ is grounded. The validator must respect this "OR" junction, or it will underestimate closure. Also, the `sense-unfolding-index.json` is large (51MB); the validator should use a streaming reader or a sparse IC-level map to remain performant.

## Concrete Proposal for Next Commit

- **File Paths:** 
  - `data/base-assembler-rules.yaml` (The "Base Definition")
  - `scripts/validate_assembler_definitions.py` (The "Measuring Instrument")
  - `reports/base-assembler-rules.md` (The "Impact Report")

- **CLI:**
  ```powershell
  uv run python scripts\validate_assembler_definitions.py `
    --rules data\base-assembler-rules.yaml `
    --unfolding data\sense-unfolding-index.json `
    --pressure-table data\kernel-pressure-table.csv `
    --report reports\base-assembler-rules.md
  ```

- **Acceptance Gate:** 
  The script correctly identifies a target sense (e.g., `oewn-abdominal__1.08.00..`) as "Closed" if its dependencies (e.g., `ic:abdomen`) are added to the YAML base, and "Failed" (naming `ic:abdomen`) if they are removed.

- **Falsifier:** 
  The Marginal Grounding Yield (additional closed senses / new base ICs) is less than 1.0. If we add 13 ICs and get fewer than 13 new closed senses, the base expansion is inefficient.

## Additional Observations
- **Resource Artifacts:** 18 nodes in the obstruction core are labeled `resource_artifact`. The validator should specifically flag if these "garbage" nodes are blocking a large number of closures, which would prioritize a "Graph Cleaning" phase over a "Primitive Discovery" phase.
- **Unfolding Limit:** The index truncates closures at 500 IDs. If a target sense's closure is truncated, the validator must report it as "Indeterminate/Oversized" rather than "Failed" to avoid false negatives.
