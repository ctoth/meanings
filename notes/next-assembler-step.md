# Next assembler step — survey notes

2026-05-16. Q asked: look at recent work, think, talk to codex and gemini, figure out the next part for assembly/kernel.

## What I observed

- Commits up to `71fb621` "Record kernel pressure result".
- Latest reports: `kernel-pressure-table.md` (2026-05-16 13:09) and `kaikki-obstruction-workstream.md` (13:10). The workstream file is the executable plan-of-record.
- Phases 0–4 are marked done in the workstream. Phase 4 produced `data/kernel-pressure-table.{csv,json}` and `reports/kernel-pressure-table.md`.
- Pressure table rows: 85,137. Obstruction-core rows: 86. L0 rows: 317. Clean candidate rows: 1,476.
- Obstruction-core bucket split: circular_dependency 55, resource_artifact 18, primitive_candidate 11, assembler_helper 2.
  - primitive_candidate ICs: animal, answer, certain, desire, express, helpful, name, place, plural, request, useful.
  - assembler_helper ICs: giving, office.
- Workstream's "Immediate Commit-Sized Slice" at the bottom names Phase 5: `data/base-assembler-rules.yaml` + `scripts/validate_assembler_definitions.py`. Validator must consume `data/sense-unfolding-index.json` and `data/kernel-pressure-table.csv`.
- Phase 5 acceptance gate: a definition either closes under the selected base or reports the missing ICs; the validator must distinguish primitive failure, assembler-helper failure, artifact failure, and graph-data failure.
- Phase 5 falsifier: if common target definitions require huge closures or many artifact exceptions, the assembly-language hypothesis is weakened and the report says so.
- Sibling tooling: `../argumentation` provides ADF/BAF, enforcement, ranking semantics, SAT/ASP encodings. `../gunray` provides defeasible-logic four-valued YES/NO/UNDECIDED/UNKNOWN. `../belief-set` has alphabet ≤16 so unusable for vocabulary work directly.
- `data/sense-unfolding-index.json` exists. `reports/unfolding-index.md` (May 15) documents it.
- Untracked: `data/oewn-upgoer-admitted-expanded.json`, `notes/kaikki-argumentation-next-steps.md`, `notes/p2-seed-export-review.md`.

## What I have not verified

- I have not read `scripts/build_unfolding_index.py` or the unfolding-index schema. Need that before drafting a validator that consumes it.
- I have not opened `data/kernel-pressure-table.csv` to check the actual column names against the workstream spec.
- I have not yet asked codex or gemini.

## Current state

- Prompt `prompts/next-assembler-step.md` drafted with 5 questions.
- Codex (`b7ttsejfv`) and Gemini (`b2lwxbu7h`) dispatched in parallel.
- Gemini returned: verdict = proceed with Phase 5 as-stated, but commit script + minimal YAML together. Proposed **Marginal Grounding Yield (MGY)** as falsifier: closed-sense increase from adding the 13 ICs to L0; threshold <1.0 closed-sense per added IC = inefficient. Flagged polysemy grounding gap (sense S grounded if any sense of definiens IC is grounded, OR-junction). Flagged 51 MB unfolding-index size → streaming reader. Flagged closure truncation at 500 → indeterminate, not failed. Report at `reports/gemini-next-assembler-step-report.md`.
- Codex still running.

## My own draft verdict (pre-Codex)

Phase 5 is named next, but a 13-IC base against 20,744 senses will close almost nothing (P90 closure 157, max 1,591). Better first commit: **validator first, no YAML**. Treat L0 ∪ primitive_candidate ∪ assembler_helper as the implicit base. Output a failure histogram. YAML is then *derived* from the top blockers rather than guessed. Gemini partially agrees (script + minimal YAML together) and adds the MGY falsifier — that's a good metric to steal.

## Blocker

Codex pending.

## 2026-05-16 evening — v1 validator results

Wrote `scripts/validate_assembler_definitions.py`. Runs in 1.4s on the full unfolding index.

Real numbers (admitted targets, augmented base = L0 ∪ primitive_candidate ∪ assembler_helper):

- L0 base size: **317**. Augmented base size: **326**. Augmented *layer* size: **9** (not 13 — because `animal, answer, name, place` were already in L0).
- Selected target rows: 15,872 admitted senses.
- Closure rate at `closure_size <= 200`: L0 = **0.1366**, augmented = **0.1418**.
- MGY: **8.56** closures added per added base IC (77 new closures from 9 added ICs).
- Artifact share at `closure_size <= 200`: **0.635** — most failures hit ICs flagged `resource_artifact`.
- Status histogram (augmented, `closure_size <= 200`): artifact 9,445 / background 3,048 / closed 2,110 / external 205 / circular 77.

