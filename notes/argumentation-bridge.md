# argumentation bridge experiment

2026-05-12 (subagent)

## State
- `formal-argumentation @ git+https://github.com/ctoth/argumentation@8d28624` added to pyproject. `import argumentation` works under `uv run`. Also added `z3-solver>=4.12` (direct dep, experiment-only) and `pytest` (dev) -- needed because the project venv had no pytest; `uv run pytest` was using an external 3.13-32 pytest that can't see `.venv` site-packages, so `argumentation`-importing tests failed there. Adding pytest as dev dep makes `uv run pytest` use the venv pytest. 19 tests pass (15 pre-existing + 4 new).
- Wrote `src/meanings/argumentation_bridge.py`: `dung_attack_framework` (u->v = attack), `bipolar_support_framework` (u->v = support, empty defeats), `kernel_attack_framework`, `scc_attack_framework`, `edges_of`. Reuses `graph_analysis.induced_subgraph`.
- Wrote `tests/test_argumentation_bridge.py`: chain, 2-cycle, self-loop, support-edges. Pass.
- DO NOT TOUCH: minset.py, graph_analysis.py, cli.py, workstreams/.

## Key library facts
- `argumentation.dung.grounded_extension(af) -> frozenset` (least fixpoint over `defeats`).
- `argumentation.bipolar.bipolar_grounded_extension(baf)` -- with empty defeats this returns ALL arguments in one step (nothing attacks anything). So support-reading grounded is trivial; finding, not failure.
- `argumentation.af_sat.find_stable_extension(framework, ...) -> frozenset|None` (z3-backed).
- `argumentation.dung.stable_extensions(af) -> list[frozenset]` (brute force, no good at scale).

## TODO
- scripts/argumentation_bridge_oewn.py: build paper-wordnet oewn:2024 graph, analyze_kernel, build both AFs, time grounded ext of each, overlap vs {Rest,Kernel,Core,Satellites,seed}, stable probe via find_stable_extension on Kernel SCCs, write reports/argumentation-bridge-oewn.json
- reports/argumentation-bridge-oewn.md

## 2026-05-12 cont
- FINDING: `argumentation.dung.grounded_extension` does NOT scale to 160k nodes. `defends()` does `any((d,attacker) in defeats for d in s)` for every arg/attacker -- super-quadratic in extension size. Ran ~200s CPU on full OEWN graph still in first/second iteration; killed it. So full-graph grounded via the library is INFEASIBLE.
- Mitigation: script now computes grounded extension itself via standard linear worklist labelling (`grounded_extension_fast` in the script, NOT a reusable module -- experiment-only), with an assertion it matches the library on tiny graphs. Library `grounded_extension` is still run on the *Kernel subgraph* under a 120s cap as a scaling data point. Bipolar support grounded kept (empty defeats => 2 cheap iterations => all args).
- OEWN paper-wordnet build: nodes=160010, edges=677823, build ~83s. analyze_kernel: kernel=18151, core=510, sats=17641, seed=3620, sccs=9139, residual_cyclic_sccs=1, ~2s.
- Still need to: finish editing script (add library-grounded-on-Kernel block with cap), run it, write reports/argumentation-bridge-oewn.md.

## 2026-05-12 run results (partial)
- import argumentation: OK. z3: OK.
- OEWN paper-wordnet: 160010 nodes, 677823 edges (build ~92s). analyze_kernel: kernel=18151 core=510 sats=17641 seed=3620 sccs=9139 residual_cyclic_sccs=1 (~2s).
- Dung attack AF build: 0.82s. Grounded extension (attack reading, my fast linear labelling): |GE|=5043, 0.70s.
- Still running: bipolar support grounded, library-grounded-on-Kernel (capped 120s), stable z3 probe on SCCs + whole Kernel.

## 2026-05-12 FINAL RESULTS
- 24 tests pass. Script ran clean in 188s. JSON written.
- grounded(attack, full 160010 graph): |GE|=5043 (3.15% of nodes), fast labelling 0.81s. argumentation lib grounded_extension does NOT scale on full graph (super-quadratic in extension size); DID finish on Kernel subgraph (468 IN, 2.5s).
- grounded(support, bipolar): = all 160010 nodes (analytic; empty-defeat BAF). Lib's bipolar_grounded_extension doesn't scale (recomputes Cayrol closure per arg).
- Alignment vs partition: GE(attack) is NOT Rest, NOT Kernel. 4575/5043 of GE are in Rest (alternating IN-layers of the acyclic shell); 468 in Kernel. 137284 of Rest's 141859 nodes are OUT (attacked). GE ∪ Rest = 142327 = all nodes minus the 17683 Kernel-UNDEC nodes. So leaf-stripping (acyclic shell) and grounded labelling (IN/OUT/UNDEC) are different decompositions. GE∩seed = 2 (basically disjoint).
- Stable probe (z3): whole Kernel (18151n, 73654e) -> UNSAT, 8s. Largest SCC (8138n) -> UNSAT, 3.3s. Of ~693 non-singleton Kernel SCCs: 630 SAT, 63 UNSAT (odd cycles). 8446 singleton "SCCs" trivial. So no stable extension on the Kernel => seed/MinSet does NOT correspond to a stable-extension outsider set (none exists).
- Files: src/meanings/argumentation_bridge.py, scripts/argumentation_bridge_oewn.py, tests/test_argumentation_bridge.py, reports/argumentation-bridge-oewn.json, reports/argumentation-bridge-oewn.run.log, notes/argumentation-bridge.md. Deps: formal-argumentation @ git+...@8d28624 (pinned to a commit), z3-solver, pytest(dev). TODO: write reports/argumentation-bridge-oewn.md, remove run.log? keep it. Don't commit.
- Trimmed scc_probe to non-trivial SCCs + counts (JSON was 1.3MB from 8446 singleton entries). Re-running script.
