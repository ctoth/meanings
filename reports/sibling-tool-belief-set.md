# Sibling tool inventory: `belief-set`

Scout survey of `C:\Users\Q\code\belief-set` — a pure-Python, finite-world propositional belief-revision library. Surveyed with the lens: *can belief-revision machinery be applied to the dictionary/kernel problem in `C:\Users\Q\code\meanings`?*

All claims cite file + line. Repo not modified.

---

## 1. What's implemented

The whole library is 8 source files under `belief_set/`, ~700 lines total. Everything is finite and extensional: a belief set IS its set of satisfying worlds; operators enumerate up to `2^n` worlds.

### Public API (`belief_set/__init__.py:1-51`)
Exports: `AlphabetBudgetExceeded`, `BOTTOM`, `TOP`, `Atom`, `BeliefSet`, `EnumerationExceeded`, `EpistemicEntrenchment`, `Formula`, `ICMergeOperator`, `ICMergeOutcome`, `ICMergeProfileMemberInconsistent`, `RevisionOutcome`, `RevisionTrace`, `SpohnEpistemicState`, `World`, `conjunction`, `disjunction`, `equivalent`, `expand`, `full_meet_contract`, `lexicographic_revise`, `merge_belief_profile`, `negate`, `restrained_revise`, `revise`, `theory_subset`.

### AGM revision (`belief_set/agm.py`)
- `revise(state: SpohnEpistemicState, formula: Formula, *, max_alphabet_size=16) -> RevisionOutcome` (`agm.py:103-144`). Comment says "Darwiche-Pearl 1997 bullet revision over a Spohn ranking." Mechanics: extend state to combined signature, find min rank among `formula`-worlds, subtract that from formula-worlds, add 1 to the rest, renormalize. Returns `RevisionOutcome(belief_set, state, trace)`.
- `RevisionOutcome` (`agm.py:24-29`): dataclass `{belief_set: BeliefSet, state: SpohnEpistemicState, trace: RevisionTrace}`.
- `RevisionTrace` (`agm.py:17-22`): `{operator: str, pre_image_fingerprint: str, timestamp}` — `timestamp` is `datetime.now(utc)`, marked `compare=False`.

### Contraction (`belief_set/agm.py`)
- `full_meet_contract(state, formula, *, max_alphabet_size=16) -> RevisionOutcome` (`agm.py:147-177`). Docstring: "AGM contraction using the Harper identity over the finite theory." Implemented as Harper: revise by `negate(formula)`, intersect the result's theory with the original (`agm.py:163-168`), and take pairwise-min ranks. Also exported as `full_meet_contract` from `__init__`.
- **No partial-meet, no safe/Hansson "kernel" contraction, no maxichoice.** Only full-meet contraction exists. Note for the dictionary question: *"kernel contraction" in the AGM/Hansson sense (contraction via minimal `A`-implying subsets — "kernels") is NOT implemented* and the word "kernel" never appears in the source. `papers/Hansson_1989_NewOperatorsTheoryChange/` and `papers/Alchourron_1985_TheoryChange/` are present as paper notes but their operators (safe/kernel contraction, partial meet) are not coded.

### Expansion (`belief_set/core.py`)
- `expand(belief_set: BeliefSet, formula: Formula) -> BeliefSet` (`core.py:119-120`) = `belief_set.conjunction_with_formula(formula)` (`core.py:91-97`). Simple model intersection. No Spohn-state version.

### Levi / Harper identities
- Harper identity is what `full_meet_contract` uses internally (`agm.py:163-168`, docstring `agm.py:153`).
- **No Levi identity function** — there is no `contract`-then-`expand` revision constructor exposed; `revise` is implemented directly via Spohn conditioning, not via Levi. So the two identities are not both available as composable operators; only Harper-style contraction-from-revision exists.

### Epistemic entrenchment (`belief_set/entrenchment.py`)
- `EpistemicEntrenchment` dataclass wrapping a `SpohnEpistemicState` (`entrenchment.py:11-19`). Docstring: "Gärdenfors-Makinson style entrenchment induced by a Spohn ranking."
- `EpistemicEntrenchment.from_state(state) -> EpistemicEntrenchment` (`entrenchment.py:17-19`).
- `EpistemicEntrenchment.leq(left: Formula, right: Formula, *, max_alphabet_size=16) -> bool` (`entrenchment.py:21-35`): returns `_negation_rank(left) <= _negation_rank(right)` — i.e. `left` is no more entrenched than `right`.
- `_negation_rank(formula)` (`entrenchment.py:37-55`): minimum Spohn rank among worlds satisfying `negate(formula)`; `inf` if no countermodels (so a tautology is maximally entrenched). This is the "min rank of countermodels" definition — exactly the entrenchment ↔ OCF correspondence (Spohn).
- It's a **predicate (`leq`) only** — there's no method that returns a total order / sorted list of formulas by entrenchment, and no method that ranks members of a set by entrenchment. You'd build that yourself by calling `leq` pairwise or `_negation_rank` per formula.

