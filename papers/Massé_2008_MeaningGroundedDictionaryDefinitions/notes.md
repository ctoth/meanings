---
title: "How Is Meaning Grounded in Dictionary Definitions?"
authors: "A. Blondin Masse; G. Chicoisne; Y. Gargouri; S. Harnad; O. Picard; O. Marcotte"
year: 2008
venue: "TextGraphs-3 Workshop"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T00:45:38Z"
---
# How Is Meaning Grounded in Dictionary Definitions?

## One-Sentence Summary
This paper gives a graph-theoretic formalization of the symbol-grounding problem for dictionaries, proves that grounding sets are exactly feedback vertex sets, introduces the `grounding kernel` as the recursively irreducible definitional subgraph, and sketches how these tools could be applied to real learner dictionaries such as LDOCE. *(p.1-9)*

## Problem Addressed
The paper asks how many words, and which words, must be learned by means other than dictionary definitions so that all the remaining words in a dictionary can be learned by recursive definition alone. *(p.1)*

## Key Contributions
- Frames dictionary lookup as an infinite regress unless some words are learned by means other than definitions. *(p.1-2)*
- Formalizes dictionaries as directed graphs whose vertices are words and whose arcs run from defining words to defined words. *(p.2-3)*
- Defines `reachable` and `groundable` sets and identifies the minimum grounding-set problem with the minimum feedback vertex set problem. *(p.3-4)*
- Shows that every minimum grounding set is the union of minimum grounding sets of the strongly connected components, reducing the problem to SCCs. *(p.4-5)*
- Defines the `grounding kernel`, the set of words remaining after recursively removing words that are not used to define any others outside loops. *(p.5-6)*
- Applies the idea conceptually to LDOCE and argues that a defining vocabulary can still contain cycles, so a much smaller grounding kernel likely exists inside it. *(p.6-7)*

## Study Design (empirical papers)
- **Type:** Mathematical/conceptual graph-theoretic formalization with toy examples and a lexicographic application sketch. *(p.2-7)*
- **Population:** Abstract dictionary graphs plus the Longman Dictionary of Contemporary English defining vocabulary as motivating real-world example. *(p.6-7)*
- **Intervention(s):** Formal definitions, lemmas, theorem, SCC decomposition, kernel-stripping algorithm. *(p.2-6)*
- **Comparator(s):** None experimental; contrasts graph-theoretic reduction against naive dictionary lookup and against broader computationalist views. *(p.1, p.5-7)*
- **Primary endpoint(s):** Existence/size characterization of grounding sets and grounding kernels. *(p.3-6)*
- **Secondary endpoint(s):** Feasibility of extracting a real dictionary grounding kernel and implications for cognitive grounding. *(p.6-8)*
- **Follow-up:** N/A. *(p.1-9)*

## Methodology
The authors first define a dictionary as a set of `(word, definition)` pairs and its associated digraph `G=(V,E)` where an arc `(u,v)` means word `u` occurs in the definition of word `v`. They then define a recursive reachability operator `R'(U)` for words learnable from a seed `U` by repeated use of definitions whose undefined predecessors are already in `U`. A set `U` is a grounding set if `R^*(U)=V`. The minimum grounding-set problem is then related to the minimum feedback vertex set problem: a seed grounds the whole graph iff it intersects every directed cycle. The paper further decomposes the problem over strongly connected components and defines the `grounding kernel` by recursively deleting vertices with no outgoing non-loop arcs. *(p.2-6)*

## Key Equations / Statistical Models

$$
R'(U) = U \cup \{ v \in V \mid N^-(v) \subseteq U \}
$$
Where: `R'(U)` is the one-step reachable set from seed `U` in dictionary graph `G=(V,E)`; `N^-(v)` is the set of predecessors of `v`. Recursive closure yields the words learnable by iterated dictionary lookup. *(p.3)*

$$
U \text{ is a grounding set of } G \iff R^*(U)=V
$$
Where: `R^*(U)` is the fixed point of repeated application of `R'`. *(p.3)*

