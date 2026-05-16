## Summary verdict

Proceed with a Phase 5 variant: first write the validator as a closure-coverage scan over the existing pressure table, without a YAML rules file. The next uncertainty is not whether another SCC probe can discover more candidate vocabulary; it is whether the current L0 plus pressure-table primitive/helper surface actually closes useful target definitions and where it fails. YAML should come after that first falsifiable run, because otherwise it will encode untested review opinions as rules.

## 1. Is Phase 5 the right next slice?

Yes, but only as a measurement slice. Do not widen the base yet via non-largest SCCs or staged-remainder probes. I do not know whether those probes would surface better primitives, because the reviewed artifacts do not contain that run. The higher-leverage move is to measure the current bet before adding more candidates.

The right next slice is option (b) in spirit: a closure-coverage scan before hand-authored rules. Implement it inside Phase 5, not as a detour. Use `data/kernel-pressure-table.csv` as the implicit rules source: L0 plus `primitive_candidate` plus `assembler_helper`, with `resource_artifact` and `circular_dependency` as failure labels.

## 2. Smallest correct first commit for Phase 5

Write `scripts/validate_assembler_definitions.py` first. No YAML in the first commit.

The script should read:

- `data/sense-unfolding-index.json`
- `data/kernel-pressure-table.csv`

It should derive the base mechanically from existing columns and emit a report. That is smaller and more falsifiable than `data/base-assembler-rules.yaml`, because the YAML would mostly duplicate current CSV bucket decisions before we know whether they matter.

One caveat: `data/sense-unfolding-index.json` truncates `transitive_closure_ic_ids` for 433 rows and `seed_ics_in_closure` for 77 rows. A validator that promises exact missing ICs cannot silently use truncated rows. First commit should either mark those rows as `graph_data_failure` / `exact_missing_unavailable`, or require a regenerated unfolding index with full closure IDs. Treating truncated rows as exact would be wrong.

## 3. Falsifier

The current falsifier is directionally right but too soft. "Huge closures" and "many artifact exceptions" need operational thresholds in the report.

Use one acceptance falsifier for the first commit:

- For non-truncated admitted target senses with `closure_size <= 200`, fewer than 60% close under L0 plus pressure-table primitive/helper ICs, or more than 10% of failures are blocked by `resource_artifact` ICs.

Those numbers are provisional, but a hard threshold is better than a prose-only warning. The report can still show sensitivity bands, e.g. `closure_size <= 50`, `<= 100`, `<= 200`, and all non-truncated rows.

## 4. Plausibility of the 11+2 set

As a standalone defining vocabulary, no. As pressure-backed additions to L0, maybe. The 13 ICs are not the base; they are the extra obstruction-pressure surface on top of 317 L0 rows.

`plural`, `certain`, `express`, `giving`, and `office` are suspicious enough that they should not be human-approved before the first run. Run raw first and let the failure report become the review queue. Pre-run override flags would hide exactly the evidence Phase 5 is supposed to collect.

The first report should show each base IC's marginal usage: how many target closures require it, and examples. If `plural` closes many targets only because of morphology/parser artifacts, that should surface as evidence against it.

## 5. Missing from the workstream

- The validator cannot meet the "reports exactly which ICs prevent closure" gate for truncated closure rows unless it excludes them, labels them graph-data failures, or the unfolding index is regenerated with full closure IDs.
- "Common target definitions" is not defined. Use an explicit first target set, such as admitted kernel rows with `closure_size <= 200`, then report broader sensitivity bands.
- Phase 5 should separate `target_ic_id in base` from `target closure is assembled by base`. A target that is itself L0/P2-seed terminal can trivially close; that should not be counted the same as a non-base definition assembled from primitives.
- The failure taxonomy needs deterministic precedence. Suggested order: truncated/missing graph data, artifact blockers, circular-dependency blockers, missing candidate/background blockers, then allowed-helper/primitive closure.
- The report should include marginal blocker counts by IC, not only aggregate closed/open counts. Otherwise it will not tell the next reviewer whether to add a primitive, reject an artifact, or fix graph parsing.

## Concrete next commit

Files:

- Add `scripts/validate_assembler_definitions.py`
- Add generated report `reports/base-assembler-validation.md`
- Do not add `data/base-assembler-rules.yaml` yet

CLI:

```powershell
uv run python scripts\validate_assembler_definitions.py `
  --unfolding data\sense-unfolding-index.json `
  --pressure-table data\kernel-pressure-table.csv `
  --report reports\base-assembler-validation.md `
  --target admitted `
  --max-closure-size 200
```

Acceptance gate:

- For every non-truncated target row selected by the CLI, the report classifies the row as closed or failed, and failed rows list missing/blocking ICs grouped as primitive/helper/artifact/circular/graph-data/background.

Falsifier:

- On admitted, non-truncated target rows with `closure_size <= 200`, closure rate under L0 plus `primitive_candidate` plus `assembler_helper` is below 60%, or artifact-blocked failures exceed 10% of evaluated rows.
