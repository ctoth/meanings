# Sibling tool inventory: `gunray` (defeasible-logic engine)

Survey of `C:\Users\Q\code\gunray` as of 2026-05-12. Lens: *could a defeasible-logic
engine model word meaning — definitions as defeasible rules, polysemy as competing
rules where context defeats, `UNDECIDED` as a real outcome for circular definitions?*

All paths below are relative to `C:\Users\Q\code\gunray\` unless absolute.

---

## 0. What it is, one paragraph

Pure-Python implementation of García & Simari 2004 *Defeasible Logic Programming*
(DeLP), plus a stratified-Datalog engine and a KLM-closure engine. Zero runtime
deps, MIT, `requires-python = ">=3.11"` (`pyproject.toml` lines 1-12). Package name
`gunray`, version 0.1.0. The DeLP path is the "main event": you give it facts,
strict rules, defeasible rules, defeaters, and a superiority relation; it enumerates
arguments, builds dialectical trees, marks them U/D by Procedure 5.1, and answers
queries four-valued: `YES` / `NO` / `UNDECIDED` / `UNKNOWN`. It can also hand back
the dialectical tree, the marking, a Unicode/Mermaid render, and a prose
"why did the engine decide that" transcript.

---

## 1. What's implemented (walk of `src/gunray/`)

24 modules. Public surface in `__init__.py` (135 lines, exports ~70 names).
`ARCHITECTURE.md` is the authoritative internals map; it matches the code.

### Representation — `DefeasibleTheory` (`schema.py`)

`schema.py` lines 144-209. Frozen dataclass with slots; `__post_init__` validates.
Fields:

- `facts: Mapping[str, Iterable[FactTuple]]` — predicate → set of argument-tuples,
  e.g. `{"bird": {("tweety",), ("opus",)}}`. `FactTuple = tuple[Scalar, ...]`,
  `Scalar = str | int | float | bool` (`schema.py` lines 20-21).
- `strict_rules: tuple[Rule, ...]` — Π rules (classical, indefeasible).
- `defeasible_rules: tuple[Rule, ...]` — Δ rules (`head -< body`).
- `defeaters: tuple[Rule, ...]` — Nute/Antoniou third category: a rule that can
  *block* an argument but never *support* a warranted one (undercutting defeat,
  cf. `examples/looks_red_under_red_light.py`). Not a García-2004 rule kind;
  documented as a Gunray extension (`parser.py` lines 1-10).
- `presumptions: tuple[Rule, ...]` — defeasible rules with empty body (`h -< true`),
  García 2004 §6.2; `__post_init__` rejects non-empty bodies (`schema.py` 176-181).
- `superiority: tuple[tuple[str, str], ...]` — explicit priority pairs
  `(stronger_rule_id, weaker_rule_id)` over declared rule ids; validated at
  construction as irreflexive + acyclic over known ids (`schema.py` 200-209,
  `_raise_if_superiority_cyclic` 226-249).
- `conflicts: tuple[tuple[str, str]]` — extra predicate pairs treated as
  mutually contradictory beyond the built-in `p` / `~p` strong negation.

`Rule` (`schema.py` 128-142): `id: str`, `head: str`, `body: tuple[str, ...]`.
Head and body literals are **text strings** in a DeLP surface syntax, parsed lazily:
`"flies(X)"`, `"~flies(X)"`, `"penguin(X)"`. A body element starting with `"not "`
is default negation (only allowed in defeasible rules — `parser.py` 99-110). Strong
negation is a leading `~` on the predicate (`~p` and `p` collide; `parser.py`
`_PREDICATE_IDENTIFIER_RE` line 41 allows optional `prefix:` namespace, e.g.
`oewn:dog`). Variables are `[A-Za-z][A-Za-z0-9_]*` starting uppercase by Datalog
convention; `_` wildcards exist. Arithmetic / comparison terms exist in the Datalog
side (`AddExpression`, `Comparison` in `types.py` 27-48).

Backend value types (`types.py`): `Variable`, `Constant`, `Atom(predicate, terms)`,
`GroundAtom(predicate, arguments)`, `DefeasibleRule(rule_id, kind, head, body,
default_negated_body)`, `GroundDefeasibleRule(...)`. `GroundAtom` carries the `~`
prefix in `.predicate` for negated literals (per `disagreement.complement`).

### Grounding

`grounding.py` / `grounding_types.py` — a single grounding pass turns variable
rules into `GroundDefeasibleRule`s over the active Herbrand universe. `_ground_theory`
(in `_internal.py`, used everywhere) returns grounded strict/defeasible/defeater
rules, the fact atoms, and the `conflicts` set. `GroundingInspection` /
`GroundRuleInstance` / `GroundRuleResolution` (`grounding_types.py`) record what got
grounded; exposed on the trace as `trace.grounding_inspection`. Naive subset
enumeration in `build_arguments` is brute-force on the *grounded* rule base — there's
a `max_arguments` budget (`anytime.EnumerationExceeded`, carries `partial_arguments`).

### The evaluator(s) — `adapter.py`, `defeasible.py`, `evaluator.py`, `closure.py`

`GunrayEvaluator` (`adapter.py`) is a dispatcher over input type:
- `DefeasibleTheory` → `DefeasibleEvaluator` (`defeasible.py`) — the DeLP pipeline.
- `Program` → `SemiNaiveEvaluator` (`evaluator.py`) — stratified Datalog,
  Apt-Blair-Walker safety, `NegationSemantics.SAFE` (default) vs `NEMO`.
- propositional defaults / `ClosurePolicy` → `ClosureEvaluator` (`closure.py`) —
  KLM rational / lexicographic / relevant closure + KLM `Or` (zero-arity only).

`DefeasibleEvaluator.evaluate(theory, *, marking_policy=MarkingPolicy.BLOCKING,
closure_policy=None, grounding_mode=GroundingMode.DIRECT,
negation_semantics=NegationSemantics.SAFE,
projection_semantics=ProjectionSemantics.GARCIA, max_arguments=None) -> DefeasibleModel`
(`defeasible.py` 72-96). `evaluate_with_trace(...)` (98-201) is the canonical entry
point and additionally returns a `DefeasibleTrace`.

DeLP pipeline body: `_evaluate_via_argument_pipeline` (`defeasible.py` 204-354):
`build_arguments` → for each non-defeater argument, `build_tree` → `mark` → collect
warranted atoms → project into the four answer sections. A **strict-only fast path**
(`_is_strict_only_theory`, 689-695) routes degenerate theories (no defeasible rules,
no defeaters, no presumptions, no superiority) into the Datalog engine, after a Π
consistency check that raises `ContradictoryStrictTheoryError` on any `{h, ~h}` or
listed-conflict pair (740-746).

### `ClosurePolicy` / `MarkingPolicy` — BLOCKING vs PROPAGATING, team-defeat?

`schema.py` 44-117. **Two separate enums.**
- `MarkingPolicy`: `BLOCKING` (the García-2004 dialectical-tree path — the default
  and the real one), `ANTONIOU_BLOCKING`, `ANTONIOU_PROPAGATING` (opt-in
  Antoniou-2007 §3.5 ambiguity-blocking vs ambiguity-propagating defeasible-logic
  projections — implemented as fixpoint computations in `_evaluate_antoniou_policy`,
  `defeasible.py` 525-606). Note `ARCHITECTURE.md` lines 137-150 says Antoniou
  ambiguity-propagation was *deprecated / out-of-contract*; the `schema.py` enum
  values and the `defeasible.py` handlers are present, so the doc and code are
  slightly out of sync — treat the Antoniou policies as experimental.
- `ClosurePolicy`: `RATIONAL_CLOSURE`, `LEXICOGRAPHIC_CLOSURE`, `RELEVANT_CLOSURE`
  — route to the KLM engine, not the dialectical-tree path.
- `ProjectionSemantics`: `GARCIA` (default four-valued) vs `SPINDLE` (Lam/Governatori
  2009 + Maher 1999 constructive-defeasible-logic proof tags; superiority applied at
  the opposing-rule level; `_evaluate_spindle_projection`, `defeasible.py` 357-439).
- `GroundingMode`: `DIRECT` vs `DILLER_SIMPLIFIED` (Diller 2025 strict/fact
  simplification before argumentation).

Ambiguity blocking vs propagating: García's dialectical tree is **blocking** by
construction; ambiguity-propagation is only available through the explicit
`ANTONIOU_PROPAGATING` policy. **Team defeat**: not implemented as such — there is no
Maher-99 "team of rules" mechanism in the BLOCKING path; the SPINdle projection
handles superiority opposing-rule-by-opposing-rule, not team-wise.

### The answer model — `model.sections`

`DefeasibleModel(sections: GarciaSections)` where `GarciaSections = Mapping[str,
Mapping[str, set[FactTuple]]]` (`schema.py` 24-25, 219-223). The DeLP path populates
exactly four section keys (`defeasible.py` 332-337):

- `"yes"` — warranted literals (some argument for the literal roots a tree marked
  `U`); strict Π consequences also land here.
- `"no"` — the strong complement is warranted, *or* a defeater rule probed the
  literal (Nute/Antoniou contribution — a defeater touch makes the attacked literal
  `NO`; `defeasible.py` 320-329).
- `"undecided"` — neither side warranted but at least one argument exists on some
  side. **This is a first-class outcome, not an error.**
- `"unknown"` — the literal's predicate (strong negation stripped) is absent from
  the theory's language.

`ARCHITECTURE.md` lines 44-48: the pre-rewrite section names `definitely`,
`defeasibly`, `not_defeasibly` are **no longer model fields** — the README's opening
example (`model.sections["defeasibly"]`) is stale relative to the current code; the
live keys are `yes`/`no`/`undecided`/`unknown`. The standalone `answer()` function
(`dialectic.py` 869-913, `answer.py`) returns the `Answer` enum
(`YES`/`NO`/`UNDECIDED`/`UNKNOWN`) — García & Simari 2004 Def 5.3.

### Superiority / priority — `preference.py`

`preference.py` 258-356. `SuperiorityPreference(theory)` reads `theory.superiority`,
computes its transitive closure over rule ids at construction, and: argument A1 is
preferred to A2 iff *every* rule in A1 dominates *every* rule in A2 under that
closure. Strict-only (empty-rule) arguments are incomparable under it.
`GeneralizedSpecificity(theory)` (82-256) is the fallback: Simari & Loui 1992 Lemma
2.4 antecedent-coverage check (A1 ≽ A2 iff every antecedent of A2 is derivable from
K_N ∪ An(A1) ∪ rules(A2)); facts are deliberately excluded from K_N or specificity
would collapse. `CompositePreference(SuperiorityPreference(theory),
GeneralizedSpecificity(theory))` (359-454) is what the evaluator uses
(`defeasible.py` 249-252): **first-criterion-to-fire** — explicit user superiority
decides any pair it has an opinion on, otherwise fall through to specificity.
`TrivialPreference` (prefers nothing — every counter-argument becomes a blocking
defeater) is exported for tests. `PreferenceCriterion` is a `Protocol`
(`prefers`, `explain_preference`). `PreferenceComparison` is an inspectable
relation report (`left`/`right`/`incomparable`/`equi_specific` + reason + citation).

### Semantics — well-founded vs other

García/Simari DeLP dialectical-tree semantics, *not* a well-founded model. Marking
(`mark`, `dialectic.py` 508-597) is Procedure 5.1 post-order U/D: leaf → `U`; any
`U` child → `D`; all-`D` children → `U` (reinstatement). The tree is finite by
construction (Def 4.7 cond 1, cond 3 forbids re-entry along an argumentation line).
There is *also* a KLM closure engine (rational/lex/relevant — `closure.py`) and a
Goldszmidt/Pearl p-consistency analyzer (`consistency.py`), both separate from the
DeLP answer semantics. No partial-stable / WFS module.

### Consistency / coherence checks — `consistency.py`, plus Π checks

- Π contradiction: `ContradictoryStrictTheoryError` raised if strict closure has
  `{h, ~h}` or a `conflicts` pair (`arguments.py` 96-97; `defeasible.py` 724-746).
- Argument non-contradiction (García Def 3.1 cond 2): every candidate argument's
  rule set, unioned with Π and closed, must be free of complementary pairs
  (`arguments.py` 167-185).
- Dialectical-line concordance (García Def 4.7 cond 2): the supporting set (even
  positions in the line) and interfering set (odd positions) must each stay
  concordant with Π; enforced *during* tree construction (`dialectic.py` `_concordant`,
  `_concordant_rules`, `_expand` 395-492).
- `consistency.py`: Goldszmidt & Pearl 1992 p-consistency for small zero-arity
  conditional databases — `ConditionalSentence`, `ConditionalDatabase`,
  `ConsistencyReport`, `analyze_p_consistency`, `strictly_p_entails`. Standalone; not
  wired into `DefeasibleEvaluator`.

### "Explain why" / argument-trace facility — `dialectic.py`, `trace.py`

Rich. `build_arguments(theory) -> frozenset[Argument]` (`arguments.py`);
`Argument(rules: frozenset[GroundDefeasibleRule], conclusion: GroundAtom)`.
`build_tree(root_arg, criterion, theory) -> DialecticalNode`
(`DialecticalNode(argument, children, defeater_kind)`); `mark(node) -> "U"|"D"`;
`render_tree(node)` → Unicode tree; `render_tree_mermaid(node)` → Mermaid flowchart;
`explain(tree, criterion)` → prose transcript naming the supporting argument, each
defeater considered, and the preference reason on every edge (`dialectic.py`
698-808). `counter_argues`, `proper_defeater`, `blocking_defeater`, `classify_defeat`
expose Defs 3.4/4.1/4.2. `DefeasibleTrace` (`trace.py` 130-170) carries
`grounding_inspection`, `arguments`, `trees`, `markings`, and lookups
`tree_for(atom)` / `marking_for(atom)` / `arguments_for_conclusion(atom)` (plus
`*_parts` string overloads). `DatalogTrace` carries per-stratum, per-iteration
rule-fire logs for the Datalog path.

Entry-point names worth knowing: `GunrayEvaluator().evaluate(theory) ` /
`.evaluate_with_trace(...)`; `DefeasibleEvaluator().evaluate(theory, *,
marking_policy=...)`; `answer(theory, GroundAtom(...), criterion)`;
`build_arguments`, `build_tree`, `mark`, `explain`, `render_tree`,
`render_tree_mermaid`; `GeneralizedSpecificity(theory)`,
`SuperiorityPreference(theory)`, `CompositePreference(...)`.

---

## 2. Data structures — and how to encode dictionary content

- A **theory** = `DefeasibleTheory(facts=..., strict_rules=..., defeasible_rules=...,
  defeaters=..., presumptions=..., superiority=..., conflicts=...)`. All frozen.
- A **rule** = `Rule(id="r1", head="<literal text>", body=["<literal text>", ...])`.
  Literal text uses predicate + paren args; `~` for strong negation; `not X` body
  prefix for default negation; uppercase = variable.
- A **derivation/argument** = `Argument(rules: frozenset[GroundDefeasibleRule],
  conclusion: GroundAtom)`. A **trace node** = `DialecticalNode(argument, children:
  tuple[DialecticalNode,...], defeater_kind: "root"|"proper"|"blocking")`.

**"Word w is defined using words u, v"** — straightforward as a defeasible rule
(definitions are not strict equivalences — exceptions, prototype effects — so
defeasible is the right kind):

```python
Rule(id="def_w", head="means(w)", body=["means(u)", "means(v)"])
# or, to model "knowing/grounding w follows defeasibly from grounding its definiens":
Rule(id="def_w", head="grounded(w)", body=["grounded(u)", "grounded(v)"])
```

**"Word w has sense s1 (rule r1) and sense s2 (rule r2), r1 > r2 in context c"** —
two competing defeasible rules whose heads disagree (e.g. `sense(w, s1)` vs
`~sense(w, s1)` / or `reading(w, s1)` vs `reading(w, s2)` made mutually exclusive via
`conflicts=(("reading_s1","reading_s2"),)`), plus an explicit superiority pair —
*but* superiority in Gunray is **unconditional** over rule ids, not parameterized by
a context predicate. To make "r1 > r2 *only in context c*" you'd instead make the
context a body literal: `r1: reading(w,s1) -< triggers(w), context(c)` and let
`GeneralizedSpecificity` award r1 the win because it discharges more antecedents than
r2 — that is the idiomatic way Gunray gets context-sensitive defeat (the
chicken/scared-chicken and penguin examples work exactly this way). Pure
`theory.superiority` is for global, context-free priority.

**`UNDECIDED` for a genuinely circular definition** — see §3.

---

## 3. The cycles / UNDECIDED story

This is the load-bearing question. Three sub-cases:

**(a) Plain rule cycle `r1: a -< b; r2: b -< a`, no facts.** `build_arguments`
builds minimal rule sets bottom-up from `pi_closure` (the strict-only closure of
facts under strict rules) (`arguments.py` 138-185). With no facts, `pi_closure` is
empty, neither `a` nor `b` ever gets a non-empty *minimal* support — the loop
`while changed` makes no progress — so **no argument for `a` or `b` is ever
constructed**. Then `answer(theory, a, criterion)` (`dialectic.py` 869-913): not
warranted (no argument), complement not warranted, `has_argument_for_either` is
False, and `a`'s predicate *is* in the language → returns **`Answer.UNDECIDED`**
(the final `return Answer.UNDECIDED` at line 913, *not* `UNKNOWN`). In the section
projection (`defeasible.py` 311-330), `a` lands in `"undecided"`. So: a cyclic
definition with no external grounding ⇒ `UNDECIDED`. (If the predicate appeared
*nowhere* — not even in a rule head/body — it would be `UNKNOWN` instead;
`dialectic._theory_predicates` 811-827 scans facts + rule heads + rule bodies.)

This is a clean analogue of "circular definition, no grounding set ⇒ undecided."
Add a fact (or a presumption) that grounds `b`, and `a` becomes derivable and
`YES` — analogue of "supply a member of the minimal grounding set."

**(b) Mutual attack with superiority — `r1: flies -< bird; r2: ~flies -< penguin`,
facts `bird(opus), penguin(opus)`, and `r2 > r1` (or specificity favors r2).** Both
arguments get built. `build_tree` on the `flies(opus)` argument admits the
`~flies(opus)` argument as a *proper* defeater (since r2 is preferred); the child
is a leaf → marked `U`; the root → `D`. `build_tree` on the `~flies(opus)` argument:
the `flies(opus)` argument is *not* a proper or blocking defeater of it (preference
goes the other way), so the tree is a bare root → `U`. ⇒ `~flies(opus)` warranted ⇒
`flies(opus)` is **`NO`**, `~flies(opus)` is **`YES`**. (This is the README's Tweety
example and `explain()` output.) Without the superiority and without a specificity
difference (the Nixon diamond — `republican`/`quaker` both bare facts, neither rule
out-specifies the other), both trees come back `D` (each argument is blocked by the
other), neither side warranted, arguments exist on both sides ⇒ **`UNDECIDED`**
(`examples/nixon_diamond.py`; README "`UNDECIDED` is a first-class answer" section).

**What exactly produces `UNDECIDED`** (`dialectic.answer` 869-913, mirrored in
`defeasible.py` 311-330): the literal is not warranted, its complement is not
warranted, **and** (an argument exists for one side **or** the predicate is in the
language). Two distinct generators: (i) competing arguments that mutually block (no
preference resolves it), (ii) the predicate exists in the rule language but no
argument can be grounded (the circular-no-grounding case). Stability: the marking is
a pure deterministic post-order function on a finite tree (`mark` is "no mutation, no
caching, no early exit" — `dialectic.py` 508-520), and `build_arguments` returns a
finite frozenset; `answer`/section-projection are deterministic over sorted argument
lists. So `UNDECIDED` is *stable* in the sense of reproducible and well-defined. It
is **not** "well-founded" in the WFS technical sense — Gunray does not compute a
well-founded model; there's no third-truth-value fixpoint, it's the García
dialectical-tree definition.

---

## 4. Existing lexical / semantic contact

**Essentially none.** Grepped `notes/`, `papers/`, `docs/` (no `docs/` dir),
`examples/`, `README.md`, `ARCHITECTURE.md` for: dictionary, lexicon, WordNet, word
sense, polysemy, definition (as in lexical definition), symbol grounding, Harnad,
gloss, lexical semantics.

- No WordNet, no `wn`, no polysemy, no Harnad, no symbol-grounding anywhere.
- The only literal "gloss" hit: `notes/readme_rewrite.md` line 25 — "Opens with Nute
  *gloss*" (i.e. a gloss on the name, not a dictionary gloss).
- "definition" hits are all "García & Simari 2004 Definition 3.1" etc.
- "dictionary" hits are Python `dict` usage.
- `papers/` (14 papers) is entirely defeasible-logic / argumentation / Datalog
  theory: García 2004, Simari 1992, Antoniou 2007, Stolzenburg 2003 (specificity),
  Lam 2009 (SPINdle), Maher 1999/2021, Governatori 2004, Goldszmidt 1992, Diller
  2025, Bozzato 2020, Morris 2020, Deagustini 2013, Darwiche 1997. No lexical
  semantics, no cognitive-science / grounding lineage.
- Closest *conceptual* contact: `examples/looks_red_under_red_light.py` (Pollock's
  undercutting defeater — perceptual evidence, grounding-flavored but not lexical)
  and `examples/platypus.py`, `nixon_diamond.py`, `innocent_until_proven_guilty.py`
  (classic non-monotonic-reasoning toy domains). No domain example touches language.

So: zero prior art to build on inside gunray; whatever the meanings project does with
it would be greenfield modeling.

---

## 5. How to depend on it

- Install: `pip install git+https://github.com/ctoth/gunray.git` or
  `uv add git+https://github.com/ctoth/gunray.git` (README "Install"). Local clone +
  `uv sync --extra dev` for dev.
