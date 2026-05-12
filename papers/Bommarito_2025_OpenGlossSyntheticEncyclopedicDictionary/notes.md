---
title: "OpenGloss: A Synthetic Encyclopedic Dictionary and Semantic Knowledge Graph"
authors: "Michael J. Bommarito II"
year: 2025
venue: "arXiv preprint"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T02:33:16Z"
---
# OpenGloss: A Synthetic Encyclopedic Dictionary and Semantic Knowledge Graph

## One-Sentence Summary
This paper presents `OpenGloss`, a large synthetic English lexical-semantic resource built with a schema-validated multi-agent LLM pipeline, producing 150,101 lexemes, 536,829 senses, 9.1 million semantic edges, encyclopedic context, etymology, usage examples, and collocations at a scale comparable to WordNet but with a more learner-oriented and computationally tractable design. *(p.1-25)*

## Problem Addressed
The paper asks whether current LLM-based structured generation can produce a large, usable lexical-semantic resource that bridges dictionary definitions, encyclopedic context, etymology, and semantic relations without relying on slow manual curation or noisy multi-source integration alone. *(p.1-6, p.21-25)*

## Key Contributions
- Builds a schema-governed synthetic lexical resource with `150,101` lexemes and `536,829` senses, roughly WordNet-scale in breadth but much richer in sense definitions and contextual content. *(p.1-2, p.11-18)*
- Uses a four-stage pipeline: lexeme selection, sense generation, graph construction, and enrichment. *(p.5-10)*
- Defines a hierarchical data model with three layers: `Lexeme`, `PartOfSpeechEntry`, and `LexicalSense`. *(p.6-8)*
- Produces a semantic graph with `9.1M` edges including synonyms, antonyms, hypernyms, hyponyms, collocations, and inflections. *(p.1, p.8-10, p.15)*
- Adds near-universal encyclopedic and etymological coverage for educational and NLP use. *(p.2, p.10-16)*
- Benchmarks the result against WordNet, BabelNet, and ConceptNet and argues that OpenGloss is complementary rather than a replacement. *(p.16-25)*

## Methodology
OpenGloss is built by a multi-agent generation pipeline implemented with schema-validated structured outputs. Stage 1 chooses the lexeme inventory from an American dictionary core and pedagogically expanded terms; Stage 2 generates POS-specific senses with concise definitions, examples, and semantic relations; Stage 3 deterministically extracts graph edges from the structured sense records; Stage 4 enriches entries with etymological trails and short encyclopedic descriptions. Strict Pydantic validation, retry-on-error, graph connectivity checks, and a 1,000-item QA sample with Claude Sonnet 4.5 are used to assess structure and quality. *(p.5-11, p.24-25, p.29-30)*

## Key Equations / Statistical Models
This paper is primarily a systems/data paper and does not center its contribution on formal equations. The closest thing to a model is the staged data-generation and graph-extraction pipeline described in Figures 1-2 and Sections 3.1-3.6. *(p.5-11)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Total unique words / lexemes | — | count | 150,101 | — | 1-2, 12-13 | Final lexeme inventory. |
| Total word senses | — | count | 536,829 | — | 1-2, 11-13 | Average 3.58 senses per lexeme. |
| Average senses per word | — | count | 3.58 | — | 1-2, 11-13 | Maximum reported sense count 24. |
| Maximum senses per word | — | count | 24 | — | 13 | Table 1. |
| Sense-level semantic edges | — | count | 5,199,334 | — | 15 | Synonym, antonym, hypernym, hyponym, inflection. |
| POS-level edges | — | count | 3,939,092 | — | 15 | Mostly collocations plus inflections. |
| Total semantic edges | — | count | 9.14M | — | 1, 9-10, 15 | Combined network size. |
| Usage examples | — | count | about 1M | — | 1 | Roughly 2 per sense on average. |
| Collocations | — | count | about 3M | — | 1 | POS-level lexical patterns. |
| Encyclopedic content | — | words | about 60M | 200-400 per entry | 1, 10, 15-16 | Rich contextual enrichment. |
| Etymology coverage | — | proportion | 97.3% | — | 2, 15 | Lexeme-level etymology trails. |
| Encyclopedia coverage | — | proportion | 99.7% | — | 2, 15 | Contextual entries. |
| Pipeline runtime | — | hours | <96 | — | 2, 10, 21, 24 | Full dataset generation. |
| API cost | — | USD | <1000 | — | 2, 10, 21, 24 | Reported full-run cost. |
| Validation sample size | — | entries | 1,000 | — | 10-11, 29-30 | QA sample. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| WordNet-style breadth comparison | synsets/senses | 536,829 vs 117,769 | — | — | OpenGloss vs WordNet 3.0 senses | 16-18 |
| Shared vocabulary with WordNet | overlap proportion | 38% | — | — | unique-word overlap | 21 |
| OpenGloss unique words not in WordNet | count | 93,444 | — | — | complementary vocabulary | 17 |
| WordNet unique words not in OpenGloss | count | 90,669 | — | — | complementary vocabulary | 17 |
| Sense-level synonym coverage | proportion | 99.7% | mean 3.0 | — | senses with synonyms present | 15 |
| Sense-level hypernym coverage | proportion | 99.9% | mean 2.0 | — | senses with hypernyms present | 15 |
| Sense-level hyponym coverage | proportion | 98.6% | mean 2.6 | — | senses with hyponyms present | 15 |
| Successful WordNet-pragmatic replication in QA | proportion | 38.6% | — | — | flagged entries judged deliberate design choices | 29-30 |
| High-confidence QA entries | proportion | 14.1% | — | — | 1,000-entry sample | 30 |
| Acceptable with minor issues | proportion | 17.1% | — | — | 1,000-entry sample | 30 |
| Flagged for analysis | proportion | 68.8% | — | — | 1,000-entry sample | 30 |

