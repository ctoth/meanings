# Research prompt: Perron–Frobenius valuation across constitutive systems — the canonical-anchor algorithm rediscovered six times

**Date:** 2026-05-12
**Type:** deep-research prompt (literature-based discovery / Swanson link — the central one)
**Status:** unstarted

> This is the deeper bridge that prompts 1–4 (`reports/research-swanson-{1,2,3,4}-*.md`) circle without landing on. Read those first for the dictionary-kernel context; this one subsumes prompt 1's economics angle and connects to prompt 3's "what is the canonical anchor of a relational graph" question.

## Context you need first

Read the paper notes for `Massé_2008_MeaningGroundedDictionaryDefinitions`, `Vincent-Lamarre_2014_LatentStructureDictionaries`, `Harnad_1990_SymbolGroundingProblem`, and `reports/synthesis-minimal-core-to-expansion.md` and `reports/graph-object-definitions.md`. Then internalise this:

**The unifying object.** A non-negative irreducible matrix `M` has (Perron–Frobenius) a unique positive dominant eigenvalue `λ*` with a positive eigenvector `v*`, unique up to scaling. `v*` is the *self-consistent valuation the relational structure implies about itself*: "the importance/value/foundational-ness of each node is proportional to the importance of the nodes that point to it." It is a **canonical-anchor algorithm** — it picks one privileged weighting out of a system that has no intrinsic units.

This exact object has been independently rediscovered, with near-empty cross-citation, as at least:

1. **Sraffa's standard commodity** (economics, 1960) — `v*` of the augmented input–output technology matrix; `λ*` gives the standard ratio / maximum profit rate `R`. Formalised by P. Newman (1962) and Pasinetti. Predecessor: Leontief input–output analysis.
2. **LSA / latent semantic axes** (NLP, 1990s, Deerwester/Landauer) — top singular vectors of the term–context count matrix `M`; since SVD of `M` ⇔ eigendecomposition of `MᵀM` and `MᵀM` is non-negative for counts, the leading semantic dimension *is* a Perron eigenvector of the co-occurrence Gram matrix.
3. **PageRank** (web search, 1998, Page/Brin) — `v*` of the Google matrix = stationary distribution of the random-surfer Markov chain. The teleportation/damping term exists *only* to restore irreducibility so Perron–Frobenius applies.
4. **Eigenvector / Bonacich centrality** (sociology, 1972/1987) — `v*` of the adjacency matrix. Ancestors: Katz centrality (1953), Hubbell's input–output prestige (1965 — essentially PageRank-for-citations, 33 years early), Pinski–Narin influence weights (1976, eigenvector journal prestige), Kleinberg HITS (1999, singular vectors / hubs & authorities), EigenTrust (2003).
5. **Markov-chain stationary distribution** (probability) — left Perron eigenvector of the transition matrix; the ergodic theorem is Perron–Frobenius in probabilist clothing.
6. *(check whether to add)* **Estrada subgraph centrality / communicability** (`exp(M)` spectra), **DeGroot consensus / social learning** (`Mᵗ → v*` dynamics), **the dominant eigenmode in replicator / quasispecies dynamics** (Eigen), **structural balance / status spectra**.

## The hypothesis to investigate

> "Perron–Frobenius valuation" is a **convergent rediscovery across every field that studies a constitutive relational system** — economic production flows, lexical co-occurrence, hyperlink/citation structure, social influence, Markovian dynamics — and the citation graph *between* these rediscoveries is nearly empty. The thing being rediscovered is: *the way a relational system, given no external units, names its own canonical anchor.*

And the payoff specific to this repo:

- The dictionary-kernel literature picks the grounding anchor **combinatorially** — minimum feedback vertex set: discrete, NP-hard, **many tied optima** ⇒ "MinSets, none privileged" ⇒ the arbitrariness that Harnad's grounding-residue worry sits on top of.
- The Perron lineage picks the anchor **spectrally** — `v*`: continuous, polynomial-time, **unique** whenever the graph is irreducible.
- **Claim to test:** the Perron eigenvector of the definition graph is a canonical *soft grounding vocabulary* — a real-valued "how foundational is this word" score with **no ties to break** — and it stands to the combinatorial MinSet exactly as Sraffa's standard commodity stands to "pick any numéraire." It *dissolves* the which-MinSet problem rather than solving it.
- **And the two pictures compose.** Perron–Frobenius needs irreducibility = strong connectivity. The dictionary graph isn't strongly connected — but its **Kernel is exactly the strongly-connected cyclic core** and the **Rest is the reducible DAG part** the recursive-unrolling story already handles. So: run Perron–Frobenius *on the Kernel* for canonical within-core weights; handle the Rest combinatorially. The Kernel/Rest decomposition is precisely the preprocessing that says *where the spectral method is licensed*. PageRank's damping is the blunt global version of the same irreducibility fix.

