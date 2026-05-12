---
title: "Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks"
authors: "Bernold Fiedler, Atsushi Mochizuki, Gen Kurosawa, Daisuke Saito"
year: 2013
venue: "Journal of Dynamics and Differential Equations 25:563-604"
doi_url: "https://doi.org/10.1007/s10884-013-9312-7"
pages: "563-604"
---

# Dynamics and Control at Feedback Vertex Sets. I: Informative and Determining Nodes in Regulatory Networks


## One-Sentence Summary
For ODE regulatory networks on a directed graph with a uniform decay condition, the graph-theoretic notion of a *feedback vertex set* (FVS) coincides with the dynamical notions of *informative* nodes (Mochizuki–Saito) and *determining* nodes (Foias–Temam): observing only the FVS pins down the entire network's long-time dynamics for *every* admissible nonlinearity, and open-loop control (overriding) the FVS forces the rest of the network onto a stable copy of the prescribed trajectory.

## Problem Addressed
Identify the smallest set of nodes in a large regulatory ODE network whose observation (or control) suffices to determine (or steer) the asymptotic state of the whole network — using only the network's wiring graph, independent of the precise nonlinear functional forms.

## Key Contributions
- Theorem 1.3: a subset I of vertices is a set of *determining nodes* for the nonautonomous regulatory network (1.1) **for all admissible nonlinearities** if and only if I is a feedback vertex set of the di-graph Γ. *(p.566)*
- Theorem 1.6: for autonomous networks, the projection of the global attractor onto the FVS history time-tracks (z_I(t), t ≤ 0) is *injective* — the FVS reconstructs the full trajectory of any bounded solution (steady states, periodic, quasiperiodic, chaotic). *(p.567)*
- Corollary 2.4: feedback vertex set ⇔ informative set (Mochizuki–Saito sense). *(p.571)*
- Corollary 4.1: recovers the Mochizuki–Saito steady-state result: stationary solutions agreeing on the FVS are identical. *(p.578)*
- Open-loop control statement (Sect. 8, "control at FVS"): overriding the FVS makes the remaining network follow the prescribed solution.
- Five mathematical examples (acyclic, single self-loop, 2-loop, Lorenz, Frobenius graph) + three biological examples (ascidian cell differentiation; EGF/mammalian signal transduction; mammalian circadian gene network).

## Setup / Methodology
Nonautonomous regulatory ODE network on di-graph Γ with vertices {1,…,N}:

$$ \dot z_k = F_k(t, z_k, z_{I_k}), \quad k = 1,\dots,N $$
Where: z_k ∈ ℝ is the state of node k; I_k ⊆ {1,…,N} is the *input set* (predecessors) of k; z_{I_k} = P_{I_k} z is the projection onto those coordinates; edges i→k exist iff i ∈ I_k. Self-loops k ∈ I_k allowed. Autonomous variant (1.3): ẋ_k = F_k(z_k, z_{I_k}). *(p.564)*

Standing assumptions:
- F_k, F_{k,z} continuous (C^0); for the global-attractor theorem F_k ∈ C^1. *(p.564)*
- **Dissipativity:** every solution eventually enters a fixed Euclidean ball of radius C. Sufficient condition: Σ_k z_k F_k(t,z,z_{I_k}) < 0 for |z| ≥ C (eq 1.4). *(p.564-565)*
- **Decay condition (1.5):** ∂_1 F_k(t, z_k, z_{I_k}) < 0 for all t ≥ 0 and bounded z — the partial derivative wrt the *own* variable z_k is strictly negative. Holds automatically for loop-free Γ; e.g. F_k = f_k(t,z_{I_k}) − d_k(t) z_k with positive dilution/decay d_k. *(p.565)*
- Self-loops circumvent (1.5); to handle a net-positive self-feedback, augment with artificial variable: \tilde F_k(t, ζ_k, z_{\tilde I_k}) := F_k(t,z_k,z_{I_k}) + z_k − ζ_k, then set ζ_k := z_k (eq 1.6). *(p.565)*

Determining nodes (Def 1.1, after Foias–Temam Navier–Stokes context, ref [11]): I is *determining* if for any two solutions z, \tilde z of ż = F(t,z) with \tilde z_I(t) − z_I(t) → 0 as t→+∞, then \tilde z(t) − z(t) → 0. *(p.566)*

Feedback vertex set (Def 1.2): I ⊆ V is an FVS of di-graph Γ if Γ∖I (remove I and all incident edges) is acyclic. Empty FVS ⇔ Γ acyclic. Minimal FVS not unique in general. Finding minimum FVS for di-graphs is NP-complete (ref [19]). *(p.566)*

Informative set (Def 2.1, Mochizuki–Saito [28]): I is *informative* if for any nonzero ζ with ζ_I = 0 there exists a vertex n with ζ_n ≠ 0 but ζ_{I_n} = 0. Equivalently: any two states agreeing on I and on the predecessors of n must agree at n. *(p.570)*

Global attractor (Def 1.4): A := {z(0) : sup_{t∈ℝ}|z(t)| < ∞}; nonempty, compact, invariant, smallest set attracting bounded sets, largest compact invariant set (Prop 1.5). *(p.567)*

