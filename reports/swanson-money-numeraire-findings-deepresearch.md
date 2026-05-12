# Meaning Has No Gold Standard
## The symbol-grounding problem as the numéraire problem

> **Provenance:** produced by a separate external deep-research thread, executing the same brief as `reports/research-swanson-1-money-numeraire.md`. Kept verbatim. The in-repo agent's parallel run of the same brief is `reports/swanson-money-numeraire-findings.md`; the two converge strongly — see `reports/swanson-synthesis.md` § "Money / numéraire" for the reconciliation. This document's distinctive contributions are the formal theorem in §8 and the four-experiment research agenda in §9.

**Date:** 2026-05-12  
**Status:** completed / literature-based Swanson-link scan  
**Deliverable:** correspondence map, disjointness evidence, transferable tools, falsifiers, and proposed paper

---

## Executive verdict

The proposed link is real enough to be worth writing up, but the strongest version is **not** “dictionary MinSets are literally numéraires.” The precise claim is:

> Lexical grounding-set theory and monetary numéraire theory are independent treatments of **relational systems whose internal relations determine only relative positions unless some external convention, coordinate, commodity, sensorimotor category, or institutional anchor is supplied**.

That is a meaningful Swanson link because the two sides have complementary machinery. The lexical side gives a sparse directed graph, SCCs, feedback vertex sets, and many non-unique minimal cycle-breaking sets. The monetary side gives normalization of homogeneous systems, commodity standards, units of account, fixed-point existence, Sraffian standardization, and theories of anchor-maintenance cost. The link becomes shallow only if we collapse these different mathematical objects into one. A dictionary **MinSet** is generally a *set of vertices that hits every directed cycle*. A monetary **numéraire** is usually a *normalization of a relative-price vector*. A **commodity standard** is an institutional promise or convertibility rule, not just a coordinate choice. A **Sraffian standard commodity** is a constructed basket/eigenvector-like composite, not a minimum feedback vertex set.

The best paper thesis is therefore conservative and stronger than the pun: **meaning has no gold standard because a lexical graph has many possible grounding standards; economics has already theorized the same arbitrariness, and its tools can turn “choose a MinSet” into a weighted, convention-sensitive standard-selection problem.**

---

## 1. Source basis

The uploaded prompt asked for a report that maps the dictionary-kernel literature to monetary economics, checks citation disjointness in both directions, evaluates what economics can lend back, states falsifiers, and names the paper that should exist. The prompt’s own summary gives the lexical baseline: dictionary definitions induce cycles; grounding sets are feedback vertex sets; real dictionaries decompose into `Rest → Kernel → Core → Satellites`; many MinSets exist; and Harnad’s symbol-grounding problem blocks treating recursive definability as meaning.

The lexical side is grounded in the uploaded synthesis and notes:

- The synthesis identifies the core line as `Masterman 1961 -> Harnad 1990 -> Massé 2008 / Picard 2013 / Vincent-Lamarre 2014 -> LGDE 2025 / OpenGloss 2025`, and separates philosophical ancestry, kernel science, and growth/infrastructure.
- Harnad supplies the philosophical limit: a purely symbolic system cannot generate intrinsic meaning from definitions alone; elementary symbols need nonsymbolic grounding before higher-order symbolic composition can inherit meaning.
- Massé et al. formalize dictionaries as directed graphs and show that grounding sets are feedback vertex sets.
- Picard et al. separate `Dictionary`, `Kernel`, `Core`, `Satellites`, and `MGSs`, warning against treating “the core vocabulary” as a single object.
- Vincent-Lamarre et al. scale the analysis to large dictionaries, showing small Kernels, about-1%-of-dictionary MinSets, non-uniqueness, and psycholinguistic gradients.

The monetary side was checked against primary or near-primary sources: Sraffa’s *Production of Commodities by Means of Commodities*; John Broome’s reconstruction of Sraffa’s standard commodity; Arrow–Debreu on equilibrium existence; Buiter’s Patinkin-centered “numerairology”; Fama and McCallum on unit of account / medium of account; Starr on the price of money; and Federal Reserve sources on gold-standard anchors and the end of convertibility.

---

## 2. Load-bearing evidence

### 2.1 Harnad: recursive definability is not grounded meaning

Harnad frames the issue as the problem of how meanings can be fixed intrinsically rather than parasitically. His central intuition pump is “trying to learn Chinese from a Chinese/Chinese dictionary alone,” where dictionary lookup produces a “symbol/symbol merry-go-round.” The uploaded note summarizes the same point: Harnad argues that a purely symbolic system cannot generate intrinsic meaning from definitions alone, and proposes grounding elementary symbols in nonsymbolic sensory categories before higher-order meanings are built compositionally.

