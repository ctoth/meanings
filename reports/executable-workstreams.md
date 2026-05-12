# Executable Workstreams: English Dictionary Kernel

**Date:** 2026-05-12

## North Star

Build a reproducible pipeline that extracts recursively sufficient semantic seeds from English dictionary graphs, validates those seeds against the dictionary-kernel literature, and prepares the same machinery for later cross-language comparison.

The core graph objects are:

- `Kernel`: recursively irreducible definitional subgraph after removing nodes that define nothing else in the remaining graph.
- `Core`: union of source SCCs inside the Kernel, following Picard/Vincent-Lamarre.
- `Satellites`: Kernel nodes outside the Core.
- `MinSet` / `MGS`: a feedback vertex set that hits every directed cycle so the rest can be unfolded recursively.
- `Loop ecology`: short cycles and SCC structure analyzed as semantic signal, following Levary.

## Workstream 0: Guardrails And Definitions

**Purpose:** Prevent drift away from the papers while implementation evolves.

**Inputs**

- `papers/Massé_2008_MeaningGroundedDictionaryDefinitions/notes.md`
- `papers/Picard_2013_HiddenStructureFunctionLexicon/notes.md`
- `papers/Vincent-Lamarre_2014_LatentStructureDictionaries/notes.md`
- `papers/Levary_2012_LoopsSelfReferenceDictionaries/notes.md`

**Tasks**

- Add `reports/graph-object-definitions.md`.
- Record exact implementation definitions for `Kernel`, `Core`, `Satellites`, `MinSet`, `source SCC`, `content word`, and `definitional edge`.
- Add a short "allowed deviations" section for our experimental synset graph.
- Add source references back to the paper notes.

**Commands**

```powershell
rg -n "Kernel|Core|Satellite|MinSet|feedback vertex|content words|function words|loops|source SCC" papers -g notes.md
```

**Outputs**

- `reports/graph-object-definitions.md`

**Acceptance Checks**

- Every graph object used in reports has a definition in the document.
- Any difference between the paper baseline and our experimental graph is named explicitly.
- No code change that alters `Kernel`, `Core`, `Satellites`, or `seed` semantics is made without updating this document.

## Workstream 1: Paper-Faithful WordNet Baseline

**Purpose:** Reproduce the closest practical Vincent-Lamarre-style WordNet graph so we have a reference point.

**Current State**

- We have `lemma` and `sense` graph modes.
- The current `sense` mode is experimental and uses strict overlap disambiguation.
- The current `lemma` mode collapses all senses and POS, which is not the paper baseline.

**Implementation Tasks**

- Add a new CLI graph mode: `paper-wordnet`.
- Create a builder that approximates Vincent-Lamarre's WordNet setup:
  - one node per normalized `lemma::pos`
  - choose one representative synset per `lemma::pos`, using the first/common WordNet ordering
  - parse definitions using content words only
  - map each defining word to `defining_lemma::target_pos` if available, otherwise to its first available POS only if unambiguous
  - keep the construction intentionally simpler than the synset resolver
- Preserve current `lemma` and `sense` modes for comparison.

**Likely Files**

- `src/meanings/wordnet_pipeline.py`
- `src/meanings/cli.py`
- `src/meanings/normalize.py`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --top 25
uv run python -m meanings.cli --graph-type paper-wordnet --top 25 --report reports/oewn-paper-wordnet-kernel-report.md --json reports/oewn-paper-wordnet-kernel-summary.json
```

**Outputs**

- `reports/oewn-paper-wordnet-kernel-report.md`
- `reports/oewn-paper-wordnet-kernel-summary.json`

**Acceptance Checks**

- Report includes graph policy and deviations from Vincent-Lamarre.
- Report includes reference values from Vincent-Lamarre's WordNet analysis:
  - WordNet total word meanings: `132,477`
  - Kernel: `9,802` (`12%`)
  - Core: `6,392`
  - Satellites: `3,410`
  - MinSet: `1,094`
- Our baseline numbers do not need to match exactly, but mismatches are explained by resource/version and modeling differences.

## Workstream 2: Experimental Synset Graph

**Purpose:** Keep the more semantically ambitious graph, but evaluate it against the baseline instead of treating it as the baseline.

**Current State**

- Default `sense` graph uses synset nodes.
- Gloss lemma resolution:
  - unique same-POS match
  - unique global match
  - strict overlap within same POS
  - strict overlap globally
  - unresolved ties skipped

**Implementation Tasks**

- Rename report text from "closer to the papers" to "experimental synset graph" where appropriate.
- Add explicit resolution-mode metadata to JSON.
- Add counts for accepted vs skipped ambiguous matches as percentages.
- Keep output stable at:
  - `reports/oewn-synset-kernel-report.md`
  - `reports/oewn-synset-kernel-summary.json`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type sense --top 25
```

