# Background Bucket Audit

Read-only Phase 1 inventory of `candidate_background` and `external_substrate` ICs in `data/kernel-pressure-table.csv`.

## Inputs

- Pressure table: `data\kernel-pressure-table.csv`
- Unfolding index: `data\sense-unfolding-index.json`

## Bucket Summary

| pressure_bucket | rows | blocking | non_blocking | with_freq | with_aoa | with_conc | freq_med | aoa_med | conc_med | high_freq | early_aoa | high_conc | all_three | p2_seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_background | 46155 | 4101 | 42054 | 3501 | 2443 | 2971 | 3.105 | 9.750 | 2.790 | 181 | 335 | 629 | 33 | 1668 |
| external_substrate | 35321 | 3258 | 32063 | 2967 | 2574 | 2866 | 3.499 | 9.170 | 3.000 | 128 | 376 | 725 | 25 | 0 |

## Top-100 vs Bottom-100 Norm Contrast

If the top-100 blockers do not have meaningfully higher frequency / earlier
AOA / higher concreteness than the bottom-100 (among ICs with at least one
blocked target), the promote-by-norms hypothesis fails.

| pressure_bucket | top100_freq_med | bot100_freq_med | top100_aoa_med | bot100_aoa_med | top100_conc_med | bot100_conc_med | top100_p2_seed | bot100_p2_seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_background | 4.867 | 2.823 | 6.320 | 10.415 | 2.740 | 2.480 | 98 | 11 |
| external_substrate | 4.062 | 3.364 | 8.840 | 8.585 | 2.430 | 3.430 | 0 | 0 |

## Top 50 Blocking ICs - `candidate_background`