**Use in this report:** this is the lexical analogue of a system of relative values with no exogenous standard. The dictionary can relate symbols to symbols, but something must connect at least some of them to non-symbolic referents, actions, perceptions, or learned categories.

### 2.2 Massé et al.: grounding sets are feedback vertex sets

Massé et al. define a dictionary graph `G=(V,E)`, with arcs from defining words to defined words. A seed set `U` recursively grounds the dictionary when repeated closure reaches all vertices. The paper’s core theorem is: `U` is a grounding set iff it intersects every directed cycle; equivalently, grounding-set minimization is the feedback-vertex-set problem.

Formal lexical skeleton:

```text
R'(U) = U ∪ { v ∈ V | N⁻(v) ⊆ U }
U is grounding iff R*(U) = V
U is grounding iff U hits every directed cycle
minimum grounding set = minimum feedback vertex set
```

**Use in this report:** the lexical anchor is not just a nameable “gold word.” It is a set that breaks all circular definitional dependencies. This makes the analogy stronger but also makes it mathematically non-identical to the ordinary one-good numéraire.

### 2.3 Picard and Vincent-Lamarre: the anchor is non-unique

Picard et al. distinguish `D`, `K`, `C`, `S`, and overlapping `MGSs`; Vincent-Lamarre et al. mature the framework, showing that full dictionaries contain a large `Rest`, a smaller `Kernel`, a `Core`, `Satellites`, and many `MinSets`. The Vincent-Lamarre note reports that Kernels are about 8–12% of full dictionaries, MinSets are about 1%, and MinSets are numerous and non-unique.

**Use in this report:** this is the strongest lexical fact for the monetary analogy. The system needs an anchor to become recursively usable, but no single minimal anchor is naturally privileged by graph theory alone.

### 2.4 Monetary economics: numéraire, unit of account, and commodity standards are conventional anchors

Several monetary sources support the economic side of the analogy:

- The Federal Reserve defines a nominal anchor as a variable that ties down the price level, and describes a gold standard as a commitment to fix the money supply to a “fixed quantity of gold.”
- The Federal Reserve History account of August 1971 says the United States ended dollar convertibility into gold, i.e., closed the gold window.
- Buiter, discussing Patinkin, quotes the “abstract unit of account” as serving “only for purposes of computation and record keeping” and having “no physical existence.”
- Buiter also says that what serves as the private unit of account is determined by individual choice, social convention, culture, and history; there is no primitive requirement that the unit physically exist.
- Starr emphasizes the circularity of fiat money: modern money can be “useless paper” or accounting entries and yet have value because it is “accepted because it is accepted.”

**Use in this report:** monetary economics already has a vocabulary for systems in which relative relations require a unit, standard, or acceptance convention, but the unit need not itself possess unique intrinsic content.

### 2.5 Sraffa: the standard commodity as a least-arbitrary constructed standard

Sraffa’s Chapter IV introduces the *Standard commodity* and *Standard system*. In the primary text, he calls the constructed mixture the “Standard commodity” and the corresponding proportional system the “Standard system.” Broome reconstructs this in linear-algebraic terms: the standard commodity is associated with an eigenvector of the production matrix, and using it as numéraire can “cut through that circle” in which prices and profit rate depend on each other.

**Use in this report:** Sraffa is not simply saying “pick any good.” He constructs a special composite that makes a circular price/profit relation tractable. That is the right model for a possible *standard MinSet*: not a naturally metaphysical primitive, but an algorithmically selected convention that reduces arbitrariness under stated criteria.

### 2.6 Arrow–Debreu: circularity can be consistency, not vicious regress

Arrow and Debreu describe Walras’s state of the economy as a system of simultaneous equations and stress the importance of proving that such a system has a solution. The point for the lexical side is not that dictionary SCCs are markets. It is that circular interdependence need not be pathological if it can be represented as a simultaneous fixed-point problem with existence and stability conditions.

**Use in this report:** economics can help reframe the `Core` SCC. A cyclic definitional core is not automatically meaningless; it may be a mutually constraining system that needs either an anchor, a fixed point, or both.

---

## 3. Correspondence table