Augmented-layer marginal usage (closed_uses on the 9 added ICs):
- `certain` 13, `desire` 8, `office` 5, `giving` 4, `plural` 3, `useful` 1
- `express` 0, `helpful` 0, `request` 0 — **deadweight** in the augmented layer.

Top blockers (with bucket): `act (artifact, 3633)`, `amount (background, 2109)`, `time (background, 2003)`, `quality (artifact, 1933)`, `capable (background, 1844)`, `event (background, 1802)`. Many "artifact"-bucketed top blockers (`act, quality, part, event, time`) are clearly core English — the pressure-table artifact classification is over-aggressive on abstract nouns. This is a real finding, not a bug.

Falsifier verdict: **weakened** — closure rate 0.142 < 0.60, artifact share 0.635 > 0.10. MGY passes (8.56 > 1.0). So the *augmented-layer* hypothesis is fine; the *60% closure under this base* falsifier was unrealistic because P2 has 2,739 ICs and our base is 326.

Interpretation:
- The 9 augmented-layer ICs deliver real marginal closures. Worth keeping `certain, desire, office, giving, plural`; flag `express, helpful, request` for review.
- The next genuine workstream is **not** more primitive hunting — it is **artifact-bucket re-audit**. Words like `act, quality, part, time, event, energy, complete, force, power, life` blocking thousands of definitions are not technical_term artifacts. The classifier in `scripts/classify_seed_disagreement.py` mislabels abstract-noun common-English as `technical_term`.

## Current blocker

None. Validator clean (`uv run pyright scripts/validate_assembler_definitions.py` → 0 errors). Re-ran with same numbers; output stable.

## 2026-05-16 — Ready to commit

Workstream `reports/kaikki-obstruction-workstream.md` updated: Phase 5 renamed to "Phase 5A: implicit-base validator (done)" with results; new Phase 5B "Re-audit `resource_artifact` Classifications" queued; "Immediate Commit-Sized Slice" rewritten to point at 5B.

Codex auto-committed its review report as `fee476b "Review next assembler step"` — `reports/codex-next-assembler-step-report.md` is already tracked. Don't re-commit.

Files for this commit:
- new: `scripts/validate_assembler_definitions.py`
- new: `reports/base-assembler-validation.md`
- new: `reports/base-assembler-validation.json`
- new: `reports/gemini-next-assembler-step-report.md`
- new: `prompts/next-assembler-step.md`
- new: `notes/next-assembler-step.md` (this file)
- modified: `reports/kaikki-obstruction-workstream.md`

