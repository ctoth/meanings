# Is meaning Yoneda-complete? Category theory's "objects are their relations" vs Harnad's grounding residue

**Date:** 2026-05-12
**Type:** research findings (conceptual cross-disciplinary confrontation + empirical sketch)
**Status:** complete; empirical adjudication partly run, partly specified (repo lacks the psycholinguistic overlay data)
**Brief:** `reports/research-swanson-4-yoneda-harnad.md`

---

## 0. TL;DR

- **Disjointness: confirmed, strongly, both directions.** Categorical-structuralism philosophy (Marquis, Awodey, Landry, McLarty; Hellman as critic) does not cite Harnad or the symbol-grounding problem. The symbol-grounding literature (Harnad 1990; Taddeo & Floridi 2005 review; Scholarpedia) does not cite the Yoneda lemma, categorical semantics, or "mathematical structuralism." DisCoCat (Coecke–Sadrzadeh–Clark 2010 and successors) is the closest crossing of streams — it is *literally* category theory applied to word meaning — and it still says nothing about grounding: it takes distributional vectors as given "meaning" and never asks where the elementary content comes from. Inferentialism / conceptual-role semantics (Sellars, Brandom, Block, Harman) *is* the philosophical theory "meaning = relations to other expressions" and it does not know about Yoneda. The one near-miss is Seremeti & Kameas 2013, "Yoneda Philosophy in Engineering," which uses the Yoneda embedding to formalize ontology/concept identity in software engineering — peripheral, no cognitive-science contact.
- **One-sentence statement of the disagreement** (forced to quantifiers): *For every entity X in a relational system S, is X's identity / content exhausted by the bundle of S-relations incident to X?* Yoneda answers **yes — but only relative to a fixed ambient category C** (objects, morphisms, composition, identities all pre-given). Harnad answers **no — for the symbols of a cognitive agent — because the ambient "category" (which relata exist, which relations are real) is not given a priori; it must be grounded into existence non-symbolically.**
- **Verdict: Resolution A** ("compatible; the synthesis is: grounding = constructing/choosing the base category, after which Yoneda takes over"), with a sharp **symmetry rider toward B** (if you *are* a thoroughgoing structuralist who denies any residue, then mathematics inherits the very same grounding problem — the Benacerraf access problem — and you can't have it both ways). **Resolution C is a thumb on the scale for Harnad but a *light* thumb**; the dictionary-graph correlations are real but under-determine the philosophical point, for reasons spelled out in §4.
- **Empirical status:** the repo has the dictionary-graph layer data (`reports/oewn-paper-wordnet-layers.json`: 12,853 kernel-node depth labels) and a complete annotation *pipeline* (`src/meanings/annotations.py`, `--annotations` CLI flag), **but ships zero psycholinguistic values** (`annotation_sources: []`, all coverage 0). So the headline regression — "variance in which-layer-a-word-lands-in: structural features vs concreteness/AoA/frequency" — **cannot be run as stated without supplying external norm CSVs** (Brysbaert et al. 2014 concreteness; Kuperman et al. 2012 AoA; SUBTLEX-US frequency). I ran the structural-only descriptive (§4.2) and specify the full regression precisely (§4.3) so it is a drop-in once the CSVs are in `data/psycholinguistic/`.

---

## 1. The two doctrines, at full strength

### 1.1 The Yoneda side (strongest version)

Let **C** be a locally small category. The Yoneda lemma gives a full and faithful embedding **C ↪ [Cᵒᵖ, Set]**, A ↦ Hom(–, A). Consequences usually sloganized as: "an object is determined up to isomorphism by its bundle of relations to all other objects"; "an object is what it does"; "mathematics has no nouns, only verbs" (Lawvere's structuralist program; the "behavioristic" / "relative" viewpoint). There is **no residue**: two objects with naturally isomorphic hom-functors *are* isomorphic. Internal constitution is not just unknowable — it is *irrelevant*; the relational profile is constitutive, exhaustively. Categorical structuralism (Awodey "Structure in Mathematics and Logic" 1996; Marquis on categorical structuralism; Landry; McLarty) elevates this to a philosophy of mathematical objects in general: numbers, groups, spaces have no nature beyond their structural role.

The strongest *cognitive-science* extrapolation (not made by category theorists, but the natural one): a concept just *is* its inferential/associative profile within an agent's web of concepts; functional-role / inferential-role semantics is then "Yoneda for the mind," and there is nothing more to having concept C than occupying C's node in the relational graph.

### 1.2 The Harnad side (strongest version)

A purely symbolic system — a system whose symbols are individuated and "defined" only via other symbols of the same system — has no intrinsic meaning; its interpretation is parasitic on interpreters outside it (the Chinese-room / "Chinese-Chinese dictionary-go-round" argument: looking up a word in a monolingual dictionary of a language you don't know cycles forever among meaningless tokens). Meaning requires that *elementary* symbols be **grounded** in non-symbolic representations — sensorimotor "iconic" projections and the learned "categorical" representations that let an agent reliably detect, sort, and act on the things symbols refer to. The relational/definitional structure among symbols is **necessary but not sufficient**; recursive definability ≠ meaning. There *is* a residue, and it is non-symbolic.

### 1.3 The single proposition they fight about

> **P:** "X's identity/content is exhausted by the relations X bears to the other elements of the relational system X belongs to."

- Yoneda: **P is a theorem** — *given* a fixed ambient category. (Quantifier: ∀ object A ∈ C, A ≅ A′ iff Hom(–,A) ≅ Hom(–,A′). The "system" is frozen.)
- Harnad: **P is false** for the symbol-system of a cognitive agent — *because the ambient system is not frozen and not given*; which relata exist and which relations obtain is exactly what grounding has to settle, non-symbolically. (Quantifier shift: Harnad is not denying Yoneda *within* C; he's denying that C comes for free.)

So the apparent head-on collision is, on inspection, **a quantifier/scope difference**: Yoneda quantifies inside a fixed C; Harnad's whole point is about *where C comes from*.

---

## 2. Disjointness evidence (what was searched, what was found)

**Direction 1 — does symbol-grounding / lexical-graph / cognitive-science work cite Yoneda or categorical semantics?**
- Harnad 1990 ("The Symbol Grounding Problem", *Physica D* 42:335–346) and its descendant literature (Taddeo & Floridi 2005, "Solving the Symbol Grounding Problem: A Critical Review of Fifteen Years of Research"; Scholarpedia "Symbol grounding problem"; Wikipedia ditto) — **no** mention of Yoneda, category theory, or mathematical structuralism. The framing is entirely cognitive-science / robotics ("robotic Turing test", iconic/categorical representations).
- The dictionary-kernel lineage in this repo (Massé 2008, Picard 2013, Vincent-Lamarre et al. 2014, Levary 2012) — graph theory (feedback vertex sets, SCCs, definitional distance), **no** category theory.

**Direction 2 — does categorical-semantics / structuralism-in-philosophy-of-math work cite Harnad / symbol grounding?**
- Categorical structuralism: Awodey, Marquis (entries and papers on categorical structuralism), Landry, McLarty; the critical side, Hellman ("Structuralism without structures?"); SEP "Structuralism in the Philosophy of Mathematics"; Benacerraf "What Numbers Could Not Be" 1965 as the ur-text of the access/identity worry. **None** engage Harnad or symbol grounding. The "access problem" they worry about (how do we have epistemic access to abstract structures?) is *structurally* Harnad's grounding problem in another domain — but the literatures don't talk.

**Adjacent fields the brief flagged:**
- **DisCoCat** (Coecke, Sadrzadeh, Clark 2010 "Mathematical Foundations for a Compositional Distributional Model of Meaning"; Grefenstette & Sadrzadeh 2011 "Concrete Models and Empirical Evaluations…"; the DisCoPy/lambeq line). This is the literal intersection of category theory and word meaning — pregroup grammar + FdVect as rigid/compact-closed categories, sentence meaning via a strong monoidal functor. **It does not connect to grounding.** Word vectors are *inputs*; the framework is about *composition*, not about where elementary content comes from. So DisCoCat is, ironically, a Yoneda-flavored project that has never met Harnad even though it's the obvious place for them to meet. (That's the venue, see §6.)
- **Conceptual-spaces** (Gärdenfors): geometric, prototype-based; closer in spirit to "grounding" than to Yoneda; doesn't cite either Yoneda or Harnad in the relevant way.
- **Inferentialism / conceptual-role semantics** (Sellars; Brandom *Making It Explicit*; Block "Advertisement for a Semantics for Psychology" / "Conceptual Role Semantics"; Harman; Horwich). This *is* "meaning = relational role." It is the philosophical position that, if true, makes Yoneda the right formal picture of meaning. **It does not cite Yoneda.** And it has its own standing objection — the "input/output residue": Block himself splits "narrow" conceptual role from a "wide"/referential factor precisely because pure internal role seems to leave out the world. That residue is Harnad's residue under a different name. So the philosophers already discovered the gap; nobody wired it to the category-theory slogan.

**Net:** the disjointness in the brief is real. Four mutually non-citing communities (categorical structuralists; DisCoCat; symbol-grounding/cog-sci; inferentialists) are all circling the same proposition P. The contribution of any paper here is to put them in one room.

---

## 3. Which resolution? — the argument for A

**Resolution A (compatible; synthesis = "grounding ≈ constructing the base category"):**

The Yoneda lemma is *conditional on C*. It says nothing about how C is selected — which objects are "in", which arrows count as morphisms, what composition means. Change C and the same naked entity gets a different identity (an object that's terminal in one category is unremarkable in another; the integers-as-a-ring vs integers-as-an-ordered-set carry different Yoneda profiles). Harnad's claim, read precisely, is **not** "within the agent's conceptual web, a concept has content over and above its web-relations" — it's "**the agent's conceptual web isn't given a priori; the agent has to fix which relata exist and which relations are real, and *that* fixing is non-symbolic** (sensorimotor categorization)." Those two claims do not contradict; they compose:

> **Synthesis:** Grounding = choosing/constructing the ambient category C (its objects = the agent's bottoming-out categories, carved by sensorimotor learning; its morphisms = the relations the agent treats as inferentially live). *Once C is fixed, Yoneda is exactly right*: a grounded concept is then nothing over and above its hom-bundle in C. The residue Harnad insists on is **the residue of category-*selection*, not of object-*identity-within-a-category*.**

This is a clean reframing of the repo's own objects:
- A **MinSet** is a *generating set* for (the relevant fragment of) C — a minimal set of objects/arrows from which the rest is reachable.
- The empirical **arbitrariness of MinSets** (Vincent-Lamarre et al.: many distinct minimal grounding sets exist) ↔ the **many equivalent presentations / generating sets of one category**. Different MinSets, same category — same way different group presentations give the same group. This is a *prediction*: if the dictionary graph really behaved like a category, MinSets should be inter-translatable in a structured way, not arbitrary noise.
- The **Kernel** (recursively irreducible core) is the part of C that is not freely generated from anything smaller — the "irreducible relata," the obvious candidates for "where grounding must bottom out." Picard's Kernel/Core/Satellite anatomy then says: grounding is *graded*, not binary — which is itself friendlier to A than to a hard-residue reading.

**Why not B (genuine fight, someone is wrong):** B only bites if you collapse the scope distinction — i.e., if you insist that the agent's conceptual universe just *is* whatever relational structure its current symbols instantiate, full stop, no prior question of "which structure." That is thoroughgoing structuralism / pure (narrow) conceptual-role semantics. If you take that line, then yes: Yoneda says that's all there is and Harnad is wrong **— but then the bill comes due in mathematics.** If "an object's content = its structural role, no residue, ever," then mathematical objects have no residue either, and you owe an account of how the ambient category *itself* gets any content (the Benacerraf access problem; Hellman's "structures without structures" worry). You cannot consistently say "for concepts, relational role is everything (so Harnad's wrong)" while also feeling the force of "for numbers, *something* must pin down which structure we're talking about (the access problem is real)." Either there's a residue (selection/access) in both cases — that's A — or in neither, and then you've signed up to a very strong structuralism whose own house isn't in order. **B's stable form isn't "Harnad loses"; it's "the symmetry — math has a grounding problem too."** That's a real result, but it's a *consequence* of A's scope analysis, not a refutation of it.

**Why C is only a light thumb:** see §4.

---

## 4. Empirical adjudication via the dictionary graph

### 4.1 The C-claim and why the data only weakly supports it

Resolution C's bet: if **extra-graph** features (concreteness, age-of-acquisition, sensory ratings) *add real predictive power for "which layer a word lands in" given the purely structural graph features*, then something outside the relational structure is doing explanatory work — a thumb for Harnad. Vincent-Lamarre et al. 2014 reported exactly this kind of correlation: words in/near the Kernel skew earlier-acquired, more concrete, more frequent. **That is genuine, replicated.** But it is weak as an *anti-Yoneda* argument, for three reasons:

1. **Correlation ≠ residue.** Concreteness/AoA could be *causes* of a word's graph position (concrete, early words get used in many definitions ⇒ high out-degree ⇒ shallow layer) without being any *part of the word's meaning that the relations miss*. Harnad needs the latter; the data shows the former. A structuralist happily says: "of course the carving of C tracks sensorimotor salience — that's *consistent* with concepts being exhausted by their role *in the C that salience carved*." Which is just Resolution A again.
2. **The dictionary graph is not actually a category.** Edges are "appears-in-the-definition-of" — there's no honest composition, no identities, no functoriality; it's a digraph, not a category. So "the dictionary graph adjudicates Yoneda" is already a stretch: Yoneda is a theorem about categories, and a definitional digraph fails the axioms. It's a *suggestive analogue*, not a worked instance.
3. **Layer is itself a structural feature.** "Which layer" = definitional distance from the seed in the digraph — it's *defined by the graph*. So "do structural features predict layer" is nearly tautological; the only non-trivial version is "does the *residual* of layer, after the obvious structural predictors (degree, PageRank, SCC membership), get explained by extra-graph features?" — which is the regression in §4.3, and which **cannot be run on shipped data.**

### 4.2 What *can* be run now (structural-only descriptive — done)

From `reports/oewn-paper-wordnet-layers.json` (paper-wordnet graph, exact-small-greedy seed; 160,010 nodes; kernel = 12,853 nodes ≈ 8.0%; core = 288; satellites = 12,565; seed = 2,370) and `reports/oewn-paper-wordnet-kernel-summary.json`:

- **Layer histogram is heavy-headed:** layer 0 = 2,370 nodes (the seed), layer 1 = 1,614, decaying to a long thin tail out to layer 64; mean layer ≈ 12.2, median = 5.
- **POS composition shifts with depth** (kernel-node lemmas, banded):
  - L0 (seed): 72% noun, 16% adj, 10% verb, 3% adv
  - L1–3: 51% noun, 32% adj, 8% adv, 9% verb
  - L4–10: 61% noun, 29% adj
  - L11+: 77% noun, 17% adj, 4% verb
  Adjectives bulge in the shallow-but-not-seed band; deep layers are noun-dominated. (Plausible structural story: adjectives have low out-degree but get pulled in early by many noun definitions; obscure technical nouns sit deep.)
- **Multiword fraction by band:** L0 14%, L1–3 14%, L4–10 17%, **L11+ 21%** — multiword terms (`abdominal_aorta`, `myotonic_dystrophy`) concentrate in the deep tail. Again a structural fact (multiword expressions are leaves: rarely *used in* others' definitions).
- **Top out-degree nodes** (the structural "hubs" — what a Yoneda-style account would call the high-fan-out generators): `small[n]` (out-deg 4878), `large[n]` (3497), `white[n]` (2073), `tropical[a]` (1938), `can[n]` (1788). These are exactly the kind of concrete/early/high-frequency words V-L's correlations are about — *and* they're identifiable from the graph alone. That's the §4.1(1) point made concrete: the structural and the psycholinguistic stories point at the same words, so the data underdetermines which is doing the explaining.

**What this descriptive shows:** the Kernel/Core/Satellite split and the layer index are *entirely graph-derived* and already carve the lexicon into bands that look psycholinguistically meaningful — i.e., a lot of the apparent "extra-graph signal" is *recoverable from structure*. That's mildly *pro-Yoneda*. It does **not** settle whether there's residual extra-graph signal, because that needs the norms.

### 4.3 The regression to run once norms are in the repo (precise spec)

**Data join:** for each single-word kernel-node lemma in `layer_by_node` (~9,897 of them; or use the lemma graph, ~10,430 kernel nodes), attach: concreteness (Brysbaert, Warriner & Kuperman 2014, ~40k words), age-of-acquisition (Kuperman, Stadthagen-Gonzalez & Brysbaert 2012, ~30k words), log word frequency (SUBTLEX-US Zipf), and if available a sensory-experience rating (Juhasz & Yap 2013) or the Lancaster sensorimotor norms (Lynott et al. 2020). Put these CSVs in `data/psycholinguistic/` with a `word` column; the existing `--annotations` flag and `src/meanings/annotations.py` ingest them as-is. Expected coverage: roughly 50–70% of single-word lemmas (proper nouns, multiword, technical terms drop out — note and report the coverage, and check it's not differentially missing by layer, which would itself be a finding).

**Outcome variable:** `layer` (count; or, more robustly, `is_kernel`/`is_core`/`is_satellite` as an ordered factor, or log(1+layer)). Use negative-binomial regression for the count (layer is over-dispersed) or ordinal logistic for the band.

**Models (nested, compare by ΔAIC / likelihood-ratio test and ΔR²):**
- **M0 (extra-graph only):** layer ~ concreteness + AoA + log_freq + POS.
- **M1 (structural only):** layer ~ out_degree + in_degree + log(out_degree+1) + PageRank + SCC_size + is_in_largest_SCC + POS. (All computable from the graph the CLI already builds.)
- **M2 (structural + extra-graph):** M1 + concreteness + AoA + log_freq.

**The test:** *partial R² of the extra-graph block, added to M1* — i.e., R²(M2) − R²(M1), and the LR test M1 vs M2. Also report standardized coefficients of concreteness/AoA *in M2* (after structure is partialled out).

**Decision rule (pre-registered):**
- If extra-graph partial R² **> ~0.05** and concreteness/AoA stay significant with non-trivial standardized β in M2 ⇒ **real residue ⇒ thumb for Harnad / against Yoneda-completeness.** Report effect size, don't just report p.
- If extra-graph partial R² **< ~0.01** (structure already absorbs almost everything) ⇒ **pro-Yoneda:** the "psycholinguistic" signal *is* the structural signal; concreteness etc. are screened off by degree/PageRank. This is the §4.2 trajectory's natural extrapolation.
- In between ⇒ honest "mixed; the residue is small but nonzero," which is *itself* most consistent with Resolution A's "graded grounding."

**Why I didn't run it:** the norm databases are external multi-MB CSVs; fetching and integrity-checking them through the available tools is unreliable and out of scope for this brief, which explicitly says "note whether the data to run it already exists in the repo" — it does not. The pipeline is ready; the data is a one-command add.

### 4.4 What the §4.3 result would and wouldn't license

Even a *strong* extra-graph residue would only show that **the definitional digraph under-describes word usage** — which everyone already grants (a dictionary isn't a mind). It would be a thumb for Harnad's *spirit*, not a disproof of Yoneda, because (a) Yoneda is about categories and this isn't one, and (b) the residue would be exactly the "category-selection residue" of Resolution A, not an "object-identity-within-the-category residue." So C, run either way, lands you back at A. That's *why* the verdict is A and not C.

---

## 5. Verdict

**Resolution A**, stated without hedging:

> **Yoneda and Harnad are not contradictory; they are about different things.** Yoneda fixes the identity of an object *within a given category*; Harnad's residue is the residue of *which category an agent is in* — which relata exist and which relations are real — and that is fixed non-symbolically (sensorimotor categorization). The synthesis: **grounding = constructing/selecting the base category; Yoneda then takes over inside it.** A grounded concept genuinely is "nothing but its relations" — *in the category that grounding built*. The dictionary-kernel apparatus is the toy model of this: Kernel = the irreducible relata, MinSets = generating sets / equivalent presentations of the same category, MinSet-arbitrariness = presentation-non-uniqueness, the Kernel/Core/Satellite gradient = grounding is graded.

With the **symmetry rider** (the live edge of B): anyone who rejects A by going full structuralist ("relational role is *all* there is, for concepts *and* for numbers") thereby owes mathematics a grounding story — the Benacerraf access problem is Harnad's problem wearing a different hat. You don't get to apply structuralism asymmetrically. So the *interesting* contrarian position isn't "Harnad is wrong" — it's "fine, then math has a grounding problem too," and that's a thesis worth writing down, not a refutation of A.

The dictionary-graph evidence (Resolution C) is **real but light**: it shows the graph layers track psycholinguistic gradients, but (i) the graph isn't a category, (ii) layer is itself structural, (iii) correlation underdetermines residue, and (iv) the proper residual test can't be run on shipped data. Run §4.3 and, whichever way it lands, it confirms A's framing.

**What I could not verify:** (1) the headline regression — no psycholinguistic norms in the repo; spec given. (2) Whether *some* obscure paper bridges Yoneda and symbol grounding — searched four ways, found only the peripheral Seremeti & Kameas 2013 engineering paper and the standard Yoneda-as-philosophy expositions (math3ma, Milewski, Tao's "form and function" post, nLab); I can't prove a negative, but the disjointness is as clean as a literature search gets. (3) Whether DisCoCat insiders have *informally* discussed grounding — the published record doesn't; conference talks I can't see.

---

## 6. Proposed output paper

- **Title:** *Yoneda's Mind: Why "An Object Is Its Relations" and "Symbols Need Grounding" Are the Same Theorem Read at Two Scopes.* (Alt: *Grounding the Base Category: Reconciling the Yoneda Lemma with the Symbol-Grounding Problem.*)
- **Thesis:** The Yoneda lemma and Harnad's symbol-grounding problem make the same claim about constitution-by-relations, evaluated at different quantifier scopes — inside a fixed category vs. about category-selection — and are therefore compatible; the synthesis ("grounding = building the base category, then Yoneda applies within it") is formally exhibited on the dictionary-kernel model, where MinSets are generating sets and the Kernel/Core/Satellite stratification is graded grounding; and the corollary is a symmetry result — thoroughgoing structuralism inherits the grounding problem in mathematics (the Benacerraf access problem), so the residue is real in both domains or neither.
- **Empirical contribution:** the §4.3 regression on a real dictionary digraph (OEWN) — structural vs. extra-graph variance in definitional depth — as the first quantitative probe of "how much of word meaning is non-relational residue," with the OEWN/MinSet pipeline in this repo as the artifact.
- **Venue:** the natural home is the **applied-category-theory / DisCoCat community** — *Applied Category Theory (ACT)* conference, *Compositionality* journal, or the *SemSpace / QNLP* workshops — because that audience already has the categorical machinery and is conspicuously missing the grounding question. Secondary: a philosophy-of-cognitive-science venue (*Minds and Machines* — Harnad-adjacent; *Synthese*; *Philosophy & Technology*). Worst case it's two papers: the philosophical reconciliation for *Minds and Machines*, the OEWN regression for an *NLP/cognitive-modeling* venue (e.g., *CogSci*, *Computational Linguistics* short).