| Dictionary-kernel concept | Monetary-economics concept | Shared formal object / structural role | Where the analogy breaks |
|---|---|---|---|
| Word / word-meaning vertex | Commodity, currency unit, accounting unit | Element in a relational system | Words have intentional and inferential roles; commodities have utility, production, legal, and fiscal roles. |
| Definition edge: defining word → defined word | Price quote, exchange relation, or input-output production dependency | Directed dependency or equation coefficient | Dictionary edges are sparse and lexical; price relations are often dense, continuous, and market-mediated. |
| Recursive lookup closure `R*(U)` | Valuation once a unit/account standard is selected | Closure from a chosen basis | Lexical closure is reachability/definability; monetary valuation is solving equations or normalizing a price vector. |
| Directed cycle | Circular definition; simultaneous price/profit dependence; circular acceptability of money | Self-referential dependency | A lexical cycle blocks acyclic learning; an economic cycle may simply be simultaneous determination. |
| Strongly connected component | Mutually dependent price/production subsystem | Irreducible circular subsystem | SCCs are graph-theoretic; economic interdependence may be algebraic without literal graph sparsity. |
| Kernel | Basic productive subsystem / irreducible monetary-price core | Part that cannot be recursively peeled away | The dictionary Kernel is unique under a deletion rule; economic “basic goods” or core equations depend on model assumptions. |
| Core | Main source SCC / central self-sustaining price-equation block | Dominant mutually defining component | Dictionary Core does not itself ground the whole dictionary; a price-equation core may determine relative prices conditional on distribution. |
| Satellites | Non-basic or auxiliary sectors; peripheral standards | Peripheral but sometimes necessary components | Weak mapping. Sraffian non-basics are usually price-takers from basics; lexical Satellites may be needed in MinSets. |
| Grounding set | Commodity standard / direct convertibility anchor | Exogenous basis that lets the rest be defined | A grounding set is normally multi-word and hits all cycles; a commodity standard may be a single good, basket, or institutional promise. |
| Minimum grounding set / MinSet | Choice of numéraire; choice of unit/medium of account | Minimal or conventional coordinate basis | A numéraire normalizes a price ray; a MinSet deletes vertices to make a graph acyclic. They are analogous, not isomorphic. |
| Many MinSets, none privileged by graph theory alone | Any commodity/basket/unit can serve as account standard, but not equally well | Underdetermined standard choice | Monetary standards differ in transaction cost, political feasibility, legal support, and credibility. MinSets differ in cognitive cost, concreteness, frequency, and pedagogical usability. |
| Sensorimotor grounding of seed words | Gold convertibility / commodity redemption / tax acceptability | External tie to something outside the internal symbolic-price system | Gold is itself economically valued within a social system; sensorimotor grounding is not merely another symbol. Fiat money shifts anchors rather than removing them. |
| Dictionary graph with no ultimate semantic primitive | Fiat monetary system / abstract unit of account | Anchorless-looking relational convention | Actual fiat systems are not unanchored: taxes, legal contracts, central banks, and expectations matter. |
| Sraffa standard commodity | Canonical weighted lexical “standard basket” | Perron-Frobenius-style standardization of a circular system | Sraffa’s object is a composite vector, not a feedback vertex set. A lexical version needs an additional selection rule. |
| Definitional distance hierarchy | Price transmission / production-chain distance | Distance from a core or standard | Dictionary distance is acyclic after reduction/collapse; monetary dynamics can be nonlinear and temporal. |
| Weighted MinSet | Cheapest/most credible standard; seigniorage-aware anchor | Optimization under maintenance costs | Seigniorage is fiscal revenue; lexical grounding cost is cognitive/pedagogical cost. The mapping works only after operationalizing costs. |

---

## 4. The analogy, stated precisely

### 4.1 Strong version that survives

Both literatures study a system in which internal relations alone underdetermine absolute content:

- In a dictionary, definitions can recursively relate words to other words, but cycles prevent the whole lexicon from being learned from definitions unless some words are already known outside the system.
- In monetary theory, relative prices can be stated only up to a standard; nominal units can be abstract; a commodity standard or unit of account supplies a coordinate and/or institutional anchor.

The shared schema is:

```text
Relational system S
  internal relation R among elements
  circular or homogeneous dependence inside S
  no privileged intrinsic coordinate from R alone
  external/conventional/algorithmic anchor A selected
  rest of system becomes usable relative to A
```

This is not a mere metaphor. It supports research transfer because both sides face the same second-order question: **when many anchors work, how do we choose among them without pretending one is metaphysically primitive?**

### 4.2 Weaker versions that do not survive literally

The following claims should be softened:

1. **“A grounding set is a numéraire.”**  
   Better: a grounding set is closer to a *commodity standard or anchor set* than to a scalar numéraire. A numéraire fixes one degree of price-scale freedom; an FVS removes all directed cycles. These are different mathematical operations.

