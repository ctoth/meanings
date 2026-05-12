# Open English WordNet Synset-Kernel Report

- Lexicon: `oewn:2024`
- Graph type: synset-level gloss graph
- Node policy: one node per defined synset
- Edge policy: add `defining_synset -> defined_synset` only when a gloss lemma resolves to a unique source synset
- Sense resolution: prefer unique matches within the target synset POS; otherwise allow globally monosemous matches

## Summary

- Total synset nodes: `120630`
- Total directed edges: `497227`
- Kernel nodes: `19508` (16.17%)
- Kernel SCC count: `4842`
- Source SCCs inside kernel: `187`
- Core size (largest kernel SCC): `13442`
- Satellite size (kernel minus largest SCC): `6066`
- Fast cycle-hitting seed size: `1061` (0.88%; 5.44% of kernel)
- Residual cyclic SCCs after bounded heuristic: `3`

## Resolution Stats

- Candidate gloss matches: `509303`
- Resolved by unique same-POS match: `119944`
- Resolved by unique global match: `50818`
- Resolved by overlap within same POS: `233394`
- Resolved by overlap across POS: `103649`
- Ambiguous matches skipped: `0`
- Self-only matches skipped: `1498`
- Unresolved matches skipped: `0`

## Largest Kernel SCCs

- SCC `1`: `13442` nodes
- SCC `2`: `11` nodes
- SCC `3`: `10` nodes
- SCC `4`: `10` nodes
- SCC `5`: `6` nodes
- SCC `6`: `5` nodes
- SCC `7`: `5` nodes
- SCC `8`: `5` nodes
- SCC `9`: `5` nodes
- SCC `10`: `4` nodes

## Layer Histogram

- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.

## Top Fast Seed Candidates

- `act [n] :: a manifestation of insincerity` (degree score `1559`)
- `can, canful [n] :: the quantity contained in a can` (degree score `1193`)
- `piece, part [n] :: an item that is an instance of some type` (degree score `1027`)
- `make [v] :: be suitable for` (degree score `882`)
- `quality [n] :: high social status` (degree score `843`)
- `body [n] :: the central message of a communication` (degree score `759`)
- `time [n] :: a suitable moment` (degree score `598`)
- `sealed, certain [a] :: established irrevocably` (degree score `516`)
- `inside, within [r] :: on the inside` (degree score `303`)
- `cheese [n] :: a solid food prepared from the pressed curd of milk` (degree score `82`)
- `flies [n] :: (theater) the space over the stage (out of view of the audience) used...` (degree score `77`)
- `tree [n] :: a tall perennial woody plant having a main trunk and branches forming...` (degree score `74`)
- `occurrence [n] :: an instance of something occurring` (degree score `70`)
- `violin, fiddle [n] :: bowed stringed instrument that is the highest member of the violin fa...` (degree score `32`)
- `zeus [n] :: (Greek mythology) the supreme god of ancient Greek mythology; son of...` (degree score `31`)

## Highest Outdegree Synsets

- `small [n] :: a garment size for a small person`: `2742`
- `large [n] :: a garment size for a large person`: `1965`
- `act [n] :: a manifestation of insincerity`: `1557`
- `can, canful [n] :: the quantity contained in a can`: `1190`
- `piece, part [n] :: an item that is an instance of some type`: `1025`
- `tropical [a] :: of or relating to the tropics, or either tropic`: `913`
- `make [v] :: be suitable for`: `881`
- `versatile, various [s] :: having great diversity or variety`: `847`
- `quality [n] :: high social status`: `841`
- `form [n] :: a particular mode in which something is manifested`: `833`
- `long [r] :: for an extended distance`: `831`
- `through [r] :: to completion`: `831`
- `plant [n] :: something planted secretly for discovery by another`: `787`
- `body [n] :: the central message of a communication`: `756`
- `several [s] :: distinct and individual`: `749`

## Highest Indegree Synsets

- `microsensor [n] :: A submicrometer- to millimeter-size device that converts a nonelectri...`: `27`
- `myotonic_muscular_dystrophy, myotonic_dystrophy, ... [n] :: a severe form of muscular dystrophy marked by generalized weakness an...`: `26`
- `mononychus_olecranus [n] :: a turkey-sized long-legged fossil 75 million years old found in the G...`: `25`
- `maxwells_demon [n] :: an imaginary creature that controls a small hole in a partition that...`: `25`
- `welwitschia, welwitschia_mirabilis [n] :: curious plant of arid regions of southwestern Africa having a yard-hi...`: `25`
- `michigan, chicago, ... [n] :: a gambling card game in which chips are placed on the ace and king an...`: `23`
- `arbovirus, arborvirus [n] :: a large heterogeneous group of RNA viruses divisible into groups on t...`: `23`
- `temple_in_jerusalem, temple_of_jerusalem, ... [n] :: any of three successive temples in Jerusalem that served as the prima...`: `23`
- `generic, generic_wine [n] :: wine that does not meet the minimum qualifications and standards for...`: `23`
- `punks [n] :: a youth subculture closely associated with punk rock music in the lat...`: `23`
- `kuru [n] :: a progressive disease of the central nervous system marked by increas...`: `23`
- `becker_muscular_dystrophy [n] :: a form of muscular dystrophy that sets in in adolescence or adulthood...`: `23`
- `neobehaviorism [n] :: a school of psychology based on the general principles of behaviorism...`: `23`
- `liver [n] :: large and complicated reddish-brown glandular organ located in the up...`: `22`
- `hooke, robert_hooke [n] :: English scientist who formulated the law of elasticity and proposed a...`: `22`

## Caveats

- This is closer to the graph described in the papers, but it still uses a conservative heuristic rather than full sense disambiguation.
- Ambiguous gloss lemmas are skipped rather than forced, so this graph sacrifices recall for cleaner semantic edges.
- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.
