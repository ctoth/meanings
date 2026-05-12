# Up-Goer Five Kernel Export

This is the current executable Up-Goer candidate: the strict graph seed is the set of graph nodes removed to make the OEWN definition kernel acyclic; the human seed surface is that seed collapsed from `lemma::pos` nodes to lemmas.

## Summary

- Candidate seed id: `exact-small-greedy:n5044:r0`
- Seed method: `exact-small-greedy`
- Seed exact: `False`
- Strict graph seed nodes: `5044`
- Human seed surfaces: `4817`
- Kernel nodes exported: `18151`
- Kernel surfaces exported: `16733`
- Residual cyclic SCCs after seed removal: `0`
- Deepest definitional layer: `64`
- Components: `{'core': 510, 'satellite': 17641}`
- Annotation sources: `['data\\psycholinguistic\\frequency.csv', 'data\\psycholinguistic\\age_of_acquisition.csv', 'data\\psycholinguistic\\concreteness.csv']`

## Annotation Coverage

| field | seed_count | seed_total | seed_fraction | kernel_count | kernel_total | kernel_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| frequency | 3120 | 5044 | 0.6186 | 12466 | 18151 | 0.6868 |
| age_of_acquisition | 2446 | 5044 | 0.4849 | 9729 | 18151 | 0.536 |
| concreteness | 2529 | 5044 | 0.5014 | 10904 | 18151 | 0.6007 |

## Layer Histogram

| layer | count |
| --- | --- |
| 0 | 5044 |
| 1 | 1888 |
| 2 | 1177 |
| 3 | 902 |
| 4 | 658 |
| 5 | 581 |
| 6 | 510 |
| 7 | 444 |
| 8 | 353 |
| 9 | 320 |
| 10 | 283 |
| 11 | 256 |
| 12 | 239 |
| 13 | 191 |
| 14 | 206 |
| 15 | 189 |
| 16 | 164 |
| 17 | 170 |
| 18 | 140 |
| 19 | 151 |
| 20 | 143 |
| 21 | 137 |
| 22 | 133 |
| 23 | 127 |
| 24 | 134 |
| 25 | 127 |
| 26 | 134 |
| 27 | 132 |
| 28 | 116 |
| 29 | 96 |
| 30 | 89 |
| 31 | 110 |
| 32 | 108 |
| 33 | 112 |
| 34 | 130 |
| 35 | 122 |
| 36 | 111 |
| 37 | 101 |
| 38 | 129 |
| 39 | 172 |
| 40 | 177 |
| 41 | 168 |
| 42 | 135 |
| 43 | 120 |
| 44 | 70 |
| 45 | 50 |
| 46 | 38 |
| 47 | 52 |
| 48 | 77 |
| 49 | 115 |
| 50 | 91 |
| 51 | 76 |
| 52 | 93 |
| 53 | 82 |
| 54 | 79 |
| 55 | 65 |
| 56 | 67 |
| 57 | 69 |
| 58 | 53 |
| 59 | 58 |
| 60 | 46 |
| 61 | 24 |
| 62 | 12 |
| 63 | 4 |
| 64 | 1 |

## Top Human Seed Surfaces

