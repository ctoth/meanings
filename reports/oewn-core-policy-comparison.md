# OEWN Kernel Model Comparison

- Left: `paper_wordnet` from `reports\oewn-paper-wordnet-kernel-summary.json`
- Right: `paper_wordnet` from `reports\oewn-paper-wordnet-largest-core-summary.json`
- Reference: `Vincent-Lamarre WordNet` values from the paper notes

| Metric | Paper Reference | Left | Right |
|---|---:|---:|---:|
| `node_count` | 132477 | 160010 | 160010 |
| `edge_count` | - | 677823 | 677823 |
| `kernel_node_count` | 9802 | 12853 | 12853 |
| `kernel_fraction` | 0.1200 | 0.0803 | 0.0803 |
| `kernel_scc_count` | - | 3841 | 3841 |
| `source_scc_count` | - | 286 | 286 |
| `core_node_count` | 6392 | 288 | 8138 |
| `satellite_node_count` | 3410 | 12565 | 4715 |
| `seed_node_count` | 1094 | 2370 | 2370 |
| `seed_fraction_total` | - | 0.0148 | 0.0148 |
| `seed_fraction_kernel` | - | 0.1844 | 0.1844 |
| `residual_cyclic_scc_count` | - | 0 | 0 |

## Notes

- The paper reference is not expected to match exactly because OEWN 2024 and our builders differ from the WordNet resource and preprocessing used in Vincent-Lamarre.
- Large deviations are interpretation prompts, not automatic failures.
- The paper-faithful baseline is the measuring stick; the synset graph is experimental.
