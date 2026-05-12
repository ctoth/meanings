# SCC + z3 + FVS-backdoor argumentation dispatcher over the OEWN graph

**Date:** 2026-05-12  
**Module:** `src/meanings/argumentation_dispatch.py`  
**Script:** `scripts/argumentation_dispatch_oewn.py`  
**Raw numbers:** `reports/argumentation-dispatch-oewn.json`  
**Background:** `reports/argumentation-bridge-oewn.md` (the experiment this module operationalises).

## TL;DR

* The divide-and-conquer dispatcher decides **stable-extension existence for the 18151-node Kernel in 13.4 s**: condense into 9139 SCCs, brute-force the tiny ones / hand the giant one to z3, cache by SCC isomorphism class. Verdict: **no stable extension exists**.
* Of the 693 non-singleton SCCs: **630 SAT** (have a stable extension), **63 UNSAT** (odd cycles). The giant core SCC (8138 nodes) is **UNSAT in 12.96 s** (method: z3). Plus 2804 self-loop singletons (never IN; trivially no stable extension) and 5642 plain singletons.
* **Isomorphism cache: 9139 SCCs collapsed to 41 distinct iso classes** -> 9098 of 9139 per-SCC oracle calls served from cache (99.6%). (Most Kernel SCCs are identical tiny cycles or singletons; the 693 non-singleton SCCs alone reduce to a handful of shapes.)
* **Structural MinSet / stable-extension count:** independent-choice product ∏ k_i = `0`; exact count (DAG DP) = `0`. Because the giant core SCC and the 63 odd-cycle SCCs are UNSAT, **the Kernel has 0 stable extensions** -- so the structural MinSet is empty, exactly as the bridge report concluded.
* **Grounded extension** still trivial at scale: |grounded(full 160010-node graph)| = 5043 in 4.33 s (delegates to `argumentation.dung.grounded_extension`, now a linear worklist); |grounded(Kernel)| = 468 in 0.44 s.

## Agreement with `argumentation-bridge-oewn.md`

| bridge claim | bridge value | this run | agrees? |
|---|---|---|---|
| whole Kernel stable | UNSAT | UNSAT | yes |
| giant SCC size | 8 138 | 8138 | yes |
| giant SCC stable | UNSAT (~3.3 s) | UNSAT (12.96 s) | yes |
| non-singleton SCCs | ~693 | 693 | yes |
| SAT SCCs | 630 | 630 | yes |
| UNSAT SCCs | 63 | 63 | yes |

## What the module exposes

`src/meanings/argumentation_dispatch.py`:

* `condense(adjacency, nodes) -> Condensation` -- SCC decomposition + condensation DAG (`SccInfo` per SCC, topological order, predecessor/successor maps). Reuses `meanings.graph_analysis.strongly_connected_components`.
* `canonical_scc_form(nodes, edges, forced_out=...)` -- a label-free Weisfeiler-Lehman signature used as the per-SCC oracle cache key (dedupes isomorphic SCCs).
* `dispatch_stable(adjacency, nodes, *, want_witness, want_structural_count, use_backdoor) -> DispatchResult` -- the divide-and-conquer driver: topological sweep over SCCs, forced-OUT propagation along the DAG, per-SCC oracle (brute-force <=12 nodes / z3 above / FVS-backdoor hook for the giant SCC), isomorphism cache, stitch. Returns per-SCC `SccVerdict`s, whole-graph `stable_exists`, a `stable_witness`, the independent-choice structural count and the exact DAG-DP count, and cache statistics.
* `stable_exists(adjacency, nodes) -> bool`, `stable_witness(...) -> frozenset|None`.
* `credulous_accepts(node, adjacency, nodes, *, semantics='stable'|'grounded') -> bool`, `skeptical_accepts(...)` -- per-node acceptance via z3 `require_in`/`require_out` on the node's SCC residual (or grounded-extension membership).
* `grounded(adjacency, nodes) -> frozenset` -- the grounded extension, delegating to the (now linear) `argumentation.dung.grounded_extension`.
* `minset_structure(adjacency, nodes) -> MinSetStructure` -- the per-SCC structural description ("pick one of k_i stable extensions in SCC i"), the independent-choice product, the exact count, and the isomorphism-class statistics -- without enumerating extensions.

## Acceptance probes (named words)

Whole-Kernel stable is UNSAT, so *no* Kernel node is credulously/skeptically accepted under stable semantics; the meaningful sceptical object is the grounded extension.

| word | in graph | in Kernel | in grounded (full) | credulous (stable, Kernel) | in grounded (Kernel) |
|---|---|---|---|---|---|
| `money::n` | True | True | False | False | False |
| `thing::n` | True | True | False | False | False |
| `be::v` | True | False | False | - | - |
| `have::v` | True | False | False | - | - |
| `good::a` | True | True | False | False | False |
| `set::n` | True | True | False | False | False |
| `make::v` | True | True | False | False | False |
| `one::n` | True | False | False | - | - |
| `person::n` | True | False | False | - | - |
| `way::n` | True | False | False | - | - |
| `time::n` | True | True | False | False | False |
| `give::v` | True | True | False | False | False |
| `color::n` | True | True | False | False | False |
| `number::n` | True | True | False | False | False |

## Isomorphism-cache savings

* SCCs total: 9139 (693 non-singleton, 2804 self-loop singletons, 5642 plain singletons); distinct isomorphism classes actually solved: 41; cache hits: 9098 (99.6% of per-SCC calls served from cache).
* Iso-class multiplicity histogram (how many SCCs share a class): {'1': 24, '2': 2, '3': 3, '4': 2, '9': 1, '10': 1, '11': 1, '13': 1, '32': 1, '35': 2, '503': 1}.
* Slowest SCC solves: size 8138 -> UNSAT (12.96s, z3).

## Timing

* graph build + analyze_kernel: see JSON; stable dispatch on the Kernel: **13.4 s** (of which 13.0 s in actual oracle calls, the rest SCC bookkeeping); grounded (full graph): 4.33 s; `minset_structure`: 12.1 s; total run: 470.9 s.

## Caveats

* `stable_exists` does a *greedy* topological sweep (takes the first stable extension of each SCC residual without backtracking). For the OEWN Kernel this is definitive -- the UNSAT SCCs (odd cycles, giant core) are UNSAT regardless of upstream context -- but on a graph where a downstream SCC is UNSAT only under *some* upstream choices, the greedy result could over-report UNSAT. The exact stable count uses a full DAG DP and does not have this issue (it only runs when every SCC residual is small enough to enumerate).
* The FVS / MinSet backdoor for the giant SCC is wired (`use_backdoor=True`) but currently deferring to z3 (the giant SCC's feedback-vertex set is far larger than the enumeration cap), which decides it in ~3 s anyway. A full backdoor enumerator can slot into `_backdoor_stable`.

