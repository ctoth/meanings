# Research prompt: Lexical grounding sets ↔ structural controllability and driver nodes

**Date:** 2026-05-12
**Type:** deep-research prompt (literature-based discovery / Swanson link)
**Status:** unstarted

## Context you need first

Read the paper notes for `Massé_2008_MeaningGroundedDictionaryDefinitions`, `Vincent-Lamarre_2014_LatentStructureDictionaries`, and `Fomin_2008_MinimumFeedbackVertexSetProblem`, plus `reports/graph-object-definitions.md`. Key fact: a dictionary's **grounding set = a minimum feedback vertex set (FVS)** of the definition digraph — the smallest node set whose removal makes the graph acyclic, equivalently the smallest set you must "know from outside" to bootstrap the rest by recursive definition unrolling.

Independently, in network science: **structural controllability of complex networks** — Liu, Slotine & Barabási, *Nature* 2011, "Controllability of complex networks." For a linear-dynamical network, the minimum set of **driver nodes** you must directly actuate to steer the whole system to any state is given by a **maximum-matching** computation on the digraph (the unmatched nodes are the drivers). Large follow-up literature: minimum-input theorems, control profiles, controllability of biological/neuronal/social networks, energy-of-control, target controllability.

## The hypothesis to investigate

Both fields ask the *same shaped question* — **"what is the minimum set of nodes from which you control / reach / generate the entire directed network?"** — but they answer it with **different combinatorial objects**: lexical grounding uses **feedback vertex set**; network control uses **maximum matching / unmatched nodes**. The literatures appear disjoint. The payoff of connecting them is a real conceptual result, not just a metaphor:

- Either FVS and the driver-node set coincide / bound each other on the relevant graph classes — in which case "grounding a vocabulary" *is* "controlling a network" and decades of control-theory machinery (energy, target control, robustness) imports directly; or
- they genuinely diverge — in which case the difference *characterizes* what is special about definitional grounding vs dynamical control (e.g., grounding cares about *acyclicity / well-foundedness*, control cares about *reachability under integrator dynamics*), which is itself a publishable clarification of what "grounding" means.

## What to find and produce

1. **Confirm disjointness.** Citation search both directions: do any symbol-grounding / lexical-graph / dictionary papers cite Liu–Slotine–Barabási or structural-controllability work? Do any network-controllability papers cite Massé, Vincent-Lamarre, Harnad, or dictionary-graph work? Nearest misses (e.g., anyone applying controllability to *semantic* networks, WordNet, or language graphs)?
2. **Compare the combinatorics directly.** On the same digraph: minimum FVS vs the set of unmatched nodes under maximum matching. Are there inclusion relations? Bounds (e.g., |drivers| ≤ |FVS| + something)? On a DAG, FVS = ∅ but driver nodes ≠ ∅ — so they already differ; characterize *how*. Look for any existing graph-theory result relating FVS to maximum matching / Dilworth-type structure. Worked small examples.
3. **Run it on our data.** We already build OEWN definition digraphs (`src/meanings/wordnet_pipeline.py`, outputs in `reports/oewn-*-summary.json` / `*-layers.json`). Compute the maximum-matching driver-node set on the same graph for which we compute the kernel/FVS-seed, and compare: sizes, overlap, where they disagree (which words are "drivers" but not "grounders," and vice versa). This is a concrete coding deliverable — propose it as a follow-up task with the exact function to add.
4. **Inventory what control theory lends.** Rank by usefulness: target controllability ("ground only the subvocabulary needed to define *this* domain" — directly relevant to the LGDE expansion line in `Schindler_2025`), control energy ("cost of grounding," cf. age-of-acquisition correlates), control profiles (source/external-dilation/internal-dilation classification of why a node is a driver — does it map onto Kernel/Core/Satellite roles?), robustness of control to edge removal (stability of MinSets under dictionary revision).
5. **Falsifiers / scope limits.** Linear-integrator dynamics is the wrong model for "meaning unrolling" (which is more like reachability / fixed-point logic programming). Is the controllability framing only a structural-graph analogy, with the *dynamics* part inapplicable? Say so plainly; the structural part may still be the useful 80%.

## Deliverable

A markdown report in `reports/` (suggest `reports/swanson-controllability-findings.md`): disjointness evidence; FVS-vs-driver-nodes comparison with worked examples and any graph-theory bounds found; **proposed code task + predicted result** for running maximum-matching on the existing OEWN graphs; ranked transferable tools; falsifiers; proposed paper (title/venue/thesis/key result). Web access expected — read Liu–Slotine–Barabási 2011 and at least one critique/extension (e.g., the "few inputs / one input" debates, target controllability papers).
