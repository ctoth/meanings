# Artifact Bucket Re-audit Rules

Phase 2 of `reports/artifact-bucket-reaudit-workstream.md`. Implementation
follows the pre-implementation Codex review at
`reports/codex-artifact-bucket-rules-review.md`.

This document records the rules applied in the rebuild. The rebuild itself
is Phase 3; the validator re-run is Phase 4.

## Rule R1 — Direct psycholinguistic join in the pressure-table builder

**File:** `scripts/kernel_pressure_table.py`.

**Rule:** the pressure-table builder now loads
`data/psycholinguistic/frequency.csv`,
`data/psycholinguistic/age_of_acquisition.csv`, and
`data/psycholinguistic/concreteness.csv` directly. For each row, the
builder looks up by `normalize_surface(primary_alias)` and applies the
thresholds from `scripts/base_english_candidates.py`:

- `high_frequency`: SUBTLEX zipf >= 5.0
- `early_aoa`: Kuperman AOA <= 6.0
- `high_concreteness`: Brysbaert concreteness >= 4.0

`normalize_surface` is duplicated from `base_english_candidates.py`:
`value.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "")`.
This keeps the join consistent with the existing candidates workbench.

**Rationale.** Previously the pressure-table builder inherited norm
values only via `data/base_english_candidates.csv` membership. ICs not
in that CSV (`ic:act, ic:all, ic:can, ic:out, ic:law`, plus many
Kaikki-only ICs) received empty norm cells even though the underlying
surface had SUBTLEX data. Verified directly: `act` has frequency 5.04,
`all` 6.71, `can` 6.72, `law` 5.07, `out` 6.59 in
`data/psycholinguistic/frequency.csv`. The pressure-table cells were
all empty before this rule.

**Positive example:** `ic:act` (frequency 5.04, AOA 6.42) → cells now
populated; `high_frequency = True`.

**Negative example:** `ic:hypertensin` (no norm data) → cells stay
empty; `high_frequency = False`.

## Rule R2 — `common_vocabulary` pressure-bucket override

**File:** `scripts/kernel_pressure_table.py`, `pressure_bucket(row)`.

**Rule:** a new override runs first in the cascade:

```python
if typed_bucket in COMMON_VOCABULARY_ELIGIBLE and bool(row.get("high_frequency")):
    return "common_vocabulary", "artifact lexicality but high frequency"
```

`COMMON_VOCABULARY_ELIGIBLE = ARTIFACT_BUCKETS - {"taxon"}`. The override
applies to four `typed_bucket` values:

- `abbreviation_or_code`
- `proper_name`
- `technical_term`
- `morphology_register_artifact`

`taxon` is excluded; taxonomic vocabulary is artifact pressure even when
the surface happens to be a common English form. The override does NOT
touch `candidate_flags` like `numeric_form` or `multiword`; those still
route to `resource_artifact` via the existing artifact-flag clause.

`common_vocabulary` is added as a top-level pressure_bucket. It is NOT
added to `ARTIFACT_BUCKETS`, so downstream consumers that filter on
artifact pressure see the migrated ICs as non-artifact.

**Rationale.** The Phase 1 audit
(`reports/artifact-bucket-audit.md`) showed the top 100 blocking
`resource_artifact` ICs were dominated by common English: `act, quality,
part, energy, work, force, power, life, hope, more`. Their artifact
classification is real (Wiktionary tags them with proper-name or
technical-term readings, or they are short surfaces that the cascade
catches) but their use as definers in OEWN is common-English use, not
artifact use. The high-frequency threshold cleanly separates these from
genuine artifacts like `ic:hypertensin` or `ic:carbonate`.

**Positive example:** `ic:work` (typed_bucket=technical_term, frequency
5.90, high_frequency=True) → `common_vocabulary`.

**Negative example:** `ic:hypertensin` (typed_bucket=technical_term, no
frequency data, high_frequency=False) → stays `resource_artifact`.

**Codex audited risk.** The override can in principle pull genuine
common abbreviations (`tv`, `us`, `s`, `re`) into `common_vocabulary` if
they are artifact-typed AND high-frequency. The impact report (Phase 4)
must list every IC whose `pressure_bucket` changes, so any such case is
visible for human review.

## Rule R3 — Tighter `abbreviation_or_code` short-form trigger

**File:** `scripts/classify_seed_disagreement.py`,
`bucket_for(...)`.

**Rule:** the bare clause
`len(surface.replace("_", "")) <= 3` is replaced with a stricter
conjunction:

```python
or (
    len(surface.replace("_", "")) <= 2
    and candidate is None
    and p2_row is None
)
```

The full disjunction with explicit abbreviation lexicality, tag_counts,
numeric form, digit content, and `_abbr/_abbrev` suffix is preserved.
The conjunctive short-form clause now fires only when the surface is at
most two non-underscore characters AND has no candidate workbench row
AND no P2 lexicality row, i.e. when the surface is short and
unsupported by any non-Kaikki evidence.

**Rationale.** The previous standalone `len <= 3` clause routed `act,
can, out, all, law` (3-letter content words) and any other 3-letter
form to `abbreviation_or_code`. Codex flagged that simply removing the
short-form clause would break detection of `ic:pa` (genuine short code
with no candidate or P2 row). The conjunctive form keeps `ic:pa`
captured while letting `act/can/out/all/law` continue through the
cascade where their high-frequency signal (Rule R2) reroutes them.

**Positive example:** `ic:pa` (no candidate, no P2, length 2) →
`abbreviation_or_code`.

**Negative example:** `ic:act` (length 3, has Kaikki staged-seed
support) → passes through the abbreviation clause and reaches a later
cascade arm; pressure_bucket then routes via Rule R2.

**Codex audited limitation.** Rule R3 still does not catch `ic:abbr` if
the surface happens to have a P2 lexicality row, because the
conjunction requires `p2_row is None`. The fix here is to enrich
classifier inputs with explicit abbreviation evidence rather than
weaken the rule further. That is out of scope for Phase 2.

## Falsifier discipline

Phase 4 will trip the workstream's falsifier if the rebuild's
`artifact_share` at `closure_size <= 200` does not drop by at least 5
absolute percentage points and no `closed` sense regresses. The Phase 2
rules together rest on the prediction that the artifact-share drop
will be large because R2 alone targets 200+ blocking `resource_artifact`
rows with combined containment over 35,000 admitted-target references.

## Hand-list count

Zero. No rule references a specific IC. R1 is a structural join. R2 is
a threshold conjunction over an existing norm. R3 is a feature
conjunction over existing classifier inputs.