- Package name `gunray`; import e.g.
  `from gunray import DefeasibleTheory, GunrayEvaluator, Rule, Answer, answer,
  GeneralizedSpecificity, build_arguments, build_tree, mark, explain, render_tree`
  and `from gunray.types import GroundAtom`.
- Python `>=3.11`. Zero runtime dependencies (`pyproject.toml` `dependencies = []`).
  Dev extras only: `datalog-conformance`, `hypothesis`, `pyright`, `pytest`,
  `pytest-timeout`, `ruff`, `vulture`. MIT.
- It's a library, no CLI. Hatchling build; wheel packages `src/gunray`.
- Caveat for callers: README's headline snippet uses
  `model.sections["defeasibly"]` and `MarkingPolicy.BLOCKING` as a kwarg to
  `GunrayEvaluator().evaluate(...)`; the *current* section keys are
  `yes`/`no`/`undecided`/`unknown` (`ARCHITECTURE.md` 44-48, `defeasible.py`
  332-337). Use `evaluate_with_trace` and the four current keys, or the `answer()`
  function.

---

## Raw observations only

- **Size**: `src/gunray/` is 24 `.py` modules; the heavy ones are `defeasible.py`
  (~760 lines), `dialectic.py` (~915), `preference.py` (~470), `arguments.py` (~270),
  `parser.py` (~460). Plus `evaluator.py` (Datalog), `closure.py` (KLM),
  `consistency.py` (Goldszmidt/Pearl). `examples/` has ~18 worked examples; `tests/`,
  `notes/` (~60 markdown files of dev history), `papers/` (14 papers with notes),
  `reviews/`, `workstreams/`, `prompts/`, `tools/`, `out/`, `logs/`. There's also a
  stray `pyghidra_mcp_projects/` dir at repo root — looks unrelated to gunray.
