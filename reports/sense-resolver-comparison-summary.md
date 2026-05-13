# Sense Resolver Comparison

Edge-budget-controlled comparison of the audit-baseline resolver vs
the IC-fallback resolver. See `reports/sense-resolver-fix.md` for the
full writeup.

## Side-by-side

| Metric | baseline | ic_fallback | lemma-level |
|---|---|---|---|
| nodes | 212478 | 212478 | 160,010 |
| edges | 418094 | 910355 | n/a |
| edges/node | 1.97 | 4.28 | 4.24 |
| self-loops | 0 | 0 | 3413 |
| Kernel | 12142 | 20744 | 18151 |
| Core | 1939 | 154 | 510 |
| Satellites | 10203 | 20590 | 17,641 |
| seed | 1582 | 3040 | 5,044 |
| residual cyclic SCCs | 0 | 0 | 0 |

## Genus victims (high-polysemy words from audit finding #2)

Format: `senses_in_kernel / total_senses (total_in_degree)`

| Lemma | baseline | ic_fallback |
|---|---|---|
| `line` | 14/36 (57) | 20/36 (143) |
| `head` | 8/42 (70) | 10/42 (159) |
| `break` | 3/75 (85) | 6/75 (236) |
| `take` | 2/44 (57) | 12/44 (146) |
| `make` | 12/51 (50) | 22/51 (132) |
| `set` | 5/45 (62) | 11/45 (160) |
| `run` | 3/57 (62) | 6/57 (193) |
| `point` | 9/40 (63) | 12/40 (151) |

## Verdict

- **(ii)** — sense-Kernel with IC-fallback (20744) is about the same size as the lemma-Kernel (18151, 14% delta). The original sense-level Kernel shrink 12142 vs 18151 was substantially dropped edges, not artifact dissolution: when the resolver keeps the genus-word edges, the cyclic core comes back. The audit's charge survives.

## IC-projection P1 vs P2

- P1 (collapse IC -> one node, then FVS): seed = `4122`
- P2 (sense-graph FVS, then restrict to one rep per IC): seed = `2739`
- Delta: `-1383`
- IC ids in P1-only: `200`
- IC ids in P2-only: `200`
- IC ids in both: `200`

Recommendation: P2 (restrict sense-graph seed at export). P2's seed is tighter; the sense-graph FVS has access to the full edge structure and the per-IC representative is then the highest-in-degree-cited sense, which is a more informative anchor than 'this IC was in the FVS' would be.

## Self-loop prediction check

- baseline self-loops: `0` (vs lemma-level `3413`)
- ic_fallback self-loops: `0` (vs lemma-level `3413`)

The synthesis section 3 prediction was 'near-zero on the sense graph'.
Whether that holds after the resolver fix is shown above.
