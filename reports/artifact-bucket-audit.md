# Artifact Bucket Audit

Read-only Phase 1 inventory of every IC currently labelled `pressure_bucket = resource_artifact` in `data/kernel-pressure-table.csv`.

## Inputs

- Pressure table: `data\kernel-pressure-table.csv`
- Unfolding index: `data\sense-unfolding-index.json`

## Summary

- Total `resource_artifact` rows: `4376`
- Rows blocking at least one admitted target: `1468`
- Rows with zero containment in admitted targets: `2908`

Containment is the number of admitted, non-truncated rows in
`data/sense-unfolding-index.json` whose `transitive_closure_ic_ids` references
the IC. It is an upper bound on the IC's blocker impact under any base that
does not include the IC.

## Typed Bucket — Row Counts (blocking only)

How many `resource_artifact` ICs sit in each `typed_bucket`, among ICs that
block at least one admitted target.

| typed_bucket | row_count |
| --- | --- |
| technical_term | 794 |
| proper_name | 260 |
| abbreviation_or_code | 215 |
| morphology_register_artifact | 186 |
| taxon | 13 |

## Typed Bucket — Blocker Sums

Sum of containment counts within each `typed_bucket`. This is the cumulative
admitted-target reach of the bucket — the falsifier metric for the
workstream's Phase 1 acceptance gate.

| typed_bucket | blocker_sum |
| --- | --- |
| technical_term | 86494 |
| morphology_register_artifact | 33800 |
| abbreviation_or_code | 20685 |
| proper_name | 15852 |
| taxon | 190 |

## Top 100 Blockers — Typed Bucket Distribution

Distribution of `typed_bucket` over the top 100 blocking ICs. The workstream's
Phase 1 falsifier triggers if this distribution does not concentrate in one or
two `typed_bucket` values.

| typed_bucket | count_in_top_100 |
| --- | --- |
| technical_term | 55 |
| morphology_register_artifact | 27 |
| abbreviation_or_code | 11 |
| proper_name | 7 |

## Top 60 Blocking ICs

Ranked by containment over admitted, non-truncated targets.

