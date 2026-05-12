---
title: "LGDE: Local Graph-based Dictionary Expansion"
authors: "Juni Schindler; Sneha Jha; Xixuan Zhang; Kilian Buehling; Annett Heft; Mauricio Barahona"
year: 2025
venue: "Computational Linguistics"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  timestamp: "2026-04-03T02:33:16Z"
---
# LGDE: Local Graph-based Dictionary Expansion

## One-Sentence Summary
This paper proposes `LGDE`, a graph-based method for expanding a seed dictionary by building a local semantic similarity graph over domain-specific word embeddings and extracting overlapping local semantic communities via diffusion-based community detection, outperforming thresholding, `kNN`, IKEA, and TextRank on hate-speech, 20 Newsgroups, and conspiracy-content tasks. *(p.1-24)*

## Problem Addressed
The paper asks how to expand a small, expert-provided keyword dictionary into a more useful domain-specific dictionary without drifting into irrelevant nearest neighbors or depending on global semantic geometry that misses local manifold structure. *(p.1-4)*

## Key Contributions
- Introduces `LGDE`, combining a geometric cKNN graph with `severability`-based local community detection to recover semantically coherent neighborhoods around seed keywords. *(p.1-8)*
- Formalizes dictionary expansion as extending seed dictionary `W_0` into `W*` so that the new dictionary is more representative of topic-relevant documents. *(p.2)*
- Uses domain-specific static word embeddings retrofitted from base GloVe vectors rather than contextual embeddings, arguing that static word-level vectors better support polysemous overlapping communities in this setting. *(p.8-9)*
- Shows consistent macro-F1 gains over thresholding, `kNN`, IKEA, and TextRank on benchmark hate-speech and 20 Newsgroups datasets. *(p.10-15)*
- Shows higher median likelihood-ratio scores for words found only by `LGDE`, indicating that `LGDE` tends to discover more discriminative keywords than the baselines. *(p.14-15)*
- Demonstrates a real-world application to conspiracy-related 4chan content, where local graph structure recovers relevant neologisms, phrases, and code words missed by direct similarity methods. *(p.17-23)*

## Methodology
The method begins with a domain-specific vocabulary `V` and word embeddings `u_v`. A sparse undirected weighted semantic similarity graph is built by first computing normalized cosine distances, then constructing an unweighted cKNN backbone `B^(k)_δ` that preserves local geometry, and finally weighting edges by normalized similarity. For each seed keyword `w ∈ W_0`, the method applies `severability`, a random-walk / graph-diffusion local community detector, to find a semantic community `C^(k,t)(w)` maximizing a retention-plus-mixing quality function at time scale `t`. The expanded dictionary is the union of these local communities. Hyperparameters include graph sparsity `k` and diffusion time `t`; embedding dimension `r` is also tuned in experiments. *(p.5-9)*

## Key Equations / Statistical Models

$$
S_{\cos}(u,v)=\frac{\langle u,v\rangle}{\|u\|_2\|v\|_2}
$$
Where: direct cosine similarity between word embeddings `u` and `v`, used as the baseline notion of lexical similarity. *(p.3)*

$$
W(\varepsilon)=\bigcup_{w\in W_0}\{v\in V\mid S_{\cos}(w,v)\ge \varepsilon\}
$$
Where: `ε`-threshold dictionary expansion baseline. *(p.3)*

$$
W(k)=\bigcup_{w\in W_0}\{v\in V\mid v\in N_k(w)\}
$$
Where: `kNN` expansion baseline using the `k` nearest words to each seed. *(p.3)*

$$
\tau := \|1-S_{\cos}\|_{\max},\qquad S := 1-\tau
$$
Where: `τ` is the matrix of normalized cosine distances and `S` the normalized similarity matrix used to weight the graph. *(p.5)*

$$
B^{(k)}_\delta(u,v)=
\begin{cases}
1 & \text{if }\tau(u,v)<\delta \sqrt{\tau(u,u_k)\tau(v,v_k)}\\
0 & \text{otherwise}
\end{cases}
$$
Where: `u_k,v_k` are the `k`-th nearest neighbors of `u,v`; cKNN constructs a sparse local-geometry-preserving backbone graph. *(p.5-6)*

$$
A^{(k)} := S \odot B^{(k)}
$$
Where: the final weighted adjacency matrix is the Hadamard product of similarity and the cKNN backbone. *(p.6)*

