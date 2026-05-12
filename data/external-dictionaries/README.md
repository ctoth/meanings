# External dictionaries — for the cross-dictionary stability comparison

Used by `scripts/cross_dictionary_stability.py` (agenda item #5 in `reports/synthesis.md`):
test whether the Kernel/Core/MinSet structure of the OEWN definition graph is
stable across dictionaries built under different editorial policies.

## `longman-defining-vocabulary.txt`

The ~2,000-word controlled defining vocabulary that LDOCE (Longman Dictionary of
Contemporary English) restricts its definitions to. One word per line, lowercased,
part-of-speech / inflection annotations and parenthetical glosses stripped (so
`above adv., prep.` → `above`, `your(s)` → `your`, `according (to)` → `according`).

- Source: `healthypackrat/longman-american-defining-vocabulary` on GitHub
  (`longman-american-defining-vocabulary.txt`), itself transcribed from
  <http://www.longmandictionariesusa.com/longman/defining_vocabulary> — i.e. the
  **American** Longman Defining Vocabulary. The British LDOCE list is very close
  but not identical; this is the cleanest one-word-per-line copy available.
- 2,066 unique words after cleaning (the raw list has POS-split duplicates).
- `_ldv_raw.txt` — the raw upstream file (kept for provenance; has the POS tags).

## `ogden-basic-english-850.txt`

Charles Kay Ogden's Basic English (BE 850) — the 850-word controlled vocabulary
(1930). Public domain. One word per line, lowercased.

- Source: Simple English Wikipedia, `Wikipedia:BASIC English alphabetical wordlist`
  (fetched via the MediaWiki API as wikitext, link targets extracted).
- 851 unique words extracted (the list nominally has 850; one extra link slipped in).
- `_ogden_raw.wikitext` — the raw wikitext (provenance).

## `gcide/gcide-0.54.tar.xz`

The GNU Collaborative International Dictionary of English, version 0.54 (the
"gcide-latest" as of 2024-12-31), which is Webster's Revised Unabridged 1913 plus
WordNet 1.5 supplements plus volunteer additions. Public domain / GPL. ~14 MB
compressed; expands to `gcide-0.54/CIDE.{A..Z}` (~59 MB of SGML-ish text).

- Source: <https://ftp.gnu.org/gnu/gcide/gcide-0.54.tar.xz>
- The script extracts and parses it on the fly (entries delimited by `<ent>...</ent>`,
  headword in `<hw>...</hw>`, part of speech in `<pos>...</pos>`, definition text in
  `<def>...</def>`). Kept as the tarball (parseable, under the 50 MB git limit) rather
  than the unpacked text.