### Spohn ranking states / OCFs (`belief_set/agm.py:31-100`)
- `SpohnEpistemicState` (`agm.py:31-66`): frozen dataclass `{alphabet: frozenset[str], ranks: Mapping[World, int|float]}`. `__post_init__` validates that ranks cover *every* world over the alphabet, rejects NaN and negatives (`agm.py:201-207`), normalizes so the minimum *finite* rank is 0 (`agm.py:51-66`, `_normalize_rank` `agm.py:191-198`), and represents a contradiction as all-`inf` ranks.
- `SpohnEpistemicState.from_ranks(alphabet, ranks)` (`agm.py:68-74`).
- `SpohnEpistemicState.from_belief_set(belief_set)` (`agm.py:76-90`): models get rank 0, non-models rank 1; empty model set → all `inf`.
- `.belief_set` property (`agm.py:92-100`): the worlds at minimum rank = the believed set.
- `extend_state(state, alphabet)` (`agm.py:180-188`): lift an OCF to a larger signature (each new atom doubles the world set, ranks copied).
- This IS an ordinal conditional function: integer (or `inf`) plausibility grades over all `2^n` worlds.

### Iterated revision (`belief_set/iterated.py`)
- `lexicographic_revise(state, formula, *, max_alphabet_size=16) -> RevisionOutcome` (`iterated.py:17-46`). Docstring: "Nayak-Spohn lexicographic revision." All formula-worlds ranked below all non-formula-worlds, old order preserved within each group; `_dense_ranks` re-compresses (`iterated.py:95-100`).
- `restrained_revise(state, formula, *, max_alphabet_size=16) -> RevisionOutcome` (`iterated.py:49-92`). Docstring cites "Booth and Meyer, JAIR 26 (2006), Definition 4 (RR)."
- **Darwiche-Pearl is the base `revise` in `agm.py`** (DP bullet revision). **No Jeffrey conditioning, no Boutilier natural revision, no Spohn `c`-revisions / `(α, n)` conditionalization as separate entry points.** The README "Correctness Coverage" section names Booth-Meyer and Nayak-Spohn as the iterated families covered.

### IC belief merging (`belief_set/ic_merge.py`)
- `merge_belief_profile(alphabet, profile: tuple[Formula,...], mu: Formula, *, operator=ICMergeOperator.SIGMA, max_alphabet_size=16) -> ICMergeOutcome` (`ic_merge.py:43-79`). Docstring: "Konieczny-Pino Pérez style finite model-theoretic IC merge." Scores each `mu`-world by Hamming distances to each profile member's model set, aggregates, returns the minimizers.
- `ICMergeOperator` StrEnum: `SIGMA` (sum of distances), `GMAX` (sorted-descending distance vector, compared lexicographically) (`ic_merge.py:14-16`, `82-92`).
- `ICMergeOutcome` (`ic_merge.py:30-34`): `{belief_set: BeliefSet, scored_worlds: tuple[tuple[World, tuple[float,...]],...]}`.
- `ICMergeProfileMemberInconsistent` raised if a profile member is unsatisfiable (`ic_merge.py:19-27`, `206-211`).
- Distance is Hamming over symmetric difference of world sets (`_hamming` `ic_merge.py:223-224`).

---

## 2. Data structures

