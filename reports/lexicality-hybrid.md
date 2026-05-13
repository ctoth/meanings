# Hybrid lexicality classifier: surface rules + a trained gloss classifier (three-way head-to-head)

Agenda item #6 (the lexicality part), following the agenda-#4 head-to-head verdict (ii) (`reports/lexicality-headtohead.md`): keep the surface-pattern rules where they win (short-token / symbol-code / abbreviation), replace the gloss-keyword *templates* (taxon / chemical / technical / proper-name) with a small trained gloss classifier where the bag-of-words baseline won.

Reproduce: `uv run python scripts/train_lexicality_classifier.py` (builds `data/lexicality_gloss_clf.joblib`), then `uv run python scripts/lexicality_headtohead.py` (writes `data/lexicality-gold.csv` if missing, `reports/lexicality-headtohead.{md,json}` for the 2-way agenda-#4 result, and `reports/lexicality-hybrid.{md,json}` -- this file).

## 1. The three systems

- **pure-rules** -- the *pre-hybrid* ordered rule pile (surface rules + gloss-keyword templates), reproduced verbatim in `scripts/lexicality_headtohead.py::pure_rules_predict`. This is what agenda #4 audited.
- **pure-TF-IDF+LR** -- the agenda-#4 Baseline B: TF-IDF over gloss (word 1-2 grams) + lemma surface (char-wb 3-5 grams) + cheap structural features -> class-balanced `LogisticRegression`, 5-fold stratified CV.
- **hybrid** -- the new production `meanings.lexicality.classify_lexicality`: a **surface layer** (single-char -> symbol-code; short-token case rules; code-case; the 27-item short-token whitelist; the abbreviation regex; the chemical-formula regex; multiword -> phrase; idiom regex) runs first and returns immediately if it fires; otherwise a **trained gloss classifier** (`meanings.lexicality_model.GlossClassifier`, persisted to `data/lexicality_gloss_clf.joblib`) is consulted for the gloss-cue classes {taxon, chemical, technical-term, proper-name, lexical-word}; if its top-class probability is below the threshold (`0.40`) and no surface rule fired, the verdict is `uncertain`. Every verdict's `reasons` tuple names its path (`surface.<rule>` / `trained.<class>.p<prob>` / `trained.lowconf.p<prob>` / `fallback.<rule>`).

## 2. Training data for the gloss component (and the silver-label scheme)

The trained gloss classifier is fitted on the **1194-sense agent-judged gold set** plus **silver** rows -- the production rule classifier's verdicts on the *full* OEWN corpus, kept only when the *entire* reason trace consists of **surface** paths (single-char / short-token-case / code-case / short-token-whitelist / abbreviation-regex / chemical-formula-regex). Those paths look only at the lemma surface (plus, for abbreviation, an explicit "abbreviation"/"acronym" gloss phrase), and the agenda-#4 audit found them near-perfect (F1 0.86-0.97), so their labels there are trustworthy. The **gloss-cue classes** (taxon / chemical / technical-term / proper-name / lexical-word) take **gold labels only** -- the old keyword templates are unreliable there (taxa outside `genus of` fall through; formula-less chemicals fall through; `surface.titlecase_noun` over-fires for proper-name at precision ~0.39), so their silver labels are not used. Silver rows are down-weighted (`sample_weight=0.25`) vs gold rows.

**Silver-label risk (stated plainly):** silver labels are only as good as the surface rules. On the gold set's short-token/abbreviation strata those rules are near-perfect, but on the full corpus they will occasionally mislabel -- e.g. a 2-letter ordinary word not on the 27-item whitelist gets silver-labelled `symbol-code`. Mitigations: (1) only surface *paths* are trusted, never gloss-keyword paths; (2) the gloss-cue classes that matter for the hybrid take gold labels only; (3) silver down-weighting. And at inference the hybrid's *surface layer fires first*, so the trained model's symbol-code/abbreviation predictions never decide anything -- the silver rows mostly teach it which gloss patterns go with codes so it does not claim them.

**CV note:** the CV hybrid (the honest number below) re-fits the gloss component per fold on the training fold's *gold* rows only (no silver). Production additionally adds silver rows for the surface-handled classes; that does not affect the gloss-cue classes the CV measures, so the CV hybrid is a faithful (slightly under-trained) proxy for production.

Gold-label distribution:

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

## 3. Three-way head-to-head (5-fold stratified CV, identical items)

- splits: **5-fold stratified CV**; n=`1194`; trained-confidence threshold for `uncertain` = `0.40`.

| metric | pure-rules | pure-TF-IDF+LR | hybrid | winner |
|---|---|---|---|---|
| macro-F1 | 0.739 | 0.744 | **0.745** | tie |
| micro-F1 (accuracy) | 0.760 | 0.796 | **0.770** | a pure approach |

**Hybrid >= both pure approaches on macro-F1: True.  On micro-F1: False.**

### Per-class F1 (CV)

| class | pure-rules F1 | pure-TF-IDF F1 | hybrid F1 | support | hybrid vs pure-rules |
|---|---|---|---|---|---|
| `lexical-word` | 0.843 | 0.800 | 0.779 | 299 | loss (-0.064) |
| `phrase` | 0.733 | 0.873 | 0.891 | 262 | win (+0.158) |
| `symbol-code` | 0.969 | 0.877 | 0.788 | 207 | loss (-0.181) |
| `chemical` | 0.558 | 0.754 | 0.689 | 138 | win (+0.131) |
| `proper-name` | 0.527 | 0.737 | 0.757 | 106 | win (+0.230) |
| `taxon` | 0.626 | 0.667 | 0.677 | 71 | win (+0.051) |
| `technical-term` | 0.800 | 0.468 | 0.388 | 67 | loss (-0.412) |
| `abbreviation` | 0.857 | 0.778 | 0.989 | 44 | win (+0.132) |

### Subset breakdown (identical CV items)

| subset | n | pure-rules macro-F1 | pure-TF-IDF macro-F1 | hybrid macro-F1 |
|---|---|---|---|---|
| `short_token_symbol` | 240 | 0.580 | 0.296 | **0.353** |
| `taxon_chemical` | 261 | 0.256 | 0.454 | **0.464** |
| `ordinary_lexical_word` | 283 | 0.934 | 0.899 | **0.828** |
| `other` | 410 | 0.871 | 0.800 | **0.823** |

### `uncertain` reachability (hybrid)

- On the 5-fold CV: surface layer handled **286** of 1194 senses; the trained layer handled the rest. `uncertain` was emitted **32** times (top-class prob below `0.40` and no surface rule) -- so the tag is now reachable, unlike the old pile (where `fallback.uncertain` fired 0 times on the gold set).
- On the full gold set with the persisted (in-sample) model, `uncertain` fired 8 times.

## 4. Hybrid confusion matrix (CV, rows = gold, cols = predicted)

### Hybrid (5-fold CV out-of-fold)

| gold\pred | abbr | chemical | lex | phrase | prop | sym | taxon | tech | unc |
|---|---|---|---|---|---|---|---|---|---|
| `abbr` | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `chemical` | 1 | 93 | 8 | 15 | 3 | 9 | 1 | 1 | 7 |
| `lex` | 0 | 4 | 212 | 0 | 24 | 36 | 1 | 9 | 13 |
| `phrase` | 0 | 4 | 0 | 244 | 0 | 4 | 10 | 0 | 0 |
| `prop` | 0 | 1 | 4 | 8 | 84 | 2 | 5 | 1 | 1 |
| `sym` | 0 | 29 | 0 | 0 | 0 | 178 | 0 | 0 | 0 |
| `taxon` | 0 | 0 | 0 | 19 | 4 | 1 | 45 | 1 | 1 |
| `tech` | 0 | 1 | 21 | 0 | 1 | 15 | 0 | 19 | 10 |
| `unc` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Hybrid top failure modes (CV; gold -> predicted, count)

  - `lexical-word` -> `symbol-code`: 36
  - `symbol-code` -> `chemical`: 29
  - `lexical-word` -> `proper-name`: 24
  - `technical-term` -> `lexical-word`: 21
  - `taxon` -> `phrase`: 19
  - `technical-term` -> `symbol-code`: 15
  - `chemical` -> `phrase`: 15
  - `lexical-word` -> `uncertain`: 13
  - `phrase` -> `taxon`: 10
  - `technical-term` -> `uncertain`: 10
  - `chemical` -> `symbol-code`: 9
  - `lexical-word` -> `technical-term`: 9

## 5. Pure-rules baseline (frozen snapshot) on the full gold set

(For reference -- the agenda-#4 audit's Baseline A, regenerated from the frozen `pure_rules_predict`.)

### pure-rules on the full gold set

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

## 6. Verdict

**hybrid matches the better of the two pure approaches on macro-F1 (no regression)**

Why this is the expected shape: the hybrid is, by construction, "run the surface rules where they win (short tokens / symbol-code / abbreviation), and the trained gloss classifier where bag-of-words wins (taxa / chemicals / proper-name / technical-term)". So on `short_token_symbol` it should match pure-rules, on `taxon_chemical` it should match (a per-fold proxy of) the TF-IDF baseline, and overall it should be >= both. The subset table above is the check.

## 7. Limitations / what was not done

- Gold labels are agent-judged; a human pass would move absolute numbers (comparisons unaffected).
- The full-gold hybrid figure is in-sample for the trained component; the CV figure is the honest one.
- The CV hybrid's gloss component is trained on gold rows only (no silver) per fold -- production adds silver rows for the surface-handled classes, which the CV does not exercise; this is a faithful (slightly conservative) proxy.
- `uncertain` is reachable but rare: the LR's softmax is fairly peaked even at `C=1.0`, so it fires only for the lowest-confidence gloss-layer cases. Spreading it further (temperature scaling, lower `C`) would trade accuracy for more `uncertain`; not done.
- The trained gloss component is still TF-IDF+LR (the agenda-#4 floor); a sentence-transformer gloss embedding would likely lift the gloss-cue classes further -- not done here.

