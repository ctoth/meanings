# Open English WordNet Paper-Baseline Kernel Report

- Lexicon: `oewn:2024`
- Graph type: paper-faithful WordNet approximation
- Node policy: one normalized `lemma::pos` node with the first available representative synset definition
- Edge policy: content-word `defining_lemma::pos -> defined_lemma::pos`, preferring same POS and otherwise unambiguous POS
- Seed method: `exact-small-greedy`
- Core policy: `source-union`

## Summary

- Total lemma/POS nodes: `160010`
- Total directed edges: `677823`
- Kernel nodes: `12853` (8.03%)
- Kernel SCC count: `3841`
- Source SCCs inside kernel: `286`
- Core size (union of source SCCs): `288`
- Satellite size (kernel minus source-SCC Core): `12565`
- Candidate seed size: `2370` (1.48%; 18.44% of kernel)
- Residual cyclic SCCs after seed method: `0`
- Candidate seed exact: `no`
- Candidate seed lower bound: `unknown`
- Candidate seed upper bound: `2370`
- Solver SCCs exact / heuristic: `1380` / `872`
- Solver runtime: `75.768` seconds
- Candidate seed id: `exact-small-greedy:n2370:r0`

## Vincent-Lamarre WordNet Reference

- Word meanings: `132477`
- Kernel: `9802` (12%)
- Core: `6392`
- Satellites: `3410`
- MinSet: `1094`

## Resolution Stats

- `definition_count`: `160010`
- `candidate_matches`: `719836`
- `resolved_same_pos`: `512641`
- `resolved_unambiguous_pos`: `175554`
- `ambiguous_skipped`: `31641`
- `missing_skipped`: `0`

## Largest Kernel SCCs

- SCC `1`: `8138` nodes
- SCC `2`: `11` nodes
- SCC `3`: `10` nodes
- SCC `4`: `6` nodes
- SCC `5`: `6` nodes
- SCC `6`: `6` nodes
- SCC `7`: `5` nodes
- SCC `8`: `5` nodes
- SCC `9`: `5` nodes
- SCC `10`: `5` nodes

## Layer Histogram

- Layer `0`: `2370` nodes
- Layer `1`: `1614` nodes
- Layer `2`: `1009` nodes
- Layer `3`: `768` nodes
- Layer `4`: `573` nodes
- Layer `5`: `499` nodes
- Layer `6`: `413` nodes
- Layer `7`: `342` nodes
- Layer `8`: `276` nodes
- Layer `9`: `265` nodes
- Layer `10`: `241` nodes
- Layer `11`: `208` nodes
- Layer `12`: `195` nodes
- Layer `13`: `161` nodes
- Layer `14`: `166` nodes
- Layer `15`: `147` nodes
- Layer `16`: `136` nodes
- Layer `17`: `135` nodes
- Layer `18`: `112` nodes
- Layer `19`: `120` nodes
- Layer `20`: `109` nodes
- Layer `21`: `110` nodes
- Layer `22`: `113` nodes
- Layer `23`: `103` nodes
- Layer `24`: `104` nodes
- Layer `25`: `90` nodes
- Layer `26`: `96` nodes
- Layer `27`: `91` nodes
- Layer `28`: `85` nodes
- Layer `29`: `74` nodes
- Layer `30`: `72` nodes
- Layer `31`: `81` nodes
- Layer `32`: `65` nodes
- Layer `33`: `88` nodes
- Layer `34`: `91` nodes
- Layer `35`: `91` nodes
- Layer `36`: `87` nodes
- Layer `37`: `80` nodes
- Layer `38`: `96` nodes
- Layer `39`: `130` nodes
- Layer `40`: `128` nodes
- Layer `41`: `115` nodes
- Layer `42`: `97` nodes
- Layer `43`: `87` nodes
- Layer `44`: `43` nodes
- Layer `45`: `30` nodes
- Layer `46`: `29` nodes
- Layer `47`: `41` nodes
- Layer `48`: `58` nodes
- Layer `49`: `81` nodes
- Layer `50`: `66` nodes
- Layer `51`: `52` nodes
- Layer `52`: `56` nodes
- Layer `53`: `50` nodes
- Layer `54`: `52` nodes
- Layer `55`: `52` nodes
- Layer `56`: `45` nodes
- Layer `57`: `41` nodes
- Layer `58`: `38` nodes
- Layer `59`: `33` nodes
- Layer `60`: `24` nodes
- Layer `61`: `17` nodes
- Layer `62`: `8` nodes
- Layer `63`: `3` nodes
- Layer `64`: `1` nodes

