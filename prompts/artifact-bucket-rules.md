# Review Task: Artifact-bucket re-audit rules (Phase 2 of artifact-bucket-reaudit-workstream)

## Context

The `meanings` repo's kernel pressure table is built by joining several
signals over the OEWN definition graph. The Phase 5A validator
(`reports/base-assembler-validation.md`) showed that 63.5% of failed
admitted target rows at `closure_size <= 200` are blocked by ICs labelled
`pressure_bucket = resource_artifact`. The Phase 1 audit
(`reports/artifact-bucket-audit.md`) drilled in and found the
misclassification is wider than the workstream theory predicted.

Phase 1 numbers (verbatim):

- 4,376 `resource_artifact` rows total.
- 1,468 block at least one admitted target.
- Top 100 blockers by `typed_bucket`: technical_term 55, morphology_register_artifact 27, abbreviation_or_code 11, proper_name 7.

Concrete misclassifications visible in the audit:

- `abbreviation_or_code`: `ic:act, ic:can, ic:out, ic:all, ic:law` —
  flagged via the cascade rule `len(surface.replace("_", "")) <= 3` even
  though their SUBTLEX frequencies are 5.04, 6.72, 6.59, 6.71, 5.07.
- `proper_name`: `ic:energy, ic:more, ic:hope` — flagged via Wiktionary
  proper-name lexicality even though all three are common English.
- `technical_term`: `ic:quality, ic:part, ic:work, ic:force, ic:power,
  ic:purpose, ic:point, ic:value, ic:complete, ic:life, ic:form,
  ic:activity, ic:function` — flagged via Wiktionary technical-term tag
  or hardcoded TECHNICAL_TOKENS, but all are common abstract English.
- `morphology_register_artifact`: `ic:showing, ic:writing, ic:drawing,
  ic:government, ic:environment, ic:considered, ic:expected, ic:designed,
  ic:established, ic:putting, ic:accepted, ic:coming, ic:existing` —
  flagged via `-ed/-ing/-ment` suffix with known stem even though many
  are real productive English nouns/verbs.

Root structural defect: `scripts/kernel_pressure_table.py` joins
psycholinguistic data only via `data/base_english_candidates.csv`. ICs
not in that CSV get no `frequency / age_of_acquisition / concreteness`
fields, even when the underlying surface is in the
`data/psycholinguistic/{frequency,age_of_acquisition,concreteness}.csv`
norms. Verified: `act, can, out, all, law` all have frequency rows
(5.04–6.72) and AOA rows but their pressure-table cells are empty.

## What you are reviewing

Two proposed code changes plus one new pressure-table bucket. Below is
the full proposal. Critique whether this is the right shape, whether it
satisfies the workstream's "rules-not-handlists" gate, whether the
falsifier is sound, and whether anything is missing.

## Files to read

- `reports/artifact-bucket-reaudit-workstream.md` — the parent
  workstream. Honour its non-negotiable boundaries.
- `reports/artifact-bucket-audit.md` — Phase 1 evidence.
- `reports/artifact-bucket-audit.json` — full enumeration of 4,376
  `resource_artifact` ICs and their containment counts.
- `scripts/classify_seed_disagreement.py` — the existing cascade
  classifier. Reading is mandatory.
- `scripts/kernel_pressure_table.py` — where the pressure_bucket is
  assigned. Reading is mandatory.
- `data/kernel-pressure-table.csv` — sample rows to confirm the column
  shapes I describe above.
- `data/psycholinguistic/` — the norms files (`frequency.csv`,
  `age_of_acquisition.csv`, `concreteness.csv`).

## Proposed changes

### Change A — Fix the psycholinguistic join in `kernel_pressure_table.py`

Currently each pressure-table row inherits `frequency / aoa /
concreteness / high_frequency / early_aoa / high_concreteness` from the
matching `data/base_english_candidates.csv` row, or gets empties if the
candidate row is absent. Change this so the builder loads
`data/psycholinguistic/frequency.csv` and `age_of_acquisition.csv` and
`concreteness.csv` directly and looks up by `primary_alias` (the surface
form of `ic_id`). Existing thresholds for `high_frequency`,
`early_aoa`, `high_concreteness` are read from
`scripts/build_psycholinguistic_csvs.py` (or whatever module owns the
threshold constants) and re-applied.