$$
U \text{ is a grounding set of } G \iff U \cap C \neq \varnothing \text{ for every directed cycle } C \subseteq G
$$
Where: grounding sets are equivalent to feedback vertex sets. This is the core theorem of the paper. *(p.4)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Toy dictionary size | n | count | 9 | — | 3-5 | Example dictionary with words such as `apple`, `banana`, `bad`, `not`, `or`, `thing`, `color`, `red`, `fruit`. |
| Example minimum grounding number | γ(G) | count | 5 | — | 5 | For the toy example shown in Figure 3. |
| LDOCE defining vocabulary size | — | count | 2,000 | — | 7 | Official controlled vocabulary in LDOCE. |
| Example grounding-kernel levels in toy graph | — | count | 3 | — | 6 | Level 1 removed: `color`, `eatable`, `level`; level 2: `fruit`, `red`, `yellow`; level 3: `apple`, `banana`, `tomato`. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| Example minimum grounding number | count | 5 | — | — | Toy graph in Figure 3 | 5 |
| Defining vocabulary size | count | 2,000 | — | — | LDOCE defining vocabulary | 7 |

## Methods & Implementation Details
- Relations are treated as transitive closures and SCC partitions are used to decompose cyclic structure. *(p.2-5)*
- The minimum grounding set problem is reduced to the minimum feedback vertex set problem, which is NP-complete. *(p.4-5)*
- SCC decomposition is computationally manageable because Tarjan's algorithm runs in linear time. *(p.5)*
- The grounding kernel is computed by recursively deleting vertices with no outgoing non-loop arcs until no further deletion is possible. *(p.5-6)*
- The authors distinguish formal graph-theoretic grounding conditions from actual cognitive grounding; graph conditions alone do not explain how a person comes to know meanings. *(p.6)*
- LDOCE is proposed as a promising applied target because it already uses a controlled 2000-word defining vocabulary, making kernel extraction plausible. *(p.6-7)*

## Figures of Interest
- **Table 1 (p.3):** Toy dictionary and definitions.
- **Fig. 1 (p.3):** Graph representation of the toy dictionary.
- **Fig. 2 (p.4):** Example reachable set from a chosen seed.
- **Fig. 3 (p.5):** Strongly connected components and one minimum grounding set for the toy graph.

## Results Summary
The main technical result is that grounding sets in dictionary graphs are feedback vertex sets: to make the graph definitionally learnable from a seed, the seed must hit every directed cycle. This immediately implies NP-hardness for minimum grounding sets but also yields a practical decomposition by SCCs. The grounding-kernel construction provides a second, non-minimal but easier-to-compute object: the subset of words that remain after all recursively removable leaves are stripped away. The paper then argues that a real dictionary's defining vocabulary, such as LDOCE's 2000 words, still contains cycles and should itself contain a smaller grounding kernel. *(p.4-7)*

## Limitations
- The applied real-dictionary case is mostly programmatic; the paper does not yet present the full extracted kernel for a large natural-language dictionary. *(p.6-8)*
- Definitions are treated as if definitional relations were already disambiguated, but the authors note that real dictionaries face severe word-sense disambiguation problems. *(p.7-8)*
- The graph formalism addresses recursive definability, not genuine grounding in experience. *(p.6)*

## Arguments Against Prior Work
- Purely formal symbol manipulation is insufficient for meaning because a dictionary graph can only reach meanings if some seed words are known independently. *(p.1, p.6)*
- Pure direct sensorimotor grounding of every word is unrealistic; verbal definition is indispensable for scaling vocabulary. *(p.6)*
- Even controlled defining vocabularies are not enough by themselves because they may still be cyclic. *(p.6-7)*