| ic_id | primary_alias | containment_admitted | p2_seed | typed_bucket | freq | aoa | conc | norms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ic:amount | amount | 2109 | True | plausible_missing_primitive | 4.393 | 6.630 | 2.740 | - |
| ic:time | time | 2003 | True | plausible_missing_primitive | 6.291 | 5.160 | 3.070 | HF+EA |
| ic:capable | capable | 1844 | True | plausible_missing_primitive | 4.318 | 9.160 | 2.210 | - |
| ic:event | event | 1802 | True | plausible_missing_primitive | 4.421 | 7.810 | 2.690 | - |
| ic:degree | degree | 1582 | True | plausible_missing_primitive | 4.173 | 10.350 | 3.000 | - |
| ic:mind | mind | 1548 | True |  | 5.685 | 5.370 | 2.500 | HF+EA |
| ic:body | body | 1504 | True |  | 5.291 | 4.280 | 4.790 | HF+EA+HC |
| ic:property | property | 1468 | True | plausible_missing_primitive | 4.522 | 8.160 | 3.900 | - |
| ic:feeling | feeling | 1458 | True |  | 5.225 | 5.305 | 1.680 | HF+EA |
| ic:things | things | 1423 | True | plausible_missing_primitive | 5.840 |  |  | HF |
| ic:knowledge | knowledge | 1384 | True | plausible_missing_primitive | 4.407 | 7.680 | 1.730 | - |
| ic:group | group | 1361 | True |  | 4.867 | 5.940 | 4.120 | EA+HC |
| ic:nature | nature | 1345 | True | plausible_missing_primitive | 4.654 | 6.160 | 2.920 | - |
| ic:whole | whole | 1242 | True | plausible_missing_primitive | 5.585 | 6.890 | 3.250 | HF |
| ic:general | general | 1235 | True | plausible_missing_primitive | 5.062 | 8.050 | 1.620 | HF |
| ic:size | size | 1177 | True |  | 4.664 | 4.840 | 3.130 | EA |
| ic:mental | mental | 1173 | True | plausible_missing_primitive | 4.293 | 8.840 | 2.040 | - |
| ic:regard | regard | 1171 | True | plausible_missing_primitive | 3.867 | 10.200 | 1.790 | - |
| ic:small | small | 1140 | True |  | 5.096 | 3.220 | 3.220 | HF+EA |
| ic:feelings | feelings | 1134 | True |  | 4.760 |  |  | - |
| ic:done | done | 1129 | True | plausible_missing_primitive | 5.685 |  | 2.000 | HF |
| ic:up | up | 1120 | True |  | 6.564 | 2.918 | 3.830 | HF+EA |
| ic:attention | attention | 1119 | True | plausible_missing_primitive | 4.994 | 6.780 | 2.300 | - |
| ic:change | change | 1104 | True | plausible_missing_primitive | 5.380 | 4.260 | 2.890 | HF+EA |
| ic:information | information | 1077 | True | plausible_missing_primitive | 4.951 | 7.190 | 2.870 | - |
| ic:strong | strong | 1057 | True |  | 4.938 | 4.580 | 3.140 | EA |
| ic:characteristic | characteristic | 1045 | True | plausible_missing_primitive | 3.077 | 10.470 | 2.380 | - |
| ic:great | great | 1017 | True |  | 5.914 | 5.050 | 1.810 | HF+EA |
| ic:make | make | 1010 | True |  | 6.142 | 4.680 | 2.670 | HF+EA |
| ic:skill | skill | 978 | True | plausible_missing_primitive | 3.899 | 6.800 | 2.170 | - |
| ic:give | give | 975 | True |  | 6.067 | 4.280 | 2.830 | HF+EA |
| ic:causing | causing | 939 | True | plausible_missing_primitive | 3.993 |  | 1.550 | - |
| ic:large | large | 937 | True |  | 4.617 | 5.740 | 3.370 | EA |
| ic:over | over | 926 | True |  | 6.121 | 5.572 | 2.460 | HF+EA |
| ic:ability | ability | 922 | True | plausible_missing_primitive | 4.284 | 8.840 | 1.810 | - |
| ic:relative | relative | 898 | True | plausible_missing_primitive | 3.892 | 6.470 | 2.970 | - |
| ic:within | within | 893 | True | plausible_missing_primitive | 4.772 | 7.650 | 2.810 | - |
| ic:conditions | conditions | 892 | True | plausible_missing_primitive | 4.103 |  |  | - |
| ic:condition | condition | 887 | True | plausible_missing_primitive | 4.579 | 8.420 | 2.150 | - |
| ic:full | full | 884 | True |  | 5.222 | 4.240 | 3.590 | HF+EA |
| ic:together | together | 879 | True |  | 5.583 | 5.945 | 2.740 | HF+EA |
| ic:especial | special | 877 | True |  | 5.171 | 5.000 | 1.760 | HF+EA |
| ic:under | under | 877 | True |  | 5.418 | 5.891 | 3.450 | HF+EA |
| ic:different | different | 865 | True |  | 5.321 | 5.500 | 1.970 | HF+EA |
| ic:direction | direction | 840 | True | plausible_missing_primitive | 4.381 | 6.680 | 2.790 | - |
| ic:given | given | 837 | True | plausible_missing_primitive | 4.978 |  | 2.330 | - |
| ic:branch | branch | 823 | True |  | 4.004 | 5.110 | 4.900 | EA+HC |
| ic:values | values | 812 | True | plausible_missing_primitive | 3.928 |  |  | - |
| ic:bingle | bingle | 801 | True |  |  |  |  | - |
| ic:surface | surface | 794 | True | plausible_missing_primitive | 4.261 | 8.860 | 4.260 | HC |

## Top 50 Blocking ICs - `external_substrate`

