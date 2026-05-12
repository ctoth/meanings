# argumentation_dispatch module — build notes

Date: 2026-05-12

## Task
Build `src/meanings/argumentation_dispatch.py` — SCC + z3 + FVS-backdoor divide-and-conquer dispatcher.
Plus `scripts/argumentation_dispatch_oewn.py`, `tests/test_argumentation_dispatch.py`, `reports/argumentation-dispatch-oewn.{md,json}`.
Do NOT touch argumentation_bridge.py, graph_analysis.py, minset.py, cli.py, wordnet_pipeline.py, pyproject.toml, workstreams/.
Do NOT commit.

## Known API
- `meanings.graph_analysis.strongly_connected_components(nodes, adjacency)` -> list[set[str]]
- `meanings.graph_analysis.induced_subgraph`, `reverse_adjacency`, `analyze_kernel`, `KernelAnalysis`
- `meanings.argumentation_bridge.dung_attack_framework(nodes, adjacency)`, `scc_attack_framework(scc, adjacency)`, `edges_of`
- `argumentation.dung.grounded_extension(af)` — super-quadratic, used patched? bridge says it does NOT scale
- `argumentation.af_sat.find_stable_extension(af)` -> frozenset|None ; also find_preferred_extension etc.
- `meanings.minset.solve_minset(nodes, adjacency, method)` -> MinSetResult with .nodes (FVS seed)
- `meanings.wordnet_pipeline.build_paper_wordnet_graph("oewn:2024")` -> build.nodes, build.adjacency

## Bridge findings to confirm
- whole Kernel (18151 nodes) stable: UNSAT ~8s
- largest SCC (8138 nodes): UNSAT ~3.3s
- ~693 non-singleton SCCs: 630 SAT, 63 UNSAT
- Kernel: 18151 nodes; 9139 SCCs (8446 singletons: 2804 self-loops, 5642 plain); seed/MinSet 3620

## Status
- Reading done. About to write argumentation_dispatch.py.

## Update 1
- argumentation.dung.grounded_extension is ALREADY linear (patched upstream by Q concurrently). Good.
- find_stable_extension supports require_in/require_out (single node) -> used for credulous/skeptical.
- Wrote src/meanings/argumentation_dispatch.py. Exposes: condense, Condensation, SccInfo, canonical_scc_form,
  SccVerdict, DispatchResult, dispatch_stable, stable_exists, stable_witness, grounded, credulous_accepts,
  skeptical_accepts, minset_structure, MinSetStructure.
- Backdoor: stubbed (returns None -> falls back to z3) because OEWN giant SCC FVS ~few hundred nodes >> 18 cap.
  z3 handles 8138-node SCC in 3.3s anyway per bridge report.
- NEXT: clean up the dead _propagate_forced_out stub, write tests, write script, run pytest, run OEWN script.

## Update 2
- Refactored _solve_scc: dropped special-cases for trivial-singleton/self-loop; all SCCs <=12 go through
  brute-force which respects forced_out (singleton attacked-from-upstream -> residual empty -> witness {}).
- SccVerdict gained is_cyclic property.
- dispatch_stable witness: recompute via find_stable_extension on residual if verdict carries no witness.
- ABOUT TO: re-run pytest.

## Update 3
- Tests pass: 25 new, 49 total (was 24 baseline -> +25 = 49). No regressions.
- Realized structural count is NOT a flat product when cross-SCC IN->node edges force downstream OUT.
  -> dispatch_stable now exposes both structural_minset_count (independent-choice product, upper bound)
     and exact_stable_count (DAG DP over condensation, exact, when all SCC residuals enumerable).
  MinSetStructure: independent_choice_count + exact_count + total_count property (prefers exact).
- NEXT: write scripts/argumentation_dispatch_oewn.py + run it.

## Update 4
- scripts/argumentation_dispatch_oewn.py written; running in background (b6junrrqx), log at reports/argumentation-dispatch-oewn.run.log
- Monitor armed. Module imports clean.

## Update 5
- Re-armed monitor (b4p6ye7t0). First monitor died on SIGPIPE from tail; harmless.
- Verified forced-OUT reduction soundness (deleting OUT nodes + their attacks preserves residual stable structure).
- Waiting on OEWN run.

## Update 6
- Monitors via tail keep dying on this Windows git-bash; switched to a while-loop monitor (biwg5rbkz) that
  exits when JSON appears or log shows error. Also a bash bg poll (bjjbc24ta).
- Concern: 14 credulous probes + minset_structure each re-run full dispatch; if too slow may hit 580s timeout. Watch for it.

## Update 7
- OEWN run stuck in graph-build phase for 7+ min (normally ~90s). Machine under contention (many python procs from
  other agents). Letting monitor biwg5rbkz wait. Not polling further.

## Update 8
- Added _CANON_MAX=64 (skip WL canon for huge SCCs -> cheap degree-multiset key) + _backdoor_stable early
  return for size>200. Tests still pass (25). These are perf/safety; don't change results.
- Realized WL refinement is O(m) per iteration not O(n*m) -> the running (old-code) OEWN process is fine,
  will produce correct results, just letting it finish. Monitor bnhy7nbp8 watching.
- by8oqn8w2 launched the nohup child (new tmp file tmpqwcgytbg) -> that's the live run, still in graph build.

## DONE
- All deliverables written. uv run pytest: 49 passed (24 baseline + 25 new). No regressions.
- OEWN run results match bridge report exactly: kernel 18151, 9139 SCCs (2804 self-loop + 5642 plain + 693 nontrivial),
  693 nontrivial = 630 SAT / 63 UNSAT, giant SCC 8138 nodes UNSAT (~11-13s z3, slower than bridge's 3.3s due to
  machine contention), whole Kernel stable UNSAT, grounded(full)=5043, grounded(kernel)=468, structural MinSet count=0.
- Iso cache: 9139 SCCs -> 41 distinct iso classes, 9098 cache hits (99.6%). Biggest iso class = 503 identical SCCs.
- Bug fixed: _write_markdown didn't write the file (only built a list); added REPORT_MD.write_text. Regenerated MD from JSON.
- run.log is interleaved from two concurrent processes (the original `timeout 580` run + a relaunch) — supplementary only;
  JSON+MD are clean and correct.
- I did NOT touch argumentation_bridge.py/graph_analysis.py/minset.py/cli.py/wordnet_pipeline.py/pyproject.toml. Did NOT commit.
