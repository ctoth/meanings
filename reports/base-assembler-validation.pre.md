# Base Assembler Validation

Closure-coverage scan over `data/sense-unfolding-index.json` using the implicit base derived from `data/kernel-pressure-table.csv` columns.

## Inputs

- Unfolding index: `data\sense-unfolding-index.json` (lexicon `oewn:2024`)
- Pressure table: `data\kernel-pressure-table.csv`
- Target selector: `admitted` with `closure_size <= 200` cutoff
- Selected target rows: `15872`

## Bases

- L0-only baseline size: `317`
- Augmented base size (L0 + primitive_candidate + assembler_helper): `326`
- Augmented layer size (primitive_candidate + assembler_helper): `9`

## Closure Rate by Band

Counts are status histograms over the target selection. Closure rate is
`closed / (closed + artifact + circular + external + background)`; truncated rows
are reported as `graph_data` and excluded from the denominator.

| band | closed_l0 | closed_aug | non_truncated_total | rate_l0 | rate_aug |
| --- | --- | --- | --- | --- | --- |
| closure_size_le_50 | 2033 | 2110 | 12957 | 0.1569 | 0.1628 |
| closure_size_le_100 | 2033 | 2110 | 14100 | 0.1442 | 0.1496 |
| closure_size_le_200 | 2033 | 2110 | 14885 | 0.1366 | 0.1418 |
| all_targets | 2033 | 2110 | 15660 | 0.1298 | 0.1347 |

## Status Histogram (augmented base, `closure_size <= 200`)

| status | count |
| --- | --- |
| artifact | 9445 |
| background | 3048 |
| closed | 2110 |
| external | 205 |
| circular | 77 |

## Marginal Grounding Yield

- Added base ICs (augmented layer): `9`
- Closed under L0 only (all targets): `2033`
- Closed under augmented (all targets): `2110`
- Delta closed: `77`
- MGY = delta_closed / added_base_size: `8.5556`

## Falsifier Verdict

- Closure rate at `closure_size <= 200` (augmented): `0.1418`
- Artifact share at `closure_size <= 200` (augmented): `0.6345`
- MGY: `8.5556`
- Triggered: `['closure_rate 0.142 below threshold 0.600 on closure_size <= 200', 'artifact_share 0.635 above threshold 0.100 on closure_size <= 200']`
- Hypothesis weakened: `True`

## Top Marginal Usage (augmented base)

ICs in the augmented base ranked by number of closed target rows whose closure references them.

| ic_id | primary_alias | closed_uses |
| --- | --- | --- |
| ic:make | make | 46 |
| ic:place | place | 34 |
| ic:together | together | 22 |
| ic:give | give | 21 |
| ic:body | body | 18 |
| ic:clean | clean | 16 |
| ic:cover | cover | 14 |
| ic:head | head | 14 |
| ic:sound | sound | 14 |
| ic:certain | certain | 13 |
| ic:different | different | 13 |
| ic:high | high | 12 |
| ic:mind | mind | 12 |
| ic:strong | strong | 12 |
| ic:taste | taste | 12 |
| ic:free | free | 11 |
| ic:inside | inside | 11 |
| ic:material | material | 11 |
| ic:open | open | 11 |
| ic:outside | outside | 11 |
| ic:piece | piece | 11 |
| ic:size | size | 11 |
| ic:small | small | 11 |
| ic:solid | solid | 11 |
| ic:feeling | feeling | 10 |
| ic:first | first | 10 |
| ic:group | group | 10 |
| ic:play | play | 10 |
| ic:soft | soft | 10 |
| ic:forrad | forrad | 9 |
| ic:full | full | 9 |
| ic:hand | hand | 9 |
| ic:liquid | liquid | 9 |
| ic:back | back | 8 |
| ic:beginning | beginning | 8 |
| ic:desire | desire | 8 |
| ic:early | early | 8 |
| ic:field | field | 8 |
| ic:frame | frame | 8 |
| ic:hard | hard | 8 |

