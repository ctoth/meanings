# Codex Swanson Review

**Date:** 2026-05-12

## Scope and Evidence

I read the five Swanson briefs, `README.md`, `reports/synthesis-minimal-core-to-expansion.md`, `reports/graph-object-definitions.md`, `papers/index.md`, the local notes for Massé 2008, Picard 2013, Vincent-Lamarre 2014, and Harnad 1990, and skimmed `src/meanings/`. I did not do fresh web searches or citation-graph verification. So I treat the prompts' "literatures appear disjoint" claims as hypotheses, not established facts.

The repo currently computes dictionary graphs with edges `defining word -> defined word`, Kernel by iterative removal, Core/Satellite by SCC policy, candidate seed sets by cycle hitting, loop ecology, and optional annotation overlays. The bundled OEWN summaries have no psycholinguistic annotation coverage unless local CSVs are supplied. That matters: several briefs ask for empirical comparisons that are not yet in the repo outputs.

## Executive Verdict

The five prompts are not equal.

1. **Perron-Frobenius valuation** is the strongest. It names a real mathematical recurrence across economics, Markov chains, sociology, bibliometrics, web search, and parts of NLP. The specific contribution to this repo is also concrete: compare discrete FVS grounding sets with continuous spectral centrality on the Kernel. The risk is overclaiming "anchor" where the eigenvector is only "stationary importance under a chosen flow convention."

2. **Structural controllability / driver nodes** is the second strongest. It is not a synonym for grounding, but the mismatch is useful. FVS asks "what must be taken as already known to make definitions well-founded?" Maximum-matching controllability asks "where must inputs enter a linear dynamical system?" They diverge on simple graphs, which is not a defect; it sharpens the meaning of lexical grounding.

3. **Core-satellite ecology** is empirically promising but conceptually fragile. The shared vocabulary is a real Swanson clue, and Hanski gives a generative dynamic missing from the static dictionary literature. But the lexical Core/Satellite split is SCC/dependency structure, not obviously an occupancy bimodality. It becomes strong only if diachronic dictionary data show colonization-extinction dynamics in defining vocabularies.

4. **Money / numeraire** is a good metaphor and partly a real bridge through Sraffa and input-output eigenvectors, but as written it mixes three different things: numeraire choice, commodity standards, and intrinsic grounding. Prompt 5 largely subsumes the durable part.

5. **Yoneda / Harnad** is philosophically interesting but the easiest to inflate. The best resolution is mostly compatibility: Yoneda is internal to a specified category; Harnad asks how the symbol-category link gets grounded for an agent. The dictionary graph can illustrate that distinction, but it will not adjudicate categorical structuralism by itself.

If only one line is pursued next, pursue **Perron-Frobenius on the OEWN Kernel**. If two, pair it with **FVS-vs-driver-node comparison**. Together they turn "what is a grounding set?" into a small comparative theory of discrete grounding, spectral valuation, and dynamical control.

## Brief 1: Money, Numeraire, and Symbol Grounding

**Is the link real?** Partly. The strongest version is not "meaning is money" or "a grounding set is gold." The real common structure is weaker and more precise: a relational system lacks intrinsic units; one can choose a reference element or vector to express the rest. Monetary economics has several such devices: a numeraire for relative prices, a commodity standard as institutional anchor, Sraffa's standard commodity as a constructed invariant bundle, and fixed-point price systems in general equilibrium.

The dictionary side is different. A MinSet is not a unit of account. It is a cycle-hitting set that makes recursive definition well-founded. It does not assign relative semantic prices to all words. It says which nodes must be removed from cycles so the rest can be unfolded. That is closer to "primitive vocabulary" than to "numeraire."

**Strongest objection.** The prompt conflates external anchor and internal normalization. A numeraire is often a gauge choice: prices are relative, and choosing one commodity as unit does not ground economic value in that commodity. A gold standard is an institutional convertibility rule, not a theorem about value. A MinSet is stronger than either: without some seed, the recursive definition operator cannot bottom out. So the analogy is not exact.

**What the brief missed.** It should separate:

