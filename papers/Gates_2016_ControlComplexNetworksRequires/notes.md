---
title: "Control of complex networks requires both structure and dynamics"
authors: "Alexander J. Gates; Luis M. Rocha"
year: 2016
venue: "Scientific Reports 6:24456"
doi_url: "https://doi.org/10.1038/srep24456"
pages: 11
arxiv_id: "1509.08409"
---

# Control of complex networks requires both structure and dynamics

## One-Sentence Summary
Using fully enumerated Boolean-network ensembles and three real biochemical models, the paper demonstrates that structure-only controllability methods (structural controllability / maximum matching, and minimum dominating set) both *under-* and *over-estimate* the size of the minimum driver set AND identify the *wrong* driver variables, because real control depends on dynamics (specifically on how canalizing the transition functions are) — so a driver set derived from the interaction graph alone is not even an approximation of the true control set.

## Problem Addressed
Two influential methods — **structural controllability (SC)**, Liu–Slotine–Barabási 2011, based on maximum matching; and **minimum dominating set (MDS)**, Nacher–Akutsu 2012/2013 — claim to predict which "driver nodes" can fully control a complex system *from the interaction graph alone, ignoring dynamics*. The paper asks: how well does network structure actually predict the controllability of a realistic *nonlinear* dynamical system, especially from a control viewpoint? Answer: poorly, in both number and identity of driver variables.

## Key Contributions
- Three new exact controllability measures for Boolean networks (BNs), computed by full state-space enumeration: mean fraction of reachable configurations $\bar R_D$, mean fraction of *additional* controlled configurations $\bar C_D$ (beyond what the natural dynamics already visits), and mean fraction of reachable attractors $\bar A_D$. *(p.3)*
- Constructs the **controlled state-transition graph (CSTG)** $\mathcal G_D = (\mathcal X, \mathcal T \cup \mathcal T_D)$ and the **controlled attractor graph (CAG)** as the objects on which exact control is evaluated. *(p.2-3)*
- On ensembles of 8 canonical network motifs (Feed-Forward, Chain, Loop, Co-regulated, Co-regulating, BiParallel, BiFan, Dominated-Loop), shows wide variation in real control for *fixed* structure and *fixed* number of driver variables — SC and MDS pick a single answer that is mostly wrong. *(p.4-6)*
- On the *Drosophila* segment polarity network (SPN), budding-yeast cell cycle (CCN), and *Arabidopsis* floral organ model: SC/MDS driver sets are "essentially random" with respect to actual attractor control; the structure-only minimum sets miss the true control variables. *(p.5-7)*
- Identifies **canalization** of the automata transition functions as the lever: most edges in a random BN's structural graph are partly or fully *redundant* (not in the "effective structure"); the larger the mismatch between structural graph and effective-structure graph, the worse SC/MDS do. Canalization can be orchestrated either to make control *harder* than structure predicts (CCN) or *easier* (SPN driven to wild-type). *(p.7-9)*
- Shows that BN ensembles engineered to have *zero* canalization — Full Effective Connectivity (FEC) — still have SC/MDS predictions wrong, and are in fact controllable by *smaller* driver sets than the canonical models; and that appropriately chosen *full* canalization can collapse the effective structure to a linear chain, the one regime where structure-only methods are correct (but such configurations are vanishingly rare at realistic network size). *(p.8-9)*