- **World**: `World = frozenset[str]` (`language.py:7`) — the set of atoms true in that valuation. Documented mental model: "A world is a `frozenset[str]` containing exactly the atoms true in that world" (`README.md:62`).
- **Formula**: a `Protocol` with `evaluate(world) -> bool` and `atoms() -> frozenset[str]` (`language.py:10-13`). Concrete impls: `Atom`, `Top`/`TOP`, `Bottom`/`BOTTOM`, `Not`, `And`, `Or` (`language.py:16-95`). Constructors `negate`, `conjunction`, `disjunction` do shallow simplification against the concrete dataclasses (`language.py:88-131`). No implication/iff/xor connective; no quantifiers; propositional only.
- **BeliefSet** (`core.py:11-105`): frozen dataclass `{alphabet: frozenset[str], models: frozenset[World]}`. Extensional — it stores the satisfying worlds directly. `all_worlds(alphabet)` enumerates the full `2^n` powerset (`core.py:31-38`). `cn()` returns `self` (closure already represented). Helpers: `entails`, `equivalent`, `with_alphabet`, `intersection_theory`, `conjunction_with_formula`, `fingerprint` (sha1 of sorted alphabet+models). `theory_subset(left, right)` (`core.py:113-116`): subset on entailed formulas = superset on models.
- **SpohnEpistemicState**: see §1 — a complete `World -> int|float` map.
- **Cost model**: explicitly `O(2^n)` in the size of the alphabet. README: "Given an alphabet of `n` atoms, many operations enumerate up to `2^n` worlds. Treat alphabet size as the main cost driver" (`README.md:9-12`). `architecture.md:21-24`: "suitable as a reference kernel for small finite signatures, not as a SAT/SMT-backed reasoner."
- **`max_alphabet_size`**: keyword arg on every public operator (`revise`, `full_meet_contract`, `lexicographic_revise`, `restrained_revise`, `EpistemicEntrenchment.leq`, `merge_belief_profile`). Default `MAX_ALPHABET_SIZE = 16` (`agm.py:14`). `enforce_alphabet_budget` raises `AlphabetBudgetExceeded` if `len(signature) > max_alphabet_size` (`anytime.py:22-32`). With the default, that's up to 65,536 worlds per operation. `EnumerationExceeded` (`anytime.py:6-9`) is a separate, internal "anytime scan interrupted" type used only in private `ic_merge` distance code; README and `notes/audit-2026-05-01.md` flag it as not a public approximation result.

---

## 3. The "graded foundational-ness" angle

What the library exposes that maps onto "how-foundational-is-this-word":

- **Epistemic entrenchment** = a *preorder predicate on formulas*: `EpistemicEntrenchment.leq(left, right)` (`entrenchment.py:21-35`). More entrenched = harder to give up = higher min-rank of countermodels. Induced entirely from a Spohn OCF. There is no constructor that hands you the total order or a ranked list — you call `leq` pairwise, or call the private `_negation_rank(formula)` (`entrenchment.py:37-55`) to get the numeric entrenchment degree of a single formula and sort yourself.
- **Spohn ranks / OCFs** = integer (or `inf`) plausibility grades over *worlds*, not formulas: `SpohnEpistemicState.ranks` (`agm.py:35`). Rank 0 = most plausible / believed; higher = more surprising. A formula's "disbelief degree" is `min{rank(w) : w ⊨ ¬formula}` — that is exactly what entrenchment computes, so **entrenchment and the OCF are two views of one object** (the entrenchment of `φ` = the OCF-rank of the most plausible `¬φ`-world).
- **Relation to contraction**: `full_meet_contract` (`agm.py:147-177`) gives up `formula` by mixing in the `¬formula`-revised ranks (pairwise min) — i.e. it specifically demotes nothing and *promotes* the best `¬formula` worlds to rank 0 alongside the old beliefs. Entrenchment is the AGM-classical handle on "which beliefs survive contraction"; here it's derived from the same OCF, not used to drive `full_meet_contract` directly (full-meet ignores entrenchment by definition — it's the least discriminating contraction).
- **"Rank the elements of a set by how resistant they are to retraction"**: not directly provided as a function. The raw material is there — for each candidate formula `φ` compute `_negation_rank(φ)` against a Spohn state and sort descending — but there's no packaged "entrenchment ranking of a set" call. This is the single most relevant gap to fill for the dictionary use case.

---

## 4. Existing lexical / semantic contact

**Essentially none.** Grepping `notes/`, `papers/`, `docs/`, `belief_set/` for `dictionary | wordnet | lexicon | "symbol ground" | "word meaning"` returned **zero matches** (`grep -rni` over those dirs, no output). The hits for `semantic` / `definition` are all the ordinary logician's senses — "sphere semantics," "model-theoretic semantics," "definition 4," etc. (e.g. `papers/Grove_1988_TwoModellingsTheoryChange/notes.md`, `papers/index.md`).

The `papers/` directory holds processed notes for the belief-revision canon only: Alchourrón-Gärdenfors-Makinson 1985, Gärdenfors 1988, Grove 1988, Hansson 1989, Spohn 1988, Konieczny-Pino Pérez 2002, Booth-Meyer 2006 (`papers/index.md`, dir listing). No Harnad, no Massé/Picard/Vincent-Lamarre, no lexical-graph literature. The two projects currently share no references and no vocabulary. `architecture.md` and `README.md` "Non-Goals" explicitly disclaim provenance graphs, argumentation adapters, and anything application-specific — so dictionary modeling would be a downstream consumer, not an in-package concern.

---

## 5. How to depend on it

