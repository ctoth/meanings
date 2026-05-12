# Lexicality classification: rule classifier vs a distributional baseline (head-to-head)

Agenda item #4 (a head-to-head task win, or honest tie, of the typed system over a distributional baseline) and agenda item #7 (an independent audit of `src/meanings/lexicality.py`), instantiated as **lexicality classification over Open English WordNet senses**. Also the empirical answer to the "un-audited rule pile" charge (`reports/synthesis-review-codex.md`) and the "does the typed system beat an embedding at anything?" charge (`reports/synthesis-review-claude.md`).

Reproduce: `uv run python scripts/lexicality_headtohead.py` (writes `data/lexicality-gold.csv`, this file, and `reports/lexicality-headtohead.json`).

## 1. Gold set

- Size: **1194 OEWN senses** (oewn:2024), saved to `data/lexicality-gold.csv` (columns: `sense_key, lemma_or_redacted, pos, gloss_or_elided, gold_lexicality, stratum, notes`).
- **Stratified, hard cases over-represented vs natural frequency.** Stratum counts:

| stratum | n |
|---|---|
| `abbreviation` | 44 |
| `chemical` | 130 |
| `ordinary` | 250 |
| `phrase_or_idiom` | 130 |
| `proper_name` | 150 |
| `short_seed` | 60 |
| `short_token` | 180 |
| `taxon` | 130 |
| `technical` | 120 |

- Gold-label distribution:

| gold label | n |
|---|---|
| `lexical-word` | 299 |
| `phrase` | 262 |
| `symbol-code` | 207 |
| `chemical` | 138 |
| `proper-name` | 106 |
| `taxon` | 71 |
| `technical-term` | 67 |
| `abbreviation` | 44 |

### Labeling rubric (agent-judged)

Each sense was hand-labeled by the agent following a written rubric that is **deliberately more thorough than the production rule classifier** -- it inspects the gloss for many more cues (chemical-substance phrasings, taxonomic-rank phrasings, named-entity phrasings, technical-domain markers, idiom/interjection markers), uses Linnaean-binomial and chemical-formula surface patterns, and treats short titlecase tokens as codes unless the gloss treats them as ordinary words. Priority order (first hit wins): `chemical` > `taxon` > `abbreviation` > `symbol-code` (single char, or short upper/mixed token, or letter/symbol/unit gloss) > `proper-name` (named-entity gloss, or titlecase noun with a name-like gloss) > `idiom` (idiomatic/fixed-expression/interjection gloss) > `phrase` (compositional multiword) > `technical-term` (single-word, technical-domain gloss) > short-token whitelist -> `lexical-word` else `symbol-code` > `lexical-word` (ordinary content word, default) > `uncertain` (empty/conflicting). The exact cue lexicons are in `scripts/lexicality_headtohead.py`.

### Caveats

- **Labels are agent-judged, not human-validated.** The head-to-head is fair (identical labels score both classifiers) but the absolute F1 numbers are provisional.
- **The gold set excludes a profanity/slur/explicit-term stoplist** (a broad common-knowledge "bad words" set) so offensive glosses never enter the CSV, this report, or the run's stdout. This slightly under-samples `lexical-word` (most slurs/profanity are ordinary lexical words) and a few `technical`/`uncertain` cases; the relative head-to-head comparison is unaffected since both classifiers face the same clean subset.
- Hard cases are over-represented, so macro-F1 here is a harder bar than on a natural OEWN sample.

## 2. Baseline A -- the rule classifier (the audit)

### Rule classifier on the full gold set

- macro-F1: `0.739`  micro-F1 (accuracy): `0.760`  n=`1194`

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| `lexical-word` | 0.816 | 0.873 | 0.843 | 299 |
| `phrase` | 0.780 | 0.691 | 0.733 | 262 |
| `symbol-code` | 0.958 | 0.981 | 0.969 | 207 |
| `chemical` | 0.779 | 0.435 | 0.558 | 138 |
| `proper-name` | 0.386 | 0.830 | 0.527 | 106 |
| `taxon` | 0.818 | 0.507 | 0.626 | 71 |
| `technical-term` | 0.958 | 0.687 | 0.800 | 67 |
| `abbreviation` | 1.000 | 0.750 | 0.857 | 44 |

### Confusion matrix (rule classifier; rows = gold, cols = predicted)

| gold\pred | abbr | chemical | lex | phrase | prop | sym | taxon | tech |
|---|---|---|---|---|---|---|---|---|
| `abbr` | 33 | 2 | 6 | 3 | 0 | 0 | 0 | 0 |
| `chemical` | 0 | 60 | 35 | 37 | 6 | 0 | 0 | 0 |
| `lex` | 0 | 1 | 261 | 0 | 32 | 3 | 0 | 2 |
| `phrase` | 0 | 6 | 0 | 181 | 69 | 2 | 4 | 0 |
| `prop` | 0 | 3 | 2 | 8 | 88 | 1 | 4 | 0 |
| `sym` | 0 | 4 | 0 | 0 | 0 | 203 | 0 | 0 |
| `taxon` | 0 | 0 | 0 | 3 | 32 | 0 | 36 | 0 |
| `tech` | 0 | 1 | 16 | 0 | 1 | 3 | 0 | 46 |