- **Gauge fixing:** choosing units among already meaningful relative prices.
- **Institutional backing:** monetary convertibility, state acceptability, settlement constraints.
- **Production eigenstructure:** Sraffa/Leontief-style self-replacing systems.
- **Grounding:** exogenous non-symbolic connection in Harnad's sense.

Only the third has a tight mathematical bridge to prompt 5. The first is mostly analogy. The second is social ontology. The fourth is cognitive grounding.

**Highest-yield use.** Keep this brief as an interpretive preface to the Perron-Frobenius line. Do not make it the lead paper. The "Nixon shock = dictionary has no Kernel that bottoms out" sentence is rhetorically vivid but technically loose: going off gold does not imply an economy is pure relation in the same sense that a cyclic dictionary has no acyclic definitional base.

## Brief 2: Core-Satellite Ecology

**Is the link real?** Potentially, but it needs data. The shared words "Core" and "Satellite" are not enough. Hanski's core-satellite model is about occupancy distributions across habitat patches under colonization-extinction dynamics, often with rescue effects. The dictionary Core/Satellite split is graph-theoretic: source SCC(s) inside the Kernel versus other Kernel nodes. These are structurally different observables.

The real opportunity is dynamic: dictionary components are currently static outputs, while ecology offers a mechanism that could generate persistent central/peripheral classes. The lexical analogue would be words entering and leaving definitions across editions or corpora. A common definer has a higher chance of being reused because lexicographers expect readers to know it; rare definers disappear unless maintained by domain necessity. That is a plausible preferential-attachment/rescue-effect story.

**Strongest objection.** Hanski's target signature is occupancy bimodality. The lexical literature's Core/Satellite split does not require a bimodal distribution of definer occupancy. It comes from SCC decomposition after Kernel stripping. A heavy-tailed definer-degree distribution could produce "core-looking" words without Hanski's mechanism. If OEWN definer degrees are unimodal or simply Zipfian/heavy-tailed, the specific ecological transfer weakens.

**What the brief missed.** It should distinguish at least four lexical analogues of "site occupancy":

- number of definitions containing a word;
- number of dictionary editions in which a word appears as a definer;
- number of semantic domains whose definitions use the word;
- number of local SCCs or loop motifs in which the word participates.

Only the second is genuinely ecological in the Hanski sense. The first is static abundance. The third is closer to niche breadth. The fourth is graph role.

The brief also underplays a local warning: this repo's current OEWN top definer lists are dominated by resolution and gloss-parsing artifacts such as `large [n]` as a garment size, `born [n]` as Max Born, and proper-name-like senses. Any occupancy test must first fix sense resolution and stopword/gloss-glue leakage, or it will measure parser artifacts.

**Highest-yield use.** Medium-high, but only after a bimodality check and preferably with diachronic data. The proposed "colonization of definitions" model is worth keeping; the static shared terminology alone is weak.

## Brief 3: Controllability and Driver Nodes

**Is the link real?** Yes, but the answer is "interesting divergence," not identity. FVS grounding and structural controllability both ask for small privileged node sets in directed graphs, but they privilege different failure modes.

FVS removes every directed cycle. It is about well-foundedness of recursive definitions. In a DAG, the empty set is an FVS, because no cyclic regress exists. But a DAG still needs driver nodes under structural controllability: unmatched sources or dilation-created unmatched nodes must be directly actuated. That one example already proves the two concepts cannot coincide generally.

**Strongest objection.** Structural controllability assumes a linear dynamical system `x' = Ax + Bu` and generic edge weights. Dictionary definition unrolling is closer to a monotone closure operator or logic-program dependency graph. The matching theorem is about controllability of continuous state variables, not semantic learnability. Calling driver nodes "grounding nodes" would be wrong.

**What the brief missed.** The best bridge is not raw driver nodes; it is a three-way comparison among:

- **FVS:** cycles that block definitional well-foundedness;
- **minimum path cover / matching in DAGs:** how many independent definitional chains remain after cycles are broken;
- **target controllability:** which seed words are needed to define a specified target vocabulary.

The DAG point is especially important. After removing a MinSet, the residual graph is acyclic. On that residual graph, matching/path-cover ideas become relevant again: they can describe how many independent "definition streams" are needed to traverse the acyclic remainder, even though they are not grounding in the Harnad/Massé sense.

