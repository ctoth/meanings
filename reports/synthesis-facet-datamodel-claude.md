# Synthesis facet: the data model the project needs and currently lacks

**Date:** 2026-05-12 · **Author:** Claude subagent · **Scope:** the typed object model — schema, layer records, inter-layer relations, the argumentation-tool mapping, the two deliverable surfaces, the falsifiable prediction, the "not just an LLM" invariants. A parallel Gemini draft of this same facet lives at `reports/synthesis-facet-datamodel-gemini.md`.

**Primary source:** `notes/upgoer-identity-clusters.md`. Supporting: `reports/sibling-tools-connection.md` §7, the three sibling-tool inventories, `reports/argumentation-bridge-oewn.md`, and the current pipeline source (`src/meanings/{wordnet_pipeline,normalize,annotations,graph_analysis}.py`).

---

## 1. What the current model is, and why it is wrong

### 1.1 Verified facts about the current pipeline

The three graph builders in `wordnet_pipeline.py`:

- **`lemma`** (`build_lemma_graph`) — one node per `normalize_lemma(word.lemma())`; all senses and all parts of speech collapsed; edge `defining_lemma -> defined_lemma` whenever a *de-duplicated set of definitions* across all of a lemma's synsets contains a matched lexicon lemma. No POS, no sense identity at all.
- **`paper-wordnet`** (`build_paper_wordnet_graph`) — the "measuring stick" against Vincent-Lamarre. One node per `lemma::pos`. Crucially: `synset = next((candidate for candidate in word.synsets() if candidate.definition()), None)` — **the *first* synset with a non-empty gloss is the representative**, and only that gloss feeds the graph. Edge resolution: try `defining_lemma::same_pos`, else the unique `lemma::pos` for that lemma, else skip (`ambiguous_skipped` / `missing_skipped`). `metadata["construction"] == "lemma_pos_first_representative_synset_content_words"`.
- **`sense`** (`build_synset_graph`) — experimental; one node per *defined synset*; edges resolved by same-POS preference plus a strict overlap tie-break (`choose_best_candidate`). This is the closest existing thing to a sense graph, but it is still keyed by `synset.id` (a WordNet artifact), carries no lexicality typing, has no IC layer, no provenance, and no admission policy. Its resolution silently drops everything ambiguous.

`normalize.py` is a *token-level* gloss parser: longest-match n-gram scan up to width 3 against the lemma set, with three hand-curated stoplists (`FUNCTION_WORDS`, `GLOSS_GLUE`, `TAXONOMIC_GLUE`, `NUMBER_WORDS`) and a titlecase-span skip (a crude proper-name filter). There is no per-sense type tag anywhere; lexicality is approximated only by these blocklists and the titlecase heuristic.

`annotations.py` overlays psycholinguistic CSVs (`frequency`, `concreteness`, `age_of_acquisition`, `imageability`) keyed on `node.split("::", 1)[0]` — i.e. on the *lemma*, not the sense. So even the metadata that exists is attached at the wrong granularity.

`graph_analysis.py` is pure graph theory: `compute_kernel` (leaf-strip; self-loop counts as a cycle so a word in its own gloss is never stripped — commit `7d12e64`/`7d12e64`-era fix), SCC, `source_sccs`, `analyze_kernel` → `KernelAnalysis`. None of it knows what a node *is*.

### 1.2 The three conflations

The current `lemma::pos` (and `lemma`) graph collapses three distinct things into one node identity:

1. **Form** — the observed string. `color` and `colour` are two forms; `ax` and `axe` are two forms; `No` and `no` are two forms (only one survives `normalize_lemma`, which lowercases — so `No`/`no` are *already silently merged* in a way that is wrong: `No` the chemical symbol and `no` the negation are not the same thing, and lowercasing erases the distinction the model needs to keep).
2. **Sense** — a dictionary reading attached to a lexical item. `no::n` in OEWN includes the synset for *nobelium / chemical symbol No*; `s::n` includes *sulfur*. Collapsing senses into `lemma::pos` and then taking the *first representative gloss* means a single arbitrary WordNet ordering decision determines whether `no::n` enters the graph as "the negative particle" or "the element."
3. **Identity cluster (IC)** — the referential unit you are willing to treat as one thing for definitional closure. `wash` and `warsh` denote the same act and should share an IC; `color` and `colour` share an IC; but they are different forms and different senses.

The damage is concrete and measurable:

