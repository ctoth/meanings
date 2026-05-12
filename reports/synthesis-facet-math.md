# Synthesis Facet: Mathematics and Complexity

**Date:** 2026-05-12

This facet covers the mathematical spine of the project: Perron-Frobenius valuation, feedback vertex sets / MinSets, and the complexity of running argumentation semantics on the OEWN definition graph.

## Executive Claim

There are two different mathematical answers to "what fixes meaning in a circular definition system."

The spectral answer is a valuation: when a nonnegative relational matrix is irreducible, Perron-Frobenius gives a unique positive dominant eigenvector, a self-consistent weighting internal to the system. This is the same matrix object rediscovered in Sraffa-style production economics, Markov stationary distributions, PageRank and its bibliometric/sociological ancestors, eigenvector centrality, and adjacent spectral NLP methods. On the OEWN definition graph, however, the useful orientation is reverse-PageRank, and the empirical result is deflationary: reverse-PageRank mostly collapses to out-degree.

The combinatorial answer is a basis: a feedback vertex set (FVS) is a set of nodes that hits every directed cycle, so after those words are grounded externally, the rest of the dictionary unfolds acyclically. That is the Massé / Picard / Vincent-Lamarre MinSet object. In argumentation terms, it is a minimal enforcement/backdoor set that makes the cyclic verdict determinate.

Those are not the same object. Spectral valuation ranks; FVS grounding cuts cycles. On OEWN they agree at the top because the same high-out-degree genus terms dominate both, but the agreement is mostly degree-driven rather than a deep spectral law. See `reports/swanson-synthesis.md`, `reports/swanson-perron-frobenius-findings.md`, and `reports/spectral-valuation-oewn.md`.

## Perron-Frobenius Valuation

The theorem-level fact is narrow and powerful: for an irreducible nonnegative square matrix, Perron-Frobenius gives a unique positive dominant eigenvector, up to scale. For a stochastic matrix, the same object is the stationary distribution. For a reducible graph, there is no single canonical positive Perron vector without either restricting to irreducible blocks or adding a damping / teleportation perturbation.

That algebra is the rediscovered object across fields:

- In Sraffa's production system, as reconstructed by Newman/Pasinetti-style eigenvector readings, the standard commodity is the Perron eigenvector of the irreducible "basics" input-output block. The basics/non-basics split is an SCC/Frobenius-normal-form idea in economic clothing.
- In Markov chains, the stationary distribution is the left Perron vector of a stochastic transition matrix.
- In web search and bibliometrics, PageRank is the stationary distribution of a damped hyperlink chain; Hubbell, Pinski-Narin, Bonacich, Katz, and HITS are earlier or adjacent prestige/eigenvector centrality constructions.
- In LSA and spectral NLP, the leading singular vectors of a term-context matrix are adjacent rather than identical: the singular vectors are eigenvectors of the nonnegative co-occurrence Gram matrices when those matrices meet the relevant conditions.

The honest synthesis is therefore "same matrix algebra under an irreducibility/normalization problem," not "same idea in every field." What flows is different: commodities/value in economics, probability in Markov chains, prestige/authority in PageRank and bibliometrics, co-occurrence mass in LSA, and definitional productivity in a dictionary graph. `reports/swanson-perron-frobenius-findings.md` makes this caveat explicitly.

## OEWN: The Wrong Eigenvector and the Degree Collapse

OEWN uses the edge convention `u -> v` meaning "word `u` occurs in the definition of word `v`." That makes orientation decisive.

Forward PageRank, in this convention, is an authority score on the `defining -> defined` graph. Empirically it ranks definitional sinks and technical/proper-noun leaves: `magnificat`, `palaquium_gutta`, `coelogyne`, `niobe`, `laocoon`, and similar items. The major FVS seed hubs are near the bottom or middle of this ranking. This is an empirical observation from `reports/swanson-perron-frobenius-findings.md` and `reports/spectral-valuation-oewn.md`, not a theorem.

Reverse PageRank is the meaningful spectral object for lexical grounding: it runs PageRank on the transpose, so score flows from defined words back to their definers. Its top words are abstract productive definers: `act`, `degree`, `time`, `event`, `part`, `place`, `can`, `quality`, `quantity`, `extent`, `point`, `relation`, and similar genus vocabulary. The watch-words land where the theory predicts: `large` rank 27/160,010, `body` 29, `small` 66, `water` 132, `plant` 151, `white` 472 in the spectral report.

