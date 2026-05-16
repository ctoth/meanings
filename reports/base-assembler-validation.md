# Base Assembler Validation

Closure-coverage scan over `data/sense-unfolding-index.json` using the implicit base derived from `data/kernel-pressure-table.csv` columns.

## Inputs

- Unfolding index: `data\sense-unfolding-index.json` (lexicon `oewn:2024`)
- Pressure table: `data\kernel-pressure-table.csv`
- Target selector: `admitted` with `closure_size <= 200` cutoff
- Selected target rows: `15872`

## Bases

- L0-only baseline size: `317`
- Augmented base size (L0 + assembler_helper + base_promotable_terminal_common + primitive_candidate): `378`
- Augmented layer size (assembler_helper + base_promotable_terminal_common + primitive_candidate): `61`

## Closure Rate by Band

Counts are status histograms over the target selection. Closure rate is
`closed / (closed + artifact + circular + external + background)`; truncated rows
are reported as `graph_data` and excluded from the denominator.

| band | closed_l0 | closed_aug | non_truncated_total | rate_l0 | rate_aug |
| --- | --- | --- | --- | --- | --- |
| closure_size_le_50 | 2033 | 3044 | 12957 | 0.1569 | 0.2349 |
| closure_size_le_100 | 2033 | 3044 | 14100 | 0.1442 | 0.2159 |
| closure_size_le_200 | 2033 | 3044 | 14885 | 0.1366 | 0.2045 |
| all_targets | 2033 | 3044 | 15660 | 0.1298 | 0.1944 |

## Status Histogram (augmented base, `closure_size <= 200`)

| status | count |
| --- | --- |
| artifact | 8147 |
| background | 3177 |
| closed | 3044 |
| external | 435 |
| circular | 82 |

## Marginal Grounding Yield

- Added base ICs (augmented layer): `61`
- Closed under L0 only (all targets): `2033`
- Closed under augmented (all targets): `3044`
- Delta closed: `1011`
- MGY = delta_closed / added_base_size: `16.5738`

## Falsifier Verdict

- Closure rate at `closure_size <= 200` (augmented): `0.2045`
- Artifact share at `closure_size <= 200` (augmented): `0.5473`
- MGY: `16.5738`
- Triggered: `['closure_rate 0.205 below threshold 0.600 on closure_size <= 200', 'artifact_share 0.547 above threshold 0.100 on closure_size <= 200']`
- Hypothesis weakened: `True`

## Top Marginal Usage (augmented base)

ICs in the augmented base ranked by number of closed target rows whose closure references them.

| ic_id | primary_alias | closed_uses |
| --- | --- | --- |
| ic:make | make | 55 |
| ic:place | place | 51 |
| ic:time | time | 46 |
| ic:together | together | 29 |
| ic:body | body | 26 |
| ic:give | give | 26 |
| ic:line | line | 23 |
| ic:water | water | 22 |
| ic:certain | certain | 21 |
| ic:different | different | 20 |
| ic:move | move | 20 |
| ic:aright | aright | 20 |
| ic:thing | thing | 18 |
| ic:causa | causa | 17 |
| ic:material | material | 17 |
| ic:clean | clean | 16 |
| ic:cover | cover | 16 |
| ic:sound | sound | 16 |
| ic:group | group | 15 |
| ic:mind | mind | 15 |
| ic:forrad | forrad | 14 |
| ic:head | head | 14 |
| ic:inside | inside | 14 |
| ic:strong | strong | 14 |
| ic:back | back | 13 |
| ic:piece | piece | 13 |
| ic:small | small | 13 |
| ic:solid | solid | 13 |
| ic:high | high | 12 |
| ic:open | open | 12 |
| ic:outside | outside | 12 |
| ic:soft | soft | 12 |
| ic:taste | taste | 12 |
| ic:feeling | feeling | 11 |
| ic:free | free | 11 |
| ic:full | full | 11 |
| ic:going | going | 11 |
| ic:leave | leave | 11 |
| ic:over | over | 11 |
| ic:size | size | 11 |

## Augmented-Layer Marginal Usage

Marginal usage restricted to the 61 augmented-layer ICs added on top of L0.

