# Swanson link: Hanski's core–satellite species hypothesis (ecology, 1982) ↔ the dictionary Core/Satellite decomposition (Picard 2013 / Vincent-Lamarre 2014/2016)

**Date:** 2026-05-12
**Type:** deep-research findings (literature link + concrete data check)
**Status:** complete
**Author:** research subagent
**Inputs read:** `reports/paper-Vincent-Lamarre_2014_LatentStructureDictionaries.md`, `reports/paper-Picard_2013_HiddenStructureFunctionLexicon.md`, `reports/synthesis-minimal-core-to-expansion.md`, `reports/graph-object-definitions.md`, the OEWN summary/layers JSONs in `reports/`, and a re-build of the paper-WordNet graph via `uv run`.

---

## TL;DR

- **The vocabulary collision is real and the literatures are disjoint.** Both fields independently coined "core" and "satellite" for a high-centrality / peripheral split, neither cites the other, and the lexical-graph authors (Picard, Massé, Vincent-Lamarre, Harnad) cite psycholinguistics and feedback-vertex-set graph theory — not metapopulation ecology. Canonical Swanson signature. (See §1.)
- **But the key empirical bridge fails.** Hanski's split is *defined by* bimodality of site-occupancy and is *produced by* a stochastic colonization–extinction dynamic with a rescue effect. In OEWN, the analogue variable (definer out-degree = number of definitions a word appears in) is **not bimodal** — it is a one-spike-plus-monotone-heavy-tail distribution (74.3% of nodes never appear in any definition; among the rest, frequencies decay monotonically). The Hartigan dip test "rejects unimodality" but only because of the zero-spike + power-law tail at n = 160 010, not because of two separated humps; GMM BIC keeps falling as you add components (the signature of fitting a skewed continuum, not a 2-mode mixture). (See §2.)
- **And the lexical Core/Satellite split is not a degree split at all.** Core nodes (288) and Satellite nodes (12 565) have nearly identical out-degree distributions (means 43.8 vs 42.5; medians 14.5 vs 13). The lexical Core/Satellite distinction is a *position-in-the-condensation* distinction (source SCC vs non-source SCC inside the Kernel), not a "common vs rare" distinction. In Hanski, core-vs-satellite *is* common-vs-rare. So the two "core/satellite" pairs are structurally analogous only at the level of metaphor, not at the level of the formal object. (See §2.3.)
- **Net verdict:** the static graph decomposition stands on its own; the analogy to Hanski's *specific generative mechanism* (rescue-effect-driven occupancy bimodality) is **not supported by our data** and should not be the headline. A weaker, still-interesting line survives: porting a colonization–extinction *process view* of how words enter and leave the *defining vocabulary* across dictionary editions, which would need diachronic data we do not yet have. (See §3, §5.)

---

## 1. Disjointness

### 1.1 The two "core/satellite" usages

| | Ecology (Hanski 1982, *Oikos* 38: 210–221) | Lexical graph (Picard 2013; Vincent-Lamarre 2014, pub. 2016 *Topics in Cognitive Science*) |
|---|---|---|
| Population/object | A species in a regional set of habitat patches | A word (`lemma::pos`) in the directed definition graph |
| "Core" | Species occupying most patches; locally abundant; low extinction risk | Words in the source SCC(s) inside the Kernel; can define one another but not the rest |
| "Satellite" | Species occupying few patches; sparse; high local-extinction risk | Kernel words outside the Core; functionally needed for full definitional reach |
| What produces the split | Stochastic colonization–extinction (a Levins-type model) + **rescue effect** (immigration falls with patch occupancy → extinction probability falls with occupancy → positive feedback → **bimodal** occupancy-frequency distribution) | A purely combinatorial peeling: remove nodes with no outgoing non-self edge until a fixed point (Kernel), condense to SCCs, split on source vs non-source |
| Diagnostic signature | **Bimodality** of fraction-of-patches-occupied | Membership in graph substructures; *no claim of bimodality* |
| Psycholinguistic / ecological correlates | Abundance ↑ with regional distribution | Core learned earlier, more frequent, less concrete than Satellites; Satellites earlier/more frequent but more concrete than the Rest |

