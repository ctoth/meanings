# Codex Review: Sense-Rebuild Numbers

## Strongest Charge

The sense-level rebuild is a useful prototype, but the synthesis over-sells it as a typed defeasible ingestion result. The strongest charge is not that the reported numbers are fabricated. The charge is that several headline numbers are true only under narrow implementation definitions that the prose then inflates:

- "zero surviving gloss self-loops" means "zero literal emitted edges where `source_node == target_node`," after the builder has already removed the target node from candidate choices and counted 1,496 same-sense references as skipped. It is real as an adjacency fact, but not yet real as a disambiguation finding.
- "4,562 short non-lexical artifacts quarantined/excluded" rests on a hand-written rule pile with no measured precision or recall, no `uncertain` outcomes in the OEWN run, and a default that sends almost every normal WordNet POS to `lexical-word`.
- "IC merge as belief merge" is currently seven hard-coded spelling-pair records over fourteen forms. That is provenance-bearing bookkeeping, not a merge method.
- "121,375 admitted ICs" is not the admitted extension of a defeasible admission theory. It is the output of a simple lexicality-tag filter over IC IDs.
- "Kernel shrank 18,151 -> 12,142" is explicitly not apples-to-apples, and the synthesis mostly says that, but the surrounding success framing still lets the shrinkage read as stronger evidence than it is.

The honest conclusion is narrower: this rebuild demonstrates that a sense-node graph can be built over all OEWN senses, with a much lower literal self-loop count, a smaller exact-small-greedy Kernel on a different node surface, and two export files produced from metadata. It does not yet demonstrate validated lexicality, real WSD, IC belief merge, or an end-to-end admission theory.

## Specific Findings

### 1. The zero-self-loop result is implementation-real but semantically under-validated.

The rebuild report says the sense graph has 212,478 nodes, 418,094 edges, Kernel 12,142, residual cyclic SCCs 0, and acyclic closure yes (`reports/sense-ingestion-rebuild.md:13`-`22`). It also reports 0 surviving sense-level self-loops (`reports/sense-ingestion-rebuild.md:34`) against the 3,413 lemma-level baseline (`reports/sense-ingestion-rebuild.md:26`-`30`). The summary repeats `self_loop_count: 0` and the 3,413 baseline (`reports/oewn-sense-ingestion-summary.json:4`-`15`).

That number is mechanically true for the emitted adjacency: `self_loop_count` is just `sum(1 for node, targets in build.adjacency.items() if node in targets)` (`scripts/sense_ingestion_rebuild.py:42`-`43`). But the builder makes literal self-loops structurally hard to emit. During gloss resolution, same-POS choices are `lemma_pos_index[(candidate, target_pos)] - {target_node}` and global choices are `lemma_index[candidate] - {target_node}` (`src/meanings/wordnet_pipeline.py:377`-`397`). If there is no other candidate and the head sense was a candidate, the builder increments `self_reference_skipped` rather than emitting an edge (`src/meanings/wordnet_pipeline.py:414`-`415`). The run skipped 1,496 such cases (`reports/oewn-sense-ingestion-summary.json:23`-`25`; `reports/sense-ingestion-rebuild.md:61`-`63`).

So "zero surviving self-loops" currently means "no head sense was linked to itself after excluding the head sense from resolution." It does not prove that all same-surface gloss references were correctly resolved to the intended other sense or IC. Nearly half a million ambiguous candidate matches were skipped (`reports/oewn-sense-ingestion-summary.json:18`-`24`), and the resolver's tie-break is only signature overlap, returning `None` on zero overlap or tied top overlap (`src/meanings/wordnet_pipeline.py:75`-`100`). The stronger synthesis wording says same-surface gloss references resolve to the intended sense and dissolve all self-loops (`reports/synthesis.md:54`); the code supports the weaker claim that the emitted sense graph has no literal self-edge under a skip-on-self policy.

Where this is sound: replacing the first-representative `lemma::pos` graph with all sense IDs is real. The builder iterates every word sense with a definition (`src/meanings/wordnet_pipeline.py:319`-`327`) and records source synset, lemma, POS, lexicality, and IC ID (`src/meanings/wordnet_pipeline.py:341`-`355`). The old paper builder really did select only the first glossed synset per `lemma::pos` (`src/meanings/wordnet_pipeline.py:434`-`453`). That is a genuine improvement.

