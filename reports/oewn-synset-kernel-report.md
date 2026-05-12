# Open English WordNet Synset-Kernel Report

- Lexicon: `oewn:2024`
- Graph type: experimental synset-level gloss graph
- Node policy: one node per defined synset
- Edge policy: add `defining_synset -> defined_synset` when a gloss lemma resolves uniquely or wins a strict overlap tie-break
- Sense resolution: prefer same-POS candidates; for ambiguous cases require positive overlap after removing the candidate lemma itself and require the best score to beat the runner-up
- Seed method: `exact-small-greedy`

## Summary

- Total synset nodes: `120630`
- Total directed edges: `223324`
- Kernel nodes: `10430` (8.65%)
- Kernel SCC count: `6335`
- Source SCCs inside kernel: `1599`
- Core size (union of source SCCs): `1710`
- Satellite size (kernel minus source-SCC Core): `8720`
- Fast cycle-hitting seed size: `1376` (1.14%; 13.19% of kernel)
- Residual cyclic SCCs after bounded heuristic: `0`

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

- Layer `0`: `1376` nodes
- Layer `1`: `2090` nodes
- Layer `2`: `1019` nodes
- Layer `3`: `626` nodes
- Layer `4`: `490` nodes
- Layer `5`: `354` nodes
- Layer `6`: `272` nodes
- Layer `7`: `264` nodes
- Layer `8`: `224` nodes
- Layer `9`: `225` nodes
- Layer `10`: `204` nodes
- Layer `11`: `170` nodes
- Layer `12`: `160` nodes
- Layer `13`: `143` nodes
- Layer `14`: `115` nodes
- Layer `15`: `109` nodes
- Layer `16`: `95` nodes
- Layer `17`: `100` nodes
- Layer `18`: `90` nodes
- Layer `19`: `78` nodes
- Layer `20`: `75` nodes
- Layer `21`: `83` nodes
- Layer `22`: `74` nodes
- Layer `23`: `71` nodes
- Layer `24`: `96` nodes
- Layer `25`: `80` nodes
- Layer `26`: `81` nodes
- Layer `27`: `68` nodes
- Layer `28`: `78` nodes
- Layer `29`: `69` nodes
- Layer `30`: `86` nodes
- Layer `31`: `99` nodes
- Layer `32`: `97` nodes
- Layer `33`: `74` nodes
- Layer `34`: `71` nodes
- Layer `35`: `56` nodes
- Layer `36`: `57` nodes
- Layer `37`: `38` nodes
- Layer `38`: `40` nodes
- Layer `39`: `34` nodes
- Layer `40`: `22` nodes
- Layer `41`: `25` nodes
- Layer `42`: `27` nodes
- Layer `43`: `21` nodes
- Layer `44`: `34` nodes
- Layer `45`: `34` nodes
- Layer `46`: `49` nodes
- Layer `47`: `46` nodes
- Layer `48`: `44` nodes
- Layer `49`: `40` nodes
- Layer `50`: `49` nodes
- Layer `51`: `48` nodes
- Layer `52`: `53` nodes
- Layer `53`: `45` nodes
- Layer `54`: `35` nodes
- Layer `55`: `24` nodes
- Layer `56`: `28` nodes
- Layer `57`: `22` nodes
- Layer `58`: `15` nodes
- Layer `59`: `10` nodes
- Layer `60`: `15` nodes
- Layer `61`: `12` nodes
- Layer `62`: `11` nodes
- Layer `63`: `15` nodes
- Layer `64`: `15` nodes
- Layer `65`: `16` nodes
- Layer `66`: `8` nodes
- Layer `67`: `13` nodes
- Layer `68`: `10` nodes
- Layer `69`: `4` nodes
- Layer `70`: `4` nodes
- Layer `71`: `4` nodes
- Layer `72`: `1` nodes

## Top Fast Seed Candidates

