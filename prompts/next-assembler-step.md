# Review Task: What is the next workstream slice for base-English assembly?

## Context

The `meanings` repo studies the OEWN (Open English WordNet) definition digraph as an
argumentation / belief-revision object. The current workstream (`reports/kaikki-obstruction-workstream.md`)
has just finished Phase 4: a "kernel pressure table" that classifies every IC
(IC = inflection-collapsed lemma sense node) by structural pressure.

Phase 4 output, verbatim from `reports/kernel-pressure-table.md`:

- Rows: 85,137
- Obstruction-core rows: 86 (from a tracked-clause stable-UNSAT analysis on the
  Kaikki largest SCC after self-loops were stripped — see Phase 3/3B)
- L0 rows: 317
- Clean candidate rows: 1,476
- Obstruction-core bucket split: circular_dependency 55, resource_artifact 18,
  primitive_candidate 11, assembler_helper 2
- primitive_candidate ICs: `animal, answer, certain, desire, express, helpful,
  name, place, plural, request, useful`
- assembler_helper ICs: `giving, office`

The workstream's "Immediate Commit-Sized Slice" names Phase 5: write
`data/base-assembler-rules.yaml` and `scripts/validate_assembler_definitions.py`.
The validator should consume `data/sense-unfolding-index.json` and
`data/kernel-pressure-table.csv` and, for each target sense, either close it
under the chosen base or report exactly which ICs prevent closure (distinguishing
primitive / assembler-helper / artifact / graph-data failure).

## Files to Review

- `reports/kaikki-obstruction-workstream.md` (the executable plan-of-record;
  Phase 5 spec is near the bottom)
- `reports/kernel-pressure-table.md`
- `reports/unfolding-index.md`
- `data/kernel-pressure-table.csv` (header + sample rows; columns include
  `ic_id, primary_alias, l0_candidate, clean_candidate, p2_seed,
  kaikki_staged_seed, obstruction_core, obstruction_coverage,
  obstruction_attack_endpoint, strict_admission, evidence_count, frequency,
  age_of_acquisition, concreteness, high_frequency, early_aoa,
  high_concreteness, typed_bucket, flags, pressure_bucket, review_reason`)
- `data/sense-unfolding-index.json` (rows have
  `sense_id, ic_id, label, pos, layer, admission_decision, closure_size,
  seed_closure_size, direct_definiens_ic_ids, transitive_closure_ic_ids,
  seed_ics_in_closure, ...`)
- `notes/kaikki-argumentation-next-steps.md`
- `notes/p2-seed-export-review.md`
- `notes/next-assembler-step.md` (the survey notes I just wrote)

## Questions to Answer

1. **Is Phase 5 the right next slice, or is there a higher-leverage move?**
   The workstream names it next, but a 13-IC primitive+helper set against a
   20,744-sense unfolding index is a very specific bet. Should we instead
   (a) widen the base via a second tracked-core probe on the *non-largest*
   SCCs or on the staged-acyclic remainder, (b) do a closure-coverage scan
   *before* writing the rules YAML so that the rules can be data-driven, or
   (c) just write Phase 5 with whatever base we have?

2. **What is the smallest correct first commit for Phase 5?**
   I want a slice that takes <1 day, produces a falsifiable artifact, and
   sets up further work. Concretely: should the first cut just be
   `scripts/validate_assembler_definitions.py` reading existing
   `data/kernel-pressure-table.csv` as the implicit rules (no YAML yet), or
   should the YAML come first?

3. **What is the falsifier?** The workstream says: "if common target
   definitions require huge closures or many artifact exceptions, the
   assembly-language hypothesis is weakened." Is this the right falsifier,
   or do we need a stronger one (e.g., a hard fraction-of-senses-closed
   threshold)?

4. **Is the 11+2 primitive+helper set actually plausible as a partial
   defining vocabulary?** Words like `plural`, `certain`, `express` are
   suspect. Should the validator allow override flags from a human review
   pass before being run, or is the right move to run it once raw and use
   the failure report as the review pass?

5. **What's missing from the workstream that I haven't noticed?** Cross-check
   against the existing notes/reports and surface gaps.

## Output

Write your review to `reports/{your-name}-next-assembler-step-report.md` with:

- Summary verdict (1 paragraph): proceed with Phase 5 as-stated / proceed with
  variant / different next slice / blocked-need-info.
- Question-by-question answers (numbered to match above).
- Concrete proposal for the next commit, with: file paths, the script's CLI,
  one acceptance gate, and one falsifier.
- Anything else you noticed that the workstream missed.

Be terse and direct. No flattery, no preamble. If you don't know, say so.
