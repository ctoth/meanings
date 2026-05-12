# Psycholinguistic Annotation Data Ingest

**2026-05-12**

## Goal
Get SUBTLEX-US freq, Kuperman 2012 AoA, Brysbaert 2014 Concreteness into data/psycholinguistic/, transform to CSV that annotations.py expects, verify CLI coverage.

## CSV format annotations.py wants (verified by reading src/meanings/annotations.py)
- csv.DictReader, encoding utf-8-sig
- key column: one of word/lemma/term/node/key (case-insensitive)
- value columns named exactly: frequency, concreteness, age_of_acquisition, imageability (also no-underscore / space variants accepted)
- key normalized: strip().lower(), spaces->_, hyphens->_, apostrophes removed (matches normalize_lemma for node keys)
- node keys in graph = normalize_lemma(word.lemma()) for paper-wordnet/lemma graph; ~160k nodes
- Only need frequency, age_of_acquisition, concreteness (per swanson-4 and swanson-5 reports). imageability not required.

## Downloads
- crr.ugent.be/papers/* -> 404 (site reorganized)
- raw.githubusercontent.com/chrplr/openlexicon/master/datasets-info/... -> 404 (paths guessed wrong)
- TODO: find correct openlexicon paths or OSF mirrors. OSF: SUBTLEX osf.io/djpqz, AoA osf.io/d7x6q. Concreteness: ?
- ugent expsy: http://expsy.ugent.be/subtlexus/ ; lexique mirror subtlexus.lexique.org

## Status: still locating download URLs

## DOWNLOADS DONE (2026-05-12)
- aoa.xlsx (1.94MB) <- https://osf.io/download/vb9je/ (OSF node d7x6q) "AoA_ratings_Kuperman_et_al_BRM_with_PoS.xlsx" -- Kuperman/Stadthagen-Gonzalez/Brysbaert 2012, Rating.Mean col
- conc.zip (2.2MB, actually xlsx) <- https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0403-5/MediaObjects/13428_2013_403_MOESM1_ESM.xlsx -- Brysbaert/Warriner/Kuperman 2014 Concreteness, Conc.M col
- subtlexus.xlsx (10.76MB) <- https://osf.io/download/7wx25/ (OSF node djpqz) "SUBTLEX-US frequency list with PoS and Zipf information.xlsx" -- Brysbaert&New 2009 + Zipf (Van Heuven 2014), Lg10WF / Zipf-value col
  NOTE: 10.76MB < 50MB so fine to commit.

## NEXT: parse xlsx with pandas/openpyxl via uv add, build CSVs with columns: word, frequency / age_of_acquisition / concreteness. Then run CLI.

## VERIFIED (2026-05-12)
CLI ran exit 0:
uv run python -m meanings.cli --lexicon oewn:2024 --graph-type paper-wordnet --annotations data/psycholinguistic/frequency.csv data/psycholinguistic/age_of_acquisition.csv data/psycholinguistic/concreteness.csv
=> reports/oewn-paper-wordnet-kernel-summary.json annotation_coverage:
  frequency: 46386/160010 (28.99%)
  concreteness: 38572/160010 (24.11%)
  age_of_acquisition: 34314/160010 (21.44%)
  imageability: 0 (not provided, not needed)
Report: reports/oewn-paper-wordnet-kernel-report.md "## Annotation Coverage" section now non-zero.

## CSV format produced
header: word,<field>   ; field in {frequency, age_of_acquisition, concreteness}
word = normalized lemma (lowercased, -/space -> _, apostrophes dropped), dedup, finite values only
frequency.csv: 74284 rows, value = SUBTLEX-US Zipf-value
age_of_acquisition.csv: 31104 rows, value = Kuperman Rating.Mean
concreteness.csv: 39953 rows, value = Brysbaert Conc.M

## Files written
data/psycholinguistic/{frequency,age_of_acquisition,concreteness}.csv  (loadable)
data/psycholinguistic/{subtlexus.xlsx, aoa.xlsx, conc.zip}  (raw sources; conc.zip is actually xlsx -> rename to conc.xlsx)
data/psycholinguistic/README.md  (citations)
.gitignore: only *.png *.pdf etc - does NOT exclude data/ or csv/xlsx. OK. Largest file subtlexus.xlsx 10.76MB < 50MB.
