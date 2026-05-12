# Graph Object Definitions

**Date:** 2026-05-12

This file is the implementation contract for the dictionary-kernel code. If code changes alter these meanings, this file must change in the same slice.

## Directed Definitional Graph

A dictionary graph is a directed graph `G = (V, E)` where nodes are lexical units and an edge `u -> v` means lexical unit `u` occurs in the definition of lexical unit `v`.

For the paper-faithful WordNet baseline, nodes are normalized `lemma::pos` units and definitions are parsed as content words only.

For the experimental synset graph, nodes are OEWN synsets and gloss lemmas are resolved to source synsets by unique or strict-overlap heuristics.

Source notes:

- [Massé notes](/C:/Users/Q/code/meanings/papers/Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md)
- [Vincent-Lamarre notes](/C:/Users/Q/code/meanings/papers/Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md)

## Content Words

Content words are the definition tokens retained after syntax and function words are removed. The paper baseline follows Vincent-Lamarre's simplifying stance: ignore syntax and function words, and use content words as definitional predecessors.

Implementation note: [normalize.py](/C:/Users/Q/code/meanings/src/meanings/normalize.py) owns token normalization and stopword filtering.

## Kernel

The `Kernel` is the recursively irreducible subgraph left after repeatedly removing nodes with no outgoing non-self edges inside the remaining graph. Intuitively, these are the words/senses still trapped in definitional cycles after everything definitionally downstream has been peeled away.

Implementation note: [graph_analysis.py](/C:/Users/Q/code/meanings/src/meanings/graph_analysis.py) implements this as `compute_kernel()`.

## Strongly Connected Component

An SCC is a maximal set of nodes where each node has a directed path to every other node in the set.

Implementation note: [graph_analysis.py](/C:/Users/Q/code/meanings/src/meanings/graph_analysis.py) implements this as `strongly_connected_components()`.

## Source SCC

A source SCC inside a graph is an SCC with no incoming edge from a different SCC. The papers use source SCCs inside the Kernel to define the Core.

## Core

The `Core` is the union of source SCCs inside the Kernel. In many full dictionary graphs this appears as one large SCC, but the implementation must not assume that.

This corrects the earlier temporary implementation that reported the largest SCC as Core.

Operational update: the code now exposes this as `--core-policy source-union`. It also exposes `--core-policy largest-scc` because the Picard/Vincent-Lamarre notes use both source-SCC hierarchy language and largest-SCC summary language, and the published WordNet table is much closer to the largest-SCC policy in our OEWN runs. Reports must state which policy was used.

Source notes:

- [Picard notes](/C:/Users/Q/code/meanings/papers/Picard_2013_HiddenStructureFunctionLexicon/notes.md)
- [Vincent-Lamarre notes](/C:/Users/Q/code/meanings/papers/Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md)

## Satellites

`Satellites` are Kernel nodes outside the Core. They are not trash and must not be removed just because they look abstract or editorial. Picard and Vincent-Lamarre interpret Satellite words as functionally important for full definitional reach.

## MinSet / Minimal Grounding Set

A `MinSet` or `MGS` is a feedback vertex set: a set of nodes that intersects every directed cycle. Once those nodes are treated as already known, the remaining graph is acyclic and can be recursively unfolded.

The exact minimum feedback vertex set problem is hard. The code may compute candidate MinSets with named methods, but reports must distinguish heuristic seeds from exact MinSets.

Source notes:

- [Massé notes](/C:/Users/Q/code/meanings/papers/Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md)
- [Fomin notes](/C:/Users/Q/code/meanings/papers/Fomin_2008_MinimumFeedbackVertexSetProblem/notes.md)

## Loop Ecology

Cycles and SCCs are also semantic objects. Levary shows that short loops are not merely defects to be cut away; they are often semantically coherent and structurally meaningful.

Implementation consequence: seed extraction and loop analysis must be separate report surfaces.

Source notes:

- [Levary notes](/C:/Users/Q/code/meanings/papers/Levary_2012_LoopsSelfReferenceDictionaries/notes.md)

## Allowed Model Deviations

`paper-wordnet` is the baseline mode. It exists to approximate Vincent-Lamarre's WordNet setup.

`sense` is experimental. It uses synset nodes and a strict overlap resolver. Its results can be better or worse, but they are not direct paper replication.

`lemma` is a rough proxy. It collapses senses and parts of speech and should not be used as evidence for paper-level claims.