### 1.2 Citation search, both directions

- **Lexical → ecology:** Massé 2008, Picard 2013, Vincent-Lamarre 2014/2016, Harnad's grounding line. Their cited machinery is (a) feedback-vertex-set / minimum-FVS graph theory (Fomin et al.), (b) psycholinguistic norms (age-of-acquisition, frequency, concreteness — Kucera–Francis, Brysbaert, etc.), (c) WordNet / dictionary-graph work (Levary 2012, Steyvers–Tenenbaum 2005, Sparck-Jones). **No citation of Hanski, "core–satellite", "metapopulation", "rescue effect", or occupancy-frequency distributions** turned up in any search, and nothing in the repo's paper notes references ecology in this sense.
- **Ecology → lexical:** Hanski 1982 and its descendants (Hanski & Gyllenberg 1993 *Am. Nat.*; Tokeshi 1992; Gaston; McGeoch & Gaston 2002 *Biol. Rev.*; the marine-microbiome bimodality papers). These cite metapopulation theory, island biogeography, species-abundance distributions — **no citation of Vincent-Lamarre, Massé, Picard, or dictionary-graph / Kernel work**.
- **Was "core/satellite" in the lexical papers borrowed from ecology?** No evidence of that. The lexical authors describe it operationally ("one huge SCC, the Core, surrounded by many small SCCs, the Satellites"); the imagery is plausibly independent (a hub with things "in orbit"). The Swanson disjointness looks genuine, not an artifact of an unacknowledged borrowing.

### 1.3 Nearest misses / partial bridges

- **Species-abundance ↔ word-frequency (Zipf):** the long-standing observation that random sampling from a log-series or lognormal abundance distribution can *itself* generate a bimodal occupancy-frequency distribution (the "sampling artifact" critique of Hanski) is the closest existing cross-domain machinery, because word-frequency ranks famously obey Zipf/Zipf–Mandelbrot. This is a *real* partial bridge: if you sampled "which word appears in which definition" by drawing words proportional to a Zipfian frequency, you could ask whether the resulting definer-occupancy distribution is bimodal for artifactual reasons. (It is not, in our data — see §2 — which is consistent with the lexical occupancy distribution simply being a heavy-tailed continuum.)
- **Metapopulation models of language change:** searched and **not found** as an explicit framework. Adjacent work exists — drift-vs-selection accounts of why frequent words change/regularize less (Pagel, Lieberman, Bybee; "words more similar in meaning to other words are more likely to go extinct"), and "entrenchment"/frequency-increase models of language change — but none of it is cast as a Levins/Hanski patch-occupancy model, and none of it touches the *defining* vocabulary specifically. So the "port the dynamic" line below would be genuinely novel territory.

---

## 2. The bimodality check on existing OEWN outputs (the concrete deliverable)

**Setup.** Re-built the paper-faithful WordNet graph from `oewn:2024` via `uv run python` calling `meanings.wordnet_pipeline.build_paper_wordnet_graph` (matches `reports/oewn-paper-wordnet-kernel-summary.json`: 160 010 nodes, 677 823 edges, Kernel 12 853, Core 288, Satellites 12 565, core-policy = source-union). Edge `u → v` means *word u occurs in the definition of word v*. So the Hanski **occupancy analogue is out-degree(u)** = number of definitions u appears in as a definer (≈ "fraction of patches occupied"). Scripts: `scripts/bimodality_check.py` and `scripts/bimodality_kernel.py`. Stats run with `uv run --with scikit-learn --with diptest`.

### 2.1 Out-degree (the occupancy variable) — NOT bimodal