- **`no::n` = Nobelium.** A bare WordNet entry, never an English primitive, pulled into the graph because `lemma::pos` has no lexicality type and the first-representative-gloss heuristic doesn't care.
- **Gloss self-loops.** The `compute_kernel` self-loop fix (a *correct* fix for the lemma-level graph: a word literally in its own gloss is a 1-node FVS member) grew the lemma-level Kernel from **12,853 → 18,151**, pulling in **3,413 gloss self-loops**. Many of those are artifacts: a gloss for `violin::n` that mentions "violin" is referring to the *intended sense* (or to the IC "violin"), not re-defining `violin` in terms of itself. On a sense-level graph that occurrence resolves to a *different* node and the self-loop dissolves. (See §6.)
- **Spelling/pronunciation variants amplified.** `color`/`colour`, `center`/`centre`, `theater`/`theatre` are counted as separate nodes with separate (often near-identical) glosses, inflating cycle structure and the Kernel with what is one meaning wearing two coats.
- **Constructions flattened.** `bless her heart` — a phrase with literal, idiomatic, pragmatic, and indexical readings — has no representation as a *construction*; it is either dropped or its meaning is (falsely) imputed to be a composition of `bless` + `her` + `heart`.
- **Indexical signal lost or mis-located.** `warsh` indexes region/class/age of the speaker. The current model has nowhere to put that, so it either drops `warsh` or treats it as a distinct denotation — both wrong.

### 1.3 The target stack

From the upgoer note, the layers that must be *distinct typed records*:

```
form  →  token occurrence  →  reading  →  sense  →  IC
                                                     ↑
                                            (+ construction, metadata, admission policy)
```

Each arrow is a *defeasible inference carrying provenance*, not a rewrite. The base referential graph — the thing whose Kernel/MinSet we compute — lives at the **sense** and **IC** layers, not the `lemma::pos` layer.

---

## 2. The schema, concretely