2. **“Going off gold means discovering no Kernel bottoms out.”**  
   Better: going off gold shows that an economy can replace a commodity-convertibility anchor with legal, fiscal, policy, and expectation anchors. It is not evidence of literal anchorlessness.

3. **“Sraffa gives a canonical MinSet algorithm.”**  
   Better: Sraffa gives a way to construct a least-arbitrary *standard basket* for a circular production-price system. The lexical analogue would need to combine a Perron-Frobenius weighting of the Kernel with a weighted feedback-vertex-set objective.

4. **“Bitcoin maximalism vs MMT is Harnad vs distributionalism.”**  
   Better: as a stylized argumentative map, hard-money positions resemble the insistence on an exogenous scarce anchor, while chartalist/MMT-style accounts resemble institutional anchoring by tax/legal structures. But neither side maps cleanly onto Harnad or distributional semantics.

---

## 5. Citation-disjointness evidence

### 5.1 Result

The two literatures appear genuinely disjoint for the specific technical link proposed here. I found **no direct citation bridge** between:

- Harnad / Massé / Picard / Vincent-Lamarre / dictionary-graph grounding sets, and
- Walras / Sraffa / Patinkin / Fisher / Hahn / numéraire / commodity-standard monetary economics.

This is not a mathematical proof over all databases. It is strong negative evidence from direct full-text checks of the relevant lexical papers, direct full-text checks of representative monetary papers, and targeted web searches for mixed terms.

### 5.2 Lexical → economics: negative checks

| Lexical source checked | Terms checked | Result |
|---|---:|---|
| Harnad 1990 HTML version | `Walras`, `Sraffa`, `Patinkin`, `numeraire`, `Fisher`, `Hahn` | No matches in the opened source. |
| Massé et al. 2008 PDF / ACL version | `Walras`, `Sraffa`, `Patinkin`, `numeraire`, `numéraire` | No matches in the opened source. |
| Vincent-Lamarre et al. 2014 PDF | `Walras`, `Sraffa`, `Patinkin`, `numeraire` | No matches in the opened source. |
| Uploaded Picard note and bibliography summary | monetary names / numéraire terms | No monetary-economics bridge in the cited/recommended work list. |

The lexical bibliographies instead point to Harnad, dictionary resources such as LDOCE and WordNet, SCC/FVS algorithms, psycholinguistic databases, semantic networks, and dictionary-loop work.

### 5.3 Economics → lexical graph / symbol grounding: negative checks

| Monetary/economic source checked | Terms checked | Result |
|---|---:|---|
| Broome on Sraffa’s standard commodity | `Harnad`, `dictionary`, `Massé`, `symbol grounding` | No matches in the opened source. |
| Buiter, “Is Numerairology the Future of Monetary Economics?” | `Harnad`, `Massé`, `Vincent`, `symbol grounding` | No matches in the opened source. |
| Fama, “Banking in the Theory of Finance” | `Harnad`, `Massé` | No matches in the opened source. |
| McCallum, “The Role of Overlapping-Generations Models in Monetary Economics” / monetary-account discussion | `Harnad`, `Massé` | No matches in the opened source. |
| Starr, “The Price of Money in a Pure Exchange Monetary Economy with Taxation” | `Harnad`, `dictionary`, `Massé` | No matches in the opened source. |

### 5.4 Near misses

1. **AI barter / multi-agent RL.**  
   A search found an AI/RL paper on emergent bartering that discusses a numéraire-like good and cites Harnad’s symbol-grounding work. This is a genuine near miss, but it is not the monetary-economics/dictionary-graph bridge. It sits in multi-agent learning, not Sraffa/Patinkin/Walras or Massé/Vincent-Lamarre.

2. **Multiagent systems textbooks.**  
   Some multiagent systems material contains both a divisible numéraire in mechanism-design examples and symbol-grounding / shared-ontology discussion elsewhere. Again, this is co-location in AI, not a direct theoretical bridge.

3. **Sraffa and Wittgenstein.**  
   There is a separate literature linking Sraffa to Wittgenstein and philosophy of language. This is historically interesting but not the Harnad/Massé/FVS dictionary-graph link.

4. **Buiter / Patinkin on “numerairology.”**  
   Buiter comes closest on the economics side because he explicitly asks why a unit of account is selected and emphasizes convention, history, and culture. But he does not connect this to symbol grounding or lexical graphs.

5. **Marxian value-form and commodity fetishism.**  
   Marxian discussions of exchange value, money, and social relations among commodities are conceptually adjacent to the “no intrinsic content” theme. They are not, in the checked sources, connected to Harnad or dictionary FVS work.