## Proof architecture
- §2: Labeling Lemma 2.2 — if I is informative (relabel I = {N'+1,…,N}, N' = N−|I|) there is an ordered labeling of Γ∖I with I_{n'} ⊆ I ∪ {1,…,n'−1} (eq 2.1) for all n' ∈ J = {1,…,N'}. Lemma 2.3: same labeling characterizes FVS. ⇒ Corollary 2.4 (FVS ⇔ informative). Also: FVS invariant under reversing all edge orientations. *(p.570-571)*
- §3: Linear lemma 3.1 — for ẇ_k = −a_k(t)w_k + b_k(t)^T w_{I_k} with 0 < a_0 ≤ a_k(t), |b_k(t)| ≤ b_0: w_I(t)→0 implies w(t)→0 (variation of constants + induction along labeling order, Lebesgue dominated convergence). Lemma 3.2: the difference w = \tilde z − z of two nonlinear solutions satisfies ẇ = A(t)w with A(t) = ∫_0^1 ∂_z F(t, z+ϑw)dϑ; decay (1.5) gives the lower bound a_0; apply Lemma 3.1 ⇒ FVS ⇒ determining (if-part of Thm 1.3). *(p.572-574)*
- §4: Proof of Thm 1.6 — for two solutions in A agreeing on I for all t ≤ 0, shift the variation-of-constants initial time t_0 → −∞ to get w_k(t) = ∫_{-∞}^t exp(−∫_s^t a_k)b_k^T w_{I_k} ds; recursion along labeling order with w_I ≡ 0 ⇒ w ≡ 0 ⇒ injectivity of P_I on A. Corollary 4.1 recovers [28] steady-state uniqueness. *(p.575-578)*
- §6: only-if part of Thm 1.3 (FVS necessary) — built from the mathematical examples in §5.

## Mathematical examples (§5)
- 5.1 acyclic Γ: empty FVS; whole network determined by initial-condition-free asymptotics.
- 5.2 single self-loop.
- 5.3 loop of length two (two vertices 1↔2): minimal FVS = {1} or {2}, non-unique.
- 5.4 Lorenz equations as a 3-node network — feedback vertices of Lorenz.
- 5.5 linear autonomous Frobenius graph (Fig. 1): one-point FVS I = {N} (the self-looped vertex).

## Biological examples (§7) — see companion paper [29] (Mochizuki et al., J Theor Biol 2013)
- Ascidian (Halocynthia) cell-differentiation gene regulatory network (Imai et al., Science 2006).
- EGF / mammalian signal-transduction network (Oda et al., Mol Syst Biol 2005).
- Mammalian circadian-rhythm gene network (Mirsky et al., PNAS 2009).
In each, the FVS (observation/control set) is far smaller than the whole network.

## Key Equations
$$ \dot z_k = F_k(t, z_k, z_{I_k}), \quad k=1,\dots,N $$
Regulatory network ODE on di-graph Γ; I_k = predecessors of k. *(p.564)*

$$ \partial_1 F_k(t, z_k, z_{I_k}) < 0 $$
Decay condition (1.5): own-variable Jacobian strictly negative; holds automatically for loop-free Γ. *(p.565)*

$$ \widetilde F_k(t,\zeta_k, z_{\widetilde I_k}) := F_k(t,z_k,z_{I_k}) + z_k - \zeta_k,\quad \zeta_k := z_k $$
Self-loop augmentation (1.6) to make a net-positive self-feedback satisfy (1.5). *(p.565)*

$$ I_{n'} \subseteq I \cup \{1,\dots,n'-1\}\ \text{for all } n' \in J=\{1,\dots,N'\},\quad N' = N-|I| $$
Labeling-order property (2.1) characterizing both informative sets and FVS. *(p.569)*

$$ \dot w(t) = A(t) w(t),\quad A(t) := \int_0^1 \partial_z F(t, z(t)+\vartheta w(t))\, d\vartheta $$
Difference w = \tilde z − z of two solutions; decay (1.5) gives the uniform lower bound on −A's diagonal. *(p.574)*

$$ \mathcal P_I : \mathcal A \to BC^2(\mathbb R_-, \mathbb R^{|I|}),\quad z(0) \mapsto z_I(\cdot)\ \text{is injective} $$
Attractor reconstruction (Thm 1.6, eq 1.14). *(p.567)*

$$ \dot z = Cz - z,\quad p_C(\lambda) = \lambda^N + c_{N-1}\lambda^{N-1} + \dots + c_0 $$
Linear Frobenius example (5.12-5.13): companion matrix; minimal FVS = {N}; spectrum of C−id chosen via p_C(λ+1)=0. *(p.581)*

$$ (\lambda+1)^m - 1 = 0 \ \Rightarrow\ \lambda = e^{2\pi i k/m} - 1,\ k=0,\dots,m-1 $$
Spectrum of the m-cycle linear construction (6.4-6.5) used to prove FVS is necessary; Re λ < 0 except trivial λ=0 ⇒ multiplicity invisible on a non-FVS I. *(p.583)*

$$ \dot z^1 = F(z^1),\quad \dot z^2 = F(z^2) + D(z^1 - z^2),\ D = \mathrm{diag},\ d_k = 0\ \text{unless } k\in I\ (\text{FVS}) $$
Chaos-synchronization via FVS-only coupling (8.29) ⇒ z²(t) ≈ z¹(t). *(p.600)*

## Relevance to Project (definition digraphs / MinSet)
A *definition digraph* (words → words used in their definitions) is exactly a di-graph Γ; the lexical "grounding set" / MinSet that must be defined externally is a feedback vertex set of that digraph (cf. Fomin 2008 in this collection — MinSet reduces to FVS). This paper supplies the dynamical-systems analogue: if one models "meaning" as a flow on the definition digraph, then (a) the FVS is the minimal set of words whose fixed semantics *determines* the semantics of every other word, for *any* admissible compositional rule (F_k is unconstrained beyond decay/dissipativity); (b) overriding (grounding) the FVS *forces* the rest of the lexicon onto a unique consistent assignment — and §7.3 shows this even works onto otherwise-unstable configurations. The "regardless of nonlinear functional form" property is the key transfer: the grounding-set claim is structural, not dependent on how definitions compose.

