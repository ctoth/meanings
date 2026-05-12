# Research: Workstream 5 Candidate MinSet Extraction

**Date:** 2026-05-12

## Scope

This report answers the current Workstream 5 question: how should this repo move from a cycle-breaking seed heuristic toward serious candidate `MinSet` extraction for English dictionary graphs?

I inspected the existing local reports in `./reports`, especially:

- `reports/executable-workstreams.md`
- `reports/oewn-paper-wordnet-kernel-report.md`
- `reports/oewn-paper-wordnet-loop-ecology.md`
- `reports/oewn-kernel-model-comparison.md`
- `reports/core-mismatch-verdict.md`
- `reports/synthesis-minimal-core-to-expansion.md`
- `reports/swanson-perron-frobenius-findings.md`

I also searched current and historical directed feedback vertex set literature. I did not reread full PDFs from page images for this report; web sources used here are abstracts, official challenge pages, bibliographic pages, and already-existing local paper notes.

## Local State

The repo already has a real graph surface, not a toy:

- `paper-wordnet`: 160,010 lemma/POS nodes, 677,823 edges.
- Kernel: 12,853 nodes.
- Largest kernel SCC: 8,138 nodes.
- Loop ecology: 3,497 cyclic SCCs, including 1,240 two-cycles and 535 three-cycles.
- Current `exact-small-greedy` candidate seed: 2,370 nodes.
- Residual cyclic SCCs after that seed: 0.
- Vincent-Lamarre WordNet reference: MinSet 1,094.

So the current code is operationally useful: it finds a seed that acyclicizes the kernel and supports recursive layering. But it is not a verified minimum. The gap between `2,370` and the paper reference `1,094` is too large to treat as only resource-version noise.

The local paper notes matter here:

- Massé proves grounding sets are feedback vertex sets.
- Vincent-Lamarre treats `MinSet` as the minimum feedback vertex set problem, solves small dictionaries exactly, and approximates large dictionaries with CPLEX.
- Fomin 2008 is useful algorithmically but is undirected, so it is not a drop-in solver for dictionary `MinSet`.
- Picard cites Lin and Jou 2000 and Lapointe et al. 2012 as the directed-FVS line directly relevant to multiple candidate seeds.

## External Literature Snapshot

The exact object is Directed Feedback Vertex Set (DFVS): find a minimum vertex subset whose deletion leaves the directed graph acyclic. PACE 2022 used exactly this problem as its challenge target, with separate exact and heuristic tracks. The official challenge definition matches our `MinSet` semantics directly.

Key external signals:

- PACE 2022 exact track required optimal DFVS solutions within 30 minutes, and heuristic track ranked best valid feedback vertex sets within 10 minutes. This is the right engineering split for us too: exact where possible, heuristic but honestly labelled where necessary.
- The PACE 2022 report says the challenge focused on NP-hard DFVS and solver engineering: FPT, kernelization, exact algorithms, and heuristics.
- DAGer, a top exact PACE solver, used preprocessing/data reductions plus incremental MaxSAT. Its core idea is directly relevant: do not encode all cycles up front; add cycle constraints lazily when violated.
- Meiburg's PACE note says reduction rules plus ILP were enough to build a strong exact solver, reducing DFVS toward minimal cover and solving the remainder with SCIP.
- Lapointe et al. 2012 is especially on-axis for this repo because it was written by the dictionary-kernel circle and targets enumeration of cardinality-minimum feedback vertex sets in directed graphs. It uses Lin and Jou-style contraction/reduction operators and a branch-and-bound representation of all solutions.
- The 2025 Acta Informatica work on data reduction for DFVS confirms the current frontier is still reduction-first. It is not a universal practical solver for our graph, but it reinforces that graph reductions before exact solving are not optional polish.

## Verdict

The best path is not to keep tuning the current greedy seed. The best path is to make `MinSet` extraction a solver layer with three explicit modes:

- `heuristic`: fast deterministic cycle breaking for full-scale runs and diagnostics.
- `exact-cutting`: exact minimum by lazy cycle constraints on SCCs that fit the solver budget.
- `enumerating`: multiple optimal or near-optimal seeds where the SCC/reduced instance is small enough.

The local graph structure supports this because DFVS decomposes over SCCs. Most cyclic SCCs are tiny. The hard part is the one giant SCC of 8,138 nodes. Therefore, the system should solve thousands of small SCCs exactly, reduce the giant SCC aggressively, and only then use ILP/MaxSAT or a bounded heuristic fallback.

## Implementation Recommendation

Add `src/meanings/minset.py` as the solver boundary. Keep graph construction and kernel computation where they are; do not mix solver policy into `wordnet_pipeline.py`.

Minimum API:

