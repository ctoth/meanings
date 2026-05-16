# Artifact Bucket Re-audit Impact

Phase 4 A/B diff for `reports/artifact-bucket-reaudit-workstream.md`.

## Inputs

- Pre pressure table: `data\kernel-pressure-table.pre.csv`
- Post pressure table: `data\kernel-pressure-table.csv`
- Unfolding index: `data\sense-unfolding-index.json`

## Augmented Layer

- Pre augmented layer size: `9`
- Post augmented layer size: `14`
- Added by R1 norm join: `['ic:ask', 'ic:called', 'ic:do', 'ic:has', 'ic:than']`
- Removed: `none`

## Closure Status — `closure_size <= 200`

| status | pre | post | delta |
| --- | --- | --- | --- |
| artifact | 9445 | 8551 | -894 |
| background | 3048 | 3664 | 616 |
| circular | 77 | 101 | 24 |
| closed | 2110 | 2119 | 9 |
| external | 205 | 450 | 245 |

- Closure rate pre: `0.1418` (`2110/14885`)
- Closure rate post: `0.1424` (`2119/14885`)
- Closure rate delta: `+0.06 pp`
- Artifact share pre: `0.6345` (`9445`)
- Artifact share post: `0.5745` (`8551`)
- Artifact share delta: `-6.01 pp`

## All Targets

- Closed under L0 only, pre: `2033`
- Closed under L0 only, post: `2033`
- Closed under augmented, pre: `2110`
- Closed under augmented, post: `2119`
- MGY pre: `8.5556` over `9` added ICs
- MGY post: `6.1429` over `14` added ICs

## Regression Gate

- Regressed sense count (closed pre, not closed post): `0`

## Bucket Transitions

| from | to | count |
| --- | --- | --- |
| resource_artifact | external_substrate | 780 |
| resource_artifact | common_vocabulary | 165 |
| resource_artifact | assembler_helper | 3 |
| resource_artifact | candidate_background | 3 |
| circular_dependency | assembler_helper | 2 |

Total ICs with changed `pressure_bucket`: `953`.

## Top 50 Migrated ICs by Frequency