**Highest-yield use.** High. It gives a precise negative theorem surface: FVS and driver sets disagree on DAGs, directed cycles, and SCCs in predictable ways. That makes a good paper because the result is clarifying even if the analogy fails.

## Brief 4: Yoneda and Harnad

**Is the link real?** Conceptually real, but mostly as a boundary clarification. Yoneda says an object in a fixed category is determined up to isomorphism by its Hom-relations. Harnad says symbolic meanings are not secured by relations among uninterpreted symbols alone. These are not straightforwardly contradictory because Yoneda presupposes the category, objects, morphisms, and equality notion. Harnad is asking how a cognitive agent's symbols get connected to the world so that the relational structure is about anything.

**Strongest objection.** The prompt risks treating a theorem about mathematical representation as if it were a thesis about cognitive semantics. "Determined up to isomorphism" is not "intrinsically meaningful to an agent." A perfect relational profile inside an uninterpreted graph can identify a node structurally without grounding it sensorimotorily.

**What the brief missed.** The closest philosophical neighbors are not only category theory. They are inferential-role semantics, conceptual-role semantics, structuralism in philosophy of mathematics, model-theoretic permutation arguments, Putnam-style model-theoretic indeterminacy, Benacerraf's problem, and distributional semantics. The natural opponent for Harnad is not Yoneda alone but any strong claim that role within a system exhausts meaning.

The empirical suggestion also needs care. If graph features correlate with AoA/concreteness/frequency, that is not automatically evidence against "Yoneda completeness"; those features could themselves be reflected in graph position because lexicographers write definitions for human learners. The stronger analysis would ask whether extra-graph sensorimotor variables predict layer membership or MinSet membership after controlling for structural features such as in-degree, out-degree, SCC size, layer, PageRank, and cycle participation. The repo supports annotation loading, but bundled reports currently have zero annotation coverage.

**Highest-yield use.** Low-to-medium as an empirical project, medium as a philosophy note. It is useful as a guardrail against overclaiming that a graph kernel is "meaning." It is not the best computational next step.

## Brief 5: Perron-Frobenius Valuation

**Is the link real?** Yes, with distinctions. Perron-Frobenius theory is genuinely a repeated answer to "what self-consistent positive weighting does this nonnegative relational system induce?" It appears in Markov stationary distributions, eigenvector centrality, input-output economics, Sraffa-style production systems, PageRank-like web ranking, HITS/LSA-adjacent spectral methods, and social influence/consensus dynamics.

The repo-specific idea is strong: FVS gives a discrete family of possible grounding sets, usually non-unique. A Perron vector gives a continuous weighting that is unique under irreducibility and aperiodicity conditions. On the dictionary Kernel, especially within large SCCs, it could serve as a "soft foundationalness" score. That is not a replacement for grounding, but it is a principled way to rank cyclic importance.

**Strongest objection.** Perron centrality is not grounding. It is a stationary valuation under a chosen adjacency orientation and normalization. On this repo's edge convention (`defining -> defined`), high outdegree means a word is used in many definitions, while high eigenvector centrality depends on being connected to other high-scoring nodes in the selected direction. Reverse the graph and the interpretation changes. Add damping and you import an exogenous teleportation prior. Restrict to the largest SCC and you discard smaller cyclic structures. None of those choices is neutral.

**What the brief missed.** It should distinguish "canonical because theorem" from "substantive because model." Perron-Frobenius gives uniqueness once a nonnegative irreducible matrix is specified. It does not tell you which matrix is semantically right:

- adjacency vs transpose;
- weighted definitions vs binary edges;
- lemma graph vs synset graph vs `lemma::pos`;
- Kernel-only vs full graph with damping;
- raw eigenvector vs PageRank vs HITS authority/hub vectors;
- stopword-filtered content graph vs richer syntactic dependency graph.

The brief also needs a null model. If Perron ranking merely recovers outdegree or frequency, the "canonical soft grounding vocabulary" claim is thin. The right test is incremental predictive value over degree and layer.

**Highest-yield use.** Highest of the five. It gives a concrete implementation path and a publishable comparison: discrete cycle-hitting grounding versus continuous spectral self-valuation.