### 2. The lexicality classifier has unknown precision and recall.

I found no precision/recall evaluation in the requested files. The synthesis itself says the new source has no independent audit yet (`reports/synthesis.md:86`) and calls classifier precision an open critic target (`reports/synthesis.md:96`). The only direct tests are a small fixed set: Nobelium, taxon, abbreviation, titlecase noun, multiword phrase, water, and the named short-token cases (`tests/test_lexicality.py:6`-`45`, `tests/test_lexicality.py:48`-`81`).

The classifier is a rule pile. Chemical, taxon, abbreviation, case, idiom, phrase, short-token, technical-domain, POS, then fallback (`src/meanings/lexicality.py:146`-`198`). The most consequential rule is the near-bottom default: if POS is one of `a`, `n`, `r`, `s`, or `v`, return `lexical-word` (`src/meanings/lexicality.py:193`-`195`). Since OEWN senses overwhelmingly use those POS tags, the `uncertain` fallback is practically unreachable in this run. The summary has no `uncertain` count at all (`reports/oewn-sense-ingestion-summary.json:27`-`37`), despite the design saying `uncertain` is for insufficient or conflicting evidence (`notes/sense-ingestion-design.md:96`-`109`) and never admits by default (`notes/sense-ingestion-design.md:182`-`192`).

The hard cases show both strengths and fragility:

- `no::n` as Nobelium is handled only because chemical rules run before the short-token whitelist and look for phrases such as "atomic number", "nobelium", and "sulfur" (`src/meanings/lexicality.py:29`-`39`, `src/meanings/lexicality.py:146`-`148`; tested at `tests/test_lexicality.py:50`-`66`).
- `s::n`, `e::n`, `g::n`, `ph`, and `th` are excluded because they are short and not whitelisted, except single-character tokens are always `symbol-code` (`src/meanings/lexicality.py:178`-`187`; tested at `tests/test_lexicality.py:53`-`70`). That is plausible for the named artifacts, but it is a whitelist policy, not a learned or validated classifier.
- `ax` and `axe` are admitted because they are explicitly whitelisted (`src/meanings/lexicality.py:71`-`100`; tested at `tests/test_lexicality.py:58`-`73`).
- Taxa are only caught by gloss phrases like "genus of", "family of", "species of" (`src/meanings/lexicality.py:41`-`51`, `src/meanings/lexicality.py:150`-`152`). A taxon gloss outside those string templates will fall through to `lexical-word`.
- Chemicals are only caught by a short keyword list or a chemical-formula regex (`src/meanings/lexicality.py:29`-`39`, `src/meanings/lexicality.py:103`-`104`, `src/meanings/lexicality.py:146`-`148`). The test for `water` deliberately classifies "binary compound..." as `lexical-word` (`tests/test_lexicality.py:41`-`45`), which may be right for a human vocabulary, but it shows that the chemical boundary is policy-loaded and not validated.
- Proper names are titlecase nouns (`src/meanings/lexicality.py:166`-`168`), which will miss lowercased proper-name lemmas and can misclassify titlecase common entries if any survive source casing.

The reported 110,088 `lexical-word` senses and 4,562 short non-lexical artifacts (`reports/oewn-sense-ingestion-summary.json:27`-`44`) are therefore counts emitted by these rules, not measured classifier performance. They should be presented as "rule-tagged by the current heuristic classifier," not as validated quarantine/exclusion accuracy.

### 3. The IC merge layer is a hard-coded demo, not a method.

The synthesis admits the whitelist is hand-picked (`reports/synthesis.md:56`), and the source confirms it. `HIGH_CONFIDENCE_SPELLING_VARIANTS` contains exactly seven records: `color/colour`, `center/centre`, `theater/theatre`, `ax/axe`, `gray/grey`, `honor/honour`, and `organize/organise` (`src/meanings/identity_clusters.py:16`-`59`). The rebuild reports exactly 7 ICs over 14 forms (`reports/sense-ingestion-rebuild.md:36`-`39`; `reports/oewn-sense-ingestion-summary.json:49`-`50`).

