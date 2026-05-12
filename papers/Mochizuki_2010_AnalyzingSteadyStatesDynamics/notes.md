---
title: "Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks"
authors: "Atsushi Mochizuki, Daisuke Saito"
year: 2010
venue: "Journal of Theoretical Biology"
doi_url: "https://doi.org/10.1016/j.jtbi.2010.06.007"
pages: "266 (2010) 323–335"
affiliations: "RIKEN Advanced Science Institute; Tokyo Institute of Technology; PRESTO, JST"
---

# Analyzing steady states of dynamics of bio-molecules from the structure of regulatory networks

## One-Sentence Summary
Introduces "linkage logic" — a method to determine the *diversity* (count and combinatorial structure) of steady states of an ODE regulatory network using **only the wiring** (which node regulates which), not the signs or strengths of regulation; the key derived object is the set of **informative nodes** (`Infn`), whose activities at a steady state determine the activities of all other nodes for *every* admissible nonlinearity. *(p.323)*

## Problem Addressed
Prior work on structure↔dynamics relations was either restricted to small substructures (network motifs) or to binary-valued steady states. This paper asks: how much of the steady-state behavior of a regulatory network can be inferred from the *graph alone*, with no quantitative dependence and no sign information, for general ODE forms? *(p.324)*

## Key Contributions
- **"Linkage logic"**: a framework with two principles. *(p.324)*
  - **Principle of Compatibility** — upper limit on the dimension of steady-state diversity realizable by a given network = `|Infn|`.
  - **Principle of Dependency** — which combinations of steady states are mutually possible (regulatory linkages constrain the set of steady states).
- **Informative nodes** (`Infn`): a graph-theoretically determined node subset such that observing all node activities of a steady state restricted to `Infn` pins down the entire state. Determined from the in-link argument sets `I(n)` alone — independent of the actual steady state, the nonlinearities, and the signs. *(p.325, Appendix B/C)*
- An **algorithm** (Appendix C) computing `Infn` of minimum size via a "matrix form" reduction over incompatible regions. *(p.332–333)*
- A **network-reduction** procedure: replace the network by one on just the informative nodes (with direct + indirect linkages), preserving the potential to generate the original steady-state diversity (Section 3.3). *(p.327)*
- Worked application to the **ascidian *Ciona* developmental gene regulatory network of Imai et al. (2006)**: reduced from full network to **16 informative nodes**; 10 observed expression patterns implies the network (if correct) must have ≥ 78 *unobserved* steady states (88 = 8 × 11 total predicted). *(p.329)*

## Methodology — the model
ODE regulatory network on a directed graph. Node `n ∈ N` = a species; `u_n(t)` = its abundance/activity. Dynamics:

$$
\frac{du_n}{dt} = f_n(\mathbf{u}) - \delta_n u_n, \quad n \in N
$$
Where: `f_n` ("regulatory function") depends only on the variables specified by the in-links to `n` (its **argument set** `I(n)`); `δ_n u_n` is linear decay (extendable to any increasing `δ_n(u_n)`). `Î(n) = I(n) ∪ {n}` = full set of variables appearing in `f_n - δ_n u_n` (i.e. in-neighbours plus the node itself). The method uses **only the sets `I(n)` / `Î(n)`** — never the form of `f_n`, never signs, never strengths. *(p.324)*

Steady-state condition for node `n`: `f_n(\mathbf{u}) = δ_n u_n`. The theory works for general steady states; "RSP" (regular stationary points, near-binary) is used only for exposition, not relied on. *(p.324)*

## Key definitions / equations

### Extension map (Appendix A)
`X(\mathbf{s}; Fixn)` = the subspace of `|N|`-dim real space where the variables in `Fixn ⊆ N` are fixed at the values they take in point `\mathbf{s}`, the rest free. Dimension `|N| − |Fixn|`. *(p.331, Eq. A.1)*

### Incompatible region of node n at steady state s
`X(\mathbf{s}; I(n)) \ X(\mathbf{s}; Î(n))` — the region where `n`'s in-neighbours sit at their steady-state values but `n` itself does not; node `n`'s steady-state condition cannot hold there. *(p.325)*

### Total incompatible region including steady state s
$$
U^{*}(\mathbf{s}) = \left[ \bigcup_{n \in N} X(\mathbf{s}; I(n)) \setminus X(\mathbf{s}; \hat I(n)) \right] \cup \{\mathbf{s}\}
$$
Where: this is the set of points that are *not* steady states except `\mathbf{s}` itself, deducible from wiring alone. Its shape is mirror-symmetric about `\mathbf{s}` (depends on `\mathbf{s}` only by translation). *(p.326, p.331 Appendix B)*