### 5.5 Conclusion on disjointness

The disjointness claim is supported in the relevant sense: **the exact bridge “dictionary grounding sets / MinSets ↔ numéraire / commodity standard / Sraffa standard commodity” appears not to have been made in the technical literatures checked.** The closest near misses are metaphorical, historical-philosophical, or in AI multi-agent systems rather than monetary economics and lexical graph theory.

---

## 6. What economics can lend back to lexical grounding

### Rank 1 — Weighted MinSets as anchor-budget optimization

**Transfer:** seigniorage and standard-maintenance costs → weighted feedback vertex sets.

Massé et al. already leave open the question of weights: not just the smallest grounding set, but one satisfying cognitive, morphosyntactic, and semantic constraints. Vincent-Lamarre’s findings make this urgent because MinSets are numerous and non-unique. Monetary economics asks a parallel question: not “can this serve as a standard?” but “what does it cost to maintain this standard, and who benefits?”

A lexical version:

```text
Given dictionary graph G=(V,E)
and cost c(v) = α·AoA(v) - β·frequency(v) - γ·concreteness(v)
              + δ·polysemy(v) + ε·definition-maintenance-cost(v)
              + ζ·sensorimotor-grounding-cost(v),
find F ⊆ V minimizing Σ_{v∈F} c(v)
s.t. F hits every directed cycle.
```

**Feasibility:** high. Weighted FVS is a standard extension of the existing formalism; the uploaded notes already identify weighted MinSets as an open question.  
**Payoff:** converts “many MinSets, none privileged” into a family of explicit standard-selection regimes.  
**Risk:** weights can smuggle in the answer. The research contribution is the Pareto frontier, not a single allegedly final MinSet.

### Rank 2 — Fixed-point semantics for the cyclic Core

**Transfer:** Arrow–Debreu/Walrasian existence proofs → conditions under which a cyclic definitional Core is self-consistent rather than vicious.

Arrow–Debreu’s relevance is not direct market realism. It is proof strategy: simultaneous interdependence can be coherent if there is a fixed point satisfying all constraints. Dictionary cycles might be interpreted as semantic equations rather than lookup failures:

```text
For each word i in a Core SCC:
  meaning_i = F_i(meaning_j for j in predecessors(i))
```

Then ask:

- Does a fixed point exist?
- Is it unique?
- Is it stable under definitional revision?
- Which seed terms make the fixed point identifiable rather than merely self-consistent?

**Feasibility:** medium-high for formal models and toy lexicons; harder for real semantics.  
**Payoff:** prevents the reductive “cycles are garbage” stance. Cyclicity can be a structural fact of mutual constraint.  
**Risk:** self-consistency is not grounding. Harnad still applies.

### Rank 3 — Sraffa-style standard lexical commodity

**Transfer:** Sraffa’s standard commodity → an eigenvector-weighted lexical standard.

Let `A_K` be a weighted adjacency matrix for the Kernel or Core, where `A_ij` measures how much defining word `i` contributes to defined word `j`. If `A_K` is irreducible or decomposed into irreducible SCCs, compute a Perron-Frobenius vector `π`. Interpret `π_i` as a circular-definitional importance weight. Then define a *standard MinSet* as a weighted FVS minimizing a cost such as:

```text
c(i) = grounding_cost(i) / π_i
```

or choose MinSets whose aggregate weight vector best approximates the Core’s standard vector.

**Feasibility:** medium. The eigenvector part is easy; the theoretical interpretation is delicate.  
**Payoff:** gives a principled, Sraffa-inspired way to find a least-arbitrary MinSet without claiming metaphysical primitiveness.  
**Risk:** Sraffa’s standard commodity is a composite basket, not a cycle-hitting set. A “standard lexical commodity” is probably a weighted basket over the Kernel; the MinSet is then selected relative to it.

### Rank 4 — Unit-of-account / medium-of-exchange unbundling

**Transfer:** monetary distinction among numéraire, unit of account, medium of account, medium of exchange, and standard of deferred payment → semantic distinction among coordinate system, grounding medium, expressive medium, and teaching medium.

Lexical analogue:

| Monetary distinction | Lexical analogue |
|---|---|
| Analyst’s numéraire | Coordinate convention for measuring definitional centrality |
| Private unit of account | Shared lexical/conceptual unit in a community |
| Medium of exchange | Tokens actually used in communication |
| Commodity convertibility | Ostensive/sensorimotor grounding |
| Legal/tax acceptability | Institutional or pedagogical enforcement of meanings |

