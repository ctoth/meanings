---
title: "Leveraging LLMs to Automatically Construct WordNets as Bilingual Resources"
authors: "Johann Bergh; Jörg Waitelonis; Melanie Siegel"
year: 2025
venue: "Global Wordnet Conference"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T01:05:52Z"
---
# Leveraging LLMs to Automatically Construct WordNets as Bilingual Resources

## One-Sentence Summary
The paper presents a practical pipeline for creating inferred and hybrid non-English WordNets from the Open English WordNet by translating lemma-definition pairs with LLMs or machine translation, showing that LLM-assisted prompting substantially improves bilingual WordNet construction quality. *(p.1-9)*

## Problem Addressed
The paper asks how to create usable WordNets for languages that lack large hand-curated lexical-semantic resources, especially as bilingual resources linked to OEWN. *(p.1-2)*

## Key Contributions
- Defines an `inferred WordNet` pipeline that translates lemma-definition combinations from OEWN into a target language. *(p.2-4)*
- Defines a `hybrid WordNet` pipeline that merges inferred synsets with existing local WordNet structure such as OMW or OdeNet. *(p.4)*
- Shows that naive machine translation is often not enough, especially for polysemy and homography, and that context-aware prompting materially improves outcomes. *(p.2-6)*
- Reports strong success rates for German and Afrikaans when LLM prompting is combined with manual evaluation or LLM-as-judge verification. *(p.6-7)*
- Positions LLMs as practical accelerators for multilingual lexical-graph construction. *(p.7-9)*

## Methodology
For each OEWN synset, the system concatenates lemma and definition, translates that combined string into the target language, and inserts the translated lemma-definition pair into a database while preserving links to the source OEWN synset and ILI. Several prompting strategies are evaluated: raw translation prompts, context-aware translation prompts, non-context-aware prompts, and an LLM-as-judge setup for selecting or validating candidates. The resulting entries are compared against manually verified subsets. *(p.2-7)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| OEWN synsets | — | count | 120,135 | — | 1 | English OEWN size used as source. |
| OMW German synsets | — | count | 35,912 | — | 1 | Existing resource scale. |
| Afrikaans evaluated synsets | — | count | 697 | — | 6-7 | Manual evaluation subset. |
| German evaluated synsets | — | count | 697 | — | 6-7 | Manual evaluation subset. |
| German context-aware success | — | proportion | 83% | — | 6-7 | 577/697 after prompt-based context-aware translation. |
| German LLM-as-judge success | — | proportion | 93% | — | 6-7 | 645/697. |
| Afrikaans context-aware success | — | proportion | 89% | — | 7 | 545/607. |
| Afrikaans LLM-prompt success | — | proportion | 90% | — | 7 | 630/697 in table. |

## Methods & Implementation Details
- Each synset carries a stable ILI and WordNet ID, allowing bilingual linking even when lexeme strings change. *(p.1, p.3-4)*
- Translation inputs combine lemma and definition to reduce ambiguity; for example `washer` can map to different synsets depending on the definition context. *(p.2-3)*
- Hybrid WordNets are built by merging inferred WordNet entries with pre-existing local resources to improve quality and coverage over time. *(p.4, p.7-8)*
- LLM prompting can disambiguate difficult cases like abstract adjectives or polysemous nouns better than raw machine translation. *(p.5-6)*
- LLM-as-judge is used as a high-throughput evaluation surrogate, with results roughly matching manual validation quality. *(p.6-7)*

## Results Summary
The core result is practical: LLMs and prompt engineering can make multilingual WordNet construction fast enough to be viable for under-resourced languages. The paper reports 93% success for German and around 90% for Afrikaans in the strongest settings, with context-aware prompts consistently outperforming naive translation. *(p.6-9)*

## Limitations
- Quality depends heavily on the target language and translation support quality. *(p.5-8)*
- The method constructs WordNets from an existing English source rather than discovering lexical structure de novo. *(p.2-4)*
- LLM outputs still need verification, deduplication, and structural cleanup. *(p.3-7)*

## Relevance to Project
This matters for the cross-language version of your kernel project. It suggests that if exact multilingual definitional resources do not already exist, we can increasingly build aligned lexical graphs automatically and then compare their hidden structures. It is not a kernel paper, but it is a direct enabler of multilingual kernel comparison. *(p.1-9)*

## Open Questions
- [ ] How stable would kernel structure be across LLM-generated bilingual WordNets?
- [ ] Does automatic WordNet construction preserve the same cycle/SCC profile as human-built lexica?

## Related Work Worth Reading
- Siegel and Bergh (2023), connecting multilingual WordNets. *(p.2, p.8-9)*
- Voyiatzis et al. (2023), WordNet from definition generation. *(p.1)*
- Ramnyshyn et al. (2024), automatic hypo-hypernym induction. *(p.2, p.8)*