This is not belief merge in the advertised sense. The data-model facet describes IC merge as a `belief-set`-style merge over sense sets with retained inputs and provenance (`reports/synthesis-facet-datamodel-claude.md:284`-`301`) and even says it is literally `merge_belief_profile` over rival senses (`reports/synthesis-facet-datamodel-claude.md:334`). The implementation only maps normalized forms to preauthored `ic_id`s (`src/meanings/identity_clusters.py:62`-`76`) and then assigns those IC IDs during graph build (`src/meanings/wordnet_pipeline.py:341`-`344`). That preserves aliases, which is good, but it does not discover merges, compare glosses, adjudicate rival senses, or record split/exclusion dialectics.

It also obviously misses broad classes: other US/UK variants, inflectional/orthographic variants not in the seven records, pronunciation variants like `warsh/wash`, historical spellings, multiword construction aliases, and any sense-specific case where one form pair shares one sense but not another. Calling this "IC merge as belief merge" over-dignifies a whitelist unless the synthesis clearly labels it as a seed fixture.

### 4. The Kernel shrinkage claim should not be used as evidence of semantic improvement.

The shrinkage number is real in the report: the sense graph Kernel is 12,142 (`reports/sense-ingestion-rebuild.md:13`-`19`), while the post-self-loop lemma exact-small-greedy Kernel baseline is 18,151 (`reports/sense-ingestion-rebuild.md:24`-`30`; `reports/self-loop-fix-impact.md:7`-`12`). The report also correctly warns that the graph has a different node surface (`reports/sense-ingestion-rebuild.md:67`-`70`). The synthesis repeats that caveat and says the raw size drop is not load-bearing (`reports/synthesis.md:56`).

Still, the synthesis section leads with "Result: ... Kernel 12,142 (vs 18,151)" and then says the self-loop prediction passes (`reports/synthesis.md:54`). The original prediction was specifically a typed-lexical-IC Kernel prediction: project to ICs, drop non-lexical aggregate ICs, then compute the Kernel (`reports/synthesis-facet-datamodel-claude.md:347`-`349`, `reports/synthesis-facet-datamodel-claude.md:363`-`367`). The script does not compute that object. It computes `analyze_kernel` on the raw sense-node graph (`scripts/sense_ingestion_rebuild.py:295`-`297`), then filters seed nodes to `lexical-word` for export (`scripts/sense_ingestion_rebuild.py:46`-`99`). The human vocabulary is separately a whole-graph IC tag projection (`scripts/sense_ingestion_rebuild.py:103`-`158`).

So the honest shrinkage statement is: "Under exact-small-greedy, the raw all-sense graph's Kernel is 12,142, smaller than the post-self-loop lemma::pos Kernel of 18,151, but this compares different node identities and a graph with many skipped ambiguous/self references. The strict typed-lexical-IC Kernel predicted by the data-model facet has not been computed." Anything stronger is over-claim.

Where this is sound: residual cyclic SCCs after the chosen seed are 0 (`reports/oewn-sense-ingestion-summary.json:11`-`16`), and the solver metadata is explicit that the seed is not exact overall: `seed_exact: false`, with 1,355 exact SCCs and 135 greedy SCCs (`reports/oewn-sense-ingestion-summary.json:55`-`65`). That is transparent and should stay.

### 5. The admission-policy theory is not wired end-to-end.

The design says admission is evaluated over typed records with structured rules, priorities, blockers, and decisions such as admit, exclude, quarantine, merge, and split (`notes/sense-ingestion-design.md:130`-`180`). It says the default policy admits `lexical-word`, `phrase`, and `idiom` candidates while excluding or quarantining symbol-code, abbreviation, proper-name, taxon, chemical, and technical-term unless higher-priority rules override them (`notes/sense-ingestion-design.md:182`-`192`). The data-model facet says the human Up-Goer list is the admitted extension of an admission theory, with admission dialectical trees and explicit evidence (`reports/synthesis-facet-datamodel-claude.md:351`-`357`).

