---
title: "Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks"
authors: "Atsushi Mochizuki, Bernold Fiedler, Gen Kurosawa, Daisuke Saito"
year: 2013
venue: "Journal of Theoretical Biology"
doi_url: "https://doi.org/10.1016/j.jtbi.2013.06.009"
pages: "335:130–146"
affiliations: "Theoretical Biology Laboratory, RIKEN (Wako, Saitama, Japan); Institut für Mathematik, Freie Universität Berlin"
---

# Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks

## One-Sentence Summary
For any ODE system whose interaction structure is a directed graph, the **feedback vertex set (FVS)** of that graph is a set of *determining nodes*: observing the time courses of just the FVS variables uniquely pins down the long-term trajectory of *every* variable in the network — and which nodes form the FVS is computable from the wiring diagram alone, with no knowledge of the rate functions.

## Problem Addressed
Modern molecular biology yields large regulatory networks (signal transduction, gene regulation, metabolism), but: (1) network dynamics are hard to observe completely — you cannot measure every molecule at high time resolution; (2) the dynamical rate laws ("regulatory functions") are mostly unknown; (3) even the network topology is often incomplete/uncertain. The paper asks: using *only* the regulatory linkage information, can we (a) identify a small subset of molecules whose measurement suffices to read off the entire system's dynamical state ("faithful monitor"), and (b) identify a small subset whose control suffices to switch the whole system between attractors? This is the observational counterpart of the control result in Part I (Fiedler, Mochizuki, Kurosawa, Saito 2013, the companion paper).

## Key Contributions
- **Determining-nodes theorem (informative-set / faithful-monitor result):** A feedback vertex set *J* of the network's directed graph is a set of determining nodes — if two solutions x(t) and y(t) of the ODE system are asymptotically equal on all FVS components (`x_j(t) − y_j(t) → 0` for `j ∈ J` as `t → ∞`), then they are asymptotically equal on *all* components. So measuring FVS time courses determines (in the limit) every attractor — steady states, periodic orbits, quasiperiodic orbits, chaos. *(p.133, Section 3)*
- **The FVS is read off the topology alone** — independent of the (unknown) nonlinear rate functions, requiring only mild monotonicity-style assumptions on the regulatory functions (e.g. derivative of f_i w.r.t. x_j is bounded and bounded away from 0, or more generally a "decay + globally bounded nonlinearity" structure; see Appendix discussions and the cited mathematical companions). *(p.133, p.143)*
- **Quantitative reach:** A signal-transduction network downstream of the EGF receptor, 113 molecules, has an FVS of size 5 — so the activities of just 5 molecules monitor the diversity of all attractors of the 113-variable system. A 16-gene Ascidian developmental network reduces to a single FVS node (FoxD-a/b). A 21-component mammalian circadian network has a 7-node FVS. *(abstract; p.133, p.134–139)*
- **Numerical confirmation:** in silico, for each test network they generate thousands of random monotone regulatory functions and random initial conditions, integrate the full ODE, then check whether the FVS time-course pins the rest — ~99% identification rates reported for the Ascidian network. *(p.135–136, Fig. 5)*
- **Control via the FVS (linking to Part I):** numerically demonstrated for the EGF signal transduction network and the mammalian circadian network — by forcing the FVS variables onto the target trajectory ("clamping control"), the *whole* system is dragged onto the corresponding attractor; once the FVS is on target the remaining ("residual") network has an empty feedback vertex set and therefore relaxes to a unique trajectory consistent with the clamped inputs. *(p.137–138 EGF; p.139–142 circadian; Figs. 7–10)*
- **Conceptual unification:** "determining nodes" generalizes notions of determining modes/nodes for PDEs (Foias–Prodi, etc.) to network ODEs, and connects to control-theoretic structural controllability (Liu, Slotine, Barabási 2011) and the Takens delay-embedding / observability literature (Joly 2012, Letellier–Aguirre) — but uses a *graph-combinatorial* criterion (FVS) rather than a rank/Jacobian condition. *(p.139–143, Section 7)*

## Methodology
Pure-theory result (the determining-nodes theorem) plus numerical case studies.

