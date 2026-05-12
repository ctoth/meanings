
## 2026-05-12 (agent run, agenda #4/#7)
- Built data/lexicality-gold.csv (1194 senses, 617 stoplisted lemmas skipped). Stratified, hard cases over-represented.
- Rule classifier full-gold: macro-F1 0.739, micro-F1 0.760. symbol-code F1 0.97; proper-name P only 0.39 (titlecase-noun rule over-fires); chemical R 0.43, taxon R 0.51 (templates too narrow). 0 uncertain preds. 12 short tokens -> lexical-word (whitelist does fire).
- TF-IDF+LR (5-fold CV): macro-F1 0.744, micro-F1 0.796. Wins taxon/chemical, loses symbol-code & technical-term.
- Verdict (ii): hybrid. short_token_symbol rule 0.58 vs distr 0.30; taxon_chemical rule 0.26 vs distr 0.45; ordinary ~tie.
- Files: scripts/lexicality_headtohead.py, reports/lexicality-headtohead.{md,json}, data/lexicality-gold.csv. pytest 60 passed before+after. lexicality.py untouched. Not committed.
