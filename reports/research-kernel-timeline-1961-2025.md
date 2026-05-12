# Research: kernel-timeline-1961-2025

## Summary
The core dictionary-kernel line in the current collection runs from Harnad (1990) through Blondin-Masse et al. (2008), Picard et al. (2013), and Vincent-Lamarre et al. (2014). Looking earlier and later changes the framing in useful ways. The earlier work is less about kernels and more about semantic organization, interlingua, thesauri, and resolving multiple meaning through structured lexical relations. The later work is less about proving graph-theoretic properties from first principles and more about building, expanding, linking, and multilingualizing lexical-semantic graphs at scale. The right lesson is: keep the kernel program, but embed it in a larger historical arc of semantic classification, lexical resource construction, multilingual linkage, and synthetic lexicography.

## Timeline

### 1961: Masterman as prehistory
**Source:** https://aclanthology.org/1961.earlymt-1.24/
**Why it matters:** Margaret Masterman's "Semantic message detection for machine translation, using an interlingua" is an early attempt to make meaning operational in machine processing. It is not a dictionary-kernel paper, but it is part of the same ancestry: lexical meaning is not just a bag of words but something that needs structured semantic mediation.
**Project relevance:** Outside-the-box ancestor for your idea. If your project eventually grows from dictionary graphs into language-independent semantic scaffolds, Masterman is one of the roots.

### 1962: Kay on computation in semantics
**Source:** https://aclanthology.org/www.mt-archive.info/50/IFIP-1962-Kay.pdf
**Why it matters:** Kay explicitly frames semantics as a computational problem and argues that vocabulary and grammar cannot be treated as a trivial appendix to syntax.
**Project relevance:** Useful conceptual ancestor if we want to justify a semantics-first engineering program instead of treating lexical meaning as an afterthought.

### 1965: Sparck Jones on semantic classification
**Source:** https://aclanthology.org/www.mt-archive.info/MT-1965-Sparck-Jones.pdf
**Why it matters:** Karen Sparck Jones argues that a thesaurus or semantic classification is needed to resolve multiple meaning in machine translation, and proposes defining word uses by semantic relations to other words, then grouping synonymous uses into classes. This is not yet dictionary-graph kernel theory, but it is very close in spirit: meaning as structured relational position in a lexical network.
**Project relevance:** This is the best clean 1965 node for your timeline. It is an ancestor of graph-based lexical organization and disambiguation, and it shows that "semantic structure in the lexicon" was already computationally alive by 1965.

### 2008: Blondin-Masse et al.
**Source:** current local collection plus https://aclanthology.org/W08-2003/
**Why it matters:** This is where the kernel project becomes exact. Grounding sets are feedback vertex sets; the grounding kernel is defined by recursive stripping.
**Project relevance:** First implementation-grade formalization of your project.

### 2013: Picard et al.
**Source:** current local collection plus https://arxiv.org/abs/1308.2428
**Why it matters:** Distinguishes Kernel, Core, Satellites, and Minimal Grounding Sets, and starts attaching psycholinguistic function to those parts.
**Project relevance:** Tells us not to collapse everything into one "core vocabulary."

### 2014: Vincent-Lamarre et al.
**Source:** current local collection plus https://arxiv.org/abs/1411.0129
**Why it matters:** Mature large-scale version with multiple dictionaries and definitional-distance hierarchies.
**Project relevance:** Current best direct methods paper in the corpus.

### 2025: LGDE
**Source:** https://aclanthology.org/2025.cl-4.5/
**Why it matters:** "LGDE: Local Graph-based Dictionary Expansion" is not about definitional kernels, but it is very relevant to what happens after you have a seed. It builds a local graph from embeddings and expands a dictionary by diffusion/community structure rather than by direct similarity only.
**Project relevance:** If your kernel becomes a practical lexical-engineering tool, LGDE is a plausible modern way to expand from a hand-curated seed into a broader semantic neighborhood without losing graph structure.

### 2025: OpenGloss
**Source:** https://arxiv.org/abs/2511.18622
**Why it matters:** OpenGloss is a synthetic English dictionary and semantic knowledge graph with 537K senses, 150K lexemes, and 9.1M semantic edges, generated through a multi-agent pipeline. It is not a proof-oriented paper, but it is a major practical signal that lexical-semantic resources can now be generated and iterated much faster than classical manual lexicography allowed.
**Project relevance:** Extremely relevant if we decide to build our own experimental dictionary resource rather than relying only on WordNet/LDOCE-style incumbents. Also important as a warning: generated lexical graphs are now easy enough that "what graph do we trust?" becomes part of the research problem.