$$
P_{ij}=\frac{A^{(k)}_{ij}}{\sum_{\ell\in V}A^{(k)}_{i\ell}}
$$
Where: random-walk transition probabilities on the semantic graph. *(p.6)*

$$
\sigma(C,t)=\frac{\rho(C,t)+\mu(C,t)}{2}
$$
Where: `σ(C,t)` is severability quality for community `C` at time `t`, combining retention `ρ` and mixing `μ`. *(p.6-7)*

$$
W(k,t)=\bigcup_{w\in W_0} C^{(k,t)}(w)
$$
Where: the final `LGDE` expanded dictionary is the union of local semantic communities around seed words. *(p.7)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Embedding dimensions tested | r | dimensions | 50 | 50-300 | 9-15 | `r ∈ {50,100,300}` in experiments. |
| cKNN neighborhood size | k | neighbors | varies | 3-13 | 10-18, 24 | Tuned per dataset and embedding dimension. |
| Diffusion time | t | steps | varies | 2-8 | 10-18, 24 | Tuned per dataset and embedding dimension. |
| Hate-speech seed size | \|W₀\| | keywords | 7 | — | 10 | Chosen from most frequent hate-speech words. |
| Hate-speech vocab size | N | words | 7,093 | — | 10 | After filtering low-frequency terms. |
| 20 Newsgroups seed size | \|W₀\| | keywords | 16 | — | 14 | Positive-class group names. |
| 20 Newsgroups vocab size | N | words | 10,751 | — | 14 | After filtering low-frequency terms. |
| 4chan initial seed size | \|W₀\| | keywords | 215 | — | 18 | Built from RPC-Lex and literature. |
| 4chan corpus size | d | documents | 102,058 | — | 18 | English posts from sampled weeks 2011-2021. |
| LGDE asymptotic cost | — | operations | `O(N^2k + nb\log_2 t)` | — | 7 | For a single run. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| Hate-speech seed F1 | macro F1 | 0.856 | — | — | benchmark test set | 11-12 |
| Hate-speech best LGDE F1 (`r=300`) | macro F1 | 0.875 | — | — | benchmark test set | 12 |
| Hate-speech best thresholding F1 (`r=300`) | macro F1 | 0.846 | — | — | benchmark test set | 12 |
| 20 Newsgroups seed F1 | macro F1 | 0.621 | — | — | benchmark test set | 15 |
| 20 Newsgroups best LGDE F1 (`r=300`) | macro F1 | 0.694 | — | — | benchmark test set | 15 |
| 20 Newsgroups best thresholding F1 (`r=300`) | macro F1 | 0.618 | — | — | benchmark test set | 15 |
| 4chan seed precision / recall / F1 | scores | 0.769 / 0.559 / 0.529 | — | — | expert-coded test set | 20 |
| 4chan LGDE precision / recall / F1 | scores | 0.700 / 0.821 / 0.829 | — | — | expert-coded test set | 20 |
| Words discovered by LGDE judged relevant on 4chan | proportion | 30.2% | — | `p < 0.01` | blind expert assessment | 20-21 |
| Words discovered by thresholding judged relevant on 4chan | proportion | 18.9% | — | — | blind expert assessment | 20-21 |

## Methods & Implementation Details
- The method is explicitly local: it avoids using the full embedding geometry directly and instead works in seed-centered local graph neighborhoods. *(p.1-4, p.22-23)*
- cKNN is preferred over plain `kNN` because it preserves local manifold geometry under sampling inhomogeneity rather than connecting every point to its raw nearest neighbors. *(p.5-6)*
- `Severability` is preferred over local modularity, SIWO, and local random-walk modularity because it uses weighted edges, is deterministic, and naturally accommodates local communities of varying size. *(p.15-17)*
- Domain-specific embeddings are produced by retrofitting GloVe with the Mittens objective, with `μ=0.1` chosen to balance staying close to base embeddings and adapting to the new corpus. *(p.8-9, p.10, p.18)*
- Static embeddings are deliberately used instead of contextual ones because the task needs word-level units and overlapping communities around potentially polysemous words. *(p.8-9)*
- Higher-dimensional embeddings (`r=300`) usually improve performance, especially for `LGDE`, because richer semantic information gives the local graph more structure to exploit. *(p.10-16, p.22)*

