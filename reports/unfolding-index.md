# Sense Unfolding Index

This is a kernel-only prototype over the OEWN IC-fallback sense graph. It tests whether the P2 seed can unfold cyclic definitions into finite IC closures.

## Summary

- Output: `data\sense-unfolding-index.json`
- Indexed kernel senses: `20744`
- Residual unlayered kernel senses: `0`
- Missing predecessor closure references: `0`
- Same-IC direct definition edges: `1889`
- Median closure size: `6.0`
- P90 closure size: `157`
- Max closure size: `1591`
- Median seed-closure size: `5.0`
- P90 seed-closure size: `100`
- Max seed-closure size: `751`
- Rows with truncated closure IDs: `433`
- Rows with truncated seed-closure IDs: `77`

## Layer Histogram

| layer | count |
| --- | --- |
| 0 | 6293 |
| 1 | 2801 |
| 2 | 1741 |
| 3 | 1270 |
| 4 | 1006 |
| 5 | 879 |
| 6 | 726 |
| 7 | 583 |
| 8 | 524 |
| 9 | 468 |
| 10 | 513 |
| 11 | 483 |
| 12 | 388 |
| 13 | 352 |
| 14 | 312 |
| 15 | 261 |
| 16 | 211 |
| 17 | 222 |
| 18 | 236 |
| 19 | 212 |
| 20 | 187 |
| 21 | 193 |
| 22 | 147 |
| 23 | 114 |
| 24 | 89 |
| 25 | 94 |
| 26 | 78 |
| 27 | 85 |
| 28 | 56 |
| 29 | 41 |
| 30 | 27 |
| 31 | 20 |
| 32 | 13 |
| 33 | 10 |
| 34 | 11 |
| 35 | 5 |
| 36 | 4 |
| 37 | 3 |
| 38 | 5 |
| 39 | 4 |
| 40 | 2 |
| 41 | 1 |
| 42 | 2 |
| 43 | 2 |
| 44 | 2 |
| 45 | 2 |
| 46 | 8 |
| 47 | 4 |
| 48 | 6 |
| 49 | 5 |
| 50 | 6 |
| 51 | 15 |
| 52 | 10 |
| 53 | 6 |
| 54 | 4 |
| 55 | 2 |

## Admission Decisions

| admission_decision | count |
| --- | --- |
| admit | 15872 |
| not_admitted_or_unavailable | 4872 |

## Largest Closures

