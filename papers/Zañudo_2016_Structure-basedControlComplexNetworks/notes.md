---
title: "Structure-based control of complex networks with nonlinear dynamics"
authors: "Jorge G. T. Zañudo, Gang Yang, Réka Albert"
year: 2017
venue: "Proceedings of the National Academy of Sciences (PNAS) 114(28): 7234-7239"
doi_url: "https://doi.org/10.1073/pnas.1617387114"
pages: "7234-7239 (arXiv v3 preprint 1605.08415, 33pp incl. SI)"
arxiv_id: "1605.08415"
---

# Structure-based control of complex networks with nonlinear dynamics

## One-Sentence Summary
A network's *feedback vertex set* (FVS) plus its *source nodes* form a structure-based control set: overriding the state of those nodes is sufficient to drive any nonlinear-dynamic network governed by Eq. 1-2 to any of its natural attractors regardless of the functional forms — and empirically this set is *tiny* for biological networks (1-18% of nodes) while structural-controllability (maximum-matching) driver sets for the same networks are huge (75-96%), with the relationship flipped for social/intra-organizational networks.

## Problem Addressed
Structural controllability (Liu–Slotine–Barabási 2011) assumes linear/linearized dynamics and "full control" (any state to any state via input signals u(t)) — a notion that mismatches biological/social/technological systems, where control means steering to *naturally occurring* states (attractors). The paper asks: what can we say about controlling a *nonlinearly* dynamic networked system from its wiring diagram alone? It adapts Fiedler–Mochizuki feedback vertex set control (FC) to networks with source nodes, applies it to many real networks, and contrasts it with structural controllability (SC).

## Key Contributions
- Extends Fiedler–Mochizuki–et-al. FVS control (FC) to networks with source nodes: control set = **FVS ∪ source nodes** *(p.2-3)*.
- Proves (via prior FC theory + SI) that overriding the state of all control-set nodes onto a target attractor's trajectory drives the whole network asymptotically to that attractor, for *any* bounded nonlinear dynamics of the form Eq. 1 *(p.2)*.
- Empirical comparison of FC control-set size n_FC vs. structural-controllability driver-set size n_SC across many real network classes; identifies cycle structure (SCCs, short cycles) as what determines n_FC *(p.3-5)*.
- Shows FC is a model-independent *upper bound* on attractor-control set size for parameterized dynamic models (Drosophila segmentation ODE + Boolean models): full FVS (52 nodes, 0.74/0.35 and 0.5/0.18 of network) overrides to wild-type attractor; only 16 (12) of those nodes needed in the specific model *(p.6)*.

## Study Design (empirical comparison component)
- **Type:** computational analysis of real-world network datasets + dynamic-model case studies.
- **Population:** ~real networks across classes: regulatory, metabolic, food-web, neural, WWW, internet, electronic circuits, trust, citation, social-communication, intra-organizational, power grid (full list / sizes in SI Appendix Table S1) *(p.3-4)*.
- **Methods compared:** (i) FC — needs only the digraph; control set = FVS (computed with fast near-minimal heuristics, since exact min-FVS is NP-hard) plus all source nodes. (ii) SC — Liu et al. maximum-matching driver-node identification on the same digraph *(p.1-5)*.
- **Outcomes:** n_FC / N and n_SC / N (fraction of nodes that must be controlled); contribution of source nodes vs. FVS; relation of n_FC to SCC size n_SCC and to short-cycle count; comparison to degree-preserving and SCC-preserving randomized network ensembles *(p.3-4)*.
- **Dynamic-model case studies:** von Dassow et al. ODE model and Albert–Othmer Boolean model of Drosophila embryonic segment-polarity gene network *(p.6)*.

## Methodology / Framework
System of N nodes: N_s source nodes (no incoming edges) with variables S_j(t), N − N_s internal nodes with variables X_i(t):

$$
\frac{dX_i}{dt} = F_i(X_i, X_{I_i}, t), \qquad \frac{dS_j}{dt} = G_j(t)
$$