**Outputs**

- Updated `reports/oewn-synset-kernel-report.md`
- Updated `reports/oewn-synset-kernel-summary.json`

**Acceptance Checks**

- Report clearly states this is not the paper-faithful baseline.
- JSON records all resolution stats.
- The graph remains reproducible with one command.

## Workstream 3: Side-By-Side Comparison Report

**Purpose:** Make model differences visible and measurable.

**Implementation Tasks**

- Add a comparison script or CLI subcommand that reads summary JSON files and writes a Markdown comparison.
- Compare:
  - node count
  - edge count
  - kernel count and fraction
  - SCC count
  - source SCC count
  - core count
  - satellite count
  - seed count and fraction
  - residual cyclic SCCs
  - layer depth, when available
- Include paper reference numbers as a third comparison column.

**Likely Files**

- `src/meanings/compare_reports.py` or `src/meanings/comparison.py`
- `src/meanings/cli.py`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --top 25
uv run python -m meanings.cli --graph-type sense --top 25
uv run python -m meanings.compare_reports `
  --left reports/oewn-paper-wordnet-kernel-summary.json `
  --right reports/oewn-synset-kernel-summary.json `
  --output reports/oewn-kernel-model-comparison.md
```

**Outputs**

- `reports/oewn-kernel-model-comparison.md`

**Acceptance Checks**

- The comparison can be regenerated without manual editing.
- It names which graph is the paper baseline and which is experimental.
- It flags any metric where the experimental model strongly diverges from the paper baseline.

## Workstream 4: Levary Loop Ecology

**Purpose:** Analyze cycles as structure before cutting them for seed extraction.

**Implementation Tasks**

- Add SCC and short-loop analysis over any graph mode.
- Compute:
  - SCC size histogram
  - number of cyclic SCCs
  - top largest SCCs
  - short directed cycles up to length 2, 3, and optionally 4
  - seed-node overlap with short cycles
- Keep the first version bounded and deterministic.

**Likely Files**

- `src/meanings/loop_analysis.py`
- `src/meanings/graph_analysis.py`
- `src/meanings/wordnet_pipeline.py`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --top 25
uv run python -m meanings.loop_analysis `
  --summary reports/oewn-paper-wordnet-kernel-summary.json `
  --output reports/oewn-paper-wordnet-loop-ecology.md
```

**Outputs**

- `reports/oewn-paper-wordnet-loop-ecology.md`
- `reports/oewn-synset-loop-ecology.md`

**Acceptance Checks**

- The report distinguishes small meaningful loops from giant SCC structure.
- Seed overlap with loops is measured.
- No claim is made that loops are merely errors.

## Workstream 5: Candidate MinSet Extraction

**Purpose:** Replace the current bounded seed heuristic with named candidate-MinSet methods.

**Current State**

- `bounded_cycle_hitting_set()` removes one high-degree node per cyclic SCC per pass.
- It is useful for a first pass, but it is not a true MinSet solver.

**Implementation Tasks**

- Keep the bounded heuristic as `seed_method=bounded-scc`.
- Add exact search for small SCCs.
- Add greedy feedback-vertex heuristic for large SCCs.
- Record `seed_method`, limits, residual cycles, and runtime in JSON.
- Produce at least three candidate seeds for the paper baseline:
  - fast bounded SCC seed
  - exact-small-plus-greedy seed
  - weighted experimental seed after annotation exists

**Likely Files**

- `src/meanings/graph_analysis.py`
- `src/meanings/minset.py`
- `src/meanings/wordnet_pipeline.py`
- `src/meanings/cli.py`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --seed-method bounded-scc --top 25
uv run python -m meanings.cli --graph-type paper-wordnet --seed-method exact-small-greedy --top 25
```

**Outputs**

