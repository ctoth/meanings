# Sibling tool inventory: `argumentation`

Scout survey of `C:\Users\Q\code\argumentation` — a pure-Python formal-argumentation library — read with one lens: *could its machinery be applied to the dictionary-grounding problem in `C:\Users\Q\code\meanings`?* This document maps the library; it does not argue the connection.

All paths below are relative to `C:\Users\Q\code\argumentation\` unless absolute.

---

## 0. TL;DR map

- ~20.5k lines of source under `src/argumentation/`, 51 modules, pure-Python core with zero runtime deps.
- It is a *finite formal argumentation* kernel: Dung AAFs + extension/labelling semantics, ASPIC+, ABA/ABA+, ADFs, bipolar AFs, value-based AFs, SETAFs, claim-augmented AFs, partial/incomplete AFs, AF revision, dynamics, enforcement, probabilistic AFs, gradual/ranking-based semantics, weighted AFs, SAT/ASP/datalog encodings, ICCMA interop, plus typed solver-adapter boundaries.
- The fundamental object is **a directed graph of string-id nodes with an attack/defeat edge relation** (`ArgumentationFramework` in `dung.py`, line 19). That is structurally very close to "a directed graph of words with definition edges" — same shape, different edge semantics.
- There is **zero existing lexical/dictionary/WordNet/symbol-grounding/feedback-vertex-set content** in `notes/`, `papers/`, `docs/`, `reports/`, `workstreams/`, `CITATIONS.md`. The only hits for "lexico*" are "lexicographic" (the ordering, used in ranking semantics). Reported in section 4.

---

## 1. What's actually implemented (`src/`)

Every module is `argumentation.<name>`. Import name `argumentation`; PyPI distribution name `formal-argumentation`. Reference-implementation status noted per item.

### Core: Dung AAFs, labellings, preferences, dispatch

- **`dung.py`** (684 lines, full reference impl). `ArgumentationFramework` frozen dataclass: `arguments: frozenset[str]`, `defeats: frozenset[tuple[str,str]]`, optional `attacks: frozenset[tuple[str,str]] | None` (pre-preference layer; conflict-freeness uses `attacks`, defence uses `defeats` — Modgil & Prakken 2018 Def 14). Structural equality, immutable, no global state.
  - Primitives: `conflict_free(s, relation)`, `attackers_of`, `defends`, `characteristic_fn`, `admissible`, `range_of` (lines 96–192).
  - Extensions / labellings: `grounded_extension(af) -> frozenset[str]` (193), `complete_extensions(af) -> list[frozenset[str]]` (217), `preferred_extensions` (255), `stable_extensions` (271), `semi_stable_extensions` (318, Caminada 2011), `stage_extensions` (330), `eager_extension` (348), `naive_extensions` (441), `cf2_extensions` (496, Gaggl & Woltran 2013), `stage2_extensions` (512), `ideal_extension` (645, Dung-Mancarella-Toni 2007), plus prudent variants `prudent_conflict_free` / `prudent_admissible` / `prudent_preferred_extensions` / `prudent_grounded_extension` (575–614) and `indirect_attacks` (548).
  - Has a private `_strongly_connected_components` (374) — Tarjan over the defeat relation, used by cf2/stage2 — and `_subframework` (420). **This is the only SCC code in the library** (relevant: the dictionary project does its own SCC work in `graph_analysis.py`).
- **`labelling.py`** (367 lines). `Labelling` (three-valued IN/OUT/UNDEC); `Labelling.from_extension(af, ext)` bridge; `.in_arguments`, `.out_arguments`, `.undecided_arguments`, `.range`.
- **`preference.py`**. `strict_partial_order_closure` (transitive closure, rejects cycles + reflexivity), `strictly_weaker` (elitist/democratic over numeric strength vectors), `defeat_holds`.
- **`semantics.py`**. Set-returning dispatcher across families: `extensions(af, semantics=...)` (line 129), `accepted_arguments(af, semantics=..., mode="credulous"|"skeptical")` (144). Dung names accepted: `grounded, ideal, complete, preferred, semi-stable, stage, stage2, cf2, prudent-grounded, prudent-preferred, stable`. Also routes bipolar and partial semantics.

### Structured argumentation: ASPIC+, ABA/ABA+, accrual

- **`aspic.py`** (1394 lines, full reference impl — the biggest module). `ArgumentationSystem`, `ContrarinessFn`, `GroundAtom`, `Literal`, `KnowledgeBase`, `Rule`, `PreferenceConfig`, `CSAF`. Functions: `build_arguments(system, kb)`, `compute_attacks(args, system)`, `compute_defeats(attacks, args, system, kb, pref)`, accessors `conc/prem/sub/top_rule/def_rules/last_def_rules/prem_p/is_firm/is_strict`, `transposition_closure`, `strict_closure`, `is_c_consistent`.
- **`aspic_encoding.py`** (766 lines). Deterministic ASP-style fact vocabulary for ASPIC+ theories (Lehtonen-Niskanen-Järvisalo 2024) + typed grounded-query surface, backed by reference projection or registered backend (clingo via `[asp]`).
- **`aspic_incomplete.py`**. `evaluate_incomplete_grounded` — enumerates all completions of unknown ordinary premises, classifies a query literal as `stable | relevant | unknown | unsupported`.
- **`subjective_aspic.py`**. Wallner-style value filtering before ASPIC+ construction.
- **`accrual.py`**. Prakken weak/strong applicability + accrual envelopes for same-conclusion arguments.
- **`aba.py`** (387 lines, full reference impl). Flat ABA / ABA+ over ASPIC literals: complete/preferred/stable/naive/grounded/well-founded/ideal assumption-extension functions + a Dung projection.
- **`aba_sat.py`** (911 lines). Task-directed support-mask SAT enumeration for ABA stable/complete/preferred.
- **`aba_asp.py`** (355 lines). Clingo-backed ABA extension queries (`[asp]` extra) — solver-adapter boundary.

### ADFs (abstract dialectical frameworks)

- **`adf.py`** (638 lines, full reference impl). `AbstractDialecticalFramework` dataclass (statements + acceptance conditions). Acceptance conditions are a **typed AST**: `AcceptanceCondition` base, `Atom`, `True_`, `False_`, internal `_Not/_And/_Or`, smart constructors `Not()`, `And(children)`, `Or(children)` (lines 37–161). `ThreeValued` StrEnum, `Interpretation`, `LinkType` StrEnum (link classification: supporting/attacking/redundant/dependent).
  - `gamma(framework, interpretation)` operator (200); `grounded_interpretation` (218, well-founded fixpoint); `is_admissible`/`is_complete` (229/236); `admissible_interpretations` (243), `complete_models` (253), `model_models` (261, two-valued models), `preferred_models` (269), `stable_models` (282, via `_stable_reduct`).
  - `classify_link` (291), `dung_to_adf` (310), `adf_to_dung` (325). I/O: `to_json`/`from_json`, `write_iccma_formula`/`parse_iccma_formula`.

### Bipolar / value-based / collective-attack / claim-augmented

- **`bipolar.py`** (375 lines, full reference impl). `BipolarArgumentationFramework`: `arguments`, `defeats`, `supports` (a *second* directed edge relation). `support_closure`, `cayrol_derived_defeats(defeats, supports)` — supported + indirect derived defeats to a fixpoint (line 106), `derived_set_defeats`, `set_defeats`/`set_supports`, `support_closed`. d/s/c-admissibility (`d_admissible`/`s_admissible`/`c_admissible`), `d_preferred_extensions`/`s_preferred_extensions`/`c_preferred_extensions`, `stable_extensions`, `bipolar_grounded_extension` (348), `bipolar_complete_extensions` (365).
- **`vaf.py`** + **`vaf_completion.py`**. Bench-Capon value-based AFs: audience-specific defeat removes attacks whose target value is preferred to attacker value; objective/subjective acceptance quantify over audience orders. `vaf_completion` adds argument-chain/audience helpers for fact-uncertainty completions.
- **`setaf.py`** + **`setaf_io.py`**. Collective-attack AFs (attacker is a *set*): conflict-free/admissible/complete/preferred/grounded/stable/semi-stable/stage. `setaf_io` = ASPARTIX fact I/O + compact parser/writer.
- **`caf.py`** (268 lines). Claim-augmented AFs: inherited + claim-level extension views + concurrence checker.
- **`practical_reasoning.py`** (242 lines). Atkinson/Bench-Capon AATS for AS1-style practical arguments + CQ5/CQ6/CQ11 objections. (Domain-specific; least relevant here.)

### Quantitative: ranking, gradual, weighted, DF-QuAD, equational, game-theoretic

- **`ranking.py`** (399 lines, full reference impl). `RankingResult` (`.scores`, `.ranking` = tuple of frozensets best-tier-first, `.converged`, `.iterations`, `.semantics`). `categoriser_scores`/`categoriser_ranking` (38/88), `burden_numbers`/`burden_ranking` (101/138), `discussion_based_ranking` (147), `counting_ranking` (184), `tuples_ranking` (227), `h_categoriser_ranking` (259), `iterated_graded_ranking` (299). **`h_categoriser_ranking` is the h-categorizer the task asked about.**
- **`gradual.py`** (474 lines). Potyka quadratic-energy strengths for weighted bipolar graphs; revised direct-impact attribution; exact Shapley-style per-attack impact (Al Anaissy et al. 2024 Def 13).
- **`weighted.py`**. Dunne-style weighted argument systems — enumerate attack subsets whose deleted weight fits an inconsistency budget.
- **`dfquad.py`** (243 lines). DF-QuAD aggregation/combination + strength propagation.
- **`equational.py`**. Gabbay iterative equational fixpoint scoring schemes.
- **`matt_toni.py`** (233 lines). Finite zero-sum game strengths; raises if game matrix too large for in-package solver.
- **`gradual_principles.py`** / **`ranking_axioms.py`** (443 lines). Executable principle/axiom checkers (balance, directionality, monotonicity, ranking preorder, void-precedence, cardinality-precedence).

### Probabilistic / epistemic

- **`probabilistic.py`** (1479 lines) + `probabilistic_components.py` + `probabilistic_treedecomp.py` (1663 lines). `ProbabilisticAF(framework, p_args, p_defeats)`; `compute_probabilistic_acceptance(praf, semantics=...)` dispatches across seven strategies: `deterministic`, `exact_enum`, `mc` (Monte Carlo, Agresti-Coull stopping), `exact_dp` (tree-decomp DP for credulous grounded), `paper_td` (Popescu-Wallner 2024), `dfquad_quad`, `dfquad_baf`. Query kinds: per-argument acceptance (default) or `query_kind="extension_probability"` with `queried_set=...`. `summarize_defeat_relations`.
- **`epistemic.py`** (842 lines). Epistemic graphs: positive/negative influences over belief levels, finite model enumeration, evidence updates, projection to constellation PrAFs. Z3-backed linear constraint sat/entailment with `[z3]` extra.

### Dynamics / revision / enforcement / approximation

- **`partial_af.py`** (424 lines). `PartialArgumentationFramework`: pairs over A×A partitioned into `attacks` / `ignorance` / `non_attacks`; reasoning by enumerating *completions*. Merge aggregations `sum_merge_frameworks` / `max_merge_frameworks` / `leximax_merge_frameworks`; `consensual_expand`.
- **`af_revision.py`** (401 lines). `AFChangeKind` StrEnum (`DECISIVE | RESTRICTIVE | QUESTIONING | DESTRUCTIVE | EXPANSIVE | CONSERVATIVE | ALTERING`), `AFKernelSemantics` StrEnum. `baumann_2015_kernel_union_expand(base, incoming)` (175), `stable_kernel(framework)` (195), `baumann_2015_kernel(framework, semantics)` (206), `diller_2015_revise_by_formula` (274), `diller_2015_revise_by_framework` (292), `cayrol_2014_classify_grounded_argument_addition(framework, argument, attacks)` (314). `ExtensionRevisionState` / `ExtensionRevisionResult` for extension-level revision.
- **`dynamic.py`** (531 lines). `DynamicArgumentationFramework` (recompute-from-scratch wrapper, line 78), `IncrementalDynamicArgumentationFramework` (413), `DynamicUpdate`, update streams: `parse_update_stream` / `apply_update_stream`; `incremental_extension_update` (329), `influenced_arguments` (244), `reduced_framework` (285); credulous/skeptical queries after each transition.
- **`enforcement.py`** (681 lines). Brute-force minimal-change oracle. `AFEdit`, `EnforcementResult` (typed witness edits + edited framework + resulting extensions), `Expansion`/`ExpansionEnforcementResult`. `enforce_credulous(framework, argument, *, semantics="preferred", max_cost=2)` (432) — "minimally edit defeats so `argument` appears in *some* extension"; `enforce_skeptical(...)` (451) — "...in *every* extension"; `enforce_extension(framework, target, *, semantics, ...)` (471); plus expansion-constrained variants `enforce_expansion_credulous/skeptical/extension` (501–552) and `enforce_liberal_expansion_*` (592–649); expansion-shape predicates `is_normal_expansion`/`is_strong_expansion`/`is_weak_expansion`.
- **`approximate.py`**. k-stable semantics, bounded grounded iteration, budgeted semi-stable approximation, with exactness metadata.

### Encoding / interop / solver surfaces

- **`iccma.py`** (379 lines) + **`iccma_cli.py`** (327 lines). `parse_af`/`write_af`, ICCMA-style AF/ADF/ABA exchange. `iccma-cli` console script (problem codes `SE`/`DC`/`DS`; semantics `CO/GR/PR/ST/SST/STG/ID/CF2`; backends `auto/native/sat`).
- **`sat_encoding.py`**. Pure-Python CNF encoding of stable-extension semantics (one Boolean var per argument), solver-independent.
- **`af_sat.py`** (1274 lines). Z3-backed incremental SAT kernel for Dung AFs with telemetry (`SATCheck`, `SATTraceSink`, `AfSatKernel`) — `[z3]` extra.
- **`datalog_grounding.py`** (392 lines). `ground_defeasible_theory(theory) -> GroundedDatalogTheory` — grounds a Gunray `DefeasibleTheory` into propositional ASPIC+. Requires `[grounding]` extra (pulls `gunray` from git). Solver/sister-project boundary.
- **`llm_surface.py`**. Dependency-free QBAF adapter for argumentative LLM pipelines (Freedman et al. 2025): callers supply propositions + attack/support edges, get QBAF strengths + Shapley-style attack explanations + contestation witnesses.
- **`solver.py`** (1074 lines), `solver_results.py`, `solver_differential.py`, `backends.py`, `solver_adapters/` (`clingo.py`, `iccma_af.py`, `iccma_aba.py`). Typed solver tasks (`ExtensionEnumerationSuccess` / `SingleExtensionSuccess` / `AcceptanceSuccess`); `solve_dung_extensions`, `solve_dung_single_extension`, `solve_dung_acceptance`, `solve_aba_*`, `solve_adf_models`, `solve_setaf_extensions`; capability detection `has_clingo`/`has_z3`, `default_backend(...)`, `backend_choice_reason(...)`; typed unavailable returns (`SolverUnavailable`, `SolverProcessError`, `SolverProtocolError`); `solver_capability_matrix`. These are *adapters around external tools*, not algorithms.

**Reference-impl vs stub vs adapter, summary:**
- Full pure-Python reference implementations: `dung`, `labelling`, `preference`, `semantics`, `aspic`, `aspic_encoding`, `aspic_incomplete`, `subjective_aspic`, `accrual`, `aba`, `aba_sat`, `adf`, `bipolar`, `vaf`, `vaf_completion`, `setaf`, `setaf_io`, `caf`, `practical_reasoning`, `ranking`, `ranking_axioms`, `gradual`, `gradual_principles`, `weighted`, `dfquad`, `equational`, `matt_toni`, `probabilistic` (+ `_components`, `_treedecomp`), `epistemic` (core), `partial_af`, `af_revision`, `dynamic`, `enforcement`, `approximate`, `iccma`, `iccma_cli`, `sat_encoding`, `llm_surface`.
- Optional-dependency adapters (typed boundaries, not algorithms): `aba_asp` (clingo), `af_sat` (z3), `datalog_grounding` (gunray), `epistemic` z3 helpers, `aspic_encoding` clingo backend, `solver` + `solver_adapters/*`.
- No empty stubs spotted; smallest modules (`matt_toni` 233 ln, `practical_reasoning` 242 ln) are still substantive.

---

## 2. Data structures — how is an AF represented, and how close is it to "a digraph of words with definition edges"?

- **Dung AF (`dung.py:19`):** a frozen dataclass = `(arguments: frozenset[str], defeats: frozenset[tuple[str,str]], attacks: frozenset[tuple[str,str]] | None)`. That is literally *a set of string-id nodes plus a set of directed edges* (plus an optional second edge layer). Nodes are opaque string ids. **This is the same data structure as the dictionary project's definition digraph** — words as node ids, definition references as directed edges. The difference is purely semantic: in the AF an edge `(a,b)` means "a attacks/defeats b"; in the dictionary graph an edge `(w,v)` means "v appears in the definition of w" (or the reverse, depending on the build). Mapping one onto the other is a relabeling, not a restructuring.
- **Bipolar AF (`bipolar.py:16`):** adds `supports: frozenset[tuple[str,str]]` — a *second* directed-edge relation over the same node set. So bipolar AFs natively model two-edge-type digraphs.
- **SETAF (`setaf.py`):** attacker side of an edge is a *set* of arguments (collective attack) — i.e. a directed hypergraph on the attacker side.
- **ADF (`adf.py:161`):** `AbstractDialecticalFramework` = a set of statements, each with an **acceptance condition** that is a typed boolean-formula AST (`adf.py:37–161`: `Atom`, `True_`, `False_`, `Not`, `And`, `Or`) over other statement names. So the "edge" structure is implicit in which atoms appear in which acceptance condition, and the *kind* of dependency (positive/negative/dependent/redundant link) is recovered by `classify_link` (`adf.py:291`). This is the most expressive representation: it can encode "statement w is accepted iff (some boolean combination of) the statements appearing in w's definition are accepted."
- All of these use opaque `str` node ids, frozensets, structural equality, no global state — trivial to populate from an existing networkx-style digraph.
- **Caveat:** there is no built-in graph-algorithm toolbox (no FVS, no general SCC API, no cycle enumeration exposed publicly). The only SCC code is the private `_strongly_connected_components` in `dung.py:374`, used internally for cf2/stage2. Anything graph-theoretic (FVS, cycle ecology) the dictionary project already does itself in `graph_analysis.py` / `loop_analysis.py`.

---

## 3. The cycle / multiplicity story

How the library handles attack cycles, mapped to the things the task asked about:

- **Even-length cycles → multiple stable extensions.** Demonstrated in the README quick-start: a 4-cycle `a→b→c→d→a` yields `preferred_extensions(af) == [{a,c}, {b,d}]` and `stable_extensions(af) == [{a,c}, {b,d}]`. `stable_extensions` (`dung.py:271`) and `preferred_extensions` (`dung.py:255`) return a `list[frozenset[str]]` — *all* of them. So multiplicity-of-solutions is first-class output, not a single answer.
- **Odd cycles → no stable extension, grounded copes.** A 3-cycle has `stable_extensions(af) == []` (empty list — no stable extension) but `grounded_extension(af) == frozenset()` always exists. Grounded is the well-founded least fixpoint of the characteristic function (`characteristic_fn` `dung.py:127`, `grounded_extension` `dung.py:193`) — always defined, always unique, sceptical. Conceptually the same role as the dictionary project's "the part that's forced regardless of which cycle-break you choose."
- **Grounded = skeptical, unique:** `grounded_extension(af) -> frozenset[str]` (`dung.py:193`). Also `ideal_extension` (`dung.py:645`) and `eager_extension` (`dung.py:348`) as other unique sceptical-ish points; `accepted_arguments(af, semantics="preferred", mode="skeptical")` (`semantics.py:144`) gives sceptical acceptance = intersection over all preferred extensions.
- **Enforcement ("minimal change to make argument X accepted"):** `enforcement.py`. `enforce_credulous(framework, argument, *, semantics="preferred", max_cost=2) -> EnforcementResult` (`enforcement.py:432`) — minimal defeat-edits so `argument` is in *some* extension; `enforce_skeptical(...)` (`enforcement.py:451`) — in *every* extension; `enforce_extension(framework, target, *, semantics, ...)` (`enforcement.py:471`) — make a whole set be an extension. Returns typed `AFEdit` witnesses + edited framework + resulting extensions (`EnforcementResult` `enforcement.py:75`). Expansion-constrained variants (`enforce_expansion_*`, `enforce_liberal_expansion_*`) restrict the edits to normal/strong/weak expansions. **Brute-force oracle** — exact, not scalable, `max_cost` bounded.
- **AF revision:** `af_revision.py`. `baumann_2015_kernel_union_expand(base, incoming)` (line 175), `baumann_2015_kernel(framework, semantics)` (206) and `stable_kernel(framework)` (195) — compute the *kernel* of an AF (the redundancy-reduced attack relation that's update/deletion-equivalent — Baumann 2015; note "kernel" here is AF-revision jargon, **not** the Vincent-Lamarre "grounding kernel"); `diller_2015_revise_by_formula` / `diller_2015_revise_by_framework` (274/292) — extension-based belief revision preserving AGM-style postulates; `cayrol_2014_classify_grounded_argument_addition(framework, argument, attacks) -> AFChangeKind` (314) — classify the qualitative effect of adding one argument (`DECISIVE | RESTRICTIVE | QUESTIONING | DESTRUCTIVE | EXPANSIVE | CONSERVATIVE | ALTERING`).
- **Dynamics:** `dynamic.py`. `DynamicArgumentationFramework` / `IncrementalDynamicArgumentationFramework`, `incremental_extension_update`, `influenced_arguments`, `reduced_framework`, `apply_update_stream` — recompute (or incrementally update) extensions across a stream of argument/attack add/remove updates.
- **cf2 / stage2 and SCC-recursive semantics:** `cf2_extensions` (`dung.py:496`), `stage2_extensions` (`dung.py:512`) explicitly decompose the graph by SCC and recurse — these are the semantics that take cycle structure most seriously. `naive_extensions` (`dung.py:441`) = maximal conflict-free sets.

---

## 4. Existing lexical / semantic contact — essentially none

Grepped `notes/`, `papers/`, `docs/`, `reports/`, `workstreams/`, `CITATIONS.md` (case-insensitive) for: `dictionary`, `lexico*`, `wordnet`, `word meaning`, `symbol grounding`, `harnad`, `definition graph`, `feedback vertex`, `vincent-lamarre`, `massé 2008`, `picard 2013`.

**Result: zero substantive hits.** The only matches are for the substring `lexico` inside `lexicographic` / `lexicographically` / `leximax`, all referring to lexicographic *orderings* in ranking-based semantics and merge operators — e.g.:
- `papers/Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/notes.md` — "lexicographic comparison of burden numbers", "discussions of odd length are won (count negatively), even length are lost (count positively)" — note this is about *argument-chain* discussion lengths, not definitional cycles.
- `papers/Bonzon_2016_ComparativeStudyRanking-basedSemantics/notes.md`, `papers/Coste-Marquis_2007_MergingDung'sArgumentationSystems/notes.md` ("Leximax"), `papers/Dunne_2011_WeightedArgumentSystemsBasic/notes.md` ("lexicographic-minimum SAT"), `papers/Gabbay_2012_...`, `reports/encoding-preconditions.md`, `reports/workstream-datalog-grounding.md`.

No WordNet, no Harnad, no dictionary, no feedback-vertex-set, no Massé/Picard/Vincent-Lamarre, no symbol grounding anywhere in the corpus. The `papers/` directory (~60 subdirs, each with `notes.md`/`abstract.md`/`citations.md`) is entirely formal-argumentation literature (Dung, Caminada, Amgoud, Cayrol, Brewka, Bench-Capon, Baumann, Dunne, etc.). **There is no prior contact between this library and the dictionary-grounding problem.** That's expected; stating it for the record.

---

## 5. How to depend on it

- **Distribution name:** `formal-argumentation`. **Import name:** `argumentation`. Version `0.2.0`. `Development Status :: 3 - Alpha`.
- **Python:** `requires-python = ">=3.11"` (classifiers list 3.11/3.12/3.13).
- **Core has zero runtime dependencies** (`dependencies = []` in `pyproject.toml`).
- **Optional extras:** `[z3]` (`z3-solver>=4.12`) — unlocks `epistemic` constraint sat + `af_sat` SAT backend; `[asp]` (`clingo>=5.7`) — clingo-backed ABA + ASP backends; `[grounding]` (`gunray`, sourced from `git+https://github.com/ctoth/gunray.git` per `[tool.uv.sources]`, **not on PyPI**) — datalog grounding of defeasible theories.
- **README's stated install:** `uv add formal-argumentation` (and `uv add "formal-argumentation[z3]"` etc.). README also says PyPI distribution name is `formal-argumentation`; the task brief expected a `git+https` story — the actual `pyproject.toml` URLs point at `https://github.com/ctoth/argumentation`, and the only git-sourced thing is the optional `gunray` dep. So: depend on it either from PyPI as `formal-argumentation` or from the git repo directly (`git+https://github.com/ctoth/argumentation`). Build backend is `hatchling`; wheel packages `src/argumentation` and force-includes `src/argumentation/encodings` (prebuilt clingo `.lp` files).
- Console script: `iccma-cli` → `argumentation.iccma_cli:main`.
- Dev: `uv sync`, `uv run pyright src`, `uv run pytest -vv`. Tests tagged `unit` / `property` (Hypothesis) / `differential`.

---

## Raw observations only

- **Bigger than expected.** ~20.5k lines, 51 modules, ~60 cited papers each with a notes/abstract/citations triad. This is a serious reference library, not a toy. The biggest single module is `aspic.py` at 1394 lines; `probabilistic_treedecomp.py` (1663) and `probabilistic.py` (1479) are also large.
- **The core data structure is startlingly generic** — `ArgumentationFramework` is just `(frozenset[str] nodes, frozenset[tuple[str,str]] edges)`. Nothing about it is argumentation-specific until you call a semantics function. It will ingest any string-keyed digraph as-is.
- **No graph-theory toolbox.** I expected at least an SCC API and maybe cycle enumeration. There's exactly one private Tarjan (`dung.py:374`) used for cf2/stage2, and `preference.strict_partial_order_closure` which detects cycles only to *reject* them. No public SCC, no FVS, no cycle enumeration, no condensation. The dictionary project's `graph_analysis.py`/`loop_analysis.py` would not be subsumed by depending on this library.
- **"Kernel" is an overloaded word here.** `af_revision.stable_kernel` / `baumann_2015_kernel` compute the *minimal update-equivalent attack relation* (Baumann 2015) — a completely different notion from the Vincent-Lamarre "grounding kernel" (recursively-irreducible subgraph) the meanings project uses. Anyone bridging the projects must not conflate them.
- **The closest conceptual analogues to the dictionary problem are:** (a) grounded extension = the forced-regardless-of-choices core (≈ what survives every cycle-break); (b) the set of *all* stable/preferred extensions = multiplicity of valid choices (≈ multiple MinSets); (c) enforcement = minimal edits to force a target node's status; (d) ADF acceptance-condition ASTs = a way to encode "node accepted iff boolean combination of its definitional neighbours accepted." But the edge semantics are inverted relative to attack: definition edges are more like *support* than *attack*, so the bipolar/ADF side is the more natural fit than plain Dung.
- **Surprising gap:** no incomplete/uncertain-*argument* support beyond `partial_af` (uncertain *attacks*) and `aspic_incomplete` (uncertain *premises*). Argument-set uncertainty is not modelled. Probably irrelevant to the dictionary use case.
- **No `workstreams/` or `notes/` entry references anything outside formal argumentation.** The repo is hermetic to its own domain. Cross-pollination with `meanings` would be net-new.
- **Did not run anything** — pure source survey, no test execution, no install. The repo has a `.venv/` and `.pytest_cache/` so it's been built and tested locally before; I left it untouched.

---

### Bottom line for the dictionary problem

The single most directly relevant capability: **`enforcement.py` — minimal-change enforcement** (`enforce_credulous` / `enforce_skeptical` / `enforce_extension`, lines 432/451/471), backed by `dung.py`'s full set of *all*-extensions enumerators. It is the closest off-the-shelf machinery to "what is the minimal set of words I must externally ground (edit the graph at) so that target word X becomes accepted/reachable" and "enumerate every minimal valid grounding choice." Caveat: it's a brute-force oracle (`max_cost`-bounded, exponential), and the edge semantics (attack vs. definition-reference) would need a deliberate translation — the bipolar/ADF representations are the more honest target than plain Dung. Whether any of this *should* be used is the next agent's call; structurally, the AF object and the definition digraph are the same shape.
