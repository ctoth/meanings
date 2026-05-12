# Abstract

## Original Text (Verbatim)

We present Local Graph-based Dictionary Expansion (LGDE), a method for data-driven discovery of semantic neighbourhoods of words using tools from manifold learning and network science. At the heart of LGDE lies the creation of a word similarity graph from the geometry of word embeddings followed by local community detection based on graph diffusion. The diffusion in the local graph manifold allows the exploration of the complex nonlinear geometry of word embeddings to capture word similarities based on paths of semantic association, over and above direct pairwise similarity. Exploiting such semantic neighborhoods enables the expansion of dictionaries of pre-selected keywords, an important step for tasks in information retrieval, such as database queries and online data collection. We validate LGDE on two user-generated English-language corpora and show that LGDE enriches the list of keywords with improved performance relative to methods based on direct word semantic occurrences. We further demonstrate our method through a real-world use case from communication science, where LGDE is evaluated quantitatively on the expansion of a conspiracy-related dictionary from online data collected and analyzed by domain experts. Our empirical results and expert user assessment indicate that LGDE expands the seed dictionary with more useful keywords due to the manifold-learning-based similarity network.

---

## Our Interpretation

This is one of the strongest practical papers in the collection for “what do we do after we have a seed?” It does not solve kernel minimality, but it gives a concrete graph method for growing a small vocabulary into a richer working lexicon without relying on naive nearest-neighbor similarity.