| lemma | surface_word | seed_node_count | parts_of_speech | best_frequency | earliest_age_of_acquisition | max_degree_score |
| --- | --- | --- | --- | --- | --- | --- |
| s | s | 1 | n | 7.316033195866643 |  | 271 |
| do | do | 2 | n, v | 6.787261912174824 | 3.6 | 210 |
| no | no | 2 | a, n | 6.7754927459819 | 2.715564 | 498 |
| can | can | 2 | n, v | 6.719354331308571 | 4.32 | 1795 |
| all | all | 1 | a | 6.712212420338913 | 4.239515000000001 | 70 |
| get | get | 1 | n | 6.66062849230587 | 3.17 | 74 |
| here | here | 1 | a | 6.655049247524397 | 3.738636 | 2 |
| so | so | 1 | n | 6.627197751579461 | 5.14536 | 414 |
| right | right | 2 | a, n | 6.602376646359637 | 4.346085 | 297 |
| like | like | 1 | v | 6.601353592943822 | 3.6853510000000003 | 101 |
| out | out | 3 | a, n, v | 6.586591270205694 | 3.280385 | 414 |
| go | go | 1 | v | 6.578393896124764 | 3.37 | 80 |
| up | up | 1 | a | 6.564072702809289 | 2.918047 | 74 |
| come | come | 1 | v | 6.496472254640901 | 3.32 | 81 |
| well | well | 2 | n, r | 6.475172328433664 | 6.157775000000001 | 237 |
| want | want | 1 | v | 6.4401868823515045 | 4.16 | 6 |
| good | good | 2 | a, r | 6.4160709261850934 | 3.55 | 90 |
| let | let | 1 | n | 6.383085947944817 | 4.53 | 18 |
| will | will | 1 | n | 6.326490668604775 | 7.53 | 318 |
| back | back | 2 | a, n | 6.302422401748658 | 5.3052150000000005 | 481 |
| time | time | 2 | n, v | 6.29136050297892 | 5.16 | 852 |
| look | look | 1 | v | 6.288835870185782 | 4.05 | 63 |
| take | take | 1 | v | 6.276109356519957 | 4.37 | 171 |
| tell | tell | 1 | n | 6.23606998593794 | 4.26 | 32 |
| down | down | 2 | a, n | 6.172676305490812 | 4.93222 | 282 |
| make | make | 2 | n, v | 6.141720156407864 | 4.68 | 1043 |
| over | over | 1 | n | 6.121067135292526 | 5.571640000000001 | 748 |
| more | more | 3 | a, n, r | 6.112882339773854 | 3.781264 | 700 |
| need | need | 1 | n | 6.111647782919253 | 3.56 | 64 |
| mean | mean | 1 | v | 6.094224698597197 | 4.0 | 6 |
| very | very | 1 | a | 6.093272155268496 | 4.900249000000001 | 183 |
| give | give | 2 | n, v | 6.066788831224598 | 4.28 | 217 |
| sure | sure | 1 | r | 6.040735067507489 | 4.85 | 11 |
| thing | thing | 1 | n | 6.036307065878121 | 4.58 | 174 |
| help | help | 1 | v | 5.963728665708805 | 3.65 | 17 |
| god | god | 1 | n | 5.955176933134951 | 4.346085 | 357 |
| night | night | 1 | n | 5.936951708951002 | 3.61 | 147 |
| talk | talk | 1 | v | 5.931380392596807 | 3.68 | 61 |
| first | first | 1 | n | 5.9239876256550925 | 4.388713 | 1068 |
| put | put | 1 | v | 5.917681413262269 | 3.72 | 175 |
| great | great | 2 | a, n | 5.913685237688773 | 5.05 | 262 |
| thought | thought | 1 | n | 5.907079076170835 | 5.891350000000001 | 234 |
| day | day | 1 | n | 5.903493734796248 | 3.5 | 319 |
| work | work | 2 | n, v | 5.90142855136968 | 5.86 | 553 |
| life | life | 1 | n | 5.9006809644708715 | 5.89 | 504 |
| before | before | 1 | r | 5.899310611470681 | 5.454413000000001 | 575 |
| better | better | 1 | r | 5.899235545446485 | 5.017476 | 10 |
| again | again | 1 | r | 5.898527141458522 | 5.784780000000001 | 214 |
| still | still | 1 | v | 5.896340991412325 | 5.262587000000001 | 12 |
| home | home | 2 | r, v | 5.888343270486459 | 3.8665200000000004 | 16 |

## Layer 1 Samples