**Feasibility:** medium. Mostly conceptual, but it cleans up confusions.  
**Payoff:** prevents treating “definition,” “meaning,” “grounding,” and “usage” as one thing.  
**Risk:** too taxonomic unless attached to experiments.

### Rank 5 — Monetary history as natural experiment

**Transfer:** shifts among gold, silver, fiat, currency boards, pegs, and inflation-targeting regimes → lexicographic changes in controlled vocabularies and grounding policies.

For lexical work, the better data are not monetary history itself but lexical analogues:

- revisions of LDOCE defining vocabulary,
- controlled technical vocabularies,
- bilingual dictionary pivots,
- child-directed vocabulary lists,
- school curricula,
- crowdsourced mini-dictionaries,
- dictionary games over time.

**Feasibility:** medium-low. Historical monetary regimes are good conceptual analogues but poor direct experiments. Lexical resources can supply the actual experiments.  
**Payoff:** tests whether swapping anchors changes reachability, definition length, learnability, and semantic drift.  
**Risk:** historical regime changes are overdetermined; too many institutional variables.

### Rank 6 — Hard-money vs chartalist rhetoric as a mirror of Harnad vs distributionalism

**Transfer:** metallist / Bitcoin-hard-anchor intuitions vs chartalist / MMT institutional-anchor intuitions → Harnad-style exogenous grounding vs distributional/usage-based semantics.

**Feasibility:** low as a technical research contribution; medium as a framing device.  
**Payoff:** rhetorically powerful.  
**Risk:** high noise. Bitcoin, MMT, distributional semantics, and Harnad’s grounding problem are all internally diverse. Use only as an introductory contrast, not as the core theorem.

---

## 7. Falsifiers and failure modes

The link is interesting only if it survives the following tests.

### Falsifier 1 — The formal objects are too different

If monetary numéraire choice is only homogeneous scaling of a complete relative-price system, while dictionary grounding is sparse directed cycle-hitting, then the analogy is formal only at the highest abstraction. This is the main threat.

**Assessment:** real but not fatal. The correct bridge is not numéraire = MinSet. It is standard-selection under relational underdetermination. The formal transfer should go through weighted standards, fixed points, and anchor-cost functions, not a claimed graph isomorphism.

### Falsifier 2 — Gold is not exogenous either

A commodity standard does not supply intrinsic value in a metaphysical sense. Gold’s monetary role is historically and institutionally mediated; its commodity value is itself endogenous to social and market systems.

**Assessment:** strengthens the cautious version. Gold is like a concrete word that is easier to ground, not like a final semantic atom.

### Falsifier 3 — Fiat money is not anchorless

Fiat systems are stabilized by taxes, legal settlement, accounting practices, central-bank policy, network expectations, and state capacity. Going off gold does not prove that value floats freely.

**Assessment:** the original “off gold = no Kernel that bottoms out” should be revised. Off gold is anchor substitution: commodity convertibility is replaced by institutional anchoring.

### Falsifier 4 — Weighted cognitive criteria make MinSets unique

If adding psycholinguistic or multimodal grounding weights makes one MinSet robustly dominant across dictionaries and languages, then “many MinSets, none privileged” is a graph-theoretic artifact, not the final cognitive story.

**Assessment:** this is an empirical opportunity. The analogy predicts convention and cost matter; it does not require equal legitimacy of all MinSets once costs are specified.

### Falsifier 5 — Sraffa cannot be translated without losing the theorem

If the standard commodity’s algebraic properties depend on production equations in a way that lexical adjacency matrices cannot reproduce, then the Sraffa transfer is only metaphorical.

**Assessment:** likely partly true. The safe transfer is not Sraffa’s theorem wholesale, but the design pattern: construct a composite standard from an irreducible circular system and then select anchors relative to it.

### Falsifier 6 — Lexical dynamics matter too much

Dictionaries are static snapshots; money is dynamic, strategic, and institutionally enforced. If lexical meaning changes through use in a way that cannot be modeled as graph revision or flow, the analogy underfits.

**Assessment:** not fatal; it identifies the next extension. Dynamic dictionary graphs, corpus-updated definitional edges, and diachronic controlled vocabularies could make the analogy stronger.

### Falsifier 7 — Economic dependency graphs are dense or complete

If relative-price systems are best represented as complete graphs, then sparse FVS structure has no useful economic counterpart.

**Assessment:** fatal only for the strict FVS analogy. Production networks, input-output tables, payment networks, and credit chains are sparse enough that graph tools may still matter, but ordinary Walrasian price normalization is not FVS.

