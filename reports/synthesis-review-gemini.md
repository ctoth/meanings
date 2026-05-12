# Synthesis review — Gemini (adversarial; angle: "the argumentation reframing is a relabeling, not a result")

*(Salvaged from `gemini-review.log` — Gemini wrote the review to stdout but didn't execute the file write. Content verbatim; provenance: `gemini --yolo` run `bqmrb4qqj`, 2026-05-12.)*

The argumentation-framework (AF) reframing presented in the synthesis is currently a **high-fidelity relabeling** of existing graph-theoretic results, not a new mathematical result. While it provides a sophisticated conceptual "type system" for the project's next phase, its claims of "theorems" are largely identities, and its primary hypothesis — that stable extension multiplicity explains MinSet non-uniqueness — has collapsed upon contact with real data.

## 1. The strongest version of the charge

The project has constructed an elaborate "terminological shell game." By mapping 1960s graph theory (SCCs) and 2008 dictionary-grounding theorems (Massé's FVS) onto 1995 formal argumentation (Dung's AF), the synthesis creates an illusion of a "new result" where there is only a translation dictionary. The "scaling result" is an engineering win for caching, but it serves to compute a "grounded extension" that the synthesis itself admits is "deflationary" and a "stable semantics" that returns a null result (UNSAT).

## 2. Specific findings

### (a) The "theorems" are identities, not insights
"MinSet = a minimal-enforcement set" and "FVS = an FPT backdoor parameter" are presented as theorem-level facts in the math facet. In reality: Massé (2008) already proved that a minimal set of nodes needed to make a definition graph well-founded is a minimum feedback vertex set — identifying this as an "enforcement set" for "skeptical determinacy" adds a syllable but no new math; it's a restatement of the definition of an FVS in the context of an acyclic AF. And the FPT result (Dvořák et al.) is a known property of AFs with small backdoors; since the dictionary graph's FVS is already the object of study, noting that it's *also* the FPT parameter is a trivial observation, not a discovery.

### (b) The triviality of the bipolar/ADF framing
On the current `lemma::pos` graph, "the definition digraph *is* an ADF/bipolar AF" is trivial to the point of vacuity: the "support" reading has an *empty* defeat relation (`src/meanings/argumentation_bridge.py:66`); the bridge report admits that because defeats are empty, the bipolar grounded extension is "trivially the whole argument set"; so the grounded operator for bipolar AFs is just the identity on this graph. The real work of cycle-breaking is still done by `compute_kernel` (leaf-stripping) and `solve_minset` (FVS heuristics), not by the argumentation semantics.

### (c) The mnemonic mapping (Kernel-vs-loop)
"Foundationalism vs coherentism = grounded vs preferred" is a powerful mnemonic but lacks computational teeth right now. Grounded semantics on the attack reading is a 0.8s labelling pass that identifies an "acyclic-from-outside fringe"; the synthesis shows no result where preferred semantics (the coherentist view) provides a ranking or word set that the original "loop ecology" analysis hadn't already identified.

### (d) The collapse of the stable-extension story
The synthesis originally hypothesized "many MinSets = many stable extensions." The dispatcher report refutes it: the OEWN Kernel AF has **zero stable extensions** (UNSAT in 8s); the dispatcher's structural MinSet count is `0`. The story of stable-extension multiplicity as an explanation for grounding choice has evaporated. "This isn't embarrassing" is a salvage; in fact, for `oewn:2024`, stable semantics is a useless tool.

### (e) Scaling claims: an over-claim?
"Argumentation can't scale is retired in code" (§2) is an over-claim. What scaled: grounded semantics (polynomial/linear) and a SAT-check (z3) — the "easy" parts of the argumentation zoo. What didn't: the dispatcher doesn't even attempt preferred extensions for the 8,138-node giant core; preferred semantics (Π₂ᵖ-complete) remains un-scaled. The 99.6% isomorphism-cache hit rate is a brilliant optimization for the thousands of tiny satellite SCCs but doesn't solve the hard semantics of the core.

## 3. Where the reframing earns its keep

The reframing genuinely contributes when it moves from the `lemma::pos` graph to the **sense-level graph**: at the sense level rival senses of a form *do* attack each other — net-new content the graph-only FVS approach cannot represent. And the `form → reading → sense → IC` pipeline turns "graph necessity" into a "defeasible admission policy"; using `gunray` to mark senses `UNDECIDED` is a legitimate formalization of Harnad's symbol-grounding problem that goes beyond bare connectivity.

## 4. Verdict

The argumentation-reframing material is a **useful framing** (a conceptual architecture for the sense-level rebuild) but, as currently applied to the OEWN `lemma::pos` graph, it is a **relabeling**. The scaling "result" is essentially "we can run grounded (because we fixed a bug) and z3 (because the graph is sparse)." The mathematical "result" is essentially "Massé (2008) is still true if you use Dung's vocabulary." The reframing earns its stay only if the sense-level rebuild successfully uses non-empty attack relations to solve the Nobelium-artifact problem, which the original graph-only Kernel analysis could not.
