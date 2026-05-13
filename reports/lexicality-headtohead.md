# Lexicality classification: rule classifier vs a distributional baseline (head-to-head)

Agenda item #4. **NOTE:** the production classifier is now a *hybrid* (surface rules + a trained gloss classifier) -- see `reports/lexicality-hybrid.md`. The "rule classifier" scored here is the FROZEN pre-hybrid rule pile, reproduced in `scripts/lexicality_headtohead.py::pure_rules_predict`, so this 2-way result stays reproducible.

- gold set: **1194 OEWN senses** (oewn:2024).

### Pre-hybrid rule classifier on the full gold set

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

### Confusion matrix (pre-hybrid rule classifier; rows = gold, cols = predicted)

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

### Pre-hybrid rule classifier on the same 5 CV test folds

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

## Head-to-head

| metric | rule classifier | TF-IDF+LR | winner |
|---|---|---|---|
| macro-F1 | 0.739 | 0.744 | TF-IDF |
| micro-F1 | 0.760 | 0.796 | TF-IDF |

### Subset breakdown (identical CV items)

| subset | n | rule macro-F1 | TF-IDF macro-F1 | rule micro-F1 | TF-IDF micro-F1 |
|---|---|---|---|---|---|
| `short_token_symbol` | 240 | 0.580 | 0.296 | 0.942 | 0.850 |
| `taxon_chemical` | 261 | 0.256 | 0.454 | 0.333 | 0.720 |
| `ordinary_lexical_word` | 283 | 0.934 | 0.899 | 0.876 | 0.816 |
| `other` | 410 | 0.871 | 0.800 | 0.846 | 0.800 |

See `reports/lexicality-hybrid.md` for the three-way (pure-rules / pure-TF-IDF / hybrid) comparison and the per-class wins/losses.

