# IC merge method — replacing the 7-pair whitelist with a procedure

*Agenda #6 (the IC-merge part) from `reports/synthesis.md`. Implements
`src/meanings/identity_clusters.py`; data in `reports/ic-merge-method.json`
(full table) and `reports/ic-merge-method.summary.json` (stats + samples).*

## What was there

`HIGH_CONFIDENCE_SPELLING_VARIANTS` was a hand-coded tuple of **7** merge
records over **14** forms (`color/colour`, `center/centre`, `theater/theatre`,
`ax/axe`, `gray/grey`, `honor/honour`, `organize/organise`). `wordnet_pipeline`
consumed it through `identity_cluster_for_form(lemma) -> .ic_id`. The Codex
review's verdict was correct: *"a fixture, not a method."*

## The procedure

`build_identity_clusters(lexicon)` over OEWN 2024:

1. **Candidate detection** — over the 151,622 OEWN lemmas (single-token,
   alphabetic, length ≥ 2, not obviously a symbol-code), generate candidate
   spelling-variant pairs by:
   - **Orthographic-variant rules** (`_RULES`): `-or`/`-our`, `-er`/`-re`,
     `-ize`/`-ise` + `-ization`/`-isation`, `-yze`/`-yse`, `-og`/`-ogue`,
     `-ce`/`-se` + `-nce`/`-nse`, `-mme`/`-m`, `ae`/`e`, `oe`/`e`, doubled-vs-
     single consonant before a vowel-initial suffix (`traveled`/`travelled`),
     and stem-`e` elision (`judgment`/`judgement`, `aging`/`ageing`). Plus a
     hand list of irregular alternants (`grey`/`gray`, `ax`/`axe`,
     `plough`/`plow`, `aluminium`/`aluminum`, `metre`/`meter`, …).
   - **A generic Levenshtein ≤ 1 pass** for what the rules miss
     (`pavis`/`pavise`, `kathmandu`/`katmandu`, `feldspar`/`felspar`,
     `bermudan`/`bermudian`). Implemented with selective blanked-position
     substitution keys + capped indel buckets (Norvig/SymSpell-style) so it runs
     in seconds, not an O(n²) scan; a small hard-capped transposition pass
     catches anagram-distance-2 alternants. Both members of every candidate must
     be in the lexicon.
   - **Code-like exclusion** (`_is_code_like`): Roman numerals (`^[ivxlcdm]{2,}$`),
     IEC binary-unit prefixes (`kibit`, `mibyte`), and vowel-less lemmas are
     dropped before the candidate pass — they cluster densely under
     edit-distance-1 with near-identical glosses ("the cardinal number that
     is …"), so the gloss gate cannot separate them, and they are `symbol-code`s,
     not spelling variants. Removing them killed two junk clusters (a 38-form
     Roman-numeral blob and an 8-form `*bit` blob).

   → **33,801 candidate pairs**.

2. **Gloss-similarity gate** — a candidate `(f1, f2)` merges only if some sense
   of `f1` and some sense of `f2` *of the same POS* have glosses with token-
   Jaccard similarity ≥ **0.34** (`GLOSS_GATE_THRESHOLD`). Jaccard over
   stop-stripped gloss content tokens, not per-pair TF-IDF (degenerate over a
   two-document corpus); a corpus-wide TF-IDF cosine helper
   (`gloss_cosine_corpus`, sklearn) is provided for analysis but the gate uses
   Jaccard. **0.34** sits in the gap between real variant pairs (whose glosses
   are near-identical → Jaccard 0.5–1.0) and edit-distance look-alikes (which
   share essentially nothing → ~0.0–0.1). Senses that don't pass stay in their
   own ICs.

   → **4,770 candidates pass; 29,031 are rejected by the gate.**

3. **The merge** — each accepted candidate emits a `MergeRecord`:
   `contributing_forms`, `merged_sense_ids` (the same-POS sense pairs that
   cleared the gate), `rule_id` (which orthographic rule fired, or
   `edit-distance`), `gloss_score` (Jaccard of the best matched pair),
   `matched_sense_pair`, `pos`, `provenance`. Accepted pairs are unioned
   (union-find) into `IdentityCluster`s; each IC keeps **all** member forms
   (`forms`/`aliases`), **all** their senses (`sense_ids`), and the
   `MergeRecord`s that built it. This is merge, not canonicalization — no form
   is rewritten away (cf. `notes/sense-ingestion-design.md` and
   `reports/synthesis-facet-datamodel-claude.md` §3.3). `ic_id` is
   deterministic: `ic:<alphabetically-first-member-form>`.

4. **Interface** — `identity_cluster_for_form(form)` is unchanged in signature
   and returns an `IdentityClusterMerge` view (`ic_id`, `forms`, `rationale`,
   `evidence`) for any merged form, else `None`; `wordnet_pipeline`'s
   `ic_id` assignment keeps working. The table is computed once and persisted to
   `reports/ic-merge-method.json`; the runtime lookup loads that JSON lazily so
   per-sense calls in the pipeline stay O(1). `spelling_variant_index(rebuild=True)`
   recomputes from the live lexicon. `build_identity_clusters` has a fast path
   that reads the `wn` SQLite store directly (one query, ~2 s) instead of the
   per-object `wn` navigation API (~1 ms/call → ~6 min over OEWN); it falls back
   to navigation if the DB isn't there.

## Evaluation over OEWN 2024

| metric | value |
|---|---|
| lemmas considered | 151,622 |
| candidate pairs | 33,801 |
| accepted (merged) pairs | 4,770 |
| rejected by gloss gate | 29,031 |
| **identity clusters formed** | **4,248** |
| **forms in clusters** | **8,897** |
| merge records | 4,770 |
| baseline | 7 ICs / 14 forms |

Cluster-size histogram: `{2: 3971, 3: 194, 4: 62, 5: 11, 6: 4, 7: 4, 8: 1, 10: 1}`
— almost all are plain pairs; the long tail is transliteration families
(`cabala/cabbala/kabbalah/qabalah…` 10 forms; `chasidim/chassidism/hasidim…` 8;
`channukah/chanukkah/hanukah…` 7; `mama/mamma/mammy/momma/mommy/mumma/mummy` 7;
`mujahideen/mujahedin/mujahadeen…` 7; `borsch/borscht/borshch/bortsch…` 6;
`cither/cittern/zither/gittern…` 6).

Merges by which rule fired: `edit-distance` 3,158, `spelling.ize_ise` 795,
`spelling.doubled_consonant` 312, `spelling.ae_e` 240, `spelling.oe_e` 79,
`spelling.er_re` 57, `spelling.or_our` 50, `spelling.dropped_e` 29,
`spelling.lexical_pairs` 22, `spelling.yze_yse`/`spelling.ce_se` 9 each,
`spelling.og_ogue` 7, `spelling.mme_m` 3. Of the 4,248 clusters, 2,691 were
built only by edit-distance merges, 1,486 only by orthographic rules, 71 mixed.

**Regression**: all 7 original whitelist pairs are still merged by the
procedure (`regression_missed == []`).

### Spot-check (two random samples of 30 merges, hand-graded)

~26–27 of every 30 are unambiguously correct spelling / transliteration
variants: `bowdlerise/bowdlerize`, `naturalisation/naturalization`,
`pyorrhea/pyorrhoea`, `saber/sabre`, `picometer/picometre`, `kathmandu/katmandu`,
`feldspar/felspar`, `baritone/barytone`, `peewit/pewit`, `marshal/marshall`,
`taradiddle/tarradiddle`, `odesa/odessa`, `bishkek/biskek`, `farthest/furthest`,
`humblebee/bumblebee`, `vertu/virtu`, `ashurbanipal/assurbanipal`, etc.

The misses are the **morphological / synonym false positives** an edit-distance
≤ 1 pass produces when two genuinely different words happen to be one edit apart
*and* have near-identical glosses (so the gloss gate can't reject them):

- derivational pairs where the differing character is a real morpheme:
  `theism`/`theist` (-ism/-ist, Jaccard 0.38), `asynchrony`/`synchrony`
  (a-prefix, 0.56), `ciliate`/`ciliated`.
- true synonyms one edit apart: `crumple`/`rumple` (both "wrinkle"),
  `ratty`/`tatty` (both "worn"); chains of onomatopoeic neighbours all glossed
  "a short light metallic sound" produced the one ugly 7-form cluster
  `chink/clack/click/clink/cluck/crack/flick`.

Estimated precision ≈ **90%** (≈ 3 false-positive merges per 30). False
positives concentrate in the `edit-distance` bucket; the orthographic-rule
buckets are essentially clean. Catching the derivational ones would need a
known-affix check (don't merge across `-ism`/`-ist`, `a-`/`∅`, `-e`/`-ed`);
that's a follow-up, not done here.

### What the gloss gate caught (29,031 rejections, all with best gloss-Jaccard 0.0)

The gate is the load-bearing filter. It rejected, among others:
`colon`/`color`, `desert`/`dessert`, `affect`/`effect`, `loose`/`lose`,
`then`/`than` and `tor`/`tour`, `amor`/`amour`, `boer`/`bore`, `goer`/`gore`,
`seer`/`sere`, `advice`/`advise`, `race`/`rase`, `terce`/`terse`, `dyeing`/`dying`,
`prolog`/`prologue`, `filing`/`filling`, `razing`/`razzing`, `compositae`/`composite`,
`moirae`/`moire`, plus the entire proper-name doubled-consonant noise band
(`hoffman`/`hoffmann`, `curtis`/`curtiss`, `mantel`/`mantell`, `star`/`starr`,
`marri`/`mari`). 28,717 of the 29,031 rejections came from the generic
edit-distance pass — i.e. the gate is doing exactly its job: an edit-distance
candidate is *provisional* until two same-thing-denoting senses confirm it.

### What it still misses (out of scope, noted)

- **Pronunciation variants with non-orthographic spelling differences** —
  `warsh`/`wash`, dialectal respellings: not generated by any rule and usually
  > 1 edit apart, so not candidates. (And per the data model these are *indexical*
  on the form, not a referential split — they should land in the same IC, but
  detecting them needs a pronunciation/dialect signal, not orthography.)
- **Sense-specific overlap** — two forms that share *one* sense but not another
  are currently merged into one IC carrying *all* senses of both forms (the
  `merged_sense_ids` on the `MergeRecord` does record which senses actually
  matched, so the finer split is reconstructible, but the IC itself is whole-form).
- **Long transliteration chains** are correct as families but the union-find
  collapses them by transitivity through edit-distance links; the `MergeRecord`
  list per IC preserves which specific pairs were judged identical and on what
  evidence, so a later `SplitRecord` could prune a chain without information loss.

## Files

- `src/meanings/identity_clusters.py` — the procedure (`OrthographicRule`,
  `candidate_pairs`, `gloss_similarity`, `MergeRecord`, `IdentityCluster`,
  `build_identity_clusters`, `_iter_form_pos_sense_def` fast path,
  `spelling_variant_index`/`identity_cluster_for_form` runtime interface,
  `ORIGINAL_REGRESSION_PAIRS`, `HIGH_CONFIDENCE_SPELLING_VARIANTS` kept as the
  regression fixture).
- `tests/test_identity_clusters.py` — 34 tests: edit distance, orthographic
  rules, candidate detection + code-like exclusion, the gloss gate, a full
  `build_identity_clusters` over a fake lexicon (incl. the `colon`/`color`
  rejection), the 7 original pairs as a regression fixture, ~13 new pairs the
  procedure should merge, 5 look-alike pairs it must not merge, and the runtime
  interface contract.
- `scripts/build_ic_table.py` — rebuilds `reports/ic-merge-method.json` and the
  summary over OEWN. `scripts/ic_profile.py` — phase timing helper.
- `reports/ic-merge-method.json` — the full table (clusters + merge records +
  rejected candidates). `reports/ic-merge-method.summary.json` — stats,
  size histogram, regression check, rejected examples, a 40-merge spot sample.
