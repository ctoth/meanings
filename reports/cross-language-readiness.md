# Cross-Language Readiness

**Date:** 2026-05-12

The graph algorithms are resource-neutral: they operate on `set[str]` nodes and `dict[str, set[str]]` adjacency lists.

The OEWN-specific behavior lives in the WordNet adapter layer:

- `build_paper_wordnet_graph()`
- `build_synset_graph()`
- token normalization in `normalize.py`

The shared adapter shape is `LexicalGraphBuild` in [lexical_graph.py](/C:/Users/Q/code/meanings/src/meanings/lexical_graph.py). Future multilingual adapters should produce:

- `nodes`
- `adjacency`
- `labels`
- `pos_by_node`
- `metadata`
- `language`
- `resource_id`

## Next Multilingual Adapter Targets

- Open Multilingual WordNet resources where synset alignment already exists.
- LLM-assisted WordNets built by the Bergh 2025 style pipeline.
- Linked-data lexical resources where senses can be anchored by URI.

## Required Discipline

Do not put language-specific parsing into `graph_analysis.py`. Keep tokenization, lemmatization, POS mapping, sense resolution, and resource IDs inside adapters.

