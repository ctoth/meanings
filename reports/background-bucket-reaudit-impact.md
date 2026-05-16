# Background Bucket Re-audit Impact

BG Phase 4 A/B diff for `reports/background-bucket-reaudit-workstream.md`.

## Inputs

- Pre pressure table: `data\kernel-pressure-table.bg-pre.csv`
- Post pressure table: `data\kernel-pressure-table.csv`
- Unfolding index: `data\sense-unfolding-index.json`

## Augmented Layer

- Pre size: `14`
- Post size: `61`
- Added: `47` ICs
- Removed: `none`

## Closure Status — `closure_size <= 200`

| status | pre | post | delta |
| --- | --- | --- | --- |
| artifact | 8551 | 8147 | -404 |
| background | 3664 | 3177 | -487 |
| circular | 101 | 82 | -19 |
| closed | 2119 | 3044 | 925 |
| external | 450 | 435 | -15 |

- Closure rate pre: `0.1424` (`2119/14885`)
- Closure rate post: `0.2045` (`3044/14885`)
- Closure rate delta: `+6.21 pp`
- Artifact share pre: `0.5745` (`8551`)
- Artifact share post: `0.5473` (`8147`)
- Artifact share delta: `-2.71 pp`
- Background share pre: `0.2462` (`3664`)
- Background share post: `0.2134` (`3177`)
- Background share delta: `-3.27 pp`

## All Targets

- Closed under L0 only, pre: `2033`
- Closed under L0 only, post: `2033`
- Closed under augmented, pre: `2119`
- Closed under augmented, post: `3044`
- MGY pre: `6.1429` over `14` added ICs
- MGY post: `16.5738` over `61` added ICs

## Regression Gate

- Regressed sense count (closed pre, not closed post): `0`

## Bucket Transitions

| from | to | count |
| --- | --- | --- |
| candidate_background | base_promotable_terminal_common | 121 |

Total ICs with changed `pressure_bucket`: `121`.

## Top 60 Promoted ICs