| ic_id | primary_alias | closed_uses |
| --- | --- | --- |
| ic:time | time | 46 |
| ic:line | line | 23 |
| ic:water | water | 22 |
| ic:certain | certain | 21 |
| ic:aright | aright | 20 |
| ic:move | move | 20 |
| ic:causa | causa | 17 |
| ic:going | going | 11 |
| ic:leave | leave | 11 |
| ic:found | found | 10 |
| ic:number | number | 10 |
| ic:turn | turn | 10 |
| ic:do | do | 9 |
| ic:food | food | 9 |
| ic:change | change | 8 |
| ic:come | come | 8 |
| ic:desire | desire | 8 |
| ic:like | like | 8 |
| ic:still | still | 8 |
| ic:waite | waite | 8 |
| ic:meet | meet | 7 |
| ic:picture | picture | 7 |
| ic:better | better | 6 |
| ic:careful | careful | 6 |
| ic:find | find | 6 |
| ic:game | game | 6 |
| ic:home | home | 6 |
| ic:many | many | 6 |
| ic:blood | blood | 5 |
| ic:blue | blue | 5 |
| ic:fight | fight | 5 |
| ic:hair | hair | 5 |
| ic:happen | happen | 5 |
| ic:keep | keep | 5 |
| ic:last | last | 5 |
| ic:next | next | 5 |
| ic:office | office | 5 |
| ic:about | about | 4 |
| ic:giving | giving | 4 |
| ic:learn | learn | 4 |
| ic:storey | storey | 4 |
| ic:check | check | 3 |
| ic:eyes | eyes | 3 |
| ic:feel | feel | 3 |
| ic:plural | plural | 3 |
| ic:real | real | 3 |
| ic:sure | sure | 3 |
| ic:throw | throw | 3 |
| ic:today | today | 3 |
| ic:behind | behind | 2 |
| ic:house | house | 2 |
| ic:both | both | 1 |
| ic:useful | useful | 1 |
| ic:almost | almost | 0 |
| ic:ask | ask | 0 |
| ic:called | called | 0 |
| ic:express | express | 0 |
| ic:has | has | 0 |
| ic:helpful | helpful | 0 |
| ic:request | request | 0 |
| ic:than | than | 0 |

## Top Blocking ICs (augmented base)

Non-base ICs that prevented closure, with their pressure-bucket label.

| ic_id | primary_alias | blocked_targets | pressure_bucket |
| --- | --- | --- | --- |
| ic:amount | amount | 2109 | candidate_background |
| ic:quality | quality | 1933 | resource_artifact |
| ic:capable | capable | 1844 | candidate_background |
| ic:event | event | 1802 | candidate_background |
| ic:showing | showing | 1795 | resource_artifact |
| ic:can | can | 1566 | common_vocabulary |
| ic:property | property | 1468 | candidate_background |
| ic:energy | energy | 1447 | resource_artifact |
| ic:things | things | 1423 | candidate_background |
| ic:physical | physical | 1404 | resource_artifact |
| ic:knowledge | knowledge | 1384 | candidate_background |
| ic:words | words | 1268 | common_vocabulary |
| ic:general | general | 1235 | candidate_background |
| ic:activity | activity | 1199 | resource_artifact |
| ic:more | more | 1194 | common_vocabulary |
| ic:complete | complete | 1192 | resource_artifact |
| ic:life | life | 1181 | common_vocabulary |
| ic:regard | regard | 1171 | candidate_background |
| ic:marked | marked | 1164 | resource_artifact |
| ic:feelings | feelings | 1134 | candidate_background |
| ic:done | done | 1129 | candidate_background |
| ic:attention | attention | 1119 | candidate_background |
| ic:power | power | 1084 | common_vocabulary |
| ic:information | information | 1077 | candidate_background |
| ic:characteristic | characteristic | 1045 | candidate_background |
| ic:quantity | quantity | 1044 | resource_artifact |
| ic:purpose | purpose | 1032 | resource_artifact |
| ic:according | according | 1022 | resource_artifact |
| ic:occurrence | occurrence | 1005 | external_substrate |
| ic:intensity | intensity | 985 | resource_artifact |
| ic:skill | skill | 978 | candidate_background |
| ic:unit | unit | 974 | resource_artifact |
| ic:satisfaction | satisfaction | 951 | resource_artifact |
| ic:strength | strength | 943 | resource_artifact |
| ic:law | law | 929 | common_vocabulary |
| ic:ability | ability | 922 | candidate_background |
| ic:relative | relative | 898 | candidate_background |
| ic:conditions | conditions | 892 | candidate_background |
| ic:writing | writing | 882 | resource_artifact |
| ic:essential | essential | 878 | resource_artifact |

## Failed Target Examples

Up to ten failed rows per status (augmented base, `closure_size <= 200`).

### artifact