Where: i = 1,…,N−N_s indexes internal nodes; j = N−N_s+1,…,N indexes source nodes; I_i = predecessors of node i (source or internal); F_i is nonlinear in predecessors and **includes decay in X_i** (e.g. F_i = f_i(X_{I_i}) − α_i(X_{I_i})·X_i). Source dynamics G_j depend only on t (independent of internal nodes); simplest case G_j = 0 so S_j stays at its initial value. Such systems possess naturally occurring end states = dynamical attractors (steady states, limit cycles) that in biology = cell fates, in social = opinion-consensus states, in epidemics = endemic states *(p.1-2)*.

**FVS control (FC) core claim (Fiedler–Mochizuki et al.):** A *feedback vertex set* is a node set intersecting every directed cycle (feedback loop) in the digraph; removing it makes the graph acyclic. For dynamics of the form Eq. 1, *overriding* (forcing) the state variables of the FVS into the trajectory specified by a chosen attractor of Eq. 1 guarantees the network asymptotically approaches that attractor, **independent of the functional forms F_i**. FC uses *node-state override* as the control action (not a controller/driver signal u(t)) — matching interventions like genome editing, drug treatment, vaccination *(p.2)*. Controlling the FVS is *sufficient* for every form of F_i and *necessary* if sufficiency must hold for *every* F_i. Identifying the *minimal* FVS is NP-hard; near-minimal heuristics (GRASP etc., SI) are used *(p.2)*.

**Adaptation to source nodes:** Source nodes encode external stimuli / boundary conditions; different attractors may exist for each source state. They're iteratively removed from the network *before* applying FVS control, then re-attached to the control set. So the full structure-based control set = **FVS of the source-stripped digraph ∪ all source nodes** *(p.2-3)*. (Fig. 1.)

## Key Equations / Quantities

$$
n_{FC} = \frac{|\text{FVS} \cup \text{source nodes}|}{N}, \qquad n_{SC} = \frac{|\text{maximum-matching driver set}|}{N}
$$
Where: N = number of nodes; n_FC = FC control fraction; n_SC = structural-controllability driver fraction. *(p.3-5)*

$$
n_{SCC} = \frac{|\text{largest strongly connected component}|}{N}
$$
Strong correlation observed between n_FC and n_SCC, and with the number of short directed cycles (length ≤ 4) *(p.3-4)*.

