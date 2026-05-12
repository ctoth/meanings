# Open English WordNet Lemma-Kernel Report

- Lexicon: `oewn:2024`
- Graph type: lemma-level proxy over Open English WordNet glosses
- Node policy: collapse all senses and parts of speech into normalized lemmas
- Edge policy: add `defining_lemma -> defined_lemma` when a gloss contains a matched lexicon lemma
- Gloss parsing: longest-match n-gram scan up to width 3 with tightened gloss-glue and taxonomy filtering

## Summary

- Total lemma nodes: `151622`
- Total directed edges: `851835`
- Kernel nodes: `18533` (12.22%)
- Kernel SCC count: `937`
- Source SCCs inside kernel: `68`
- Core size (largest kernel SCC): `17261`
- Satellite size (kernel minus largest SCC): `1272`
- Fast cycle-hitting seed size: `399` (0.26%; 2.15% of kernel)
- Residual cyclic SCCs after bounded heuristic: `1`

## Largest Kernel SCCs

- SCC `1`: `17261` nodes
- SCC `2`: `6` nodes
- SCC `3`: `6` nodes
- SCC `4`: `5` nodes
- SCC `5`: `5` nodes
- SCC `6`: `5` nodes
- SCC `7`: `4` nodes
- SCC `8`: `4` nodes
- SCC `9`: `4` nodes
- SCC `10`: `4` nodes

## Layer Histogram

- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.

## Top Fast Seed Candidates

- `act` (degree score `3037`)
- `make` (degree score `2452`)
- `form` (degree score `2357`)
- `part` (degree score `2011`)
- `quality` (degree score `1685`)
- `time` (degree score `1625`)
- `cause` (degree score `1503`)
- `place` (degree score `1255`)
- `orchid` (degree score `175`)
- `financial` (degree score `150`)
- `flattened` (degree score `145`)
- `snake` (degree score `141`)
- `crab` (degree score `90`)
- `repeatedly` (degree score `78`)
- `breaking` (degree score `65`)

## Highest Outdegree Lemmas

- `small`: `5705`
- `large`: `4117`
- `merica`: `3138`
- `act`: `2996`
- `make`: `2343`
- `white`: `2317`
- `form`: `2279`
- `can`: `2243`
- `tropical`: `2056`
- `part`: `1952`
- `tree`: `1840`
- `body`: `1812`
- `long`: `1791`
- `eastern`: `1747`
- `plant`: `1720`

## Highest Indegree Lemmas

- `break`: `183`
- `cut`: `183`
- `draw`: `147`
- `play`: `147`
- `run`: `146`
- `light`: `145`
- `check`: `138`
- `head`: `138`
- `line`: `135`
- `charge`: `132`
- `set`: `132`
- `call`: `131`
- `point`: `128`
- `hold`: `125`
- `take`: `123`

## Caveats

- This is a real lexicon but still a first-pass proxy, not the final sense-disambiguated graph from the papers.
- Polysemy is collapsed at the lemma level, so cycles and kernel sizes are only approximations to the meaning-level structures described by `Massé`, `Picard`, and `Vincent-Lamarre`.
- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.