- **Distribution / package name**: `formal-belief-set` (`pyproject.toml:2`), version `0.1.0`, `requires-python = ">=3.11"`, **zero runtime dependencies** (`pyproject.toml:5`). Build backend hatchling; wheel ships only the `belief_set` package (`pyproject.toml:12-13`). No declared license yet (README `belief-set/README.md:13`).
- **Import name**: `belief_set` (underscore), e.g. `from belief_set import Atom, BeliefSet, SpohnEpistemicState, revise` (`README.md:37`, `belief_set/__init__.py`).
- **Dependency line** (`belief-set/README.md:17-21`): `uv add "formal-belief-set @ git+https://github.com/ctoth/belief-set@<commit>"`. The README explicitly forbids pinning to a local checkout / editable path. This matches the `meanings` README's stated form `formal-belief-set @ git+https://github.com/ctoth/belief-set@<commit>`. Confirmed: package name `formal-belief-set`, import `belief_set`, Python ≥3.11.
- Dev: `uv sync; uv run pytest` (`property` marker for the slow exponential property tests); `uv run pyright` (basic mode). Test files live under `tests/` (~20 files) plus `tests/remediation/`.

---

## Raw observations only

- **Tiny.** ~700 lines of source across 8 files. "small pure-Python package for finite propositional belief-revision kernels" (`README.md:3`) is accurate to the point of understatement. The `papers/` tree (paper notes + page PNGs, ~7 papers) is larger than the code.
- **"Kernel" is a red herring here.** The library is described as "belief-revision *kernels*" (in the sense of small reusable cores), and the `meanings` project is about lexical *kernels* (in the feedback-vertex-set sense), but neither matches AGM "kernel contraction" — and **AGM kernel contraction is not implemented at all**. The word "kernel" appears nowhere in `belief_set/*.py`.
- **Only full-meet contraction.** No partial-meet, no maxichoice, no safe/kernel contraction, no recovery-respecting contraction. For "minimal grounding set"-flavored intuitions you'd be building on top, not reusing.
- **The OCF / entrenchment duality is the usable bit.** A `SpohnEpistemicState` is a graded plausibility ranking over all `2^n` worlds; entrenchment of a formula falls out as the min rank of its countermodels (`entrenchment.py:37-55`). If you encode "word `w` is in the grounding set" as atoms, an OCF over those atoms gives you a graded foundational-ness measure, and `EpistemicEntrenchment.leq` gives you the comparison — but you must construct the OCF yourself; the library never *learns* or *infers* one, it only transforms ones you give it (`from_belief_set` only does the trivial 0/1 ranking).
- **`max_alphabet_size=16` is a hard ceiling that kills any realistic dictionary.** 65k worlds max with the default; even raised, `2^n` enumeration means this can model at most ~20-25 atoms before it's hopeless. A dictionary has ~10^4–10^5 words. This library cannot represent a dictionary's worth of propositions directly — any application would have to work on tiny sub-vocabularies (a single cycle, a handful of seed candidates) at a time.
- **Known bugs are documented in-repo.** `notes/audit-2026-05-01.md` and `notes/package-review.md` (both dated 2026-05-01) list real defects: inconsistent belief set silently becomes a tautology (`from_belief_set` on empty models → all ranks 1 → normalized to 0 → "believes everything"); `revise`/`full_meet_contract` on an inconsistent state produce `inf - inf = NaN` ranks that slip past validation; `full_meet_contract` `KeyError`s when the contracted formula introduces a new atom (`agm.py:163-172` enumerates old-alphabet worlds but indexes the extended state); module-global LRU distance cache in `ic_merge`; partial public-API export; non-deterministic `RevisionTrace` equality. Status line: "audit complete, no fixes requested." Treat the library as experimental-with-known-holes.
- **No diachrony / edition machinery.** Nothing about sequences of revisions over time beyond the two iterated-revision operators (`lexicographic_revise`, `restrained_revise`), and those operate on one OCF + one input formula, not on a series of dictionary states. "Dictionary edition N → edition N+1 as belief revision" would be: model each edition's definition-facts as formulas, apply `revise` iteratively — conceptually clean, but bounded by the `2^n` ceiling above.
- **Single most relevant capability for the dictionary problem**: `SpohnEpistemicState` (`agm.py:31-100`) + `EpistemicEntrenchment` (`entrenchment.py`) — a graded ordinal plausibility ranking over worlds, from which "how entrenched / how foundational is this formula" is computable as the min rank of its countermodels. That is the closest thing to "spectral how-foundational-is-this-word scoring as a graded kernel measure." Everything else (revision/contraction/merge) is downstream of having such a ranking, and the library does not build one for you.

---

**Report path**: `C:\Users\Q\code\meanings\reports\sibling-tool-belief-set.md`
