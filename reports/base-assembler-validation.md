# Base Assembler Validation

Closure-coverage scan over `data/sense-unfolding-index.json` using the implicit base derived from `data/kernel-pressure-table.csv` columns.

## Inputs

- Unfolding index: `data\sense-unfolding-index.json` (lexicon `oewn:2024`)
- Pressure table: `data\kernel-pressure-table.csv`
- Target selector: `admitted` with `closure_size <= 200` cutoff
- Selected target rows: `15872`

## Bases

- L0-only baseline size: `317`
- Augmented base size (L0 + primitive_candidate + assembler_helper): `331`
- Augmented layer size (primitive_candidate + assembler_helper): `14`

## Closure Rate by Band

Counts are status histograms over the target selection. Closure rate is
`closed / (closed + artifact + circular + external + background)`; truncated rows
are reported as `graph_data` and excluded from the denominator.

| band | closed_l0 | closed_aug | non_truncated_total | rate_l0 | rate_aug |
| --- | --- | --- | --- | --- | --- |
| closure_size_le_50 | 2033 | 2119 | 12957 | 0.1569 | 0.1635 |
| closure_size_le_100 | 2033 | 2119 | 14100 | 0.1442 | 0.1503 |
| closure_size_le_200 | 2033 | 2119 | 14885 | 0.1366 | 0.1424 |
| all_targets | 2033 | 2119 | 15660 | 0.1298 | 0.1353 |

## Status Histogram (augmented base, `closure_size <= 200`)

| status | count |
| --- | --- |
| artifact | 8551 |
| background | 3664 |
| closed | 2119 |
| external | 450 |
| circular | 101 |

## Marginal Grounding Yield

- Added base ICs (augmented layer): `14`
- Closed under L0 only (all targets): `2033`
- Closed under augmented (all targets): `2119`
- Delta closed: `86`
- MGY = delta_closed / added_base_size: `6.1429`

## Falsifier Verdict

- Closure rate at `closure_size <= 200` (augmented): `0.1424`
- Artifact share at `closure_size <= 200` (augmented): `0.5745`
- MGY: `6.1429`
- Triggered: `['closure_rate 0.142 below threshold 0.600 on closure_size <= 200', 'artifact_share 0.574 above threshold 0.100 on closure_size <= 200']`
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
| ic:do | do | 5 |
| ic:office | office | 5 |
| ic:giving | giving | 4 |
| ic:plural | plural | 3 |
| ic:useful | useful | 1 |
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
| ic:act | act | 3633 | common_vocabulary |
| ic:amount | amount | 2109 | candidate_background |
| ic:time | time | 2003 | candidate_background |
| ic:quality | quality | 1933 | resource_artifact |
| ic:capable | capable | 1844 | candidate_background |
| ic:event | event | 1802 | candidate_background |
| ic:showing | showing | 1795 | resource_artifact |
| ic:part | part | 1758 | common_vocabulary |
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
| ic:position | position | 1146 | circular_dependency |
| ic:feelings | feelings | 1134 | candidate_background |
| ic:done | done | 1129 | candidate_background |
| ic:attention | attention | 1119 | candidate_background |
| ic:force | force | 1091 | resource_artifact |
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
| oewn-absorbing__5.00.00.interesting.00 | ic:absorbing | absorbing | s | 4 | ic:act,ic:attention,ic:capable,ic:holding |
| oewn-acellular__3.00.00.. | ic:acellular | acellular | a | 4 | ic:divided,ic:parts,ic:separated |
| oewn-addition__1.06.00.. | ic:addition | addition | n | 6 | ic:abstract,ic:component,ic:part |
| oewn-adverbial__1.10.00.. | ic:adverbial | adverbial | n | 5 | ic:adverb,ic:word,ic:words |
| oewn-afternoon__1.28.00.. | ic:afternoon | afternoon | n | 5 | ic:day,ic:noon,ic:part |
| oewn-agile__5.00.00.active.01 | ic:agile | agile | s | 6 | ic:good,ic:moving,ic:quickly,ic:reason,ic:speed |
| oewn-animation__1.26.00.. | ic:animation | animation | n | 4 | ic:alive,ic:condition,ic:life |
| oewn-anonymous__3.00.00.. | ic:anonymous | anonymous | a | 9 | ic:identity,ic:individual,ic:known,ic:no,ic:recognised |
| oewn-assumed__5.00.00.counterfeit.00 | ic:assumed | assumed | s | 5 | ic:acquired,ic:adopted,ic:choice,ic:deceive |
| oewn-attachment__1.12.00.. | ic:attachment | attachment | n | 5 | ic:affection,ic:institution,ic:liking,ic:positive |

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

