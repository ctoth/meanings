# Research: english-bootstrap-seed

## Summary
You can build an English dictionary from a recursive seed, but only if you are explicit about what kind of "from" you mean. If you mean purely lexical recursion with no grounding outside words, then a complete dictionary cannot start from one word, and probably cannot honestly start from any tiny set without importing hidden assumptions. If you mean a non-circular defining system with a small grounded base, then yes: there is strong prior art. The most principled strict base is the Natural Semantic Metalanguage (NSM) semantic primes, around 60-65 universal meaning atoms. The most practical next layer is about 300 semantic molecules, as in Minimal English and Learn These Words First. The most practical industrial lexicographic layer is the 2000-word Longman Defining Vocabulary. So the real answer is not "one word" but "layered seed": primes -> molecules -> defining vocabulary -> full lexicon.

## Approaches Found

### Symbol-grounded seed
**Source:** https://arxiv.org/abs/cs/9906002
**Description:** A dictionary cannot get all meaning from other words alone; some base meanings must be grounded in perception, action, or shared human experience.
**Pros:** Philosophically honest; explains why purely circular definition systems fail.
**Cons:** Hard to formalize if you want a text-only artifact.
**Complexity:** Medium

### Semantic-prime seed
**Source:** https://www.nsm-approach.net/wp-content/uploads/2022/05/Chart-of-NSM-Semantic-Primes_English_v20_May-2022.pdf
**Description:** Start from NSM semantic primes such as `I`, `YOU`, `SOMEONE`, `SOMETHING`, `DO`, `HAPPEN`, `KNOW`, `SAY`, `GOOD`, `BAD`, `PLACE`, `TIME`, `MOVE`, `BECAUSE`, `IF`, `MAYBE`.
**Pros:** Best claim to irreducibility; designed specifically for reductive paraphrase.
**Cons:** Definitions become long and stylistically strange; some ordinary English words must wait a long time before they can be introduced.
**Complexity:** Medium

### Multi-layer non-circular dictionary
**Source:** https://learnthesewordsfirst.com/tools/tools-for-checking-nsm-min-english.pdf
**Description:** Use primes first, then introduce a few hundred semantic molecules in dependency order, then define a larger controlled vocabulary, then define the rest.
**Pros:** This is the closest direct precedent for your idea; practical and tested.
**Cons:** Still needs editorial judgment; "minimal" is partly optimized for usability, not only formal purity.
**Complexity:** Medium

### Defining-vocabulary dictionary
**Source:** https://learnthesewordsfirst.com/tools/tools-for-checking-nsm-min-english.pdf
**Description:** Longman defines a large dictionary using a controlled vocabulary of about 2000 words.
**Pros:** Practical, scalable, familiar lexicographic workflow.
**Cons:** The 2000-word layer still contains circularity unless you further reduce it.
**Complexity:** Low

### Tiny auxiliary-language seed
**Source:** https://kids.britannica.com/students/article/Basic-English/317080
**Description:** Ogden's Basic English used 850 words as a simplified English.
**Pros:** Demonstrates that surprisingly small English subsets can be useful.
**Cons:** Not primarily a non-circular semantic bootstrap; more a controlled language than a grounded definitional system.
**Complexity:** Low

### Graph-theoretic minimal set
**Source:** https://arxiv.org/abs/1411.0129
**Description:** Analyze a dictionary as a directed graph of definitions. Extract a Kernel, Core, Satellites, and a minimum feedback vertex set (MinSet).
**Pros:** Gives a rigorous sense in which a small subset can generate the rest.
**Cons:** The resulting minimal set is not automatically a good human seed; graph minimality is not the same as conceptual naturalness.
**Complexity:** High

