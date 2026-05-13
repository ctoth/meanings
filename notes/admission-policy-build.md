# Admission Policy Build (agent, 2026-05-12)

Task: make human Up-Goer list the admitted extension of a defeasible admission policy
(replacing scripts/sense_ingestion_rebuild.py's HUMAN_ADMITTED_TAGS filter).

State:
- src/meanings/admission.py written: ICRecord/SenseRecord -> ICFacts (derived predicates)
  -> AdmissionPolicy (declarable Rule list + superiority) -> AdmissionVerdict
  (decision admit/exclude/quarantine/uncertain + fired/defeated rules + rationale + aliases).
  Rules: r_block_symbol_only(100), r_block_sense_mismatch(100), r_quarantine_low_conf(50),
  r_admit_lexical(10), r_admit_phrase_idiom(10, togglable). Per-class precision lookup from
  reports/lexicality-headtohead.md rule-classifier CV precisions (proper-name 0.386 = low).
- tests/test_admission.py: 9 tests, all pass.
- TODO: scripts/admission_export.py (load build_sense_level_paper_wordnet_graph metadata,
  run policy, emit data/oewn-upgoer-admitted.json + reports/admission-policy.json),
  gunray demonstrator for `no`, reports/admission-policy.md.
- Old filter admitted 121,375 ICs (reports/oewn-sense-ingestion-summary.json).

## Update (later, 2026-05-12)
- scripts/admission_export.py + scripts/admission_gunray_demo.py written.
- gunray demo WORKS: admit_ic_no=YES (negation, nothing attacks), admit_nobelium_only=NO
  (r_block_symbol_only defeats r_admit_lexical_nob), ~admit_nobelium_only=YES. Mermaid in
  reports/gunray-demo-admission-no-{negation,nobelium,block}.mmd.
- admission_export.py running in background (pid 33530, log scratch/admission_export.log) --
  the slow part is build_sense_level_paper_wordnet_graph (~925k candidate matches resolution).
  Original sense_ingestion_rebuild took similar; expect ~10-20 min wall clock.
- TODO: wait for export -> get counts -> write reports/admission-policy.md -> rerun full pytest.

## Update 3
- First export (model absent): admit 43896, exclude 26299, quarantine 0, uncertain 76778.
- Rerun (model present): IDENTICAL numbers. The trained model classifies color-as-noun as
  technical-term (p0.51) -- a real classifier hole, not a fallback artifact. color/colour DO
  merge into ic:color (forms color,colour) but get tagged technical-term/symbol-code/uncertain,
  zero lexical-word -> uncertain. Honest finding: policy only as good as upstream tags.
- no -> admit, alias [no], Nobelium (No) symbol-code sense excluded. CORRECT.
- s/a/e/g -> exclude (all symbol-code; single-char rule fires before short-token whitelist).
- quarantine=0 structurally: missing-evidence path never fires (build only keeps glossed senses);
  low-conf path needs lexical-word tag with conf<0.5 AND precision<0.5, but lexical-word precision
  is 0.816 -> never. Note this in report.
- DEVIATION FIXED: removed technical-term from SYMBOL_ONLY_TAGS (task spec block set is
  {symbol-code,abbreviation,taxon,chemical,proper-name}). Re-running export now.
- Then: write reports/admission-policy.md, rerun full pytest.

## Update 4
- Refactored sense-mismatch + low-conf-quarantine: restricted to lexical-word readings (phrase
  shaky -> deferred to uncertain, not excluded). _shaky_lexical helper: shaky iff non-surface
  AND a low-precision class (proper-name P~0.39) implicated in reasons. Both rules gated on
  not-has_solid_lexical. 9 admission tests pass.
- numbers from the run BEFORE this refactor (technical-term removed from block set, model present):
  admit 43896, exclude 35531, quarantine 0, uncertain 67546, total 146973. delta vs old 121375 = -77479.
  NOTE: exclude went 26299->35531 between runs partly due to other agents editing identity_clusters.py
  / retraining the model concurrently -> numbers not perfectly reproducible. Need a final clean run.
- TODO: final export run, then reports/admission-policy.md, then full pytest.

## DONE
Final run: admit 48049 / exclude 30078 / quarantine 0 / uncertain 68846 (total 146973).
Old filter admitted 121375 -> delta -73326. gunray demo works. Full pytest 113 passed.
Files: src/meanings/admission.py, scripts/admission_export.py, scripts/admission_gunray_demo.py,
tests/test_admission.py, reports/admission-policy.{md,json}, data/oewn-upgoer-admitted.json (gitignored, 89MB),
reports/gunray-demo-admission-no-{negation,nobelium,block}.mmd, .gitignore updated.
