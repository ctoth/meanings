# Sense Ingestion Design

This is the implementation contract for the sense-level Up-Goer ingestion
rebuild. The graph-theoretic seed, the identity-cluster surface, and the human
vocabulary export are separate artifacts.

## Typed Records

### Form

An observed spelling or pronunciation surface.

Fields:

- `form_id`: stable id, `form:<normalized_surface>`.
- `surface`: original observed string.
- `normalized`: normalized lookup key from `normalize_lemma`.
- `script`: script or orthography, default `Latin`.
- `language`: BCP-47 language tag, default `en`.
- `case_pattern`: `lower`, `title`, `upper`, `mixed`, or `uncased`.
- `token_length`: number of alphabetic characters after normalization.
- `metadata`: shared metadata record.

### TokenOccurrence

A form in a specific source context.

Fields:

- `occurrence_id`: stable source-local id.
- `form_id`: referenced Form.
- `source_id`: source document, gloss, corpus, or annotation source.
- `span`: byte or token offsets when available.
- `context`: short text window or structured gloss context.
- `metadata`: shared metadata record.

### Reading

The contextually resolved interpretation of one TokenOccurrence.

Fields:

- `reading_id`: stable id.
- `occurrence_id`: referenced TokenOccurrence.
- `sense_id`: referenced Sense when dictionary-backed.
- `construction_id`: referenced Construction when multi-token or idiomatic.
- `confidence`: `accepted`, `rejected`, or `uncertain`.
- `rationale`: short provenance text.
- `metadata`: shared metadata record.

### Sense

A dictionary or WordNet-like sense attached to a lexical item.

Fields:

- `sense_id`: OEWN sense id when available, otherwise `sense:<source>:<id>`.
- `synset_id`: source synset id.
- `form_id`: referenced Form for the sense lemma.
- `lemma`: normalized lemma.
- `pos`: source part of speech.
- `definition`: source gloss.
- `examples`: source examples.
- `lexicality`: LexicalityTag.
- `lexicality_reasons`: ordered rule ids that fired.
- `metadata`: shared metadata record.

### IdentityCluster

The referential unit used for definitional closure and admission.

Fields:

- `ic_id`: stable id, normally `ic:<primary_normalized_form>`.
- `sense_ids`: source senses merged into the IC.
- `form_ids`: all admitted forms and aliases for the IC.
- `lexicality`: aggregate LexicalityTag used for admission.
- `merge_rationales`: per-merge rationale records.
- `exclusions`: rejected sense ids or form ids with rule ids.
- `metadata`: shared metadata record.

### Construction

A multi-token form whose meaning, force, or role is not recoverable from naive
word-by-word composition.

Fields:

- `construction_id`: stable id, `construction:<normalized_surface>`.
- `forms`: ordered component Form ids.
- `surface_pattern`: observed phrase or parse pattern.
- `reading_ids`: context-sensitive readings.
- `force`: semantic, pragmatic, idiomatic, or indexical force when known.
- `metadata`: shared metadata record.

## LexicalityTag

Allowed values:

- `lexical-word`: ordinary lexical English word.
- `symbol-code`: letter, symbol, unit code, chemical symbol, or similar code.
- `abbreviation`: abbreviation or acronym.
- `proper-name`: named entity or proper-name sense.
- `taxon`: biological taxon or taxonomic proper name.
- `chemical`: chemical element, compound, radical, or formula sense.
- `technical-term`: domain-specific technical sense.
- `phrase`: compositional multi-word lexical item.
- `idiom`: non-compositional phrase or construction.
- `uncertain`: evidence is insufficient or conflicting.

## Metadata

Every typed record may carry:

- `source`: source name, version, and source-local id.
- `provenance`: rule id, script id, operator, timestamp when available.
- `dialect`: dialect or variety.
- `register`: formal, informal, slang, archaic, vulgar, poetic, or unknown.
- `domain`: source domain such as chemistry, taxonomy, law, computing, or music.
- `spelling_system`: US, UK, Canadian, historical, dialectal, or unknown.
- `pronunciation`: IPA or source pronunciation key.
- `geography`: geographic signal.
- `speaker_signal`: indexical signal such as region, class, age, or community.
- `confidence`: accepted, rejected, or uncertain.
- `notes`: human-readable rationale.

Metadata is not referential identity by itself. Dialect, register, domain, and
speaker signal can explain an alias or exclusion without creating a new IC.

## Admission Policy Rule Format

Admission is evaluated over typed records, not raw graph nodes. Each rule is a
structured record:

```json
{
  "rule_id": "lexicality.short_token.no",
  "scope": "sense",
  "priority": 100,
  "when": {
    "normalized": "no",
    "pos": "r",
    "lexicality": "lexical-word"
  },
  "then": {
    "decision": "admit",
    "target": "ic",
    "reason": "short-token whitelist admits ordinary adverbial no"
  },
  "unless": [
    {
      "lexicality": "chemical",
      "definition_contains": "nobelium"
    }
  ]
}
```

Required fields:

- `rule_id`: stable dotted id.
- `scope`: `form`, `sense`, `reading`, `ic`, or `construction`.
- `priority`: higher priority rules override lower priority rules.
- `when`: structured predicates over record fields.
- `then`: decision and rationale.

Optional fields:

- `unless`: structured blockers.
- `evidence`: source sense ids, gloss snippets, annotations, or merge ids.
- `outputs`: metadata fields or exclusion records to attach.

Allowed decisions:

- `admit`: include the IC or reading in the human vocabulary surface.
- `exclude`: reject the target from the human vocabulary surface.
- `quarantine`: keep the source node for graph analysis but exclude it from the
  human vocabulary surface pending review.
- `merge`: merge senses/forms into an IC while retaining all forms.
- `split`: prevent a surface or sense from inheriting another reading's evidence.

Default policy:

- A form may enter the human Up-Goer list only through at least one admitted IC
  or admitted reading.
- `lexical-word`, `phrase`, and `idiom` senses are admissible candidates.
- `symbol-code`, `abbreviation`, `proper-name`, `taxon`, `chemical`, and
  `technical-term` senses are excluded or quarantined unless a higher-priority
  rule explicitly admits the IC for the human vocabulary surface.
- `uncertain` never admits by default.
- Short forms of one to three characters require the short-token whitelist and
  must still pass sense-level lexicality checks.
- Variant spelling merges retain all forms and record the rationale; they do
  not canonicalize away aliases.