| ic_id | primary_alias | typed_bucket | containment_admitted | frequency | age_of_acquisition | concreteness |
| --- | --- | --- | --- | --- | --- | --- |
| ic:act | act | abbreviation_or_code | 3633 |  |  |  |
| ic:quality | quality | technical_term | 1933 | 4.269 | 8.780 | 2.180 |
| ic:showing | showing | morphology_register_artifact | 1795 | 4.493 |  | 3.060 |
| ic:part | part | technical_term | 1758 | 5.417 | 5.110 | 3.290 |
| ic:extent | extent | technical_term | 1755 | 3.610 | 10.720 | 1.440 |
| ic:can | can | abbreviation_or_code | 1566 |  |  |  |
| ic:energy | energy | proper_name | 1447 | 4.517 | 6.520 | 3.110 |
| ic:physical | physical | technical_term | 1404 | 4.434 | 8.160 | 3.310 |
| ic:work | work | technical_term | 1378 | 5.901 | 5.860 | 3.480 |
| ic:words | words | technical_term | 1268 | 5.086 |  |  |
| ic:form | form | technical_term | 1263 | 4.630 | 7.580 | 3.130 |
| ic:activity | activity | technical_term | 1199 | 4.110 | 6.470 | 2.720 |
| ic:more | more | proper_name | 1194 | 6.113 | 3.781 | 2.370 |
| ic:complete | complete | technical_term | 1192 | 4.713 | 6.580 | 2.700 |
| ic:life | life | technical_term | 1181 | 5.901 | 5.890 | 2.690 |
| ic:marked | marked | morphology_register_artifact | 1164 | 4.031 |  | 3.880 |
| ic:space | space | technical_term | 1152 | 4.819 | 5.670 | 3.540 |
| ic:force | force | technical_term | 1091 | 4.849 | 6.000 | 3.000 |
| ic:power | power | technical_term | 1084 | 5.173 | 7.480 | 2.040 |
| ic:quantity | quantity | technical_term | 1044 | 3.274 | 11.110 | 2.970 |
| ic:purpose | purpose | technical_term | 1032 | 4.545 | 8.370 | 1.520 |
| ic:according | according | morphology_register_artifact | 1022 | 4.621 | 8.449 | 1.630 |
| ic:intensity | intensity | technical_term | 985 | 3.399 | 11.260 | 2.140 |
| ic:unit | unit | technical_term | 974 | 4.558 | 7.790 | 3.770 |
| ic:satisfaction | satisfaction | technical_term | 951 | 3.843 | 9.530 | 1.900 |
| ic:strength | strength | technical_term | 943 | 4.567 | 6.210 | 2.960 |
| ic:law | law | abbreviation_or_code | 929 |  |  |  |
| ic:point | point | technical_term | 921 | 5.373 | 4.550 | 3.390 |
| ic:out | out | abbreviation_or_code | 896 |  |  |  |
| ic:writing | writing | morphology_register_artifact | 882 | 4.747 | 4.772 | 3.700 |
| ic:essential | essential | technical_term | 878 | 3.686 | 10.280 | 1.520 |
| ic:value | value | technical_term | 876 | 4.332 | 6.780 | 1.620 |
| ic:making | making | technical_term | 867 | 5.347 |  | 2.340 |
| ic:all | all | abbreviation_or_code | 846 |  |  |  |
| ic:respect | respect | technical_term | 844 | 4.854 | 8.500 | 2.040 |
| ic:surrounding | surrounding | morphology_register_artifact | 803 | 3.577 |  | 3.120 |
| ic:hope | hope | proper_name | 792 | 5.505 | 4.890 | 1.250 |
| ic:living | living | technical_term | 769 | 5.194 |  | 3.040 |
| ic:considered | considered | morphology_register_artifact | 764 | 4.365 |  | 1.970 |
| ic:expected | expected | morphology_register_artifact | 760 | 4.522 |  |  |
| ic:designed | designed | morphology_register_artifact | 753 | 4.244 |  | 2.930 |
| ic:environment | environment | morphology_register_artifact | 730 | 4.107 | 9.850 | 3.740 |
| ic:established | established | morphology_register_artifact | 722 | 3.911 |  | 1.970 |
| ic:government | government | morphology_register_artifact | 716 | 4.814 | 8.500 | 2.880 |
| ic:putting | putting | morphology_register_artifact | 696 | 4.832 |  |  |
| ic:substance | substance | technical_term | 693 | 3.854 | 9.680 | 3.440 |
| ic:support | support | technical_term | 693 | 4.705 | 8.530 | 2.830 |
| ic:expression | expression | technical_term | 686 | 4.106 | 6.940 | 2.540 |
| ic:accepted | accepted | morphology_register_artifact | 681 | 4.196 |  | 2.280 |
| ic:coming | coming | morphology_register_artifact | 663 | 5.721 | 4.772 | 2.070 |
| ic:practice | practice | technical_term | 661 | 4.659 | 6.240 | 2.520 |
| ic:relation | relation | technical_term | 658 | 3.980 | 8.110 | 2.110 |
| ic:drawing | drawing | morphology_register_artifact | 656 | 4.205 | 4.826 | 4.600 |
| ic:existing | existing | morphology_register_artifact | 650 | 3.287 | 8.650 | 2.000 |
| ic:military | military | technical_term | 645 | 4.615 | 8.200 | 4.000 |
| ic:specific | specific | technical_term | 639 | 4.250 | 9.280 | 2.180 |
| ic:authority | authority | technical_term | 632 | 4.326 | 7.500 | 2.340 |
| ic:highly | highly | morphology_register_artifact | 622 | 4.326 |  | 2.190 |
| ic:musical | musical | technical_term | 615 | 4.119 | 7.280 | 3.720 |
| ic:function | function | technical_term | 597 | 4.045 | 9.100 | 1.920 |

## Per-Typed-Bucket Top 20 Examples

### technical_term

| ic_id | primary_alias | containment_admitted | frequency | concreteness |
| --- | --- | --- | --- | --- |
| ic:quality | quality | 1933 | 4.269 | 2.180 |
| ic:part | part | 1758 | 5.417 | 3.290 |
| ic:extent | extent | 1755 | 3.610 | 1.440 |
| ic:physical | physical | 1404 | 4.434 | 3.310 |
| ic:work | work | 1378 | 5.901 | 3.480 |
| ic:words | words | 1268 | 5.086 |  |
| ic:form | form | 1263 | 4.630 | 3.130 |
| ic:activity | activity | 1199 | 4.110 | 2.720 |
| ic:complete | complete | 1192 | 4.713 | 2.700 |
| ic:life | life | 1181 | 5.901 | 2.690 |
| ic:space | space | 1152 | 4.819 | 3.540 |
| ic:force | force | 1091 | 4.849 | 3.000 |
| ic:power | power | 1084 | 5.173 | 2.040 |
| ic:quantity | quantity | 1044 | 3.274 | 2.970 |
| ic:purpose | purpose | 1032 | 4.545 | 1.520 |
| ic:intensity | intensity | 985 | 3.399 | 2.140 |
| ic:unit | unit | 974 | 4.558 | 3.770 |
| ic:satisfaction | satisfaction | 951 | 3.843 | 1.900 |
| ic:strength | strength | 943 | 4.567 | 2.960 |
| ic:point | point | 921 | 5.373 | 3.390 |

### morphology_register_artifact