Specific transferable points: (1) Source nodes (empty predecessor set — words defined by ostension / primitives, never in terms of other listed words) behave like the C_⁻ "ultimate predecessors": they converge to fixed values and must simply be given; the practical observation/grounding set is FVS ∪ {source nodes}, matching the task statement. (2) The proper reduction is to the *cyclicity set* C_0 (words on definitional cycles), not to the FVS — knowing only the "current state" of the FVS isn't enough, you need its trajectory; the lexical analogue: a single consistent fixpoint is the "stationary solution" special case where the FVS *initial condition* does determine everything (Cor 4.1 / §8.2), which is plausibly the regime we actually care about for static dictionaries. (3) Non-uniqueness of minimal FVS (the EGF network had 36) ⇒ there is no canonical MinSet; redundancy is useful for consistency checks (caveat 8.2-i). (4) The load-bearing assumption with no obvious lexical analogue is the decay condition (1.5)/dissipativity — for a static-fixpoint reading this is the Mochizuki-Saito *informative*-set characterization (Def 2.1, purely combinatorial: "any nonzero ζ vanishing on I has a vertex n with ζ_n ≠ 0 but ζ vanishing on I_n"), which is exactly "the only assignment agreeing with the grounding set on every recursively-resolvable word is the intended one" — that transfers cleanly without any dynamics. (5) Caveat against over-claiming: this is not a *dimension reduction* of meaning; it is an *identification* result (which words pin down which).

## Mathematical examples — details (§5)
- **5.1 Acyclic Γ:** empty FVS I=∅; if-part of Thm 1.3 ⇒ \tilde z(t) − z(t) → 0 for any two solutions (eq 5.3). Degree theory ⇒ A contains a stationary z; uniqueness ⇒ A = {z}, a globally asymptotically stable point. *(p.579)*
- **5.2 Single self-loop:** ż_1 = F(z_1), z_1 ∈ ℝ (eq 5.4); decay (1.5) void; dissipativity ⇔ F(z)z < 0 for |z| ≥ C (eq 5.5). I = {1} the only FVS; A = [min zero of F, max zero of F]. Polynomials F(z) = −z^{2n+1} + ⋯ + c_0 of odd degree give arbitrarily many coexisting equilibria. Proves the only-if part (FVS necessary) for the self-loop: I=∅ fails whenever F has >1 real zero. *(p.579)*
- **5.3 Loop of length 2:** ż_1 = G_1(z_1,z_2), ż_2 = G_2(z_1,z_2) (eq 5.7); decay (5.8): ∂_1 G_1 < 0, ∂_2 G_2 < 0. Minimal FVS = {1} or {2}, non-unique. Decay ⇒ negative divergence ⇒ gradient-like, no periodic/homoclinic/heteroclinic orbits. Explicit multi-equilibrium dissipative example (5.9): ż_1 = a z_2 − z_1, ż_2 = sin z_1 − z_2, a > 1. *(p.580)*
- **5.4 Lorenz system** (eq 5.10): ż_1 = σ z_2 − σ z_1; ż_2 = ρ z_1 − z_1 z_3 − z_2; ż_3 = z_1 z_2 − β z_3. As a regulatory network on Fig. 4, unique minimal FVS I = {2}. ⇒ monitoring history time-track z_2(t), t ≤ 0, reconstructs the whole Lorenz attractor dynamics. Also applies to chaotic Chen system (ref [5]). *(p.580-581)*
- **5.5 Frobenius matrices** (Fig. 1): linear autonomous ż_k = z_{k+1} − a_0 z_k (k<N), ż_N = −c_0 z_1 − ⋯ − c_{N-1} z_N − a_0 z_N; i.e. ż = Cz − z with C a companion (Frobenius) matrix, char. poly p_C(λ) = λ^N + c_{N-1}λ^{N-1} + ⋯ + c_0 (eq 5.13). Minimal FVS I = {N}. Spectrum of C − id chosen arbitrarily via shifted zeros p_C(λ+1)=0. Dissipativity enforced by nonlinear modification a_0 = a_0(z) = 1 + χ(z²) (eq 5.14). For purely imaginary simple spectrum, the FVS component z_N(t) recovers the full quasiperiodic solution z(t) = Σ_j α_j e^{iω_j t} z^j via Fourier averages (Mz_N)(ω) = lim_{T→−∞} (1/T)∫_0^T z_N(t)e^{−iωt}dt = α_j z_N^j at ω = ω_j, 0 else (eq 5.18) — because z_N^j ≠ 0 for all j. *(p.581-582)*

## §6 — FVS is necessary (only-if part of Thm 1.3)
Lemma 6.1: if I is **not** an FVS of Γ, there exist smooth dissipative F_k with decay (1.5) such that I is not determining. Proof: Γ∖I has a cycle M = {1,…,m}. Off M choose pure decay F_k(z_k,z_{I_k}) := −z_k (eq 6.1) ⇒ z_k → 0 there, so those nodes are invisible on I. On M choose F_k(z_k, z_{I_k}) = F_k(z_k, z_{k+1}) (cyclically), I_k = {k+1} mod m (eq 6.2). m=1 ⇒ self-loop (example 5.2, multiple equilibria); m=2 ⇒ 2-loop (example 5.3); m ≥ 3 ⇒ linear F_k(z_k,z_{k+1}) := z_{k+1} − z_k (eq 6.3), char poly (λ+1)^m − 1 = 0 (eq 6.4), spectrum = shifted roots of unity λ = e^{2πik/m} − 1 (eq 6.5), Re λ < 0 except trivial λ = 0 with eigenvector (1,…,1) ⇒ a line of stationary solutions ⇒ multiplicity invisible on I. Slight perturbation gives generic hyperbolic multiple stable/unstable equilibria/periodic orbits. Minimality of Γ not required but achievable with a more intricate construction (constancy of the Γ-coupling on the constructed orbit values; local constancy of switching nonlinearities makes this realistic — cf. ascidian network, §4-2 of [29]). *(p.582-584)*

