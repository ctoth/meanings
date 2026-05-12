# meanings

Tooling and a research dossier for one question: **how small is the non-circular core of a dictionary?**

A dictionary defines words with other words. Follow the references long enough and you hit cycles — words that are, ultimately, defined in terms of themselves. The set of words you'd have to already know (ground from outside the dictionary) before everything else becomes reachable is, formally, a *feedback vertex set* of the definition graph. Massé (2008), Picard (2013), and Vincent-Lamarre et al. (2014) turned this into a concrete graph decomposition — `Rest → Kernel → Core → Satellites`, plus many possible minimal grounding sets (`MinSets`) — and showed those layers correlate with word frequency, age of acquisition, and concreteness.

This repo applies that machinery to [Open English WordNet](https://github.com/globalwordnet/english-wordnet) (via the [`wn`](https://pypi.org/project/wn/) library), builds the gloss graph, extracts the kernel/core/satellite layers and candidate seeds, and writes comparison reports against the published WordNet numbers.

## Layout

- `src/meanings/` — the pipeline.
  - `wordnet_pipeline.py` — build the definition graph from a WordNet lexicon (lemma-level, sense-level, or "paper-faithful" reconstruction), run the kernel analysis, emit Markdown + JSON reports.
  - `graph_analysis.py` — SCCs, induced subgraphs, kernel extraction, seed (feedback-vertex-set) candidates.
  - `loop_analysis.py` — short-cycle "loop ecology" inspection (per Levary 2012: cycles are signal, not just noise to cut).
  - `core_diagnostics.py`, `compare_reports.py` — diff our layers against paper reference values; investigate Core/Kernel mismatches.
  - `annotations.py` — overlay psycholinguistic CSVs (frequency, AoA, concreteness) onto graph layers.
  - `normalize.py`, `lexical_graph.py` — lemma normalization, tokenization, graph build types.
- `scripts/inspect_wn.py` — poke at the `wn` API.
- `papers/` — the literature this is built on: per-paper `notes.md` / `abstract.md` / `description.md` / `citations.md`, plus `papers/index.md`. The lineage runs Masterman 1961 → Harnad 1990 → Massé 2008 / Picard 2013 / Vincent-Lamarre 2014 → LGDE 2025 / OpenGloss 2025. (Source PDFs are gitignored.)
- `reports/` — generated kernel reports, model comparisons, loop-ecology writeups, cross-language readiness notes, and synthesis docs (`synthesis-minimal-core-to-expansion.md` is the orientation piece).

## Usage

```bash
uv sync
uv run python -m meanings.cli --lexicon oewn:2024 --graph-type sense
# writes reports/oewn-synset-kernel-report.md and reports/oewn-synset-kernel-summary.json
```

Options of note: `--graph-type {lemma,sense,paper-wordnet}`, `--seed-method {bounded-scc,exact-small-greedy}`, `--core-policy {source-union,largest-scc}`, `--annotations a.csv b.csv`, `--export-layers layers.json`. You'll need the WordNet data downloaded first (`python -m wn download oewn:2024`).

## Status

Research scaffolding, not a product. The "paper-faithful" graph is the measuring stick; the synset graph is experimental. Large deviations from the published Vincent-Lamarre numbers are prompts for interpretation, not automatic failures — OEWN 2024 and these builders differ from the resource and preprocessing in the original work.
