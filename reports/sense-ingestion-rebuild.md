# Sense Ingestion Rebuild

## Workflow Used

- Built the new `build_sense_level_paper_wordnet_graph` surface over OEWN sense nodes.
- Classified each sense at ingestion time with lexicality tags.
- Merged high-confidence spelling variants into IC ids while keeping all forms.
- Ran `analyze_kernel` with `exact-small-greedy` on the sense-level graph.
- Exported a strict lexical seed surface and a human Up-Goer IC vocabulary surface.

## Kernel Numbers

- Sense nodes: `212478`
- Edges: `418094`
- Kernel: `12142`
- Core: `1939`
- Satellites: `10203`
- Seed: `1582`
- Kernel SCCs: `7466`
- Source SCCs: `1793`
- Residual cyclic SCCs after seed: `0`
- Acyclic definitional closure: `yes`

## Lemma-Level Baseline

- Lemma-level exact-small-greedy Kernel: `18151`
- Lemma-level exact-small-greedy Core: `510`
- Lemma-level exact-small-greedy Satellites: `17641`
- Lemma-level exact-small-greedy Seed: `5044`
- Lemma-level gloss self-loops: `3413`

## Artifact Results

- Surviving sense-level self-loops: `0`
- Self-loop shrinkage vs lemma-level: `yes`
- Short non-lexical artifacts quarantined/excluded: `4562`
- Spelling-variant IC merges: `7` ICs over `14` forms
- Strict lexical seed ICs exported: `834`
- Human vocabulary admitted ICs exported: `121375`
- Excluded-only ICs: `30240`

## Lexicality Counts

- `abbreviation`: `46`
- `chemical`: `2663`
- `idiom`: `37`
- `lexical-word`: `110088`
- `phrase`: `63220`
- `proper-name`: `22930`
- `symbol-code`: `4701`
- `taxon`: `5413`
- `technical-term`: `3380`

## Resolution Stats

- `candidate_matches`: `925283`
- `resolved_same_pos_unique`: `221897`
- `resolved_global_unique`: `94444`
- `resolved_same_pos_overlap`: `86471`
- `resolved_global_overlap`: `21115`
- `ambiguous_skipped`: `499860`
- `self_reference_skipped`: `1496`
- `unresolved_skipped`: `0`

## Prediction Check

- Kernel shrank vs lemma-level artifact-inflated Kernel: `yes`
- Gloss self-loops shrank vs `3,413`: `yes`

The self-loop prediction passed if the target is self-loop dissolution. The Kernel-size prediction is measured separately because this graph has a different node surface: every OEWN sense node is retained instead of collapsing to one `lemma::pos` node.