```
OUT-DEGREE over all 160 010 nodes:
  zeros = 118 813  (74.3% of all nodes never appear in any definition)
  max = 4878   mean = 4.215   median = 0
  quantiles: q50=0  q90=5  q99=78  q99.9=427
  count by degree 0..15:
    0:118813  1:9727  2:7340  3:4002  4:3046  5:2056  6:1649  7:1291
    8:1092  9:810  10:714  11:598  12:511  13:486  14:424  15:382
  → among the 41 197 nodes with out-degree ≥ 1, the histogram decays
    monotonically from 1 upward. There is no second hump near the high end.
    No "most words appear in most definitions" mode. The opposite of Hanski.
```

This is a one-mass-at-zero + monotone-heavy-tail (roughly power-law / log-series-like) shape — i.e. it looks exactly like a **species-abundance distribution**, not like Hanski's **occupancy-frequency** bimodality.

**Formal tests (on out-degree ≥ 1, i.e. 41 197 values):**
- Hartigan dip test, raw out-degree (all nodes incl. zeros): dip = 0.0304, p < 0.0001. Nonzero only: dip = 0.0891, p < 0.0001.
- *Interpretation:* the dip test "rejects unimodality", but this is driven by (a) the giant point mass at 0 and (b) the extreme right tail, at huge sample size — not by two separated modes. A point mass plus a heavy tail is technically "not unimodal" but is **not** the Hanski pattern. (The `diptest` library itself warns the precomputed critical values are unreliable above n = 72 000; we are at n = 41 197 for the nonzero set and n = 160 010 for the full set.)
- Gaussian-mixture BIC on log10(1 + out-degree), nonzero set: BIC k=1 = 58 600, k=2 = 42 760, k=3 = 38 255. BIC keeps dropping with more components and the fitted "modes" are not well separated (means 0.52 / 1.27 for k=2; 0.41 / 0.84 / 1.57 for k=3) — the classic signature of a GMM straining to approximate a single skewed distribution, **not** evidence of two genuine populations.

**Conclusion:** the definer-occupancy distribution in OEWN is **not bimodal** in Hanski's sense. The static Kernel/Core/Satellite decomposition is unaffected by this (it's a deterministic graph construction), but the specific *Hanski mechanism* — rescue-effect-driven occupancy bimodality — has **no empirical analogue here**, which is the brief's stated falsifier for the strong form of the analogy.

### 2.2 In-degree and total degree — also not bimodal (and roughly Gaussian-ish)

```
IN-DEGREE (# definer-words used inside this word's own definition):
  zeros = 3509 (2.2%)  max = 27  mean = 4.215  median = 4
  count 0..15: 0:3509 1:16419 2:28690 3:29092 4:23362 5:17474 6:12984 ...
  → single broad mode around 2–3 with a short right tail. Bounded by gloss
    length. Unimodal.

TOTAL DEGREE: zeros = 2456 (1.5%)  max = 4881  mean = 8.43  median = 4
  → single mode ~3 with a heavy right tail inherited from out-degree.
```

So no degree-based centrality variable on this graph is bimodal.

### 2.3 Core vs Satellite are NOT a degree split

```
Global out-degree by Kernel membership:
  CORE      (n=288):    mean 43.78   median 14.5   max  869   min 1
  SATELLITE (n=12565):  mean 42.55   median 13     max 4878   min 1
  REST      (n=147157): mean  0.86   median 0      max  460   min 0

Kernel-INTERNAL out-degree (edges that stay inside the 12 853-node Kernel):
  CORE      (n=288):    mean 3.99   median 2   max  54
  SATELLITE (n=12565):  mean 3.98   median 2   max 300
  kernel-internal out-degree histogram 0..20:
    1:6366  2:2282  3:1069  4:691  5:444  6:325  7:245  8:209  9:147 ...
    (monotone decay; unimodal; dip on raw = 0.089, p<0.0001 — again the
     "point mass + heavy tail", not two modes)
```