### Informative nodes (Appendix B, the central definition)
A subset `Infn ⊆ N` is **informative** if it generates a convex subspace inside the total incompatible region:
$$
\text{Infn} \subseteq N \text{ s.t. } X(\mathbf{s}; \text{Infn}) \subseteq U^{*}(\mathbf{s})
$$
Equivalently: `U^*(\mathbf{s})` contains a `(|N| − |Infn|)`-dimensional convex extent fixing exactly the `Infn` coordinates. The nodes in `Infn` are the **informative nodes**. Because `U^*(\mathbf{s})`'s shape doesn't depend on `\mathbf{s}`, `Infn` is determined purely from the `I(n)`'s. There may be several minimum `Infn`'s. *(p.331)*

Consequence (the "wiring determines dynamics" statement): the activities of the informative nodes at a steady state **represent all possible steady states of the whole system** — any two steady states agreeing on `Infn` are equal. *(p.326, p.331)*

### Principle of Compatibility (Section 3)
The number of distinct steady states (sets-of-steady-states diversity) a network can realize is bounded; its **dimension ≤ |Infn|**. With `|Infn|` informative nodes the max steady-state diversity is `2^{|Infn|}` worth of combinations (in the binary picture), and in general the diversity dimension `≤ |Infn|`. *(p.325–326, p.332)*

### Principle of Dependency (Section 4)
For a given set of steady states `S = {\mathbf{s}^1, \mathbf{s}^2, \dots}` of ODE system (1), the following necessary condition must hold:
$$
\bigcap_{n \in N} \bigcup_{\mathbf{s} \in S} X(\mathbf{s}; \hat I(n)) = S
$$
Where: intersection over nodes of the union over observed steady states of the steady-state regions. If the observed `S` violates this, the wiring is inconsistent with that `S` — there must be additional (unobserved) steady states, or the network is wrong. Derived in Appendix D. *(p.328, Eq. 3)*

Corollary form (Appendix D, p.332): if a dynamical system has multiple steady states `{\mathbf{s}^1, \mathbf{s}^2, \dots}` sharing the same `Infn`, then `U^*(\mathbf{s}^a) ⊇ X(\mathbf{s}^a; Infn)` for each; since `X(\mathbf{s}^a; Infn)` has at most one steady state, the steady states are *identified by their values on `Infn`*, and the diversity dimension is `≤ |Infn|`.

## Algorithm — computing minimum-size `Infn` (Appendix C)
Assume observed steady state `\mathbf{0} = (0,…,0)` (WLOG by symmetry). Encode each node's incompatible region as a row vector over symbols `\{0, \bar 0, -\}`: `\bar 0` = "this coordinate ≠ 0" (the focal node), `0` = "= 0" (an in-neighbour at steady value), `-` = unspecified. Stack rows into a matrix `U^*(\mathbf{0})` (≤ `|N|+1` rows incl. a bottom all-`0` row). Reduce by integrating row vectors one-by-one **into the bottom row** using two union rules:

- (C3): `(…, \bar 0, …)` over `(…, 0, …)` with all else identical ⇒ `(…, -, …)` (one site relaxed to unspecified).
- (C4): rows differing at multiple sites ⇒ the `( -,0)` pair → `0`, the `(\bar 0,0)` pair → `-`, others unchanged.

Rules (1)–(2-3) (p.333) fix the order of integration (bottom→top), increasing the number of `-` in the bottom row while never breaking existing `-`'s. The remaining specified (`0`) positions in the final bottom row are the **informative nodes**. The result depends on the chosen node ordering; cycling orderings systematically gives the minimum `|Infn|` (a combinatorial-optimization problem flagged for future work). Worked on the 5-node chain example of Fig. 10 → `Infn = {2, 4}`. *(p.332–333, Eqs. C1–C5)*

## Network reduction (Section 3.3, Appendix E)
Build a reduced network on `Infn` only, with edges = direct **and indirect** regulatory paths among informative nodes. The reduced network retains the potential to generate the original steady-state diversity, but may *over*-estimate it (because in the reduced network the regulatory functions of a node may have more possible forms than in the original — e.g. independence of two inputs is lost). Keeping some *non*-informative intermediary nodes (Fig. 11c) can yield a tighter mimic than the minimal reduction (Fig. 11b). Whether to integrate a non-regulating informative node into the system changes the analysis (Fig. 11b example). *(p.327, p.334)*

