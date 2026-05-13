"""Train the gloss-cue component of the hybrid lexicality classifier.

Agenda item #6 (the lexicality part), following the agenda-#4 head-to-head
verdict (ii): keep the surface-pattern rules where they win (short-token /
symbol-code / abbreviation), replace the gloss-keyword *templates*
(taxon / chemical / technical / proper-name) with a small trained gloss
classifier where the bag-of-words baseline won.

Training data construction
--------------------------
The 1,194-sense agent-judged gold set (``data/lexicality-gold.csv``) is small
for a multinomial classifier, so we augment it with *silver* labels:

  * For the classes the surface-pattern rules are near-perfect on
    (``symbol-code`` -- F1 ~0.97 -- and ``abbreviation`` -- F1 ~0.86, both
    driven by surface patterns, not gloss keywords), we take the production
    rule classifier's verdicts on the *full* OEWN corpus and keep only the
    ones produced by a *surface* rule path (single-char / short-token-case /
    code-case / short-token-whitelist / abbreviation-regex / chemical-formula
    regex).  Those paths look only at the lemma surface (plus, for
    abbreviation, an explicit "abbreviation"/"acronym" gloss phrase), so the
    labels are trustworthy as silver data.
  * For the gloss-cue classes (``taxon``, ``chemical``, ``technical-term``,
    ``proper-name``, ``lexical-word``) we use ONLY the gold-set labels -- the
    old keyword rules are unreliable there (per the head-to-head: taxa outside
    the ``genus of`` template fall through; formula-less chemicals fall
    through; ``surface.titlecase_noun`` over-fires for proper-name with P~0.39),
    so we do not trust their silver labels for those classes.

The trained component only needs to be good at the *gloss-cue* classes
({taxon, chemical, technical-term, proper-name, lexical-word}); the surface
layer of the hybrid handles symbol-code / abbreviation / phrase / single-char
before the trained model is ever consulted.  We still include the
surface-rule silver rows for symbol-code/abbreviation in training so the model
learns to *not* claim those (it sees them and learns the gloss patterns that
go with codes), but at inference time the surface layer fires first so the
model's symbol-code/abbreviation predictions are moot.

Risk of the silver labels: the surface-rule silver rows are only as good as
the surface rules.  Those rules are near-perfect *on the gold set's
short-token/abbreviation strata* (F1 0.86-0.97), but on the full corpus they
will occasionally mislabel (e.g. a 2-letter ordinary word not on the 27-item
whitelist gets silver-labelled symbol-code).  Mitigation: (1) only surface
*paths* are trusted, never the gloss-keyword paths; (2) the gloss-cue classes
that actually matter for the hybrid take gold labels only; (3) the silver rows
are down-weighted relative to gold rows (sample_weight).

Run:  uv run python scripts/train_lexicality_classifier.py
Writes:  data/lexicality_gloss_clf.joblib  (a few MB; the TF-IDF vocab dominates)
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import wn

from meanings.lexicality import SURFACE_REASON_PREFIXES, _surface_layer
from meanings.lexicality_model import GLOSS_CUE_LABELS, GlossClassifier
from meanings.normalize import normalize_lemma

REPO = Path(__file__).resolve().parents[1]
GOLD_CSV = REPO / "data" / "lexicality-gold.csv"
MODEL_PATH = REPO / "data" / "lexicality_gloss_clf.joblib"
LEXICON_ID = "oewn:2024"
SEED = 20240512

# The trained classifier's label space (the gloss-cue classes).  symbol-code,
# abbreviation, phrase, idiom, single-char are handled by the surface layer.
# Surface-rule reason prefixes whose verdicts we trust as silver data (these
# paths look only at the lemma surface, not at gloss keywords).
TRUSTED_SILVER_REASONS = SURFACE_REASON_PREFIXES

# How many full-corpus silver rows to draw per trusted surface class.
SILVER_PER_CLASS = {
    "symbol-code": 4000,
    "abbreviation": 800,
}
SILVER_WEIGHT = 0.25  # silver rows down-weighted vs gold rows (weight 1.0)


# ---------------------------------------------------------------------------
def load_gold_rows() -> list[dict]:
    """Load the gold CSV and re-hydrate live glosses/lemmas/pos from the lexicon."""
    if not GOLD_CSV.exists():
        raise SystemExit(f"missing {GOLD_CSV}; run scripts/lexicality_headtohead.py first")
    keys: list[tuple[str, str]] = []  # (sense_key, gold)
    with GOLD_CSV.open(encoding="utf-8", newline="") as fh:
        for d in csv.DictReader(fh):
            keys.append((d["sense_key"], d["gold_lexicality"]))
    wnet = wn.Wordnet(LEXICON_ID)
    by_key: dict[str, object] = {}
    for word in wnet.words():
        for sense in word.senses():
            by_key[sense.id] = (word, sense)
    rows: list[dict] = []
    for sk, gold in keys:
        rec = by_key.get(sk)
        if rec is None:
            continue
        word, sense = rec
        syn = sense.synset()
        gloss = syn.definition() or ""
        if not gloss.strip():
            continue
        rows.append(
            {
                "sense_key": sk,
                "lemma": word.lemma(),
                "pos": word.pos,
                "gloss": gloss,
                "gold": gold,
                "source": "gold",
            }
        )
    return rows


def collect_silver_rows(rng: random.Random, exclude_keys: set[str]) -> list[dict]:
    """Walk the full OEWN corpus; for each sense run the rule classifier and
    keep it only if a *trusted surface* rule produced the verdict."""
    wnet = wn.Wordnet(LEXICON_ID)
    pools: dict[str, list[dict]] = {cls: [] for cls in SILVER_PER_CLASS}
    seen: set[str] = set()
    for word in wnet.words():
        lemma = word.lemma()
        pos = word.pos
        for sense in word.senses():
            sk = sense.id
            if sk in seen or sk in exclude_keys:
                continue
            seen.add(sk)
            syn = sense.synset()
            gloss = syn.definition() or ""
            if not gloss.strip():
                continue
            # only the SURFACE layer -- never the trained model (which may be a
            # stale artifact during a re-train) and never the legacy
            # gloss-keyword fallbacks (those are not trusted as silver).
            c = _surface_layer(normalize_lemma(lemma), lemma, gloss, gloss)
            if c is None:
                continue
            tag = c.tag.value
            if tag not in pools:
                continue
            # belt-and-suspenders: every reason must be a trusted surface path
            if not c.reasons or not all(
                any(r.startswith(p) for p in TRUSTED_SILVER_REASONS) for r in c.reasons
            ):
                continue
            pools[tag].append(
                {
                    "sense_key": sk,
                    "lemma": lemma,
                    "pos": pos,
                    "gloss": gloss,
                    "gold": tag,
                    "source": "silver",
                }
            )
    out: list[dict] = []
    for cls, target in SILVER_PER_CLASS.items():
        pool = pools[cls]
        rng.shuffle(pool)
        out.extend(pool[: min(target, len(pool))])
    return out


def main() -> None:
    rng = random.Random(SEED)
    gold_rows = load_gold_rows()
    gold_keys = {r["sense_key"] for r in gold_rows}
    print(f"gold rows hydrated: {len(gold_rows)}  ({Counter(r['gold'] for r in gold_rows)})")
    silver_rows = collect_silver_rows(rng, exclude_keys=gold_keys)
    print(f"silver rows (trusted surface-rule paths only): {len(silver_rows)}  ({Counter(r['gold'] for r in silver_rows)})")

    rows = gold_rows + silver_rows
    lemmas = [r["lemma"] for r in rows]
    glosses = [r["gloss"] for r in rows]
    poss = [r["pos"] for r in rows]
    y = [r["gold"] for r in rows]
    weights = np.asarray([1.0 if r["source"] == "gold" else SILVER_WEIGHT for r in rows])

    clf = GlossClassifier().fit(lemmas, glosses, poss, y, sample_weight=weights)
    print(f"trained classifier; classes = {clf.classes_}")

    joblib.dump(clf, MODEL_PATH, compress=3)
    size_mb = MODEL_PATH.stat().st_size / 1e6
    print(f"wrote {MODEL_PATH}  ({size_mb:.2f} MB)")

    meta = {
        "lexicon_id": LEXICON_ID,
        "model_path": str(MODEL_PATH.relative_to(REPO)),
        "model_size_mb": round(size_mb, 3),
        "gloss_cue_labels": list(GLOSS_CUE_LABELS),
        "trained_classes": clf.classes_,
        "gold_rows": len(gold_rows),
        "silver_rows": len(silver_rows),
        "silver_per_class_target": SILVER_PER_CLASS,
        "silver_weight": SILVER_WEIGHT,
        "trusted_silver_reason_prefixes": list(TRUSTED_SILVER_REASONS),
        "seed": SEED,
    }
    (REPO / "data" / "lexicality_gloss_clf.meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote data/lexicality_gloss_clf.meta.json")


if __name__ == "__main__":
    main()
