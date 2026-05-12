# Annotation Sources

**Date:** 2026-05-12

The code supports optional local CSV annotation files via `--annotations`.

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

No psycholinguistic values are bundled or invented in this repository. Reports include zero coverage unless local CSV files are supplied.

Example:

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --annotations data/psycholinguistic/frequency.csv data/psycholinguistic/concreteness.csv
```

