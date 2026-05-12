# Research prompt: "Meaning has no gold standard" — the symbol-grounding problem as the numéraire problem

**Date:** 2026-05-12
**Type:** deep-research prompt (literature-based discovery / Swanson link)
**Status:** unstarted

## Context you need first

Read `reports/synthesis-minimal-core-to-expansion.md` and the paper notes for `Massé_2008_MeaningGroundedDictionaryDefinitions`, `Picard_2013_HiddenStructureFunctionLexicon`, `Vincent-Lamarre_2014_LatentStructureDictionaries`, and `Harnad_1990_SymbolGroundingProblem`.

The short version: a dictionary is a directed graph (word → words used to define it). Following definitions far enough produces cycles. The set of words you must "already know" — ground from outside the dictionary — before everything else becomes reachable is a *feedback vertex set* of that graph. Massé proved grounding sets = minimum feedback vertex sets; Vincent-Lamarre showed real dictionaries decompose into `Rest → Kernel → Core → Satellites` with *many possible* minimal grounding sets ("MinSets"), no canonical one. Harnad's symbol-grounding problem says: recursive definability is not meaning; a purely symbolic system needs an exogenous anchor.

## The hypothesis to investigate

The structure "a relational value system with no intrinsic content, where 'grounding' is an *arbitrary choice of anchor* rather than a property any element possesses" is **the same structure monetary economics has theorized for 150+ years**, and the two literatures do not cite each other. Specifically:

- A **grounding set** of a dictionary ≈ a **commodity standard** (gold standard) for a currency: an element designated as exogenously anchored so the rest of the system can be defined relative to it.
- Vincent-Lamarre's observation that there are **many MinSets, none privileged** ≈ the classical result that **any commodity can serve as the numéraire** — and Sraffa's **standard commodity** as the attempt to find a least-arbitrary one.
- Going **off the gold standard** (Nixon shock, 1971) ≈ discovering that the dictionary graph has **no Kernel that bottoms out** — value/meaning floats on pure relation, stabilized only by a fixed point (general equilibrium ↔ the graph's cyclic core).
- The **Bitcoin-maximalist vs MMT** argument ≈ Harnad-vs-distributionalist: does the system *require* an exogenous anchor, or is it anchorless and fine?

## What to find and produce

1. **Map the correspondences precisely.** Build a table: dictionary-kernel concept ↔ monetary-economics concept ↔ shared formal object (if any). Be honest where the analogy breaks (e.g., money has *flows* and *dynamics*; the dictionary graph as studied is static — is that a real disanalogy or just an unexploited extension?).
2. **Confirm the literatures are genuinely disjoint.** Search citation graphs both directions: do any symbol-grounding / lexical-graph papers cite Walras, Sraffa, Patinkin, Fisher, Hahn, monetary-economics work on the numéraire? Do any economics papers on numéraire choice / commodity standards cite Harnad, Massé, Vincent-Lamarre, or the dictionary-graph literature? Report the closest near-misses (e.g., anyone using "semantics" and "money" metaphorically).
3. **Identify what economics could lend back.** Candidates to evaluate: (a) general-equilibrium existence proofs (Arrow–Debreu fixed point) as a model for why a cyclic definitional core is *self-consistent* rather than vicious; (b) Sraffa's standard commodity as an algorithm for picking a *canonical* MinSet; (c) the theory of *seigniorage* / which anchor is cheapest to maintain, mapped onto "which grounding vocabulary minimizes total definitional length / cognitive cost"; (d) monetary history as a natural experiment in what happens when you swap or remove the anchor.
4. **State the falsifiers.** What would show this is a shallow pun rather than a real Swanson link? (E.g., if the FVS structure has no economic counterpart because money's relational structure is a complete graph / market-clearing system, not a sparse digraph — assess this.)
5. **Name the paper that should exist.** One paragraph: title, venue, thesis, the one figure or theorem that carries it.

## Deliverable

A markdown report in `reports/` (suggest `reports/swanson-money-numeraire-findings.md`): correspondence table, citation-disjointness evidence, ranked list of transferable tools with feasibility notes, falsifiers, and the proposed paper. Cite everything; verbatim quotes for the load-bearing claims. Web access expected — go read Sraffa's *Production of Commodities by Means of Commodities*, Patinkin on the numéraire, and the modern monetary-economics treatment of standards.