## Application: ascidian *Ciona* GRN (Imai et al. 2006)
- Full developmental GRN → reduced to **16 informative nodes** (Fig. 5 highlights them; Fig. 6 = reduced 16-node network). *(p.326–327, p.329)*
- 10 observed tailbud-stage expression patterns (Table 2), assumed to be steady states. Substituting into Eq. (3): LHS yields **88 patterns** ⇒ at least **78 unobserved steady states** must exist if the wiring is correct. *(p.329)*
- Diversity decomposes as `{MyoD} × {Snail} × {Tbx2/3} × {9-gene cluster Dll-B…Otx}` (direct-product structure): three independent on/off switches (8 combos) × 11 patterns from the 9-gene cluster = 88. Four informative genes (Brachyury, Mesp, Tbx6b/c/d, ZicL) are always inactive among observed states. *(p.329, Table 3)*
- Tables 1–4: Table 1 = which sets of steady states a 2-node topology can realize (conditional switch / independent switches / upstream-follower); Tables 3–4 = predicted diversity after adding 7 more direct linkages (Fig. 9). *(p.329–330)*

## Figures of Interest
- **Fig. 1 (p.324):** 3-node example; defines `I(n)`, `Î(n)`.
- **Fig. 2 (p.325):** graphical depiction of a basic compatibility (incompatible region) idea.
- **Fig. 3 (p.325):** schematic of incompatible regions in 2- and 3-node examples.
- **Fig. 4 (p.327):** schematic incompatible regions; reduced network from informative nodes.
- **Fig. 5 (p.327):** full *Ciona* GRN (~18 genes), 16 informative nodes in red.
- **Fig. 6 (p.327):** reduced 18-node *Ciona* network (16 informative + edge color = in/de/static).
- **Figs. 7–8 (p.328):** small example networks for the dependency principle (4-node Fig. 7c; 2-node topologies Fig. 8a/b/c).
- **Fig. 9 (p.330):** suggested 7 extra linkages among the 16 informative *Ciona* genes.
- **Fig. 10 (p.333):** 5-node bidirectional chain `A↔B↔C↔D↔E`; incompatible region schematic → `Infn = {2,4}`.
- **Fig. 11 (p.334):** network reduction; (a) original with informative nodes {A,B,C,D}; (b) minimal reduced; (c) reduced keeping a non-informative node X — better mimic.

## Glossary (Section 5 / p.331 table — terminology summary)
- **Regulatory function** `f_n(\mathbf{u})`: rate of enhancement of node `n`'s activity; depends only on `I(n)`.
- **Argument set** `I(n)`: nodes specified by in-links to `n`.
- **Argument set incl. n** `Î(n) = I(n) ∪ {n}`: variables in the dynamics of `n` (for formula (1)).
- **Extension map** `X(\mathbf{s}; Fixn)`: subspace fixing the `Fixn` coordinates at `\mathbf{s}`'s values.
- **Incompatible region** (of node `n` at `\mathbf{s}`): where `n`'s in-neighbours are at steady values but `n` is not.
- **Total incompatible region incl. steady state `\mathbf{s}`** `U^*(\mathbf{s})`: region with no equilibrium except `\mathbf{s}`, deduced from linkages.
- **Informative nodes** `Infn`: node subset whose steady-state activities determine the whole steady state; `X(\mathbf{s}; Infn) ⊆ U^*(\mathbf{s})`.
- **Principle of Compatibility**: steady-state diversity dimension `≤ |Infn|`.
- **Principle of Dependency**: linkages restrict the achievable set of steady states (Eq. 3).

## Limitations
- `Infn` is **not unique**; the minimum-size computation is a combinatorial problem only partially solved here (systematic reordering). *(p.333)*
- The reduced network on informative nodes can **over-estimate** steady-state diversity vs. the original (loses input-independence structure). *(p.327, p.334)*
- Eq. (3) consistency depends on the chosen "focal range" — including vs. excluding a non-regulating informative node changes the result. *(p.334)*
- Only treats steady states / equilibria; nothing about oscillations or chaos. Uses linear (or monotone) decay assumption. *(p.324)*
- The *Ciona* prediction (78 unobserved steady states) is contingent on the published wiring being correct and on tailbud expression patterns being genuine steady states. *(p.329)*

## Arguments Against Prior Work
- Network-motif studies (Shen-Orr et al. 2002; Mangan & Alon 2003): focus on small substructures, not whole-system dynamics. *(p.324)*
- Organism-specific GRN studies (Reinitz et al.; von Dassow et al. 2000; Albert & Othmer 2003; Mendoza & Alvarez-Buylla 1998): resolve particular networks but say little about the *general* structure↔dynamics relation. *(p.324)*
- Mochizuki (2008) "steady states incompatibility": preliminary, restricted to binary steady states; this paper generalizes to general ODE forms and general steady states. *(p.324–325)*
- Switching-function approaches (Glass & Kauffman 1973; Snoussi & Thomas 1993; Thomas et al. 1995; Mochizuki 2005): use thresholds/RSP/SSP classification; this method needs neither. *(p.324)*