But the quantitative result is deflationary. Over the Kernel used in `reports/spectral-valuation-oewn.md`, reverse-PageRank has only `rho = 0.316` with the FVS heuristic degree key `internal_out + internal_in`. It correlates much more strongly with out-degree: `rho = 0.995` on the full graph and `rho = 0.746` on the Kernel. The degree-preserving edge-swap null still recovers a large fraction of the real reverse ranking (`rho = 0.521`), and total/out-degree nulls explain much of the signal (`rho` about 0.68 in the reported comparison).

So the observed OEWN conclusion is:

- Forward PageRank is the wrong eigenvector for grounding vocabulary.
- Reverse PageRank qualitatively surfaces the right genus words.
- Reverse PageRank is mostly laundered out-degree on this graph.
- The spectral object and the FVS seed agree at the very top and fan apart in the bulk.

One bookkeeping caveat matters. `reports/spectral-valuation-oewn.md` reports the pre-self-loop-fix Kernel counts: 12,853 Kernel nodes, 288 Core nodes, 12,565 Satellites, seed 2,370. `reports/self-loop-fix-impact.md` says the textbook self-loop policy puts all self-loop nodes in the Kernel, increasing the post-fix exact-small-greedy Kernel to 18,151, Core to 510, Satellites to 17,641, and seed to 5,044. The spectral null-model numbers cited here are the spectral report's run; the self-loop report changes the current graph decomposition counts.

## FVS, MinSets, and Enforcement

The theorem-level dictionary claim is Massé's: in a definition digraph, a grounding set that makes every definition recursively unfold is exactly a feedback vertex set. Removing an FVS leaves a DAG; then every remaining word has a finite derivation from the grounded words. A minimum FVS is a MinSet.

The repo implements this in `src/meanings/graph_analysis.py` and `src/meanings/minset.py`:

- `compute_kernel` strips nodes with no live outgoing edge; what remains can reach a cycle.
- `strongly_connected_components` and `source_sccs` give the Kernel/Core/Satellite anatomy.
- `solve_minset` offers bounded and exact-small-greedy cycle-hitting heuristics.
- `choose_feedback_vertex` is degree-based inside an SCC: it maximizes `internal_out + internal_in`, with tie-breakers.

The argumentation bridge gives a second theorem-level reading. An FVS is a minimal enforcement set for skeptical determinacy: fix those cyclic nodes externally, and the residual acyclic argumentation/definition structure has a unique recursively determined verdict. This is the same mathematical role as a backdoor. Dvorak-Pichler-Woltran-style backdoor results say that if deleting `k` arguments puts an argumentation framework into a tractable class such as acyclic frameworks, then reasoning for otherwise hard semantics becomes fixed-parameter tractable in `k`. An FVS is exactly such a deletion set for cycles.

This is the important bridge to argumentation complexity: MinSets are not just "small vocabularies." They are FPT backdoors into the hard semantics of the cyclic framework.

## Running Argumentation Semantics at 160k Nodes

The theorem-level complexity story:

- Grounded semantics for Dung AFs is polynomial-time computable by a least-fixed-point / labelling algorithm.
- Stable-extension existence is NP-complete in general.
- Skeptical reasoning under preferred semantics is at the second level of the polynomial hierarchy, commonly stated as Pi_2^P-complete.
- Acyclic AFs are tractable, and SCC decomposition plus small FVS backdoors can make hard cases practical on sparse, mostly acyclic graphs.

The OEWN empirical story is better than the worst-case bounds suggest.

`reports/argumentation-bridge-oewn.md` built the full `paper-wordnet` graph as an attack-reading Dung AF with 160,010 arguments and 677,823 defeats. A linear grounded labelling computed the full grounded extension in about 0.8s in that experiment, while the old library implementation did not finish. `reports/verify-argumentation-perf-fixes.md` then verified the patched sibling `argumentation.dung.grounded_extension`: on the real OEWN graph it returned the same 5,043-node grounded extension in about 1.3-1.7s, median about 1.5s.