- **Surprise — README is partly stale**: `model.sections["defeasibly"]` /
  `["definitely"]` in the opening example are no longer model fields per
  `ARCHITECTURE.md`; live keys are `yes`/`no`/`undecided`/`unknown`. Also the README
  shows `GunrayEvaluator().evaluate(theory, marking_policy=...)` but `evaluate` on the
  dispatcher and on `DefeasibleEvaluator` take `marking_policy` as keyword-only — fine
  — yet the README example may not actually run as written against current section
  names.
- **Surprise — Antoniou doc/code mismatch**: `ARCHITECTURE.md` 137-150 says Antoniou
  ambiguity-propagation is deprecated/out-of-contract and `Policy.PROPAGATING` was
  removed, but `MarkingPolicy.ANTONIOU_BLOCKING` / `ANTONIOU_PROPAGATING` enum values
  exist and `_evaluate_antoniou_policy` (`defeasible.py` 525-606) implements both.
  Treat as experimental, possibly half-reverted.
- **Surprise — performance**: argument enumeration is explicitly "naive subset
  enumeration" / "brute-force"; comments warn a 20-rule chain forced 2^20 closure
  checks before the bottom-up minimal-support rewrite landed. There's a
  `max_arguments` budget and `EnumerationExceeded` with partial results. For a
  dictionary-scale rule base (tens of thousands of definition rules) this engine is
  almost certainly not going to enumerate arguments tractably — it's built for
  small hand-authored theories, not WordNet-scale graphs. The closure-cycle /
  `UNDECIDED` *semantics* might still be the conceptually right model; the
  *implementation* would need scoping to small sub-theories.