All records below are intended to be implementable directly (frozen dataclasses, or rows in a small typed store). Field names are suggestions; what matters is the typing discipline. IDs are stable surrogate keys *minted by us*, never reused from WordNet (a WordNet `synset.id` is *evidence about* a sense, recorded in provenance, not the sense's identity).

### 2.0 The shared lexicality-tag enum

Used on `Sense`, on `Reading`, and (as a derived/aggregated tag) on `IC`:

```python
class Lexicality(StrEnum):
    LEXICAL_WORD = "lexical_word"        # ordinary English word: "dog", "run", "blue"
    SYMBOL_CODE  = "symbol_code"          # "No" (Nobelium), "s" (sulfur), unit symbols, ISO codes
    ABBREVIATION = "abbreviation"         # "etc.", "Dr.", "USA" as an abbreviation reading
    PROPER_NAME  = "proper_name"          # "Paris", "Shakespeare"
    TAXON        = "taxon"                # "Felis catus", "Rosaceae"
    CHEMICAL     = "chemical"             # "sodium chloride", "H2O" as a chemical-name reading
    TECHNICAL    = "technical"            # domain term that is real language but not a "plain" word
    PHRASE       = "phrase"               # multi-token, compositional-ish but lexically stored
    IDIOM        = "idiom"                # multi-token, non-compositional ("kick the bucket")
    UNCERTAIN    = "uncertain"            # classifier could not decide — first-class, NOT a default
```

`UNCERTAIN` is the typed analogue of `gunray`'s `UNDECIDED`: a real outcome, propagated, never silently coerced to `LEXICAL_WORD`. Admission (§5) keys off lexicality: only `LEXICAL_WORD` (and arguably `PHRASE`/`IDIOM` for an "expanded" list) is admissible to the human Up-Goer vocabulary; `SYMBOL_CODE`, `PROPER_NAME`, `TAXON`, `CHEMICAL`, and `UNCERTAIN` are not — that is the rule that keeps `no` from inheriting evidence from `no::n` = Nobelium.

### 2.1 `Form`

An observed orthographic (or phonological) string. **No meaning attached.**

```python
@dataclass(frozen=True)
class Form:
    form_id: str                 # surrogate key, e.g. "form:colour"
    surface: str                 # "colour", "warsh", "No", "no", "bless her heart"
    surface_kind: SurfaceKind    # ORTHOGRAPHIC | PHONETIC | PHONEMIC
    n_tokens: int                # 1 for "colour", 3 for "bless her heart"
    spelling_system: str | None  # "en-GB-1996", "en-US", "Webster", None if unknown
    case_pattern: str            # "lower" | "title" | "upper" | "mixed" — preserved, never normalized away
    provenance: Provenance       # which lexicon/list/corpus this form was observed in
```

Key discipline point: `normalize_lemma` currently lowercases and strips. That is fine as a *join key for evidence gathering*, but it must not be the identity of the form. `No` and `no` are two `Form`s with `case_pattern` `"title"` and `"lower"` respectively; the model decides *later* (via sense resolution) which senses each form can carry. Spelling variants stay as separate `Form`s forever — "we do not rewrite `colour` into `color` and pretend the form disappeared."

### 2.2 `TokenOccurrence`

A `Form` appearing in a particular context. The atom the pipeline actually ingests when it scans a gloss.

```python
@dataclass(frozen=True)
class TokenOccurrence:
    occurrence_id: str
    form_id: str
    context_id: str              # which gloss / sentence / corpus span this occurrence is in
    span: tuple[int, int]        # char or token offsets within the context
    context_kind: ContextKind    # GLOSS_OF(sense_id) | EXAMPLE_OF(sense_id) | CORPUS | USER_LIST
    provenance: Provenance
```

A `TokenOccurrence` is **semantically indeterminate by itself** — "time flies", "Buffalo buffalo buffalo", "bless her heart". It does not yet have a meaning; it has a context. This is the layer the current pipeline implicitly works at when `extract_lemma_candidates` finds `"violin"` inside the gloss of `violin::n` — except the current pipeline immediately jumps to `lemma`, skipping `reading` and `sense`, and so cannot tell "this occurrence of `violin` means the IC violin" from "this occurrence re-defines violin in terms of itself."

### 2.3 `Reading`

The contextually resolved interpretation of a `TokenOccurrence`. A `Reading` is the *output of disambiguation*; it points at a `Sense` (or, when only the referential identity is recoverable, directly at an `IC`).

```python
@dataclass(frozen=True)
class Reading:
    reading_id: str
    occurrence_id: str
    resolved_to: SenseRef | ICRef        # tagged union: SENSE(sense_id) | IC(ic_id)
    lexicality: Lexicality               # the lexicality of *this reading in this context*
    construction_id: str | None          # set iff this occurrence is part of a Construction span
    confidence: float                    # [0,1]; UNCERTAIN reading => low confidence + lexicality=UNCERTAIN
    evidence: list[ArgumentRef]           # the arguments that selected this reading (see §4)
    defeated_alternatives: list[SenseRef] # the readings this one beat, with the defeating argument id
    provenance: Provenance
```

A self-loop in a gloss graph is *honest* only when a `Reading` of a token in the gloss of sense `S` resolves to `S` itself. If it resolves to a *different* sense of the same form, or to the IC, there is no self-loop — there is an ordinary edge to that other node, or no edge at all (if it resolves to the IC and the IC is the head's own IC, that is a self-loop *at the IC layer* and is a real claim, but a different one than "this sense is defined in terms of itself").

### 2.4 `Sense`

A dictionary/WordNet-like sense attached to a lexical item. **This is the node type the base definition graph runs on.**

```python
@dataclass(frozen=True)
class Sense:
    sense_id: str                        # surrogate, e.g. "sense:dog#1" — NOT a WordNet synset id
    form_ids: frozenset[str]             # the forms that can express this sense (≥1)
    pos: str
    gloss: str                           # the definition text
    lexicality: Lexicality               # lexical_word | symbol_code | ... | uncertain
    metadata: SenseMetadata              # dialect/register/domain/spelling-system/etc. (see §2.7)
    definiens_edges: list[DefinitionEdge]   # outgoing: senses this sense's gloss depends on (see §3.1)
    ic_id: str | None                    # which IC this sense belongs to (set by an IC merge, see §3.3)
    source_synsets: list[SynsetRef]      # WordNet synsets that contributed — evidence, in provenance
    annotations: dict[str, float]        # frequency/AoA/concreteness/imageability AT THE SENSE LEVEL
    provenance: Provenance
```

Critical change from the current `paper-wordnet` build: **keep every candidate sense and every gloss**, do not pick a "first representative." The current code's `representative_definition[key] = synset.definition()` for the first synset is the single biggest artifact generator after the lemma collapse — it makes the graph depend on WordNet's internal synset ordering. The sense-level model has one `Sense` per (resolved) WordNet sense, all of them, each carrying its own gloss and its own `definiens_edges`.

### 2.5 `IC` (identity cluster)

The semantic object treated as one referential unit for definitional closure. An IC is *built by merges over senses*; it is not a canonical form.

```python
@dataclass(frozen=True)
class IC:
    ic_id: str                           # surrogate
    member_sense_ids: frozenset[str]     # the senses merged into this cluster (≥1)
    aliases: frozenset[str]              # all forms that express any member sense — color, colour, ...
    representative_label: str            # a human-readable handle; NOT load-bearing, NOT canonical
    lexicality: Lexicality               # aggregate; UNCERTAIN if members disagree and no rule resolves
    metadata_union: ICMetadata           # union of member metadata, with per-member attribution
    merge_provenance: list[MergeRecord]  # one record PER MERGE that built this cluster (see §3.3)
    exclusions: list[ExclusionRecord]    # senses considered for membership and rejected, with reason
    admitted: bool                       # output of the admission theory (§5) — NOT decided here
    provenance: Provenance
```

`color` and `colour` map to the *same* `IC` whose `aliases = {"color", "colour", ...}` and whose `member_sense_ids` are the colour-senses of both forms; both `Form`s and both `Sense`s still exist. `wash` and `warsh` map to the same referential `IC` (they denote the same act); the `warsh`-only indexical signal is **not** in the IC — it is metadata on the `warsh` `Form` / the `warsh`-flavoured `Sense` (§2.7, §3.4).

### 2.6 `Construction`

A multi-token form whose meaning or force is not recoverable from word-by-word composition.

```python
@dataclass(frozen=True)
class Construction:
    construction_id: str
    form_id: str                         # the multi-token form, e.g. "bless her heart"
    slots: list[SlotSpec]                # fixed vs open positions; "bless [POSS] heart"
    readings: list[ConstructionReading]  # literal | idiomatic | pragmatic | indexical — each with force
    selecting_context_features: list[str]  # what context features pick which reading
    lexicality: Lexicality               # typically PHRASE or IDIOM
    metadata: ConstructionMetadata
    provenance: Provenance

@dataclass(frozen=True)
class ConstructionReading:
    label: str                           # "literal" | "blessing-idiom" | "condescension-marker" | ...
    resolved_to: SenseRef | ICRef | None # the literal reading points at the compositional meaning;
                                          # the idiomatic/pragmatic ones may point at their own Sense/IC
    force: PragmaticForce                 # ASSERTION | EVALUATIVE | MITIGATOR | DEROGATION | ...
    is_compositional: bool
```

In ADF terms (§4) a `Construction` is a node whose acceptance condition is *parametrized by context*, not a flat word-list entry — exactly the upgoer note's point. `bless her heart` does not get decomposed into the literal senses of `bless`/`her`/`heart` for the base referential graph; it is one node with alternate readings.

### 2.7 `Metadata` (dialect / register / domain / spelling-system / …)

A single typed bag, attached at whatever layer it pertains to (`Form` for spelling-system; `Sense` for register/domain; `IC` as an attributed union; `Construction` for pragmatic force).

```python
@dataclass(frozen=True)
class Metadata:
    dialect: frozenset[str] = frozenset()       # "en-GB", "AAVE", "Appalachian", ...
    register: frozenset[str] = frozenset()      # "formal", "slang", "child-directed", ...
    domain: frozenset[str] = frozenset()        # "chemistry", "law", "music", ...
    spelling_system: frozenset[str] = frozenset()
    geography: frozenset[str] = frozenset()
    period: frozenset[str] = frozenset()        # "archaic", "obsolete", "contemporary"
    speaker_signal: frozenset[str] = frozenset()  # indexical info ABOUT THE SPEAKER (see §3.4)
    technical_field: frozenset[str] = frozenset()
    source_provenance: list[Provenance] = field(default_factory=list)
```

`speaker_signal` is where `warsh`'s "indexes region/class/age" lives. It is *metadata about the speaker*, not part of the IC's denotation — this is the referential/indexical split made structural (§3.4).

### 2.8 `Provenance` and `AdmissionPolicy`

```python
@dataclass(frozen=True)
class Provenance:
    source: str                          # "oewn:2024" | "BNC-freq" | "Kuperman-AoA" | "LLM:gpt-X" | "manual"
    extracted_at: str
    extractor: str
    evidence_kind: EvidenceKind          # LEXICON_ENTRY | CORPUS_STAT | EMBEDDING | LLM_PROPOSAL | HEURISTIC | MANUAL
    raw_payload_ref: str | None          # pointer to the unmodified source datum

@dataclass(frozen=True)
class AdmissionPolicy:
    policy_id: str
    strict_rules: tuple[Rule, ...]       # gunray-shaped — see §4 / §5
    defeasible_rules: tuple[Rule, ...]
    defeaters: tuple[Rule, ...]
    superiority: tuple[tuple[str, str], ...]
    surface: AdmissionSurface            # STRICT_SEED | HUMAN_UPGOER  (the two outputs, §5)
```

`evidence_kind` is the type-level enforcement of "embeddings or corpus statistics are evidence, not authority": an `LLM_PROPOSAL` or an `EMBEDDING` provenance can attach to an `ArgumentRef`, never directly to a `Sense.lexicality` or an `IC.member_sense_ids` decision — those are only ever set by a rule that *adjudicated* such arguments.

---

## 3. Relations between layers

### 3.1 Definition edges = `supports` between resolved senses

A gloss occurrence, once it has a `Reading`, contributes a directed edge in the base definition graph **from the resolved sense to the head sense**:

```python
@dataclass(frozen=True)
class DefinitionEdge:
    head_sense_id: str                   # the sense being defined
    definiens_sense_id: str              # a sense appearing in head's gloss (via a Reading)
    via_reading_id: str                  # the Reading that produced this edge — full provenance
    relation: Literal["supports"]        # ALWAYS supports — "you can't know head until you know definiens"
```

So the sense-level definition graph is a **bipolar AF whose `supports` relation is exactly this edge set, and whose `defeats` relation is §3.2** (currently empty in `argumentation_bridge.bipolar_support_framework` *only because the `paper-wordnet` build threw the attacks away by collapsing senses* — the sense model puts them back). It is also an **ADF**: each `Sense` carries an acceptance condition "you know me iff you know [a Boolean combination over] my definiens senses." The repo's `compute_kernel` (leaf-strip) is the closest existing operator to the honest support-closure here; the formal-argumentation library's plain bipolar grounded semantics is *not* that operator (it's "defended against set-defeat," which is vacuous with empty defeats — see `argumentation-bridge-oewn.md`).

If a `Reading` resolves to an `IC` rather than a `Sense` (the disambiguator could fix the referent but not the exact sense), the edge is `definiens_ic_id -> head_sense_id` and the graph is heterogeneous (sense and IC nodes); for Kernel computation that is fine — collapse IC nodes' incident edges onto their member senses, or run the analysis at the IC layer directly (see §5).

### 3.2 Attack edges between competing senses of a form

Two senses of the *same form* that cannot both be the reading of a given occurrence attack each other:

```python
@dataclass(frozen=True)
class SenseRivalryEdge:
    form_id: str
    sense_a_id: str
    sense_b_id: str
    relation: Literal["attacks"]         # symmetric: a↔b — they are rival readings of `form_id`
    arbitrating_arguments: list[ArgumentRef]  # context features / gloss-type checks that pick one
```

`no::n`-Nobelium vs `no`-the-negation are rival readings of the form `no`; `s`-sulfur vs `s`-the-letter are rivals of the form `s`. The gloss-type check ("does this sense's gloss look like a chemistry definition?") and the 1–3-char whitelist are *arguments* on these edges (§4): they defeat `no::n`-Nobelium as the reading of an ordinary occurrence of `no`. The accepted reading per occurrence is the surviving extension of this local attack structure plus the contextual arguments. This is `gunray`-shaped defeasible WSD; the `defeated_alternatives` field on `Reading` records the outcome with the defeating argument id — the **dialectical tree is the merge/exclusion rationale the admission policy demands**.

### 3.3 IC merge = belief merge over sense clusters, with per-merge provenance

An `IC` is built by a sequence of `MergeRecord`s, each one a `belief-set`-style IC merge (Konieczny–Pino Pérez profile merge) over the *sense sets* of the forms being unified:

```python
@dataclass(frozen=True)
class MergeRecord:
    merge_id: str
    merged_sense_ids: frozenset[str]     # the senses brought into the cluster by THIS merge
    contributing_forms: frozenset[str]   # the forms whose senses these are
    rationale: MergeRationale            # SPELLING_VARIANT | PRONUNCIATION_VARIANT | SYNONYMY | ...
    evidence: list[ArgumentRef]          # the arguments that justified this merge
    operator: str                        # "sigma" | "gmax" | "manual" — which merge operator
    dialectical_tree_ref: str | None     # the rationale tree, when the merge was contested
    provenance: Provenance
```

The discipline (verbatim from the note): **this is merge, not canonicalization.** We do not rewrite `colour → color`. Both `Form`s, both `Sense`s, the `IC` with `aliases = {color, colour, ...}`, and the `MergeRecord` saying *on what evidence* the colour-senses of the two forms were judged to share referential identity — all persist. A merge can later be *split* (a `SplitRecord`, same shape, marking which senses left the cluster and why) without loss, because nothing was overwritten. This is exactly `belief-set`'s `merge_belief_profile` semantics, except: (a) we keep the inputs, (b) every merge carries provenance, (c) the `max_alphabet_size=16` ceiling means the actual merge computation runs per small profile (a handful of rival senses), never over the whole vocabulary — which is the right scope anyway.

### 3.4 Referential vs indexical

The split is structural, not annotational:

- **Referential** content → `Sense.gloss`, `Sense.definiens_edges`, `IC.member_sense_ids`. This is "what is denoted." `wash` and `warsh` share this — same act, same IC.
- **Indexical** signal → `Metadata.speaker_signal` (and `dialect`/`register`/`geography`/`period`) on the *form-flavoured* records, and/or as `ArgumentRef`s of `evidence_kind = HEURISTIC/CORPUS_STAT` that update a *belief about the speaker*, not about the word. `warsh` "indexes Appalachian / older / working-class speaker" is a fact recorded on the `warsh` `Form`'s metadata; it is **never** allowed to fork the IC or alter a `definiens_edge`. In `belief-set` terms: the indexical signal is part of the *source/entrenchment structure around* a belief, not the belief — which is why a provenance-carrying belief-set, not a flat dictionary, is the right shape, and why this layer is exactly where the argumentation/belief family beats vector soup.

So: a sentence with `warsh` in it gives you (1) the same referential edge `wash`'s IC would give, plus (2) an argument that updates `P(speaker is Appalachian)` etc. The base referential Kernel is computed on (1) only.

---

## 4. How this maps onto the argumentation / belief / defeasible tools

This is the §7-of-the-connection-report claim made into the data model. The mapping:

| Pipeline object | Argumentation object | Tool |
|---|---|---|
| sense-level definition graph (`DefinitionEdge`s as `supports`, `SenseRivalryEdge`s as `attacks`) | bipolar AF / ADF over **sense nodes** (not `lemma::pos`) | `argumentation` (`bipolar.py`, `adf.py`) — *honest granularity* |
| Kernel of that graph (leaf-strip / well-founded part) | grounded extension ≈ the acyclically-determined vocabulary; the "Rest" | `meanings.graph_analysis.compute_kernel` (the library's grounded semantics is the *wrong* operator at scale — see `argumentation-bridge-oewn.md`; use our own linear labelling) |
| MinSet / FVS over sense ICs | minimal-enforcement set forcing skeptical determinacy; outsider set of a stable extension *where one exists* | `meanings.minset` + `argumentation.enforcement.enforce_skeptical` (demo-scale only) |
| per-occurrence WSD (`Reading` selection, `SenseRivalryEdge` arbitration) | defeasible reasoning; the accepted extension is the disambiguated reading; the dialectical tree is the rationale | `gunray` (`DefeasibleTheory`, `build_tree`, `explain`); `UNCERTAIN` lexicality = `gunray`'s `UNDECIDED`, first-class |
| `IC` merge (`MergeRecord`) | belief merging over sense profiles, with provenance | `belief-set` (`merge_belief_profile`, `ICMergeOperator`) — per small profile |
| graded "how foundational is this sense/IC" | epistemic entrenchment / Spohn OCF | `belief-set` (`SpohnEpistemicState`, `EpistemicEntrenchment`) — build the OCF from the layer index; library transforms, doesn't infer |
| **admission of an IC to the controlled vocabulary** | accepted extension of a **defeasible theory** | `gunray`-shaped `AdmissionPolicy` (§5) |
| LLM/embedding proposals | *arguments* (`ArgumentRef` with `evidence_kind = LLM_PROPOSAL / EMBEDDING`) adjudicated by typed rules — never accepted wholesale | feeds the above; nothing else |

The load-bearing claims:

1. **The honest definition graph is over `Sense` nodes, not `lemma::pos`.** The current `paper-wordnet` graph's collapse to `lemma::pos` + first-representative gloss is what *creates* the artifacts; the bipolar-AF/ADF encoding of the sense graph is the one that means something. `argumentation_bridge.py` already builds bipolar/ADF wrappers — point them at the sense graph, not the lemma graph.
2. **The admission rule is a defeasible theory whose accepted extension is the controlled vocabulary.** Rules like: `r_admit: admitted(IC) -< maps_to_lexical_reading(IC), evidence_explicit(IC)`; `r_block_symbol: ~admitted(IC) -< only_reading_is(IC, symbol_code)`; `r_block_mismatch: ~admitted(IC) -< admission_depends_on_sense_mismatch(IC)` (the `no` ⊀ `no::n`-Nobelium rule); with `r_block_symbol > r_admit`, etc. The accepted set is `gunray`'s `yes` section. Correlation supplies `maps_to_lexical_reading` candidates; the rules adjudicate.
3. **The dialectical tree IS the merge/exclusion rationale.** The note demands "maintain provenance for each merge, split, exclusion, and admission decision." `gunray`'s `build_tree` / `explain` / `render_tree_mermaid` *is* that artifact — `MergeRecord.dialectical_tree_ref`, `ExclusionRecord`, and the admission theory's per-IC tree are not extra bookkeeping, they fall out of running the theory.
4. **IC merge is `belief-set`'s IC merging** — literally `merge_belief_profile` over the rival senses, with the discipline additions in §3.3.
5. **Correlation never wins on its own.** Structurally enforced by `EvidenceKind`: an `EMBEDDING`/`LLM_PROPOSAL` provenance can only ever sit on an `ArgumentRef`. The type system makes "vector soup decides" *unrepresentable*.

Scale caveat (verified in `argumentation-bridge-oewn.md`): all three sibling libraries are demonstrator-tier on a real vocabulary — `gunray` enumerates argument subsets, `belief-set` enumerates `2^n` worlds, `argumentation`'s enforcement is a brute-force oracle. The *graph-theoretic* part (Kernel, MinSet, SCC) the `meanings` repo already does at scale (0.8 s on 160k nodes). So the production path is: `meanings` machinery for the graph skeleton + the sibling libraries (and their semantics) as *per-SCC / per-profile oracles* and as the *conceptual type system*. The data model above is the type system; it stands whether or not the libraries are ever called at scale.

---

## 5. The two deliverable surfaces

The note is explicit: "the raw graph seed remains valuable as a strict feedback-vertex result; the human list is a separate controlled-vocabulary projection with policy." Two outputs, two definitions:

### 5.1 The strict typed seed

`= the grounded extension / FVS restricted to typed-lexical ICs.`

Concretely: build the sense-level definition graph (§3.1–§3.2), project it to the **IC layer** (an IC node has an edge to another IC node iff some member sense of the first appears, via a `Reading`, in the gloss of some member sense of the second), drop every IC whose aggregate `lexicality` is not `LEXICAL_WORD` (this is the filter that excludes `no::n`-Nobelium, taxa, chemicals, proper names, `UNCERTAIN`), compute `compute_kernel` + `solve_minset` on the surviving sub-DAG. Output = the MinSet over typed-lexical ICs. This is the "strict graph seed over typed sense/IC nodes" from the note's workstream. It is a *research artifact* — the answer to "how small is the non-circular core, done honestly" — not a vocabulary anyone would hand a learner.

### 5.2 The human Up-Goer list

`= the admitted extension of the admission theory.`

Concretely: run the `AdmissionPolicy` defeasible theory (§4, item 2) over the typed IC store; the admitted ICs (`gunray`'s `yes` section) are the vocabulary; each admitted IC ships with its `aliases` (so `colour` rides in alongside `color`), its `exclusions`, its `merge_provenance`, and its admission dialectical tree. A `Form` enters the human-readable word list iff it expresses some admitted IC's member sense **and** that reading is `LEXICAL_WORD` **and** the evidence is explicit **and** admission does not depend on a sense mismatch. This is a *superset-shaped* projection of 5.1: it can include phrases/idioms (`PHRASE`/`IDIOM` ICs) the strict seed excludes, and it is shaped by editorial policy the strict seed is not.

The relationship is **not** "5.2 is a subset of 5.1" — they're different objects. 5.1 is "what the graph forces, restricted to clean lexical items." 5.2 is "what the admission policy admits, which may add idioms and is filtered by explicit-evidence requirements 5.1 doesn't impose." Both are derived, both carry provenance, neither is the raw `lemma::pos` node set.

---

## 6. The falsifiable prediction

**Written down before the sense-level rebuild:** the sense-level Kernel should *shrink* relative to the current artifact-inflated lemma-level Kernel.

The reasoning (all numbers verified from the codebase / connection report): the `compute_kernel` self-loop fix (commit `7d12e64`-era) was *correct for the lemma-level graph* — a word literally in its own gloss is a 1-node FVS member — and it grew the lemma-level Kernel **12,853 → 18,151**, of which **3,413** are gloss self-loops. The upgoer note's diagnosis: many of those self-loops are *artifacts of the lemma collapse*. A gloss for `violin::n` that says "violin" is referring to the *intended sense* (or the IC), not literally re-defining `violin` in terms of itself. On the sense-level graph, the `Reading` of that occurrence resolves to a *different* node (another sense, or the IC), the self-loop dissolves, and the node leaves the Kernel under leaf-stripping. Plus: spelling-variant ICs (`color`/`colour`) merge two near-identical glosses into one node, removing duplicated cycle structure; symbol-code/taxon/chemical senses (`no::n`-Nobelium) are dropped before the strict-seed Kernel computation. All three forces push the (typed-lexical-IC) Kernel *down*.

**Prediction:** sense-level (typed-lexical-IC) Kernel < 18,151, and plausibly < 12,853 (below even the pre-fix lemma Kernel), because the lemma-level number was already inflated by the lemma collapse, not just by the self-loop fix.

**What it means if it *doesn't* shrink:** if the self-loops survive sense resolution — if `Reading`s of in-gloss tokens genuinely keep resolving to the head sense itself — then those are *real* definitional circularity, not artifacts, and the ingestion redesign did not do the thing it claims (the conflations weren't the source of the inflation). That would be a real result against the upgoer note's central diagnosis, and a signal to look elsewhere for what's inflating the Kernel. Either outcome is a check on the redesign; the prediction is not decoration.

(Cannot verify: I have not run the sense-level rebuild — it doesn't exist yet. The lemma-level numbers 12,853 / 18,151 / 3,413 are quoted from `reports/sibling-tools-connection.md` §7, not re-derived here. The current `build_synset_graph` is *not* the sense-level model described above — it has no lexicality typing, no IC layer, no provenance — so even running the current `--graph-type sense` would not test this prediction; the prediction is about the *redesigned* sense model.)

---

## 7. The "Why This Is Not Just An LLM" invariants, as type + epistemic-stance constraints

The upgoer note's six "required invariants" become, in this data model:

1. **Form is not sense.** `Form` and `Sense` are distinct record types; a `Form` carries no `gloss`, no `definiens_edges`. `normalize_lemma`'s lowercasing is a *join key*, never an identity — `No` and `no` are two `Form`s. *Violation looks like:* a node that is both "the string `no`" and "the negation"; i.e. the current `lemma::pos` graph.
2. **Sense is not IC.** `Sense.ic_id` is a *pointer set by a `MergeRecord`*, not an identity; an `IC` is the set of senses a merge unified, with the merge provenance retained. *Violation looks like:* canonicalizing `colour → color` and deleting `colour`.
3. **Referential meaning is not indexical signal.** Denotation lives in `Sense.gloss` / `definiens_edges` / `IC.member_sense_ids`; speaker-indexing lives in `Metadata.speaker_signal` and in `ArgumentRef`s about the speaker. The base referential Kernel is computed on the former only. *Violation looks like:* `warsh` forking the IC, or being dropped because "it's dialect."
4. **Definition dependency is not usage correlation.** A `DefinitionEdge` requires a `Reading` of a gloss `TokenOccurrence` (`context_kind = GLOSS_OF`); a corpus co-occurrence produces an `ArgumentRef` with `evidence_kind = CORPUS_STAT`, which can *propose* a sense/merge but cannot be a `DefinitionEdge`. *Violation looks like:* edges added because two words appear near each other in text.
5. **Graph necessity is not human-primitive admission.** Two surfaces (§5): the strict FVS-over-typed-lexical-ICs (graph necessity) is a *different object* from the admitted extension of the `AdmissionPolicy` (human-primitive admission). They are not even subset-related. *Violation looks like:* shipping the raw `MinSet` node set as "the words to teach."
6. **Embeddings or corpus statistics are evidence, not authority.** Enforced at the type level: `EvidenceKind ∈ {EMBEDDING, LLM_PROPOSAL, CORPUS_STAT}` provenances can only attach to `ArgumentRef`s; `Sense.lexicality`, `IC.member_sense_ids`, `IC.admitted`, and every `DefinitionEdge` are set only by a *rule* in the `AdmissionPolicy` / WSD theory that *adjudicated* such arguments. "Vector soup decides" is unrepresentable in the schema.

The epistemic stance, stated once: the graph seed is *evidence about definitional circularity* — it is not the human vocabulary, and the data model must make it impossible to confuse the two. The typed layers + the provenance-on-every-edge + the two-surfaces split are how that impossibility is built in.

---

## 8. What I could not verify / open schema questions

- **The IC-projection of the sense graph** (§5.1): I assert "IC `A` → IC `B` iff some member sense of `A` appears in the gloss of some member sense of `B`." The alternative — keep the graph at the sense layer and only restrict the *seed output* to ICs — would give different Kernel numbers. The note says "build sense-level nodes first, then project to ICs and human forms" but doesn't pin down whether the *Kernel* is computed pre- or post-IC-projection. I went with post-projection for the strict seed because that's what "restricted to typed-lexical ICs" most naturally means, but this is a real choice with measurable consequences. **This is the §8 item the Gemini draft might reasonably disagree with.**
- The exact `Lexicality` boundary between `TECHNICAL` and `LEXICAL_WORD`, and whether `PHRASE`/`IDIOM` are admissible to the *strict* seed or only the human list — the note lists the enum but not the admission cut precisely; I put the cut at `LEXICAL_WORD`-only for the strict seed.
- Whether `Reading.resolved_to` should *ever* be allowed to point at an `IC` directly, or always at a `Sense` (with IC membership inferred) — heterogeneous graphs are messier; I allowed it because the note says glosses should resolve "to the *intended* sense, or to the IC, where possible."
- The 12,853 / 18,151 / 3,413 numbers are quoted, not re-derived; `git log` for commit `7d12e64` was not inspected by me in this session.
- No sense-level rebuild exists, so §6's prediction is untested by construction.

---

### Summary (5 sentences)

The current `lemma::pos` graph with first-representative glosses conflates form, sense, and identity-cluster, which is what manufactures the artifacts (`no::n` = Nobelium, 3,413 gloss self-loops, spelling-variant inflation), so the project needs a typed stack `Form → TokenOccurrence → Reading → Sense → IC` plus `Construction`, `Metadata`, `Provenance`, and `AdmissionPolicy` as distinct records, with a shared `Lexicality` enum (lexical word / symbol-code / abbreviation / proper name / taxon / chemical / technical / phrase / idiom / uncertain) gating admission. Definition edges become `supports` between resolved `Sense` nodes (making the sense graph the honest bipolar-AF/ADF), rival senses of a form `attack` each other (defeasible WSD, `gunray`-shaped, with the dialectical tree as the rationale), and IC merge is a `belief-set` profile merge over sense clusters that *keeps both forms* and carries per-merge provenance — never canonicalization. Referential content lives in glosses/definiens-edges/IC membership; indexical signal (`warsh` → region/class/age) lives in `Metadata.speaker_signal` and as arguments about the speaker, outside the base referential IC. The two deliverables are the strict typed seed (Kernel/FVS restricted to typed-lexical ICs — a research artifact) and the human Up-Goer list (the admitted extension of the admission defeasible theory — shaped by editorial policy), with the falsifiable prediction that the sense-level Kernel *shrinks* versus the artifact-inflated lemma-level 18,151, and the type system itself enforcing the six "not just an LLM" invariants by making "embeddings decide" unrepresentable.

**One design decision I'm least sure about:** whether the Kernel/MinSet should be computed on the IC-projected graph (my choice for the strict seed) or on the raw sense graph with only the *output* restricted to ICs — the upgoer note doesn't pin this down, the two give different numbers, and a Gemini draft could reasonably argue the sense-layer Kernel is the "real" object with IC-restriction applied only at the seed-export step.
