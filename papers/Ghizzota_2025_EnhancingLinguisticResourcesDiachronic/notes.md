---
title: "Enhancing Linguistic Resources for Diachronic Analysis via Linked Data"
authors: "Eleonora Ghizzota; Pierpaolo Basile; Claudia D'Amato; Nicola Fanizzi"
year: 2025
venue: "Global Wordnet Conference"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T01:05:52Z"
---
# Enhancing Linguistic Resources for Diachronic Analysis via Linked Data

## One-Sentence Summary
The paper builds a Linked Linguistic Knowledge Graph (LLKG) by aligning a linguistic knowledge graph, Etymological WordNet, and external linked-data resources to support diachronic lexical analysis with explicit identifiers for senses, texts, authors, dates, and etymological relations. *(p.1-11)*

## Problem Addressed
The paper asks how to organize heterogeneous lexical resources so they can support diachronic semantic analysis rather than remaining isolated graphs or databases. *(p.1-3)*

## Key Contributions
- Aligns a linguistic knowledge graph with Etymological WordNet and external resources such as Lexvo, LiLa, Universal WordNet, and Wikidata. *(p.1-3, p.7-9)*
- Converts an LPG-style graph into RDF-S/linked-data form using OntoLex/LEMON-inspired modeling. *(p.3-6)*
- Adds modeling for lexical entries, lexical senses, examples, documents, corpora, authors, and time points relevant to diachronic analysis. *(p.4-7)*
- Reports the scale of the resulting graph: 114 works, 180 occupations, 527 senses, 7,908 languages, and 2,879,193 lexical entries. *(p.8)*
- Positions linked lexical graphs as infrastructure for tracing semantic change across time and sources. *(p.1, p.8-11)*

## Methodology
The authors start from an existing Linguistic Knowledge Graph and Etymological WordNet, redesign their schema around linked-data principles, then manually and programmatically map entities to external URIs from Lexvo, LiLa, Universal WordNet, and Wikidata. They define subgraphs for lexical entries, lexical senses, examples, dates, authors, documents, and corpora, and use SPARQL queries to connect internal entities to external linked-data resources. *(p.2-9)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| EtymWN terms | — | count | 3,000,000 | — | 2 | Mined from English Wiktionary. |
| EtymWN origin links | — | count | 500,000 | — | 2 | Etymological origin relations. |
| LLKG works | — | count | 114 | — | 8 | Included after integration. |
| LLKG occupations | — | count | 180 | — | 8 | Author/metadata dimension. |
| LLKG senses | — | count | 527 | — | 8 | Sense layer reported in final graph. |
| LLKG languages | — | count | 7,908 | — | 8 | Linked via Lexvo and related resources. |
| LLKG lexical entries | — | count | 2,879,193 | — | 8 | Scale of integrated graph. |

## Methods & Implementation Details
- The schema is broken into subgraphs for lexical information, examples, dates, authors, documents, and corpora. *(p.3-7)*
- OntoLex/LEMON is used to model lexical entries and senses, while schema.org classes are used for authors, books, and corpus/document metadata. *(p.3-7)*
- Lexvo provides language and lexical URI anchors; LiLa provides Latin lemma infrastructure; UWN and Wikidata provide further sense/entity linking. *(p.6-9)*
- Etymological relations are retained and made explicit as linked-data properties rather than staying buried inside a separate lexical network. *(p.4-5, p.8)*
- The graph is motivated by lexical semantic change detection and the need to combine word senses with author/date/document metadata. *(p.1-2, p.8-11)*

## Results Summary
The paper’s main result is infrastructural rather than algorithmic: it shows that lexical, etymological, bibliographic, authorship, and temporal data can be integrated into a single linked-data graph suitable for diachronic semantic analysis. That makes lexical resources far more explorable and reusable than isolated WordNet-like resources. *(p.1-11)*

## Limitations
- This is not a kernel/minset paper and does not analyze definitional cycles or grounding sets directly. *(p.1-11)*
- Many mappings required manual intervention and disambiguation. *(p.2-3, p.8-9)*
- The graph quality depends on the quality of linked external resources such as Wikidata and EtymWN. *(p.2, p.8-9)*

## Relevance to Project
This is one of the best outside-the-box papers for your longer-term vision. If we ever compare lexical kernels across languages or across time, we will need exactly this kind of identifier-rich infrastructure so kernels can be aligned not only by glosses but by senses, dates, documents, authors, and etymological lineage. *(p.1-11)*

## Open Questions
- [ ] Can kernel extraction be layered on top of a linked-data lexical graph like LLKG?
- [ ] Could diachronic graphs reveal how kernels shift over time within one language?

## Related Work Worth Reading
- De Melo (2014), Etymological WordNet. *(p.2, p.9)*
- Basile et al. (2022), Linguistic Knowledge Graph. *(p.2, p.9)*
- McCrae et al. (2012), OntoLex/LEMON background. *(p.2-4)*