The mathematical setting: a system of ODEs whose dependency graph is a directed graph *G* (vertices = molecular species, an edge j → i iff f_i depends on x_j). The proof of the determining-node property uses the FVS definition: removing the FVS vertices J leaves a graph G \ J with **no directed cycles** (a DAG / forest of feedback-free structure). On the cycle-free residual, the dynamics of the non-FVS variables is "slaved" to the boundary input from J: by following the DAG topologically, each removed variable's asymptotic behavior is forced by its (asymptotically determined) inputs. Iterating from the FVS through the DAG layers yields asymptotic determination of the whole state. The hypotheses on the regulatory functions guarantee this slaving (existence/uniqueness + asymptotic contraction in the feedback-free directions); the paper points to its mathematical companions for the full hypotheses (decay terms, globally Lipschitz/bounded nonlinearities, "informative set" formulation).

Numerical protocol per network: (1) extract the directed regulatory graph (with self-loops handled — repressive self-degradation self-loops can be subsumed into the decay term and removed from the cycle structure, Eq. (2)); (2) compute a (minimal) FVS by inspection / standard FVS combinatorics; (3) instantiate random monotone regulatory functions (sigmoidal / Hill-type product forms, random Hill exponents, random thresholds in (0,1), random activation/repression sign per edge); (4) integrate the full ODE from random initial conditions; (5) compare the trajectory of the non-FVS variables against the value forced by the FVS time course; (6) count fraction of trials where the rest of the network is correctly identified. Also: clamping-control experiments where FVS variables are externally driven onto a target attractor and the rest of the network is checked for convergence.

## Key Equations / Statistical Models

General regulatory ODE (enhanced/inhibited interactions, with self-regulation):
$$
\frac{dx_k}{dt} = F_k(x_1,\dots,x_N),\qquad k = 1,\dots,N
$$
where x_k = activity/concentration of molecule k, F_k = (unknown) regulatory rate function depending only on the regulators of k. *(p.132, Eq. (1))*

Form with an explicit linear decay term separated out (so a repressive self-loop becomes part of the decay and is removed from the feedback structure):
$$
\frac{dx_k}{dt} = f_k(x_1,\dots,x_N) - d_k\,x_k,\qquad k = 1,\dots,N
$$
where d_k > 0 is the degradation/decay rate of molecule k; f_k collects the cross-regulatory (and non-self) terms. *(p.132, Eq. (2))*

Determining-nodes / faithful-monitor statement (informal): if x(t), y(t) are solutions of (1) (or (2)) and J is a feedback vertex set of the dependency graph, then
$$
x_j(t) - y_j(t) \to 0 \ \text{for all}\ j \in J \ \text{as}\ t \to \infty
\quad\Longrightarrow\quad
x_k(t) - y_k(t) \to 0 \ \text{for all}\ k = 1,\dots,N.
$$
*(p.133, Section 3)*

Random regulatory function used in the Ascidian numerics (product of step-like sigmoids):
$$
f_k = \prod_{j \in J_k} g_{kj}(x_j)
$$
with, for an activating edge,
$$
g^{+}_{kj}(x) =
\begin{cases}
0.1 & (0 \le x < 0.2)\\
0.3 & (0.2 \le x < 0.4)\\
0.5 & (0.4 \le x < 0.6)\\
0.7 & (0.6 \le x < 0.8)\\
0.9 & (0.8 \le x)
\end{cases}
\qquad g^{0}_{kj}(x) = 1 \ (\text{no edge})
$$
and the smooth-step (Hill-like) variant
$$
g_{kj}(x) =
\begin{cases}
0.5 & (0 \le x < T_{j\to k})\\
1.0 & (T_{j\to k} \le x)
\end{cases}
$$
with threshold `T_{j→k}` drawn uniformly in (0,1) per regulatory edge. *(p.135–136, Eqs. (5), (6a), (6b))*

Clamping-control example on the lac-style 2-vertex toy network (Fig. 1): a two-variable mutually-inhibitory pair with Hill-type repression and decay; bistability vs monostability depends on regulatory function shape. *(p.131–132, Fig. 1 caption gives the explicit f_A, f_B with Hill exponents and constants.)*