## Independent Contribution 1: A Sharper Perron-FVS Program

The target claim should not be "Perron solves the MinSet arbitrariness problem." It should be:

> In a dictionary definition graph, FVS identifies the nodes whose exogenous grounding is sufficient to make recursive definition well-founded; Perron-Frobenius identifies the self-consistent centrality of nodes inside the cyclic dependency substrate. These are complementary notions of foundationalness: one discrete and well-foundedness-oriented, one continuous and flow-oriented.

That formulation avoids the false implication that a high Perron score makes a word grounded. It also yields precise predictions.

**Prediction A: Perron rank and FVS membership will overlap but not coincide.** High Perron nodes in the largest Kernel SCC should be overrepresented in heuristic MinSets because removing high-cycle-participation nodes breaks many cycles. But exact or near-exact MinSets should also include low-centrality articulation-like nodes that hit specific local cycles cheaply. Those low-centrality FVS nodes are theoretically important: they are "cycle bottlenecks," not global anchors.

**Prediction B: Core/Satellite contrast will split by spectral role.** Core nodes should dominate the top Perron ranks under the repo's source-SCC Core policy only if the Core includes the large strongly connected source structure. Satellite nodes should include two different populations: peripheral low-score nodes and small-SCC specialists that have high within-SCC centrality but low global centrality.

**Prediction C: orientation will expose two senses of foundationalness.** On `defining -> defined`, centrality measures definitional productivity or downstream use. On `defined -> defining`, it measures dependency on already-important definers. A serious report should compute both and name them separately. If only one is used, the paper will smuggle in a theory of "importance" through edge orientation.

**Prediction D: damping will be less informative than Frobenius normal form.** PageRank on the full graph solves reducibility by adding teleportation, but teleportation is a modeling hack for browsing, not dictionary learning. A better dictionary-native approach is SCC condensation: compute spectral scores inside nontrivial SCCs, then propagate scores outward through the DAG using the recursive definition operator or an absorbing Markov-chain model. This respects the Kernel/Rest decomposition instead of flattening it.

Relevant literature beyond the prompt includes Katz centrality as an attenuated walk-count predecessor, Hubbell influence, Pinski-Narin journal influence, Kleinberg HITS, DeGroot consensus, Bonacich power/centrality, Leontief input-output models, Sraffa/Pasinetti/Newman, Perron-Frobenius treatments of nonnegative matrices, and modern non-backtracking centrality warnings in networks. The warning literature matters because eigenvector centrality can localize on high-degree subgraphs; a localized vector would be bad evidence for global semantic foundationalness.

Concrete implementation target:

- add `src/meanings/spectral_analysis.py`;
- expose `perron_scores(adjacency, nodes, orientation, component_policy)`;
- compute SCC-local eigenvectors for nontrivial Kernel SCCs;
- write a report comparing ranks against seed membership, Core/Satellite labels, degree, cycle participation, and available annotations;
- include null models: degree rank, randomized edge-preserving graph, and label-shuffled layer membership.

The one figure should be a scatter: x-axis Perron rank or score, y-axis cycle-hitting frequency across many sampled MinSets or greedy runs, colored by Core/Satellite/Rest. If the top-left and top-right structures separate cleanly, the paper has a real result.

## Independent Contribution 2: Controllability as a Negative Control for Grounding

The controllability link becomes strongest if used adversarially: not "driver nodes are grounding nodes," but "driver nodes are a control-theoretic foil that reveals what FVS grounding is not."

Formal contrast:

> A grounding seed is sufficient when every non-seed node is reachable by iterated satisfaction of all definitional prerequisites. A control input set is sufficient when generic linear dynamics over the graph are structurally controllable. The first is an all-predecessors closure condition plus cycle breaking; the second is a matching/dilation condition.

Worked examples should carry the argument:

- **DAG chain `a -> b -> c`:** FVS is empty; structural controllability needs a driver at `a` under the usual orientation. Grounding says no external symbol is needed to break cycles, but learning still needs base definitions outside this three-node toy if `a` has no definers. This exposes that FVS over the full dictionary assumes sources are either already available or outside the modeled cycle problem.
- **Directed cycle `a -> b -> c -> a`:** FVS size is 1. Structural controllability of a simple directed cycle can need one driver. They coincide in size, but for different reasons.
- **Two cycles sharing one articulation node:** FVS may select the articulation as a cheap cycle breaker; matching may select a different unmatched node depending on edge pattern. This isolates cycle economy from actuation placement.
- **Star-like DAG:** many nodes can be definitionally acyclic while matching can still require particular drivers because of dilation.

