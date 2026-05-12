# Open English WordNet Synset-Kernel Report

- Lexicon: `oewn:2024`
- Graph type: synset-level gloss graph
- Node policy: one node per defined synset
- Edge policy: add `defining_synset -> defined_synset` when a gloss lemma resolves uniquely or wins a strict overlap tie-break
- Sense resolution: prefer same-POS candidates; for ambiguous cases require positive overlap after removing the candidate lemma itself and require the best score to beat the runner-up

## Summary

- Total synset nodes: `120630`
- Total directed edges: `223324`
- Kernel nodes: `10430` (8.65%)
- Kernel SCC count: `6335`
- Source SCCs inside kernel: `1599`
- Core size (largest kernel SCC): `2769`
- Satellite size (kernel minus largest SCC): `7661`
- Fast cycle-hitting seed size: `1122` (0.93%; 10.76% of kernel)
- Residual cyclic SCCs after bounded heuristic: `1`

## Resolution Stats

- Candidate gloss matches: `509303`
- Resolved by unique same-POS match: `119944`
- Resolved by unique global match: `50818`
- Resolved by overlap within same POS: `46313`
- Resolved by overlap across POS: `11765`
- Ambiguous matches skipped: `278965`
- Self-only matches skipped: `1498`
- Unresolved matches skipped: `0`

## Largest Kernel SCCs

- SCC `1`: `2769` nodes
- SCC `2`: `15` nodes
- SCC `3`: `11` nodes
- SCC `4`: `10` nodes
- SCC `5`: `10` nodes
- SCC `6`: `8` nodes
- SCC `7`: `8` nodes
- SCC `8`: `7` nodes
- SCC `9`: `7` nodes
- SCC `10`: `6` nodes

## Layer Histogram

- Layering skipped because the bounded seed heuristic did not fully acyclicize the kernel.

## Top Fast Seed Candidates

- `large [n] :: a garment size for a large person` (degree score `1947`)
- `many [a] :: a quantifier that can be used with count nouns and is often preceded...` (degree score `570`)
- `more, thomas_more, ... [n] :: English statesman who opposed Henry VIII's divorce from Catherine of...` (degree score `551`)
- `located, placed, ... [s] :: situated in a particular spot or position` (degree score `449`)
- `things [n] :: any movable possession (especially articles of clothing)` (degree score `394`)
- `homo, man, ... [n] :: any living or extinct member of the family Hominidae characterized by...` (degree score `274`)
- `above [n] :: an earlier section of a written text` (degree score `262`)
- `sociable, social, ... [n] :: a party of people assembled to promote sociability and communal activity` (degree score `215`)
- `metallic_element, metal [n] :: any of several chemical elements that are usually shiny solids that c...` (degree score `110`)
- `tree [n] :: a tall perennial woody plant having a main trunk and branches forming...` (degree score `72`)
- `flies [n] :: (theater) the space over the stage (out of view of the audience) used...` (degree score `71`)
- `breathing, external_respiration, ... [n] :: the bodily process of inhalation and exhalation; the process of takin...` (degree score `64`)
- `declared, stated [s] :: declared as fact; explicitly stated` (degree score `53`)
- `detailed, elaborate, ... [s] :: developed or executed with care and in minute detail` (degree score `47`)
- `earlier, before [r] :: earlier in time; previously` (degree score `45`)

## Highest Outdegree Synsets

- `large [n] :: a garment size for a large person`: `1944`
- `yellow, yellowness [n] :: yellow color or pigment; the chromatic color resembling the hue of su...`: `625`
- `perennial [n] :: (botany) a plant lasting for three seasons or more`: `624`
- `park, commons, ... [n] :: a piece of open land for recreational use in an urban area`: `622`
- `born, max_born [n] :: British nuclear physicist (born in Germany) honored for his contribut...`: `621`
- `found [n] :: food and lodging provided in addition to money`: `616`
- `northern [n] :: a dialect of Middle English that developed into Scottish Lallans`: `591`
- `over [n] :: (cricket) the division of play during which six balls are bowled at t...`: `571`
- `many [a] :: a quantifier that can be used with count nouns and is often preceded...`: `565`
- `central, telephone_exchange, ... [n] :: a workplace that serves as a telecommunications facility where lines...`: `553`
- `peer, equal, ... [n] :: a person who is of equal standing with another in a group`: `547`
- `more, thomas_more, ... [n] :: English statesman who opposed Henry VIII's divorce from Catherine of...`: `544`
- `spoken [a] :: uttered through the medium of speech or characterized by speech; some...`: `517`
- `parts [n] :: the local environment`: `505`
- `shrub, bush [n] :: a low woody perennial plant usually having several major stems`: `495`

## Highest Indegree Synsets

- `arbovirus, arborvirus [n] :: a large heterogeneous group of RNA viruses divisible into groups on t...`: `17`
- `generic, generic_wine [n] :: wine that does not meet the minimum qualifications and standards for...`: `17`
- `hanseatic_league [n] :: a commercial and defensive confederation of free cities in northern G...`: `16`
- `placebo_effect [n] :: any effect that seems to be a consequence of administering a placebo;...`: `16`
- `winsorized_mean [n] :: a statistical measure of central tendency, much like the mean and med...`: `16`
- `palestine_liberation_organization, plo [n] :: a political movement uniting Palestinian Arabs in an effort to create...`: `15`
- `pyramiding [n] :: a fraudulent business practice involving some form of pyramid scheme...`: `14`
- `fentanyl, sublimaze [n] :: trade names of a narcotic analgesic that can be inhaled and that acts...`: `14`
- `phenolphthalein [n] :: a laxative used in many preparations under various trade names; also...`: `14`
- `greshams_law [n] :: (economics) the principle that when two kinds of money having the sam...`: `14`
- `craig_venter, ventner, ... [n] :: United States geneticist who published the complete base sequences fo...`: `14`
- `welwitschia, welwitschia_mirabilis [n] :: curious plant of arid regions of southwestern Africa having a yard-hi...`: `14`
- `siskiyou_lewisia, lewisia_cotyledon [n] :: evergreen perennial having a dense basal rosette of long spatula-shap...`: `14`
- `selenium, se, ... [n] :: a toxic nonmetallic element related to sulfur and tellurium; occurs i...`: `14`
- `vx_gas [n] :: a highly lethal nerve agent used in chemical warfare; a toxic liquid...`: `14`

## Caveats

- This is closer to the graph described in the papers, but it still uses a heuristic rather than full sense disambiguation.
- Ambiguous gloss lemmas are only resolved when a strict overlap test separates one candidate from the others; unresolved ties are still skipped.
- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.
