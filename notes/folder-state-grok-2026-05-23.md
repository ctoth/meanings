# Folder state grok — 2026-05-23

Q asked me to evaluate current state of the `meanings/` repo before he loads more theory on me. Pure reconnaissance, no edits.

## What I've observed so far

### Recent commit train (last 20)
The last ~10 commits are a tight, well-numbered "bucket re-audit" cadence:
- Artifact bucket: Phase 1 audit → review → Phase 2 rules apply → pressure-table rebuild → Phase 4 impact → close + queue next.
- Background bucket: identical 5-step shape (Phase 1 → review → Phase 2 → pressure-table rebuild → Phase 4 → close + queue second pass).
- Most recent: `1171549 Eliminate three hardcoded-drift risks` (cleanup after BG cycle).

So the working pattern is **two completed re-audit cycles** (artifact, background), each producing a `*-reaudit-impact.{md,json,csv}` triple plus a `*-second-pass-workstream.md` queueing the next.

### Uncommitted files = the in-flight cycle's intermediate state
- `data/kernel-pressure-table.pre.{csv,json}` — pressure table snapshot taken BEFORE artifact-bucket Phase 2 rules applied (baseline).
- `data/kernel-pressure-table.bg-pre.{csv,json}` — pressure table snapshot taken BEFORE background-bucket Phase 2 rules applied.
- `reports/base-assembler-validation.pre.{md,json}` — validator output pre-artifact rules.
- `reports/base-assembler-validation.bg-pre.{md,json}` — validator output pre-background rules.
- `data/oewn-upgoer-admitted-expanded.json` — Up-Goer admitted-set export (per p2-seed-export-review.md: "unrelated to this commit", got left untracked).
- `notes/kaikki-argumentation-next-steps.md` (2026-05-15) — Kaikki probe analysis; concludes the Dung-symmetric probe didn't falsify the AF reframing — it just used the wrong reading; next slice is mining the seed-disagreement file.
- `notes/p2-seed-export-review.md` (2026-05-15) — adversarial review of commit `1583aa0` (P2 seed export); flagged that the new default `data/oewn-sense-p2-ic-seed.json` is missing from disk, schema_version not checked, Windows-path hard-coded in `command` field.

### Modified
- `reports/synthesis-facet-philosophy-codex.md` — a substantial rewrite/expansion. Headline reframe: from "make a sharp distinction and refuse to blur it" → a structured "Thesis / Harnad / Foundationalism+Coherentism+Argumentation / Yoneda+Harnad / ..." sectioned philosophy facet, ~150 lines added. Looks like a Codex-produced facet draft replacing an earlier sketch. Part of the synthesis paper pipeline (`reports/synthesis-*`).

## What I still need to look at
- The `*.pre` / `*.bg-pre` baseline JSON to see whether the deltas are real (need to compare against the committed `*.md` / `*.json` current versions).
- `reports/background-bucket-second-pass-workstream.md` to see what cycle 3 is supposed to do.
- Whether the "three hardcoded-drift risks" commit explains itself.
- Whether there's a current top-level workstream doc that names the next slice.

## Blocker
None. Continuing reconnaissance.

## 2026-05-23 update — G estimator + validator integration

Q dropped his grounded-content theory (G = I(X;V), apparatus-relative
mutual information between outputs and verdicts). Wrote the standalone
estimator `scripts/grounded_content.py` against the three on-disk
validation snapshots (pre / bg-pre / current). Results:

- Apparatus ceiling at 5-class verdict alphabet: log2(5) * 14,885 =
  34.55 kbits. Current G = 23.97 kbits = 69% of ceiling.
- Per-cycle marginal yield under fine coarsening:
  - artifact-bucket: +2236 bits over +5 base entries = 447 bits/base.
  - background-bucket (BR1): +759 bits over +47 base entries = 16 bits/base.