| sense_id | ic_id | label | pos | layer | closure_size | seed_closure_size | admission_decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| oewn-hypertensin__1.06.00.. | ic:hypertensin | hypertensin | n | 29 | 1591 | 751 | not_admitted_or_unavailable |
| oewn-vasoconstrictor__1.06.00.. | ic:vasoconstrictor | vasoconstrictor | n | 28 | 1589 | 750 | not_admitted_or_unavailable |
| oewn-vasopressin__1.08.00.. | ic:vasopressin | vasopressin | n | 27 | 1516 | 722 | not_admitted_or_unavailable |
| oewn-pitressin__1.08.00.. | ic:pitressin | pitressin | n | 26 | 1515 | 722 | not_admitted_or_unavailable |
| oewn-steatorrhea__1.26.00.. | ic:steatorrhea | steatorrhea | n | 51 | 1399 | 704 | admit |
| oewn-quinine__1.06.00.. | ic:quinine | quinine | n | 32 | 1386 | 677 | not_admitted_or_unavailable |
| oewn-prometheus__1.18.00.. | ic:prometheus | prometheus | n | 30 | 1320 | 673 | not_admitted_or_unavailable |
| oewn-fluorapatite__1.27.00.. | ic:fluorapatite | fluorapatite | n | 46 | 1319 | 679 | admit |
| oewn-wood-rat__1.05.00.. | ic:wood_rat | wood_rat | n | 52 | 1249 | 643 | not_admitted_or_unavailable |
| oewn-vascular_hemophilia__1.26.00.. | ic:vascular_hemophilia | vascular_hemophilia | n | 40 | 1221 | 629 | not_admitted_or_unavailable |
| oewn-tomato_hornworm__1.05.00.. | ic:tomato_hornworm | tomato_hornworm | n | 23 | 1159 | 631 | not_admitted_or_unavailable |
| oewn-kinetoscope__1.06.00.. | ic:kinetoscope | kinetoscope | n | 20 | 1156 | 606 | not_admitted_or_unavailable |
| oewn-white_chocolate__1.13.00.. | ic:white_chocolate | white_chocolate | n | 31 | 1125 | 585 | not_admitted_or_unavailable |
| oewn-malpighian_body__1.08.00.. | ic:malpighian_body | malpighian_body | n | 27 | 1117 | 568 | not_admitted_or_unavailable |
| oewn-pyramid__1.06.00.. | ic:pyramid | pyramid | n | 38 | 1117 | 599 | admit |
| oewn-proteolytic_enzyme__1.27.00.. | ic:proteolytic_enzyme | proteolytic_enzyme | n | 54 | 1114 | 570 | not_admitted_or_unavailable |
| oewn-xenopus__1.05.00.. | ic:xenopus | xenopus | n | 55 | 1105 | 567 | not_admitted_or_unavailable |
| oewn-malaria__1.26.00.. | ic:malaria | malaria | n | 31 | 1104 | 577 | admit |
| oewn-african_clawed_frog__1.05.00.. | ic:african_clawed_frog | african_clawed_frog | n | 54 | 1103 | 566 | not_admitted_or_unavailable |
| oewn-warhead__1.06.00.. | ic:warhead | warhead | n | 34 | 1102 | 574 | not_admitted_or_unavailable |
| oewn-pouch__1.08.00.. | ic:pouch | pouch | n | 31 | 1101 | 570 | admit |
| oewn-skipjack_tuna__1.05.00.. | ic:skipjack_tuna | skipjack_tuna | n | 50 | 1101 | 565 | not_admitted_or_unavailable |
| oewn-recessive__1.08.00.. | ic:recessive | recessive | n | 39 | 1096 | 578 | admit |
| oewn-olive__1.20.00.. | ic:olive | olive | n | 34 | 1092 | 575 | admit |
| oewn-bowman-ap-s_capsule__1.08.00.. | ic:bowmans_capsule | bowmans_capsule | n | 26 | 1085 | 555 | not_admitted_or_unavailable |
| oewn-tuna__1.05.01.. | ic:tuna | tuna | n | 49 | 1081 | 559 | admit |
| oewn-fat_metabolism__1.22.00.. | ic:fat_metabolism | fat_metabolism | n | 50 | 1078 | 584 | not_admitted_or_unavailable |
| oewn-carob_tree__1.20.00.. | ic:carob_tree | carob_tree | n | 34 | 1065 | 564 | not_admitted_or_unavailable |
| oewn-delaware__1.18.00.. | ic:delaware | delaware | n | 40 | 1053 | 566 | not_admitted_or_unavailable |
| oewn-allele__1.08.00.. | ic:allele | allele | n | 38 | 1051 | 564 | not_admitted_or_unavailable |
| oewn-guided_missile__1.06.00.. | ic:guided_missile | guided_missile | n | 33 | 1049 | 550 | not_admitted_or_unavailable |
| oewn-cough__1.26.00.. | ic:cough | cough | n | 30 | 1048 | 553 | admit |
| oewn-grape_fern__1.20.00.. | ic:grape_fern | grape_fern | n | 28 | 1048 | 545 | not_admitted_or_unavailable |
| oewn-chimera__1.18.00.. | ic:chimaera | chimera | n | 51 | 1039 | 554 | admit |
| oewn-brachial_vein__1.08.00.. | ic:brachial_vein | brachial_vein | n | 33 | 1036 | 558 | not_admitted_or_unavailable |
| oewn-apatite__1.27.00.. | ic:apatite | apatite | n | 45 | 1033 | 565 | admit |
| oewn-brachial_artery__1.08.00.. | ic:brachial_artery | brachial_artery | n | 32 | 1032 | 556 | not_admitted_or_unavailable |
| oewn-medea__1.18.00.. | ic:medea | medea | n | 39 | 1030 | 551 | not_admitted_or_unavailable |
| oewn-sacral__3.01.00.. | ic:sacral | sacral | a | 54 | 1030 | 541 | admit |
| oewn-sacrum__1.08.00.. | ic:sacrum | sacrum | n | 53 | 1029 | 541 | not_admitted_or_unavailable |

## Largest Seed Closures