## Design Rationale
- Use graph theory because dictionary definitions naturally induce a directed dependency graph. *(p.2-3)*
- Reduce grounding sets to cycle hitting because infinite definitional regress is exactly cycle dependence in the graph. *(p.3-5)*
- Compute the grounding kernel as an easier first-pass object before tackling exact minimum grounding sets. *(p.5-6)*
- Study learner dictionaries like LDOCE because their controlled vocabularies are already partially optimized for definitional economy. *(p.6-7)*

## Testable Properties
- A set of words grounds a dictionary graph iff it intersects every directed cycle. *(p.4)*
- The minimum grounding number of a graph equals the size of a minimum feedback vertex set. *(p.4-5)*
- Every minimum grounding set of a graph decomposes as the union of minimum grounding sets of its SCCs. *(p.4-5)*
- The grounding kernel can be found by recursively deleting words that define no other remaining words outside loops. *(p.5-6)*
- Real dictionaries with controlled defining vocabularies should still contain smaller cyclic kernels inside those vocabularies. *(p.6-7)*

## Relevance to Project
This is the first paper in the collection that gives the exact graph formalism you want to implement. It is where the project stops being a metaphor and becomes a precise computational problem: build the definitional graph, compute SCCs, compute or approximate feedback vertex sets, and strip the grounding kernel. It also explicitly positions LDOCE as a practical starting point for real English experiments. *(p.4-7)*

## Open Questions
- [ ] How should real-word polysemy and sense disambiguation be handled in a production graph?
- [ ] How small is the actual grounding kernel of LDOCE or WordNet once definitions are normalized?
- [ ] What weighting scheme would make a minimum grounding set more cognitively plausible, not just smaller?

## Related Work Worth Reading
- Harnad (1990), "The Symbol Grounding Problem." *(p.1, p.6-7)*
- Tarjan (1972), SCC decomposition. *(p.5, p.9)*
- Karp (1972), NP-completeness of feedback vertex set. *(p.5, p.9)*
- Steyvers and Tenenbaum (2005), semantic-network structure for comparison with definitional graphs. *(p.8-9)* → NOW IN COLLECTION: [[Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks]]
- Fellbaum (1998, 2005) and Procter (1978, 1995) on WordNet and LDOCE as target dictionaries. *(p.7-9)*

## Collection Cross-References

### Already in Collection
- [[Harnad_1990_SymbolGroundingProblem]] — supplies the grounding argument that motivates why some seed words must be known outside the dictionary graph.
- [[Picard_2013_HiddenStructureFunctionLexicon]] — extends this paper by assigning psycholinguistic roles to Kernel/Core/Satellites/MGS structure.
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — scales this formalism to multiple large dictionaries and adds definitional-distance hierarchies and stronger psycholinguistic evidence.

### Now in Collection (previously listed as leads)
- [[Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks]] — broad semantic-network comparator useful for separating generic lexical-network structure from specifically definitional graph structure.

### New Leads (Not Yet in Collection)
- Clark (2003) — "Recursion Through Dictionary Definition Space" — likely an early direct treatment of definitional recursion.
- Chicoisne et al. (2008) — "Grounding Abstract Word Definitions in Prior Concrete Experience" — adjacent grounding-extension paper.
- Tarjan (1972) — "Depth-first search and linear graph algorithms" — SCC algorithmic basis.
- Karp (1972) — "Reducibility among combinatorial problems" — NP-completeness and FVS complexity basis.

### Supersedes or Recontextualizes
- [[Harnad_1990_SymbolGroundingProblem]] is not superseded; it is formalized here as a dictionary-graph problem.

### Conceptual Links (not citation-based)
- [[Picard_2013_HiddenStructureFunctionLexicon]] — sharpens this paper's kernel/minimal-grounding vocabulary into a differentiated functional anatomy.
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — broadens the same graph framework and gives the mature Kernel/Core/Satellites/MinSet picture.

### Cited By (in Collection)
- [[Picard_2013_HiddenStructureFunctionLexicon]] — cites this as the earlier graph-theoretic grounding formalization.
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — cites this as prior work on grounding in dictionary definitions.