**This is the sharpest mismatch.** In Hanski, "core" and "satellite" *are* the two ends of the occupancy axis — that's the whole content of the hypothesis. In the lexical graph, Core and Satellite have essentially **the same** out-degree distribution; what distinguishes them is *topological position* (Core = source SCC(s) of the Kernel's condensation; Satellite = downstream SCCs), not magnitude of "occupancy". The big-occupancy outliers (max out-degree 4878) live in the Satellites, not the Core. So the formal objects do not line up the way the shared vocabulary suggests.

### 2.4 What about the layer histograms?

`layer_histogram` in the summary JSONs is the *definitional-distance* layering from the chosen seed (layer 0 = seed, layer k = max-predecessor-layer + 1). It is monotone-decaying with a long thin tail (0:2370, 1:1614, 2:1009, 3:768, 4:573, …, out to layer ~64), with a slight bump around layers 38–45 (130, 91, 91, 87…). Not bimodal in any Hanski-relevant sense — and in any case it's a different object (distance from a seed, not occupancy).

---

## 3. Porting the dynamic (sketch, plus the data it would need)

Hanski's model (Levins form with rescue effect): for the fraction p of occupied patches,
dp/dt = c·p·(1 − p) − e·p·(1 − p)  *(rescue: e·(1−p) replaces constant e)* — which has the bistable behavior giving the bimodal stationary distribution under demographic stochasticity.

**Lexical port — "definitional metapopulation":**
- "Patches" = definitions (one per word-sense). "Species" = candidate defining words.
- A word *colonizes* a definition when a lexicographer adopts it into that gloss in a new edition; it *goes locally extinct* when a revision removes it.
- **Rescue effect analogue:** a word already used in many definitions is more "available to mind" / more conventional as a defining term, so editors reach for it more readily and revise it out less readily → colonization rate ↑ and extinction rate ↓ with current occupancy → positive feedback.
- *Prediction if the mechanism transferred:* the stationary distribution of definer-occupancy would be **bimodal** (a stable "core defining vocabulary" + a churning "satellite" of rarely-used defining words). 

**This prediction is contradicted by §2:** the actual OEWN definer-occupancy distribution is monotone-decaying, not bimodal. So either (a) the rescue effect is too weak in lexicography (editors do *not* preferentially reuse already-common defining words enough to create bistability — plausible, since controlled defining vocabularies and stylistic diversity push the other way), or (b) the right state variable isn't raw occupancy. Either way, the strong port doesn't survive contact with the data we have.

**What would actually test a weaker version (colonization/extinction of the *defining* vocabulary over time, without requiring bimodality):**
- Multiple historical editions of one dictionary with machine-readable definitions: **Webster's 1828 / 1913 / Merriam-Webster modern**, or **OED1 vs OED3 entries**, or successive editions of a learner's dictionary with an explicit defining vocabulary (Longman LDOCE editions, where the controlled defining vocabulary is itself documented and revised — a near-perfect natural experiment).
- The diachronic resources flagged in `Ghizzota_2025_EnhancingLinguisticResourcesDiachronic` (`reports/paper-Ghizzota_2025_EnhancingLinguisticResourcesDiachronic.md` / `papers/Ghizzota_2025/`) — worth checking whether any of them give *definition text across time* rather than just word-sense-over-time; if so, that's the substrate.
- The measurable quantities: per defining-word, the time series of "number of definitions it appears in", edition over edition; estimate colonization and extinction rates as functions of current occupancy; test for the rescue-effect signature (negative dependence of extinction rate on occupancy) and for bistability/bimodality of the occupancy distribution. The Longman LDOCE controlled-defining-vocabulary revisions would also let you ask the inverse design question directly: do editors, when revising the controlled vocabulary, preferentially keep high-occupancy words?

---