- **Gap for the dictionary use-case**:
  (1) superiority is global over rule ids, not context-conditional — context-sensitive
  sense selection has to be encoded via extra body literals + specificity, not via the
  `superiority` field;
  (2) no notion of "minimal grounding set" / feedback-vertex-set — Gunray tells you a
  literal is `UNDECIDED`, it does not tell you *which* facts you'd need to add to make
  it `YES` (you'd compute that externally, e.g. with the meanings project's graph
  machinery, then feed the seeds back in as `facts`/`presumptions`);
  (3) no built-in "the predicate is circular" classifier distinct from `UNDECIDED` —
  circular-no-grounding and mutually-blocked-arguments both surface as `undecided`;
  distinguishing them means inspecting whether `build_arguments` produced anything;
  (4) literals are flat predicate(args) text — no native multi-sense / sense-key
  structure; you choose the encoding.
- **Most relevant capability**: the four-valued answer with `UNDECIDED`/`UNKNOWN` as
  first-class outcomes (`Answer`, `dialectic.answer`, the `undecided`/`unknown`
  sections), combined with the fact that a definitional cycle with no external
  grounding *naturally* yields `UNDECIDED` (not error, not arbitrary winner) and that
  adding a grounding fact flips dependents to `YES` — that is a direct, working
  formal analogue of "the Kernel is the un-grounded circular core; pick a minimal
  grounding set and the rest becomes derivable." The `explain()` / dialectical-tree
  render is the secondary draw: it can show *why* one sense reading defeats another.
