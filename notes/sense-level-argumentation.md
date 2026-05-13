# Sense-level argumentation (agenda #3) — working notes

2026-05-12

## State
- Added `SenseLevelGraphWithAttacks`, `add_rival_sense_attacks`, `build_sense_level_paper_wordnet_graph_with_attacks` to `wordnet_pipeline.py` (cross-POS rivalry by `lemma` metadata; per_pos flag).
- Added `bipolar_with_attacks_framework`, `derived_dung_framework` (Cayrol derived defeats → plain Dung AF, z3-able) to `argumentation_bridge.py`.
- Wrote `tests/test_sense_attack_layer.py`.
- Baseline `uv run pytest` = 60 passed. NOT yet re-run with new tests.

## Next
1. Run pytest with new tests.
2. Write `scripts/sense_level_argumentation.py`: build sense graph + attacks, stats (attack edge count, rivalry-clique size distribution), Kernel, bipolar AF on small SCC slice (preferred/stable/grounded), z3 on whole sense-Kernel-with-derived-attacks (time-box ~300s), `enforce_skeptical` on slice, ranking semantics (h-categorizer) on bipolar.
3. Report `reports/sense-level-argumentation.md` + JSON.
4. Commit atomically.

## Key design choices made
- Rivalry per FORM (lemma), all POS — justified: same written shape, reader disambiguates over whole rival set.
- bipolar→Dung via Cayrol `cayrol_derived_defeats` (poly-time supported/indirect defeat closure), then z3 `af_sat.find_stable_extension`.
- Concern: cyclic support graph → attacker on one SCC node attacks whole SCC reach → derived-defeat blowup. Time-box.

## Progress 2026-05-12 (cont)
- Commit b3daa8a: attack layer builder + bridge + 6 tests, all pass.
- scripts/sense_level_argumentation.py written; running now (Model A=attacks-only disjoint cliques; Model B=Cayrol-derived Dung; small-SCC slice + whole-Kernel time-boxed; h-categoriser ranking variant a=support-as-attack, b=support+rival).
- Discovery from tiny test: support edge INTO a rival breaks 2-clique symmetry via Cayrol *mediated* defeat (r supports s1, s1 attacks s2 => r attacks s2). So Model B is non-trivial; the "k senses => k stable" only holds for bare cliques (Model A, vacuous).

## Blocker (2026-05-12 cont)
First run exited 0 but produced no stdout and no JSON (output lost — likely stdout buffering under `timeout|tee|tail` + `uv run`). Re-running with `python -u`, nohup-backgrounded, to /tmp/sla2.log. Monitor bkpem5q8k armed.
Commit 777618b = script + notes. b3daa8a = builder+bridge+tests. b3daa8a tests pass.