---

## 8. Proposed paper

**Title:** “Meaning Has No Gold Standard: Lexical Grounding Sets and the Numéraire Problem”

**Venue:** *Cognitive Science* if framed as symbol grounding and cognitive lexicon; *Synthese* if framed as philosophy of language/economics; *Journal of Economic Methodology* if framed as a cross-domain methodological theorem; or *Transactions of the Association for Computational Linguistics* if the paper includes new weighted-MinSet experiments.

**Thesis:** Harnad’s symbol-grounding problem and the dictionary-graph program of Massé/Picard/Vincent-Lamarre independently rediscover the same underdetermination problem that monetary economics treats under numéraire, unit-of-account, commodity-standard, and standard-commodity theory: an internally relational system can be recursively or numerically coherent only relative to an anchor, but many anchors work and none is metaphysically privileged by the internal relations alone. The paper’s contribution is to state the exact non-isomorphism—MinSet is FVS, numéraire is normalization, standard commodity is a composite—and then exploit the analogy productively by introducing a Sraffa-inspired, weighted feedback-vertex-set method for selecting *standard MinSets*.

**One figure:** two panels. Left: a dictionary graph decomposed as `Rest → Kernel → Core/Satellites`, with several alternative MinSets piercing every directed cycle. Right: a price simplex/ray with alternative numéraires, a commodity-convertibility anchor, and a Sraffian standard commodity vector. A bridge arrow labels the common abstraction: “relational closure + arbitrary but costed anchor.”

**One theorem / formal result:**

> Let `K` be an irreducible weighted dictionary Kernel with nonnegative adjacency matrix `A_K`. Let `π` be its Perron-Frobenius vector, normalized to sum to one. For any positive grounding-cost function `g(v)`, define `c(v)=g(v)/π_v`. A `c`-minimum feedback vertex set is invariant under scalar renormalization of `π` and supplies a Sraffa-style *standard MinSet* conditional on `A_K` and `g`. It is canonical relative to the stated standard, not semantically ultimate.

That theorem is modest but publishable: it turns “many MinSets” into a family of explicit standard-selection regimes, exposes the exact analogy to economic numéraire choice, and preserves Harnad’s warning that internal recursive closure is not meaning.

---

## 9. Working research agenda

### Experiment A — Weighted MinSet frontier

Build a dictionary graph from LDOCE, WordNet glosses, or OpenGloss. Compute approximate MinSets under multiple cost functions:

1. size-only,
2. age-of-acquisition weighted,
3. concreteness weighted,
4. frequency weighted,
5. multimodal-groundability weighted,
6. Sraffa/PF-standard weighted,
7. composite pedagogical cost.

Report overlap, stability, definition depth, average definitional length, and psycholinguistic profile.

### Experiment B — Core fixed-point diagnostics

For the Core SCC, treat definitions as simultaneous constraints and test whether embedding-based or logical semantic representations converge under iterative definition substitution. Compare:

- no external anchor,
- random MinSet anchor,
- weighted MinSet anchor,
- Sraffa/PF-standard MinSet anchor,
- human controlled defining vocabulary.

### Experiment C — Anchor swap natural experiments

Use historical revisions of controlled defining vocabularies and compare how anchor changes affect:

- reachable vocabulary,
- average definitional depth,
- loop structure,
- MinSet composition,
- psycholinguistic costs,
- cross-dictionary stability.

### Experiment D — Monetary graph back-transfer

Build input-output or payment-network graphs and ask whether FVS-like anchor sets identify commodities/institutions whose exogenous stabilization would make the rest of a price/payment network recursively determined. This is speculative, but it is the reciprocal Swanson payoff.

---

## 10. References and URLs consulted

### Lexical grounding and dictionary graphs

- Harnad, Stevan. 1990. “The Symbol Grounding Problem.” *Physica D*. HTML version consulted.  
  URL: https://arxiv.org/html/cs/9906002

- Blondin Massé, Alexandre; Chicoisne, Guillaume; Gargouri, Yassine; Harnad, Stevan; Picard, Olivier; Marcotte, Odile. 2008. “How Is Meaning Grounded in Dictionary Definitions?” *TextGraphs-3*.  
  URL: https://aclanthology.org/W08-2003.pdf

- Picard, Olivier; Lord, Mélanie; Blondin-Massé, Alexandre; Marcotte, Odile; Lopes, Marcos; Harnad, Stevan. 2013. “Hidden Structure and Function in the Lexicon.” Uploaded notes consulted.

