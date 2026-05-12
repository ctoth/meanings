---
title: "On the minimum feedback vertex set problem: Exact and enumeration algorithms"
authors: "Fedor V. Fomin; Serge Gaspers; Artem V. Pyatkin; Igor Razgon"
year: 2008
venue: "Algorithmica"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T01:59:43Z"
---
# On the minimum feedback vertex set problem: Exact and enumeration algorithms

## One-Sentence Summary
This paper gives an exact exponential-time algorithm for minimum feedback vertex set in undirected graphs, proves an upper bound on the number of minimal feedback vertex sets, and supplies the algorithmic middle layer that turns dictionary `MinSet` work from a graph-theoretic reduction into something computationally actionable. *(p.1, p.7-14)*

## Problem Addressed
The paper asks how to compute a minimum feedback vertex set exactly in an undirected graph, and how many minimal feedback vertex sets an `n`-vertex graph can contain in the worst case. *(p.1-2)*

## Key Contributions
- Gives a time `O(1.7548^n)` exact algorithm for minimum feedback vertex set on undirected graphs. *(p.1, p.7-10)*
- Recasts the problem through the complementary `maximum induced forest` objective and then generalizes that objective to include an already-fixed acyclic subset `F`. *(p.3-7)*
- Uses branch-and-reduce plus measure-and-conquer analysis rather than naive direct branching on feedback vertices. *(p.5-10)*
- Proves that every `n`-vertex graph has at most `1.8638^n` minimal feedback vertex sets and that this is not wildly loose by exhibiting an infinite family with `105^{n/10} ≈ 1.5926^n` maximal induced forests / minimal feedback vertex sets. *(p.1, p.10-14)*
- Shows that all minimal feedback vertex sets can therefore be enumerated in `O(1.8638^n)` time. *(p.2, p.10)*

## Methodology
The authors work on the complement of feedback vertex set: if `X` is a maximum induced forest of `G`, then `V \ X` is a minimum feedback vertex set. They define a generalized problem `mif(G,F)` where `F` is an acyclic subset that must be included in the forest, preprocess disconnected and non-independent cases, and then branch on local neighborhood structure around an active vertex. Correctness is proved through structural propositions about maximal induced forests under contractions, while the runtime and enumeration bounds are established by measure-and-conquer recurrences with carefully chosen weights `α = 0.955` for the exact algorithm and `α = 0.5491` for the enumeration bound. *(p.3-13)*

## Key Equations / Statistical Models

$$
\tau(G) = |V| - \operatorname{mif}(G,\varnothing)
$$
Where: `\tau(G)` is the size of a minimum feedback vertex set of graph `G`; `mif(G,\varnothing)` is the size of a maximum induced forest. This is the central complement relation the whole algorithm exploits. *(p.3, p.5)*

$$
\operatorname{mif}(G,F) = \max \{ |X| : F \subseteq X \subseteq V,\; G[X] \text{ is acyclic} \}
$$
Where: `F` is an acyclic subset that must be contained in the induced forest. The generalized problem is easier to recurse on than the raw feedback-vertex formulation. *(p.3, p.5-7)*

$$
\mu = |V \setminus F| + \alpha \, |V \setminus (F \cup N(t))|
$$
Where: `t` is the active vertex in the branching analysis, `N(t)` is its neighborhood, and `α = 0.955` in the exact-algorithm analysis. The weighted measure is chosen to make the branch recurrences close under `1.7548^n`. *(p.8-10)*

$$
P(k) \leq \alpha^\mu \;\Rightarrow\; T(n) = O(1.7548^n)
$$
Where: the branching-count function is bounded by the weighted measure, yielding the final exact running time. *(p.8-10)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Exact-algorithm running-time base | — | exponential base | 1.7548 | — | 1, 7-10 | Theorem 6. |
| Enumeration upper-bound base | — | exponential base | 1.8638 | — | 1, 10-13 | Theorem 7 upper bound on minimal FVS count. |
| Lower-bound family base | — | exponential base | 1.5926 | — | 1, 13-14 | Infinite family achieving `105^{n/10}` minimal FVSs. |
| Measure weight for exact algorithm | α | weight | 0.955 | — | 8 | Used in the `μ` measure for Section 3. |
| Measure weight for enumeration proof | α | weight | 0.5491 | — | 10 | Used in the `μ(G,F,t)` measure for Section 4. |
| Branching exponent in measure analysis | a | weight | 1.333628 | — | 8-10 | Chosen so `f(μ) ≤ a^μ` closes the recurrences. |
| Lower-bound gadget size | — | vertices | 10 | — | 13-14 | Figure 1 gadget used for the `105^{n/10}` lower bound. |
| Maximal induced forests in gadget | — | count | 105 | — | 13-14 | Count for the 10-vertex gadget in Figure 1. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| Minimum FVS exact runtime | exponential time | `O(1.7548^n)` | — | — | Undirected graphs on `n` vertices | 1, 7-10 |
| Number of minimal FVSs upper bound | exponential count | `1.8638^n` | — | — | Any `n`-vertex undirected graph | 1, 10-13 |
| Number of minimal FVSs lower-bound family | exponential count | `105^{n/10} ≈ 1.5926^n` | — | — | Infinite family of constructed graphs | 1, 13-14 |