## Methods & Implementation Details
- The data model deliberately constrains sense granularity to `1-4` senses per POS entry, prioritizing tractability and pedagogical usefulness over maximal expert refinement. *(p.6-8, p.18-19, p.22)*
- Lexeme selection blends a general American English base with snowball expansion from seed concepts relevant to K-12 vocabulary and academic domains. *(p.5-6)*
- Sense generation uses two agents: an overview agent deciding POS/sense counts and a detail agent generating definitions, examples, and semantic neighborhoods. *(p.8-10)*
- Graph construction is deterministic once the structured sense outputs exist: synonym, antonym, hypernym, and hyponym edges are extracted from sense records without further LLM calls. *(p.9-10)*
- Validation includes schema checks, lexical target validation, and graph invariants such as acyclic hypernym/hyponym relations and symmetric synonym/antonym pairs. *(p.10-11)*
- The authors explicitly treat inflected forms and some proper nouns as positive pragmatic design choices, even though a stricter traditional dictionary QA lens flags them. *(p.10-11, p.20-21, p.29-30)*

## Figures of Interest
- **Figure 1 (p.6):** Four-stage generation pipeline.
- **Figure 2 (p.7):** Hierarchical data model.
- **Figure 3 (p.12):** Example entries for `algorithm` and `photosynthesis`.
- **Table 1-3 (p.13-15):** Coverage, POS distribution, and relationship distribution.
- **Table 4-5 (p.16-18):** Comparison with WordNet and sense-granularity contrasts.
- **Table 6 / Appendix A (p.29-30):** QA profile and flagged-entry breakdown.

## Results Summary
OpenGloss shows that structured LLM generation can now produce a large, internally typed lexical resource with serious breadth and density. Compared with WordNet, it offers comparable or slightly broader word coverage, many more sense definitions, richer contextual support, and faster update potential, but at the cost of noisier semantic precision and coarser sense granularity. The paper is unusually explicit that this is a pragmatic engineering tradeoff rather than a philosophical victory: OpenGloss is meant to complement manual lexicography, not replace it. *(p.16-25)*

## Limitations
- Sense boundaries are coarser and more pedagogically oriented than WordNet’s expert-curated distinctions, which can be a problem for tasks requiring fine lexical disambiguation. *(p.18-19, p.22-24)*
- The content is generated from current foundation models and therefore inherits model biases, coverage artifacts, and occasional semantic imprecision. *(p.1-2, p.20-25, p.29-30)*
- QA is substantial but still sample-based and partially benchmarked against WordNet-aligned conventions rather than independent expert consensus. *(p.10-11, p.23, p.29-30)*
- The resource is English-only in the current version, though multilingual expansion is proposed as future work. *(p.23)*
- For a kernel project, this is a broad lexical graph, not a non-circular definitional basis. *(p.1-2, p.21-25)*

## Relevance to Project
This paper is useful as infrastructure, not as a direct answer to the kernel question. OpenGloss could become a very large candidate graph for experiments on kernels, multilingual alignment, or sense-level lexical neighborhoods, especially because it exposes typed semantic edges and richer context than WordNet. But it does not solve minimal recursive seeding, and its sense inventory is engineered for usability rather than philosophical minimality. *(p.16-25)*

## Open Questions
- [ ] If we induce a definitional graph from OpenGloss definitions, do the `Kernel/Core/Satellite/MinSet` objects resemble those found in WordNet/LDOCE-style resources?
- [ ] Can OpenGloss’s rich edge typing help align kernels across languages more robustly than plain dictionary definitions?
- [ ] How much does the learner-oriented sense compression distort graph-theoretic kernel structure?

## Related Work Worth Reading
- WordNet / Open English WordNet for manual lexicographic baseline. *(p.3-4, p.16-19)*
- BabelNet and ConceptNet for integration / commonsense contrasts. *(p.3-4, p.16-18)*
- pydantic-ai and related structured generation tooling for reproducible resource construction. *(p.4-5, p.8-10, p.27)*
- COMET / AutoKG / GraphRAG for adjacent structured knowledge generation. *(p.4, p.22-23, p.25-28)*

## Collection Cross-References

### Already in Collection
- [[Bergh_2025_LeveragingLLMsConstructingWordNets]] — another 2025 lexical-resource construction paper, but aimed at bilingual WordNets rather than synthetic monolingual generation.
- [[Ghizzota_2025_EnhancingLinguisticResourcesDiachronic]] — relevant knowledge-graph infrastructure for lexical resources across time.
- [[Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks]] — broad semantic-network comparator for thinking about the structure of a resource like OpenGloss.

### New Leads (Not Yet in Collection)
- AutoSynHG / AutoKG / KEPLER / COLAKE — modern structured generation and hybrid-symbolic lexical/knowledge models.
- GraphRAG — for combining structured lexical graphs with retrieval pipelines.
- Open English WordNet 2024 / Open Multilingual WordNet resources.

### Supersedes or Recontextualizes
- None in the current collection.

### Conceptual Links (not citation-based)
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — OpenGloss could serve as a new large lexical graph on which to test dictionary-kernel extraction.
- [[Schindler_2025_LGDELocalGraph-basedDictionaryExpansion]] — both are pragmatic 2025 approaches to lexical-resource building, but from opposite directions: one grows from a seed, the other generates a large resource top-down.
