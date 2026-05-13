
## 2026-05-12 agent (agenda #6 hybrid lexicality)
- Built: src/meanings/lexicality_model.py (GlossClassifier, picklable, lives in meanings so unpickle works); rewrote src/meanings/lexicality.py as hybrid (surface layer -> trained gloss clf -> uncertain fallback; new reason traces surface.* / trained.<cls>.p<prob> / trained.lowconf.p<prob> / fallback.*); scripts/train_lexicality_classifier.py (gold rows + silver surface-rule rows for symbol-code/abbreviation, silver weight 0.25); rewrote tests/test_lexicality.py.
- Training run in background (task by2qufcef) — slow phase is the 161k-word silver walk. Monitor armed (bz2frfoii).
- TODO: extend scripts/lexicality_headtohead.py with 3 cols (pure-rules frozen snapshot / pure-TFIDF / hybrid-via-CV — must avoid leakage: retrain GlossClassifier per fold); run pytest before+after; write reports/lexicality-hybrid.{md,json}.
- Blocker: waiting on training to finish (need the .joblib for pytest + headtohead hybrid in-prod path).

## 2026-05-12 checkpoint 2
- lexicality.py rewritten (hybrid: surface layer -> trained gloss clf -> uncertain @ thresh 0.40). lexicality_model.py has GlossClassifier (C=1.0 — C=4 overfit in-sample acc~1.0). headtohead script extended (3 cols: pure-rules frozen / pure-TFIDF / hybrid-CV; writes reports/lexicality-hybrid.{md,json} + still regenerates lexicality-headtohead.{md,json}).
- BLOCKER: training script (scripts/train_lexicality_classifier.py) takes >5 min — the 161k-word OEWN walk (load_gold_rows builds by_key over all words, then collect_silver_rows walks again). Fixed silver collection to use _surface_layer directly (was calling classify_lexicality which loaded the stale model -> predict_proba per call, very slow). Currently running bt0xq3j3r in background, monitor bgj2nic0m.
- Two known test failures to fix after model exists: test_taxon_outside_old_template (titlecase genus pulls proper-name in trained clf — need a real OEWN example or loosen assertion), test_low_confidence_gloss_returns_uncertain (model too confident on "a thing" — need genuinely ambiguous input).
- TODO once model built: pytest, run headtohead, fill report numbers, fix the 2 tests.

## 2026-05-12 checkpoint 3
- Model trained (C=1.0, 0.84MB, classes incl all 8). tests/test_lexicality.py: all 10 pass. Full suite: 102 passed.
- Test fixtures that worked: taxon -> classify_lexicality("Acer","n","the type genus, comprising the maples") -> taxon (trained.*). uncertain -> classify_lexicality("flarn","n","characteristic of") -> uncertain (trained.lowconf.p0.39). formula-less chemical -> "aspirin" gloss -> chemical. H2O -> surface.chemical_formula. nobelium full name -> chemical.
- Running headtohead (bg8x2gmb4, monitor bvsx1rx3f) -> writes reports/lexicality-hybrid.{md,json} + regenerates lexicality-headtohead.{md,json}.
- Remaining: read headtohead numbers, confirm hybrid>=both, finalize report (auto-gen), final report-back.

## 2026-05-12 checkpoint 4 — first headtohead result was BAD
- CV hybrid macro 0.651 << pure-rules 0.739, pure-TFIDF 0.744. Causes: (1) uncertain fired 131/1194 in CV (every uncertain = guaranteed miss since gold never = uncertain) — the per-fold gloss model was trained gold-only (no silver) so weak; (2) C=1.0 (I lowered it to make uncertain reachable) destroyed taxon/chemical F1 (0.315/0.329 vs agenda-#4's 0.667/0.754 at C=4).
- In-sample full-gold hybrid (production model on its training labels): macro 0.806 / micro 0.815 — beats pure-rules. Truth is between in-sample and the (too-pessimistic) CV.
- Fix in progress: reverted GlossClassifier to C=4 (matches agenda-#4 winner); added silver rows to the CV hybrid's per-fold training (was the unfaithful proxy); kept threshold 0.40 (uncertain "reachable but rare" — fires for gibberish like "flarn"/"characteristic of"). Retraining now (b5kk07ag0). Then re-run headtohead. Then maybe re-pick the uncertain test fixture for C=4.
- pytest currently: 102 passed (but test fixtures may need re-tuning after C=4 retrain).

## 2026-05-12 checkpoint 5 — root cause of hybrid regression
- The CV hybrid was bad (macro 0.652) because the surface layer's `multiword->phrase` rule fired BEFORE the trained classifier — so multiword chemicals/taxa (Felis_catus, acetylsalicylic_acid, Quercus_alba) got stamped `phrase`. Confusion: chemical->phrase 65×, taxon->phrase 50×.
- FIX: removed `multiword->phrase` from the surface layer; trained model handles phrase vs multiword chemical/taxon/proper-name (its label space includes phrase, learned from 262 mostly-multiword examples). Low-conf fallback: multiword->phrase, else uncertain. Same in headtohead's _hybrid_surface_layer + CV loop. Updated tests (added test_multiword_chemical_not_stamped_phrase). pytest: 107 passed.
- Re-running headtohead now.

## 2026-05-12 DONE
- CV hybrid macro-F1 0.745 >= both (pure-rules 0.739, pure-TFIDF 0.744). micro 0.770 (between). taxon_chemical 0.464 (beats both). short_token_symbol 0.353 (beats TFIDF 0.296, below rules 0.580). uncertain fired 32x CV / 8x full in-sample.
- Per-class wins vs pure-rules: proper-name +0.23, phrase +0.16, chemical +0.13, abbreviation +0.13, taxon +0.05. Losses: technical-term -0.41 (trained model bad at it; rules' gloss-keyword tech rule won there in agenda-#4 — flagged in report; task explicitly said to replace the tech template so left as-is), symbol-code -0.18, lexical-word -0.06.
- Files: src/meanings/lexicality.py (hybrid), src/meanings/lexicality_model.py (GlossClassifier C=4), scripts/train_lexicality_classifier.py, scripts/lexicality_headtohead.py (3-col), tests/test_lexicality.py (107 pass full suite), reports/lexicality-hybrid.{md,json}, reports/lexicality-headtohead.{md,json} (regenerated 2-way), data/lexicality_gloss_clf.{joblib,meta.json} (0.84MB). NOT committed.
