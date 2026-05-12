# Open English WordNet Lemma-Kernel Report

- Lexicon: `oewn:2024`
- Graph type: lemma-level proxy over Open English WordNet glosses
- Node policy: collapse all senses and parts of speech into normalized lemmas
- Edge policy: add `defining_lemma -> defined_lemma` when a gloss contains a matched lexicon lemma
- Gloss parsing: longest-match n-gram scan up to width 3 with tightened gloss-glue and taxonomy filtering

## Summary

- Total lemma nodes: `151622`
- Total directed edges: `938039`
- Kernel nodes: `23133` (15.26%)
- Kernel SCC count: `2442`
- Source SCCs inside kernel: `115`
- Core size (largest kernel SCC): `19667`
- Satellite size (kernel minus largest SCC): `3466`
- Fast cycle-hitting seed size: `1119` (0.74%; 4.84% of kernel)
- Residual cyclic SCCs after bounded heuristic: `1`

## Largest Kernel SCCs

- SCC `1`: `19667` nodes
- SCC `2`: `15` nodes
- SCC `3`: `6` nodes
- SCC `4`: `6` nodes
- SCC `5`: `6` nodes
- SCC `6`: `6` nodes
- SCC `7`: `6` nodes
- SCC `8`: `6` nodes
- SCC `9`: `5` nodes
- SCC `10`: `5` nodes

## Layer Histogram

- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.

## Top Fast Seed Candidates

- `act` (degree score `3040`)
- `make` (degree score `2452`)
- `form` (degree score `2357`)
- `part` (degree score `2011`)
- `body` (degree score `1853`)
- `time` (degree score `1624`)
- `cause` (degree score `1504`)
- `place` (degree score `1255`)
- `financial` (degree score `150`)
- `flattened` (degree score `145`)
- `antibiotic` (degree score `99`)
- `snap` (degree score `86`)
- `repeatedly` (degree score `78`)
- `clustered` (degree score `71`)
- `breaking` (degree score `65`)

## Highest Outdegree Lemmas

- `small`: `5706`
- `united`: `4850`
- `large`: `4119`
- `north`: `3859`
- `america`: `3134`
- `act`: `2999`
- `american`: `2983`
- `make`: `2343`
- `white`: `2341`
- `form`: `2279`
- `can`: `2243`
- `tropical`: `2056`
- `part`: `1952`
- `tree`: `1842`
- `body`: `1812`

## Highest Indegree Lemmas

- `break`: `183`
- `cut`: `183`
- `draw`: `147`
- `play`: `147`
- `run`: `147`
- `light`: `146`
- `check`: `138`
- `head`: `138`
- `line`: `135`
- `set`: `133`
- `charge`: `132`
- `call`: `131`
- `point`: `130`
- `hold`: `125`
- `pass`: `123`

## Caveats

- This is a real lexicon but still a first-pass proxy, not the final sense-disambiguated graph from the papers.
- Polysemy is collapsed at the lemma level, so cycles and kernel sizes are only approximations to the meaning-level structures described by `Massé`, `Picard`, and `Vincent-Lamarre`.
- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.
