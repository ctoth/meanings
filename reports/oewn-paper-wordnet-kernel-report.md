# Open English WordNet Paper-Baseline Kernel Report

- Lexicon: `oewn:2024`
- Graph type: paper-faithful WordNet approximation
- Node policy: one normalized `lemma::pos` node with the first available representative synset definition
- Edge policy: content-word `defining_lemma::pos -> defined_lemma::pos`, preferring same POS and otherwise unambiguous POS
- Seed method: `bounded-scc`
- Core policy: `source-union`

## Summary

- Total lemma/POS nodes: `160010`
- Total directed edges: `677823`
- Kernel nodes: `12853` (8.03%)
- Kernel SCC count: `3841`
- Source SCCs inside kernel: `286`
- Core size (union of source SCCs): `288`
- Satellite size (kernel minus source-SCC Core): `12565`
- Candidate seed size: `946` (0.59%; 7.36% of kernel)
- Residual cyclic SCCs after seed method: `1`

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

- Layering skipped because the selected seed did not fully acyclicize the kernel.

## Top Candidate Seed Nodes

- `can [n] :: airtight sealed metal container for food or drink or paint etc.` (degree score `1795`)
- `act [n] :: a legal document codifying the result of deliberations of a committee...` (degree score `1446`)
- `part [n] :: something determined in relation to something that includes it` (degree score `1354`)
- `body [n] :: the entire physical structure of an organism (an animal, plant, or hu...` (degree score `1260`)
- `time [n] :: an instance or single occasion for some event` (degree score `852`)
- `capable [a] :: (usually followed by ‘of’) having capacity or ability` (degree score `705`)
- `substance [n] :: the real physical matter of which a person or thing consists` (degree score `577`)
- `degree [n] :: a position on a scale of intensity or amount or quality` (degree score `432`)
- `lower [n] :: the lower of two berths` (degree score `310`)
- `defeated [n] :: people who are defeated` (degree score `268`)
- `free [n] :: people who are free` (degree score `202`)
- `giving [n] :: the act of giving` (degree score `127`)
- `situated [a] :: situated in a particular spot or position` (degree score `125`)
- `gold [n] :: coins made of gold` (degree score `123`)
- `flattened [a] :: having been flattened` (degree score `122`)
- `spring [n] :: the season of growth; spring; the beginning of spring` (degree score `120`)
- `financial [a] :: involving financial matters` (degree score `114`)
- `tea [n] :: a beverage made by steeping tea leaves in water` (degree score `101`)
- `surface [a] :: on the surface` (degree score `98`)
- `read [n] :: something that is read` (degree score `89`)
- `coffee [n] :: a beverage consisting of an infusion of ground coffee beans` (degree score `85`)
- `living [a] :: pertaining to living persons` (degree score `81`)
- `side [a] :: located on a side` (degree score `78`)
- `married [n] :: a person who is married` (degree score `77`)
- `dress [n] :: a one-piece garment for a woman; has skirt and bodice` (degree score `70`)

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
