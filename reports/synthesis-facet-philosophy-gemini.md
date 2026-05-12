# Synthesis Facet: Philosophy (Gemini Draft)

**Date:** 2026-05-12
**Status:** Independent Draft (Parallel to Codex)

## 1. The Grounding Limit: Recursive Definability is not Meaning

The project’s graph-theoretic core rests on the formalization of the **symbol-grounding problem** (Harnad 1990). The "Chinese-Chinese dictionary-go-round" serves as the primary intuition pump: a monolingual dictionary is a closed symbolic system where tokens are defined only by other tokens. Our implementation of the **grounding kernel** (Massé 2008) and **MinSets** (Vincent-Lamarre 2014) identifies the minimal set of word-senses required to break every cycle and render the lexicon a directed acyclic graph (DAG). 

However, we must remain skeptical of the claim that a MinSet *is* a set of semantic primitives. As Harnad argues, recursive sufficiency is not intrinsic meaning. The graph can tell us which nodes are topologically "foundational" (the Kernel and its feedback vertex sets), but it cannot provide the non-symbolic sensorimotor link required to fix those symbols to referents. The dictionary-as-graph identifies the **internal definitional closure** of the lexicon; it identifies where the "grounding" *must* occur if the system is to be grounded at all, but the graph itself remains ungrounded.

## 2. Foundationalism, Coherentism, and the Yoneda Scope

The project adjudicates the tension between **foundationalism** (the Kernel must be grounded in sensorimotor experience) and **coherentism** (meaning is the emergent property of the entire mutually-supporting web). 

- **The Foundationalist Move:** Cutting the Kernel and extracting a MinSet. This treats loops as "noise" or "defects" to be resolved by external anchors.
- **The Coherentist Move:** Levary’s (2012) observation that "loops are signal." Short loops are semantically coherent and historically aligned; they represent tightly coupled conceptual neighborhoods.

We reconcile these using **Dung’s argumentation semantics**. The "Rest" of the dictionary (the acyclic portion) corresponds to the **grounded extension**—the part whose status is skeptically determined by the base. The Kernel’s loop ecology corresponds to the **preferred/stable extensions**—candidate self-consistent stances that remain "undecided" without a seed.

This maps directly to the **Yoneda Lemma ↔ Harnad** confrontation. Yoneda asserts that an object is exhaustively determined by its relations to others, implying no "internal" residue. Harnad asserts a non-symbolic residue is mandatory. We find these **compatible via a scope distinction**: Yoneda determines identity *within* a fixed category; Harnad points out that for a cognitive agent, the category itself is not given a priori but must be "grounded into existence." The symmetry rider is essential: a thoroughgoing structuralist who denies Harnad's residue must face **Benacerraf’s access problem** in mathematics. If concepts are just roles, then numbers are just roles, and we are left with "structures without structures."

## 3. The Lexicographer’s Confound: Regression as a Weak Instrument

Our psycholinguistic regression (`reports/psycholinguistic-regression-findings.md`) provides a rigorous check on the "residue" claim. The finding that the psycholinguistic feature block (concreteness, AoA, frequency) adds only **≤0.01 incremental R-squared/AUC** over the structural block (degree, PageRank, SCC membership) is a significant result. It refutes the **strong claim** of a large, independent sensorimotor signal that the definitional graph fails to capture. 

However, we must avoid concluding that "meaning is Yoneda-complete." The results are likely a victim of the **lexicographer’s confound**: dictionaries are written *for learners*. Lexicographers deliberately use concrete, early-acquired, and frequent words as definers *because* they expect readers to know them. This editorial policy **creates** the structural features (high out-degree, shallow layer) from the psycholinguistic salience. The structure doesn't "replace" the grounding; it **screens it off**. The regression signature for "meaning is relational" and "the graph was built to match psycholinguistic reality" is identical.

## 4. Mechanized Grounding: The `gunray` Demonstration

We have mechanized the grounding problem in executable code using the `gunray` (DeLP) engine. In this model:
- A circular, ungrounded definition (`a -< b; b -< a`) results in a status of **`UNDECIDED`**.
- This is not a "failure" or an "error," but a formal representation of Harnad’s ungrounded regress.
- Adding a single grounding fact (`fact: b`) immediately flips the dependent node `a` to **`YES`**.

This provides a "dialectical tree" for lexical meaning: the Kernel is the `UNDECIDED` substrate of the lexicon; MinSet selection is the act of providing the "warrants" that allow the rest of the dictionary to be "grounded" into determinacy.

## 5. Epistemological Invariants: Not Merely Engineering Hygiene

Finally, the project adopts the epistemological stance outlined in the **Upgoer identity-cluster notes**:
- **Form is not Sense:** A surface word (e.g., `no`) is not its semantic role (e.g., `Nobelium` vs. negation).
- **Referential meaning is not Indexical signal:** `wash` and `warsh` denote the same act but carry different speaker metadata.
- **Correlation is not Authority:** LLM embeddings and corpus statistics are **evidence**, not the ground truth of meaning.

This is a rejection of "vector soup" architectures. We treat the lexicon as a **typed, inspectable, and falsifiable system**. The use of argumentation frameworks and identity clusters is not just an implementation choice; it is an epistemological commitment to the idea that meaning is a structured, defensible relationship, not an amorphous cloud of high-dimensional proximity. 

**Over-claim Warning:** The project currently succeeds in identifying **definitional necessity**, not **semantic sufficiency**. We can show which words are *required* to define the others, but we cannot yet prove that knowing the MinSet *suffices* for a human-like understanding of the "Rest." We have solved the graph-theoretic non-circularity problem, but the "meaning" of the seed words themselves remains a black box.