| node_id | surface_word | pos | degree_score | frequency | age_of_acquisition | gloss |
| --- | --- | --- | --- | --- | --- | --- |
| t::n | t | n | 33 | 7.1571389241459435 |  | a base found in DNA (but not in RNA) and derived from pyrimidine; pai... |
| no::r | no | r | 30 | 6.7754927459819 | 2.715564 | referring to the degree to which a certain quality is present |
| all::r | all | r | 34 | 6.712212420338913 | 4.239515000000001 | to a complete degree or to the full or entire extent; Completely or e... |
| like::n | like | n | 869 | 6.601353592943822 | 3.6853510000000003 | a similar kind |
| like::a | like | a | 299 | 6.601353592943822 | 3.6853510000000003 | resembling or similar; having the same or some of the same characteri... |
| up::v | up | v | 27 | 6.564072702809289 | 2.918047 | raise |
| about::a | about | a | 56 | 6.559491539198379 | 5.070761000000001 | on the move |
| going::n | going | n | 75 | 6.326418485363236 | 5.411785000000001 | the act of departing |
| going::a | going | a | 20 | 6.326418485363236 | 5.411785000000001 | in full operation |
| back::r | back | r | 11 | 6.302422401748658 | 5.3052150000000005 | in or to or toward a former location |
| man::n | man | n | 428 | 6.265580655533629 | 3.11 | one of the British Isles in the Irish Sea |
| down::v | down | v | 37 | 6.172676305490812 | 4.93222 | drink down entirely |
| much::a | much | a | 28 | 5.987639667533254 | 4.580539 | (quantifier used with mass nouns) great in quantity or degree or extent |
| much::r | much | r | 26 | 5.987639667533254 | 4.580539 | to a great degree or extent |
| first::a | first | a | 42 | 5.9239876256550925 | 4.388713 | preceding all others in time or space or degree |
| first::r | first | r | 10 | 5.9239876256550925 | 4.388713 | before anything else |
| still::a | still | a | 17 | 5.896340991412325 | 5.262587000000001 | not in physical motion |
| home::n | home | n | 170 | 5.888343270486459 | 3.8665200000000004 | where you live at a particular time |
| home::a | home | a | 15 | 5.888343270486459 | 3.8665200000000004 | used of your own ground |
| won::n | won | n | 111 | 5.879881639130543 |  | the basic unit of money in South Korea |
| ever::r | ever | r | 17 | 5.85019465777582 | 6.2643450000000005 | at any time |
| keep::n | keep | n | 78 | 5.846286957993113 | 4.42 | the financial means whereby one lives |
| must::a | must | a | 5 | 5.844039837815181 | 4.58 | highly recommended |
| everything::n | everything | n | 63 | 5.815580608956024 | 4.441998 | all things that are of importance to a person |
| years::n | years | n | 346 | 5.7542920385997345 |  | a late time of life |

## Layer 2 Samples

| node_id | surface_word | pos | degree_score | frequency | age_of_acquisition | gloss |
| --- | --- | --- | --- | --- | --- | --- |
| see::v | see | v | 21 | 6.407091750205684 | 3.06 | perceive by sight or have the power to perceive by sight |
| back::v | back | v | 46 | 6.302422401748658 | 5.3052150000000005 | be behind; approve of |
| look::n | look | n | 31 | 6.288835870185782 | 4.05 | the feelings expressed on a person's face |
| tell::v | tell | v | 18 | 6.23606998593794 | 4.26 | express in words |
| say::v | say | v | 13 | 6.21419623892925 | 3.42 | express in words |
| then::n | then | n | 222 | 6.172459118237157 | 6.7439100000000005 | that time; that moment |
| little::a | little | a | 97 | 6.159696263817038 | 3.95 | limited or below average in number or quantity or magnitude or extent |
| little::r | little | r | 9 | 6.159696263817038 | 3.95 | not much |
| need::v | need | v | 11 | 6.111647782919253 | 3.56 | require as useful, just, or proper |
| very::r | very | r | 50 | 6.093272155268496 | 4.900249000000001 | used to give emphasis |
| said::a | said | a | 142 | 6.0441284924303185 |  | being the one previously mentioned or spoken of |
| much::n | much | n | 273 | 5.987639667533254 | 4.580539 | a great amount or extent |
| nothing::r | nothing | r | 10 | 5.930672690939988 | 5.209302000000001 | in no respect; to no degree |
| better::n | better | n | 53 | 5.899235545446485 | 5.017476 | something superior in quality or condition or effect |
| away::r | away | r | 16 | 5.863275095829853 | 5.070761000000001 | from a particular thing or place or position (‘forth’ is obsolete) |
| new::a | new | a | 49 | 5.859025250027843 | 4.72 | in use after medieval times |
| long::v | long | v | 20 | 5.828821617275062 | 4.239515000000001 | desire strongly or persistently |
| feel::v | feel | v | 57 | 5.796848382228567 | 5.11 | undergo an emotional sensation or be in a particular state of mind |
| fine::a | fine | a | 48 | 5.776176696880547 | 7.44 | being satisfactory or in satisfactory condition |
| leave::v | leave | v | 52 | 5.748154617518834 | 5.58 | go away from a place |
| wrong::a | wrong | a | 21 | 5.7180036891797865 | 4.22 | not correct; not in conformity with fact or truth |
| wanted::a | wanted | a | 18 | 5.700362410420696 |  | desired or wished for or sought |
| course::v | course | v | 38 | 5.687143058223048 | 7.340702000000001 | move swiftly through or over |
| course::r | course | r | 8 | 5.687143058223048 | 7.340702000000001 | as might be expected |
| left::a | left | a | 36 | 5.684671734810117 | 5.571640000000001 | being or located on or directed toward the side of the body to the we... |

