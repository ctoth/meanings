# Process Leads Report

**Date:** 2026-04-02
**Leads found:** 16 from notes after expansion, plus 48 from citation graph on `1411.0129`
**Attempted:** 14 retrieval/normalization attempts beyond the initial two seed papers
**Parallelism:** sequential
**Succeeded:** 10
**Failed:** 2

## Succeeded
| # | Lead | Paper Directory |
|---|------|----------------|
| 1 | Blondin Masse et al. (2008) — "How Is Meaning Grounded in Dictionary Definitions?" | papers/Massé_2008_MeaningGroundedDictionaryDefinitions/ |
| 2 | Picard et al. (2013) — "Hidden Structure and Function in the Lexicon" | papers/Picard_2013_HiddenStructureFunctionLexicon/ |
| 3 | Sparck Jones (1965) — "Experiments in Semantic Classification" | papers/Sparck-Jones_1965_ExperimentsSemanticClassification/ |
| 4 | Kay (1962) — "Rules of Interpretation" | papers/Kay_1962_RulesInterpretationComputationSemantics/ |
| 5 | Bergh et al. (2025) — "Leveraging LLMs to Automatically Construct WordNets as Bilingual Resources" | papers/Bergh_2025_LeveragingLLMsConstructingWordNets/ |
| 6 | Ghizzota et al. (2025) — "Enhancing Linguistic Resources for Diachronic Analysis via Linked Data" | papers/Ghizzota_2025_EnhancingLinguisticResourcesDiachronic/ |
| 7 | Bommarito (2025) — "OpenGloss: A Synthetic Encyclopedic Dictionary and Semantic Knowledge Graph" | papers/Bommarito_2025_OpenGlossSyntheticEncyclopedicDictionary/ |
| 8 | Levary et al. (2012) — "Loops and Self-Reference in the Construction of Dictionaries" | papers/Levary_2012_LoopsSelfReferenceDictionaries/ |
| 9 | Steyvers and Tenenbaum (2005) — "The Large-Scale Structure of Semantic Networks" | papers/Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks/ |
| 10 | Fomin et al. (2008) — "On the minimum feedback vertex set problem" | papers/Fomin_2008_MinimumFeedbackVertexSetProblem/ |

## Failed
| # | Lead | Reason |
|---|------|--------|
| 1 | Initial title-only lookup for Blondin Masse et al. (2008) | Weak-title normalization path was brittle and hit HTTP 429/404 before strong identifier normalization |
| 2 | Initial title-only lookup for Picard et al. (2013) | Weak-title normalization path was brittle and hit HTTP 404 before strong identifier normalization |

## Remaining (not attempted)
Manual lead list still includes:

- Newell (1980) — "Physical symbol systems"
- Fodor and Pylyshyn (1988) — "Connectionism and cognitive architecture: A critical appraisal"
- Searle (1980) — "Minds, brains and programs"
- Gibson (1979) — "An ecological approach to visual perception"
- Leavy et al. (2012) — "Loops and self-reference in the construction of dictionaries"
- Lapointe et al. (2012) — "Enumerating minimum feedback vertex sets in directed graphs"
- Fomin et al. (2008) — "On the minimum feedback vertex set problem"
- Steyvers and Tenenbaum (2005) — "The Large-scale structure of semantic networks"
- Van Rensbergen et al. (2015) — "Examining assortativity in the mental lexicon"

Citation-graph expansion also surfaced algorithmic and psycholinguistic references such as Karp (1972), Tarjan (1972), Landauer & Dumais (1997), and Tenenbaum et al. (2011).

Additional manually widened timeline papers retrieved:
- Masterman (1961) — `papers/Masterman_1961_SemanticMessageDetectionInterlingua/` (retrieved, not yet read)
- Schindler et al. (2025) — `papers/Schindler_2025_LGDELocalGraph-basedDictionaryExpansion/` (retrieved, partially inspected, not yet fully read)

Additional papers completed after retrieval:
- Steyvers and Tenenbaum (2005) — `papers/Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks/` (read from page images; notes, abstract, citations, description, and metadata written)
- Fomin et al. (2008) — `papers/Fomin_2008_MinimumFeedbackVertexSetProblem/` (read from page images; notes, abstract, citations, description, and metadata written)
- Schindler et al. (2025) — `papers/Schindler_2025_LGDELocalGraph-basedDictionaryExpansion/` (read from page images; notes, abstract, citations, description, and metadata written)
- Bommarito (2025) — `papers/Bommarito_2025_OpenGlossSyntheticEncyclopedicDictionary/` (read from page images; notes, abstract, citations, and description written; metadata retained/updated)
- Masterman (1961) — `papers/Masterman_1961_SemanticMessageDetectionInterlingua/` (read from page images; notes, abstract, citations, description, and metadata written)

Unused-papers status:
- `unused-papers/` created but intentionally left empty; after reading `Fomin 2008` and `Steyvers 2005`, no currently read paper is clearly off-axis enough to move.