## Parameters / Key Quantities

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| FC control fraction, biological/regulatory nets | n_FC | fraction of N | — | 0.01–0.18 (1–18%) | p.4-5 | feedback-vertex-set-based; matches the "biological regime" |
| SC driver fraction, gene-regulatory nets | n_SC | fraction of N | — | 0.75–0.96 (75–96%) | p.4-5 | maximum-matching / structural controllability — opposite extreme from n_FC |
| Largest SCC fraction, intra-organizational nets | n_SCC | fraction of N | — | large (close to 1) | p.4 | high n_SCC ⇒ large FVS contribution |
| Largest SCC fraction, social-communication / most trust / WWW nets | n_SCC | fraction of N | — | 0.46–0.91 | p.4 | intermediate |
| Largest SCC fraction, food-web / circuits / gene-regulatory nets | n_SCC | fraction of N | — | < 0.40 | p.4 | small SCC ⇒ small FC control set |
| Min FVS computation | — | — | — | NP-hard | p.2 | near-minimal heuristics used (GRASP, SI) |
| Drosophila segment-polarity network size | N | nodes | 60 (per cell × 4 cells; FVS = 52) | — | p.6 | von Dassow ODE & Albert–Othmer Boolean |
| FVS of Drosophila model | n_FVS | nodes | 52 | — | p.6 | n_SCC/n_FVS = 0.74/0.35 (ODE) and 0.5/0.18 (Boolean) of network |
| Model-specific control nodes, Drosophila ODE model | — | nodes | 16 | (of 52 in FVS) | p.6 | 66% reduction vs full FVS |
| Model-specific control nodes, Drosophila Boolean model | — | nodes | 12 | (of 52 in FVS) | p.6 | 14% reduction; cf. Mochizuki et al. found 5 of 7 FVS nodes for mammalian circadian model |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | Context | Page |
|---------|---------|-------|---------|------|
| Biological networks easier to control by FC | n_FC | 1–18% of nodes | gene-regulatory / regulatory class | p.4-5 |
| Same biological networks hard to control by SC | n_SC | 75–96% of nodes | gene-regulatory class — n_SC ≫ n_FC | p.4-5 |
| n_SC ≫ n_FC also holds | qualitative | yes | food-web networks, internet networks | p.4-5 |
| Opposite relation n_SC ≪ n_FC | qualitative | yes | social trust networks (low n_SC), intra-organizational networks | p.4-5 |
| FC set size vs degree-preserving randomization | comparison | n_FC > n_FC^{Rand-Deg} for most networks (real nets need MORE control nodes than randomized) | exceptions: food-web & citation networks (near-acyclic) where n_FC < n_FC^{Rand-Deg} | p.4 |
| FC set size vs SCC-preserving randomization | comparison | excellent agreement (n_FC ≈ n_FC^{Rand-SCC}); also agrees with short-cycle-preserving randomization | exceptions: near-acyclic food-web & citation nets | p.4 |
| Drosophila ODE model: full-FVS override → wild-type attractor | — | works (52 nodes) | model-independent upper bound | p.6 |
| Drosophila ODE model: minimal model-specific control | — | 16 nodes (66% reduction from FVS) | model-dependent | p.6 |
| Drosophila Boolean model: minimal model-specific control | — | 12 nodes (14% reduction from FVS) | model-dependent | p.6 |

## Methods & Implementation Details
- FC control set computation: (1) iteratively strip source nodes from the digraph; (2) compute a near-minimal feedback vertex set of the remaining digraph (exact min-FVS is NP-hard — use fast heuristics, GRASP-based subroutines etc., SI Appendix); (3) control set = that FVS ∪ the stripped source nodes *(p.2-3)*.
- SC comparison: standard Liu–Slotine–Barabási maximum-matching driver-node identification on the same digraph *(p.1, 5)*.
- Cycle-structure diagnostic: count strongly connected components, largest-SCC fraction n_SCC, number of short directed cycles (length ≤ 4); these correlate with / explain n_FC *(p.3-4)*.
- Randomized null models: degree-preserving randomization (n_FC^{Rand-Deg}), SCC-preserving randomization (n_FC^{Rand-SCC}), and short-cycle-preserving (cycles length ≤ 4) randomization *(p.4)*.
- Dynamic-model validation: lock the FVS (or a subset) into the wild-type-attractor trajectory in von Dassow ODE and Albert–Othmer Boolean Drosophila segment-polarity models; verify convergence; then search for the *minimal* subset of the FVS that still works in that specific model *(p.6)*.
- Why cycles matter for the FC vs SC discrepancy: in FC, *cycles must be directly controlled* (one node per cycle, via the FVS). In SC, cycles need *no* independent control as long as a directed path reaches them from a linear chain of nodes; SC instead directly controls the *top* node of each non-intersecting linear chain. Hence networks rich in cycles (gene-regulatory) → small n_FC, large n_SC; near-acyclic networks (food webs, citation, tree-like web) → small n_FC; chain-heavy networks → large n_SC small in some, small SC large FC in trust/org nets *(p.4-5, Fig. 3b)*.

