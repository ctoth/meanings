---
title: "Experiments in Semantic Classification"
authors: "K. Sparck Jones"
year: 1965
venue: "Mechanical Translation and Computational Linguistics"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T01:05:52Z"
---
# Experiments in Semantic Classification

## One-Sentence Summary
Sparck Jones argues that machine translation needs semantic classification rather than only syntax, proposes defining word uses by semantic relations and synonym rows, and explores how thesaurus-like classes and semantic distance might be induced from contextual substitution patterns. *(p.97-112)*

## Problem Addressed
The paper asks how to construct a thesaurus or semantic classification that can resolve multiple meaning in machine translation and related computational tasks. *(p.97)*

## Key Contributions
- Treats multiple meaning as ubiquitous rather than exceptional, making semantic classification a central computational problem. *(p.97)*
- Proposes defining word uses through semantic relations, especially synonymy, and grouping word uses into rows and larger classes. *(p.97-101)*
- Distinguishes intra-linguistic definitions from extra-linguistic definition by ostension or pictures, and argues that intra-linguistic relational structure remains indispensable. *(p.98-100)*
- Develops a contextual substitution method in which rows of substitutable uses are collected from corpus positions, then used to infer thesaurus-like clusters. *(p.101-108)*
- Introduces an early notion of semantic distance via shortest paths and common intermediates in a network of synonym/use rows. *(p.109-112)*

## Methodology
The paper combines conceptual analysis with small-scale experiments on dictionary and corpus-derived rows of substitutable word uses. It examines synonymy, antonymy, hyponymy, and other relations, then builds rows of interchangeable uses, clusters them into groups or “clumps,” and proposes route-finding over these structures as a model of semantic distance. *(p.98-112)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Navigation sample headings | — | count | 267 | — | 98 | Roget-derived grouping example. |
| Initial sample words | — | count | 90 | — | 106 | Used in early clustering experiment. |
| Larger sample words | — | count | 500 | — | 107 | Follow-up clustering experiment. |

## Methods & Implementation Details
- A word’s meanings or uses are defined by surrounding context rather than taken as fixed in isolation. *(p.97)*
- Synonymy is treated not as absolute interchangeability everywhere but as context-sensitive substitutability within structured rows of use. *(p.100-103)*
- Rows of word-uses are assembled from corpus positions where replacements preserve sentence acceptability or sense. *(p.101-106)*
- Groups/clumps are then formed by similarity in shared properties or overlap, with the ambition of recovering thesaurus-like semantic classes. *(p.106-108)*
- Semantic distance is modeled through path length in a graph of shared intermediates among word-use rows. *(p.109-112)*

## Results Summary
The paper reports that purely hand-built or a priori thesaurus headings are insufficient and that contextual classification can produce more empirically grounded groupings, though the experiments remain small and labor-intensive. The strongest enduring idea is methodological: meaning should be studied through structured relations among uses, and semantic organization can be represented as paths, overlaps, and classes rather than only dictionary-style definitions. *(p.97-112)*

## Limitations
- The experimental material is small and partly hand-curated. *(p.106-108)*
- The clustering and route-finding procedures are acknowledged as simplified and not yet fully adequate. *(p.107-112)*
- The paper predates modern sense inventories and graph algorithms, so many distinctions remain informal. *(p.97-112)*

## Relevance to Project
This is the right 1965 ancestor for your project. It is not about kernels or definitional cycles, but it squarely treats lexical meaning as relational structure in a semantic network, emphasizes ambiguity resolution, and even sketches a graph-based semantic-distance concept. It shows that your project has deep roots in early computational semantics rather than being a recent curiosity. *(p.97-112)*

## Open Questions
- [ ] How would Sparck Jones's synonym rows map onto modern sense graphs?
- [ ] Could contextual substitution graphs and definitional graphs be fused in one lexical kernel model?

## Related Work Worth Reading
- Roget's Thesaurus, as the practical comparison target. *(p.97-98, p.108)*
- Lyons on semantic relations and synonymy. *(p.99-101)*
- Carnap and Quine on formal/synonymic analysis. *(p.100)*
