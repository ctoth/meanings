# L0 Grounded-Primitives Derivation

This is a candidate set, not a final semantic primitive inventory. It uses channel gates over the P2-backed Base English workbench and records unavailable channels explicitly.

## Summary

- Source: `data\base_english_candidates.csv`
- Input rows: `58099`
- L0 candidate rows: `317`
- Near misses (3 of 4 channels): `1155`
- GCIDE channel available: `False`
- Sensorimotor channel available: `False`

## Channel Counts

| channel | count |
| --- | --- |
| strict_admission | 55344 |
| structural | 3539 |
| cross_list | 1020 |
| grounding_proxy | 6973 |

## L0 Candidates

| primary_alias | strict_admission | structural | cross_list | grounding_proxy | strict_lemma_seed | typed_sense_seed | longman | ogden | early_aoa | high_concreteness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| after | True | True | True | True | True | True | True | True | True | False |
| again | True | True | True | True | True | True | True | True | True | False |
| animal | True | True | True | True | True | True | True | True | True | True |
| apple | True | True | True | True | True | True | True | True | True | True |
| back | True | True | True | True | True | True | True | True | True | True |
| before | True | True | True | True | True | True | True | True | True | False |
| blade | True | True | True | True | True | True | True | True | False | True |
| board | True | True | True | True | True | True | True | True | False | True |
| body | True | True | True | True | True | True | True | True | True | True |
| bone | True | True | True | True | True | True | True | True | True | True |
| brain | True | True | True | True | True | True | True | True | True | True |
| branch | True | True | True | True | True | True | True | True | True | True |
| brush | True | True | True | True | True | True | True | True | True | True |
| bucket | True | True | True | True | True | True | True | True | True | True |
| building | True | True | True | True | True | True | True | True | False | True |
| butter | True | True | True | True | True | True | True | True | True | True |
| clean | True | True | True | True | True | True | True | True | True | False |
| coat | True | True | True | True | True | True | True | True | True | True |
| cotton | True | True | True | True | True | True | True | True | True | True |
| danger | True | True | True | True | True | True | True | True | True | False |
| different | True | True | True | True | True | True | True | True | True | False |
| dust | True | True | True | True | True | True | True | True | True | True |
| early | True | True | True | True | True | True | True | True | True | False |
| face | True | True | True | True | True | True | True | True | True | True |
| farm | True | True | True | True | True | True | True | True | True | True |
| feeling | True | True | True | True | True | True | True | True | True | False |
| field | True | True | True | True | True | True | True | True | False | True |
| first | True | True | True | True | True | True | True | True | True | False |
| flat | True | True | True | True | True | True | True | True | True | True |
| foot | True | True | True | True | True | True | True | True | True | True |
| forrad | True | True | True | True | True | True | True | True | True | False |
| frame | True | True | True | True | True | True | True | True | False | True |
| free | True | True | True | True | True | True | True | True | True | False |
| front | True | True | True | True | True | True | True | True | True | False |
| fruit | True | True | True | True | True | True | True | True | True | True |
| full | True | True | True | True | True | True | True | True | True | False |
| give | True | True | True | True | True | True | True | True | True | False |
| glass | True | True | True | True | True | True | True | True | True | True |
| great | True | True | True | True | True | True | True | True | True | False |
| group | True | True | True | True | True | True | True | True | True | True |
| hand | True | True | True | True | True | True | True | True | True | True |
| hard | True | True | True | True | True | True | True | True | True | False |
| head | True | True | True | True | True | True | True | True | True | True |
| high | True | True | True | True | True | True | True | True | True | False |
| hole | True | True | True | True | True | True | True | True | True | True |
| horn | True | True | True | True | True | True | True | True | True | True |
| horse | True | True | True | True | True | True | True | True | True | True |
| idea | True | True | True | True | True | True | True | True | True | False |
| important | True | True | True | True | True | True | True | True | True | False |
| knee | True | True | True | True | True | True | True | True | True | True |
| knife | True | True | True | True | True | True | True | True | True | True |
| left | True | True | True | True | True | True | True | True | True | False |
| liquid | True | True | True | True | True | True | True | True | True | True |
| long | True | True | True | True | True | True | True | True | True | False |
| loss | True | True | True | True | True | True | True | True | True | False |
| machine | True | True | True | True | True | True | True | True | False | True |
| make | True | True | True | True | True | True | True | True | True | False |
| married | True | True | True | True | True | True | True | True | True | False |
| material | True | True | True | True | True | True | True | True | False | True |
| meeting | True | True | True | True | True | True | True | True | True | False |
| middle | True | True | True | True | True | True | True | True | True | False |
| mind | True | True | True | True | True | True | True | True | True | False |
| money | True | True | True | True | True | True | True | True | True | True |
| month | True | True | True | True | True | True | True | True | True | True |
| mother | True | True | True | True | True | True | True | True | True | True |
| mouth | True | True | True | True | True | True | True | True | True | True |
| music | True | True | True | True | True | True | True | True | True | True |
| name | True | True | True | True | True | True | True | True | True | False |
| normal | True | True | True | True | True | True | True | True | True | False |
| nose | True | True | True | True | True | True | True | True | True | True |
| open | True | True | True | True | True | True | True | True | True | False |
| over | True | True | True | True | True | True | True | True | True | False |
| pain | True | True | True | True | True | True | True | True | True | False |
| paper | True | True | True | True | True | True | True | True | True | True |
| place | True | True | True | True | True | True | True | True | True | False |