- `large [n] :: a garment size for a large person` (degree score `1947`)
- `yellow, yellowness [n] :: yellow color or pigment; the chromatic color resembling the hue of su...` (degree score `630`)
- `born, max_born [n] :: British nuclear physicist (born in Germany) honored for his contribut...` (degree score `626`)
- `park, commons, ... [n] :: a piece of open land for recreational use in an urban area` (degree score `624`)
- `over [n] :: (cricket) the division of play during which six balls are bowled at t...` (degree score `574`)
- `many [a] :: a quantifier that can be used with count nouns and is often preceded...` (degree score `570`)
- `more, thomas_more, ... [n] :: English statesman who opposed Henry VIII's divorce from Catherine of...` (degree score `551`)
- `characteristic [a] :: typical or distinctive` (degree score `467`)
- `located, placed, ... [s] :: situated in a particular spot or position` (degree score `449`)
- `things [n] :: any movable possession (especially articles of clothing)` (degree score `394`)
- `designed, intentional, ... [a] :: done or made or performed with purpose and intent` (degree score `359`)
- `sol, soh, ... [n] :: the syllable naming the fifth (dominant) note of any musical scale in...` (degree score `332`)
- `more, more_than [a] :: (comparative of ‘much’ used with mass nouns) a quantifier meaning gre...` (degree score `322`)
- `out [n] :: (baseball) a failure by a batter or runner to reach a base safely in...` (degree score `321`)
- `river [n] :: a large natural stream of water (larger than a creek)` (degree score `317`)
- `covered [a] :: overlaid or spread or topped with or enclosed within something; somet...` (degree score `309`)
- `homo, man, ... [n] :: any living or extinct member of the family Hominidae characterized by...` (degree score `274`)
- `narrow [n] :: a narrow strait connecting two bodies of water` (degree score `264`)
- `above [n] :: an earlier section of a written text` (degree score `262`)
- `derived [a] :: formed or developed from something else; not original` (degree score `247`)
- `relatively, comparatively [r] :: in a relative manner; by comparison to something else` (degree score `223`)
- `religious [n] :: a member of a religious order who is bound by vows of poverty and cha...` (degree score `216`)
- `drug [n] :: a substance that is used as a medicine or narcotic` (degree score `203`)
- `cognition, knowledge, ... [n] :: the psychological result of perception and learning and reasoning` (degree score `202`)
- `again, once_again, ... [r] :: anew` (degree score `202`)

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
- `characteristic [a] :: typical or distinctive`: `465`
- `formed [a] :: having or given a form or shape`: `459`
- `located, placed, ... [s] :: situated in a particular spot or position`: `448`
- `european [n] :: a native or inhabitant of Europe`: `444`
- `evergreen, evergreen_plant [n] :: a plant having foliage that persists and remains green throughout the...`: `441`
- `celebrated, famed, ... [s] :: widely known and esteemed`: `424`
- `comestible, edible, ... [n] :: any substance that can be used as food`: `406`
- `once, formerly, ... [r] :: at a previous time`: `392`
- `things [n] :: any movable possession (especially articles of clothing)`: `392`
- `given, presumption, ... [n] :: an assumption that is taken for granted`: `391`

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
- `cultural_studies [n] :: a field of theoretically, politically, and empirically engaged cultur...`: `14`
- `mononychus_olecranus [n] :: a turkey-sized long-legged fossil 75 million years old found in the G...`: `13`
- `byblos [n] :: an ancient Mediterranean seaport that was a thriving city state in Ph...`: `13`
- `maxwells_demon [n] :: an imaginary creature that controls a small hole in a partition that...`: `13`
- `varuna [n] :: in Vedism, god of the night sky who with his thousand eyes watches ov...`: `13`
- `kudzu, kudzu_vine, ... [n] :: fast-growing vine from eastern Asia having tuberous starchy roots and...`: `13`
- `xeroderma_pigmentosum [n] :: a rare genetic condition characterized by an eruption of exposed skin...`: `13`
- `potassium, k, ... [n] :: a light soft silver-white metallic element of the alkali metal group;...`: `13`
- `nephrite [n] :: an amphibole mineral consisting of calcium magnesium silicate in mono...`: `13`
- `microsensor [n] :: A submicrometer- to millimeter-size device that converts a nonelectri...`: `13`

## Annotation Coverage

- `frequency`: `0` / `120630` (0.00%)
- `concreteness`: `0` / `120630` (0.00%)
- `age_of_acquisition`: `0` / `120630` (0.00%)
- `imageability`: `0` / `120630` (0.00%)

## Caveats

- This is the experimental synset graph, not the paper-faithful baseline.
- Ambiguous gloss lemmas are only resolved when a strict overlap test separates one candidate from the others; unresolved ties are still skipped.
- The fast seed is a bounded SCC-based approximation, not an exact `MinSet` and not guaranteed to remove every residual cycle.
