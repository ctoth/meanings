# Up-Goer Identity Cluster Notes

## Problem

The current Up-Goer export correctly computes a graph-theoretic seed over the
OEWN paper-wordnet graph, but the raw projection from graph nodes to human words
is not the thing we ultimately want. A WordNet lemma is not automatically an
English primitive.

Examples:

- `no::n` is Nobelium / chemical symbol `No`, not the ordinary English word
  `no`.
- `s::n` can be sulfur or a letter/symbol entry, not a human primitive `s`.
- `ax` and `axe` are form variants of the same ordinary word.
- `color` and `colour` are spelling variants, not different meanings.
- `wash` and `warsh` can share denotation while carrying different indexical
  information about speaker, region, register, or community.
- `bless her heart` is a phrase/construction with pragmatic and indexical force;
  it should not be flattened into the literal meanings of `bless`, `her`, and
  `heart`.
- Buffalo-style sentences and "time flies" examples show that a surface form
  only becomes semantically determinate after reading/role/parse assignment.

## Core Distinctions

Keep these surfaces separate in the data model:

- **Form:** an observed string or pronunciation, such as `color`, `colour`,
  `warsh`, `No`, `no`, `buffalo`.
- **Token occurrence:** a form in a particular context.
- **Reading:** the contextually resolved interpretation of a token occurrence.
- **Sense:** a dictionary/WordNet-like sense attached to a lexical item.
- **Identity cluster (IC):** the semantic object we are willing to treat as one
  referential unit for definitional closure.
- **Construction:** a multi-token form with meaning or force not recoverable
  from naive word-by-word composition.
- **Metadata:** dialect, register, domain, spelling system, pronunciation,
  geography, speaker signal, technical field, source provenance.
- **Admission policy:** the rule deciding whether a form, sense, or IC may enter
  the human Up-Goer vocabulary.

The important move is identity-cluster merge, not canonicalization. We do not
rewrite `colour` into `color` and pretend the form disappeared. We retain both
forms and merge their relevant senses into the same IC when the evidence says the
semantic identity is shared.

## Referential vs Indexical Meaning

Some differences change denotation. Others do not change denotation but still
carry information.

`wash` and `warsh` can denote the same action, while `warsh` can index region,
dialect, class, age, or community. This signal is real, but it belongs in
metadata or belief evidence, not in the base referential IC.

Likewise, `bless her heart` has literal, idiomatic, pragmatic, and indexical
readings. The correct representation is not one flat word list entry; it is a
construction with alternate readings and context-sensitive force.

## Why This Is Not Just An LLM

The project should not become a vector soup that infers meaning from correlations
alone. Correlation can propose merges, splits, or disambiguations, but the target
artifact is typed, inspectable, and falsifiable.

Required invariants:

- Form is not sense.
- Sense is not IC.
- Referential meaning is not indexical signal.
- Definition dependency is not usage correlation.
- Graph necessity is not human primitive admission.
- Embeddings or corpus statistics are evidence, not authority.

The graph seed is evidence about definitional circularity. It is not itself the
human vocabulary.

## Ingestion-Level Consequences

The current `lemma::pos` graph is useful but too coarse. It conflates form,
sense, and IC, and it uses first representative definitions. That amplifies
WordNet artifacts.

Target ingestion should:

- Preserve every candidate sense and definition instead of selecting the first
  representative synset per `lemma::pos`.
- Build sense-level nodes first, then project to ICs and human forms.
- Attach lexicality/type tags during ingestion: lexical word, symbol/code,
  abbreviation, proper name, taxon, chemical, technical term, phrase, idiom,
  uncertain.
- Add high-precision short-token filtering for 1-3 character forms. A tiny
  English short-word whitelist can identify valid forms, while gloss/type checks
  still reject wrong senses like `no::n` as Nobelium.
- Detect spelling and pronunciation variants as IC merge candidates, not as
  canonical rewrites.
- Keep dialect/register/domain as metadata.
- Avoid self-loop artifacts by resolving same-surface gloss references to the
  intended sense where possible.
- Maintain provenance for each merge, split, exclusion, and admission decision.

## Admission Policy For The Human Up-Goer List

The Up-Goer list should be derived from IC/form admission, not from raw graph
nodes.

A surface word can enter the human list only if:

- It maps to at least one admitted IC or admitted reading.
- Its admitted reading is lexical, not merely a symbol/code artifact.
- Its evidence is explicit: source senses, glosses, tags, frequency/AoA where
  available, and merge/exclusion rationale.
- Its admission does not depend on a sense mismatch, such as ordinary `no`
  inheriting evidence from `no::n` Nobelium.

The raw graph seed remains valuable as a strict feedback-vertex result. The
human list is a separate controlled-vocabulary projection with policy.

## Next Executable Workstream

1. Add an ingestion-time lexicality classifier for OEWN senses.
2. Add a short-token whitelist and tests for `no`, `No`, `s`, `e`, `g`, `ph`,
   `th`, `ax`, and `axe`.
3. Add IC merge records for high-confidence spelling variants such as
   `color/colour`, `center/centre`, `theater/theatre`, `ax/axe`.
4. Rebuild the paper-wordnet graph with node metadata preserved.
5. Export two surfaces:
   - strict graph seed over typed sense/IC nodes;
   - human Up-Goer vocabulary with admitted ICs, aliases, and exclusions.
6. Measure how many current seed artifacts are removed, quarantined, or merged
   without breaking acyclic definitional closure.