I also ran the requested local cross-check for this facet by actually importing `argumentation.dung.grounded_extension` through `uv run` and timing a synthetic sparse AF with 100,002 arguments and 83,335 defeats. It returned a 33,334-node grounded extension in 0.233443s. I used synthetic rather than rebuilding real OEWN because the bridge report records the real OEWN build itself as roughly 83-93s, and the verifier report already contains the real OEWN timing against the patched library.

For hard semantics, the same report found the practical route: do not run monolithic brute force. Decompose by SCC, hand cyclic SCCs to z3, and use FVS as a backdoor when enumeration is needed. The post-self-loop Kernel has 18,151 nodes and 9,139 SCCs, with one giant 8,138-node SCC plus many tiny SCCs and self-loop singletons. z3 decided the whole Kernel attack AF as UNSAT in 8.1s and the largest SCC as UNSAT in 3.3s. Among the non-singleton Kernel SCCs probed, 630 were SAT and 63 were UNSAT. Because the Kernel contains UNSAT SCCs, the Kernel AF has no stable extension. The prompt's "~7s" summary and the report's 8.1s measurement are the same order-of-magnitude empirical claim.

The conclusion is not that NP / Pi_2^P hardness disappears. The conclusion is that this graph has exploitable structure: most nodes are outside the cyclic core, the condensation is SCC-decomposable, most SCCs are tiny, and the only large block is still z3-decidable for existence. For preferred-style enumeration or skeptical queries, the mathematically defensible path is SCC condensation plus per-SCC solving plus FVS-backdoor enumeration, not monolithic subset search.

## Theorems vs Observations

Theorem-level claims:

- Perron-Frobenius gives a unique positive dominant eigenvector for irreducible nonnegative matrices.
- Markov stationary distributions are Perron vectors of stochastic matrices under the usual irreducibility/aperiodicity conditions.
- A feedback vertex set deletes all directed cycles; after deleting it, the residual graph is acyclic.
- In the dictionary-graph model, grounding sets are FVSs, and minimum grounding sets are minimum FVSs.
- Deleting an FVS is an acyclicity backdoor for argumentation semantics; hard reasoning can be parameterized by that backdoor size.
- Grounded semantics is polynomial; stable existence and preferred skeptical reasoning are hard in the standard worst-case senses.

Empirical OEWN observations:

- Forward PageRank ranks definitional sinks and does not recover grounding vocabulary.
- Reverse PageRank surfaces the expected genus vocabulary at the top.
- Reverse PageRank adds little beyond out-degree on this graph.
- The spectral report's Kernel counts predate the self-loop fix; current textbook FVS accounting increases the Kernel and seed sizes.
- The patched `argumentation.dung.grounded_extension` scales to OEWN-sized sparse graphs, with real-OEWN timing around 1.5s and synthetic 100k timing around 0.23s.
- The Kernel attack AF is UNSAT for stable semantics, decided in seconds by z3 with SCC decomposition.

## Psycholinguistic Caveat

The psycholinguistic regressions in `reports/swanson-synthesis.md` are a useful negative result, not a license for metaphysics. Reverse-PageRank adds only small incremental explanatory power over `log(out-degree)`: reported partial increases are about +0.0093 for frequency, +0.0023 for age of acquisition, and +0.0307 for concreteness, with the concreteness result described as a suppression artifact partly proxying in-degree. The FVS seed adds even less: about +0.006, +0.003, and +0.0001 respectively.

That does not prove "meaning is purely relational" or "the graph contains all psycholinguistic content." It says that, in this OEWN artifact, graph structure screens off much of the variance in the available norms. The causal direction is unresolved: lexicographers write definitions for human readers, so frequent, early-acquired, concrete words may become high-out-degree definers because people already know them. The regression cannot distinguish "relations explain the norms" from "the norms shaped the relations."

The mathematically honest claim is therefore modest: the OEWN definition graph contains strong structural signals, but the spectral and psycholinguistic overlays mostly confirm how degree-dominated the current surface is. The robust core remains the FVS/Kernel machinery: it answers a precise well-foundedness question, and it gives the backdoor parameter that makes harder argumentation semantics tractable on this graph.