## Figures of Interest
- **Fig. 1 (p.3):** Worked example of structure-based control with nonlinear dynamics; (a) adaptation to source nodes; (b-e) small examples showing FVS nodes, source nodes, FC control set; (e) FC requires controlling all cycles via the FVS plus source nodes; SC requires top-of-chain nodes but no cycle control.
- **Fig. 2 (p.4):** Scatter plots of n_FC vs. n_SCC for real networks (colored by source-node contribution); n_FC vs degree-preserving randomization (n_FC^{Rand-Deg}); n_FC vs SCC-preserving randomization (n_FC^{Rand-SCC}); cycle-length distributions (cycles of length 1–4) for selected real networks vs. randomized ensembles; n_FC ≫ n_FC^{Rand-Deg} and n_FC ≪ n_FC^{Rand-Deg} cases.
- **Fig. 3 (p.5):** (a) Scatter of n_SC (structural controllability fraction) vs n_FC across all networks — biological cluster low-n_FC/high-n_SC, social cluster the reverse; (b) the three illustrative small networks showing how cycle structure makes n_FC ≷ n_SC (left: many cycles → n_FC > n_SC; right: acyclic → n_FC < n_SC).
- **Fig. 4 (p.6):** Control of the Drosophila segment-polarity gene network — (a) ODE model with control nodes; (b) Boolean model; (c-e) wild-type stable gene-expression pattern recapitulated by overriding the FVS; (f) time courses.

## Results Summary
- For nonlinear-dynamic networks, FC = FVS + source-node override is a *sufficient* (and in the worst-case-over-functions *necessary*) structure-based control set *(p.2)*.
- n_FC is governed by cycle structure: large SCC / many short cycles ⇒ large n_FC; near-acyclic ⇒ small n_FC; n_FC ≈ SCC-preserving-randomized value *(p.3-4)*.
- **The headline empirical contrast:** biological / gene-regulatory networks need only 1–18% of nodes for FC but 75–96% for SC; the n_SC ≫ n_FC pattern also holds for food-web and internet networks; the *opposite* (n_SC ≪ n_FC, i.e. small driver set but large FVS) holds for social trust networks and intra-organizational networks. Warns against naively applying SC *or* FC outside its proper domain of dynamics / control objective / control action *(p.4-5)*.
- FC provides a model-independent upper bound on attractor-control set size; specific parameterized models can do much better (Drosophila: 16/12 of 52 FVS nodes) *(p.6)*.

## Limitations
- FC gives no controller signal u(t) — only identifies which nodes to override; building the actual time-course override and the difficulty of steering toward a desired state are left to control theory (concepts SC handles) *(p.7)*.
- Minimal FVS is NP-hard; results use near-minimal heuristics, so reported n_FC are upper estimates of the true minimum *(p.2)*.
- FC requires controlling *all* source nodes (no independent control of them in the basic formulation) *(p.2)*.
- Open: the level of control provided by a *subset* of the FVS in the general (functional-form-independent) case *(p.7)*.
- Near-acyclic networks (food webs, citation, tree-like web) are exceptions in several analyses — short-cycle structure can't capture their near-acyclicity, and randomized comparisons need them treated separately *(p.4)*.

## Arguments Against Prior Work
- Structural controllability (Liu et al. 2011) and other linear/full-control methods assume "full control" (any state to any state) which does not match the meaning of control in biological/technological/social systems where control = steering to naturally occurring (attractor) states *(p.1)*.
- SC's prediction that biological networks are *hard* to control (large driver set) directly contradicts FC's finding that they are *easy* — both use only structure but answer different questions (different dynamics: linear vs nonlinear; different objective: full vs attractor control; different action: controller signal vs node-state override) *(p.4-5)*.
- Other nonlinear-control-theory methods exist but only FC can be reliably applied to *large* complex networks when only structure is known and functional forms aren't specified *(p.1)*.

## Design Rationale
- Node-state override (not driver signal) is chosen because that's what real biological interventions are — genome editing, drugs, vaccination *(p.2)*.
- Attractor control (not full control) is chosen because attractors correspond to the biological/social states of interest (cell fates, opinion consensus, endemic states) *(p.2, 7)*.
- Source nodes stripped first, then re-added: they encode external boundary conditions and provide positional information; a different attractor set may exist per source state *(p.2)*.