## Augmented-Layer Marginal Usage

Marginal usage restricted to the 13 augmented-layer ICs added on top of L0.

| ic_id | primary_alias | closed_uses |
| --- | --- | --- |
| ic:certain | certain | 13 |
| ic:desire | desire | 8 |
| ic:office | office | 5 |
| ic:giving | giving | 4 |
| ic:plural | plural | 3 |
| ic:useful | useful | 1 |
| ic:express | express | 0 |
| ic:helpful | helpful | 0 |
| ic:request | request | 0 |

## Top Blocking ICs (augmented base)

Non-base ICs that prevented closure, with their pressure-bucket label.

| ic_id | primary_alias | blocked_targets | pressure_bucket |
| --- | --- | --- | --- |
| ic:act | act | 3633 | resource_artifact |
| ic:amount | amount | 2109 | candidate_background |
| ic:time | time | 2003 | candidate_background |
| ic:quality | quality | 1933 | resource_artifact |
| ic:capable | capable | 1844 | candidate_background |
| ic:event | event | 1802 | candidate_background |
| ic:showing | showing | 1795 | resource_artifact |
| ic:part | part | 1758 | resource_artifact |
| ic:can | can | 1566 | resource_artifact |
| ic:property | property | 1468 | candidate_background |
| ic:energy | energy | 1447 | resource_artifact |
| ic:things | things | 1423 | candidate_background |
| ic:physical | physical | 1404 | resource_artifact |
| ic:knowledge | knowledge | 1384 | candidate_background |
| ic:words | words | 1268 | resource_artifact |
| ic:general | general | 1235 | candidate_background |
| ic:activity | activity | 1199 | resource_artifact |
| ic:more | more | 1194 | resource_artifact |
| ic:complete | complete | 1192 | resource_artifact |
| ic:life | life | 1181 | resource_artifact |
| ic:regard | regard | 1171 | candidate_background |
| ic:marked | marked | 1164 | resource_artifact |
| ic:position | position | 1146 | circular_dependency |
| ic:feelings | feelings | 1134 | candidate_background |
| ic:done | done | 1129 | candidate_background |
| ic:attention | attention | 1119 | candidate_background |
| ic:force | force | 1091 | resource_artifact |
| ic:power | power | 1084 | resource_artifact |
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
| ic:causing | causing | 939 | candidate_background |

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
| oewn-position__1.04.00.. | ic:position | position | n | 1 | ic:position |

### external

| sense_id | ic_id | label | pos | closure_size | missing_preview |
| --- | --- | --- | --- | --- | --- |
| oewn-acellular__3.00.00.. | ic:acellular | acellular | a | 4 | ic:divided,ic:parts,ic:separated |
| oewn-assumed__5.00.00.counterfeit.00 | ic:assumed | assumed | s | 5 | ic:acquired,ic:adopted,ic:choice,ic:deceive |
| oewn-attachment__1.12.00.. | ic:attachment | attachment | n | 5 | ic:affection,ic:institution,ic:liking,ic:positive |
| oewn-attentively__4.02.00.. | ic:attentively | attentively | r | 4 | ic:attention,ic:attentive |
| oewn-beef__1.05.00.. | ic:beef | beef | n | 4 | ic:cattle,ic:food,ic:meat |
| oewn-believing__1.09.00.. | ic:believing | believing | n | 2 | ic:cognition,ic:cognitive |
| oewn-burst__1.11.00.. | ic:burst | burst | n | 4 | ic:event,ic:happening,ic:intense,ic:sudden |
| oewn-case__1.11.00.. | ic:case | case | n | 2 | ic:event,ic:occurrence |
| oewn-causally__4.02.00.. | ic:causally | causally | r | 5 | ic:causa,ic:causal,ic:causing,ic:done,ic:fashion |
| oewn-celibacy__1.26.00.. | ic:celibacy | celibacy | n | 4 | ic:related,ic:status,ic:unmarried |

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

