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

## Blocker
None yet.
