# Annotation Sources

**Date:** 2026-05-12 (updated)

The code supports optional local CSV annotation files via `--annotations`
(loader: `src/meanings/annotations.py`).

Supported numeric fields:

- `frequency`
- `concreteness`
- `age_of_acquisition`
- `imageability`

Supported key columns:

- `word`
- `lemma`
- `term`
- `node`
- `key`

Keys are normalized exactly like graph nodes (`normalize_lemma`): lowercased,
spaces and hyphens → `_`, apostrophes stripped.

## Bundled datasets (present as of 2026-05-12)

Three standard public psycholinguistic norm sets are now committed under
`data/psycholinguistic/` (full references, URLs, and the source columns used are
in `data/psycholinguistic/README.md`; conversion script:
`scripts/build_psycholinguistic_csvs.py`):

| File | Field | Dataset | Rows |
|------|-------|---------|------|
| `data/psycholinguistic/frequency.csv` | `frequency` | SUBTLEX-US (Brysbaert & New 2009; Zipf scale via van Heuven et al. 2014) | 74,284 |
| `data/psycholinguistic/age_of_acquisition.csv` | `age_of_acquisition` | Kuperman, Stadthagen-Gonzalez & Brysbaert (2012) | 31,104 |
| `data/psycholinguistic/concreteness.csv` | `concreteness` | Brysbaert, Warriner & Kuperman (2014) | 39,953 |

Raw source spreadsheets (`subtlexus.xlsx`, `aoa.xlsx`, `conc.xlsx`) are kept
alongside for provenance. No `imageability` dataset is bundled (none of the
current research deliverables requires it).

## Coverage on OEWN 2024 (`--graph-type paper-wordnet`, 160,010 nodes)

Verified by running:

```powershell
uv run python -m meanings.cli --lexicon oewn:2024 --graph-type paper-wordnet `
  --annotations data/psycholinguistic/frequency.csv `
                data/psycholinguistic/age_of_acquisition.csv `
                data/psycholinguistic/concreteness.csv
```

| Field | Covered nodes | Fraction |
|-------|---------------|----------|
| `frequency` | 46,386 / 160,010 | 28.99% |
| `concreteness` | 38,572 / 160,010 | 24.11% |
| `age_of_acquisition` | 34,314 / 160,010 | 21.44% |
| `imageability` | 0 / 160,010 | 0% |

(Coverage is below the dataset row counts because OEWN nodes include many
multi-word and proper-name lemmas absent from the single-word norm lists, and a
single normalized key may collapse several spreadsheet rows.) The generated
`reports/oewn-paper-wordnet-kernel-report.md` "Annotation Coverage" section and
`reports/oewn-paper-wordnet-kernel-summary.json` (`annotation_coverage`,
`component_annotation_summary`) now carry these numbers.