## §7 — Biological applications (companion paper: Mochizuki et al., J Theor Biol 2013, ref [29])
General point: regulatory edges give only the wiring; quantitative regulatory functions, rates, initial conditions are unknown — but for *determining* via the FVS those details are irrelevant. Incompleteness of the assumed network shows up as inconsistency between traced and observed dynamics ⇒ predicts missing edges/molecules. *(p.584)*

- **7.1 Ascidian (Ciona intestinalis) cell-differentiation gene network** (Imai et al., Science 2006, ref [17]): 80 genes, edges = activation/repression (not distinguished, per decay 1.5); 16 genes have self-edges, all self-repressions — removed and subsumed under decay (1.5). Iteratively remove vertices with no input or no output (top/bottom genes converging to fixed inputs / inert outputs) — this preserves all di-cycles hence all minimal FVS. Reduced network: 7 vertices (Fig. 6), unique minimal FVS = a single vertex **FoxD-a/b**. ⇒ all long-term dynamics on A identifiable from FoxD-a/b activity alone. Caveat: 13 distinct tail-bud gene-expression patterns observed but recorded binary (active/inactive) — cannot be told apart in a 1D binary space; resolutions: (i) measure FoxD-a/b quantitatively, (ii) the patterns aren't stable equilibria of the ODE, (iii) the network in [17] is incomplete (missing feedback loops not cut by FoxD-a/b). *(p.584-585)*
- **7.2 EGF signal-transduction network** (Oda et al., Mol Syst Biol 2005, ref [30]): 113 species (kinases, phosphatases, ions e.g. Ca²⁺), no self-edges; remove no-input/no-output vertices ⇒ 61-vertex reduced network. Computer-aided **exhaustive search** for a minimum FVS using only Def 1.2, trying candidate sets from small to large size: found minimum size = 5 vertices, with **36 different minimal FVS** (Table 1: vertices group into 5 categories shown as polygon shapes in Fig. 7; combinatorial counts 2×3×3 = 18 and 3×6 = 18; e.g. ErbB11, SOS/ERK1/2, HB-EGF/c-Src/ADAMS, cyt Ca²⁺/CaM/CaMKII, PI4,5-P2 …). Need time-series of these key molecules to faithfully track dynamics; theory gives a rational selection criterion. *(p.585-587)*
- **7.3 Mammalian circadian-rhythm gene network** (Mirsky et al., PNAS 2009, ref [27]/[31]): the example where they **numerically demonstrate open-loop control** by overriding the informative set — forcing the key variables makes the rest of the network follow. (Detail continues on later pages.) *(p.587)*

## Parameters / quantities

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Dissipativity radius | C | — | — | "sufficiently large" | 564-565 | ball solutions enter |
| Decay-condition sign | ∂_1 F_k | — | < 0 | — | 565 | own-variable Jacobian strictly negative |
| Linear decay lower bound | a_0 | — | > 0 | 0 < a_0 ≤ a_k(t) | 572 | uniform lower bound in Lemma 3.1 |
| Linear coupling bound | b_0 | — | — | \|b_k(t)\| ≤ b_0 | 572 | uniform upper bound |
| Ascidian network size | N | genes | 80 → 7 (reduced) | — | 584-585 | minimal FVS = 1 (FoxD-a/b) |
| EGF network size | N | species | 113 → 61 (reduced) | — | 585-586 | minimum FVS size = 5; 36 distinct minimal FVS |
| Frobenius FVS size | \|I\| | nodes | 1 | — | 581 | I = {N}, the self-looped node |
| Lorenz FVS size | \|I\| | nodes | 1 | — | 580 | I = {2}, unique minimal FVS |

## Algorithmic content
- **Minimal FVS search (used on the EGF network), §7.2:** simple, exhaustive, brute-force — enumerate candidate vertex subsets in increasing size, test acyclicity of Γ∖I (Def 1.2), stop at first size that yields an FVS; enumerate all FVS of that size. No heuristic given here beyond "iteratively delete no-input/no-output vertices first (preserves all di-cycles, hence all minimal FVS) to shrink the graph." Finding a minimum FVS for di-graphs is NP-complete (ref [19] = Karp). *(p.566, 585-586)*

## §7.3 — Open-loop control of the mammalian circadian network (the "control at FVS" demonstration)
Model: Mirsky et al. PNAS 2009 (ref [25]), 21 variables, 132 parameters (full ODEs + parameter values in the Appendix; integrated by Euler Δt = 0.001). Regulatory di-graph in Fig. 8a; chosen FVS I has **7 vertices**: I = {PER1, PER2, CRY1, CRY2, RORc, CLK/BMAL1, CLK}. Under a non-standard parameter choice the model has 4 coexisting asymptotic behaviors: two stable periodic orbits P1, P2; one unstable periodic orbit UP; one unstable stationary point USS. *(p.587-588)*

**Control protocol** ("from P1 to P2"): prescribe (clamp) the forward time-tracks z_I(t) of the 7 informative variables to equal their values z_I^{P2}(t) on P2; integrate the remaining 14 ODEs from an initial state taken on the P1 orbit. Result: trajectory leaves P1, converges to P2. Symmetric experiments "P2→P1", "P1→UP", "P2→USS" all succeed — including forcing the network onto the *unstable* orbit/point. ⇒ open-loop control at an FVS overrides the rest of the network onto *any* prescribed trajectory of the network, even unstable ones. *(p.587-588)*