- Vincent-Lamarre, Philippe; Blondin Massé, Alexandre; Lopes, Marcos; Lord, Mélanie; Marcotte, Odile; Harnad, Stevan. 2014. “The Latent Structure of Dictionaries.”  
  URL: https://archipel.uqam.ca/6290/1/DictpaperFIN.pdf

### Numéraire, standards, equilibrium, money

- Sraffa, Piero. 1960. *Production of Commodities by Means of Commodities: Prelude to a Critique of Economic Theory*. PDF consulted.  
  URL: https://www.nuevatribuna.es/media/nuevatribuna/files/2013/04/15/production_of_commodities_by_means_of_commodities.pdf

- Broome, John. “Sraffa’s Standard Commodity.”  
  URL: https://users.ox.ac.uk/~sfop0060/pdf/Sraffa%27s%20standard%20commodity.pdf

- Arrow, Kenneth J.; Debreu, Gérard. 1954. “Existence of an Equilibrium for a Competitive Economy.”  
  URL: https://web.stanford.edu/class/msande311/arrow-debreu.pdf

- Buiter, Willem H. “Is Numerairology the Future of Monetary Economics?”  
  URL: https://willembuiter.com/numerairology.pdf

- Fama, Eugene F. 1980. “Banking in the Theory of Finance.”  
  URL: https://www.bu.edu/econ/files/2012/01/Fama1-Banking-in-the-theory-of-finance1.pdf

- McCallum, Bennett T. 1985. “The Role of Overlapping-Generations Models in Monetary Economics.” NBER Working Paper 1572.  
  URL: https://www.nber.org/system/files/working_papers/w1572/w1572.pdf

- Starr, Ross M. “The Price of Money in a Pure Exchange Monetary Economy with Taxation.”  
  URL: https://economics.ucsd.edu/~rstarr/PriceofMoney.pdf

- Board of Governors of the Federal Reserve System. “Historical Approaches to Monetary Policy.”  
  URL: https://www.federalreserve.gov/monetarypolicy/historical-approaches-to-monetary-policy.htm

- Federal Reserve History. “Gold Convertibility Ends.”  
  URL: https://www.federalreservehistory.org/essays/gold-convertibility-ends

- Office of the Historian. “Nixon and the End of the Bretton Woods System, 1971–1973.” Retired page, used only as corroborating historical context.  
  URL: https://history.state.gov/milestones/1969-1976/nixon-shock

### Near misses

- Emergent bartering / multi-agent reinforcement learning search result involving numéraire and Harnad-style symbol grounding.  
  URL observed via search: https://www.researchgate.net/publication/360618524_Emergent_Bartering_Behaviour_in_Multi-Agent_Reinforcement_Learning

- Weiss, Gerhard, ed. *Multiagent Systems: A Modern Approach to Distributed Artificial Intelligence*. Search/opened source with both numéraire examples and symbol-grounding/shared-ontology material in separate contexts.  
  URL: https://theswissbay.ch/pdf/Gentoomen%20Library/Artificial%20Intelligence/General/Multiagent%20systems%20a%20modern%20approach%20to%20distributed%20artificial%20intelligence%20-%20Gerhard%20Weiss.pdf

- Sraffa/Wittgenstein philosophy-of-language near miss.  
  URL: https://wab.uib.no/agora/tools/alws/collection-7-issue-1-article-17.annotate

- White, Leland. “Competitive Payments Systems and the Unit of Account.”  
  URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1422388

---

## Appendix: compressed query / full-text check log

- Searched mixed terms: `symbol grounding numeraire`, `symbol grounding numéraire`, `Harnad numeraire`, `Sraffa Harnad`, `Patinkin symbol grounding`, `dictionary graph numeraire`, `feedback vertex set numeraire`, `meaning money numeraire`, `standard commodity symbol grounding`.
- Full-text negative checks: Harnad HTML for `Walras`, `Sraffa`, `Patinkin`, `numeraire`, `Fisher`, `Hahn`; Massé PDF for `Walras`, `Sraffa`, `Patinkin`, `numeraire`, `numéraire`; Vincent-Lamarre PDF for `Walras`, `Sraffa`, `Patinkin`, `numeraire`; Broome/Sraffa, Buiter/Patinkin, Fama, McCallum, and Starr for `Harnad`, `Massé`, `Vincent`, `dictionary`, and `symbol grounding` as applicable.
- Closest near misses: multi-agent RL with Harnad and numéraire-like barter; multiagent systems material with both mechanism-design numéraire examples and separate symbol-grounding/shared-meaning material; Sraffa/Wittgenstein language literature; Buiter’s convention-centered “numerairology.”