## 4. Other direction: does the graph view give ecology anything? (bonus)

- **Kernel = feedback vertex set** has no standard counterpart in metapopulation theory. The natural ecological reading: *"the minimal set of species you'd have to re-seed to regenerate the whole assemblage's dependency structure"* — but that only makes sense if you have a directed "species A's persistence requires species B" graph (mutualism / facilitation networks, plant–pollinator, host–symbiont). In those settings the FVS / MinSet question — *"smallest set of taxa whose removal makes the facilitation graph acyclic, hence collapsible"*, or dually *"smallest reintroduction set"* — is genuinely well-posed and, as far as I can tell, not framed that way in the restoration-ecology / keystone-set literature. That's a real (small) export. Not pursued further here; flagging it.
- The lexical "definitional-distance layering" (peel order from a seed) maps to a "successional / assembly order" from a founder set — also suggestive, also out of scope.

---

## 5. Falsifiers — explicit verdicts

1. **"If the lexical degree/centrality distributions are not bimodal, the analogy to Hanski's specific mechanism weakens sharply."** — **TRIGGERED.** Out-degree, in-degree, total degree, and kernel-internal out-degree are all unimodal-plus-heavy-tail, not bimodal. The dip test's formal rejection of unimodality is a zero-spike/heavy-tail artifact at large n, not evidence of two modes; GMM BIC behavior confirms this. → The strong form of the Swanson link (transfer Hanski's rescue-effect mechanism wholesale) is **not supported**. The static decomposition stands; the dynamical analogy is at best a loose metaphor pending diachronic data.
2. **Additional falsifier found, not in the brief:** the lexical Core/Satellite split is *not* a "common vs rare" split — Core and Satellite have nearly identical occupancy distributions. In Hanski the core/satellite distinction *is* the occupancy split. So even the *naming* analogy is shallower than it looks: the lexical pair is a condensation-topology pair, the ecological pair is an abundance pair.
3. **"If 'core/satellite' in the lexical papers was itself borrowed from ecology, the disjointness is illusory — report and stop."** — **NOT triggered.** No evidence of borrowing; the lexical authors define the terms purely operationally and cite no ecology. Disjointness appears genuine.

---

## 6. Proposed paper (honest version)

Given §5, the right paper is **not** "Hanski's core–satellite hypothesis explains dictionary structure." It is the methodological/negative-result note:

- **Title:** *"Core and Satellite, Twice Over: a coincident vocabulary across ecology and lexical-graph theory, and why the mechanism does not transfer."*
- **Venue:** a methods/synthesis outlet that publishes cross-disciplinary cautionary notes — e.g. *PLOS ONE*, *Journal of Complex Networks*, *Cognitive Science* (short report), or a Swanson-style "undiscovered public knowledge" venue.
- **Thesis:** Ecology (Hanski 1982 →) and lexical-graph theory (Picard 2013 / Vincent-Lamarre 2016 →) independently use "core"/"satellite" for a centrality split and never cite each other — a textbook Swanson configuration — but the analogy is *partial*: ecology's split is defined by occupancy bimodality produced by a rescue-effect feedback, whereas the lexical split is a deterministic condensation-topology construction whose occupancy variable is a monotone heavy-tailed (species-abundance-like) distribution with no second mode and no core/satellite occupancy contrast. The transferable residue is a research program — colonization/extinction dynamics of *defining* vocabularies across dictionary editions — for which the testbed (Longman LDOCE controlled-defining-vocabulary revisions; Webster/OED edition deltas) is identified but not yet exploited.
- **Key figure:** side-by-side — (left) the canonical bimodal occupancy-frequency histogram from a core–satellite dataset (Hanski 1982 / Collins 1998 tallgrass prairie); (right) the OEWN definer out-degree histogram from §2.1 on log axes, monotone-decaying, with the Core (n=288) and Satellite (n=12 565) subsets overlaid showing they sit on *the same* curve. The visual contrast is the paper.
- **Secondary figure:** the disjoint-citation diagram (two literature clusters, the Zipf/species-abundance "sampling artifact" work as the only thin bridge).