```python
class MinSetResult:
    method: str
    nodes: set[str]
    exact: bool
    lower_bound: int | None
    residual_cyclic_scc_count: int
    scc_results: list[SccMinSetResult]
    runtime_seconds: float
```

Solver modes:

- `bounded-scc`: current method, retained as baseline.
- `exact-small`: brute force / branch search for tiny SCCs only.
- `cutting-ilp`: binary variable per vertex, objective `min sum x_v`, lazy cycle constraint `sum(x_v for v in cycle) >= 1`; iterate solve, find a directed cycle in the kept graph, add a constraint, repeat until acyclic or timeout.
- `hybrid`: exact-small for small SCCs, cutting-ILP or MaxSAT for reduced medium SCCs, deterministic greedy fallback for the giant SCC if budget expires.
- `enumerate-small`: for SCCs where exact optimum is known, enumerate multiple optimal choices or at least count/tally vertex participation.

Report fields must include:

- `seed_method`
- `seed_exact`
- `seed_lower_bound`
- `seed_upper_bound`
- `scc_exact_count`
- `scc_heuristic_count`
- `timeout_count`
- `residual_cyclic_scc_count`
- `solver_runtime_seconds`
- `candidate_seed_id`

## Why Lazy Cycle Constraints Fit This Repo

The naive ILP has one constraint per directed cycle, which can be exponential. But our existing algorithm already has the essential separation oracle: after a candidate seed is removed, run an acyclicity check and return a remaining cycle if one exists. That is exactly the lazy-constraint loop used by modern exact approaches:

1. Start with no or few cycle constraints.
2. Solve the current binary problem.
3. Remove selected vertices.
4. If graph is acyclic, the solution is certified against all discovered constraints and the separation oracle found no violation.
5. If a cycle remains, add the constraint that at least one vertex in that cycle must be selected.
6. Repeat until exact, timeout, or solver budget.

This is close in spirit to DAGer's incremental MaxSAT strategy: most instances do not need all cycle constraints materialized.

## What Not To Do

Do not call the current 2,370-node set a `MinSet`. It is a valid cycle-breaking candidate seed, not a proven minimum.

Do not implement only a spectral ranking as a replacement for DFVS. The Perron-Frobenius report already falsified the naive authority-side PageRank story on OEWN. Reverse-PageRank may become a useful heuristic ordering or weight signal, but it is not a set solver unless paired with a cycle-hitting objective.

Do not use Fomin 2008 as if it solved the directed case. It is still valuable because it explains exact/enumeration thinking and the non-uniqueness of minimal FVSs, but our dictionary graph is directed.

Do not make cross-language claims until the solver records exactness, resource policy, and preprocessing policy. Otherwise seed-size comparisons will conflate algorithm error with language/resource differences.

## Next Executable Slice

The next code slice should be:

1. Add `src/meanings/minset.py` with a path-limited SCC solver interface.
2. Move existing seed functions behind that interface without changing behavior.
3. Add `seed_exact`, `seed_lower_bound`, `seed_upper_bound`, and per-SCC method counts to JSON.
4. Add a lazy-cycle exact solver for SCCs under a conservative vertex cap.
5. Regenerate the paper-wordnet report and compare candidate seed size against the current `2,370`.

This gives an immediate correctness improvement without betting the whole project on solving the 8,138-node SCC optimally on the first pass.

## Research Leads To Add Or Retrieve

- Lin and Jou (2000), "On computing the minimum feedback vertex set of a directed graph by contraction operations." Directly relevant for reductions and contractible directed graphs.
- Lapointe et al. (2012), "Enumerating minimum feedback vertex sets in directed graphs." Directly relevant for multiple kernel seeds and authored by the dictionary-kernel circle.
- PACE 2022 solver descriptions, especially DAGer and reduction-rules-plus-ILP solvers.
- Recent DFVS reduction papers, including 2025 work on graphs without long induced cycles, as reduction-rule inspiration rather than an immediate dependency.

## Sources

- PACE 2022 DFVS definition and tracks: https://pacechallenge.org/2022/directed-fvs/ and https://pacechallenge.org/2022/tracks/
- PACE 2022 challenge report: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2022.26
- DAGer solver description: https://drops.dagstuhl.de/opus/volltexte/2022/17388/pdf/LIPIcs-IPEC-2022-32.pdf
- DAGer full preprint: https://arxiv.org/abs/2211.06109
- Meiburg, "Reduction Rules and ILP Are All You Need": https://arxiv.org/abs/2208.01119
- Lapointe et al. 2012 extended abstract: https://lapointemelodie.github.io/BGW2012.pdf
- 2025 DFVS data reduction paper: https://link.springer.com/article/10.1007/s00236-025-00490-2
