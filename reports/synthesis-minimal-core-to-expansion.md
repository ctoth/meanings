# Synthesis: Minimal Core to Expansion

**Date:** 2026-04-02

## Purpose

This note synthesizes the current collection around one question:

How do we get from the old dream of a small semantic basis to a modern, testable pipeline for lexical kernels and outward dictionary growth?

The core line is:

`Masterman 1961 -> Harnad 1990 -> Massé 2008 / Picard 2013 / Vincent-Lamarre 2014 -> LGDE 2025 / OpenGloss 2025`

This is not a story of steady improvement along one method. It is a sequence of different answers to related problems:

- `Masterman`: Can a small semantic stock support message-level analysis?
- `Harnad`: Why a symbolic stock alone is not grounded meaning.
- `Massé/Picard/Vincent-Lamarre`: How to formalize recursive definability in real dictionaries as a graph problem.
- `LGDE`: How to grow a small seed into a useful domain dictionary.
- `OpenGloss`: How to generate a large lexical resource quickly and consistently.

## Executive Verdict

The project now has a clean split between three layers:

1. `Philosophical ancestry`
   `Masterman` is worth keeping as a genuine precursor, but not as a direct implementation guide.

2. `Kernel science`
   `Massé`, `Picard`, and `Vincent-Lamarre` are the central scientific spine for extracting non-circular lexical cores.

3. `Growth and infrastructure`
   `LGDE` is the strongest paper for expanding a seed outward.
   `OpenGloss` is useful as a large lexical graph substrate, not as a theory of semantic minimality.

If we build code, the right architecture is:

- use `Massé/Picard/Vincent-Lamarre` to extract `Kernel`, `Core`, `Satellites`, and candidate `MinSets`
- use `Levary` to inspect short loops rather than only cutting them away
- use `LGDE` to expand from a chosen seed into a working dictionary
- treat `OpenGloss` as an optional later corpus/resource target

## Stage 1: Masterman 1961

### What survives

- The insistence that semantics must be modeled explicitly rather than left as residue after syntax.
- The ambition to build a compact semantic basis and compose richer meanings from it.
- The idea that there is a difference between surface sentence form and deeper message structure.

### What does not survive cleanly

- The specific tree/lattice formalism.
- The hand-built minimal vocabulary as if it were a stable universal basis.
- The lack of empirical validation and the dependence on bespoke symbolic machinery.

### Best reading of Masterman

Masterman is not “already doing kernels,” and she is not doing graph-theoretic non-circularity. What she is doing is earlier and looser:

- a small semantic basis
- explicit compositional operators
- a reduced interlingua
- a hope that semantic structure can be recovered and compared above raw words

That makes her a real ancestor of controlled defining vocabularies, semantic primitives, and recursive lexical bases, but not a technical predecessor of `MinSet` extraction.

### Verdict

Keep `Masterman` in the main collection as historical ancestry.
Do not use her formalism as a design target for code.

## Stage 2: Harnad 1990

### What Harnad fixes

Harnad gives the decisive criticism missing from `Masterman`:

symbol manipulation inside a closed symbolic system does not by itself yield grounded meaning.

This matters because any dictionary-kernel program can otherwise overclaim. A recursively sufficient seed is not automatically a semantically primitive or grounded seed.

### Consequence for this project

The kernel project is legitimate, but only if we stay honest about what it computes:

- recursive definability
- cycle-breaking lexical bases
- candidate grounding vocabularies

not

- ultimate semantic truth
- a final set of natural primitives

### Verdict

`Harnad` is the philosophical constraint that prevents the later graph work from being misread.

## Stage 3: Massé 2008, Picard 2013, Vincent-Lamarre 2014

This is the real center of gravity.

### What Massé 2008 contributes

`Massé` is where the project becomes mathematically precise.

Main move:

- represent dictionary definitions as a directed graph
- identify grounding sets with feedback vertex sets
- define the `grounding kernel` as the recursively irreducible subgraph

This gives the first exact answer to the user’s core interest in graph-theoretic non-circularity.

### What Picard 2013 adds

`Picard` differentiates the internal anatomy:

- `Kernel`
- `Core`
- `Satellites`
- `Minimal Grounding Sets`

This matters because the kernel is not one blob. Different subregions seem to have different psycholinguistic roles.

### What Vincent-Lamarre 2014 matures

`Vincent-Lamarre` scales the framework and shows:

- kernels are small
- `MinSets` are much smaller
- there are many possible `MinSets`
- psycholinguistic gradients line up with graph structure

This is the strongest existing evidence that a small recursive backbone is real, while also showing it is not unique.

### What this stage settles

- English dictionary structure is not a pure DAG.
- It can be made DAG-like by choosing seeds that hit cycles.
- The right objects are not just “the seed” but `Kernel`, `Core`, `Satellites`, `MinSets`, and definitional hierarchies.
- A small recursive basis is possible.
- It is not unique, and it is not automatically grounded.

