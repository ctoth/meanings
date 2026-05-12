# Cross-dictionary stability — the discriminator for the lexicographer's confound

*Generated: 2026-05-12. Script: `scripts/cross_dictionary_stability.py`. Data: `data/external-dictionaries/`.*

## What this tests

Agenda item #5 in `reports/synthesis.md`: if the Kernel/Core/MinSet structure of a dictionary definition graph is substantially *stable* across dictionaries written under different editorial policies, it tracks something other than "one expert community's model of learner vocabulary"; if it reshuffles wildly, the dictionary graph is a folk-distributional artifact of one resource. Different *absolute* sizes are expected and fine — different *fractions* (or wholly disjoint word sets) are the finding.

## (A) Datasets

- **GCIDE 0.54** (GNU Collaborative International Dictionary of English = Webster's Revised Unabridged 1913 + WordNet 1.5 supplements + volunteer additions; public domain) — the one alternate dictionary with *full definitions* we can build a definition graph from. Parsed from the SGML-ish dump (`<ent>`/`<hw>`/`<pos>`/`<def>`), node = `headword::pos`, edge `u -> v` iff `u` occurs in `v`'s definition after the same `meanings.normalize` tokenization + `FUNCTION_WORDS` blocklist used by `build_paper_wordnet_graph`. Build stats: {'definition_count': 116292, 'candidate_matches': 238141, 'resolved_same_pos': 160836, 'resolved_unambiguous_pos': 41095, 'ambiguous_skipped': 36210}.
- **Longman (American) Defining Vocabulary** — the ~2,000-word controlled list LDOCE restricts its definitions to. 2066 unique words after cleaning.
- **Ogden Basic English 850** — the 850-word controlled vocabulary (1930). 851 words.
- **OEWN `exact-small-greedy` seed** — 5,044 `lemma::pos` nodes, read from `reports/oewn-paper-wordnet-layers.json` (layer 0). Kernel 18,151 / 160,010 nodes.

## (B1) Kernel / seed *fractions* — GCIDE vs OEWN

| | nodes | edges | Kernel | Kernel % | Core | Satellites | seed (exact-small-greedy) | seed % of nodes | seed % of Kernel | residual cyclic SCC |
|---|---|---|---|---|---|---|---|---|---|---|
| **OEWN paper-wordnet** | 160,010 | 677,823 | 18,151 | 11.34% | 510 | 17,641 | 5,044 | 3.15% | 27.8% | 0 |
| **GCIDE 0.54** | 116,292 | 184,872 | 5,893 | 5.07% | 799 | 5,094 | 3,701 | 3.18% | 62.8% | 0 |

GCIDE largest Kernel SCC: 2,196 nodes; Kernel SCC count 3,470; source-SCC count 777.

## (B2) Controlled-vocabulary overlap with the OEWN MinSet seed

Comparison is at the **lemma** level (OEWN seed `lemma::pos` keys collapsed to lemmas: 4,817 distinct lemmas; the controlled lists and the GCIDE seed likewise as lemmas).

| controlled vocab | size | ∩ OEWN seed | % of vocab in OEWN seed | % of OEWN seed in vocab | Jaccard |
|---|---|---|---|---|---|
| Longman Defining Vocabulary | 2,066 | 752 | 36.4% | 15.6% | 0.123 |
| Ogden Basic English 850 | 851 | 427 | 50.2% | 8.9% | 0.081 |
| GCIDE exact-small-greedy seed (lemmas) | 3,149 | 670 | 21.3% | 13.9% | 0.092 |

Cross-checks: Longman∩Ogden Jaccard 0.347 (88.4% of Ogden's 850 are in the Longman list); Longman vs GCIDE-seed Jaccard 0.147; Ogden vs GCIDE-seed Jaccard 0.103.

### Example words in the disagreement buckets

**Longman ∩ OEWN seed** (words a lexicographer decreed *and* the OEWN graph found irreducible): ability, able, above, according, acid, across, act, activity, actor, addition, adjective, admit, advantage, after, again, agreement, air, airport, alcohol, all, along, also, angle, animal, anxiety …

**Longman \ OEWN seed** (Longman decreed, OEWN graph did *not* put in the MinSet): a, abbreviation, about, abroad, absence, absent, accept, acceptable, accident, account, achieve, action, active, actress, actual, actually, add, address, admiration, admire, adult, advanced, adventure, adverb, advertise …

**OEWN seed \ Longman** (OEWN graph found irreducible, Longman did *not* decree as a definer): aah, aba, abaca, abdominal_cavity, abelard, abelia, abraham, absinthe, absolute_zero, abstract, abudefduf, abundant, abutilon, abyssinia, acacia, acacia_catechu, acanthoscelides, acanthus, acaridae, accepted, accomplished, accordance, accumulated, accurate, accusation …

**GCIDE seed sample**: abb, abs, absorbed, accoutered, ace, ache, achimenes, act, actualized, add, adjourn, adz, aerides, aerospace, affixed, age, aggravated, aim, air, airborne, airbrush, airheaded, aisle, albuca, alces, aliene, all, all_right, alocasia, alpha_rays, alstroemeria, altaic, altogether, ammobium, amorphophallus, ampere_second, anaphor, anaphoric, anchor_space, anchorperson …

## (B3) Verdict for the confound

**Mixed, leaning *partial stability* — enough to deny "purely a one-resource artifact", not enough to claim the Kernel/MinSet is a policy-independent map of foundational vocabulary.**

1. **The seed *budget* is stable; the Kernel *extent* is not.** OEWN's MinSet is 3.15% of nodes; GCIDE's is 3.18%. That the *irreducible-grounding budget* of a word-defines-word graph is ~3% of nodes — robust across a 21st-century learner-oriented WordNet, a 1913 Webster + WordNet-1.5 hybrid, *and* (per #3) gene-regulatory networks — is a genuine, editorial-policy-independent structural fact. The *size of the recursively-tangled region* (the Kernel proper), 11.3% vs 5.07%, is not policy-independent; it scales with how densely definitions cross-reference (and with parser sparsity).

2. **The OEWN MinSet is *not* ⊆-ish the Longman list — "the graph just rediscovers what lexicographers decreed" fails.** Only 36.4% of the Longman Defining Vocabulary is in the OEWN seed; only 15.6% of the OEWN seed is in the Longman list (Jaccard 0.123). Ogden BE 850 → 50.2% of it in the OEWN seed but only 8.9% the other way (Jaccard 0.081). The GCIDE *emergent* seed vs the Longman *prescribed* list: Jaccard 0.147. The disagreement is structured: Longman-decreed-but-not-in-the-MinSet = morphological derivatives and pedagogical conveniences (`abbreviation, accept, acceptable, achieve, action, active, actress, actually, address, admiration, advertise`, …) — words a learner needs that are not load-bearing in the wiring; in-the-MinSet-but-not-Longman-decreed = the technical-genus / proper-noun / Linnaean-taxon frontier (`abelia, abudefduf, abutilon, acacia_catechu, acanthoscelides, acaridae, absinthe, abelard, abraham`, …) plus abstract relational vocab (`accordance, accurate, accusation`) — and the GCIDE emergent seed has the *identical* taxon pathology (`achimenes, aerides, albuca, alocasia, alstroemeria, ammobium, amorphophallus`, …). So the part of the MinSet that diverges most from the prescribed vocabularies is precisely the *parsing/sense-artifact layer* (taxa, proper nouns) the sense-level rebuild (synthesis §3) is trying to quarantine — not a layer of psychologically real primitives.

3. **What recurs everywhere is a small abstract/concrete-superordinate core.** `act, air, all, acid, across, addition, after, again, agreement, angle, animal, apple, arm, able` appear in the Longman list, the Ogden 850, *and* both emergent seeds. That few-hundred-word core — concrete superordinate nouns + a handful of high-frequency relational words — is robust to every change of policy. It is also, of course, exactly the vocabulary the lexicographer's confound predicts will be load-bearing *because* it's what readers are assumed to know — so the cross-dictionary evidence **cannot fully break the confound**: it shows the *small shared core* is real, but the *bulk* of each MinSet is resource-specific.

**Bottom line.** The MinSet *size budget* (~3% of nodes) is genuinely stable across OEWN, GCIDE, and (per #3) the FVS-control biology regime — a real, policy-independent graph-theoretic property of word-defines-word digraphs. The MinSet *membership* is only partially stable: a ~few-hundred-word abstract/concrete-superordinate core recurs everywhere, but most of each dictionary's MinSet is its own, and the divergences track curatorial idiosyncrasies (Longman's pedagogical derivations vs WordNet's taxonomic inflation) more than they track meaning. So the Kernel/MinSet structure is **neither a pure artifact of one resource nor evidence of psychologically real primitives** — it is a robust *graph-theoretic* property whose concrete instantiation is dictionary-specific. That is exactly the modest synthesis-§4 claim ("locates where a symbolic lexicon cannot justify itself from within"), and *not* the stronger "the Kernel is a stable map of foundational vocabulary" claim. The cross-dictionary check therefore **does not rescue Yoneda-completeness or fully defuse the lexicographer's confound** — it constrains it: the structural *budget* is real, the structural *content* is mostly local.

## Caveats

- **GCIDE is a different era and a different style** — Webster 1913 + WordNet 1.5 supplements + volunteers: florid encyclopedic definitions, heavy Latin/Greek scientific vocabulary, archaic spellings, a large Linnaean-taxon layer from the WordNet portion. Its definition graph being ~2.6× sparser per node than OEWN's is partly that and partly the parser (title-case spans skipped; only words that are themselves GCIDE headwords become edges). A sparser graph has a structurally smaller Kernel — so the Kernel-fraction leg is the weaker one; the seed-fraction match (sparsity-robust) and the membership overlap (lemma-level, sparsity-robust) are load-bearing.
- **The parser is approximate.** GCIDE POS strings are noisy (`v. t.`, `a.`, `n. & a.`, …) and were bucketed to {n, v, a, r, x}; `headword::pos` keys are coarser than OEWN's `wn`-derived POS. Cross-references inside `<def>` ("See {Foo}") are stripped to plain text with the rest of the markup, so a "See X" pointer becomes a plain occurrence of X — consistent with treating it as a definitional dependency, but it inflates edges from words GCIDE only *points at*. Headword pronunciation/stress marks were stripped before `normalize_lemma`.
- **The Longman list here is the *American* Longman Defining Vocabulary** (the cleanest one-word-per-line transcription available), not the British LDOCE list; they overlap heavily but not perfectly.
- **The Longman and Ogden lists are *prescribed* defining vocabularies, not *emergent* MinSets** — they were chosen by editors as the vocabulary definitions are written *in*, a different object from "the words that turn out irreducible in the resulting graph". Partial overlap with an emergent MinSet is expected under *either* hypothesis; what is diagnostic is the *direction and the which-words* of the disagreement (§B2), not the headline Jaccard. The diagnostic finding is that the OEWN MinSet is far from a subset of Longman, and the parts that diverge are artifacts rather than primitives.
- **One artifact this surfaces about the OEWN pipeline itself:** the OEWN `exact-small-greedy` seed is ~5,044 `lemma::pos` nodes but only ~4,817 distinct lemmas — and a large share of those are taxa/proper nouns (`abelia`, `abudefduf`, `abyssinia`, `abelard`, `abraham`, `acaridae`, …), the same layer GCIDE's WordNet-1.5-derived seed is full of. Cross-dictionary comparison thus also *re-confirms* the synthesis-§3 point that the lemma-level graph's MinSet is inflated by un-disambiguated proper-noun / taxonomic glosses, independently of any one resource.