Steady-state structure of a 6-vertex feedback-loop residual (Eq. (7)) and target-clamping conditions on the circadian model (Eq. (10) — drive FVS variable x*(t) onto OstxT toward target attractor) are given in Sections 5–6.

EGF signal transduction model: Eqs. (B-?) in Appendix B / cited from Oda et al. 2005 (14 informative variables x_2^{P}, x_4^{P}, ... selected; the FVS of size 5: {SOS·ERK1/2, c-Src, HB·EGF, ADAMs, cyt-Ca2+}). *(p.137–138, Table 2)*

Mammalian circadian model: full ODE system Eqs. (B.1)–(B.20) in Appendix B (Per1, Per2, Cry1, Cry2, Rev-erbα, Clk, Bmal1, Rorc mRNAs; PER1, PER2, CRY1, CRY2, REV-ERBα, CLK, BMAL1, RORc proteins; and the complexes PER1/CRY1, PER2/CRY1, PER1/CRY2, PER2/CRY2, CLK/BMAL1) — Hill-type product transcription terms with activation by CLK/BMAL1 and RORc, repression by PER/CRY complexes and REV-ERBα; parameter values listed at end of Appendix B (p.146). *(p.144–146)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| EGF network size | N | molecules | 113 | — | p.133, p.137 | Signal transduction net downstream of EGF receptor (Oda et al. 2005) |
| EGF network FVS size | \|J\| | nodes | 5 | — | p.133, p.137 | {SOS·ERK1/2, c-Src, HB·EGF, ADAMs, cyt-Ca2+} (Table 2) |
| EGF "informative" variable count | — | variables | 14 | — | p.137 | 14 informative observables used; FVS is a 5-subset |
| EGF residual feedback-vertex sets enumerated | — | sets | 30 | — | p.138, Table 2 | 30 possible choices of minimal FVS / reductions tabulated |
| Ascidian network size | N | genes | 16 | — | p.134 | Halocynthia roretzi early development (Imai et al. 2006); ≈80 regulatory interactions |
| Ascidian FVS size | \|J\| | nodes | 1 | — | p.134–135 | Single node: FoxD-a/b |
| Ascidian cell types distinguished | — | tissues | 13 | — | p.135, Table 1 | 13 differentiated cell types at tailbud stage |
| Ascidian identification rate | — | % | ~99 | — | p.136, Fig. 5 | Fraction of random-function/random-IC trials where FVS pins the rest of net |
| Circadian network size | N | components | 21 | — | p.140, p.144 | Mammalian clock model (cf. Mirsky et al. 2009); mRNAs + proteins + complexes |
| Circadian FVS size | \|J\| | nodes | 7 | — | p.139, Table 3 | e.g. {PER2, CRY1, CRY2, RORc, BMAL1} + others; 7-component minimal FVS |
| Circadian residual FVS after clamping | — | nodes | 0 | — | p.140–142 | Residual network has empty FVS ⇒ unique relaxation |
| Random Hill exponent (numerics) | n_{i,k} | — | — | integers, varied | p.135–136 | Drawn randomly per edge in numerical regulatory functions |
| Regulatory-edge threshold | T_{j→k} | (activity units, 0–1) | — | (0,1) uniform | p.136 | Threshold in the step/Hill-like g_{kj} |
| Number of random functions per network | — | trials | 1000 | — | p.136 | Also "thousands" of random initial conditions |
| Decay/degradation rate | d_k | 1/time | >0 | — | p.132 | Linear decay term in Eq. (2); absorbs repressive self-loops |
| Circadian model rate constants | v_{·}, KA_{·}, KI_{·}, k_{m,·}, t_{·}, a_{·}, d_{·}, k_{p,·} | mixed | various | listed | p.146 | Full numeric values in Appendix B (transcription, dissociation, complex formation/dissociation, translation, mRNA & protein decay) |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | Context | Page |
|---------|---------|-------|---------|------|
| FVS pins whole network (Ascidian) | identification rate | ~99% | thousands of random monotone regs. + random ICs; 16-gene net, FVS = 1 node | p.136, Fig. 5 |
| EGF net monitored by 5 molecules | dimensional reduction | 113 → 5 | full attractor diversity readable from FVS time courses | p.133, p.137 |
| Circadian net monitored by 7 components | dimensional reduction | 21 → 7 | minimal FVS = 7 | p.139, Table 3 |
| Clamping FVS forces whole-net attractor switch (EGF) | qualitative | success | drives system from one steady state P1 to P2/USS etc. by clamping the 5-node FVS only | p.137–138, Fig. 7 |
| Clamping FVS forces circadian attractor switch | qualitative | success | drives 21-component clock from stable orbit to (originally unstable) target periodic orbit / USS by clamping ≤7 components | p.139–142, Figs. 9–10 |