| sense_id | ic_id | label | pos | layer | closure_size | seed_closure_size | admission_decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| oewn-hypertensin__1.06.00.. | ic:hypertensin | hypertensin | n | 29 | 1591 | 751 | not_admitted_or_unavailable |
| oewn-vasoconstrictor__1.06.00.. | ic:vasoconstrictor | vasoconstrictor | n | 28 | 1589 | 750 | not_admitted_or_unavailable |
| oewn-pitressin__1.08.00.. | ic:pitressin | pitressin | n | 26 | 1515 | 722 | not_admitted_or_unavailable |
| oewn-vasopressin__1.08.00.. | ic:vasopressin | vasopressin | n | 27 | 1516 | 722 | not_admitted_or_unavailable |
| oewn-steatorrhea__1.26.00.. | ic:steatorrhea | steatorrhea | n | 51 | 1399 | 704 | admit |
| oewn-fluorapatite__1.27.00.. | ic:fluorapatite | fluorapatite | n | 46 | 1319 | 679 | admit |
| oewn-quinine__1.06.00.. | ic:quinine | quinine | n | 32 | 1386 | 677 | not_admitted_or_unavailable |
| oewn-prometheus__1.18.00.. | ic:prometheus | prometheus | n | 30 | 1320 | 673 | not_admitted_or_unavailable |
| oewn-wood-rat__1.05.00.. | ic:wood_rat | wood_rat | n | 52 | 1249 | 643 | not_admitted_or_unavailable |
| oewn-tomato_hornworm__1.05.00.. | ic:tomato_hornworm | tomato_hornworm | n | 23 | 1159 | 631 | not_admitted_or_unavailable |
| oewn-vascular_hemophilia__1.26.00.. | ic:vascular_hemophilia | vascular_hemophilia | n | 40 | 1221 | 629 | not_admitted_or_unavailable |
| oewn-kinetoscope__1.06.00.. | ic:kinetoscope | kinetoscope | n | 20 | 1156 | 606 | not_admitted_or_unavailable |
| oewn-pyramid__1.06.00.. | ic:pyramid | pyramid | n | 38 | 1117 | 599 | admit |
| oewn-white_chocolate__1.13.00.. | ic:white_chocolate | white_chocolate | n | 31 | 1125 | 585 | not_admitted_or_unavailable |
| oewn-fat_metabolism__1.22.00.. | ic:fat_metabolism | fat_metabolism | n | 50 | 1078 | 584 | not_admitted_or_unavailable |
| oewn-recessive__1.08.00.. | ic:recessive | recessive | n | 39 | 1096 | 578 | admit |
| oewn-malaria__1.26.00.. | ic:malaria | malaria | n | 31 | 1104 | 577 | admit |
| oewn-olive__1.20.00.. | ic:olive | olive | n | 34 | 1092 | 575 | admit |
| oewn-warhead__1.06.00.. | ic:warhead | warhead | n | 34 | 1102 | 574 | not_admitted_or_unavailable |
| oewn-pouch__1.08.00.. | ic:pouch | pouch | n | 31 | 1101 | 570 | admit |
| oewn-proteolytic_enzyme__1.27.00.. | ic:proteolytic_enzyme | proteolytic_enzyme | n | 54 | 1114 | 570 | not_admitted_or_unavailable |
| oewn-malpighian_body__1.08.00.. | ic:malpighian_body | malpighian_body | n | 27 | 1117 | 568 | not_admitted_or_unavailable |
| oewn-xenopus__1.05.00.. | ic:xenopus | xenopus | n | 55 | 1105 | 567 | not_admitted_or_unavailable |
| oewn-african_clawed_frog__1.05.00.. | ic:african_clawed_frog | african_clawed_frog | n | 54 | 1103 | 566 | not_admitted_or_unavailable |
| oewn-delaware__1.18.00.. | ic:delaware | delaware | n | 40 | 1053 | 566 | not_admitted_or_unavailable |
| oewn-apatite__1.27.00.. | ic:apatite | apatite | n | 45 | 1033 | 565 | admit |
| oewn-skipjack_tuna__1.05.00.. | ic:skipjack_tuna | skipjack_tuna | n | 50 | 1101 | 565 | not_admitted_or_unavailable |
| oewn-allele__1.08.00.. | ic:allele | allele | n | 38 | 1051 | 564 | not_admitted_or_unavailable |
| oewn-carob_tree__1.20.00.. | ic:carob_tree | carob_tree | n | 34 | 1065 | 564 | not_admitted_or_unavailable |
| oewn-tuna__1.05.01.. | ic:tuna | tuna | n | 49 | 1081 | 559 | admit |
| oewn-brachial_vein__1.08.00.. | ic:brachial_vein | brachial_vein | n | 33 | 1036 | 558 | not_admitted_or_unavailable |
| oewn-brachial_artery__1.08.00.. | ic:brachial_artery | brachial_artery | n | 32 | 1032 | 556 | not_admitted_or_unavailable |
| oewn-bowman-ap-s_capsule__1.08.00.. | ic:bowmans_capsule | bowmans_capsule | n | 26 | 1085 | 555 | not_admitted_or_unavailable |
| oewn-chimera__1.18.00.. | ic:chimaera | chimera | n | 51 | 1039 | 554 | admit |
| oewn-cough__1.26.00.. | ic:cough | cough | n | 30 | 1048 | 553 | admit |
| oewn-medea__1.18.00.. | ic:medea | medea | n | 39 | 1030 | 551 | not_admitted_or_unavailable |
| oewn-guided_missile__1.06.00.. | ic:guided_missile | guided_missile | n | 33 | 1049 | 550 | not_admitted_or_unavailable |
| oewn-star-thistle__1.20.00.. | ic:star_thistle | star_thistle | n | 34 | 1025 | 550 | not_admitted_or_unavailable |
| oewn-york__1.14.00.. | ic:york | york | n | 39 | 1013 | 548 | not_admitted_or_unavailable |
| oewn-grape_fern__1.20.00.. | ic:grape_fern | grape_fern | n | 28 | 1048 | 545 | not_admitted_or_unavailable |
