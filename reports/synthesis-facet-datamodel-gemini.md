# Project Synthesis: Data Model Facet (Draft Gemini)

## 1. The Typed Layered Object Model

The current `lemma::pos` graph is a coarse proxy that conflates distinct linguistic and semantic realities. To resolve WordNet-level artifacts and produce a human-validated "Up-Goer" vocabulary, the project requires a five-layer object model.

### 1.1 The Layers

1.  **Form:** The raw surface string or pronunciation (e.g., `color`, `colour`, `warsh`, `No`, `no`).
2.  **Token-Occurrence:** A form observed in a specific context (a sentence or gloss).
3.  **Reading:** the contextually resolved interpretation of a token-occurrence (e.g., the specific role/parse/sense assignment).
4.  **Sense:** A dictionary-level semantic unit (e.g., a Synset member in OEWN). This is the node level for the Bipolar Argumentation Framework.
5.  **Identity-Cluster (IC):** The referential unit. Multiple senses (from the same or different forms) merge into an IC when they denote the same semantic object (e.g., `color` and `colour` senses merge here).

### 1.2 Record Structure & Metadata

Each record in the model must carry specific metadata to allow for policy-based filtering and admission.

*   **Construction:** Identifies multi-token units (phrases, idioms) whose meaning is non-compositional.
*   **Metadata Facets:** Dialect, Register, Domain, Spelling System, Pronunciation, Geography, Technical Field, and Source Provenance.
*   **Lexicality-Tag Enum:**
    *   `lexical-word`: Ordinary human language primitive.
    *   `symbol-code`: e.g., chemical symbols, currency codes.
    *   `abbreviation`: Shortened forms.
    *   `proper-name`: Entities (people, places).
    *   `taxon`: Biological classifications.
    *   `chemical`: Specific chemical names (distinct from symbols).
    *   `technical-term`: Domain-specific jargon.
    *   `phrase` / `idiom`: Multi-word constructions.
    *   `uncertain`: Default for unclassified or ambiguous nodes.

## 2. Relations and Graph Dynamics

The data model is not a static list but a dynamic system of support and conflict.

### 2.1 Edge Types

*   **Supports (Definition Edges):** Directed edges between resolved **Sense** nodes. `A supports B` means `A` appears in the definition of `B`. This forms the Bipolar AF.
*   **Attacks (Conflict Edges):** Symmetrical edges between competing **Senses** of a single **Form** (polysemy). Context or lexicality-tags provide arguments to resolve (defeat) these attacks.
*   **Identity-Cluster Merge:** A belief-merge (per Konieczny–Pino Pérez) over sense clusters. Crucially, this is **not** canonicalization; the original forms are preserved, and each merge carries explicit provenance (the rationale for the semantic identity).

### 2.2 Referential vs. Indexical Meaning

Denotation (Referential Meaning) belongs to the Identity Cluster. Indexical information (Region, Class, Dialect) belongs to Metadata. `wash` and `warsh` denote the same act (same IC) but index different speaker profiles (different Metadata). The base referential graph remains clean of indexical noise.

## 3. Mapping to Sibling Tools

The data model is the implementation surface for formal argumentation and belief theory.

*   **Argumentation Framework (ADF/Bipolar AF):** The definition graph over **Sense** nodes. Grounded semantics identifies the acyclicly-determined vocabulary; stable extensions identify candidate MinSets.
*   **Admission as Defeasible Theory:** The "Admission Policy" is a `gunray`-style theory. A form is admitted to the Human Up-Goer list if its lexicality is `lexical-word`, it maps to an admitted IC, and its support structure is warranted.
*   **Belief-Set Merging:** Used for IC formation. Merging `center` and `centre` is a belief-merge operation where the "belief" is their semantic equivalence.
*   **Correlation as Evidence:** LLM embeddings and corpus statistics provide **Arguments** in the defeasible theory, not ground truth. The dialectical tree (the "explain" facility) provides the rationale for any merge or exclusion.

## 4. Deliverable Surfaces

1.  **Strict Typed Seed:** The feedback-vertex set (MinSet) restricted to Identity Clusters tagged as `lexical-word`. This is the graph-theoretic core.
2.  **Human Up-Goer List:** The admitted extension of the Admission Theory. This includes all aliases and forms that map to the admitted Core ICs, filtered for register and domain.

## 5. Falsifiable Prediction: The Sense-Level Shrinkage

The current lemma-level Kernel is artifact-inflated. The self-loop fix grew the Kernel (12,853 to 18,151) by pulling in 3,413 gloss self-loops. 

**Prediction:** Moving to a sense-resolved graph will **shrink** the Kernel. Many lemma-level self-loops (e.g., `violin::n` glossed using "violin") are artifacts of coarse POS-tagging. In a sense-resolved model, these references resolve to specific senses or the IC, breaking the self-loop and allowing the node to be stripped from the Kernel. If the sense-level Kernel remains large, it indicates that the circularity is a real semantic property of the lexicon, not a parsing artifact.