- JSON includes `seed_method`, `seed_node_count`, `residual_cyclic_scc_count`, and runtime metadata.
- Markdown reports list top seed candidates by method.

**Acceptance Checks**

- Exact solver is only used inside documented size limits.
- Large SCC fallback is deterministic.
- Residual cyclic SCC count is reported honestly.

## Workstream 6: Psycholinguistic Annotation

**Purpose:** Interpret graph structure using the variables the papers actually use instead of eyeballing hubs.

**Implementation Tasks**

- Add annotation schema for:
  - POS
  - frequency
  - concreteness
  - age of acquisition
  - imageability, if available
- Start with local optional CSV inputs rather than hard-coding a web dependency.
- Add coverage reporting for each variable.
- Summarize annotations by Rest, Kernel, Core, Satellites, and seed.

**Likely Files**

- `src/meanings/annotations.py`
- `src/meanings/wordnet_pipeline.py`
- `reports/annotation-sources.md`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --annotations data/psycholinguistic/*.csv --top 25
```

**Outputs**

- Annotation coverage in JSON.
- Component-level annotation table in Markdown.
- `reports/annotation-sources.md`

**Acceptance Checks**

- Missing annotation coverage is reported, not hidden.
- No psycholinguistic value is invented.
- Any weighted seed objective records its weights and source variables.

## Workstream 7: Recursive Unfolding

**Purpose:** Turn a seed into the "build outward" object: a layered definitional hierarchy.

**Implementation Tasks**

- Once a seed fully acyclicizes the graph, compute layers for all definable nodes.
- If residual cycles remain, report the blocked SCCs.
- Add export formats:
  - Markdown layer histogram
  - JSON node-to-layer map
  - optional CSV for inspection

**Likely Files**

- `src/meanings/graph_analysis.py`
- `src/meanings/layers.py`
- `src/meanings/wordnet_pipeline.py`

**Commands**

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --seed-method exact-small-greedy --export-layers reports/oewn-paper-wordnet-layers.json
```

**Outputs**

- `reports/oewn-paper-wordnet-layers.json`
- Layer histogram in the graph report.

**Acceptance Checks**

- If residual cycles are zero, every non-seed kernel node has a layer.
- If residual cycles are nonzero, the report identifies how many SCCs block full layering.

## Workstream 8: Cross-Language Readiness

**Purpose:** Keep the English implementation shaped so multilingual comparison is possible later.

**Implementation Tasks**

- Avoid English-only assumptions in core graph algorithms.
- Keep lexicon-specific parsing in adapters.
- Add a `LexicalGraphBuild` protocol-like structure with:
  - `nodes`
  - `adjacency`
  - `labels`
  - `metadata`
  - `language`
  - `resource_id`
- Document how Open Multilingual WordNet or LLM-generated WordNets would plug in.

**Likely Files**

- `src/meanings/wordnet_pipeline.py`
- `src/meanings/lexical_graph.py`
- `reports/cross-language-readiness.md`

**Commands**

```powershell
uv run python -m meanings.cli --lexicon oewn:2024 --graph-type paper-wordnet --top 25
```

**Outputs**

- `reports/cross-language-readiness.md`
- Shared graph-build data structure usable by future adapters.

**Acceptance Checks**

- Core graph algorithms do not depend on OEWN-specific classes.
- Resource-specific assumptions are documented in the adapter layer.

## Recommended Execution Order

1. Workstream 0: lock definitions.
2. Workstream 1: build paper-faithful WordNet baseline.
3. Workstream 3: generate comparison report.
4. Workstream 4: add loop ecology.
5. Workstream 5: improve MinSet extraction.
6. Workstream 6: add psycholinguistic annotations.
7. Workstream 7: export recursive unfolding.
8. Workstream 8: prepare multilingual adapters.

Workstream 2 should be maintained in parallel, but not allowed to define the baseline.

## Immediate Next Commit-Sized Slice

Implement Workstream 0 and the first half of Workstream 1:

- Add `reports/graph-object-definitions.md`.
- Add `paper-wordnet` as a CLI graph type.
- Build nodes as `lemma::pos`.
- Use one representative synset per `lemma::pos`.
- Generate `reports/oewn-paper-wordnet-kernel-report.md`.

This gives us the measuring stick before we improve anything else.