## Testable Properties
- For Eq.-1-type dynamics: overriding all FVS-∪-source nodes onto a target-attractor trajectory ⇒ network converges to that attractor, for *any* F_i *(p.2)*.
- n_FC correlates positively with n_SCC and with the count of short cycles (≤ length 4) *(p.3-4)*.
- n_FC ≈ n_FC of an SCC-preserving (or short-cycle-preserving) randomized version of the same network — except near-acyclic networks *(p.4)*.
- For gene-regulatory networks: n_FC ∈ [0.01, 0.18] and n_SC ∈ [0.75, 0.96], with n_SC ≫ n_FC *(p.4-5)*.
- For social trust / intra-organizational networks: n_SC ≪ n_FC *(p.4-5)*.
- For a parameterized model on a given network, the minimal attractor-control node set ⊆ the FVS (FC is an upper bound) *(p.6)*.

## Relevance to Project
This is the empirical anchor for the FVS-vs-matching comparison in the `meanings` OEWN definition-digraph work. The OEWN graph (definitions referencing other lemmas) reportedly sits in the *biological-network regime*: ~1.5% FVS-seed (the "lexical grounding set" / MinSet that breaks all definitional cycles) vs ~74% maximum-matching driver nodes — i.e. n_FC ≈ 0.015, n_SC ≈ 0.74, matching the gene-regulatory cluster (n_FC 1–18%, n_SC 75–96%). The paper's mechanism — *cycles must be directly controlled in FC but not in SC* — is exactly why a definition digraph with many short definitional cycles has a small FVS-seed: pinning one word per definitional cycle (the "primitive" / undefined-term set) suffices to ground every definition, whereas maximum-matching would demand a driver per chain. The FC theory's functional-form-independence is the formal justification that the grounding set works regardless of how downstream definitions compose. Fiedler–Mochizuki FC theory (refs 3, 21) and Mochizuki et al. (ref 21) are the upstream proofs; this paper supplies the cross-domain calibration.