**Reduced FVS, eq 7.1:** I_* := I∖{CLK} = {PER1, PER2, CRY1, CRY2, RORc, CLK/BMAL1} (6 vertices) — *not* a full FVS (Γ∖I_* still has a 2-loop CLK↔BMAL1) — yet clamping I_* still controls the whole network. Reason (Sect. 7.4): the CLK/BMAL1 subsystem (eq 7.5: Ḃ = β(t) − aBC − k_B B, Ċ = γ(t) − aBC − k_C C) does not feed back into the clamped feed-variables except through CLK/BMAL1 ∈ I_*; the difference (b,c) of two solutions satisfies a linear system (eq 7.6) with positive bounded coefficients ⇒ monotone-decay argument forces b,c → 0 (eqs 7.7-7.8). This is *model-specific* — the bare graph cannot reveal it (only-if part of Thm 1.3). Further reduction: clamping only 5 vars I' = {PER1, PER2, CRY1, CRY2, RORc} **fails** ("from P1 to P2" converges to a spurious quasiperiodic orbit, Fig. 10), but clamping a *different* 5-set I'' = {PER1, CRY1, CRY2, RORc, CLK/BMAL1} *succeeds*. ⇒ controlling a non-informative subset may or may not work depending on which nodes and which reference solution; the *full* FVS is the safe choice. (In companion [29], the 6-set I^* = {PER1,PER2,CRY1,CRY2,RORc,BMAL1} fails.) *(p.588-590)*