## Design Rationale
- Use *only* the wiring (`I(n)`) — discard signs and quantitative dependence — so conclusions hold for *all* admissible nonlinearities; trade precision for universality. *(p.324)*
- "Informative nodes" because their state alone is informative enough to reconstruct any steady state — a minimal observation/monitoring set. *(p.326, p.331)*
- Network reduction onto informative nodes (incl. indirect edges) preserves diversity-generating potential while shrinking the model. *(p.327)*

## Testable Properties
- Any two steady states of (1) that agree on all informative nodes are identical. *(p.331)*
- Steady-state diversity dimension `≤ |Infn|`. *(p.326, p.332)*
- `Infn` depends only on the digraph (in-link sets), not on `f_n`, not on signs, not on the steady states. *(p.331)*
- If observed steady-state set `S` violates `⋂_n ⋃_{s∈S} X(s; Î(n)) = S`, the system has additional steady states or the wiring is wrong. *(p.328)*
- For the 5-node chain `A↔B↔C↔D↔E`: informative set `= {B, D}` (2 nodes). *(p.333)*
- *Ciona* GRN (Imai 2006 wiring) ⇒ ≥ 78 unobserved steady states; total 88 = 8 × 11. *(p.329)*

## Relevance to Project (definition digraphs / lexical grounding)
A definition digraph (word → words used in its definition) is exactly a "regulatory network" in this paper's sense if dictionary meanings are modelled as fixed points of a propagation/activation dynamics over the wiring. Then the **informative nodes are the lexical grounding set**: the minimal subset of words whose meanings, once fixed, determine the meanings of all other words *for any admissible semantic update rule* — depending only on which words appear in which definitions, not on the content of the definitions. The "Principle of Compatibility" bounds how many distinct coherent meaning-assignments a dictionary's wiring can support (`≤ |Infn|` dimensions); the "Principle of Dependency" (Eq. 3) gives a consistency check on a candidate set of meaning-assignments against the wiring. Network reduction onto informative nodes ≈ collapsing the dictionary to its grounding kernel plus indirect definitional paths. This is the **steady-state precursor** of the later feedback-vertex-set (FVS) characterization: Fiedler–Mochizuki 2013 ("Dynamics and Control at Feedback Vertex Sets I", in this collection) prove that under a uniform-decay condition the *graph-theoretic FVS* coincides with these *informative* nodes (their Corollary 2.4) and with Foias–Temam *determining* nodes, and recover this paper's steady-state uniqueness as their Corollary 4.1; Mochizuki et al. 2013 ("…II", in this collection) gives the biological "faithful monitor" applications. So: FVS of the definition digraph ⊇ a valid grounding set, computable purely from the wiring.

## Open Questions
- [ ] Better (combinatorial-optimization) algorithm for minimum `|Infn|` — flagged for "next study". *(p.333)*
- [ ] How to choose which non-informative nodes to retain for a faithful reduced network (Fig. 11c). *(p.334)*
- [ ] Extending linkage logic beyond steady states (oscillations) — addressed by the later Part I/II papers, not here.

## Related Work Worth Reading
- **Imai, Levine, Satoh, Satou (2006)**, "Regulatory blueprint for a chordate embryo", *Science* 312:1183–1187 — the *Ciona* GRN analyzed here.
- **Mochizuki, A. (2008)**, "Structure of regulatory networks and diversity of gene expression patterns", *J. Theor. Biol.* 250:307–321 — the binary-steady-state precursor this paper generalizes.
- **Mochizuki, A. (2005)**, "An analytical study of the number of steady states in gene regulatory networks", *J. Theor. Biol.* 236:291–310.
- **Snoussi & Thomas (1993)**; **Thomas, Thieffry, Kaufman (1995)** — feedback-loop-characteristic-state / RSP–SSP framework.
- **Shen-Orr, Milo, Mangan, Alon (2002)**; **Mangan & Alon (2003)** — network motifs.
- (Forward) **Fiedler, Mochizuki, Kurosawa, Saito (2013)** "Dynamics and Control at Feedback Vertex Sets. I" (in collection) and **Mochizuki, Fiedler, Kurosawa, Saito (2013)** "… II" (in collection) — the FVS / dynamic generalization.

---
*Provenance: notes generated by research-papers:paper-reader on 2026-05-12 from `paper.pdf` (13 pp.), DOI 10.1016/j.jtbi.2010.06.007, sourced via sci-hub.ru. All page numbers refer to the printed J. Theor. Biol. pagination 323–335.*
