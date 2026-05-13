"""The trained gloss-cue component of the hybrid lexicality classifier.

Lives in ``meanings`` (not ``scripts``) so the pickled model unpickles cleanly
wherever ``meanings`` is importable.  Built by
``scripts/train_lexicality_classifier.py``; consumed lazily by
``meanings.lexicality.classify_lexicality``.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from meanings.normalize import normalize_lemma

# The trained classifier's label space (the gloss-cue classes).  symbol-code,
# abbreviation, phrase, idiom, single-char, and `technical-term` (round-7 hole
# #2) are handled by the surface layer of the hybrid before this model is
# ever consulted.  `technical-term` was previously in the label space but the
# trained classifier scored 0.39 F1 on it vs the pure-rules 0.80; the surface
# rule now owns that class.
GLOSS_CUE_LABELS = (
    "taxon",
    "chemical",
    "proper-name",
    "lexical-word",
)

_POS_SET = ("n", "v", "a", "s", "r")
_FORMULA_RE = None  # set lazily to avoid an import cycle with meanings.lexicality


def _formula_match(lemma: str) -> float:
    global _FORMULA_RE
    if _FORMULA_RE is None:
        from meanings.lexicality import CHEMICAL_FORMULA_RE

        _FORMULA_RE = CHEMICAL_FORMULA_RE
    return 1.0 if _FORMULA_RE.fullmatch(lemma.strip()) else 0.0


def structural_features(lemmas: list[str], glosses: list[str], poss: list[str]) -> csr_matrix:
    rows = []
    for lemma, gloss, pos in zip(lemmas, glosses, poss):
        norm = normalize_lemma(lemma)
        bare = norm.replace("_", "")
        letters = "".join(c for c in lemma if c.isalpha())
        is_title = 1.0 if letters and letters[:1].isupper() and letters[1:].islower() else 0.0
        is_upper = 1.0 if letters and letters.isupper() and len(letters) > 1 else 0.0
        has_digit = 1.0 if any(ch.isdigit() for ch in lemma) else 0.0
        pos_onehot = [1.0 if pos == p else 0.0 for p in _POS_SET]
        rows.append(
            [
                len(bare) / 20.0,
                is_title,
                is_upper,
                has_digit,
                1.0 if "_" in norm else 0.0,
                float(norm.count("_")) / 5.0,
                len(gloss.split()) / 30.0,
                _formula_match(lemma),
                *pos_onehot,
            ]
        )
    return csr_matrix(np.asarray(rows, dtype=float))


class GlossClassifier:
    """TF-IDF (gloss word 1-2 grams + lemma char-wb 3-5 grams) + cheap
    structural features -> class-balanced multinomial logistic regression.
    Picklable."""

    def __init__(self) -> None:
        self.word_vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        self.char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True)
        # C=4.0 matches the agenda-#4 head-to-head's winning TF-IDF+LR baseline
        # (it generalizes best in CV there, esp. on the taxon/chemical classes
        # this component exists to serve).  The softmax is fairly peaked at this
        # C, so the low-confidence `uncertain` path is reachable but rare on
        # real OEWN data -- it fires mainly for genuinely degenerate glosses.
        self.clf = LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced")
        self.classes_: list[str] = []

    @staticmethod
    def _gloss_text(gloss: str, lemma: str) -> str:
        return gloss.strip() + " || " + normalize_lemma(lemma).replace("_", " ")

    def _features(self, lemmas, glosses, poss, *, fit: bool):
        texts = [self._gloss_text(g, l) for g, l in zip(glosses, lemmas)]
        surfaces = [normalize_lemma(l).replace("_", " ") for l in lemmas]
        if fit:
            Xw = self.word_vec.fit_transform(texts)
            Xc = self.char_vec.fit_transform(surfaces)
        else:
            Xw = self.word_vec.transform(texts)
            Xc = self.char_vec.transform(surfaces)
        Xs = structural_features(lemmas, glosses, poss)
        return hstack([Xw, Xc, Xs]).tocsr()

    def fit(self, lemmas, glosses, poss, y, sample_weight=None) -> "GlossClassifier":
        X = self._features(lemmas, glosses, poss, fit=True)
        self.clf.fit(X, y, sample_weight=sample_weight)
        self.classes_ = list(self.clf.classes_)
        return self

    def predict(self, lemmas, glosses, poss) -> list[str]:
        X = self._features(lemmas, glosses, poss, fit=False)
        return list(self.clf.predict(X))

    def predict_proba(self, lemmas, glosses, poss):
        X = self._features(lemmas, glosses, poss, fit=False)
        return self.clf.predict_proba(X)

    def predict_with_confidence(self, lemma: str, gloss: str, pos: str) -> tuple[str, float]:
        proba = self.predict_proba([lemma], [gloss], [pos])[0]
        i = int(np.argmax(proba))
        return self.classes_[i], float(proba[i])