### Change B — Add a new pressure_bucket `abstract_common`

In `scripts/kernel_pressure_table.py`, in the
`pressure_bucket(row)` function, add an override that runs BEFORE the
existing `if typed_bucket in ARTIFACT_BUCKETS or flags & ...` clause:

```python
if typed_bucket in ARTIFACT_BUCKETS and bool(row.get("high_frequency")):
    return "abstract_common", "artifact lexicality but high frequency"
```

`abstract_common` is added as a top-level pressure_bucket. It is NOT
added to `ARTIFACT_BUCKETS`. The existing pressure_bucket fallthrough
continues unchanged.

### Change C — Optional classifier tightening in `classify_seed_disagreement.py`

The bare `len(surface.replace("_", "")) <= 3` clause inside the
`abbreviation_or_code` cascade is too aggressive — it routes `act, can,
out, all, law` to artifact even though they have strong frequency
support. Change to require an additional signal: a digit, a `_abbr`
suffix, `numeric_form` flag, `symbol-code` lexicality, or
`abbreviation` in tag_counts. Frequency lookups stay out of the
classifier (the override in Change B handles those after the fact);
this change only removes the over-trigger.

## What the rules together produce

1. Every IC now has psycholinguistic fields populated whenever the
   underlying surface has SUBTLEX/AOA/concreteness data, regardless of
   `base_english_candidates.csv` membership (Change A).
2. ICs with artifact lexicality but high SUBTLEX frequency get the new
   `abstract_common` pressure_bucket. They no longer count as artifact
   pressure (Change B).
3. Short surfaces no longer auto-route to `abbreviation_or_code` unless
   they also have a real abbreviation signal (Change C).

The Phase 5A validator's `artifact_share` at `closure_size <= 200`
should drop by at least 5 absolute percentage points after rebuild.
That is the workstream's Phase 4 falsifier.

## Questions for you

1. **Is the rules design data-driven enough?** The workstream forbids
   per-IC hand-listing. Change A is purely structural (a join fix).
   Change B is one threshold check. Change C is a feature-conjunction
   tightening. Is any of this still secretly per-IC?

2. **Is `abstract_common` the right bucket name?** It catches some
   concrete words (`work, point, body`). Would `common_vocabulary`
   or `lexical_word` be more honest? The workstream allows a new
   top-level bucket; naming is open.

3. **Is the `high_frequency` threshold strong enough on its own?** Or
   should the override also require `early_aoa` (to avoid pulling
   technical jargon that happens to appear in some corpora often)?
   Falsifier: words like `ic:hypertensin` have no AOA data and very
   low frequency — they would not trip the override either way.

4. **Are we leaving real artifacts in the wrong bucket?** Are there
   ICs in the audit's top blockers that genuinely SHOULD stay in
   `resource_artifact` after the override? For example, `ic:more` is
   currently `proper_name`; the override would move it to
   `abstract_common`. Is that correct?

5. **Is the falsifier (>= 5 pp drop in artifact_share at
   `closure_size <= 200`) the right magnitude?** Given that
   `technical_term` alone accounts for 55% of top-100 blockers and
   blocker_sum 86,494 (audit table), a successful rebuild should move
   a large fraction. Is 5 pp soft, right, or aggressive?

6. **Does Change A break any downstream consumer?** Reading the
   `kernel_pressure_table.py` and any caller will tell you.

7. **Is the classifier tightening (Change C) safe?** Specifically: does
   the new conjunction-of-signals criterion still catch known real
   abbreviations like `ic:pa` or `ic:abbr`?

## Output

Write your review to `reports/codex-artifact-bucket-rules-review.md`
with:

- **Verdict** (one paragraph): proceed / proceed with changes /
  blocked.
- **Question-by-question answers** matching the numbered list above.
- **Concrete edits** if you propose them, in the form of suggested
  code snippets, file paths, and the exact place they go.
- **Risks** I missed.

Be direct. No flattery, no preamble.