## §8 — Discussion, generalizations, caveats
**8.1 Further examples.** Damped harmonic oscillator z̈ + 2νż + ω²z = 0 (eq 8.1) ⇔ a 2-loop regulatory network (eq 8.2); negative discriminant ν²<ω² ⇒ negative feedback (Fig. 11). Tempting but wrong to expect empty FVS in general: nonautonomous ω²=ω(t)² (Mathieu, parametric resonance — "how children destabilize a swing") destabilizes z≡0. Chemical reaction networks subsumed: a step Z_1+Z_2→Z_3+Z_4 with decay rates d_j gives ż_k = ⋯ ± k(z_1,z_2) − d_k z_k (eqs 8.3-8.4), k = mass-action κz_1z_2 or Michaelis-Menten κz_1z_2/(1+κ_1z_1+κ_2z_2); contributes a 2-loop 1↔2 (Fig. 12); reversible reaction ⇒ complete bidirectional 4-graph ⇒ any 3 vertices form an FVS. Autocatalytic Z_1+Z_2→Z_1+Z_3 with constant feeds a_1,a_2 ⇒ acyclic graph (Fig. 13) ⇒ empty FVS, global convergence. Mochizuki-form ż_k = f_k(t,z_{I_k}) − d_k(t)z_k (eq 8.7) with ∫_{-∞} d_k = +∞ (eq 8.8): explicit recursion z_{n'}(t) = ∫_0^∞ exp(−∫ d_{n'})φ_{n'}(t−s)ds (eq 8.11) reconstructs noninformative nodes; exponential error exp(−δT) (eq 8.12) if z_I known only on [0,T] and inf d_{n'} > δ > 0 (or inf −∂_1 F_{n'} > δ > 0, eq 8.14, for general networks — but no explicit recursion in the nonlinear case). *(p.590-595)*

**8.2 Caveats.** (i) Finding/deciding k-element FVS of a di-graph is NP-complete (ref [19] Karp; recent progress ref [7] Chen et al., fixed-parameter algorithm, J. ACM 2008). Data accessibility should drive selection of I more than minimality; redundant I useful for cross-checking & detecting network errors. (ii) The *full* informative set is needed for the all-nonlinearities guarantee — smaller subsets may be determining for specific F_k but the necessity proof (§6) required determining-for-all-F_k. (iii) Naive Takens embedding (ref [35]) claiming reconstruction from a single node z_k(t) is not justified by the genericity hypotheses — patently fails at any input vertex k with empty I_k. Joly [18] does show single-node reconstruction of stationary & periodic solutions under C¹-genericity of the regulatory functions — but C¹-genericity may fail for all C² nonlinearities and (more importantly) excludes biologically relevant *switching* behavior where nonlinearities locally become independent of some inputs. Generic linear example: diagonalizable C with distinct λ_j, all off-diagonal entries & all eigenvector components nonzero ⇒ ż = Cz − z has at least the complete graph, minimal FVS has ≥ N−1 elements, yet a single z_k(t) reconstructs z(t). Lorenz also reconstructs from z_1(t) (since z_2 = z_1 + ż_1/σ) despite I = {2}. **None of this contradicts the only-if part** — it holds for *all* nonlinearities, not just generic ones. (iv) Do NOT mistake the FVS for a dimension reduction: knowing only z_I(0) (initial condition, not full history) does not determine z(0); the Frobenius example with singleton I = {N} still has periodic/quasiperiodic solutions. Only for stationary solutions does z_I(0) determine the (constant) history. *(p.594-596)*

**8.3 Generalizations.** Genuine dimension reduction: on the global attractor A, the dynamics reduces to an autonomous ODE on the **cyclicity set** C_0 = {vertices on di-cycles of length ≥ 2, or with self-loops}. If C_0 strongly connected: decompose {1,…,N} = C_⁻ ∪ C_0 ∪ C_⁺ (eq 8.16, predecessors / cyclicity / successors); C_⁻ converges to a unique equilibrium (I_{C_⁻}=∅), substitute it ⇒ reduced ODE ż_k = \tilde F_k(z_k, z_{I_k∩C_0}) on C_0 (eq 8.17); the successors are enslaved z_{C_⁺} = Φ(z_{C_0}) (eq 8.18, via Thm 1.6 injectivity). General C_0: Morse-type decomposition {1,…,N} = C_⁻ ∪ C_0 ∪ H ∪ C_⁺ (eq 8.19), C_0 = C_1 ∪ ⋯ ∪ C_m strongly-connected components (eq 8.20), induct over j ⇒ z_{H∪C_⁺} = Φ(z_{C_0}) (eq 8.21), skew-product structure. Conservative bound on attractor dimension for Takens: |C_0|. Also extends to: discrete-time iterations z_k^{n+1} = F_k^n(z_k^n, z_{I_k}^n) (eqs 8.22-8.24, decay becomes |∂_1 F_k^n| < 1; no invertibility needed); vector-valued nodes z_k ∈ ℝ^{m_k} (eqs 8.25-8.26, ∂_1 F_k negative definite); reaction-diffusion PDEs z_{k,t} = D_k Δ_x z_k + F_k(t,x,z_k,z_{I_k}) (eq 8.27, D_k Δ + ∂_1 F_k negative definite; reduction stops at full informative *profiles* z_I(t,x)); stochastic ż_k = F_k(ω,t,z_k,z_{I_k}) (eq 8.28, FVS still determining for each ω if graph & decay uniform in ω). *(p.596-599)*

**8.4 Further applications.** Open-loop *control* (already done in §7.3) ⇒ feedback vertex sets are the natural target for closed-loop feedback control too: monitor via z_I(t), actuate via control variables u(t) injected into ż_i = ⋯ + u(t) for i ∈ I. **Chaos synchronization / signal encryption**: master-slave ż¹ = F(z¹), ż² = F(z²) + D(z¹−z²) (eq 8.29) with D = diag, d_k = 0 unless k ∈ FVS I, d_k large on I ⇒ z²(t) ≈ z¹(t) (eq 8.30) — i.e. transmit only z_I(t) (which may look chaotic) to force synchrony; the systematic identification of the informative carrier signal is this paper's contribution. Also neural nets (FitzHugh-Nagumo cells eq 8.31 — but cubic nonlinearity forces self-loops at every z_k¹ ⇒ no proper FVS reduction; Morse-decomposition still applies) and electrical power grids (monitor phase via FVS sensors, possibly redundant). *(p.599-602)*

**8.5 Conclusion / "informative sets are crucial for: (i) where to measure, (ii) aiding modeling, (iii) checking data consistency, (iv) controlling dynamical properties."** Any cut of Γ into two units (one preceding the other along edges) lets the preceding unit control the following one, to an extent set by their respective FVS — a route to understanding hierarchical modularity. *(p.602)*

**Appendix:** full 21-variable mammalian circadian ODE system (eqs 9.1-9.21, Hill-function regulation for the mRNA species Per1, Per2, Cry1, Cry2, Rev-erbα, Clk, Bmal1, Rorc + mass-action complexation for the proteins/complexes PER1, PER2, CRY1, CRY2, REV-ERBα, CLK, BMAL1, RORc, PER1/CRY1, PER2/CRY1, PER1/CRY2, PER2/CRY2, CLK/BMAL1) and the 132 parameter values used. *(p.602-604)*

## Limitations (consolidated)
- Decay condition (1.5) / dissipativity are required and load-bearing; net-positive self-loops only handled via the augmentation trick (1.6). *(p.565)*
- Identifying a small FVS is NP-complete; in practice data accessibility, not minimality, should drive the choice. *(p.595)*
- FVS is NOT a dimension reduction — needs the full history track z_I(t), t≤0, not just z_I(0); singleton-FVS networks still have periodic/quasiperiodic dynamics. *(p.596)*
- The "for all nonlinearities" guarantee needs the full FVS; a non-informative subset may control/determine one reference solution and fail on another (circadian I' example). *(p.589, 596)*
- Reconstruction-from-a-single-node (Takens / Joly) requires genericity that excludes switching nonlinearities — orthogonal to this paper's all-nonlinearities claim. *(p.594-595)*

## Arguments against prior work
- Foias–Temam determining nodes [11] were developed for Navier–Stokes via spectral-gap arguments and reduce ∞→finite-dim observations; this paper instead reduces *large finite* networks to *very few* observations using only graph structure — no spectral gap, no genericity. *(p.565)*
- Naive Takens-embedding claims (single-node reconstruction) are not warranted by the actual genericity hypotheses of the embedding theorem; fail at empty-predecessor input vertices. *(p.594)*
- Joly's [18] single-node genericity result fails for the biologically realistic case of switching nonlinearities (functions locally independent of some inputs) which "undermine the underlying graph structure" his proof exploits. *(p.594-595)*

## Design rationale
- Use FVS (= informative = determining) rather than ad-hoc node sets because (a) the determination/control property then holds for *every* admissible nonlinearity, i.e. it is structural; (b) FVS is invariant under reversing all edge orientations; (c) the labeling-order lemma makes the proofs a clean induction (variation of constants along an acyclic order on Γ∖I). *(p.566, 571)*
- Subsume net-negative self-feedback under the decay condition rather than as an explicit self-loop, so that loop-free graphs automatically satisfy (1.5) and the FVS shrinks. *(p.565)*
- Reduce graphs by iteratively deleting no-input/no-output vertices before FVS search — proven to preserve all di-cycles, hence all minimal FVS. *(p.585)*

## Testable properties
- I is determining for (1.1) for all admissible F_k ⇔ I is an FVS of Γ. *(p.566)*
- I empty ⇔ Γ acyclic ⇔ A is a single globally asymptotically stable equilibrium. *(p.566, 579)*
- For autonomous dissipative C¹ networks with decay (1.5): the map A → BC²(ℝ_⁻,ℝ^{|I|}), z(0) ↦ z_I(·), is injective. *(p.567)*
- Removing no-input/no-output vertices preserves the set of minimal FVS. *(p.585)*
- Clamping a full FVS forces every other node onto the reference trajectory as t→+∞; clamping a proper subset need not. *(p.589, 597)*
- Reduced ODE on the cyclicity set C_0 captures all global-attractor dynamics; |C_0| bounds the attractor dimension. *(p.596, 598)*

## Figures of interest
- **Fig. 1 (p.565):** Frobenius di-graph, N vertices, 2N−1 edges, self-loop at N; unique minimal FVS = {N}.
- **Fig. 2 (p.569):** maximal di-graph with informative set I = {N} (illustrates labeling Lemma 2.2).
- **Fig. 3 (p.578):** single self-loop (a), 2-cycle (b) — minimal examples where FVS necessity is proven.
- **Fig. 4 (p.580):** Lorenz system as a 3-node regulatory network; unique minimal FVS = {2}.
- **Fig. 5 (p.585):** ascidian *Ciona* gene regulatory network (80 genes, after removing self-repressions) — large dense graph.
- **Fig. 6 (p.586):** reduced ascidian network (7 vertices) — single feedback vertex FoxD-a/b.
- **Fig. 7 (p.587):** EGF signal-transduction network (61 vertices), the 5 FVS-vertex categories drawn as polygon shapes.
- **Fig. 8 (p.588):** mammalian circadian network (21 vars); chosen 7-vertex FVS marked by circles; (b)(c) trajectories of P1/P2/UP/USS in the Per1–Per2 plane (Per1, Per2 are NOT in the FVS).
- **Fig. 9 (p.589):** successful open-loop controls by the full 7-vertex FVS (P1→P2, P2→P1, P1→UP, P1→USS).
- **Fig. 10 (p.590):** failed control by the 5-vertex non-informative set I' — converges to a spurious quasiperiodic orbit.
- **Figs 11-14 (p.591-601):** damped oscillator 2-loop; chemical-reaction graphs; FitzHugh-Nagumo neural motif.

## Open Questions
- [ ] Does the static-fixpoint ("stationary solution") special case — where the FVS *initial condition* alone determines everything (Cor 4.1) — carry over to definition digraphs without needing a dynamics? (Def 2.1 informative-set suggests yes, purely combinatorially.)
- [ ] Lexical analogue, if any, of the decay/dissipativity condition (1.5)? Needed only for the dynamical (history-track) version, not the steady-state version.
- [ ] Cyclicity-set reduction (§8.3): is the right "irreducible core" of a dictionary the union of words on definitional cycles, everything else enslaved?

## Related Work Worth Reading / leads
- **Mochizuki, Fiedler, Kurosawa, Saito — "Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks", J. Theor. Biol. 2013 (ref [29])** — the companion biology paper; the obvious next read.
- **Mochizuki & Saito 2010, "Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks", J. Theor. Biol. 266:323-335 (ref [28])** — origin of *informative nodes*; the steady-state precursor. → NOW IN COLLECTION: [`../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md`](../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md)
- **Mochizuki 2008, "Structure of regulatory networks and diversity of gene expression patterns", J. Theor. Biol. 250:307-321 (ref [27])**.
- **Foias & Temam 1984, "Determination of the solutions of the Navier–Stokes equations by a set of nodal values", Math. Comput. 43:117-133 (ref [11])** — origin of *determining nodes*.
- **Karp 1975, "Reducibility among combinatorial problems", Kibernet. Sb. 12:16-83 (ref [19])** — FVS NP-completeness.
- **Chen, Liu, Lu, O'Sullivan, Razgon 2008, "A fixed-parameter algorithm for the directed feedback vertex set problem", J. ACM 55(21) (ref [7])** — the practical FVS algorithm.
- **Joly 2012, "Observation and inverse problems in coupled cell networks", Nonlinearity 25:657-676 (ref [18])** — single-node generic reconstruction.
- **Imai, Levine, Satoh, Satou 2006, "Regulatory blueprint for a chordate embryo", Science 312:1183-1187 (ref [17])** — ascidian network source.
- **Oda, Matsuoka, Funahashi, Kitano 2005, "A comprehensive pathway map of EGF receptor signaling", Mol. Syst. Biol. 1:1-17 (ref [30])** — EGF network source.
- **Mirsky, Liu, Welsh, Kay, Doyle III 2009, "A model of the cell-autonomous mammalian circadian clock", PNAS 106:11107-11112 (ref [25])** — circadian model source.
- (Not cited here but the standard downstream FVS-control reference: Zañudo, Yang, Albert 2017, "Structure-based control of complex networks with nonlinear dynamics", PNAS — worth getting next.)

## Collection Cross-References

### Already in Collection
- [Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks](../Mochizuki_2013_DynamicsControlFeedbackVertex/notes.md) — the companion biology paper (ref [29], "Part II"); detailed biological analysis, in-silico identification rates, the I^* circadian counterexample.
- [Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks](../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md) — Mochizuki & Saito 2010 (ref [28]); origin of *informative nodes* / "linkage logic"; the steady-state precursor recovered here as Corollary 4.1.
- [On the minimum feedback vertex set problem: Exact and enumeration algorithms](../Fomin_2008_MinimumFeedbackVertexSetProblem/notes.md) — not cited by Fiedler et al. (they cite Karp [19] and Chen et al. [7] for FVS complexity) but the same algorithmic backbone: the §7.2 brute-force minimal-FVS search is the naive version of these exact algorithms.

### New Leads (Not Yet in Collection)
- Foias, C., Temam, R. (1984) — "Determination of the solutions of the Navier–Stokes equations by a set of nodal values", Math. Comput. 43:117–133 (ref [11]) — origin of *determining nodes*.
- Chen, J., Liu, Y., Lu, S., O'Sullivan, B., Razgon, I. (2008) — "A fixed-parameter algorithm for the directed feedback vertex set problem", J. ACM 55(21) (ref [7]) — the practical directed-FVS algorithm.
- Joly, R. (2012) — "Observation and inverse problems in coupled cell networks", Nonlinearity 25:657–676 (ref [18]) — single-node generic reconstruction, contrasted here.
- Imai et al. 2006 (Science 312, ref [17]); Oda et al. 2005 (Mol. Syst. Biol. 1, ref [30]); Mirsky et al. 2009 (PNAS 106, ref [25]) — the three biological network sources.

### Supersedes or Recontextualizes
- Recovers Mochizuki & Saito 2010 [28] (steady-state uniqueness on informative sets) as a special case (Cor 4.1) — [28] is now in the collection: [`../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md`](../Mochizuki_2010_AnalyzingSteadyStatesDynamics/notes.md).
- Generalizes the determining-nodes idea of Foias & Temam 1984 [11] from PDEs (spectral gap) to finite regulatory networks (graph structure) — [11] not in the collection.

### Cited By (in Collection)
- [Dynamics and control at feedback vertex sets. II: A faithful monitor to determine the diversity of molecular activities in regulatory networks](../Mochizuki_2013_DynamicsControlFeedbackVertex/notes.md) — Part II is the companion to this Part I.
- [Structure-based control of complex networks with nonlinear dynamics](../Zañudo_2016_Structure-basedControlComplexNetworks/notes.md) — Zañudo–Yang–Albert build on the Fiedler/Mochizuki FVS-control result, extending it to Boolean/threshold and other discrete dynamics.

### Conceptual Links (not citation-based)
- [How Is Meaning Grounded in Dictionary Definitions?](../Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md) — Massé et al. prove "grounding sets = feedback vertex sets" for definition digraphs; this paper is the dynamical-systems analogue (FVS = determining/controlling set for *any* dynamics on the graph). Strong convergence: same graph object, different layer (semantics vs. ODE dynamics).
- [The Latent Structure of Dictionaries](../Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md) — MinSets in their dictionary-graph decomposition are feedback vertex sets; Fiedler's cyclicity-set reduction (§8.3, Morse decomposition C_⁻ ∪ C_0 ∪ H ∪ C_⁺) is structurally the Rest/Kernel/Core/Satellites layering with a precise dynamical meaning attached.
- [Hidden Structure and Function in the Lexicon](../Picard_2013_HiddenStructureFunctionLexicon/notes.md) — Kernel/Core/Satellite/MinSet distinction; Fiedler's "any cut of Γ into two units lets the preceding unit control the following one" (§8.5) gives a control-theoretic reading of that hierarchy.
- [Loops and Self-Reference in the Construction of Dictionaries](../Levary_2012_LoopsSelfReferenceDictionaries/notes.md) — Levary et al.: definitional cycles are meaningful, not artifacts; Fiedler's cyclicity set C_0 (the union of all vertices on di-cycles) is exactly the "irreducible loopy core" that carries the global-attractor dynamics — a quantitative version of "the loops are where the content is."
- [The Symbol Grounding Problem](../Harnad_1990_SymbolGroundingProblem/notes.md) — Harnad: recursive definability ≠ grounding; Fiedler's only-if part (a non-FVS subset fails to determine for *some* nonlinearity) is the formal echo — fixing the FVS is necessary, and even then the decay/dissipativity assumption (no lexical analogue) is doing real work.
- [Control of complex networks requires both structure and dynamics](../Gates_2016_ControlComplexNetworksRequires/notes.md) — Gates & Rocha (2016): the *contrast* paper. Fiedler et al. prove FVS-control is dynamics-agnostic by theorem (the FVS = informative = determining set for *every* admissible nonlinearity); Gates & Rocha prove the rival structure-only constructions (structural controllability / maximum matching, minimum dominating set) are *not even an approximation* once dynamics enter, getting both the count and the identity of driver variables wrong, governed by canalization / effective connectivity. Same graph object, opposite robustness — this is why the lexical-grounding work transfers via FVS but not via maximum matching.
- [Controllability of complex networks](../Liu_2011_ControllabilityComplexNetworks/notes.md) — Liu–Slotine–Barabási (2011): the *other* "minimal set of nodes that controls a directed network" answer — for linear `ẋ = Ax + Bu` dynamics and full-state controllability, the minimal driver set is the unmatched nodes of a maximum matching (Hopcroft–Karp), not a feedback vertex set. Fiedler et al.'s FVS-control is for arbitrary nonlinear dynamics and attractor steering. The two diverge sharply: on the OEWN definition digraph the maximum-matching driver set is ~74% of words vs ~1.5% for the FVS-determining "grounding seed" — the same biological-network regime where Liu et al. find n_D ≈ 0.8 for gene-regulatory networks. Fiedler's "any cut of Γ lets the preceding unit control the following" (§8.5) is the dynamical layering; Liu et al. supply the matching baseline against which the FVS seed should be reported.

<!-- provenance: notes drafted by paper-reader subagent reading all 42 page images, 2026-05-12; cross-refs reconciled same day; Gates_2016 conceptual link added 2026-05-12 -->