---

## 7. What I could not verify

- **Hanski 1982 primary text:** read only via Wikipedia, the Semantic Scholar abstract page, and secondary summaries (degruyter reprint listings, the Gibson 1999 *J. Ecology* forum, the McGeoch & Gaston 2002 *Biol. Rev.* abstract via PubMed). The model equations and bimodality argument are well attested in those secondary sources but I did not read the original PDF in full.
- **McGeoch & Gaston 2002** and the Toronto "history and taxonomy" PDF: only the PubMed abstract / search-snippet level; the full-text PDF would not render. Tokeshi's "~46% right-skewed unimodal, 27% bimodal, 27% uniform" figure is reported via the secondary literature, not read first-hand — but it is the standard cited number and it reinforces the point that even *in ecology* bimodality is roughly a quarter of datasets.
- **Citation disjointness** is established by *absence* in every search I ran (Semantic Scholar's citing-papers list page would not render for me). I did not exhaustively crawl all ~thousands of Hanski 1982 citations; the claim is "no crossover surfaced", not "proven impossible".
- **`Ghizzota_2025` substrate:** I read the repo's process-report stub for it, not the paper itself; whether its diachronic resources include *definition text over time* (the thing the §3 test needs) is unconfirmed.
- The bimodality stats use `diptest` (Hartigan) and `sklearn.mixture.GaussianMixture` (BIC); `diptest` warns its critical values are unreliable above n≈72k, which is why I lean on the *shape of the histogram* and the BIC trend rather than the dip p-value alone. Conclusion (not bimodal) is robust to that caveat — the raw histograms in §2.1/§2.3 are monotone with no second hump.

---

### Artifacts produced
- `reports/swanson-core-satellite-findings.md` (this file)
- `scripts/bimodality_check.py`, `scripts/bimodality_kernel.py` — re-runnable: `uv run --with scikit-learn --with diptest python scripts/bimodality_kernel.py`

### Key references
- Hanski, I. (1982). Dynamics of regional distribution: the core and satellite species hypothesis. *Oikos* 38(2): 210–221. doi:10.2307/3544021
- Hanski, I. & Gyllenberg, M. (1993). Two general metapopulation models and the core–satellite species hypothesis. *Am. Nat.* 142(1): 17–41. doi:10.1086/285527
- Tokeshi, M. (1992). Dynamics of distribution in animal communities. *Researches on Population Ecology* 34: 249–273.
- McGeoch, M. A. & Gaston, K. J. (2002). Occupancy frequency distributions: patterns, artefacts and mechanisms. *Biological Reviews* 77: 311–331. doi:10.1017/S1464793101005887
- Gibson, D. J. et al. (1999). The core–satellite species hypothesis provides a theoretical basis for Grime's classification… *Journal of Ecology* 87. doi:10.1046/j.1365-2745.1999.00424.x
- Picard, O., Lord, M., Blondin-Massé, A., Marcotte, O., Lopes, M., Harnad, S. (2013). Hidden Structure and Function in the Lexicon. arXiv:1308.2428.
- Vincent-Lamarre, P., Blondin-Massé, A., Lopes, M., Lord, M., Marcotte, O., Harnad, S. (2016). The Latent Structure of Dictionaries. *Topics in Cognitive Science* 8(3): 625–659. doi:10.1111/tops.12211
- Massé, A. B., Chicoisne, G., Gargouri, Y., Harnad, S., Picard, O., Marcotte, O. (2008). How is meaning grounded in dictionary definitions? (TextGraphs-3).
- Levary, D., Eckmann, J.-P., Moses, E., Tlusty, T. (2012). Loops and self-reference in the construction of dictionaries. *Phys. Rev. X* 2: 031018.
