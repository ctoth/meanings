"""Quick profiling of the IC build phases over OEWN."""

from __future__ import annotations

import time
from collections import defaultdict

import wn

from meanings.identity_clusters import candidate_pairs, gloss_similarity
from meanings.normalize import normalize_lemma

t0 = time.time()
wn.download("oewn:2024")
lex = wn.Wordnet("oewn:2024")
print(f"load: {time.time() - t0:.1f}s", flush=True)

t = time.time()
by_pos: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
n_words = 0
for word in lex.words():
    n_words += 1
    lemma = normalize_lemma(word.lemma())
    for sense in word.senses():
        syn = sense.synset()
        d = syn.definition()
        if not d:
            continue
        by_pos[lemma][syn.pos].append((sense.id, d))
print(f"collect senses: {time.time() - t:.1f}s  words={n_words} lemmas={len(by_pos)}", flush=True)

t = time.time()
cands = candidate_pairs(set(by_pos))
print(f"candidate_pairs: {time.time() - t:.1f}s  pairs={len(cands)}", flush=True)

t = time.time()
accepted = 0
rejected = 0
n_gloss_calls = 0
for pair in cands:
    f1, f2 = sorted(pair)
    p1, p2 = by_pos[f1], by_pos[f2]
    hit = False
    for pos in set(p1) & set(p2):
        for s1, g1 in p1[pos]:
            for s2, g2 in p2[pos]:
                n_gloss_calls += 1
                if gloss_similarity(g1, g2) >= 0.34:
                    hit = True
    if hit:
        accepted += 1
    else:
        rejected += 1
print(
    f"gloss gate: {time.time() - t:.1f}s  accepted={accepted} rejected={rejected} "
    f"gloss_calls={n_gloss_calls}",
    flush=True,
)
print(f"TOTAL {time.time() - t0:.1f}s", flush=True)
