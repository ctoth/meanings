# Research prompt: Hanski's core–satellite hypothesis (ecology, 1982) ↔ the dictionary Core/Satellite decomposition (2014)

**Date:** 2026-05-12
**Type:** deep-research prompt (literature-based discovery / Swanson link)
**Status:** unstarted

## Context you need first

Read the paper notes for `Vincent-Lamarre_2014_LatentStructureDictionaries` and `Picard_2013_HiddenStructureFunctionLexicon`, plus `reports/synthesis-minimal-core-to-expansion.md` and `reports/graph-object-definitions.md`. The dictionary-graph literature decomposes the definition graph into `Rest`, `Kernel`, **`Core`**, and **`Satellites`** — Core words are central and reach/are reached by much of the graph; Satellite words hang off the Kernel, individually peripheral but (per Picard) functionally important in aggregate.

Independently, in ecology: **Ilkka Hanski's core–satellite species hypothesis (1982, *Oikos*)** — a metapopulation model in which species split into "core" species (regionally common, occupy most sites, low extinction risk) and "satellite" species (regionally rare, occupy few sites, high local extinction risk), driven by a colonization–extinction dynamic with a positive feedback (the "rescue effect") that produces a bimodal distribution of site occupancy. Decades of follow-up: Hanski & Gyllenberg, the core-satellite debate, bimodality-of-occupancy literature, metapopulation theory generally.

## The hypothesis to investigate

These two literatures use **the same two words for structurally analogous roles** and — as far as preliminary checking shows — **do not cite each other**. That is the canonical Swanson signature (identical vocabulary, disjoint literatures). The substantive bet: Hanski's literature has a *generative stochastic mechanism* (colonization–extinction with rescue effect) producing the core/satellite split, whereas the lexical literature has only a *static graph decomposition*. If the mechanism transfers, then a word's Core-vs-Satellite status should be the stationary outcome of a dynamic process over historical time — words "colonizing" and going "locally extinct" from the *defining vocabulary* of a dictionary across editions / across the diachronic record.

## What to find and produce

1. **Confirm disjointness.** Citation search both directions. Does any lexical-graph / psycholinguistics paper cite Hanski, metapopulation theory, or the core-satellite hypothesis? Does any ecology paper cite Vincent-Lamarre, Massé, Picard, or dictionary-graph work? Report nearest misses (e.g., anyone applying metapopulation models to language change, or species-abundance models to word frequency — Zipf-adjacent work may be a partial bridge).
2. **Align the formal objects.** Hanski's state variable is *fraction of sites occupied*; the lexical analogue is *fraction of definitions a word appears in* (its out-degree as a "definer", roughly the satellite-attachment structure). Hanski's split is *bimodality of occupancy*; check our existing OEWN outputs (`reports/oewn-*-layers.json`, the kernel summaries) — **is the definer-degree / centrality distribution actually bimodal?** This is a concrete, immediately runnable check against data we already have.
3. **Port the dynamic.** Sketch a colonization–extinction model for the defining vocabulary: a word "colonizes" a definition when a lexicographer adopts it; "goes extinct" when revised out; rescue effect = common defining words are more likely to be reached for. Does this predict the observed Core/Satellite split? What data would test it — historical dictionary editions (OED across editions, Webster's editions), or the diachronic resources in `Ghizzota_2025`?
4. **Pull the other direction too.** Does the *graph* perspective give ecology anything? E.g., the Kernel (feedback vertex set) has no obvious ecological counterpart — is there one? ("What's the minimal set of species you'd have to seed to regenerate the community"?) Note it if so; this is a bonus, not the main line.
5. **Falsifiers.** If the lexical degree/centrality distributions are *not* bimodal, the analogy to Hanski's specific mechanism weakens sharply (though the static decomposition stands). If "core/satellite" in the lexical papers was itself borrowed from ecology and the disjointness is illusory, report that and stop. State both clearly.

## Deliverable

A markdown report in `reports/` (suggest `reports/swanson-core-satellite-findings.md`): disjointness evidence, the formal alignment table, **results of the bimodality check on existing OEWN outputs** (this is the highest-value concrete deliverable — actually look at the JSON), the ported colonization–extinction sketch with the data needed to test it, falsifiers, and a proposed paper (title/venue/thesis/key figure). Web access expected — read Hanski 1982 *Oikos* and at least one modern review of the core-satellite / occupancy-bimodality debate.