## What to find and produce

1. **Build the rediscovery table.** Columns: field · name of the construct · year/originator · the exact matrix `M` · what `v*` is interpreted as · what `λ*` is interpreted as · key formalisation reference. Be precise about which are *literally* Perron eigenvectors (Bonacich, PageRank-without-damping on a strongly connected graph, Sraffa standard commodity) vs *spectrally adjacent* (LSA = singular vectors of a possibly-rectangular non-negative matrix; HITS = SVD; subgraph centrality = full spectrum). The distinctions matter — don't paper over them.
2. **Measure the disjointness.** Citation search across the cluster: does the LSA/distributional-semantics literature cite Sraffa, Leontief, or input–output economics? Does PageRank's lineage cite Bonacich/Hubbell/Pinski–Narin (some does — quantify how much, and how late)? Does *any* symbol-grounding / dictionary-graph paper cite *any* of: PageRank, eigenvector centrality, Sraffa, Markov stationary distributions? Report the bridges that *do* exist (e.g., the bibliometrics ↔ web-search bridge is partial; econ ↔ NLP looks empty) and the gaps that don't.
3. **Run it on our data — this is the headline deliverable.** We build OEWN definition digraphs (`src/meanings/wordnet_pipeline.py`; outputs in `reports/oewn-*-summary.json`, `*-layers.json`; kernel/SCC machinery in `src/meanings/graph_analysis.py`). Concretely:
   - Compute the Perron eigenvector (PageRank-style, and also the un-damped dominant eigenvector restricted to the Kernel where it's well-defined) over the same graph for which we compute the combinatorial seed.
   - Compare the spectral ranking to (a) the combinatorial MinSet membership, (b) the Kernel/Core/Satellite layering, (c) the psycholinguistic overlays from `src/meanings/annotations.py` / `reports/annotation-sources.md` (frequency, age-of-acquisition, concreteness). Does `v*` rank high exactly the words the combinatorial method marks as foundational? Does it correlate with AoA/frequency *as well as or better than* the layer decomposition does?
   - Propose this as a concrete code task with the exact functions to add and the predicted result, so it can be handed to an implementation agent.
4. **The reconciliation argument, written out.** Formalise "run Perron–Frobenius on the Kernel, recursion on the Rest." Does the Kernel's adjacency matrix's `v*` give a sensible canonical MinSet-weighting? What about reducibility *within* the Kernel (multiple SCCs)? — does the Frobenius normal form (block-triangular) give a principled layering that matches Core-vs-deeper-Kernel? Connect to prompt 3: the FVS anchor and the spectral anchor are two answers to one question; characterise when they agree.
5. **Falsifiers / scope.** (a) If the Perron ranking on OEWN is dominated by trivial degree effects and adds nothing over raw frequency, the "canonical soft grounding vocabulary" claim is weak — say so. (b) The economics/NLP/sociology constructs differ in *what flows* (value vs probability vs influence vs co-occurrence) — is "same matrix algebra" enough to call it the *same idea*, or is it a Cinderella-slipper fit? Assess honestly. (c) Distinguish the *Perron* eigenvector (dominant, the "anchor") from the *Fiedler* eigenvector (second, the "cleavage" — spectral clustering, Saussure's "system of differences"); note that the differences-not-anchors reading of meaning lives in the *other* end of the spectrum, and whether that's a separate paper.
6. **Name the paper.** Title, venue (applied math / network science generalist venue? a history-and-philosophy-of-science venue for the convergent-rediscovery framing? both, as two papers?), thesis, the one figure (the rediscovery table, or the OEWN spectral-vs-combinatorial scatter).

## Deliverable

A markdown report in `reports/` (suggest `reports/swanson-perron-frobenius-findings.md`): the rediscovery table; the citation-disjointness measurements with the partial bridges noted; **the OEWN spectral-vs-combinatorial-vs-psycholinguistic comparison** (actually compute it, or specify the exact runnable task and predicted outcome); the Kernel-spectral / Rest-combinatorial reconciliation worked out; falsifiers and scope limits; the proposed paper(s). Web access expected — read Sraffa Ch. 4–5 (or Newman 1962 / Pasinetti for the eigenvector formalisation), Langville & Meyer *Google's PageRank and Beyond*, Bonacich 1987, Hubbell 1965, and a Perron–Frobenius reference treatment (Berman & Plemmons, or Meyer's *Matrix Analysis* ch. 8).
