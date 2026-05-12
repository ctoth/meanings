---
title: "Rules of Interpretation: An Approach to the Problem of Computation in the Semantics of Natural Language"
authors: "M. Kay"
year: 1962
venue: "IFIP 62"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T01:05:52Z"
---
# Rules of Interpretation: An Approach to the Problem of Computation in the Semantics of Natural Language

## One-Sentence Summary
Kay argues that semantics should be approached computationally through explicit rules of interpretation that map words into judged meanings and structured semantic relations, rather than treating semantics as a vague residue left over after syntax. *(p.318-321)*

## Problem Addressed
The paper asks how to compute the semantics of natural language once grammatical form has been analyzed, especially for machine translation. *(p.318, p.321)*

## Key Contributions
- Rejects the view that descriptive linguistics can stop at grammar and leave meaning as an informal appendix. *(p.318)*
- Introduces `rules of interpretation` as the semantic analogue of rules of formation. *(p.318-319)*
- Proposes a small algebra of qualification in which modifiers can be applied compositionally to base items. *(p.319-320)*
- Represents semantic qualification using a network/lattice-style structure rather than only linear symbolic strings. *(p.320-321)*
- Connects semantic interpretation directly to machine translation, arguing that translation requires a bridge from syntax into vocabulary and semantics. *(p.321)*

## Methodology
This is a conceptual paper. Kay starts from the distinction between grammatical analysis and semantic interpretation, introduces a simple formal model based on qualificative relations, and sketches how it could be embedded computationally as equations or nodes in a network. *(p.318-320)*

## Key Equations / Statistical Models

$$
ab = c,\qquad de = c \Rightarrow d(ab)=e
$$
Where: the notation expresses a simple qualification system in which expressions can be transformed through equivalence and substitution relations in a semantic network. *(p.319-320)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Formal relations in the toy model | — | count | 4 | — | 319 | Reflexive law, anti-symmetric law, transitive law, unordered modifiers. |

## Methods & Implementation Details
- A semantics module should operate after grammar but not independently of it. *(p.318-319)*
- The model treats words like `human`, `child`, `male`, and `young` as nodes connected by qualificative structure. *(p.319-320)*
- Network representation is preferred because it offers a measurable notion of semantic similarity and supports machine manipulation. *(p.320)*
- Translation is framed as moving from a source-language node to a target-language equivalent while preserving the interpreted sense selected by context. *(p.321)*

## Results Summary
Kay does not offer experimental results. The outcome is a conceptual research program: semantics can be formalized enough to be computational, and interpretation should proceed in parallel with other linguistic analysis rather than after the fact. *(p.318-321)*

## Limitations
- The formal model is extremely small and schematic. *(p.319-320)*
- The paper does not solve the hard problem of identifying the correct rules of interpretation for full natural language. *(p.321)*
- It remains at the level of proposal rather than large-scale implementation. *(p.318-321)*

## Relevance to Project
This is an early ancestor rather than a direct kernel paper. Its value is that it treats semantics as an explicit computational object and already leans toward graph/network structure. That places your kernel project inside a much older semantics-first tradition. *(p.318-321)*

## Open Questions
- [ ] How close is Kay's qualification network to later lexical-semantic graph formalisms?
- [ ] Could a kernel extraction system treat definitional edges as a modern kind of rule of interpretation?

## Related Work Worth Reading
- Feigenbaum (1961) on heuristic learning. *(p.321)*
- Chomsky (1957), as the grammatical foil. *(p.321)*