| sense_id | ic_id | label | pos | closure_size | missing_preview |
| --- | --- | --- | --- | --- | --- |
| oewn-accepted__5.00.00.acknowledged.00 | ic:accepted | accepted | s | 1 | ic:accepted |
| oewn-accompaniment__1.10.00.. | ic:accompaniment | accompaniment | n | 1 | ic:accompaniment |
| oewn-accompaniment__1.11.00.. | ic:accompaniment | accompaniment | n | 1 | ic:accompaniment |
| oewn-according__5.00.00.accordant.00 | ic:according | according | s | 1 | ic:according |
| oewn-accurate__3.00.00.. | ic:accurate | accurate | a | 1 | ic:accurate |
| oewn-accurate__5.00.00.correct.00 | ic:accurate | accurate | s | 1 | ic:accurate |
| oewn-acid__1.27.00.. | ic:acid | acid | n | 1 | ic:acid |
| oewn-acid__5.00.00.unpleasant.00 | ic:acid | acid | s | 1 | ic:acid |
| oewn-active__1.24.00.. | ic:active | active | n | 1 | ic:active |
| oewn-active__1.27.00.. | ic:active | active | n | 1 | ic:active |

### circular

| sense_id | ic_id | label | pos | closure_size | missing_preview |
| --- | --- | --- | --- | --- | --- |
| oewn-desired__5.00.00.wanted.00 | ic:desired | desired | s | 1 | ic:desired |
| oewn-exercising__1.04.00.. | ic:exercising | exercising | n | 1 | ic:exercising |
| oewn-goal__1.04.00.. | ic:goal | goal | n | 1 | ic:goal |
| oewn-goal__1.06.00.. | ic:goal | goal | n | 1 | ic:goal |
| oewn-goal__1.09.00.. | ic:goal | goal | n | 1 | ic:goal |
| oewn-located__5.00.00.settled.01 | ic:located | located | s | 1 | ic:located |
| oewn-names__1.10.00.. | ic:names | names | n | 1 | ic:names |
| oewn-placed__5.00.00.arranged.00 | ic:placed | placed | s | 1 | ic:placed |
| oewn-placed__5.00.00.settled.01 | ic:placed | placed | s | 1 | ic:placed |
| oewn-anatomy__1.08.00.. | ic:anatomy | anatomy | n | 4 | ic:alternative,ic:names |

### external

| sense_id | ic_id | label | pos | closure_size | missing_preview |
| --- | --- | --- | --- | --- | --- |
| oewn-acellular__3.00.00.. | ic:acellular | acellular | a | 4 | ic:divided,ic:parts,ic:separated |
| oewn-addition__1.06.00.. | ic:addition | addition | n | 6 | ic:abstract,ic:component |
| oewn-adverbial__1.10.00.. | ic:adverbial | adverbial | n | 5 | ic:adverb,ic:word,ic:words |
| oewn-afternoon__1.28.00.. | ic:afternoon | afternoon | n | 5 | ic:day,ic:noon |
| oewn-agile__5.00.00.active.01 | ic:agile | agile | s | 6 | ic:moving,ic:quickly,ic:reason,ic:speed |
| oewn-animation__1.26.00.. | ic:animation | animation | n | 4 | ic:alive,ic:life |
| oewn-anonymous__3.00.00.. | ic:anonymous | anonymous | a | 9 | ic:identity,ic:individual,ic:known,ic:no,ic:recognised |
| oewn-appraisal__1.09.00.. | ic:appraisal | appraisal | n | 5 | ic:classification,ic:things,ic:worth |
| oewn-assumed__5.00.00.counterfeit.00 | ic:assumed | assumed | s | 5 | ic:acquired,ic:adopted,ic:deceive |
| oewn-attachment__1.12.00.. | ic:attachment | attachment | n | 5 | ic:affection,ic:institution,ic:liking |

### background

| sense_id | ic_id | label | pos | closure_size | missing_preview |
| --- | --- | --- | --- | --- | --- |
| oewn-aardvark__1.05.00.. | ic:aardvark | aardvark | n | 1 | ic:aardvark |
| oewn-abaca__1.20.00.. | ic:abaca | abaca | n | 1 | ic:abaca |
| oewn-abaca__1.27.00.. | ic:abaca | abaca | n | 1 | ic:abaca |
| oewn-abdomen__1.08.00.. | ic:abdomen | abdomen | n | 1 | ic:abdomen |
| oewn-ability__1.07.00.. | ic:ability | ability | n | 1 | ic:ability |
| oewn-ability__1.09.00.. | ic:ability | ability | n | 1 | ic:ability |
| oewn-able__3.00.00.. | ic:able | able | a | 1 | ic:able |
| oewn-able__5.00.00.competent.00 | ic:able | able | s | 1 | ic:able |
| oewn-able__5.00.00.fit.01 | ic:able | able | s | 1 | ic:able |
| oewn-abnormal__3.00.00.. | ic:abnormal | abnormal | a | 1 | ic:abnormal |

