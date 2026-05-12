# cross-dictionary stability (agenda #5)

## 2026-05-12 — DONE (pending final pytest confirm)

### Data acquired → data/external-dictionaries/
- `longman-defining-vocabulary.txt` — 2066 words, American LDV from healthypackrat/longman-american-defining-vocabulary (GitHub), POS tags stripped. + `_ldv_raw.txt`.
- `ogden-basic-english-850.txt` — 851 words, simple.wikipedia BASIC English alphabetical wordlist via MediaWiki API. + `_ogden_raw.wikitext`.
- `gcide/gcide-0.54.tar.xz` — 14MB, GNU GCIDE 0.54 (Webster 1913 + WordNet 1.5), from ftp.gnu.org. Script extracts+parses on the fly.
- `README.md` written.
- OEWN seed: read from `reports/oewn-paper-wordnet-layers.json` layer 0 (5044 lemma::pos, 4817 distinct lemmas). Did NOT rebuild OEWN.

### Results (scripts/cross_dictionary_stability.py → reports/cross-dictionary-stability.{md,json})
- GCIDE digraph: 116292 headword::pos nodes / 184872 edges (1.6/node, vs OEWN 4.2/node — sparse: Webster prose uses many non-headword words; parser skips titlecase).
- GCIDE Kernel 5893 = **5.07%** of nodes (OEWN 11.34%) — ~2x smaller fraction.
- GCIDE seed (exact-small-greedy) 3701 = **3.18%** of nodes (OEWN 3.15%) — essentially IDENTICAL. residual cyclic SCC = 0.
- Overlap vs OEWN seed (lemma level): Longman LDV 752/2066 (36.4%) in OEWN seed; 15.6% of OEWN seed in LDV; Jaccard 0.123. Ogden 850: 50.2% in OEWN seed, 8.9% reverse, Jaccard 0.081. GCIDE seed: 21.3% in OEWN seed, 13.9% reverse, Jaccard 0.092. Ogden 88.4% subset of LDV. LDV vs GCIDE-seed Jaccard 0.147.
- Disagreement structure: LDV\OEWNseed = morphological derivatives (abbreviation, accept, achieve, actress...). OEWNseed\LDV = taxa/proper nouns (abelia, abudefduf, acaridae, abraham...) + abstract relational (accordance, accurate). GCIDE seed full of same taxon names (achimenes, aerides, albuca...) because GCIDE 0.54 has WordNet 1.5.

### Verdict: PARTIAL stability. Seed *budget* (~3%) is policy-independent (also matches FVS-biology regime). Seed *membership* mostly resource-specific; only a small abstract/concrete-superordinate core (act,air,all,acid,animal...) recurs everywhere. Divergences track curatorial idiosyncrasies + parsing artifacts, not primitives. Does NOT fully break the lexicographer's confound, constrains it.

### pytest: baseline 60 passed (clean). Re-run after changes — was in progress, confirm.