## Top Candidate Seed Nodes

- `small [n] :: the slender part of the back` (degree score `4881`)
- `large [n] :: a garment size for a large person` (degree score `3500`)
- `white [n] :: a person of European descent with a light-skinned or pale complexion` (degree score `2079`)
- `can [n] :: airtight sealed metal container for food or drink or paint etc.` (degree score `1795`)
- `born [n] :: British nuclear physicist (born in Germany) honored for his contribut...` (degree score `1546`)
- `plant [n] :: buildings for carrying on industrial labor` (degree score `1504`)
- `form [n] :: the phonological or orthographic sound or appearance of a word that c...` (degree score `1486`)
- `yellow [n] :: yellow color or pigment; the chromatic color resembling the hue of su...` (degree score `1451`)
- `act [n] :: a legal document codifying the result of deliberations of a committee...` (degree score `1446`)
- `part [n] :: something determined in relation to something that includes it` (degree score `1354`)
- `common [n] :: a piece of open land for recreational use in an urban area` (degree score `1299`)
- `english [n] :: an Indo-European language belonging to the West Germanic branch; the...` (degree score `1265`)
- `body [n] :: the entire physical structure of an organism (an animal, plant, or hu...` (degree score `1260`)
- `city [n] :: a large and densely populated urban area; may include several indepen...` (degree score `1256`)
- `eastern [a] :: lying toward or situated in the east` (degree score `1252`)
- `northern [n] :: a dialect of Middle English that developed into Scottish Lallans` (degree score `1110`)
- `various [a] :: of many different kinds purposefully arranged but lacking any uniformity` (degree score `1095`)
- `water [n] :: binary compound that occurs at room temperature as a clear colorless...` (degree score `1095`)
- `found [n] :: food and lodging provided in addition to money` (degree score `1079`)
- `southern [a] :: in or characteristic of a region of the United States south of (appro...` (degree score `1076`)
- `first [n] :: the first or highest in an ordering or series` (degree score `1068`)
- `several [a] :: (used with count nouns) of an indefinite number more than 2 or 3 but...` (degree score `1068`)
- `make [v] :: engage in` (degree score `1043`)
- `quality [n] :: an essential and distinguishing attribute of something or someone` (degree score `1030`)
- `central [n] :: a workplace that serves as a telecommunications facility where lines...` (degree score `1004`)

## Highest Outdegree Nodes

- `small [n] :: the slender part of the back`: `4878`
- `large [n] :: a garment size for a large person`: `3497`
- `white [n] :: a person of European descent with a light-skinned or pale complexion`: `2073`
- `tropical [a] :: relating to or situated in or characteristic of the tropics (the regi...`: `1938`
- `can [n] :: airtight sealed metal container for food or drink or paint etc.`: `1788`
- `tree [n] :: English actor and theatrical producer noted for his lavish production...`: `1703`
- `perennial [n] :: (botany) a plant lasting for three seasons or more`: `1547`
- `born [n] :: British nuclear physicist (born in Germany) honored for his contribut...`: `1540`
- `plant [n] :: buildings for carrying on industrial labor`: `1502`
- `form [n] :: the phonological or orthographic sound or appearance of a word that c...`: `1478`
- `yellow [n] :: yellow color or pigment; the chromatic color resembling the hue of su...`: `1445`
- `act [n] :: a legal document codifying the result of deliberations of a committee...`: `1441`
- `part [n] :: something determined in relation to something that includes it`: `1352`
- `shrub [n] :: a low woody perennial plant usually having several major stems`: `1307`
- `common [n] :: a piece of open land for recreational use in an urban area`: `1294`
- `english [n] :: an Indo-European language belonging to the West Germanic branch; the...`: `1260`
- `body [n] :: the entire physical structure of an organism (an animal, plant, or hu...`: `1253`
- `eastern [a] :: lying toward or situated in the east`: `1249`
- `city [n] :: a large and densely populated urban area; may include several indepen...`: `1247`
- `american [n] :: a native or inhabitant of the United States`: `1145`
- `cultivated [a] :: (of land or fields) prepared for raising crops by plowing or fertilizing`: `1144`
- `european [n] :: a native or inhabitant of Europe`: `1125`
- `western [n] :: a film about life in the western United States during the period of e...`: `1111`
- `northern [n] :: a dialect of Middle English that developed into Scottish Lallans`: `1108`
- `various [a] :: of many different kinds purposefully arranged but lacking any uniformity`: `1089`