## Figures of Interest
- **Figure 1 (p.4):** Why thresholding fails and why local semantic communities help.
- **Figure 2 / Table 2 (p.11-12):** Hate-speech benchmark performance.
- **Figure 3 / Table 5 (p.14-15):** 20 Newsgroups benchmark performance.
- **Figure 4 (p.16):** Correlation between seed keyword quality and community performance.
- **Figure 5 (p.18-19):** 4chan semantic graph neighborhoods and a concrete example (`helter-skelter` → `entire-population`).
- **Table 8 / Table 9 (p.20-21):** 4chan precision/recall/F1 and discovered terms.
- **Table 10 (p.21):** Comparative method overview.

## Results Summary
Across all controlled evaluations, `LGDE` beats the direct-similarity baselines. On hate-speech and 20 Newsgroups, the improvement is moderate but consistent, with the best scores reached at `r=300`. On the 4chan conspiracy dataset the gain is more striking: the seed dictionary has the best precision, but `LGDE` markedly increases recall and therefore overall `F1`, while also surfacing more expert-judged relevant terms than thresholding. The qualitative argument is strong too: `LGDE` can recover terms linked by chains of association in the local graph even when direct cosine similarity is too weak to pass thresholding. *(p.10-23)*

## Limitations
- Evaluation is only on English-language corpora, though the method itself is not language-bound in principle. *(p.23)*
- Manual expert validation is expensive, so the real-world assessment datasets are relatively small. *(p.17-18, p.23)*
- Results depend on seed quality; poor seed keywords produce weaker or less specific communities. *(p.15-16)*
- The work does not solve word-sense disambiguation directly, though the authors speculate that overlapping communities may encode polysemy. *(p.22-23)*
- It is a method for domain dictionary expansion, not for extracting minimal noncircular kernels from definitional graphs. *(p.1-4, p.21-23)*

## Relevance to Project
This paper is highly relevant for the pragmatic side of the project. If we have a small seed and want to grow a usable dictionary outward, `LGDE` is one of the clearest modern methods in the collection. It does not solve the graph-theoretic non-circularity problem, but it gives a concrete way to expand a bootstrap lexicon using local graph structure rather than naive neighbors. That makes it a strong candidate for the “grow the up-goer-five seed outward” stage after a kernel has been chosen. *(p.1-4, p.21-23)*

## Open Questions
- [ ] Can `LGDE` be run not on distributional word graphs but on definitional dependency graphs or hybrid lexical graphs?
- [ ] What happens if the seed is a `MinSet` or `Kernel` rather than an expert-curated topical dictionary?
- [ ] Can overlapping local communities around kernel words be compared across languages as a softer form of structural alignment?

## Related Work Worth Reading
- Yu et al. (2020), `severability` local community detection. *(p.6-7, p.26)*
- Berry and Sauer (2019), cKNN graph construction. *(p.5-6, p.26)*
- Dingwall and Potts (2018), Mittens domain adaptation for embeddings. *(p.8-9, p.26)*
- Garibshah et al. (2022), IKEA iterative query expansion baseline. *(p.3-4, p.26)*

## Collection Cross-References

### Already in Collection
- [[Bergh_2025_LeveragingLLMsConstructingWordNets]] — another 2025 paper about building lexical resources, but on bilingual WordNet induction rather than seed expansion.
- [[Ghizzota_2025_EnhancingLinguisticResourcesDiachronic]] — relevant graph infrastructure for tracking lexical structures over time.
- [[Steyvers-Tenenbaum_2005_Large-ScaleStructureSemanticNetworks]] — provides the broader semantic-network frame within which local graph expansion methods sit.

### New Leads (Not Yet in Collection)
- Yu et al. (2020) — `severability` theory and algorithms.
- Berry and Sauer (2019) — cKNN graph construction.
- Dingwall and Potts (2018) — Mittens domain-adapted embeddings.
- Garibshah et al. (2022) — IKEA keyword expansion.

### Supersedes or Recontextualizes
- None in the current collection.

### Conceptual Links (not citation-based)
- [[Vincent-Lamarre_2014_LatentStructureDictionaries]] — if a minimal kernel gives the bootstrap seed, `LGDE` is one plausible outward-growth mechanism.
- [[Bommarito_2025_OpenGlossSyntheticEncyclopedicDictionary]] — both are 2025-era pragmatic lexical-resource papers, but `LGDE` is a growth method whereas `OpenGloss` is a synthetic resource-generation pipeline.
