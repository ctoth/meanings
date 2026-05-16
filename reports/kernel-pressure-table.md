# Kernel Pressure Table

This is an IC-level review table over structural, candidate, and obstruction evidence. It deliberately avoids a composite score.

## Summary

- Rows: `85137`
- Obstruction-core rows: `86`
- L0 rows: `317`
- Clean candidate rows: `1476`

## Pressure Bucket Counts

| pressure_bucket | count |
| --- | --- |
| candidate_background | 46155 |
| external_substrate | 35321 |
| resource_artifact | 3425 |
| common_vocabulary | 165 |
| circular_dependency | 53 |
| primitive_candidate | 11 |
| assembler_helper | 7 |

## Obstruction Core Counts

| pressure_bucket | count |
| --- | --- |
| circular_dependency | 53 |
| primitive_candidate | 11 |
| resource_artifact | 9 |
| assembler_helper | 7 |
| common_vocabulary | 6 |

## Obstruction Core Rows

| primary_alias | pressure_bucket | typed_bucket | l0_candidate | clean_candidate | p2_seed | kaikki_staged_seed | obstruction_coverage | review_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| act | common_vocabulary | abbreviation_or_code | False | False | True | True | False | artifact lexicality but high frequency |
| actions | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| animal | primitive_candidate |  | True | True | True | True | False | obstruction core plus L0/clean support |
| animals | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| answer | primitive_candidate |  | True | True | True | True | False | obstruction core plus L0/clean support |
| answered | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| ask | assembler_helper | resource_specific_tail | False | False | False | True | False | obstruction core plus high-frequency support |
| beneficial | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| bodily | circular_dependency | plausible_missing_primitive | False | False | False | True | True | obstruction core without clean primitive support |
| butterfly | circular_dependency | plausible_missing_primitive | False | False | False | True | False | obstruction core without clean primitive support |
| call | common_vocabulary | proper_name | False | False | False | True | False | artifact lexicality but high frequency |
| called | assembler_helper | resource_specific_tail | False | False | False | True | True | obstruction core plus high-frequency support |
| cardinal_number | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| certain | primitive_candidate | plausible_missing_primitive | False | True | True | True | True | obstruction core plus L0/clean support |
| complete | resource_artifact | technical_term | False | False | True | True | True | artifact bucket or candidate flag |
| constitute | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| constituted | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| containing | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| contents | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| countryside | resource_artifact | technical_term | False | False | True | True | False | artifact bucket or candidate flag |
| desire | primitive_candidate | plausible_missing_primitive | False | True | True | True | False | obstruction core plus L0/clean support |
| desired | circular_dependency |  | False | False | True | False | True | obstruction core without clean primitive support |
| divisions | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| do | assembler_helper | plausible_missing_primitive | False | False | True | True | False | obstruction core plus high-frequency support |
| earth | resource_artifact | proper_name | False | False | True | True | False | artifact bucket or candidate flag |
| earths | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| exercising | circular_dependency |  | False | False | True | False | True | obstruction core without clean primitive support |
| expectation | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| expectations | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| express | primitive_candidate | plausible_missing_primitive | False | True | False | True | False | obstruction core plus L0/clean support |
| expresses | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| genital | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| genital_organ | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| give_place | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| given_place | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| giving | assembler_helper | plausible_missing_primitive | False | False | True | True | False | obstruction core plus high-frequency support |
| goal | circular_dependency | plausible_missing_primitive | False | False | True | True | True | obstruction core without clean primitive support |
| good | common_vocabulary | technical_term | False | False | True | True | False | artifact lexicality but high frequency |
| ha | common_vocabulary | abbreviation_or_code | False | False | False | True | False | artifact lexicality but high frequency |
| has | assembler_helper | resource_specific_tail | False | False | False | True | True | obstruction core plus high-frequency support |
| helpful | primitive_candidate |  | False | True | False | False | True | obstruction core plus L0/clean support |
| hundred_thousand | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| liberal_conservative | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| light_fixture | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| light_fixtures | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| locate | resource_artifact | technical_term | False | False | False | True | False | artifact bucket or candidate flag |
| located | circular_dependency | plausible_missing_primitive | False | False | True | True | True | obstruction core without clean primitive support |
| name | primitive_candidate |  | True | True | True | True | False | obstruction core plus L0/clean support |
| names | circular_dependency |  | False | False | True | False | True | obstruction core without clean primitive support |
| nymphalid | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| office | assembler_helper | plausible_missing_primitive | False | False | True | True | True | obstruction core plus high-frequency support |
| organisms | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| past_participle | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| place | primitive_candidate |  | True | True | True | True | False | obstruction core plus L0/clean support |
| placed | circular_dependency | plausible_missing_primitive | False | False | True | True | True | obstruction core without clean primitive support |
| plural | primitive_candidate | plausible_missing_primitive | False | True | True | True | False | obstruction core plus L0/clean support |
| position | circular_dependency | plausible_missing_primitive | False | False | True | True | True | obstruction core without clean primitive support |
| practical | resource_artifact | technical_term | False | True | True | True | False | artifact bucket or candidate flag |
| provide | resource_artifact | technical_term | False | True | True | True | False | artifact bucket or candidate flag |
| put | common_vocabulary | abbreviation_or_code | False | False | True | True | False | artifact lexicality but high frequency |
| reference | resource_artifact | technical_term | False | False | False | True | False | artifact bucket or candidate flag |
| referred | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| referring | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| replace | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| replaced | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| request | primitive_candidate | plausible_missing_primitive | False | True | False | True | True | obstruction core plus L0/clean support |
| requirements | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| rural | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| rustic | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| satisfactorily | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| score | resource_artifact | technical_term | False | False | True | True | False | artifact bucket or candidate flag |
| see_also | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| sexual_intercourse | circular_dependency | plausible_missing_primitive | False | False | True | True | False | obstruction core without clean primitive support |
| sexually | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| simple_past | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| someones | circular_dependency |  | False | False | False | False | True | obstruction core without clean primitive support |
| suggestion | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| surname | circular_dependency | resource_specific_tail | False | False | False | True | False | obstruction core without clean primitive support |
| survey | circular_dependency | plausible_missing_primitive | False | False | False | True | False | obstruction core without clean primitive support |
| than | assembler_helper | resource_specific_tail | False | False | False | True | True | obstruction core plus high-frequency support |
| topics | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| town | common_vocabulary | proper_name | False | False | True | True | False | artifact lexicality but high frequency |
| types | circular_dependency | resource_specific_tail | False | False | False | True | True | obstruction core without clean primitive support |
| useful | primitive_candidate | plausible_missing_primitive | False | True | False | True | True | obstruction core plus L0/clean support |
| views | circular_dependency |  | False | False | False | False | False | obstruction core without clean primitive support |
| village | resource_artifact | proper_name | False | False | False | True | False | artifact bucket or candidate flag |
