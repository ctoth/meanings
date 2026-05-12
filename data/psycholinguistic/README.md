# Psycholinguistic norm datasets

Standard public psycholinguistic norms, transformed into the CSV shape that
`src/meanings/annotations.py` consumes (`--annotations`): a header row with a key
column named `word` plus one numeric value column named exactly `frequency`,
`age_of_acquisition`, or `concreteness`. Keys are normalized the same way graph
nodes are (`normalize_lemma`): lowercased, spaces and hyphens replaced with `_`,
apostrophes stripped. Only finite values are kept; duplicate keys are dropped
(first occurrence wins).

## Loadable files

| File | Rows | Field | Source column |
|------|------|-------|---------------|
| `frequency.csv` | 74,284 | `frequency` | SUBTLEX-US `Zipf-value` |
| `age_of_acquisition.csv` | 31,104 | `age_of_acquisition` | Kuperman et al. `Rating.Mean` (mean rated AoA, in years) |
| `concreteness.csv` | 39,953 | `concreteness` | Brysbaert et al. `Conc.M` (mean concreteness, 1–5 scale) |

Usage:

```bash
uv run python -m meanings.cli --lexicon oewn:2024 --graph-type paper-wordnet \
  --annotations data/psycholinguistic/frequency.csv \
                data/psycholinguistic/age_of_acquisition.csv \
                data/psycholinguistic/concreteness.csv
```

## Raw source files (kept for provenance)

- `subtlexus.xlsx` — SUBTLEX-US frequency list with PoS and Zipf information (74,286 entries).
- `aoa.xlsx` — `AoA_ratings_Kuperman_et_al_BRM_with_PoS.xlsx`.
- `conc.xlsx` — Concreteness ratings supplementary file (39,954 entries; 37,058 words + 2,896 two-word expressions).

## Citations

**SUBTLEX-US word frequencies.**
Brysbaert, M., & New, B. (2009). Moving beyond Kučera and Francis: A critical
evaluation of current word frequency norms and the introduction of a new and
improved word frequency measure for American English. *Behavior Research
Methods*, 41(4), 977–990. https://doi.org/10.3758/BRM.41.4.977
Part-of-speech and Zipf columns added by:
Brysbaert, M., New, B., & Keuleers, E. (2012). Adding part-of-speech information
to the SUBTLEX-US word frequencies. *Behavior Research Methods*, 44(4),
991–997. https://doi.org/10.3758/s13428-012-0190-4 ;
Zipf scale: van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M.
(2014). SUBTLEX-UK: A new and improved word frequency database for British
English. *Quarterly Journal of Experimental Psychology*, 67(6), 1176–1190.
https://doi.org/10.1080/17470218.2013.850521
File: "SUBTLEX-US frequency list with PoS and Zipf information.xlsx",
downloaded 2026-05-12 from the OSF mirror https://osf.io/djpqz/ (file
https://osf.io/download/7wx25/). Column used: `Zipf-value`.

**Age-of-Acquisition ratings.**
Kuperman, V., Stadthagen-Gonzalez, H., & Brysbaert, M. (2012).
Age-of-acquisition ratings for 30,000 English words. *Behavior Research
Methods*, 44(4), 978–990. https://doi.org/10.3758/s13428-012-0210-4
File: "AoA_ratings_Kuperman_et_al_BRM_with_PoS.xlsx", downloaded 2026-05-12
from the OSF mirror https://osf.io/d7x6q/ (file https://osf.io/download/vb9je/).
Column used: `Rating.Mean` (mean of valid AoA ratings, in years; rows whose
rating is `NA` are excluded).

**Concreteness ratings.**
Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for
40 thousand generally known English word lemmas. *Behavior Research Methods*,
46(3), 904–911. https://doi.org/10.3758/s13428-013-0403-5
File: supplementary material `13428_2013_403_MOESM1_ESM.xlsx`, downloaded
2026-05-12 from Springer
(https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0403-5/MediaObjects/13428_2013_403_MOESM1_ESM.xlsx).
Column used: `Conc.M` (mean concreteness rating on a 1 = abstract … 5 = concrete
scale).

## Regenerating the CSVs

The loadable CSVs were produced from the raw `.xlsx` files with pandas/openpyxl:
for each source, take the `Word` column → normalize → take the value column →
drop non-finite values and duplicate keys → write `word,<field>`.