## Methods & Implementation Details
- **FVS extraction:** build the directed dependency graph from the regulatory linkage; pure self-activation loops must be retained as cycles, but repressive self-degradation self-loops are absorbed into the linear decay term (Eq. (2)) and removed from the cycle structure before computing the FVS. *(p.132, p.134)*
- **FVS = minimum vertex set whose deletion makes the digraph acyclic.** Any FVS (not necessarily minimum) works as a determining set; smaller is just more efficient as a monitor/control handle. Computing a *minimum* FVS is NP-hard in general (cf. Fomin 2008 in this collection) but small biological networks are handled by inspection; multiple minimal FVS choices typically exist (Tables 2, 3 enumerate them). *(p.133, p.138–139)*
- **Determination procedure (conceptual):** topologically sort G \ J (a DAG); the asymptotic value of each non-FVS variable is the fixed point of its rate function given the asymptotically-known inputs (FVS variables + already-resolved upstream non-FVS variables). Walk the DAG layer by layer from the FVS frontier. *(p.133, Section 3; p.140–142 "residual network has empty FVS ⇒ unique trajectory")*
- **Numerical regulatory functions:** products of step-like / Hill-like sigmoids, one factor per incoming edge; sign (activation/repression) and threshold randomized per edge; Hill exponents randomized; values normalized to (0,1)-ish ranges. Eqs. (5), (6a), (6b). *(p.135–136)*
- **In silico identification test:** integrate full ODE from random IC; record FVS time courses; reconstruct the rest of the network from those + the (here, known) rate functions; compare to the true trajectory; tally success over 1000 functions × many ICs. *(p.136)*
- **Clamping control:** replace the FVS variables' ODEs with prescribed time functions equal to a target attractor's FVS components (Eq. (10) for circadian: x*(t) → OstxT); integrate the rest; check convergence to the target attractor of the full system, including originally unstable ones. *(p.137–138, p.140–142)*
- **EGF model:** taken from Oda et al. (2005) (228 reactions, EGFR pathway); 14 "informative" species selected; FVS of size 5; 30 alternative minimal feedback vertex sets/reductions tabulated (Table 2). *(p.137–138)*
- **Circadian model:** 21-component ODE system, Hill-type transcription, in Appendix B (Eqs. B.1–B.20), parameters at p.146; close to Mirsky et al. 2009 / Becker-Weimann-type architecture. *(p.139–142, p.144–146)*

## Figures of Interest
- **Fig. 1 (p.131):** Two-vertex mutually-inhibitory toy network; (a) graph with self-loops; (b,d) regulatory-function surfaces; (c,e) phase portraits — bistable vs monostable depending on rate-function shape; illustrates that one FVS node controls the pair. Caption contains explicit f_A, f_B.
- **Fig. 2 (p.133):** Five small example regulatory graphs (a)–(e) with a chosen minimal FVS (gray vertices) marked for each.
- **Fig. 3 (p.134):** Explanatory schematic of the theory — open-loop residual after removing the FVS; informative variable.
- **Fig. 4 (p.135):** Ascidian gene regulatory network — (a) full 16-gene net with self-loops (Imai et al. 2006); (b) reduced net after removing repressive self-degradation loops, single FVS node FoxD-a/b circled.
- **Fig. 5 (p.136):** Diversity of steady states identified by single-gene observation, per gene, across thousands of random regulatory functions — bar charts of identification rate (~99% for FoxD-a/b).
- **Fig. 6 (p.138):** EGF signal transduction network (downstream of EGFR, from Oda et al. 2005) with the 3-component / 5-node minimal FVS circled and numbered.
- **Fig. 7 (p.139):** Six simplified residual steady-state structures of the EGF network for various FVS choices; topologies of the simplified networks.
- **Fig. 8 (p.140):** Mammalian circadian network (21 components) with a minimal FVS marked; (b) time series; (c) phase-plane limit cycle (Per1 vs Per2).
- **Figs. 9–10 (p.141–142):** Numerical trajectories of clamping control of the circadian rhythm — driving from one orbit to another (stable/unstable) by clamping the FVS; phase-plane (Per1, Per2) portraits, stable vs unstable target orbits reached.