| ic_id | primary_alias | containment_admitted | frequency | concreteness |
| --- | --- | --- | --- | --- |
| ic:showing | showing | 1795 | 4.493 | 3.060 |
| ic:marked | marked | 1164 | 4.031 | 3.880 |
| ic:according | according | 1022 | 4.621 | 1.630 |
| ic:writing | writing | 882 | 4.747 | 3.700 |
| ic:surrounding | surrounding | 803 | 3.577 | 3.120 |
| ic:considered | considered | 764 | 4.365 | 1.970 |
| ic:expected | expected | 760 | 4.522 |  |
| ic:designed | designed | 753 | 4.244 | 2.930 |
| ic:environment | environment | 730 | 4.107 | 3.740 |
| ic:established | established | 722 | 3.911 | 1.970 |
| ic:government | government | 716 | 4.814 | 2.880 |
| ic:putting | putting | 696 | 4.832 |  |
| ic:accepted | accepted | 681 | 4.196 | 2.280 |
| ic:coming | coming | 663 | 5.721 | 2.070 |
| ic:drawing | drawing | 656 | 4.205 | 4.600 |
| ic:existing | existing | 650 | 3.287 | 2.000 |
| ic:highly | highly | 622 | 4.326 | 2.190 |
| ic:physically | physically | 570 | 3.966 | 2.480 |
| ic:meaning | meaning | 567 | 4.572 | 1.850 |
| ic:belonging | belonging | 530 | 3.317 | 1.920 |

### abbreviation_or_code

| ic_id | primary_alias | containment_admitted | frequency | concreteness |
| --- | --- | --- | --- | --- |
| ic:act | act | 3633 |  |  |
| ic:can | can | 1566 |  |  |
| ic:law | law | 929 |  |  |
| ic:out | out | 896 |  |  |
| ic:all | all | 846 |  |  |
| ic:set | set | 589 |  |  |
| ic:basic | basic | 572 | 4.192 | 2.260 |
| ic:no | no | 550 | 6.775 | 2.450 |
| ic:end | end | 547 |  |  |
| ic:sex | sex | 491 |  |  |
| ic:do | do | 468 | 6.787 | 2.460 |
| ic:off | off | 407 |  |  |
| ic:man | man | 327 |  |  |
| ic:far | far | 324 |  |  |
| ic:pay | pay | 309 |  |  |
| ic:e | e | 274 |  |  |
| ic:art | art | 264 |  |  |
| ic:represent | represent | 250 | 4.181 | 2.120 |
| ic:gas | gas | 248 |  |  |
| ic:th | th | 242 |  |  |

### proper_name

| ic_id | primary_alias | containment_admitted | frequency | concreteness |
| --- | --- | --- | --- | --- |
| ic:energy | energy | 1447 | 4.517 | 3.110 |
| ic:more | more | 1194 | 6.113 | 2.370 |
| ic:hope | hope | 792 | 5.505 | 1.250 |
| ic:service | service | 509 | 4.902 | 2.210 |
| ic:word | word | 505 | 5.372 | 3.560 |
| ic:common | common | 472 | 4.649 | 2.920 |
| ic:alight | light | 469 | 5.217 | 4.210 |
| ic:nation | nation | 422 | 4.311 | 3.620 |
| ic:numbers | numbers | 407 | 4.597 |  |
| ic:acts | acts | 406 |  |  |
| ic:mass | mass | 394 | 4.237 | 3.440 |
| ic:young | young | 378 | 5.385 | 3.160 |
| ic:land | land | 365 | 4.945 | 4.570 |
| ic:born | born | 349 | 4.922 | 3.220 |
| ic:truth | truth | 317 | 5.283 | 1.960 |
| ic:earth | earth | 309 | 4.997 | 4.800 |
| ic:opposition | opposition | 290 | 3.485 | 2.250 |
| ic:center | center | 283 | 4.660 | 3.850 |
| ic:male | male | 280 | 4.530 | 4.450 |
| ic:worth | worth | 236 | 5.038 | 1.890 |

### taxon

| ic_id | primary_alias | containment_admitted | frequency | concreteness |
| --- | --- | --- | --- | --- |
| ic:sales | sales | 169 | 4.104 | 2.860 |
| ic:passer | passer | 4 | 2.292 |  |
| ic:germanic | Germanic | 3 | 2.070 |  |
| ic:alyssum | alyssum | 2 |  |  |
| ic:calamus | calamus | 2 |  |  |
| ic:cassia | cassia | 2 | 1.593 |  |
| ic:cornus | cornus | 2 |  |  |
| ic:adiantum | adiantum | 1 |  |  |
| ic:austronesian | Austronesian | 1 |  |  |
| ic:conium | conium | 1 |  |  |
| ic:filoviridae | filoviridae | 1 |  |  |
| ic:nipa | nipa | 1 |  |  |
| ic:phytolacca | phytolacca | 1 |  |  |