### Verdict

This stage defines the implementation target.
If we are serious about “bootstrap seed for English,” these papers are the direct blueprint.

## Side Correction: Levary 2012

The cleanest danger in a naïve kernel project is to treat cycles as garbage.

`Levary` blocks that mistake.

Short definitional loops are often semantically meaningful and historically coherent.

So the correct implementation stance is:

- compute `MinSets` because we need cycle-breaking seeds
- also study short loops and SCC ecology because they are semantic structure, not mere defects

This is a major correction to the reductionist temptation.

## Stage 4: LGDE 2025

### What problem it solves

`LGDE` is not about non-circularity.
It is about seed expansion.

Given a small vocabulary, how do you grow it into a more useful working dictionary without the pathologies of naive nearest-neighbor expansion?

### Why it matters here

This is the first paper in the collection that gives a plausible answer to:

“Once we have a kernel or bootstrap seed, how do we grow outward pragmatically?”

The method:

- build a local semantic graph with cKNN
- detect overlapping seed-centered communities by diffusion
- expand by semantic neighborhoods defined by graph structure, not raw cosine thresholds

### Why it is strong

- consistent benchmark wins
- good real-world result on evolving jargon-heavy discourse
- explicitly local, which is exactly what we need if global geometry is too blunt

### Limitation

It expands topical or domain dictionaries from embeddings.
It does not discover non-circular semantic cores from definitions.

### Verdict

`LGDE` should be the default outward-growth method once a seed has been chosen.

## Stage 5: OpenGloss 2025

### What problem it solves

`OpenGloss` addresses large-scale lexical resource construction:

- schema
- generation pipeline
- coverage
- consistency
- cost

It does not address minimal semantic cores.

### Why it still matters

It creates a large typed lexical graph with:

- many senses
- explicit semantic edges
- etymology
- encyclopedic context
- examples and collocations

That makes it valuable as:

- a future graph substrate
- a comparison resource
- a stress test for kernel methods on generated lexical resources

### The main caution

Its sense inventory is engineered for pedagogical usefulness and tractability, not for philosophical cleanliness.

So if we use it for kernel work, we are testing kernels on a synthetic resource with a deliberate editorial bias toward:

- broader coverage
- coarser sense granularity
- practical utility

### Verdict

`OpenGloss` belongs in the collection as infrastructure and future experiment substrate, not as a direct semantic-core paper.

## What Was Superseded

### Superseded in method

- `Masterman`’s bespoke tree/lattice interlingua as a computational method

### Superseded in framing

- any idea that a compact symbolic basis alone settles meaning, after `Harnad`

### Not superseded

- the ambition to find a small compositional basis
- the value of explicit semantic structure
- the usefulness of lexical graphs for studying recursive organization

## What the Collection Now Says

The strongest integrated claim we can now defend is:

Human lexical systems appear to contain small recursively sufficient backbones, but those backbones are multiple rather than unique, are not the same thing as grounded meaning, and can be used as practical seeds for outward lexical expansion by modern graph methods.

That is already a strong and interesting program.

## Implications for Code

The collection now supports a concrete staged implementation:

### Phase A: Kernel extraction

- choose a real English lexicon
- build a directed definitional graph
- compute SCCs
- compute `Kernel`, `Core`, `Satellites`
- compute exact or approximate `MinSets`

Primary papers:

- `Massé 2008`
- `Picard 2013`
- `Vincent-Lamarre 2014`
- `Fomin 2008` for algorithmic background

### Phase B: Loop analysis

- enumerate short loops
- inspect SCC ecology
- measure whether chosen seeds preferentially hit certain loop motifs

Primary paper:

- `Levary 2012`

### Phase C: Outward growth

- choose one seed set
- run local graph expansion from that seed
- compare naive similarity expansion versus graph-based expansion

Primary paper:

- `LGDE 2025`

### Phase D: Alternative substrates

- repeat on WordNet-like resources
- later test on `OpenGloss`
- eventually compare across languages

Primary papers:

- `Bergh 2025`
- `Ghizzota 2025`
- `OpenGloss 2025`

## Recommended Research Posture

Do not ask one paper family to do another family’s job.

- Do not ask `OpenGloss` to answer the minimality question.
- Do not ask `LGDE` to answer the non-circularity question.
- Do not ask `Masterman` to serve as a modern algorithm.
- Do not ask `MinSet` papers to solve semantic grounding fully.

Instead:

- use each layer for its real contribution
- compose them into a pipeline

## Final Recommendation

The best current synthesis is:

- `Masterman` gives the early compact-semantic-basis dream.
- `Harnad` gives the grounding limit.
- `Massé/Picard/Vincent-Lamarre` give the exact kernel science.
- `Levary` saves the loops from being treated as trash.
- `LGDE` gives the outward growth method.
- `OpenGloss` gives a large future substrate.

That is enough to stop researching in the abstract and start building.