## Key Papers
- [Harnad (1990/1999 arXiv)](https://arxiv.org/abs/cs/9906002) - Classical statement of the symbol-grounding problem; explains why a monolingual dictionary alone cannot fully generate meaning.
- [Vincent-Lamarre et al. (2014/2016)](https://arxiv.org/abs/1411.0129) - Shows latent dictionary structure: Kernel about 10% of dictionary, MinSet about 1%.
- [Bullock (2019 tools paper)](https://learnthesewordsfirst.com/tools/tools-for-checking-nsm-min-english.pdf) - Describes NSM-LDOCE and Learn These Words First; gives the concrete layered recipe.

## Existing Implementations
- **Learn These Words First** (https://learnthesewordsfirst.com): Multi-layer learner's dictionary built from NSM primes, about 300 molecules, then the 2000-word Longman Defining Vocabulary.
- **CheckMinimalEnglish / CheckEnglishNsm** (https://learnthesewordsfirst.com/tools/): Tools for testing whether a definition stays inside the allowed bootstrap vocabulary.

## Complexity vs Quality Tradeoffs
The smallest philosophically serious seed is the NSM prime set. But a prime-only dictionary is not pleasant to read and not sufficient for practical dictionary writing unless you add molecules quickly. The best practical compromise is a 2-layer or 3-layer design:

1. Around 60-65 primes for the irreducible base.
2. Around 150-300 molecules for concrete human universals such as `hand`, `water`, `mother`, `fire`, `walk`, `food`, `sleep`, `day`.
3. Around 1000-2000 defining words for fluent dictionary prose.

Graph-theoretic minimization can shrink the seed further, but the mathematically smallest seed is unlikely to be the best editorial seed. It may contain weird, abstract, or low-teachability words.

## Recommendations
For this project, do not aim for a one-word seed. Treat that as a philosophical probe, not an engineering target.

Instead, choose one of these goals:

### Goal A: strictest honest seed
Use NSM semantic primes as layer 0, and commit to reductive paraphrase. This is the best answer if you want the deepest "truth" of the project.

### Goal B: best practical bootstrap seed
Use a layered seed:
- Layer 0: NSM primes
- Layer 1: 200-300 semantic molecules
- Layer 2: 1000-2000 defining vocabulary
- Layer 3: full dictionary

### Goal C: strongest formal minimality claim
Take an existing English defining vocabulary, build a dependency graph, and compute a non-circular ordering plus candidate MinSets. Then manually replace graph-artifact words with better editorial seed words where necessary.

## Estimated Implementation Effort
- **Minimal approach:** Curate a prime set plus 100-200 molecules and define 500-1000 words. This gives a convincing prototype.
- **Full approach:** Build a full layered dictionary with validation tooling, cycle checks, dependency ordering, and editorial conventions for paraphrase.

## Open Questions
- [ ] Should the seed optimize for philosophical irreducibility, human learnability, or shortest possible size?
- [ ] How much non-textual grounding is allowed: images, examples, embodied scripts, usage scenes?
- [ ] Should polysemy be split aggressively into senses before recursion analysis?
- [ ] Do function words like `and`, `or`, `make`, `have` belong in the seed, or should they be paraphrased away where possible?

## References
- Harnad, Stevan. "The Symbol Grounding Problem." arXiv:cs/9906002. https://arxiv.org/abs/cs/9906002
- Vincent-Lamarre, Philippe, et al. "The Latent Structure of Dictionaries." arXiv:1411.0129. https://arxiv.org/abs/1411.0129
- Bullock, David. "Tools for checking NSM and Minimal English." 2019. https://learnthesewordsfirst.com/tools/tools-for-checking-nsm-min-english.pdf
- Goddard, Cliff. "Chart of NSM Semantic Primes [v20, 10 May 2022]." https://www.nsm-approach.net/wp-content/uploads/2022/05/Chart-of-NSM-Semantic-Primes_English_v20_May-2022.pdf
- "Universal communication: could just 65 words hold the key?" Australian Academy of the Humanities. https://humanities.org.au/power-of-the-humanities/universal-communication-could-just-sixty-five-words-hold-the-key/
- "Basic English." Britannica Kids. https://kids.britannica.com/students/article/Basic-English/317080