| ic_id | primary_alias | pre_pressure_bucket | post_pressure_bucket | typed_bucket_post | frequency_post | high_frequency_post |
| --- | --- | --- | --- | --- | --- | --- |
| ic:s | s | resource_artifact | common_vocabulary | abbreviation_or_code | 7.316033195866643 | True |
| ic:t | t | resource_artifact | common_vocabulary | abbreviation_or_code | 7.1571389241459435 | True |
| ic:m | m | resource_artifact | common_vocabulary | abbreviation_or_code | 6.8274396270538364 | True |
| ic:don | don | resource_artifact | external_substrate | resource_specific_tail | 6.798455512004648 | True |
| ic:do | do | resource_artifact | assembler_helper | plausible_missing_primitive | 6.787261912174824 | True |
| ic:re | re | resource_artifact | common_vocabulary | abbreviation_or_code | 6.784696459714489 | True |
| ic:no | no | resource_artifact | common_vocabulary | abbreviation_or_code | 6.7754927459819 | True |
| ic:was | was | resource_artifact | external_substrate | resource_specific_tail | 6.751817351021102 | True |
| ic:can | can | resource_artifact | common_vocabulary | abbreviation_or_code | 6.719354331308571 | True |
| ic:all | all | resource_artifact | common_vocabulary | abbreviation_or_code | 6.712212420338913 | True |
| ic:get | get | resource_artifact | common_vocabulary | abbreviation_or_code | 6.66062849230587 | True |
| ic:here | here | resource_artifact | common_vocabulary | proper_name | 6.655049247524397 | True |
| ic:out | out | resource_artifact | common_vocabulary | abbreviation_or_code | 6.586591270205694 | True |
| ic:if | if | resource_artifact | common_vocabulary | abbreviation_or_code | 6.5485783393612635 | True |
| ic:got | got | resource_artifact | external_substrate | resource_specific_tail | 6.518774132983205 | True |
| ic:oh | oh | resource_artifact | common_vocabulary | abbreviation_or_code | 6.516579509125894 | True |
| ic:now | now | resource_artifact | common_vocabulary | abbreviation_or_code | 6.504910740080232 | True |
| ic:how | how | resource_artifact | external_substrate | resource_specific_tail | 6.484591104992653 | True |
| ic:good | good | resource_artifact | common_vocabulary | technical_term | 6.4160709261850934 | True |
| ic:see | see | resource_artifact | common_vocabulary | abbreviation_or_code | 6.407091750205684 | True |
| ic:let | let | resource_artifact | external_substrate | resource_specific_tail | 6.383085947944817 | True |
| ic:why | why | resource_artifact | external_substrate | resource_specific_tail | 6.351352121454454 | True |
| ic:yes | yes | resource_artifact | external_substrate | resource_specific_tail | 6.299735474541391 | True |
| ic:d | d | resource_artifact | common_vocabulary | abbreviation_or_code | 6.29759789968533 | True |
| ic:take | take | resource_artifact | common_vocabulary | technical_term | 6.276109356519957 | True |
| ic:man | man | resource_artifact | common_vocabulary | abbreviation_or_code | 6.265580655533629 | True |
| ic:hey | hey | resource_artifact | external_substrate | resource_specific_tail | 6.236711448108155 | True |
| ic:tell | tell | resource_artifact | common_vocabulary | proper_name | 6.23606998593794 | True |
| ic:us | us | resource_artifact | common_vocabulary | abbreviation_or_code | 6.228744801154089 | True |
| ic:had | had | resource_artifact | external_substrate | resource_specific_tail | 6.223663089587635 | True |
| ic:say | say | resource_artifact | external_substrate | resource_specific_tail | 6.21419623892925 | True |
| ic:really | really | resource_artifact | common_vocabulary | morphology_register_artifact | 6.1755466677612745 | True |
| ic:down | down | resource_artifact | common_vocabulary | proper_name | 6.172676305490812 | True |
| ic:little | little | resource_artifact | common_vocabulary | technical_term | 6.159696263817038 | True |
| ic:too | too | resource_artifact | external_substrate | resource_specific_tail | 6.136628069569555 | True |
| ic:more | more | resource_artifact | common_vocabulary | proper_name | 6.112882339773854 | True |
| ic:need | need | resource_artifact | common_vocabulary | technical_term | 6.111647782919253 | True |
| ic:off | off | resource_artifact | common_vocabulary | abbreviation_or_code | 6.071113092805138 | True |
| ic:mr | mr | resource_artifact | common_vocabulary | abbreviation_or_code | 6.070701387889379 | True |
| ic:has | has | resource_artifact | assembler_helper | resource_specific_tail | 6.053994844230642 | True |
| ic:am | am | resource_artifact | common_vocabulary | abbreviation_or_code | 6.043413452359134 | True |
| ic:sir | sir | resource_artifact | external_substrate | resource_specific_tail | 5.9837021356959355 | True |
| ic:help | help | resource_artifact | common_vocabulary | technical_term | 5.963728665708805 | True |
| ic:god | god | resource_artifact | common_vocabulary | abbreviation_or_code | 5.955176933134951 | True |
| ic:night | night | resource_artifact | common_vocabulary | proper_name | 5.936951708951002 | True |
| ic:call | call | resource_artifact | common_vocabulary | proper_name | 5.934615117073616 | True |
| ic:put | put | resource_artifact | common_vocabulary | abbreviation_or_code | 5.917681413262269 | True |
| ic:day | day | resource_artifact | common_vocabulary | abbreviation_or_code | 5.903493734796248 | True |
| ic:work | work | resource_artifact | common_vocabulary | technical_term | 5.90142855136968 | True |
| ic:life | life | resource_artifact | common_vocabulary | technical_term | 5.9006809644708715 | True |

