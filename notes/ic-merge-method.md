# IC merge method (agent task, 2026-05-12)

Replacing the 7-pair `HIGH_CONFIDENCE_SPELLING_VARIANTS` whitelist with a real procedure.

## State
- Rewrote `src/meanings/identity_clusters.py`: orthographic rules + Levenshtein<=1 pass
  (selective bucket indexing, hard-capped) + Jaccard gloss gate (threshold 0.34) + union-find ICs
  + `MergeRecord`/`IdentityCluster`/`build_identity_clusters`. Runtime interface
  `identity_cluster_for_form` preserved, backed by lazy-loaded `reports/ic-merge-method.json`.
- `scripts/build_ic_table.py` runs build over OEWN, writes json + summary.json.
- candidate_pairs perf OK on synthetic 40k (~0.9s). Full OEWN build running in background
  (process appears to take several min — the `wn` lemma iteration alone is ~28s).
- Earlier hang was the naive deletion-neighborhood O(n^2) within huge buckets; fixed with
  blanked-position substitution keys + capped indel buckets.

## Results (2026-05-12)
- Fast SQL path added (`_iter_form_pos_sense_def`): build now ~30s (was hanging on wn nav ~6min).
- OEWN: 4248 ICs over 8897 forms (vs 7 ICs / 14 forms baseline). 4770 merge records.
  candidates 33801, gloss gate rejected 29031. merges-by-rule: edit-distance dominates (~3200),
  then ize/ise ~800, doubled-consonant ~315, ae/e ~240.
- Added `_is_code_like` exclusion (Roman numerals, IEC units, no-vowel) to kill junk clusters.
- Known FP class: onomatopoeia chain `chink/clack/click/clink/...` (all glossed "short metallic sound").
- regression: all 7 original pairs still merge.

## Done
- `tests/test_identity_clusters.py` rewritten: 34 tests (was 3), all green. ruff clean.
- `reports/ic-merge-method.md` + `.json` + `.summary.json` written.
- full pytest: 100 passed, 2 failed — the 2 are `test_lexicality.py`, caused by a *concurrent*
  agent's `lexicality.py` edits already in this worktree, NOT this task (test_lexicality 8/8 on clean HEAD).
- wordnet_pipeline interface (`identity_cluster_for_form().ic_id`) preserved & verified.
