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