The script does not run a defeasible theory. It defines `HUMAN_ADMITTED_TAGS = {"lexical-word", "phrase", "idiom"}` (`scripts/sense_ingestion_rebuild.py:19`-`20`) and then admits any IC with at least one sense whose lexicality tag is in that set (`scripts/sense_ingestion_rebuild.py:109`-`128`). Everything else is counted as an exclusion by tag (`scripts/sense_ingestion_rebuild.py:129`-`155`). The payload policy string honestly says this is "admit ICs with at least one lexical-word, phrase, or idiom sense" (`scripts/sense_ingestion_rebuild.py:149`-`152`).

That means the 121,375 admitted ICs (`reports/sense-ingestion-rebuild.md:38`-`40`; `reports/oewn-sense-ingestion-summary.json:45`-`48`) are not an admitted extension of an admission theory. They are a lexicality filter dressed in the language of admission. The synthesis should not say the human Up-Goer vocabulary is the admitted extension unless and until a real `AdmissionPolicy` or `gunray`/defeasible evaluation is run.

### 6. The sense graph still lacks the advertised attack/ADF layer.

The synthesis says the data model requires attacks between rival senses and an ADF/bipolar structure over sense nodes (`reports/synthesis.md:52`). It even says the sense graph exists "with attack edges" in the research agenda (`reports/synthesis.md:82`). The current builder returns a `SenseLevelGraphBuild` with `nodes`, `adjacency`, labels, POS, node metadata, and resolution stats (`src/meanings/wordnet_pipeline.py:37`-`45`). No attack-edge relation is present. The builder emits only definition dependency edges into `adjacency` (`src/meanings/wordnet_pipeline.py:368`-`417`). The data-model facet warned that rival-sense attacks are the missing piece (`reports/synthesis-facet-datamodel-claude.md:264`-`282`).

This matters for the cooked-number angle because the claimed end-to-end "form -> token -> reading -> sense -> IC -> admission" system depends on rival readings and defeaters. The rebuild implements a metadata-enriched support graph plus filters. That is useful, but it is not the typed defeasible system described in the synthesis.

## What Would Make The Framing Honest

The sense-rebuild section would be honest if it said all of the following explicitly:

1. The zero-self-loop claim is a literal emitted-edge claim under the current resolver. It is not yet a validated WSD result; 1,496 self references were skipped and 499,860 ambiguous candidate matches were skipped.
2. The lexicality numbers are heuristic-rule outputs. Precision and recall are unknown until a labeled stratified audit is run across ordinary lexical words, short tokens, taxa, chemicals, abbreviations, proper names, technical terms, phrases, and `uncertain` candidates.
3. The current IC merge layer is a seven-pair seed whitelist. It preserves aliases and provenance, but it is not a merge algorithm and not a `belief-set` profile merge.
4. The demonstrated Kernel shrinkage is on the raw all-sense graph, not on the typed-lexical-IC graph predicted in the data-model facet. It should be treated as a promising diagnostic, not as proof that the typed model reduced the semantic Kernel.
5. The human Up-Goer export is currently "ICs with at least one lexical-word/phrase/idiom sense." It is not a defeasible admission-theory extension until structured admission rules, priorities, defeaters, and per-IC explanations are actually evaluated.
6. The current sense graph has support edges only. Attack edges between rival senses, ADF acceptance conditions, and per-occurrence readings remain unbuilt.

## Verdict

Defensible-with-edits. The rebuild is not fake: all-sense ingestion, metadata attachment, literal self-loop elimination in the emitted graph, acyclic closure after the chosen seed, and alias-preserving hard-coded IC IDs are real. But the synthesis as written is too generous to the prototype. It presents implementation counters as if they were validated semantic results and borrows the vocabulary of defeasible admission and belief merge before those mechanisms exist.

The section should be revised from "the sense-level ingestion rebuild fixed the artifacts and produced the admitted human Up-Goer vocabulary" to "the first sense-level prototype produced a support graph and tag-filtered exports; it removed literal emitted self-loops under a skip-on-self resolver; the classifier, IC merge method, typed-lexical-IC Kernel, attack layer, and admission theory still need validation or implementation."