| ic_id | primary_alias | pre_pressure_bucket | frequency_post | age_of_acquisition_post | concreteness_post |
| --- | --- | --- | --- | --- | --- |
| ic:so | so | candidate_background | 6.627197751579461 | 5.14536 | 1.42 |
| ic:aright | right | candidate_background | 6.602376646359637 | 4.346085 | 3.47 |
| ic:like | like | candidate_background | 6.601353592943822 | 3.6853510000000003 | 1.89 |
| ic:up | up | candidate_background | 6.564072702809289 | 2.918047 | 3.83 |
| ic:about | about | candidate_background | 6.559491539198379 | 5.070761000000001 | 1.77 |
| ic:come | come | candidate_background | 6.496472254640901 | 3.32 | 2.72 |
| ic:want | want | candidate_background | 6.4401868823515045 | 4.16 | 1.93 |
| ic:going | going | candidate_background | 6.326418485363236 | 5.411785000000001 | 2.69 |
| ic:back | back | candidate_background | 6.302422401748658 | 5.3052150000000005 | 4.33 |
| ic:time | time | candidate_background | 6.29136050297892 | 5.16 | 3.07 |
| ic:make | make | candidate_background | 6.141720156407864 | 4.68 | 2.67 |
| ic:over | over | candidate_background | 6.121067135292526 | 5.571640000000001 | 2.46 |
| ic:very | very | candidate_background | 6.093272155268496 | 4.900249000000001 | 1.43 |
| ic:give | give | candidate_background | 6.066788831224598 | 4.28 | 2.83 |
| ic:sure | sure | candidate_background | 6.040735067507489 | 4.85 | 1.73 |
| ic:thing | thing | candidate_background | 6.036307065878121 | 4.58 | 3.17 |
| ic:first | first | candidate_background | 5.9239876256550925 | 4.388713 | 2.76 |
| ic:find | find | candidate_background | 5.918995094519236 | 5.78 | 2.63 |
| ic:great | great | candidate_background | 5.913685237688773 | 5.05 | 1.81 |
| ic:thought | thought | candidate_background | 5.907079076170835 | 5.891350000000001 | 1.97 |
| ic:before | before | candidate_background | 5.899310611470681 | 5.454413000000001 | 1.96 |
| ic:better | better | candidate_background | 5.899235545446485 | 5.017476 | 1.91 |
| ic:again | again | candidate_background | 5.898527141458522 | 5.784780000000001 | 2.0 |
| ic:still | still | candidate_background | 5.896340991412325 | 5.262587000000001 | 3.46 |
| ic:home | home | candidate_background | 5.888343270486459 | 3.8665200000000004 | 4.11 |
| ic:last | last | candidate_background | 5.858613278485652 | 4.346085 | 3.04 |
| ic:keep | keep | candidate_background | 5.846286957993113 | 4.42 | 2.37 |
| ic:after | after | candidate_background | 5.833575592240191 | 5.997920000000001 | 2.12 |
| ic:long | long | candidate_background | 5.828821617275062 | 4.239515000000001 | 3.18 |
| ic:money | money | candidate_background | 5.806116190004838 | 5.11 | 4.54 |
| ic:feel | feel | candidate_background | 5.796848382228567 | 5.11 | 2.28 |
| ic:leave | leave | candidate_background | 5.748154617518834 | 5.58 | 2.53 |
| ic:through | through | candidate_background | 5.739410755667382 | 5.816751 | 2.9 |
| ic:wrong | wrong | candidate_background | 5.7180036891797865 | 4.22 | 1.83 |
| ic:house | house | candidate_background | 5.710384004194202 | 3.16 | 5.0 |
| ic:care | care | candidate_background | 5.685391797807753 | 5.65 | 2.33 |
| ic:mind | mind | candidate_background | 5.684812328687 | 5.37 | 2.5 |
| ic:left | left | candidate_background | 5.684671734810117 | 5.571640000000001 | 3.7 |
| ic:mother | mother | candidate_background | 5.680592329993564 | 2.63 | 4.6 |
| ic:next | next | candidate_background | 5.655276883423602 | 4.346085 | 2.56 |
| ic:real | real | candidate_background | 5.645635007283323 | 4.95 | 2.5 |
| ic:room | room | candidate_background | 5.64239226008616 | 4.22 | 4.79 |
| ic:today | today | candidate_background | 5.636717421514323 | 4.772365000000001 | 2.57 |
| ic:move | move | candidate_background | 5.620743547015648 | 4.62 | 3.25 |
| ic:found | found | candidate_background | 5.5971210076205855 | 5.14536 | 2.53 |
| ic:together | together | candidate_background | 5.583069752993248 | 5.944635000000001 | 2.74 |
| ic:head | head | candidate_background | 5.569397518200379 | 3.42 | 4.75 |
| ic:many | many | candidate_background | 5.555043990717209 | 4.601853000000001 | 2.37 |
| ic:idea | idea | candidate_background | 5.5545699218109466 | 5.95 | 1.61 |
| ic:play | play | candidate_background | 5.549080607051831 | 4.1 | 3.24 |
| ic:meet | meet | candidate_background | 5.546309709948331 | 4.74 | 3.0 |
| ic:open | open | candidate_background | 5.505139348307253 | 5.0 | 3.21 |
| ic:causa | cause | candidate_background | 5.49084841307908 | 5.84 | 2.43 |
| ic:hard | hard | candidate_background | 5.487761455741685 | 4.39 | 3.76 |
| ic:turn | turn | candidate_background | 5.485820905230154 | 4.11 | 3.44 |
| ic:both | both | candidate_background | 5.46974561823847 | 4.772365000000001 | 2.97 |
| ic:face | face | candidate_background | 5.4605672710785385 | 3.75 | 4.87 |
| ic:second | second | candidate_background | 5.4536212608899834 | 4.68 | 3.3 |
| ic:hand | hand | candidate_background | 5.4460450243514344 | 2.74 | 4.72 |
| ic:check | check | candidate_background | 5.4450085215159945 | 5.53 | 4.11 |