## Highest Indegree Nodes

- `microsensor [n] :: A submicrometer- to millimeter-size device that converts a nonelectri...`: `27`
- `myotonia_atrophica [n] :: a severe form of muscular dystrophy marked by generalized weakness an...`: `25`
- `myotonic_dystrophy [n] :: a severe form of muscular dystrophy marked by generalized weakness an...`: `25`
- `myotonic_muscular_dystrophy [n] :: a severe form of muscular dystrophy marked by generalized weakness an...`: `25`
- `steinerts_disease [n] :: a severe form of muscular dystrophy marked by generalized weakness an...`: `25`
- `mononychus_olecranus [n] :: a turkey-sized long-legged fossil 75 million years old found in the G...`: `24`
- `welwitschia [n] :: curious plant of arid regions of southwestern Africa having a yard-hi...`: `24`
- `welwitschia_mirabilis [n] :: curious plant of arid regions of southwestern Africa having a yard-hi...`: `24`
- `generic [n] :: wine that does not meet the minimum qualifications and standards for...`: `23`
- `generic_wine [n] :: wine that does not meet the minimum qualifications and standards for...`: `23`
- `kuru [n] :: a progressive disease of the central nervous system marked by increas...`: `23`
- `maxwells_demon [n] :: an imaginary creature that controls a small hole in a partition that...`: `23`
- `neobehaviorism [n] :: a school of psychology based on the general principles of behaviorism...`: `23`
- `newmarket [n] :: a gambling card game in which chips are placed on the ace and king an...`: `23`
- `placebo_effect [n] :: any effect that seems to be a consequence of administering a placebo;...`: `23`
- `stops [n] :: a gambling card game in which chips are placed on the ace and king an...`: `23`
- `arborvirus [n] :: a large heterogeneous group of RNA viruses divisible into groups on t...`: `22`
- `arbovirus [n] :: a large heterogeneous group of RNA viruses divisible into groups on t...`: `22`
- `dug_out [n] :: a shelter for humans or domesticated animals and livestock based on a...`: `22`
- `hooke [n] :: English scientist who formulated the law of elasticity and proposed a...`: `22`
- `liver [n] :: large and complicated reddish-brown glandular organ located in the up...`: `22`
- `pit_house [n] :: a shelter for humans or domesticated animals and livestock based on a...`: `22`
- `pithouse [n] :: a shelter for humans or domesticated animals and livestock based on a...`: `22`
- `radiation_sickness [n] :: syndrome resulting from exposure to ionizing radiation (e.g., exposur...`: `22`
- `radiation_syndrome [n] :: syndrome resulting from exposure to ionizing radiation (e.g., exposur...`: `22`

## Annotation Coverage

- `frequency`: `46386` / `160010` (28.99%)
- `concreteness`: `38572` / `160010` (24.11%)
- `age_of_acquisition`: `34314` / `160010` (21.44%)
- `imageability`: `0` / `160010` (0.00%)

## Caveats

- This is a paper-faithful approximation, not an exact reproduction of Vincent-Lamarre's original WordNet preprocessing.
- Differences can come from OEWN 2024, representative-sense ordering, token filtering, and POS resolution policy.
- Candidate seed sizes are heuristic unless the selected seed method reports exact coverage for all cyclic SCCs.