## Study Design (empirical / computational)
- **Type:** Computational study — exhaustive state-space enumeration of small Boolean-network ensembles + analysis of three published Boolean models of biochemical regulation.
- **Ensembles:** For each of 8 directed network motifs of $N\le?$ nodes (3–17 variables across the biological models), all BNs whose interaction graph is that motif (with self-interactions) and whose update functions are sampled, partitioned into *contingent* / *non-contingent* (NC) BNs (NC = at least one variable's function ignores some structural input → mismatch between structural and effective graph). *(p.3-4)*
- **Biological models:** *Drosophila melanogaster* segment polarity network (Albert & Othmer 2003) — single-cell reduction, 17 protein/mRNA variables; *Saccharomyces cerevisiae* cell-cycle network (Li et al. 2004) — Cell-Cycle Network (CCN), 11 variables; *Arabidopsis thaliana* floral organ arrangement model. *(p.5-7)*
- **Comparators:** driver sets predicted by SC (maximum matching) and by MDS, evaluated against the exact $\bar R_D$, $\bar C_D$, $\bar A_D$ over the full configuration space / attractor set. *(p.4-7)*

## Methodology
A BN is $X \equiv \{x_i\}$, $x_i \in \{0,1\}$, $i=1..N$; structural network $G=(X,E)$ with edge $e_{ji}\in E$ meaning $x_j$ is an input to $x_i$; in-degree $k_i = |X_i|$. Synchronous deterministic update: $x_i^{t+1} = f_i(X_i^t)$, $f_i:\{0,1\}^{k_i}\to\{0,1\}$. Configuration $\mathbf X^t \in \mathcal X \equiv \{0,1\}^N$, $|\mathcal X| = 2^N$. The **state-transition graph** STG $\mathcal G = (\mathcal X, \mathcal T)$ has one node per configuration and exactly one out-edge per node (determinism); being finite it contains $\ge 1$ attractor (fixed point or cycle).

**Control model:** driver set $D \subseteq X$; an *intervention* is an instantaneous bit-flip to the variables in $D$. The **controlled STG** $\mathcal G_D = (\mathcal X, \mathcal T \cup \mathcal T_D)$ adds, from every configuration, edges to each of its $2^{|D|}-1$ perturbed counterparts. $X$ is *controllable* by $D$ iff every configuration is reachable from every other in $\mathcal G_D$, i.e. $\mathcal G_D$ is strongly connected (control-theory definition, Sontag; Liu et al.). The **controlled attractor graph** CAG has attractors as nodes and an edge $A_\alpha \to A_\beta$ iff some controlled path in $\mathcal G_D$ leads from $A_\alpha$ into $A_\beta$.

**Effective structure / canalization:** a variable's transition function may not actually depend on all $k_i$ structural inputs (e.g. an AND-gate input that is already 0). The *effective connectivity* discounts redundant inputs (Marques-Pita & Rocha 2013); the *effective structure graph* keeps only the non-redundant edges. SC assumes every structural edge fully contributes — so when the effective graph is much sparser than the structural graph, SC/MDS predictions diverge from real control.

## Key Equations

Mean fraction of reachable configurations for driver set $D$:
$$
\bar R_D = \frac{1}{2^N}\sum_{\mathbf X_\alpha} r(\mathcal G_D, \mathbf X_\alpha)
$$
Where: $r(\mathcal G_D, \mathbf X_\alpha)$ = number of configurations $\mathbf X_\beta$ lying on directed paths from $\mathbf X_\alpha$ in the controlled STG $\mathcal G_D$; $2^N = |\mathcal X|$. $\bar R_D \in [0,1]$; $\bar R_D = 1$ iff $X$ is fully controllable by $D$; $\bar R_\emptyset > 0$ in general (the uncontrolled dynamics already reaches some configurations). *(p.3)*

Mean fraction of *additional* controlled configurations:
$$
\bar C_D = \bar R_D - \bar R_\emptyset
$$
Where: $\bar R_\emptyset$ = mean fraction reachable under the *uncontrolled* dynamics. $\bar C_D$ isolates the control gained *beyond* the natural system dynamics; transient configurations are irrelevant. *(p.3)*

Mean fraction of reachable attractors:
$$
\bar A_D = \frac{1}{|A|}\sum_{C_\alpha} r(C_D, C_\alpha)
$$
Where: $A = \{A_1, ..., A_{|A|}\}$ the set of attractors; $C_D$ the controlled attractor graph; $r(C_D, C_\alpha)$ = number of attractors reachable from $A_\alpha$ via controlled paths. $\bar A_D = 1$ iff $D$ can drive the system from any attractor to any attractor; $\bar A_\emptyset = 0$ since attractors are disconnected in the uncontrolled CAG. Note $\bar A_D = 1 \;\Rightarrow\; \bar R_D = 1$. *(p.3)*

## Parameters / Key Quantitative Results

| Quantity | System | Value | Page | Notes |
|---|---|---|---|---|
| Min driver vars for full configuration control | Co-Regulating-Network motif (CCN motif) | 4 (original canalizing) | p.4 | SC predicts 1; 77% of BNs in this motif ensemble are *not* fully controllable by the SC 1-driver set |
| Min driver vars for full configuration control | FEC ensemble of CCN motif (no canalization) | 2–3 | p.8-9 | All FEC nets fully controllable by 3 drivers; many by 2 — *smaller* than canonical model's 4; yet SC/MDS still wrong |
| Feed-Forward (FFC) BN ensemble | 4096 contingent / 1744 non-contingent (of 5840) | — | p.3-4 | $\bar C_\emptyset \approx 0$ for ~40% of configs reachable; $\bar R_D, \bar A_D$ vary widely with the *same* SC/MDS driver set |
| Edge redundancy in random BNs | general | "most edges entirely or partially redundant" | p.7-8 | structural graph $\ne$ effective structure graph for almost all random BNs |
| Drosophila SPN | 17 variables, single-cell reduction | SC/MDS driver sets ≈ random wrt attractor control | p.5,7 | structure-predicted subsets fail $\bar A_D$; canalization here is used to make the wild-type attractor *easier* to reach than structure suggests |
| Yeast CCN (Li et al.) | 11 variables | SC/MDS driver sets ≈ random wrt control; canalization makes control *harder* than structure predicts | p.5-7 | a "Sliol controller" / specific 4-variable sets are the real best controllers, not the SC/MDS sets |
| Arabidopsis floral model | (Boolean) | similar failure — structure does not predict actual attractor control | p.7 | see SM |

## Methods & Implementation Details
- Full state-space enumeration is only feasible for small $N$; general deterministic BN control is NP-hard (Akutsu et al. 2007), hence the focus on motifs and small published models. *(p.2)*
- Driver-set evaluation: for each candidate $D$, build $\mathcal G_D$ by adding all $2^{|D|}-1$ perturbation edges from every node, then compute reachability sets and strong-connectivity. *(p.2-3)*
- Motif ensembles: enumerate (or sample) all logical functions consistent with each structural motif + self-loops; classify contingent vs non-contingent by whether the *effective* graph equals the *structural* graph. *(p.3-4)*
- FEC ensemble construction: for the CCN structural graph, pick each variable's update from the two *non-canalizing* functions available for its in-degree → effective graph $\equiv$ structural graph by construction; sample 50 such networks. *(p.8)*
- Effective-structure / canalization quantification via schema redescription (Marques-Pita & Rocha 2013; ref 7,14). *(p.7-8)*
- Robustness vs control: both defined on response of dynamics to perturbations — robustness = how many perturbations leave dynamics invariant; control = perturbations that *alter* dynamics. Complementary, not the same. (refs 44,56) *(p.9)*

## Figures of Interest
- **Fig 1 (p.2-3):** STG and three CSTGs / CAGs for an exemplar Feed-Forward BN; shows perturbed edges (purple/dashed) added per driver choice $D=\{x_1\}, \{x_2\}, \{x_3\}$.
- **Fig 2 (p.3-4):** The 8 directed network motifs used as ensemble structures (A Feed-Forward, B Chain, C Loop, D Co-Regulated, E Co-Regulating, F Co-Regulating(?), G Co-Regulating, ... incl. BiParallel, BiFan, BiFan-with-self, Dominated-Loop).
- **Fig 3 (p.4-5):** Control portrait of the Feed-Forward ensemble — scatter of $\bar A_D$ vs $\bar C_D$ across BNs; FES / RES / NC subsets; the SC effective-structure-matching subset (FES) sits at the extreme, the bulk does not.
- **Fig 4 (p.5-6):** Control portrait of the Loop-with-self-interactions motif; $\bar R_D$ vs $\bar C_D$ and attractor counts; MDS predicts full control by 1 driver but ~all of the ensemble fails it.
- **Fig 5 (p.6-7):** Single-cell SPN control — $\bar A_D$ vs $\bar R_D$ for $|D|=1..4$; SC-predicted subsets (orange) and MDS-predicted (yellow, "S0") sit among low-control points; the wild-type attractor highlighted.
- **Fig 6 (p.7-8):** Yeast CCN control — $\bar A_D$ vs $\bar R_D$ for $|D|=1..4$; "Sliol controller" / specific variable sets highlighted; the canalized wiring diagrams (B) of each variable.

## Results Summary
For ensembles of network motifs there is a *large variation* of possible control for even the simplest network; SC and MDS each give one answer that is mostly wrong on both the *number* of driver variables (they both undershoot and overshoot) and *which* variables to pick (their sets are essentially random wrt $\bar R_D$, $\bar C_D$, $\bar A_D$). The discrepancy *worsens* when scaling from motifs to the three real biochemical models. Canalizing transition functions generally make structure-only methods *less* accurate; only when canalization is orchestrated so the effective structure collapses to a linear chain do SC/MDS become correct — and such configurations are exponentially rare at realistic size. Without information about the dynamics, structure-only control cannot be accepted as even an approximation. *(p.8-9)*

## Limitations
- Exact controllability measures require full state-space enumeration → only small $N$ (motifs, ~11–17-variable published models); large-system behavior is *argued* to be worse (motifs are building blocks) but not exhaustively shown. *(p.2,9)*
- Synchronous deterministic update only; asynchronous / stochastic BNs not treated (though the CSTG/CAG framework is stated to extend to any discrete deterministic dynamical system). *(p.9)*
- Does not propose a replacement method; only quantifies the gap and points to existing dynamics-aware methods (monotone control systems, master stability functions, schema redescription, stabilization subgraphs). *(p.2,9)*

## Arguments Against Prior Work
- **vs structural controllability (SC, Liu–Slotine–Barabási 2011, ref 20; Lin 1974, ref 19):** SC assumes every structural edge fully contributes to the dynamics and that cycles are self-regulating and need no external signal. In random/realistic BNs most edges are partly or wholly redundant (effective graph ≠ structural graph), so SC's "minimum number of driver variables" both over- and under-estimates the true minimum and the SC driver *set* is uncorrelated with real control. SC's published claim that biological systems are "harder to control" / have different control profiles than social/technological ones (refs 24,25 — Egerstedt 2011; Ruths & Ruths 2014) is therefore not a realistic portrayal. SC has already been heavily critiqued for stringent assumptions (refs 29–31: Müller & Schuppert 2011; Cowan et al. 2012 "Nodal dynamics, not degree distributions"; Sun & Motter 2013 "controllability transition and nonlocality"). *(p.1-2,8-9)*
- **vs minimum dominating set (MDS, Nacher–Akutsu, refs 21,22):** MDS assumes a node can influence all neighbors simultaneously but the signal propagates no further (every variable within one interaction of a driver). Used for protein-interaction control (ref 32 Wuchty 2014) and disease-gene perturbation of the human regulatory network (ref 33 Wang 2015); the paper shows MDS driver sets for the yeast CCN are essentially random wrt actual control and predict full control by far fewer variables than reality requires. *(p.2,5-7)*
- General: "network motifs: structure does not determine function" (ref 52 Ingram et al. 2006) — consistent with this paper extending that to control. *(p.4)*

## Design Rationale
- Boolean networks chosen as "ideal, parsimonious" testbeds: defined by *both* a clear interaction structure *and* rich nonlinear dynamics over binary variables; small enough to enumerate exactly. *(p.9)*
- Control defined via bit-flip interventions and reachability in the CSTG (Sontag control-theory definition) so it lines up with the same controllability notion SC/MDS claim to predict — making the comparison fair. *(p.2)*
- Three exact measures ($\bar R_D$, $\bar C_D$, $\bar A_D$) instead of one: $\bar R_D$ counts raw reachability, $\bar C_D$ subtracts what the natural dynamics already gives you (so transients don't inflate it), $\bar A_D$ targets the biologically meaningful question (drive the cell from one attractor/phenotype to another). *(p.3)*
- FEC ensemble (zero canalization, effective ≡ structural) is the cleanest test of "is it the canalization?" — and even there SC/MDS are wrong, so the mismatch is not the *whole* story; dynamics matter intrinsically. *(p.8-9)*

## Testable Properties
- For a given structure and a given $|D|$, $\bar R_D$ / $\bar C_D$ / $\bar A_D$ vary widely across the BN ensemble — i.e. structure + driver-set-size does not pin down controllability. *(p.4-6)*
- $\bar A_D = 1 \Rightarrow \bar R_D = 1$ (attractor-controllability implies configuration-controllability). *(p.3)*
- $\bar A_\emptyset = 0$; $\bar R_\emptyset > 0$ generically; $\bar C_\emptyset = 0$. *(p.3)*
- Larger mismatch between structural graph and effective-structure graph ⇒ worse SC/MDS control predictions. *(p.8)*
- FEC ensemble of a given structural graph is fully controllable by *fewer* driver variables than the canonically-parameterized model with that structure (canalization can *cost* controllability). *(p.8-9)*
- A BN whose effective structure is a linear chain is correctly characterized by SC/MDS; such BNs are exponentially rare as $N$ grows. *(p.8-9)*

## Relevance to Project
This is the methodological caution behind the repo's OEWN definition-digraph finding that **maximum-matching driver nodes pick the wrong words for lexical grounding** while the **feedback-vertex-set (FVS) framing is the one that transfers**. The paper shows SC (maximum matching) and MDS are *structure-only* heuristics whose driver sets are essentially random with respect to actual control once any non-trivial dynamics is present, and that they err in both the *number* and the *identity* of driver variables. By contrast, the FVS-control results already in this collection (Massé 2008 / Vincent-Lamarre 2014 / Picard 2013 for the dictionary side; Fiedler 2013, Mochizuki 2013, Zañudo 2016 for the dynamics side) are *dynamics-agnostic by theorem* — overriding the FVS (plus source nodes) drives a network of *any* nonlinear dynamics to any of its attractors, depending only on the wiring diagram. So the lexicon's ~1.5% FVS-seed is a real grounding kernel; its ~74% maximum-matching driver set is, per Gates & Rocha, not even an approximation of "the words you need to fix to fix the rest." Cross-references the same biological-network regime that Zañudo 2016 places the lexicon in (FVS-control set tiny, matching-driver set huge for gene-regulatory networks).

Also relevant: the "effective structure" / canalization point — most definitional edges may be functionally redundant in whatever the true semantic dynamics is — is a caveat that *any* structure-only analysis of definition digraphs (including FVS, in principle, if definitional edges turn out not to all "fully contribute") should keep in view; the FVS result survives this only because it is a *worst-case-over-all-dynamics* guarantee.

## Open Questions
- [ ] What exact restrictions on transition functions make structure *sufficient* (or a good approximation) for predicting control? (paper poses this; only the linear-chain effective-structure case is settled) *(p.8-9)*
- [ ] How do dynamics-aware-but-tractable methods (monotone control systems, master stability functions, schema redescription, stabilization subgraphs) scale, and how much real control do they capture? *(p.9)*
- [ ] Asynchronous / stochastic update versions of the CSTG/CAG control measures. *(p.9)*
- [ ] Quantitative relationship between robustness and control on the CSTG/CAG. *(p.9)*

## Related Work Worth Reading
- Liu, Slotine & Barabási, "Controllability of complex networks", *Nature* 473 (2011) — the SC / maximum-matching method this paper rebuts. (ref 20) → NOW IN COLLECTION: [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md)
- Nacher & Akutsu, MDS controllability papers, *New J. Phys.* 14 (2012) / *Sci. Rep.* 3 (2013). (refs 21,22)
- Cowan, Chastain, Vilhena, Freudenberg & Bergstrom, "Nodal dynamics, not degree distributions, determine the structural controllability of complex networks", *PLoS ONE* 7 (2012). (ref 30)
- Sun & Motter, "Controllability transition and nonlocality in network control", *Phys. Rev. Lett.* 110 (2013). (ref 31)
- Zañudo & Albert, "Cell fate reprogramming by control of intracellular network dynamics", *PLoS Comput. Biol.* 11 (2015) — stabilization-subgraph control; already in collection as Zañudo_2016. (ref 60)
- Marques-Pita & Rocha, "Canalization and control in automata networks: body segmentation in Drosophila melanogaster", *PLoS ONE* 8 (2013) — the effective-connectivity / schema-redescription machinery. (ref 7)
- Fiedler, Mochizuki, Kurosawa & Saito, "Dynamics and control at feedback vertex sets I" — *not cited here* but the dynamics-agnostic FVS-control result; already in collection.
- Ruths & Ruths, "Control profiles of complex networks", *Science* 343 (2014) — the SC-based social-vs-biological control-profile claim. (ref 25)
- Wuchty, "Controllability in protein interaction networks", *PNAS* 111 (2014). (ref 32)
- Akutsu, Hayashida, Ching & Ng, "Control of Boolean networks: hardness results and algorithms for tree structured networks", *J. Theor. Biol.* 244 (2007). (ref 35)

## Collection Cross-References

### Already in Collection
- [Structure-based control of complex networks with nonlinear dynamics](../Zañudo_2016_Structure-basedControlComplexNetworks/notes.md) — Zañudo–Yang–Albert cite this paper (their ref 7/8) as the structure-vs-dynamics caveat; *this* paper is the negative result (SC/MDS fail), Zañudo et al. are the positive complement (FVS-control works regardless of dynamics). Together they bracket the repo's finding: maximum-matching driver words are spurious, FVS-seed words are real.

### Now in Collection (previously listed as leads)
- [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md) — Liu–Slotine–Barabási (2011), this paper's ref 20; the structural-controllability / maximum-matching driver-node method that Gates & Rocha rebut. SC: linear `ẋ=Ax+Bu`, full-state control, driver set = unmatched nodes of a maximum matching, n_D mainly set by the degree distribution, drivers avoid hubs. Gates & Rocha show that once realistic *nonlinear* dynamics are present the SC driver count both over- and under-estimates the true minimum and the SC driver *set* is uncorrelated with real control — i.e. the very degree-distribution / hub-avoidance regularities Liu et al. report are structural artifacts that don't survive contact with dynamics. The repo's OEWN definition digraph (~1.5% FVS-seed vs ~74% matching-driver set) is exactly the regime where this matters.

### New Leads (Not Yet in Collection)
- Nacher & Akutsu (2012/2013) — minimum-dominating-set controllability, *New J. Phys.* 14 / *Sci. Rep.* 3 — the second structure-only target. (refs 21,22)
- Cowan, Chastain, Vilhena, Freudenberg & Bergstrom (2012) — "Nodal Dynamics, Not Degree Distributions, Determine the Structural Controllability of Complex Networks", *PLoS ONE* 7:e38398 — independent earlier critique on the same grounds. (ref 30)
- Sun & Motter (2013) — "Controllability Transition and Nonlocality in Network Control", *Phys. Rev. Lett.* 110:208701. (ref 31)
- Marques-Pita & Rocha (2013) — "Canalization and control in automata networks: body segmentation in Drosophila melanogaster", *PLoS ONE* 8:e55946 — the effective-connectivity / schema-redescription machinery underpinning the canalization argument. (ref 7)
- Ingram, Stumpf & Stark (2006) — "Network motifs: structure does not determine function", *BMC Genomics* 7:108 — the motif-level antecedent of the same lesson. (ref 52)
- Ruths & Ruths (2014) — "Control profiles of complex networks", *Science* 343:1373–1376 — the SC-based social-vs-biological control-profile claim that this paper says is unrealistic. (ref 25)
- Akutsu, Hayashida, Ching & Ng (2007) — "Control of Boolean networks: hardness results and algorithms for tree structured networks", *J. Theor. Biol.* 244:670–679 — BN control NP-hardness. (ref 35)

### Cited By (in Collection)
- [Structure-based control of complex networks with nonlinear dynamics](../Zañudo_2016_Structure-basedControlComplexNetworks/notes.md) — cites this as the structure-vs-dynamics counterweight (their ref 7/8).

### Conceptual Links (not citation-based)
- [Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks](../Fiedler_2013_DynamicsControlFeedbackVertex/notes.md) — tension/complement: Fiedler et al. prove FVS-control is *dynamics-agnostic by theorem* (works for every admissible nonlinearity); Gates & Rocha prove SC/MDS (maximum matching, dominating set) *are not even an approximation* once dynamics enter. The FVS framing survives precisely the failure mode that sinks the matching framing — this is *why* the repo's FVS-seed transfers and its matching-driver set does not.
- [Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks](../Mochizuki_2013_DynamicsControlFeedbackVertex/notes.md) — same complement: Mochizuki et al.'s FVS = determining-set result is structure-only *and* dynamics-correct; Gates & Rocha show the SC/MDS structure-only sets are dynamics-incorrect. Different graph functionals (FVS vs. maximum matching / dominating set) have opposite robustness to the dynamics.
- [How Is Meaning Grounded in Dictionary Definitions?](../Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md) — Massé et al.'s "grounding set = feedback vertex set" is the lexical instance of the dynamics-agnostic functional; Gates & Rocha are the cautionary tale for the alternative (a max-matching "minimum driver vocabulary" would be the wrong words). The repo's ~1.5% FVS-seed vs ~74% matching-driver split is exactly this paper's "structure-only over/undershoots and mis-identifies" phenomenon in the lexicon.
- [The Latent Structure of Dictionaries](../Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md) — MinSets there are feedback vertex sets; this paper is the reason to *not* substitute a structural-controllability driver set for a MinSet when reasoning about which words ground the lexicon.
- [The Symbol Grounding Problem](../Harnad_1990_SymbolGroundingProblem/notes.md) — Harnad: recursive definability ≠ grounding; Gates & Rocha add a control-theoretic layer of the same warning — *structural* reachability/controllability ≠ actual control, because the dynamics (here: canalization / effective connectivity) carries information the wiring diagram does not.

<!-- provenance: notes drafted by paper-reader subagent from Nature srep24456 PDF (11pp main text; SI not included), all 11 pages read as page images, 2026-05-12; cross-refs reconciled same day -->