## Results Summary
The FVS of a regulatory network's dependency graph is simultaneously a *faithful monitor* (observing it asymptotically determines the entire system's trajectory, for any attractor type) and a *control handle* (clamping it onto a target attractor's FVS components drives the full system onto that attractor, even if it was originally unstable). Both the monitor and the control set are computable from the wiring diagram alone — the (unknown) nonlinear rate laws do not enter, only mild structural/monotonicity assumptions. Demonstrated on a 113-molecule EGF signaling network (FVS = 5), a 16-gene ascidian developmental network (FVS = 1), and a 21-component mammalian circadian model (FVS = 7), with ~99% in silico identification rates over randomized rate functions. *(p.133–142)*

## Limitations
- The determination/control is **asymptotic** (`t → ∞`), not instantaneous: it pins down long-term attractors, not necessarily transients. *(p.133, p.143)*
- Requires the *correct* network topology: "if the information on the network structure is correct" — incomplete or wrong wiring breaks the guarantee. *(abstract; p.133, Discussion p.143)*
- Requires the regulatory functions to satisfy the structural hypotheses (a linear-decay term, globally bounded nonlinearities, no destabilizing self-loops other than those absorbed into decay); pure self-activation loops must be kept and can enlarge the FVS. The precise hypotheses live in the mathematical companion papers, not fully spelled out here. *(p.132, p.143, p.144)*
- A *minimum* FVS is NP-hard to compute in general; the paper relies on small networks and inspection. *(p.139; cf. Fomin 2008)*
- The clamping-control demonstration is numerical, on specific models, not a general theorem in this paper (Part I has the control theory). *(p.137–142)*
- Self-decay `k → k` is assumed; without it (or with non-standard, e.g. Michaelis–Menten, self-decay) some statements need adjustment — discussed but not fully resolved. *(p.140, p.143)*

## Arguments Against Prior Work
- **vs. structural controllability (Liu, Slotine, Barabási 2011):** that approach is built for *linear* dynamics `ẋ = Ax + Bu` and gives "driver node" sets via a maximum-matching / Jacobian-rank condition; the FVS approach handles *nonlinear* regulatory dynamics and uses a purely graph-combinatorial criterion. The two are complementary, not equivalent — driver sets and feedback vertex sets generally differ. *(p.139–140, p.143, Section 7)*
- **vs. Maximum-Matching (MM) variants:** MM-type approaches require all terminal nodes of the matching and may need more sensor/control nodes than necessary; "more parsimonious GA variant selects only one sensor per feedback loop" — but still oriented to linear theory. *(p.140)*
- **vs. Takens delay-embedding / observability (Letellier–Aguirre; Joly 2012):** Takens-style observability typically demands generic conditions and a single (or few) sensors with delay coordinates; the FVS result is sharper for networks because it exploits the cycle structure directly and identifies a concrete set. Joly (2012) gives a precise mathematical version for ODE networks of the symmetries/observability question; the paper positions its result alongside it. *(p.139–143)*
- **vs. continuous quantitative modeling:** the paper deliberately avoids requiring quantitative rate laws — prior approaches that need full kinetic parameterization are criticized as impractical given that biological rate functions are largely unknown. *(p.130–132, Section 7)*
- The paper sets aside Boolean-network approaches as a separate (also useful, also linkage-only) tradition, not directly comparable. *(p.142, Section 7)*

## Design Rationale
- **Why FVS, not Jacobian rank?** Because the FVS depends only on the *sign pattern / existence* of regulatory links, not on numerical coefficients — robust to the (huge) uncertainty in biological rate constants. The cycle structure is what creates the possibility of multiple attractors; breaking all cycles (by fixing the FVS) collapses the residual to a unique trajectory. *(p.133, p.143)*
- **Why absorb repressive self-loops into decay?** A self-degradation term is stabilizing, not a genuine feedback cycle; keeping it as a graph cycle would needlessly inflate the FVS. *(p.132, p.134)*
- **Why "informative set" / measure a *subset* rather than reconstruct everything?** Because complete high-time-resolution measurement is infeasible; the result shows you don't need it — the FVS suffices. *(p.130–133)*
- **Why asymptotic rather than exact?** The slaving of non-FVS variables to FVS inputs is a contraction-to-attractor argument; exactness would require initial-condition matching too. The asymptotic statement is the natural and useful one for "which attractor are we on?" *(p.133, p.143)*

## Testable Properties
- For any ODE system with dependency graph G and any FVS J ⊆ V(G): `x_j(t) − y_j(t) → 0 ∀ j∈J ⇒ x_k(t) − y_k(t) → 0 ∀ k∈V(G)`. *(p.133)*
- After removing an FVS, the residual graph G \ J is acyclic (a DAG/forest). *(p.133)*
- The residual (post-clamping) network has an empty feedback vertex set ⇒ for fixed inputs it converges to a unique trajectory. *(p.140–142)*
- A *smaller* FVS still works as a determining set (any superset of an FVS is an FVS); the *minimum* FVS is the most efficient monitor. *(p.133, p.139)*
- The FVS / determining set is invariant under changes to the rate functions that preserve the dependency graph and the structural hypotheses. *(p.133, p.143)*
- Clamping the FVS variables onto any attractor's FVS components drives the full system onto that attractor (numerically verified, EGF & circadian). *(p.137–142)*
- Identification rate over random monotone rate functions ≈ 99% for a single-node FVS network (Ascidian). *(p.136)*

## Relevance to Project
The "FVS = determining/grounding set" picture is the structural backbone for treating a dictionary as a *definition digraph* (each headword → the words used to define it): the FVS of that digraph is the minimal set of words whose meanings, once fixed ("grounded"), force the meanings of everything else by following the now-acyclic residual. This paper supplies the *observational/monitor* half (Part I supplies the *control* half): grounding (= clamping) the FVS makes the rest of the lexicon a DAG with a unique fixed-point assignment of meanings — directly mirroring the Vincent-Lamarre / Massé "kernel"/"grounding set" line in this collection and the FVS-complexity result (Fomin 2008). The robustness-to-rate-functions point translates to: the grounding set depends only on *which words appear in which definitions*, not on the (unknown) semantic content. Concretely useful: (a) the slaving/topological-sort argument is the algorithm for propagating grounded meanings; (b) minimum-FVS is NP-hard but small/structured digraphs are tractable; (c) multiple minimal FVS exist — there is no unique grounding set, only a unique *size* and a lattice of choices.

## Open Questions
- [ ] Exact (non-asymptotic) determination conditions — what extra structure forces transient agreement, not just attractor agreement?
- [ ] Behavior under Michaelis–Menten / saturating self-decay rather than linear decay (p.140 flags this).
- [ ] When the network topology is *uncertain*, how does the FVS / determining guarantee degrade? (Robust FVS over a family of plausible graphs.)
- [ ] Relationship between minimum FVS and the maximum-matching "driver node" set — when do they coincide, when do they differ, and is there a unified theory? (p.139–143, Section 7.)
- [ ] Extension to PDE / spatially-extended regulatory systems (connects back to Foias–Prodi determining-modes literature).

## Related Work Worth Reading
- **Fiedler, Mochizuki, Kurosawa, Saito (2013), "Dynamics and control at feedback vertex sets. I"** — the companion paper; the control theorem (clamping the FVS steers the global attractor). This is the direct Part I. → NOW IN COLLECTION: [Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks](../Fiedler_2013_DynamicsControlFeedbackVertex/notes.md)
- **Mochizuki & Saito (2010)** — "Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks", J. Theor. Biol. 266:323–335: earlier "informative nodes" / linkage-logic steady-state result this line builds on. → NOW IN COLLECTION: [Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks](../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md)
- **Fomin, Gaspers, Pyabelski, Saurabh (2008), "On the minimum feedback vertex set problem: exact and enumeration algorithms"** — already in this collection (`papers/Fomin_2008_MinimumFeedbackVertexSetProblem`); the algorithmic side of computing FVS.
- **Liu, Slotine, Barabási (2011), "Controllability of complex networks"** (Nature 473:167–173) — the structural-controllability / driver-node alternative the paper contrasts itself against. → NOW IN COLLECTION: [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md)
- **Joly (2012)** — observability/symmetries for ODE networks; precise math version of the "which sensors determine the dynamics" question.
- **Letellier & Aguirre** (graph-aided observability of nonlinear systems) and **Takens (1981)** delay-embedding theorem — the dynamical-systems observability backdrop.
- **Foias & Prodi / Ladyzhenskaya** (determining modes/nodes for Navier–Stokes & dissipative PDEs) — the PDE ancestor of "determining nodes."
- **Oda, Matsuoka, Funahashi, Kitano (2005)** — the EGF receptor signaling network map used as the 113-molecule case study.
- **Imai, Levin, Satou et al. (2006)** — the ascidian (Halocynthia/Ciona) early-development gene regulatory network used as the 16-gene case study.
- **Mirsky, Liu, Welsh, Kay, Doyle (2009)** and **Becker-Weimann et al.** — mammalian circadian clock ODE models underlying the 21-component case study.

## Provenance
Notes generated 2026-05-12 from `papers/Mochizuki_2013_DynamicsControlFeedbackVertex/paper.pdf` (sci-hub.ru, DOI 10.1016/j.jtbi.2013.06.009), all 17 pages read as page images. Equations transcribed from the printed text; some Appendix-B rate-constant values are listed at p.146 in the PDF and not reproduced exhaustively here.

## Collection Cross-References

### Now in Collection (previously listed as leads)
- [Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks](../Fiedler_2013_DynamicsControlFeedbackVertex/notes.md) — the companion Part I; supplies the *control* theory (clamping the FVS steers the global attractor onto a prescribed trajectory, including unstable ones) and the FVS ⇔ informative ⇔ determining equivalence + global-attractor reconstruction theorem. This Part II is the observational/monitor half.
- [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md) — Liu–Slotine–Barabási (2011); the structural-controllability / maximum-matching driver-node framework this paper explicitly positions itself against (Section 7). That approach is for linear `ẋ = Ax + Bu` dynamics and "full state control" and gives driver sets via maximum matching; the FVS-monitor result here is for arbitrary nonlinear regulatory dynamics and uses a graph-combinatorial criterion. Driver sets and feedback vertex sets generally differ — on the OEWN definition digraph the matching driver set is ~74% of words vs ~1.5% for the FVS-determining seed.

### Cited By (in Collection)
- [Structure-based control of complex networks with nonlinear dynamics](../Zañudo_2016_Structure-basedControlComplexNetworks/notes.md) — Zañudo–Yang–Albert build on this paper's FVS-control result (their ref 21).

### Conceptual Links (not citation-based)
- [Control of complex networks requires both structure and dynamics](../Gates_2016_ControlComplexNetworksRequires/notes.md) — Gates & Rocha (2016): the *contrast* paper. Mochizuki et al. prove the FVS is a *determining set computable from the wiring diagram alone* and dynamics-correct for every nonlinear rate law; Gates & Rocha prove the rival structure-only constructions (structural controllability / maximum matching, minimum dominating set) are dynamics-*incorrect* once any nonlinearity is present — wrong number of driver variables, wrong variables, governed by canalization / effective connectivity. Different graph functionals, opposite robustness to the dynamics: the FVS-monitor result transfers to definition digraphs (lexical grounding) precisely because it has the property the SC/MDS sets lack.