This suggests a useful repo experiment: compute maximum-matching driver nodes on the same OEWN graph and on the residual DAG after removing a candidate seed. Compare:

- drivers that are not seed nodes: graph-dynamical sources or dilations, not grounding bottlenecks;
- seed nodes that are not drivers: cycle breakers with no special control-input role;
- overlap: nodes that are both cyclic bottlenecks and dynamical entry points.

Relevant literature beyond the prompt includes Lin's structural controllability theorem, maximum matching formulations by Liu-Slotine-Barabasi, target controllability, exact controllability critiques, control energy work, and debates over whether one input signal can technically control many driver nodes. For this project, target controllability is more promising than full-network controllability: a user often wants to ground a domain vocabulary, not all of English.

The concrete prediction is low overlap after controlling for degree. If overlap is high, it will probably be because both methods favor high-degree/high-cycle-participation nodes, not because they compute the same object. That makes degree-preserving null models essential.

## Cross-Brief Synthesis

The durable architecture is three-layered:

1. **Well-foundedness layer:** Massé/Picard/Vincent-Lamarre. Compute Kernel, SCCs, Core/Satellites, candidate MinSets. This is the only layer that directly answers the dictionary bootstrap question.

2. **Valuation layer:** Perron/Sraffa/PageRank/centrality. Rank cyclic nodes by self-consistent relational importance. This can choose or weight among otherwise multiple grounding candidates, but it does not itself ground them.

3. **Dynamics layer:** controllability and ecology. Ask how the graph changes, how a target vocabulary can be reached, and which nodes act as intervention points under a specified process.

Money belongs mainly in the valuation layer. Hanski belongs in the dynamics layer. Yoneda/Harnad belongs as a philosophical boundary condition: internal relational determination is not the same as external grounding.

## Recommended Next Work

1. Implement the Perron/FVS comparison on `paper-wordnet` first, not the experimental synset graph. The current synset resolver skips many ambiguous matches, and the paper-wordnet mode is the repo's baseline.

2. Compute structural controllability as a separate report, explicitly framed as contrast rather than equivalence.

3. Before pursuing Hanski, run a static occupancy diagnostic: definer-degree distribution, Hartigan dip or mixture check if available, and degree-preserving null comparison. Then look for diachronic dictionary data.

4. Do not lead with Yoneda unless the target audience is philosophy of cognitive science or applied category theory. It is a good framing essay, not the best empirical engine.

5. Treat all citation-disjointness claims as unverified until searched. The report I wrote here is a conceptual and repo-grounded review, not a bibliometric confirmation.

## Final Ranking

| Rank | Brief | Verdict | Best Use |
|---:|---|---|---|
| 1 | Perron-Frobenius valuation | Real mathematical bridge; highest-yield | Soft cyclic foundationalness, MinSet weighting, spectral-vs-combinatorial paper |
| 2 | Controllability / driver nodes | Real contrast; not identity | Clarify what grounding is not; target-grounding extensions |
| 3 | Core-satellite ecology | Promising if data support dynamics | Diachronic defining-vocabulary model |
| 4 | Money / numeraire | Partly real but too blended | Historical/metaphorical preface to spectral valuation |
| 5 | Yoneda / Harnad | Useful boundary clarification | Philosophy framing; guardrail against graph-only semantics |

The strongest paper that should exist is not "Meaning Has a Gold Standard." It is closer to:

**Discrete Grounding and Spectral Valuation in Dictionary Graphs.**

Thesis: dictionary kernels expose two non-equivalent notions of lexical foundationalness: minimum feedback vertex sets identify nodes required for well-founded recursive definition, while Perron-Frobenius scores identify self-consistent importance inside the cyclic definitional substrate. Their agreement and disagreement predict which words are global definitional hubs, local cycle bottlenecks, or merely high-frequency editorial conveniences.