## Deepest Layer Samples

| node_id | surface_word | pos | degree_score | frequency | age_of_acquisition | gloss |
| --- | --- | --- | --- | --- | --- | --- |
| wet_bulb_thermometer::n | wet bulb thermometer | n | 9 |  |  | a thermometer with a bulb that is covered with moist muslin; used in... |

## Suspicious Seed Senses

| node_id | surface_word | pos | degree_score | suspicion_reasons | gloss |
| --- | --- | --- | --- | --- | --- |
| green_dinosaur::n | green dinosaur | n | 21 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | a living fossil or so-called ‘green dinosaur’; genus or subfamily of... |
| parental_leave::n | parental leave | n | 16 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | Parental leave or family leave is an employee benefit available in al... |
| silkworm_moth::n | silkworm moth | n | 14 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any silkworm moth of the family Saturniidae |
| solomons_seal::n | solomons seal | n | 11 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any of several plants of the genus Polygonatum having paired drooping... |
| bass_viol::n | bass viol | n | 9 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | viol that is the bass member of the viol family with approximately th... |
| brassica_oleracea::n | brassica oleracea | n | 6 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any of various cultivars of the genus Brassica oleracea grown for the... |
| more_than::a | more than | a | 618 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | (comparative of ‘much’ used with mass nouns) a quantifier meaning gre... |
| blue_green::n | blue green | n | 54 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a blue-green color or pigment |
| set_up::v | set up | v | 40 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | set up or found |
| central_africa::n | central africa | n | 37 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a landlocked country in central Africa; formerly under French control... |
| space_time::n | space time | n | 36 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | the four-dimensional coordinate system (3 dimensions of space and 1 o... |
| high_voltage::a | high voltage | a | 27 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | operating on or powered by a high voltage |
| sociopathic_personality::n | sociopathic personality | n | 25 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a personality disorder characterized by amorality and lack of affect;... |
| adult_male::n | adult male | n | 24 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | an adult person who is male (as opposed to a woman) |
| antisocial_personality_disorder::n | antisocial personality disorder | n | 24 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a personality disorder characterized by amorality and lack of affect;... |
| breeding_season::n | breeding season | n | 23 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | The breeding season is the most suitable season, usually with favoura... |
| meeting_beam_headlamp::n | meeting beam headlamp | n | 23 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | Dipped-beam (also called low, passing, or meeting beam) headlamp prov... |
| close_together::a | close together | a | 22 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | located close together |
| cock_ring::n | cock ring | n | 22 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | A cock ring is a ring that can be placed around a penis, usually at t... |
| coriolis_force::n | coriolis force | n | 22 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | (physics) a force due to the earth's rotation; acts on a body in moti... |
| psychopathic_personality::n | psychopathic personality | n | 22 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a personality disorder characterized by amorality and lack of affect;... |
| vx_gas::n | vx gas | n | 22 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a highly lethal nerve agent used in chemical warfare; a toxic liquid... |
| cucurbita_pepo::n | cucurbita pepo | n | 21 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a coarse vine widely cultivated for its large pulpy round orange frui... |
| hold_back::v | hold back | v | 21 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | hold back, as of a danger or an enemy; check the expansion or influen... |
| ion_exchange_resin::n | ion exchange resin | n | 21 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An ion-exchange resin or ion-exchange polymer is an insoluble matrix... |
| masdevallia::n | masdevallia | n | 21 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any of numerous orchids of the genus Masdevallia; tufted evergreen of... |
| pogonia::n | pogonia | n | 21 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any hardy bog orchid of the genus Pogonia: terrestrial orchids having... |
| sodium_chloride::n | sodium chloride | n | 21 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a white crystalline solid consisting mainly of sodium chloride (NaCl) |
| coal_tar::n | coal tar | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a tar formed from distillation of bituminous coal; coal tar can be fu... |
| dead_burned_lime::n | dead burned lime | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An over-burned lime (also called overburned lime, or sometimes dead-b... |
| deadburned_lime::n | deadburned lime | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An over-burned lime (also called overburned lime, or sometimes dead-b... |
| hubble_constant::n | hubble constant | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | (cosmology) the ratio of the speed of recession of a galaxy (due to t... |
| ion_exchange_polymer::n | ion exchange polymer | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An ion-exchange resin or ion-exchange polymer is an insoluble matrix... |
| over_burned_lime::n | over burned lime | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An over-burned lime (also called overburned lime, or sometimes dead-b... |
| overburned_lime::n | overburned lime | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | An over-burned lime (also called overburned lime, or sometimes dead-b... |
| siouan_language::n | siouan language | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, domain_or_named_entity_like | a family of North American Indian languages spoken by the Sioux |
| sphagnum::n | sphagnum | n | 20 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any of various pale or ashy mosses of the genus Sphagnum whose decomp... |
| third_base::n | third base | n | 20 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | the base that must be touched third by a base runner in baseball |
| fuscoboletinus::n | fuscoboletinus | n | 19 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | a genus of fungi belonging to the family Boletaceae, with distinguish... |
| guinea_worm::n | guinea worm | n | 19 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | a painful and debilitating infestation contracted by drinking stagnan... |
| ixodes_scapularis::n | ixodes scapularis | n | 19 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, domain_or_named_entity_like | parasitic on mice of genus Peromyscus and bites humans; principal vec... |
| meadow_rue::n | meadow rue | n | 19 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, domain_or_named_entity_like | any of various herbs of the genus Thalictrum; sometimes rhizomatous o... |
| wild_crab::n | wild crab | n | 19 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | wild crab apple native to Europe; a chief ancestor of cultivated apples |
| coelogyne::n | coelogyne | n | 18 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any of various orchids of the genus Coelogyne with: clusters of fragr... |
| european_beech::n | european beech | n | 18 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | large European beech with minutely-toothed leaves; widely planted as... |
| gloriosa::n | gloriosa | n | 18 | missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop, domain_or_named_entity_like | any plant of the genus Gloriosa of tropical Africa and Asia; a perenn... |
| k_lor::n | k lor | n | 18 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | salt of potassium (KCl) (trade names K-Dur 20, Kaochlor and K-lor and... |
| leavening_agent::n | leavening agent | n | 18 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | A leavening agent (also known as raising agent or leaven agent) is a... |
| lions_foot::n | lions foot | n | 18 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | common perennial herb widely distributed in the southern and eastern... |
| long_time::a | long time | a | 18 | multiword, missing_frequency, missing_age_of_acquisition, missing_concreteness, self_loop | having existed or persisted or continued in a particular role or stat... |