Skip (Q's parallel work, unrelated): `data/oewn-upgoer-admitted-expanded.json`, `notes/kaikki-argumentation-next-steps.md`, `notes/p2-seed-export-review.md`.

`*.log` and `*.lock` are gitignored — progress log won't be picked up.

## 2026-05-16 evening — executing artifact-bucket-reaudit-workstream

Phase 5A committed `b9991f3`. Workstream spinout committed `3856085`. Now executing the child workstream end-to-end on Q's instruction.

Tasks created (1=Phase 1 in_progress, 2..5 blocked sequentially).

Phase 1 progress:
- Wrote `scripts/audit_artifact_bucket.py`. Read-only. Reads pressure CSV + unfolding-index. For each `resource_artifact` IC, computes containment count = admitted, non-truncated unfolding rows whose `transitive_closure_ic_ids` mentions it. Groups by `typed_bucket`. About to run.
- Metric is "upper bound on blocker impact" — not the validator's exact blocker count (which depends on the fixpoint base). Right for Phase 1 inventory.
- Validator JSON persists only top 50 blockers; sticking with direct containment query to keep audit self-contained.

## Current blocker

None. About to run the audit script.

## Phase 1 done (`f3d49ff`)

`scripts/audit_artifact_bucket.py` shipped. Numbers:
- 4,376 `resource_artifact` rows total. 1,468 block ≥1 admitted target. 2,908 non-blockers (zero containment).
- Top-100 typed_bucket distribution: technical_term 55, morphology_register_artifact 27, abbreviation_or_code 11, proper_name 7. Falsifier passes (82% concentration in 2 buckets).
- Misclassification is wider than predicted: 4 buckets need addressing, not just technical_term.

## Phase 2 in progress — root cause identified

Read `scripts/classify_seed_disagreement.py`. The cascade rule `len(surface.replace("_", "")) <= 3` is the source of `abbreviation_or_code` over-matching `act, can, out, all, law`. Other false positives are driven by upstream Wiktionary tag_counts.

Critical structural defect found: `scripts/kernel_pressure_table.py` joins psycholinguistic data ONLY via `data/base_english_candidates.csv` membership. ICs not in that CSV (e.g. `ic:act, ic:all, ic:can, ic:out, ic:law`) get empty `frequency` fields even though `data/psycholinguistic/frequency.csv` HAS them (5.04, 6.71, 6.72, 6.59, 5.07 — all high). Verified directly.

Proposed three changes:
- **A**: fix the psycholinguistic join in `kernel_pressure_table.py` to look up by surface alias directly.
- **B**: add a new pressure_bucket `abstract_common`; if `typed_bucket ∈ ARTIFACT_BUCKETS` and `high_frequency=True`, route there instead of `resource_artifact`.
- **C**: tighten the classifier's bare `len <= 3` short-form rule to require an additional positive abbreviation signal.

Drafted `prompts/artifact-bucket-rules.md` with 7 questions for Codex. Dispatching next.

## Current blocker (revised)

None. About to dispatch Codex pre-implementation review.

## Phase 2 done (`dda6ccb`)

Codex review at `5f4f26a` returned key corrections:
- Rename `abstract_common` → `common_vocabulary`. ✓ Applied.
- Exclude `taxon` from the high-frequency override. ✓ Applied via `COMMON_VOCABULARY_ELIGIBLE = ARTIFACT_BUCKETS - {"taxon"}`.
- Reject the proposed Rule C verbatim — it would have broken `ic:pa` detection. Use `len <= 2 AND no candidate AND no P2` instead. ✓ Applied.
- Do NOT add `early_aoa` to the override — `power` has AOA 7.48. ✓ Did not add.
- Normalize surface like `base_english_candidates.py`. ✓ Duplicated `normalize_surface` exactly.
- Impact report must list every IC that changed bucket. Pending Phase 4.

Three rules shipped:
- R1: pressure table joins norms directly from `data/psycholinguistic/*.csv`.
- R2: `common_vocabulary` override on artifact ∩ high_frequency (excl. taxon).
- R3: bare `len<=3` short-form clause tightened to `len<=2 AND no candidate AND no P2`.

Hand-list count: zero.

Pyright complains about a pre-existing `writerows` typing issue in both modified scripts. Verified pre-existing via `git stash`. Not in scope.

## Phase 3 done (rebuild)

Acceptance gates all clean:
- Rows: 85,137 → 85,137 ✓
- L0 ICs lost: 0 ✓
- Obstruction-core ICs lost: 0 ✓

Bucket changes:
- `candidate_background`: 46,152 → 46,155 (+3)
- `external_substrate`: 34,541 → 35,321 (+780)
- `resource_artifact`: 4,376 → 3,425 (−951)
- `common_vocabulary`: 0 → 165 (NEW)
- `circular_dependency`: 55 → 53 (−2)
- `primitive_candidate`: 11 → 11 (unchanged)
- `assembler_helper`: 2 → 7 (+5)

The 951-IC drop in `resource_artifact` is the headline; 165 went to `common_vocabulary` (high-frequency override), 780 went to `external_substrate` (R3 short-form change), 5 obstruction-core artifacts gained frequency data and became assembler_helpers.

Typed bucket distribution:
- `abbreviation_or_code` 1,114 → 328 (−786) — R3 worked
- `resource_specific_tail` 31,212 → 31,993 (+781)
- Others unchanged

`data/kernel-pressure-table.pre.csv` and `.json`, plus `reports/base-assembler-validation.pre.{md,json}` saved as pre-state snapshots for Phase 4 diff.

## Current state — Phase 4 about to start

Need to: run validator, save new output, write `reports/artifact-bucket-reaudit-impact.md` with closed-count, artifact-share, MGY before/after; enumerate every IC whose bucket changed; verify hard regression gate (no closed sense regressed).

## Phase 4 done (`af4ecc0`)

`scripts/artifact_bucket_reaudit_impact.py` reuses validator logic (via sys.path insert + import) to classify each target under pre and post pressure tables and diff.

**Hard regression gate: PASS** — `regressed_count = 0`.
**Falsifier: PASS** — artifact share dropped 6.01 pp at `closure_size <= 200` (threshold 5 pp).

Closure rate at ≤200: 0.1418 → 0.1424 (+0.06 pp). Closed senses: 2,110 → 2,119 (+9).

Augmented-layer size grew 9 → 14. Workstream gate originally said "same 9". Updated to allow R1-driven growth with enumeration; the five additions (`ask, called, do, has, than`) are obstruction-core ICs that gained frequency data from R1.

953 ICs migrated bucket. Single-letter words (`s, t, m, re, no, if, oh`) migrated to `common_vocabulary` via R2 — Codex predicted this; mixed-quality migrations documented for the next workstream.

## Phase 5 in progress

Decision: falsifier closed → queue mirrored re-audit on `candidate_background` (3,664 blockers) and `external_substrate` (450). Writing `reports/background-bucket-reaudit-workstream.md` next.

## Current blocker

None.

## 2026-05-16 evening — background-bucket workstream begin

Q said "Go!" for the background-bucket workstream. Phases 6-10 created.

### BG Phase 1 done (`e75db6d`)

`scripts/audit_background_bucket.py` mirrors artifact audit but reports two buckets and contrasts top-100 vs bottom-100 norms.

**`candidate_background`** — 46,155 rows, 4,101 blocking:
- Top-100 freq median 4.87, bot-100 2.82 (Δ 2.04) ✓
- Top-100 AOA median 6.32, bot-100 10.42 ✓
- Top-100 has 98 P2 seeds, bot-100 has 11 ✓
- 33 ICs have all three norm flags; 181 HF only; 335 EA only; 629 HC only
- Top blockers concentrate in HF+EA (not HC, because abstract nouns score low on concreteness): time, mind, body, change, make, give, over, full, together, different, small, especial(special), great, under, feeling

**`external_substrate`** — 35,321 rows, 3,258 blocking:
- Top-100 freq median 4.06, bot-100 3.36 (Δ 0.70) — modest
- 0 P2 seeds by definition
- Phase 2 should focus on candidate_background; treat external as secondary

Falsifier holds (top-100 norms meaningfully higher than bot-100).

### BG Phase 2 in progress

Drafted `prompts/background-bucket-rules.md` proposing one main rule:

**Rule R1**: in `pressure_bucket(row)`, route to new `base_promotable_grounded_norms` if `p2_seed AND high_frequency AND early_aoa AND NOT obstruction_core`. Excludes HC because abstract nouns underweight on concreteness; excludes obstruction_core because those are already handled.

**Rule R2**: extend validator's `PRIMITIVE_BUCKETS` to include the new bucket so augmented layer auto-picks it up.

Sent to Codex (background task `b7god7ozk`). 7 questions including: is HC-exclusion right, should external_substrate get a parallel rule, falsifier risk if rule footprint is too narrow.

## Current state

Awaiting Codex.

## BG Phase 2 done (`1d321a0`)

Codex review corrections applied:
- Renamed bucket → `base_promotable_terminal_common` (cleaner: states both terminal and common claims).
- Placed rule AFTER artifact/obstruction-core/external_substrate clauses (only catches what would otherwise be candidate_background).
- Rejected adding `strict_admission` guard — would cut footprint 27% (loses time, change, number, cause, water, right, about, move).
- Updated validator's hardcoded report strings (`L0 + primitive_candidate + assembler_helper` and `13 augmented-layer ICs`) to derive from `PRIMITIVE_BUCKETS` and `len(base_aug - base_l0)` per Codex's gotcha catch.
- Did not add parallel external_substrate rule (out of scope).

Rule shape:
- BR1 in `kernel_pressure_table.py` pressure_bucket(): `p2_seed AND high_frequency AND early_aoa AND NOT obstruction_core` → `base_promotable_terminal_common`.
- BR2 in `validate_assembler_definitions.py`: extend `PRIMITIVE_BUCKETS` to include `BASE_PROMOTABLE_BUCKETS`.

Sanity check passed (positive case = `base_promotable_terminal_common`; not P2 = external_substrate; obstruction_core = assembler_helper; not HF = candidate_background).

Codex measured footprint at 121 ICs with containment sum 43,913 over admitted targets. Falsifier risk: medium. 121 may not be enough to move closure rate +2 pp.

## BG Phase 3 in progress

Pre-state snapshotted to:
- `data/kernel-pressure-table.bg-pre.{csv,json}`
- `reports/base-assembler-validation.bg-pre.{md,json}`

Rebuilt pressure table: 85,137 rows, 86 obstruction-core rows (unchanged).

Need to verify: 0 L0 lost, 0 obstruction_core lost, and check new bucket count.

## Current blocker

None. About to verify Phase 3 gates.