| ic_id | primary_alias | containment_admitted | p2_seed | typed_bucket | freq | aoa | conc | norms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ic:intended | intended | 1393 | False | resource_specific_tail | 4.071 |  | 1.850 | - |
| ic:occurrence | occurrence | 1005 | False | resource_specific_tail | 3.077 | 11.440 | 2.570 | - |
| ic:total | total | 848 | False | plausible_missing_primitive | 4.575 | 6.830 | 2.800 | - |
| ic:location | location | 749 | False | plausible_missing_primitive | 4.394 | 6.860 | 3.000 | - |
| ic:totality | totality | 728 | False | resource_specific_tail | 2.195 | 12.000 | 1.920 | - |
| ic:pleasing | pleasing | 634 | False | resource_specific_tail | 3.195 | 7.280 | 2.560 | - |
| ic:outcome | outcome | 624 | False | resource_specific_tail | 3.597 | 9.530 | 2.270 | - |
| ic:magnitude | magnitude | 596 | False | resource_specific_tail | 3.161 | 12.300 | 2.430 | - |
| ic:possible | possible | 535 | False | plausible_missing_primitive | 5.057 | 7.320 | 1.560 | HF |
| ic:component | component | 531 | False | resource_specific_tail | 3.206 | 10.780 | 3.040 | - |
| ic:source | source | 527 | False | resource_specific_tail | 4.450 | 9.210 | 2.960 | - |
| ic:taking | taking | 485 | False | plausible_missing_primitive | 5.380 |  | 2.790 | HF |
| ic:time_period | time_period | 474 | False | resource_specific_tail |  |  |  | - |
| ic:confidence | confidence | 473 | False | resource_specific_tail | 4.289 | 9.280 | 2.170 | - |
| ic:concern | concern | 468 | False | plausible_missing_primitive | 4.417 | 7.420 | 1.700 | - |
| ic:scientific | scientific | 452 | False | plausible_missing_primitive | 4.056 | 8.740 | 2.450 | - |
| ic:instance | instance | 446 | False | resource_specific_tail | 4.225 | 9.568 | 1.970 | - |
| ic:necessarily | necessarily | 444 | False | resource_specific_tail | 4.052 |  | 1.360 | - |
| ic:flow | flow | 436 | False | resource_specific_tail | 4.138 | 7.400 | 3.720 | - |
| ic:creative | creative | 416 | False | resource_specific_tail | 4.031 | 8.740 | 1.930 | - |
| ic:disposed | disposed | 411 | False | resource_specific_tail | 3.241 |  | 2.230 | - |
| ic:prominent | prominent | 359 | False | resource_specific_tail | 3.409 | 10.170 | 1.870 | - |
| ic:forceful | forceful | 346 | False | resource_specific_tail | 2.945 | 7.890 | 2.070 | - |
| ic:understood | understood | 342 | False | plausible_missing_primitive | 4.507 |  | 2.280 | - |
| ic:success | success | 337 | False | resource_specific_tail | 4.435 | 9.250 | 2.210 | - |
| ic:arouse | rouse | 330 | False | resource_specific_tail | 2.973 | 12.840 | 2.560 | - |
| ic:might | might | 330 | False | plausible_missing_primitive | 5.712 |  | 2.320 | HF |
| ic:happening | happening | 326 | False | resource_specific_tail | 4.956 |  | 2.100 | - |
| ic:cognitive | cognitive | 316 | False | plausible_missing_primitive | 2.836 | 13.630 | 1.630 | - |
| ic:attitude | attitude | 315 | False | plausible_missing_primitive | 4.416 | 6.780 | 1.970 | - |
| ic:pay | pay | 309 | False | resource_specific_tail | 5.405 | 5.500 | 3.540 | HF+EA |
| ic:acting | acting | 307 | False | resource_specific_tail | 4.719 |  | 2.540 | - |
| ic:surge | surge | 303 | False | resource_specific_tail | 3.270 | 9.820 | 2.780 | - |
| ic:affected | affected | 298 | False | resource_specific_tail | 3.831 |  | 1.930 | - |
| ic:objective | objective | 296 | False | resource_specific_tail | 3.848 | 12.720 | 2.000 | - |
| ic:expressed | expressed | 295 | False | resource_specific_tail | 3.515 |  | 2.030 | - |
| ic:potential | potential | 288 | False | resource_specific_tail | 4.275 | 9.610 | 1.910 | - |
| ic:verbal | verbal | 286 | False | resource_specific_tail | 3.468 | 8.420 | 2.500 | - |
| ic:courage | courage | 278 | False | plausible_missing_primitive | 4.374 | 8.420 | 1.520 | - |
| ic:much | much | 278 | False | plausible_missing_primitive | 5.988 | 4.581 | 1.690 | HF+EA |
| ic:naturally | naturally | 278 | False | resource_specific_tail | 4.389 | 8.556 | 1.480 | - |
| ic:reduced | reduced | 275 | False | resource_specific_tail | 3.688 |  | 2.210 | - |
| ic:unfavorable | unfavorable | 274 | False | resource_specific_tail | 2.468 |  | 1.920 | - |
| ic:walk | walk | 272 | False | plausible_missing_primitive | 5.334 | 3.450 | 4.070 | HF+EA+HC |
| ic:concept | concept | 270 | False | resource_specific_tail | 4.035 | 11.440 | 1.410 | - |
| ic:financial | financial | 269 | False | plausible_missing_primitive | 4.183 | 11.160 | 2.520 | - |
| ic:armed_forces | armed_forces | 267 | False | resource_specific_tail |  |  | 4.120 | HC |
| ic:industry | industry | 263 | False | plausible_missing_primitive | 4.068 | 10.440 | 3.290 | - |
| ic:holding | holding | 260 | False | resource_specific_tail | 4.840 |  | 3.720 | - |
| ic:struggle | struggle | 255 | False | plausible_missing_primitive | 4.126 | 9.800 | 2.790 | - |

