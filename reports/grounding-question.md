# The Grounding Question

**Date:** 2026-07-14
**Type:** anchor document. This states the question the whole stack serves, so it cannot be lost again. Reconstructed from the seam between `meanings/` and `../propstore` after it went missing in exactly that seam.

---

## 1. The question

Propstore is an epistemic operating system: it stores claims, concepts,
contexts, stances, justifications, and arguments, with typed identity,
provenance, and formal reasoning backends. But identity is not meaning.
The question is:

> **By what mechanism do the symbols in an epistemic operating system — its
> concepts, and the words their definitions bottom out in — carry meaning
> that is not merely borrowed from the human interpreter reading them?**

That is Harnad's symbol grounding problem (1990), posed operationally rather
than philosophically: what is the grounding relation, what supplies it, where
must it enter, and how does the store represent, propagate, and verify it?

The question spans two repos, which is why neither states it. Propstore
solves *what things are* (typed objects, stable identity, IC merge,
provenance). `meanings/` is the running attack on *what things mean*. The
propstore paper collection (argumentation, belief revision, provenance,
replication) contains no Harnad, Massé, or Vincent-Lamarre; those live here.
Working inside either repo alone loses the question.

## 2. Why the stack exists (the orphaned layer)

The sibling repos map almost one-to-one onto the classical "maintained
justified belief" literatures:

| repo | literature |
| --- | --- |
| `quire` | content-addressed typed storage (git plumbing) |
| `cel-parser` / `condition-ir` | typed condition evaluation |
| `belief-set` | AGM revision, Spohn ranking, IC merge |
| `argumentation` | Dung / ASPIC+ / ABA / ADF, gradual + ranking semantics, ASP/Z3 kernels |
| `gunray` | defeasible logic, four-valued verdicts |
| `doxa` | Jøsang subjective logic (explicit uncertainty mass) |
| `provenance-semiring` | provenance algebra |
| `propstore` | the OS composing them over claims/concepts/contexts/stances |
| `meanings` | symbol grounding (this document's question) |

The layer these compose — machine-maintained justified belief: what is
believed, why, on whose authority, with what uncertainty, and what to retract
when evidence changes — was started and abandoned. Doyle's TMS (1979) and de
Kleer's ATMS (1986) were this layer; the lineage died with the AI winter.
Cyc attempted the content without the epistemic discipline. The Semantic Web
layer cake never built its top layers: *proof* and *trust* were on the
diagram and were never implemented. The component theories (AGM, Dung,
subjective logic, provenance semirings, defeasible logic) then matured for
thirty years in silos, mostly as paper-math. Nobody stood in the one place
where they compose. (The project has independently documented the silo
phenomenon twice: the Perron–Frobenius convergent-rediscovery paper outline,
and the FVS-control-biology vs dictionary-grounding non-citation.)

The demand signal is recent: LLMs are fluent symbol manipulators with no
provenance, no revision discipline, and no grounding — Harnad's problem at
industrial scale. The stack is not a rejected idea; it is an orphaned one.

One design property worth naming because it is easy to mistake for scope
creep: the system is **self-applicable**. The replication literature in
propstore's collection is not background reading — field replication rates
enter as first-class facts the system can defeasibly reason *with* and argue
*about*, so the apparatus that judges claims is itself made of claims the
same machinery maintains. The epistemics are data. This is the property
that lets §4's third grounding-supply candidate work at all.

## 3. The stabs and their verdicts

Each attack on the question, with its returned verdict and pointer:

1. **Structural / combinatorial** (Kernel, MinSet ⇔ feedback vertex set).
   **Survived, as a locator.** The graph says exactly *where* external
   meaning must enter (a ~3% FVS) and proves the rest unfolds once it does.
   It cannot supply the meaning — Harnad's constraint holds under
   formalization. → `reports/swanson-synthesis.md`,
   `reports/argumentation-bridge-oewn.md`, the standard-MinSet theorem.

2. **Spectral / ranking valuation** (reverse-PageRank, gradual argumentation
   semantics). **Dead.** Everything collapses to degree (ρ ≈ 0.99 full
   graph); there is no hidden continuous foundationalness signal in the bare
   digraph. Clean negative with a mechanism (graph homogeneity).
   → `reports/spectral-valuation-oewn.md`, `reports/ranking-valuation-oewn.md`.

3. **Psycholinguistic anchoring** (frequency / AoA / concreteness as external
   grounding signal). **Blocked, not dead** — the lexicographer's confound
   makes it un-adjudicable on one dictionary. Named discriminators:
   cross-dictionary stability (LDOCE), and Lancaster sensorimotor norms used
   as a causally-upstream instrument.
   → `reports/psycholinguistic-regression-findings.md`.

4. **Assembly-language engineering** (pressure table, bucket-promotion
   cycles, closure validator). **Constructive path, live.** If grounding is
   solved for a small base (~326 ICs), definitional closure inherits it
   outward; currently 20.45% of admitted senses close under ≤200-step
   closure. → `reports/kaikki-obstruction-workstream.md`,
   `scripts/validate_assembler_definitions.py`.

5. **Argumentation / defeasible representation** (Dung grounded extension;
   gunray's four-valued UNDECIDED). **The honest representation of partial
   grounding.** A circular definition sits at UNDECIDED until a grounding
   fact enters, then resolves — "recursive definability ≠ meaning" as
   executable code. → `reports/synthesis-facet-philosophy-codex.md` §
   foundationalism/coherentism; the Yoneda/Harnad note outline.

6. **G = I(X;V), grounded content** (2026-05 detour, now wired into the
   validator). **The positive theory sketch.** Grounding as
   apparatus-relative mutual information between outputs and verdicts. This
   generalizes Harnad's "nonsymbolic capacities" to *any verification
   apparatus* — and propstore already grounds **claims** exactly this way
   (provenance to studies, measurements, verdicts). G proposes grounding
   **words** the same way. Instrument finding: different coarsenings rank
   the promotion cycles oppositely (artifact bought resolution, background
   bought closure mass) — "is this progress?" has no apparatus-free answer,
   so the apparatus must be declared, not discovered.
   → `scripts/grounded_content.py`, `reports/base-assembler-validation.md`
   § Grounded Content.

## 4. How the components compose

The stabs are components, not rivals:

- The **graph** says *where* grounding must enter: a small base
  (FVS/MinSet/kernel pressure).
- The **apparatus relation** (G; norms; verdict contact) says *what*
  grounding *is* at that base.
- **Definitional closure** (the assembler) propagates it outward.
- **Argumentation/defeasible semantics** represents partial and circular
  grounding without lying about it.
- The **Harnad constraint** polices over-claiming throughout: recursive
  definability is never meaning; a MinSet is never a set of human semantic
  primitives.

The missing middle term is the **grounding supply for the base**: an actual
source of apparatus contact for the ~326 base ICs. Candidates on the table:

- Lancaster sensorimotor norms as a causally-upstream instrument (dodges the
  lexicographer's confound);
- cross-dictionary stability (OEWN vs LDOCE — also the confound
  discriminator the lead paper needs);
- propstore's own verdict machinery pointed at the base vocabulary: treat
  each base IC as a concept whose grounding is a provenance-backed,
  uncertainty-scored claim, and let G measure how much verdict information
  the base actually carries. Because the apparatus is self-applicable (§2),
  the reliability of a grounding claim's sources — replication rates
  included — is itself a defeasible fact in the store, so base grounding
  inherits the same revision discipline as everything else.

## 5. Calibration: the "vision in a summer" worry

The 1966 summer vision project failed because vision resisted decomposition
and nobody knew the primitives. This problem is in the opposite condition:
the decomposition is done (§2–§4), every component has thirty years of
literature, and each component exists as working, citation-anchored code on
this machine. What remains is one open scientific question (the grounding
supply, §4) and integration engineering.

Scope honesty, so "close" means something:

- **Not close, and not claimed:** intrinsic meaning for an agent — full
  Harnad, sensorimotor grounding of a mind. Out of scope by construction.
- **Plausibly close:** *grounding for an epistemic OS* — every symbol in the
  store either (a) carries a provenance-backed, uncertainty-scored,
  apparatus-relative grounding record, (b) inherits one through definitional
  closure with an inspectable derivation chain, or (c) is explicitly marked
  UNDECIDED/ungrounded. That is a finishable engineering target, and it
  would be the first system since the ATMS era to attempt it end-to-end.

**Falsifiers for "we are close":**

- No instrument for the confound: if Lancaster norms + a second dictionary
  still cannot separate "graph encodes psycholinguistic salience" from
  "salience is relational," the base has no non-circular external anchor.
- Closure stalls: if hand-authoring the base YAML (deferred Phase 5C) plus
  promotion cannot push closure well past ~20% without huge closures or
  artifact exceptions, the assembly-language hypothesis weakens (the
  validator already encodes this falsifier).
- Apparatus disagreement is unresolvable: if every choice of coarsening
  yields a different progress ranking *and* no principled ground exists for
  declaring one, G degenerates into metric shopping.

## 6. Standing decisions

- The headline G apparatus (which coarsening judges progress) is a human
  declaration, not a computation. Currently: fine coarsening at
  `closure_size ≤ 200`. Owner: Q.
- Sibling repos advance only when a propstore need pulls them; this
  document is the map of which need pulls what.
