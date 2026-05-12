# Papers Index

## Bergh_2025_LeveragingLLMsConstructingWordNets  (wordnet, multilingual, llms, lexical-graphs)
This paper shows how LLMs and prompt-based translation can be used to build bilingual and hybrid WordNets from the Open English WordNet. It is relevant to this project because it points toward a practical route for constructing comparable lexical-semantic graphs across languages before attempting kernel alignment.

## Bommarito_2025_OpenGlossSyntheticEncyclopedicDictionary  (lexical-graphs, llms, knowledge-graphs, dictionaries)
This paper presents `OpenGloss`, a large synthetic English lexical-semantic resource built by a schema-validated multi-agent LLM pipeline that integrates definitions, semantic relations, encyclopedic context, examples, and etymology. It is relevant to this project as large-scale infrastructure for experiments on lexical graphs, sense inventories, and possible future kernel extraction over richer resources.

## Fomin_2008_MinimumFeedbackVertexSetProblem  (graph-theory, algorithms, feedback-vertex-set, exact-algorithms)
This paper gives exact and enumeration algorithms for minimum feedback vertex set in undirected graphs using a maximum-induced-forest formulation and measure-and-conquer analysis. It is relevant to this project because the dictionary-kernel literature reduces `MinSets` to feedback vertex sets, so this is part of the real algorithmic backbone behind seed extraction.

## Ghizzota_2025_EnhancingLinguisticResourcesDiachronic  (linked-data, diachrony, lexical-graphs, multilingual)
This paper integrates lexical, etymological, bibliographic, and temporal information into a linked-data lexical knowledge graph for diachronic analysis. It matters for this project because any serious attempt to compare kernels across languages or across time will need this kind of identifier-rich graph infrastructure.

## Harnad_1990_SymbolGroundingProblem  (semantics, symbol-grounding, cognitive-science, dictionary-graphs)
Harnad argues that purely symbolic systems cannot obtain intrinsic meaning from definitions alone and frames this as the symbol grounding problem. He proposes a hybrid architecture in which elementary symbols are grounded in sensorimotor category representations and higher-order symbols are built compositionally on top of that grounded base. This is foundational for this project because it defines the limit of any purely graph-theoretic dictionary kernel: recursive definability is not yet grounding.

## Kay_1962_RulesInterpretationComputationSemantics  (semantics, history, machine-translation, lexical-graphs)
Kay argues that natural-language semantics should be handled by explicit computational rules of interpretation rather than being left as an informal residue after syntax. The paper proposes a small qualification network and ties semantic computation directly to machine translation. For this project, it is an early ancestor of treating meaning as a structured computational graph.

## Levary_2012_LoopsSelfReferenceDictionaries  (dictionary-graphs, loops, semantics, lexical-growth)
This paper studies loops in dictionary definitions and argues that short definitional cycles are semantically meaningful rather than mere artifacts. It is especially important for this project because it shifts attention from only breaking cycles to also understanding what the cycles themselves represent.

## Massé_2008_MeaningGroundedDictionaryDefinitions  (dictionary-graphs, graph-theory, semantics, symbol-grounding)
This paper formalizes dictionary definitions as a directed graph and proves that grounding sets are exactly feedback vertex sets. It introduces the grounding kernel as the recursively irreducible definitional subgraph and argues that real learner dictionaries such as LDOCE should contain a much smaller grounding core than their full defining vocabulary suggests. This is a foundational methods paper for implementing real kernel extraction.

## Masterman_1961_SemanticMessageDetectionInterlingua  (history, semantics, machine-translation, interlingua)
This paper argues that machine translation needs a true semantic discipline and proposes a small interlingual semantic system built from minimals, connective operations, and tree/lattice structures for detecting message-level semantic correspondences. It is relevant to this project as a genuine early ancestor of the idea that a compact semantic basis might support broader compositional meaning.

## Picard_2013_HiddenStructureFunctionLexicon  (dictionary-graphs, graph-theory, psycholinguistics, semantics)
This paper sharpens the distinction between Kernel, Core, Satellites, and Minimal Grounding Sets in dictionary graphs and argues that these components have different psycholinguistic functions. It is the bridge between the early graph formalization of grounding sets and the later larger-scale latent-structure analyses, especially by treating Satellite words as functionally important rather than just peripheral.

## Schindler_2025_LGDELocalGraph-basedDictionaryExpansion  (lexical-graphs, graph-theory, dictionary-expansion, embeddings)
This paper proposes `LGDE`, a local graph-based method for expanding a seed dictionary by constructing a cKNN semantic graph over domain-specific word embeddings and extracting overlapping local communities with diffusion-based community detection. It is relevant to this project because it offers a concrete modern method for growing a bootstrap seed outward once an initial kernel or expert-selected vocabulary exists.

## Sparck-Jones_1965_ExperimentsSemanticClassification  (history, semantics, thesaurus, lexical-graphs)
Sparck Jones argues that semantic classification is necessary for resolving multiple meaning in machine translation and proposes building thesaurus-like classes from contextual substitution patterns and semantic relations. It is an early but remarkably direct ancestor of modern lexical graph thinking, especially for this project’s broader goal of structured semantic organization.

## Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks  (semantic-networks, graph-theory, psycholinguistics, semantics)
This paper shows that large semantic networks built from word association, Roget’s Thesaurus, and WordNet share sparse small-world and scale-free structure, and proposes a differentiation-based growth model that reproduces those statistics. It is relevant to this project because it provides the broad semantic-network baseline against which dictionary-kernel structure should be judged.

## Vincent-Lamarre_2014_LatentStructureDictionaries  (dictionary-graphs, semantics, graph-theory, symbol-grounding, psycholinguistics)
This paper models dictionaries as directed graphs and discovers a latent structure consisting of the Rest, Kernel, Core, Satellites, and many possible MinSets. It shows that these graph components correlate with frequency, age of acquisition, and concreteness, and interprets MinSets as candidate grounding vocabularies in a dual-code sensorimotor/symbolic model. This is the core methods paper for the project because it turns the recursive-seed idea into a concrete graph problem.