### 2025: Automatic bilingual WordNet construction
**Source:** https://aclanthology.org/2025.gwc-1.24/
**Why it matters:** "Leveraging LLMs for Constructing WordNets Automatically as Bilingual Resources" is directly relevant to your cross-language isomorphism dream. The paper itself is about automatic WordNet construction, but the deeper point is that multilingual lexical-graph induction is becoming operational.
**Project relevance:** Strong candidate for the "later" end if we want multilingual kernel comparison rather than only English.

### 2025: Linked Linguistic Knowledge Graph for diachrony
**Source:** https://aclanthology.org/2025.gwc-1.23.pdf
**Why it matters:** This paper links an etymological network with a linguistic knowledge graph for diachronic analysis, using OntoLex/LEMON-style modeling and graph linkage over lexical resources.
**Project relevance:** This is the most interesting outside-the-box late paper for your project after OpenGloss. If we ever want to compare kernels across time, not just across languages, this is the right direction.

## What Changed in the Timeline
The older papers suggest that the kernel project is part of a much older agenda:

1. Build semantic classifications or interlinguas so words can be disambiguated and grouped.
2. Formalize definitional dependence and cycles.
3. Extract minimal or sufficient lexical backbones.
4. Link those backbones to psycholinguistic, multilingual, and diachronic structure.

The newer papers suggest that the frontier has shifted:

1. Build lexical-semantic graphs faster.
2. Expand them automatically from seeds.
3. Link them across languages and timescales.
4. Use LLMs as resource constructors, not just consumers.

## Recommended Next Reading
If the goal is to deepen the exact kernel project:
- Sparck Jones (1965)
- Leavy et al. (2012), "Loops and self-reference in the construction of dictionaries"
- Fomin et al. (2008), minimum feedback vertex set algorithms

If the goal is to widen toward multilingual and resource construction:
- Bergh et al. (2025), automatic bilingual WordNets
- Ghizzotta et al. (2025), linked linguistic knowledge graph for diachrony
- OpenGloss (2025)

If the goal is to connect seed kernels to usable dictionary growth:
- LGDE (2025)

## Recommendation
Do not think of the project only as "find the smallest English seed." Think of it as three nested projects:

1. Extract the exact English definitional backbone.
2. Compare backbones across languages and perhaps across time.
3. Learn how to grow or synthesize lexical graphs from those backbones.

That view makes the 1965 and 2025 endpoints line up much better than they first appear to.

## References
- Masterman, Margaret. 1961. "Semantic message detection for machine translation, using an interlingua." https://aclanthology.org/1961.earlymt-1.24/
- Kay, M. 1962. "Rules of interpretation - an approach to the problem of computation in the semantics of natural language." https://aclanthology.org/www.mt-archive.info/50/IFIP-1962-Kay.pdf
- Sparck Jones, Karen. 1965. "Experiments in semantic classification." https://aclanthology.org/www.mt-archive.info/MT-1965-Sparck-Jones.pdf
- Blondin-Masse, A. et al. 2008. "How Is Meaning Grounded in Dictionary Definitions?" https://aclanthology.org/W08-2003/
- Picard, O. et al. 2013. "Hidden Structure and Function in the Lexicon." https://arxiv.org/abs/1308.2428
- Vincent-Lamarre, P. et al. 2014. "The Latent Structure of Dictionaries." https://arxiv.org/abs/1411.0129
- Schindler, J. et al. 2025. "LGDE: Local Graph-based Dictionary Expansion." https://aclanthology.org/2025.cl-4.5/
- Bergh, J. et al. 2025. "Leveraging LLMs for Constructing WordNets Automatically as Bilingual Resources." https://aclanthology.org/2025.gwc-1.24/
- Ghizzotta, E. et al. 2025. "Enhancing Linguistic Resources for Diachronic Analysis via Linked Data." https://aclanthology.org/2025.gwc-1.23.pdf
- Bommarito, M. J. 2025. "OpenGloss: A Synthetic Encyclopedic Dictionary and Semantic Knowledge Graph." https://arxiv.org/abs/2511.18622