- Per-cycle marginal yield under closed-vs-not (closure-rate's lens):
  - artifact-bucket: +23 bits = 5 bits/base.
  - background-bucket (BR1): +2091 bits = 44 bits/base.
- The two coarsenings rank the cycles oppositely — artifact bought
  resolution, background bought closure mass. Closure-rate sees only
  the latter.
- L0-only G shifted across snapshots (1.40 -> 1.54 -> 1.54 bits/row)
  even though L0 set is fixed. Means upstream pressure-table rebuilds
  leaked into L0 verdicts; L0 is not a clean baseline.

Q asked to wire G into the validator next to MGY. In progress:
- Added GROUNDED_CONTENT_HEADLINE_BAND and GROUNDED_CONTENT_COARSENINGS
  constants and `math` import to scripts/validate_assembler_definitions.py.
- Pyright flagged unused `math` import — expected, will be consumed by
  the entropy helper I'm about to add.

Next: add shannon_entropy_bits + coarsen_counts + compute_grounded_content
helpers parallel to marginal_grounding_yield; plumb through write_json
and write_report; run validator end-to-end; verify the produced numbers
match the standalone estimator's output on the current snapshot.

## Blocker
None. Resuming validator integration.

## 2026-05-23 — validator G integration done, numbers verified

Validator ran clean in 1.4s. New `grounded_content` block lives in
`reports/base-assembler-validation.json` next to `marginal_grounding_yield`,
with `headline` (band closure_size_le_200, fine coarsening) and a full
`by_band[band_key][coarsening]` matrix containing l0_only, augmented,
delta_G_bits, and bits_per_added_base_entry per slot.

Cross-check against the standalone `scripts/grounded_content.py` results
on the current snapshot — exact agreement to 4 decimals:
- H_bits_per_row (fine, aug): 1.6100 (standalone said 1.6100). Match.
- G_total_bits (fine, aug): 23965.3 (standalone: 23965.3). Match.
- L0 H_bits_per_row (fine): 1.5439 (standalone: 1.5439). Match.
- ΔG / added base entry (fine, vs L0, +61 added): 16.14. Sanity-checks.
- closed_vs_not bits/base entry: 37.98 (this is L0→aug at one snapshot,
  not the cycle delta — different quantity from standalone's "BR1 cycle
  44 bits/base," which was bg-pre→current. Both are legitimate G yields,
  computed against different reference apparatuses).
- triage saturation (aug): 0.591 (mid-resolution apparatus, room to grow).

Headline reading: augmented base is at 69.3% of the 5-class verdict
ceiling (1.61 / 2.32 bits/row). Closure-mass apparatus (binary) at 73.1%
of its 1.0 ceiling. Triage at 59.1% of log2(3).

Pyright diagnostics were stale across edits — `grounded` is in fact used
in write_report body (lines 576/580/581/613/617/618/621); Pyright's
"not accessed" warning was from an analysis pass before the body edits
landed. Real validator run succeeded, so the warnings were noise.

Still to do:
- Verify MD report rendered the new section correctly (spot check).
- Decide whether to commit the regenerated validation.{json,md} alongside
  the script change, or leave them as uncommitted artifacts for Q.
- Q did NOT ask to wire a G falsifier threshold; left verdict block
  unchanged on that axis.

## Blocker
None. About to spot-check MD output.

## 2026-07-14 — question reconstruction + anchor doc

Q returned after ~7 weeks; asked to recover "the question." Reconstruction
arrived at: symbol grounding for the propstore epistemic OS — the question
lives in the seam between meanings/ and ../propstore, which is why neither
repo stated it. Verified: propstore/papers has zero Harnad/Massé/
Vincent-Lamarre (grep hit only Fang_2025); grounding papers live here.

Done this session:
- Spot-checked MD grounded-content render (the last May tail): section
  present at reports/base-assembler-validation.md:49, numbers match the
  verified ones (fine 1.6100 bits/row, sat 0.6934; closed_vs_not 0.7308;
  triage 0.5910). PASS.
- Wrote reports/grounding-question.md — anchor doc: the question, the
  orphaned-layer thesis (TMS/ATMS lineage, semantic-web proof/trust never
  built), six stabs with verdicts + file pointers, composition, missing
  middle term (grounding supply for the base), vision-in-a-summer
  calibration with falsifiers.

Q correction (mid-turn): the replication papers in propstore are NOT just
demand-signal analogy — they are so propstore can defeasibly reason about
facts from papers, with field replication rates as first-class facts it can
argue about (meta-epistemic self-application; Q: "slightly too clever,
LISPy, but wtf why not"). Need to fix §2 of grounding-question.md which
framed replication as mere demand signal.

Next: fix §2, then commit (1) G instrument + snapshots + this note,
(2) grounding-question.md. Leave synthesis-facet-philosophy-codex.md and
Q's parallel untracked files alone.

## Blocker
None.
