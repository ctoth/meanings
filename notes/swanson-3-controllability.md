# Swanson-3: controllability / driver nodes vs FVS grounding set

Date: 2026-05-12

## State
- Read brief reports/research-swanson-3-controllability-driver-nodes.md, paper notes (Massé, Vincent-Lamarre, Fomin notes), reports/graph-object-definitions.md, src/meanings/{graph_analysis,wordnet_pipeline,cli}.py.
- Repo builds OEWN graphs via `wn` package; data cached at C:\Users\Q\.wn_data\wn.db (oewn). `uv run` works (wn installs into uv env).
- paper-wordnet graph: 160010 nodes, 677823 edges, kernel 12853, seed (exact-small-greedy FVS heuristic) 2370.
- synset graph: 120630 nodes, 223324 edges, kernel 10430, seed 1376.

## Plan
1. Web research: Liu-Slotine-Barabasi 2011 + critiques (Cowan/Muller, target controllability Gao 2014, control profiles Ruths 2014). Citation disjointness both ways.
2. Compute max-matching driver nodes on the paper-wordnet definition digraph (whole graph, same one kernel/FVS-seed computed on). Driver set = N - |max matching| (Hopcroft-Karp on bipartite split). Compare to FVS seed: sizes, overlap, disagreements.
3. Write reports/swanson-controllability-findings.md.

## Findings so far
(fill in)