## Methods & Implementation Details
- The search procedure never branches directly on arbitrary cycle vertices; it branches on structural cases in the induced-forest formulation. *(p.5-10)*
- A contraction operator `Id(T,t)` collapses a nontrivial tree component `T` through a designated vertex `t`, preserving the relevant maximal-induced-forest structure. *(p.3-4)*
- Proposition 2 is the key local branching lemma: when a vertex outside `F` is adjacent to exactly one vertex of `F`, any maximal induced forest must satisfy a small list of neighborhood patterns. *(p.4-5)*
- Preprocessing splits disconnected graphs, repairs non-independent `F`, and handles low-degree boundary cases before the main branching rules fire. *(p.6-7)*
- The exact algorithm’s tightest case is the degree-3 neighborhood pattern in Main 9; the authors explicitly remark that improving this case would improve the overall upper bound. *(p.10, p.13)*
- The enumeration result follows the same style of reasoning but shifts the target from optimum value to counting maximal induced forests compatible with `F`. *(p.10-13)*

## Figures of Interest
- **Figure 1 (p.14):** Ten-vertex gadget used to prove the `1.5926^n` lower bound.

## Results Summary
The paper’s main technical result is that minimum feedback vertex set in undirected graphs can be solved faster than the previous `1.8899^n` barrier by not solving FVS directly. The right complementary object is the maximum induced forest, and once the problem is generalized to `mif(G,F)`, the local structure around active vertices becomes branchable with favorable weighted recurrences. The companion counting result matters just as much for this project: there may be exponentially many minimal cycle-breaking sets, so “the kernel seed” is not a unique object even when exact optimization is feasible. *(p.1-2, p.5-14)*

## Limitations
- The paper is for **undirected** feedback vertex set, while dictionary definitions induce a **directed** graph; it is therefore a methodological bridge, not a drop-in solver for dictionary `MinSets`. *(p.1-2, p.15-17)*
- The constants are valuable for exact-algorithm history, but for large lexical graphs the practical relevance is mainly conceptual unless the graph is decomposed aggressively first. *(p.1-2, p.10-14)*
- The paper does not discuss weighted, semantically constrained, or psycholinguistically informed objectives, which are exactly what a serious dictionary-kernel project will eventually want. *(p.1-17)*

## Relevance to Project
This paper is not about language, but it is still highly useful. `Massé`, `Picard`, and `Vincent-Lamarre` reduce grounding sets / `MinSets` to feedback vertex sets; this paper shows what the exact-algorithm side of that reduction looks like when taken seriously. The most important conceptual takeaway is not the specific base `1.7548`, because our graph is directed; it is that the space of minimal cycle-breaking sets is large, structured, and enumerable in principle rather than being a single privileged kernel. *(p.1-2, p.10-14)*

## Open Questions
- [ ] What is the best directed-FVS / directed-MinSet algorithmic path for real dictionary graphs after SCC condensation?
- [ ] Can weighted semantic objectives be layered on top of enumeration so we choose “good” seeds rather than merely minimum-cardinality ones?
- [ ] Is there a practical hybrid strategy where exact search is used only inside small SCCs and heuristic/ILP methods handle the larger lexical core?

## Related Work Worth Reading
- Festa et al. (1999), survey of feedback vertex set methods. *(p.1, p.15-17)*
- Lin and Jou (2000), contraction-based methods for **directed** feedback vertex set. *(p.15)*
- Lapointe et al. (2012), enumerating minimum feedback vertex sets in directed graphs; natural next step for multiple kernel seeds. *(conceptual follow-up from collection context)*
- Karp (1972), NP-completeness background. *(p.1, p.17)*

## Collection Cross-References

### Already in Collection
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — cites this as an algorithmic reference for exact or enumerated `MinSet` computation in dictionary graphs.

### New Leads (Not Yet in Collection)
- Lapointe et al. (2012) — "Enumerating minimum feedback vertex sets in directed graphs" — directly relevant if we want many candidate English seeds rather than just one.
- Festa et al. (1999) — survey of feedback vertex set methods; useful for algorithm design space.
- Lin and Jou (2000) — directed-FVS algorithmics, closer to the dictionary setting than this undirected paper.

### Supersedes or Recontextualizes
- None in the current collection.

### Conceptual Links (not citation-based)
- [[Massé_2008_MeaningGroundedDictionaryDefinitions]] — explains why dictionary grounding sets reduce to feedback vertex sets in the first place.
- [[Picard_2013_HiddenStructureFunctionLexicon]] — motivates why multiple minimal seeds matter conceptually rather than only computationally.
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — gives the large-dictionary empirical setting where exact or approximate MinSet computation becomes the practical bottleneck.

### Cited By (in Collection)
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — cites this for the exact/enumeration algorithmic basis of `MinSet`/FVS computation.
