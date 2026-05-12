# Verification: argumentation grounded-extension perf fixes

Verdict: **MERGE** (with one performance note Q should be aware of — see Check 4).

Subject: working-tree changes in `C:\Users\Q\code\argumentation` — `src/argumentation/dung.py`,
`src/argumentation/bipolar.py` modified; `tests/test_grounded_perf_equivalence.py` added (untracked).
Spec: `C:\Users\Q\code\argumentation\prompts\perf-fixes-grounded.md`. Self-report: `...\reports\perf-fixes-grounded-report.md`.
Nothing committed. `src/` not modified by the verifier; only `scratch/` scripts added.

## Check 1 — Scope: PASS
`git diff --stat`: only `src/argumentation/dung.py` (+58/-?) and `src/argumentation/bipolar.py` (+250-ish) modified.
No `pyproject.toml` / `uv.lock` change. New test file is untracked, separate.
- `dung.py`: added private `_targets_index(defeats)` (forward adjacency view); replaced `grounded_extension`'s
  body with the standard linear grounded labelling (seed in-degree-0 as IN, mark targets OUT, decrement
  `live_attackers`, BFS). `_attackers_index`, `attackers_of`, `characteristic_fn`, `defends`, `admissible`,
  `range_of`, `complete_extensions`, `*_preferred_extensions`, `stable_extensions`, `_all_subsets` untouched.
- `bipolar.py`: `bipolar_grounded_extension` now computes `derived_set_defeats(framework)` once and delegates to
  `dung.grounded_extension(ArgumentationFramework(arguments=..., defeats=<closure>))` (new top-level import of
  dung — no cycle, suite confirms). Added additive `*, defeat_closure=None, attackers_index=None` kwargs on
  `defends` and `characteristic_fn` only. New private helpers `_attackers_index`, `_closure_or_compute`,
  `_set_defeats`, `_conflict_free`, `_safe`, `_d_admissible`, `_s_admissible`, `_c_admissible`. Public
  `set_defeats`, `conflict_free`, `safe`, `d_admissible`, `s_admissible`, `c_admissible`,
  `bipolar_complete_extensions`, `stable_extensions`, `_maximal_sets` keep their signatures and delegate to the
  helpers over a (freshly-computed or precomputed) closure — semantically unchanged. `cayrol_derived_defeats`,
  `_defeat_closure`, `set_defeats` meaning, `support_closure`, the `*_admissible` meanings, and enumeration
  semantics unchanged. No public signature removed/changed.

## Check 2 — Existing suite: PASS
`uv run pytest -q` in `C:\Users\Q\code\argumentation` (working-tree change applied): **806 passed, 2 skipped** in ~84s.
Matches Codex's reported post-change count (803+2 before, +3 from the new equivalence module). No new failures.

## Check 3 — Independent equivalence battery: PASS
`scratch/verify_equiv.py` (own textbook fixpoint-of-characteristic-function reference, independent of Codex's test):
- 250 freshly-seeded random Dung AFs, sizes 1–50, densities {0.02,0.05,0.1,0.2,0.4}, self-loops injected, isolated
  nodes present; plus 7 classic hand cases (single node, self-loop, 2-cycle, 3-cycle, chain, Tweety/penguin, node
  attacked by a 2-cycle). `dung.grounded_extension(af) == ref_grounded(af)` for **all 257**.
- 120 freshly-seeded random bipolar AFs (varied attack + support edge densities). `bipolar.bipolar_grounded_extension(baf)
  == ref over derived_set_defeats(baf)` for **all 120**. Result: `ALL EQUAL`.
- Codex's `tests/test_grounded_perf_equivalence.py`: re-ran, **3 passed**.

## Check 4 — Scaling: PASS (formal bar) — but see note
Built the OEWN `paper-wordnet` (oewn:2024) digraph via `meanings.wordnet_pipeline.build_paper_wordnet_graph`,
imported `argumentation.dung` from the local `C:\Users\Q\code\argumentation\src` working tree via a
verification-only `sys.path.insert` (the meanings venv pins `formal-argumentation` to old commit `8d28624`; no
install/pyproject changed). `scratch/verify_scaling*.py`:
- Graph: 160,010 nodes / 677,823 edges. `dung_attack_framework` build: ~0.9s.
- `grounded_extension(af)`: **|grounded| = 5043** — matches the meanings bridge agent's reported ~5,043 IN nodes
  under the attack reading. Wall-clock: **~1.3–1.7s** across 6 runs (median ~1.5s).
- Synthetic scaling (six-node reinstatement-chain + 3-cycle groups): 50,004 nodes/41,670 edges → **0.13s**
  (matches Codex's ~0.14s); 100k → 0.32s; 200k/167k edges → 1.0s; 678k nodes/565k edges → 5.3s. Random
  160k-node/678k-edge graph → 2.4s. Roughly linear in V+E with a non-trivial Python constant
  (the `_attackers_index`/`_targets_index` rebuild every adjacency set into a `frozenset`).

The spec's binding acceptance bar — "`grounded_extension` on a 50k+-node sparse graph: sub-second" — is met handily
(0.13s at 50k). On the actual 160k/678k OEWN graph it is ~1.5s, i.e. **not "well under a second"** but the same
order of magnitude, vs. the pre-change implementation which was killed after >200s. Fully fit for the downstream
one-pass analysis. The residual constant factor is inherent to the module's existing `dict[str, frozenset[str]]`
index convention (`_attackers_index` already did this pre-change); shaving it would mean *not* reusing
`_attackers_index`, arguably a separate change. **Not a blocker, but Q should know the 160k case is ~1.5s, not
sub-second**, in case the "well under a second" target was firm.

## Why MERGE despite the 1.5s
- Correctness is bit-exact and exhaustively checked: 257 Dung + 120 BAF independent-reference instances, the full
  806-test suite, and the |grounded|=5043 cross-check against the bridge agent's figure.
- Scope is clean: two source files, additive kwargs only, no public-API break, no `pyproject.toml`/`uv.lock`,
  enumeration semantics untouched, no SCC dispatcher.
- The stated acceptance criterion (50k sub-second) passes; the goal ("make it scale" from non-terminating) is met.
- The only soft miss is constant-factor (~1.5s at 160k vs. an aspirational "well under a second"), traceable to a
  pre-existing module convention, not a regression or defect.

## Artifacts
- `C:\Users\Q\code\argumentation\scratch\verify_equiv.py` — independent equivalence battery (Dung + bipolar).
- `C:\Users\Q\code\argumentation\scratch\verify_scale_synth.py` — synthetic scaling sweep.
- `C:\Users\Q\code\meanings\scratch\verify_scaling.py`, `...\verify_scaling2.py` — OEWN-scale timing with local-src import.
- Spec: `C:\Users\Q\code\argumentation\prompts\perf-fixes-grounded.md`. Codex report: `C:\Users\Q\code\argumentation\reports\perf-fixes-grounded-report.md`.