## Open Questions
- [ ] What does a subset of the FVS control in the general (function-independent) case? (paper's stated open problem)
- [ ] How tight is the n_FC ≈ SCC-preserving-randomized estimate for *lexical* digraphs specifically?
- [ ] Does the OEWN digraph's source-node fraction (words appearing in no definition? mono-semous primitives?) contribute to n_FC the way it does in the regulatory networks here?

## Related Work Worth Reading
- Mochizuki, Fiedler, Kurosawa, Saito (2013), *J Theor Biol* 335:130–146 — "Dynamics and control at feedback vertex sets II" (ref 21) — the core FC theorem this paper rests on.
- Fiedler, Mochizuki, Kurosawa, Saito (2013), *J Dyn Diff Eqns* 25(3):563–604 — "Dynamics and control at feedback vertex sets I" (ref 3).
- Liu, Slotine, Barabási (2011), *Nature* 473:167–173 — structural controllability of complex networks (ref 1) — the SC method compared against. → NOW IN COLLECTION: [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md)
- Zañudo, Albert (2015), *PLoS Comput Biol* 11(4):e1004193 — "Cell fate reprogramming by control of intracellular network dynamics" (ref 6) — Boolean attractor control via FVS subsets.
- Gates, Rocha (2016), *Sci Rep* 6:24456 — "Control of complex networks requires both structure and dynamics" (ref 7). → NOW IN COLLECTION: [Control of complex networks requires both structure and dynamics](../Gates_2016_ControlComplexNetworksRequires/notes.md)
- Wang, Angulo (2016), *Nat Commun* 7:11323 — "A geometrical approach to control and controllability of nonlinear dynamical networks" (ref 4).
- Newby, Albert et al. (2018+) — later FVS-control / stable-motif work (lead: NPJ Syst Appl Biol 2016, ref 26 Kawakami et al.; Albert group line).
- Liu, Barabási (2016), *Rev Mod Phys* 88(3):035006 — "Control principles of complex systems" (ref 11) — survey.

## Collection Cross-References

### Already in Collection
- [Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks](../Fiedler_2013_DynamicsControlFeedbackVertex/notes.md) — the FC control theorem this paper extends to networks with source nodes (their ref 3 / Part I).
- [Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks](../Mochizuki_2013_DynamicsControlFeedbackVertex/notes.md) — the companion Part II / monitor result (their ref 21).
- [On the minimum feedback vertex set problem: Exact and enumeration algorithms](../Fomin_2008_MinimumFeedbackVertexSetProblem/notes.md) — algorithmic backbone for computing the (NP-hard) minimal FVS used as the FC control set.
- [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md) — Liu–Slotine–Barabási (2011), their ref 1; the structural-controllability (SC) maximum-matching driver-node method that this paper's Fig. 3 scatter-plots n_SC against n_FC. SC = linear `ẋ=Ax+Bu`, full-state control, driver set = unmatched nodes of a maximum matching, n_SC = 75–96% for biological nets; FC = nonlinear, attractor steering, control set = FVS + sources, n_FC = 1–18% — the gap explained by cycle structure. The OEWN definition digraph (~1.5% FVS-seed vs ~74% matching-driver set) sits in the biological-network regime.

### Now in Collection (previously listed as leads)
- [Control of complex networks requires both structure and dynamics](../Gates_2016_ControlComplexNetworksRequires/notes.md) — Gates & Rocha (their ref 7); the negative counterpart to this paper. Where Zañudo–Yang–Albert prove FVS+sources control works regardless of dynamics, Gates & Rocha prove the *structure-only* alternatives (structural controllability / maximum matching, minimum dominating set) fail once dynamics are present — both in the *number* and the *identity* of driver variables, governed by canalization / effective connectivity. Confirms (does not conflict): the same biological-network regime (tiny FVS-set, huge matching-driver-set) that this paper documents is the regime Gates & Rocha use to show the matching-driver set is meaningless.

### Conceptual Links (not citation-based)
- [How Is Meaning Grounded in Dictionary Definitions?](../Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md) — Massé et al. prove "grounding sets = feedback vertex sets" for a definition digraph. This paper supplies the cross-domain calibration: real definition digraphs (like real gene-regulatory networks) have a *tiny* FVS, far smaller than the maximum-matching driver set — i.e. a dictionary's grounding kernel is small for the same structural reason a biological network's FC set is small (cycles must be hit once, not driven from a chain).
- [The Latent Structure of Dictionaries](../Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md) — MinSets there are feedback vertex sets; the ~1.5%-FVS-seed vs ~74%-matching-driver split of the OEWN graph places it in this paper's "biological-network regime" (n_FC 1–18%, n_SC 75–96%).
- [Loops and Self-Reference in the Construction of Dictionaries](../Levary_2012_LoopsSelfReferenceDictionaries/notes.md) — Levary et al.: short definitional cycles are meaningful. Zañudo et al. find n_FC is governed by exactly the short-cycle / SCC structure — quantitative confirmation that the loopy core is where the irreducible structure lives.
- [Hidden Structure and Function in the Lexicon](../Picard_2013_HiddenStructureFunctionLexicon/notes.md) — Kernel/Core/Satellite/MinSet hierarchy; the FC-vs-SC cycle-treatment contrast gives a control-theoretic reading of why the Kernel is small.
- [The Symbol Grounding Problem](../Harnad_1990_SymbolGroundingProblem/notes.md) — Harnad: recursive definability ≠ grounding. The FC necessity result (a non-FVS subset fails for *some* nonlinearity) is the structural echo: fixing the FVS is necessary; the decay/dissipativity assumption with no lexical analogue is what gives sufficiency.

<!-- provenance: notes drafted by paper-reader subagent from arXiv 1605.08415v3 PDF (33pp incl. SI), reading pages 1-8 of main text as page images, 2026-05-12; cross-refs reconciled same day -->