## Near-Miss Missing Channel Counts

| missing_channel | count |
| --- | --- |
| cross_list | 641 |
| grounding_proxy | 240 |
| strict_admission | 156 |
| structural | 118 |

## Near Misses

| primary_alias | strict_admission | structural | cross_list | grounding_proxy | strict_lemma_seed | typed_sense_seed | longman | ogden | early_aoa | high_concreteness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| able | True | True | True | False | True | True | True | True | False | False |
| acid | False | True | True | True | True | True | True | True | False | True |
| across | True | True | True | False | True | True | True | True | False | False |
| agreement | True | True | True | False | True | True | True | True | False | False |
| attempt | True | True | True | False | True | True | True | True | False | False |
| attention | True | True | True | False | True | True | True | True | False | False |
| ball | False | True | True | True | True | True | True | True | True | True |
| behavior | True | True | True | False | True | True | True | True | False | False |
| bitter | True | True | True | False | True | True | True | True | False | False |
| black | False | True | True | True | True | True | True | True | True | False |
| blood | False | True | True | True | True | True | True | True | True | True |
| blue | False | True | True | True | True | True | True | True | True | False |
| book | False | True | True | True | True | True | True | True | True | True |
| business | True | True | True | False | True | True | True | True | False | False |
| cause | False | True | True | True | True | True | True | True | True | False |
| certain | True | True | True | False | True | True | True | True | False | False |
| change | False | True | True | True | True | True | True | True | True | False |
| color | False | True | True | True | True | True | True | True | True | True |
| come | False | True | True | True | True | True | True | True | True | False |
| conscious | True | True | True | False | True | True | True | True | False | False |
| control | True | True | True | False | True | True | True | True | False | False |
| copy | True | True | True | False | True | True | True | True | False | False |
| damage | True | True | True | False | True | True | True | True | False | False |
| death | False | True | True | True | True | True | True | True | True | False |
| deep | False | True | True | True | True | True | True | True | True | False |
| degree | True | True | True | False | True | True | True | True | False | False |
| delicate | True | True | True | False | True | True | True | True | False | False |
| desire | True | True | True | False | True | True | True | True | False | False |
| discussion | True | True | True | False | True | True | True | True | False | False |
| disease | True | True | True | False | True | True | True | True | False | False |
| do | False | True | True | True | True | True | True | True | True | False |
| doubt | True | True | True | False | True | True | True | True | False | False |
| earth | False | True | True | True | True | True | True | True | True | True |
| effect | True | True | True | False | True | True | True | True | False | False |
| equal | True | True | True | False | True | True | True | True | False | False |
| event | True | True | True | False | True | True | True | True | False | False |
| fact | True | True | True | False | True | True | True | True | False | False |
| father | False | True | True | True | True | True | True | True | True | True |
| fight | False | True | True | True | True | True | True | True | True | True |
| flight | True | True | True | False | True | True | True | True | False | False |
| food | False | True | True | True | True | True | True | True | True | True |
| force | False | True | True | True | True | True | True | True | True | False |
| future | True | True | True | False | True | True | True | True | False | False |
| general | True | True | True | False | True | True | True | True | False | False |
| gold | False | True | True | True | True | True | True | True | False | True |
| government | True | True | True | False | True | True | True | True | False | False |
| gray | False | True | True | True | True | True | True | True | True | True |
| green | False | True | True | True | True | True | True | True | True | True |
| growth | True | True | True | False | True | True | True | True | False | False |
| hair | False | True | True | True | True | True | True | True | True | True |
| help | False | True | True | True | True | True | True | True | True | False |
| hope | False | True | True | True | True | True | True | True | True | False |
| insurance | True | True | True | False | True | True | True | True | False | False |
| interest | True | True | True | False | True | True | True | True | False | False |
| iron | False | True | True | True | True | True | True | True | False | True |
| keep | False | True | True | True | True | True | True | True | True | False |
| land | False | True | True | True | True | True | True | True | True | True |
| less | True | True | True | False | True | True | True | True | False | False |
| light | False | True | True | True | True | True | True | True | True | True |
| like | False | True | True | True | True | True | True | True | True | False |
| line | False | True | True | True | True | True | True | True | True | True |
| list | False | True | True | True | True | True | True | True | True | True |
| male | False | True | True | True | True | True | True | True | True | True |
| metal | False | True | True | True | True | True | True | True | True | True |
| military | False | True | True | True | True | True | True | True | False | True |
| milk | False | True | True | True | True | True | True | True | True | True |
| moon | False | True | True | True | True | True | True | True | True | True |
| more | False | True | True | True | True | True | True | True | True | False |
| move | False | True | True | True | True | True | True | True | True | False |
| narrow | True | True | True | False | True | True | True | True | False | False |
| natural | True | True | True | False | True | True | True | True | False | False |
| near | False | True | True | True | True | True | True | True | True | False |
| need | False | True | True | True | True | True | True | True | True | False |
| nerve | True | True | True | False | True | True | True | True | False | False |
| no | False | True | True | True | True | True | True | True | True | False |
