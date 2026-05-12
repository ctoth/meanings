# Research prompt: Is meaning Yoneda-complete? Category theory's "objects are their relations" vs Harnad's grounding residue

**Date:** 2026-05-12
**Type:** deep-research prompt (conceptual / cross-disciplinary confrontation)
**Status:** unstarted

## Context you need first

Read the paper notes for `Harnad_1990_SymbolGroundingProblem` and `Massé_2008_MeaningGroundedDictionaryDefinitions` / `Vincent-Lamarre_2014_LatentStructureDictionaries`, plus `reports/synthesis-minimal-core-to-expansion.md`.

Two doctrines that have, as far as preliminary checking shows, never been put in the same room:

- **The Yoneda lemma** (category theory): an object `A` in a category is determined up to isomorphism by its *bundle of relations* to all other objects — the functor `Hom(–, A)` (equivalently `Hom(A, –)`). Slogan versions: "an object is what it does," "to know a thing is to know its relationships with all other things," "mathematics has no nouns, only verbs." There is **no residue** beyond the relational structure; the relations are *constitutive*, exhaustively.
- **Harnad's symbol-grounding problem**: a purely symbolic system — symbols defined only via other symbols — cannot have intrinsic meaning. There *is* a residue: meaning requires that elementary symbols be grounded in non-symbolic (sensorimotor) category representations; the relational/definitional structure is necessary but not sufficient. Recursive definability ≠ meaning.

These appear to be in direct contradiction about the same claim — *"is X fully constituted by its relations to other X's?"* — Yoneda says yes (for objects in a category), Harnad says no (for symbols / words). Yet the symbol-grounding literature does not engage category theory, and the categorical-semantics / "structuralism in mathematics" literature does not engage Harnad.

## The hypothesis / question to investigate

It is not obvious this is a *real* contradiction rather than a category error (pun acknowledged). The research job is to determine which:

- **Resolution A — different categories.** Yoneda determines `A` *within a fixed category C* — i.e., relative to a pre-given universe of objects and morphisms. Harnad's point is precisely that the "category" (the universe of available relata) is not given a priori for a cognitive agent — it has to be *grounded into existence*. So Yoneda presupposes exactly what Harnad says is missing: the ambient category. If so, the two are compatible and the synthesis is "grounding = choosing/constructing the base category; Yoneda then takes over." This would also reframe MinSets: a MinSet is a generating set for the category, and the arbitrariness-of-MinSets ↔ the many equivalent presentations of the same category.
- **Resolution B — genuine disagreement about adequacy.** If one holds that an agent's conceptual universe just *is* whatever relational structure its symbols instantiate (a thoroughgoing structuralism / functional-role semantics), then Yoneda says that's all there is and Harnad is wrong; conversely if Harnad is right, then mathematical structuralism owes an account of how the ambient category gets its "content" — i.e., math has a grounding problem too (cf. Benacerraf, "What numbers could not be"; the access problem in philosophy of mathematics).
- **Resolution C — the dictionary graph is the worked example that adjudicates.** A dictionary digraph *is* (almost) a small category-ish structure: objects = words, "morphisms" = appears-in-definition-of. Vincent-Lamarre's empirical finding — that graph layers (Kernel/Core/Satellite) *correlate with* age-of-acquisition, concreteness, frequency — is evidence that something *outside* the relational structure (when/how words are learned, how perceptually concrete they are) is doing explanatory work the pure relations don't capture. That's a thumb on the scale for Harnad. Assess how strong this evidence actually is.

## What to find and produce

1. **Confirm disjointness.** Search both directions: any symbol-grounding / cognitive-science / lexical-graph work citing Yoneda, category-theoretic semantics, "structuralism" in the categorical sense, or "mathematics has no nouns"? Any categorical-semantics / structuralism-in-philosophy-of-math work citing Harnad or the symbol-grounding problem? Adjacent fields to check: categorical compositional distributional semantics ("DisCoCat", Coecke–Sadrzadeh) — do *they* connect their category theory to grounding? Conceptual-spaces (Gärdenfors)? Inferentialism / conceptual-role semantics (Brandom, Block) — that literature *is* about "meaning = relations," does it know about Yoneda?
2. **State the strongest version of each side** and the precise proposition they disagree about. Force it down to a single sentence with quantifiers.
3. **Adjudicate via the dictionary graph.** Use our OEWN outputs and the annotation overlays (`src/meanings/annotations.py`, the AoA/concreteness work referenced in `reports/annotation-sources.md`): how much variance in "which layer a word lands in" is explained by *purely structural* graph features vs by *extra-graph* features (concreteness, AoA, sensory ratings)? If extra-graph features add real predictive power *given* the structure, that's empirical weight against Yoneda-completeness of meaning. Specify the regression / analysis precisely; note whether the data to run it already exists in the repo.
4. **Land a verdict.** A → "compatible, here's the synthesis (grounding = constructing the base category)." B → "genuine fight, here's who owes what." C → "the data says X." Don't hedge into mush; pick the best-supported reading and say why.
5. **Proposed output paper.** Title/venue/thesis. Plausible venue: a philosophy-of-cognitive-science or applied-category-theory venue; the DisCoCat community may be the natural home.

## Deliverable

A markdown report in `reports/` (suggest `reports/swanson-yoneda-harnad-findings.md`): disjointness evidence; the one-sentence statement of the disagreement; the empirical adjudication design + whatever can be run now on existing repo data, with results; the verdict with reasoning; the proposed paper. Web access expected — read a clean exposition of Yoneda-as-philosophy (e.g., the "Yoneda perspective" expositions, Marquis on categorical structuralism), Harnad 1990, and at least one DisCoCat paper to see how close that community already is to this question.