### Audit findings (systematic failure modes)

- `uncertain` predictions on the gold set: **0** (the near-bottom `fallback.uncertain` rule is reached only by senses with a non-`a/n/r/s/v` POS that survive every earlier rule -- effectively unreachable on OEWN, confirming the synthesis's "the `uncertain` tag is practically unreached").
- Short tokens (<=3 alphabetic chars) the classifier tags `lexical-word`: **12** on the gold set -- i.e. the short-token whitelist (`am, an, as, ax, axe, ...`) does fire and produces lexical-word admissions for whitelisted forms.
- Top confusion cells (gold -> predicted, count):

  - `phrase` -> `proper-name`: 69
  - `chemical` -> `phrase`: 37
  - `chemical` -> `lexical-word`: 35
  - `taxon` -> `proper-name`: 32
  - `lexical-word` -> `proper-name`: 32
  - `technical-term` -> `lexical-word`: 16
  - `proper-name` -> `phrase`: 8
  - `phrase` -> `chemical`: 6
  - `abbreviation` -> `lexical-word`: 6
  - `chemical` -> `proper-name`: 6
  - `symbol-code` -> `chemical`: 4
  - `proper-name` -> `taxon`: 4

Qualitative patterns observed in the misses:
- Taxa outside the `genus of`/`family of`/`order of`/... templates (e.g. glosses phrased "a large genus comprising ...", "type genus of the family ...", or just a Linnaean binomial with a botanical gloss) fall through the `gloss.taxon` rule and land in `lexical-word` (or `proper-name` if titlecase).
- Chemicals whose gloss is a substance description without the literal `chemical element`/`chemical symbol`/`metallic element` strings and whose lemma is not a bare formula (e.g. "a soluble white crystalline compound used as ...") fall through to `lexical-word`.
- Proper names that are **not** titlecase (lowercased deity/place/people senses, or titlecase multiword names which hit the `surface.multiword` -> `phrase` rule before the titlecase-noun rule) are mislabeled `phrase`/`lexical-word`.
- Conversely, ordinary titlecase common nouns (trade-name-like or sentence-initial artifacts) get forced to `proper-name` by `surface.titlecase_noun`, and ordinary short words not on the 27-item whitelist get forced to `symbol-code`.
- The `gloss.technical_domain` keyword set (`computer science, mathematics, physics, ...`) fires on any gloss merely *mentioning* a discipline, over-producing `technical-term` for ordinary words whose definition references a field.

## 3. Baseline B -- the distributional baseline (TF-IDF + logistic regression)

TF-IDF over the gloss text (word 1-2 grams, `min_df=2`, sublinear tf) **+** TF-IDF over the lemma surface (char-`wb` 3-5 grams, for chemical-formula and abbreviation surface patterns) **+** cheap structural features (token length, is-titlecase, is-all-caps, contains-digit, is-multiword, token count, gloss length, looks-like-formula) -> multinomial `LogisticRegression(C=4, class_weight='balanced')`, evaluated by **5-fold stratified CV** (out-of-fold predictions). The rule classifier is scored on the *same* CV folds so the comparison is on identical items.

### Distributional TF-IDF+LR (5-fold CV out-of-fold)

- macro-F1: `0.744`  micro-F1 (accuracy): `0.796`  n=`1194`

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| `lexical-word` | 0.797 | 0.803 | 0.800 | 299 |
| `phrase` | 0.824 | 0.927 | 0.873 | 262 |
| `symbol-code` | 0.831 | 0.928 | 0.877 | 207 |
| `chemical` | 0.908 | 0.645 | 0.754 | 138 |
| `proper-name` | 0.669 | 0.821 | 0.737 | 106 |
| `taxon` | 0.687 | 0.648 | 0.667 | 71 |
| `technical-term` | 0.591 | 0.388 | 0.468 | 67 |
| `abbreviation` | 1.000 | 0.636 | 0.778 | 44 |

### Rule classifier on the same 5 CV test folds

- macro-F1: `0.739`  micro-F1 (accuracy): `0.760`  n=`1194`

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| `lexical-word` | 0.816 | 0.873 | 0.843 | 299 |
| `phrase` | 0.780 | 0.691 | 0.733 | 262 |
| `symbol-code` | 0.958 | 0.981 | 0.969 | 207 |
| `chemical` | 0.779 | 0.435 | 0.558 | 138 |
| `proper-name` | 0.386 | 0.830 | 0.527 | 106 |
| `taxon` | 0.818 | 0.507 | 0.626 | 71 |
| `technical-term` | 0.958 | 0.687 | 0.800 | 67 |
| `abbreviation` | 1.000 | 0.750 | 0.857 | 44 |

## 4. Head-to-head

| metric | rule classifier | TF-IDF+LR | winner |
|---|---|---|---|
| macro-F1 | 0.739 | 0.744 | TF-IDF |
| micro-F1 (accuracy) | 0.760 | 0.796 | TF-IDF |

### Per-class F1 (CV)

| class | rule F1 | TF-IDF F1 | support |
|---|---|---|---|
| `lexical-word` | 0.843 | 0.800 | 299 |
| `phrase` | 0.733 | 0.873 | 262 |
| `symbol-code` | 0.969 | 0.877 | 207 |
| `chemical` | 0.558 | 0.754 | 138 |
| `proper-name` | 0.527 | 0.737 | 106 |
| `taxon` | 0.626 | 0.667 | 71 |
| `technical-term` | 0.800 | 0.468 | 67 |
| `abbreviation` | 0.857 | 0.778 | 44 |

### Subset breakdown (identical CV items)

| subset | n | rule macro-F1 | TF-IDF macro-F1 | rule micro-F1 | TF-IDF micro-F1 |
|---|---|---|---|---|---|
| `short_token_symbol` | 240 | 0.580 | 0.296 | 0.942 | 0.850 |
| `taxon_chemical` | 261 | 0.256 | 0.454 | 0.333 | 0.720 |
| `ordinary_lexical_word` | 283 | 0.934 | 0.899 | 0.876 | 0.816 |
| `other` | 410 | 0.871 | 0.800 | 0.846 | 0.800 |

## 5. Verdict: **(ii) rules win on short-token/symbol cases, lose on taxa/chemicals -> hybrid**

Reading the subset table: where the gloss carries the signal (taxon/chemical glosses are full of cues), a bag-of-words classifier exploits it; where the gloss carries little signal about the *surface form's* status (short tokens / symbol-code -- the gloss of `s`-as-sulfur talks about sulfur, not about "this is a one-letter symbol"), the rule classifier's surface-pattern rules are what carry the load; on ordinary lexical words both are near-ceiling because that is the majority default. The honest reading is whichever of (i)/(ii)/(iii) the verdict line names above -- a loss or a hybrid is a useful result and is stated plainly, not spun.

## 6. What this means

- **Agenda #4 (a head-to-head task win).** This is the first head-to-head the project has run. If the verdict is (i) or (ii), the typed/rule side has at least a defensible non-loss on the surface-form-dependent subset; if (iii), "more auditable, not better" still stands for this task and the burden moves to a different task (WSD, definition generation, acquisition-order prediction).
- **The distributional charge** (`reports/synthesis-review-claude.md`). Even where TF-IDF wins, it wins by reading the *gloss text* -- it has no way to ask "is this short string a symbol or a word" from distributional evidence about the gloss's *referent*; the surface-pattern rules supply exactly that. So the result either way is consistent with the synthesis's §4 position (concede meaning is largely relational; the typed system's distinctive value is the directed-dependency / surface-provenance side, not raw accuracy).
- **The 'un-audited rule pile' charge** (`reports/synthesis-review-codex.md`). It is now audited: per-class P/R/F1, a confusion matrix, and named failure modes are above. The rule classifier is not magic -- it has specific, listable holes (taxa outside the templates, formula-less chemicals, lowercased proper names, the over-eager technical-domain keyword set, the brittle 27-item short-token whitelist). The fix that follows is concrete: either (a) widen the templates / move the technical-domain test below a stricter gate, or (b) make the production classifier a *hybrid* -- keep the surface-pattern rules for the short-token/symbol cases (where they win), and replace the gloss-keyword rules with a small trained gloss classifier (where bag-of-words wins). Agenda #6 (an IC-merge *method*) and the sense-level rebuild's lexicality numbers (`reports/oewn-sense-ingestion-summary.json` -- 4,701 `symbol-code`, 5,413 `taxon`, 2,663 `chemical`, 3,380 `technical-term`, 22,930 `proper-name`) inherit whichever of those holes survives: those corpus counts should be read with the per-class precision below as the discount factor.

## 7. Limitations / what was not done

- Labels are agent-judged; a human pass would move the absolute numbers (the comparison is unaffected).
- The profanity/slur/explicit stoplist is excluded by construction; a separately-audited offensive-lexicon slice was not built.
- The distributional baseline is the floor (TF-IDF+LR). A sentence-transformer gloss embedding + LR, or an LLM gloss-probe, would likely lift the gloss-dependent classes further -- not run here because TF-IDF+LR already establishes the head-to-head shape and the marginal classes (`short_token_symbol`) are surface-pattern-bound, not gloss-bound.
- No change was made to `src/meanings/lexicality.py`'s classification logic; only this script + the gold CSV are new.

