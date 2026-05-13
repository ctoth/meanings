# The sense-level rival-sense attack layer, and the bipolar-AF / ADF semantics over it

**Date:** 2026-05-12
**Agenda:** synthesis §6 #3 — "the bipolar-AF/ADF demonstrator over the sense-level graph, with the attack layer added first." Tests whether the argumentation reframing, which Gemini's review (`reports/synthesis-review-gemini.md`) charged is "a relabeling, not a result" on the `lemma::pos` graph, *earns its keep* at the sense level: does the rival-sense attack layer make stable-extension multiplicity real, give `enforce_skeptical` a non-trivial answer, or make a ranking semantics non-degenerate?
**Reproducer:** `scripts/sense_level_argumentation.py` → `reports/sense-level-argumentation.json`. New code: `meanings.wordnet_pipeline.{SenseLevelGraphWithAttacks, add_rival_sense_attacks, build_sense_level_paper_wordnet_graph_with_attacks}`, `meanings.argumentation_bridge.{bipolar_with_attacks_framework, derived_dung_framework}`, `tests/test_sense_attack_layer.py` (6 tests; full suite 66 passed). `argumentation` semantics: `dung`, `bipolar` (Cayrol derived defeats), `af_sat` (z3 stable), `enforcement`, `ranking`.

---

## 0. TL;DR — verdict (ii), with one honest qualification

**The attack layer does *not* rebut the relabeling charge in the way that would have mattered.** Specifically:

1. **Stable-extension multiplicity becomes technically true but vacuous.** The sense-Kernel-with-attacks AF is *SAT for stable* (z3, 1.7 s) — a change from the lemma-Kernel AF, which was UNSAT. But the reason is trivial: the rival-sense attack relation is a *disjoint union of cliques* (a form's senses attack each other and nothing else), so the attacks-only Kernel AF always has stable extensions, and their count is the product of clique sizes (log₁₀ ≈ 1,889 over the Kernel; ≈ 52,931 over the whole sense graph). This is multiplicativity, and it is "many stable extensions," but it is *not* "many MinSets = many stable extensions": the lexicon's support wiring plays no role in it; choosing a reading for `bank` is independent of choosing one for `crane`; there is no grounding-set structure here. The non-vacuous version — where the support graph *couples* the rival cliques (Cayrol-derived defeats, "Model B") — is **computationally infeasible at Kernel scale** (the derived-defeat closure on the 12,142-node Kernel blew past 9 GB RSS without terminating, because an attacker on any node of the Kernel's giant support SCC ends up attacking everything that SCC reaches → a near-complete defeat relation) and only appears in tiny SCCs where rival senses happen to co-occur — of which there are 269 in the whole Kernel, almost all degenerate near-complete-conflict gadgets.

2. **`enforce_skeptical` returns nothing MinSet-shaped.** On the trivial (attack-free) Kernel SCCs every node is already skeptically accepted (cost 0); on the one slice SCC with internal rival attacks (`cucumber`/`cucurbita`/`melon`/…) `enforce_skeptical` *fails* — "no skeptical preferred enforcement found within max_cost=2." It is a per-argument AF-edit query ("minimally edit defeats so argument X is in every preferred extension"), not a global grounding-set computation; it does not recover the MinSet and was never going to.

3. **The ranking semantics still collapses to degree on the bipolar graph.** h-categoriser on the sense Kernel: ρ(score, −in-degree) = **0.83** with support-edges-as-attacks (the sign-correct re-run of the lemma-level finding, now on the sense graph), and **0.78** when the rival-sense attacks are added on top; ρ between the two rankings = **0.81**. The rival attacks barely move it. The top-ranked words are still definitional *leaves* (`rhizomatous`, `wavelike`, `moist`, `waxed`, `pawn`-v) — the sign is still "wrong" for "foundational," exactly as at the lemma level (`reports/ranking-valuation-oewn.md`). The attack structure gives the ranking semantics nothing to chew on that degree didn't already encode.

**The honest qualification:** the attack layer *does* do one real thing — it puts genuine conflict exactly where polysemy lives (`break`-75, `cut`-70, `run`-57, `play`, `make`, `light`, `clear`, `draw`, `hold`, `set`, …; 41.6 % of all sense nodes are in a nontrivial rival clique), and on that conflict the bipolar/ADF semantics are no longer the identity function (Model B on small co-SCC slices has grounded ≠ everything, preferred-count > 1, z3-decided stable existence). So the reframing is *not* vacuous at the sense level the way it is at the lemma level. But its net-new computational content is: "a form's k senses give k stable readings" (vacuous multiplicativity), and "WSD inside a small definitional loop is a defeasible-reasoning gadget" (the `gunray`/UNDECIDED story, now with real attack edges). It does **not** deliver "stable-extension multiplicity explains MinSet non-uniqueness," and it does **not** give the FVS machinery anything it didn't have. **Verdict (ii): the relabeling charge essentially stands even at the sense level; the argumentation tools are a conceptual frame and a per-SCC-oracle architecture, not a computational lever on the dictionary-grounding problem.**

---

## 1. The attack layer

`add_rival_sense_attacks` (and `build_sense_level_paper_wordnet_graph_with_attacks`) take the sense-level support graph (`build_sense_level_paper_wordnet_graph` — 212,478 sense nodes, 418,094 `supports` edges) and add an undirected (stored symmetrically) `attacks` relation: two sense nodes attack each other iff they share a *form*. **Rivalry is computed per form across all parts of speech** — justification: the written shape `bank` is one form whatever the POS, and a reader meeting it must pick a reading from the whole rival set, not just the same-POS subset (a `per_pos=True` flag exists for the alternative). The existing builder is untouched; `SenseLevelGraphWithAttacks` is a new return type with `supports`, `attacks`, `rivalry_key_by_node`, `rivalry_cliques`.

| quantity | value |
|---|---|
| sense nodes | 212,478 |
| `supports` edges | 418,094 |
| `attacks` edges (ordered) | 415,210 |
| `attacks` pairs (unordered rivalry pairs) | 207,605 |
| rival-sense cliques (forms with ≥ 2 senses) | 27,589 |
| sense nodes in a nontrivial rival clique | 88,445 (**41.6 %** of all sense nodes) |
| largest clique | `break` — 75 senses |

**Rival-sense clique-size distribution** (forms-by-#senses): 16,217 forms with 2 senses, 5,230 with 3, 2,319 with 4, 1,250 with 5, 720 with 6, 514 with 7, 283 with 8, 219 with 9, … long tail … 1 each at 48 (`light`), 51 (`make`), 52 (`play`), 57 (`run`), 70 (`cut`), 75 (`break`). Top 15 by size: `break` 75, `cut` 70, `run` 57, `play` 52, `make` 51, `light` 48, `clear` 45, `draw` 45, `hold` 45, `set` 45, `fall` 44, `give` 44, `take` 44, `head` 42, `pass` 42 — the canonical heavy-polysemy English verbs. The attack layer concentrates conflict exactly where lexical polysemy is, which is the qualitatively right behaviour.

(Number of *ordered* attack edges per form-clique of size k is k(k−1); summed over all cliques = 415,210. The "Nobelium artifact" — `no::n` = the negation vs Nobelium — is now *structurally* a 2-clique attack, not a representative-synset coin-flip; whether the *right* sense survives is a job for a WSD/admission step this run does not implement.)

---

## 2. The bipolar AF / ADF over the sense graph

Two encodings (`meanings.argumentation_bridge`):
- `bipolar_with_attacks_framework(nodes, supports, attacks)` → `argumentation.bipolar.BipolarArgumentationFramework` with both supports and defeats. Unlike `bipolar_support_framework` (empty defeat relation → bipolar grounded semantics = identity, the lemma-level vacuity), this carries genuine conflict. But `argumentation.bipolar`'s own `stable_extensions` / `preferred_extensions` enumerate `2ⁿ` subsets — usable only on a tiny slice.
- `derived_dung_framework(nodes, supports, attacks)` → a plain `argumentation.dung.ArgumentationFramework` whose defeats are the **Cayrol & Lagasquie-Schiex (2005) derived-defeat closure** of (base attacks, supports): a base attack `w→u` plus a support chain `u→…→v` yields a *supported* defeat `w→v`; dually, support into the attacker yields *mediated/indirect* defeats; closure to a fixpoint. The result is a normal Dung AF, so the z3-backed `argumentation.af_sat` solvers and the `argumentation.dung` semantics apply.

### 2a. Small Kernel-SCC slice (Model B — Cayrol-derived)

Of the 7,466 Kernel SCCs, **724** contain a sense node that has a rival somewhere, but only **269** contain *internal* rival attacks (both rival senses in the same SCC) — the other 455 have a rival sense that sits outside the SCC, so the SCC's induced attack relation is empty. The slice (6 SCCs, ≤ 14 nodes, internal attacks preferred):

| SCC | members (sample) | support edges | attack edges (ordered) | derived Dung defeats | grounded | preferred (count / sizes) | stable exists / size | `enforce_skeptical` on 3 nodes |
|---|---|---|---|---|---|---|---|---|
| 11 | `cecum, colon, descending_colon, duodenum, ileum, jejunum, …` (gut anatomy) | 23 | **0** | 0 | 11 (all) | 1 / [11] | yes / 11 | cost 0 (already accepted) ×3 |
| 11 | `eighth, eleventh, fifth, fourth, ninth, seventh, …` (ordinals) | 20 | **0** | 0 | 11 | 1 / [11] | yes / 11 | cost 0 ×3 |
| 9 | `cucumber, cucurbita, cucurbitaceae, cucurbitaceous, melon, melon_vine, …` | 11 | **2** | **72** | **0** | **9 / [1,1,1,1,1,1,1,1,1]** | yes / 1 | **fails**: "no skeptical preferred enforcement within max_cost=2" ×3 |
| 8 | `absolution, baptism, confession, extreme_unction, matrimony, penance, …` (sacraments) | 16 | **0** | 0 | 8 | 1 / [8] | yes / 8 | cost 0 ×3 |
| 7 | `arm, carpal, elbow, elbow_joint, forearm, radius, …` (arm anatomy) | 10 | **0** | 0 | 7 | 1 / [7] | yes / 7 | cost 0 ×3 |
| 7 | `clause, complex_sentence, grammatical_constituent, main_clause, phrase, subject, …` (grammar) | 12 | **0** | 0 | 7 | 1 / [7] | yes / 7 | cost 0 ×3 |

Reading: in the *typical* small Kernel SCC the rival-sense attack relation is empty (rival senses of a form do not co-occur in a small definitional loop), so the bipolar/ADF semantics over the SCC are still trivial — grounded = the whole SCC, one preferred extension, stable = the whole SCC, every node already skeptically accepted. In the *one* SCC of the slice with internal attacks (the `cucumber`/`melon` cluster, where two senses of one form sit in the loop), the picture genuinely changes: the Cayrol closure explodes 2 base attacks into 72 derived defeats, the grounded extension empties out, there are **9 preferred extensions** (the multiplicity, all singletons — a near-complete conflict gadget), z3 finds a stable extension of size 1, and `enforce_skeptical` *cannot* make a chosen node skeptically accepted at edit-cost ≤ 2. This is what "the framing earns its keep at the sense level" amounts to concretely: the semantics stop being the identity on the SCCs where polysemy actually wires into a loop — but those SCCs are rare and the structure on them is a degenerate conflict gadget, not a grounding-set story.

(Preferred-extension enumeration: the lemma-level dispatcher punted preferred at scale; here it is run brute-force on the slice — `preferred_count` above. It works because the slices are ≤ 14 nodes. It does not scale, and was not attempted on the Kernel.)

### 2b. Whole sense Kernel (attacks-only Dung AF — Model B is infeasible at scale)

A first attempt ran the full Cayrol derived-defeat closure on the whole 12,142-node Kernel; it **blew past 9 GB RSS without terminating** and was killed. (Why: the Kernel's giant support SCC reaches almost everything; an attacker on any of its nodes is propagated to the whole reachable set; the derived defeat relation approaches a complete graph on ~10⁴ nodes ≈ 10⁸ edges.) So the Cayrol-coupled Model B is **only feasible per small SCC** — done above. On the whole Kernel we report the *attacks-only* Dung AF (rival-sense clique edges restricted to the Kernel, no support propagation), which is scalable and answers the headline question directly:

| quantity | value |
|---|---|
| Kernel nodes | 12,142 (vs lemma Kernel 18,151) |
| Kernel SCCs | 7,466 |
| Kernel seed (`bounded-scc`) | 1,299 |
| residual cyclic SCC count after seed | 2 |
| Kernel nodes in a rival clique | 6,446 |
| Kernel-restricted rival cliques | 1,519 (1,006 of size 2; 278 size 3; 115 size 4; …; one size 17) |
| Kernel `attacks` edges (ordered) | 9,436 |
| grounded extension (attacks-only Kernel AF) | 8,087 nodes — 0.04 s |
| **stable extension exists?** | **YES** (z3, `find_stable_extension`, 1.74 s); witness size 9,606 |
| stable-extension count | log₁₀ ≈ **1,889** (= product of Kernel-restricted clique sizes) |

The attacks-only Kernel AF is a disjoint union of rival-sense cliques plus ~5,696 isolated (non-rival) Kernel nodes; such an AF *always* has stable extensions (pick one member from each clique, take all isolated nodes), and the count is the product of clique sizes. So stable existence flips UNSAT→SAT *purely because the attack relation changed from "definition edges read as attacks" (odd cycles → UNSAT) to "rival-sense cliques" (no odd cycles → always SAT)* — it is an artifact of the new attack relation's shape, not a discovery about the lexicon. (The full sense graph: same story, count log₁₀ ≈ 52,931.)

---

## 3. The headline question, point by point

**(a) Is the sense-Kernel-with-attacks AF still UNSAT for stable, or does it now have stable extensions — and if so, many?**
It now *has* stable extensions (z3, 1.7 s), and many — log₁₀ ≈ 1,889 of them, multiplicatively (each rival clique contributes its size as a factor). But this multiplicity is **vacuous**: it comes from the rival-sense attack relation being a disjoint clique union, not from the lexicon's support wiring; choosing a reading for one form is independent of every other choice; there is no MinSet-like structure in it. The "many MinSets = many stable extensions" identity, which collapsed at the lemma level (Kernel AF UNSAT), does **not** become true at the sense level — what becomes true is a different, content-free statement ("a form with k senses has k readings"). The non-vacuous version (support-coupled, via Cayrol) is the one that would have been a result, and it is infeasible at Kernel scale; on the rare small SCCs where it is feasible it produces near-complete-conflict gadgets, not grounding-set families.

**(b) Does `enforce_skeptical` over this AF return something MinSet-shaped?**
No. On attack-free SCCs it returns cost 0 (the node is already skeptically accepted). On the one slice SCC with internal attacks it *fails* (no enforcement at edit-cost ≤ 2). `enforce_skeptical` is per-argument and edits defeats; it is not a global grounding-set query and does not recover the MinSet. (`enforce_skeptical` was never run on the whole Kernel — the Cayrol-derived whole-Kernel AF doesn't exist, and on the attacks-only AF it would just report cost 0 for every non-rival node and a per-clique edit for rival nodes — still not the MinSet.)

**(c) Does the ranking semantics still collapse to degree on the bipolar graph?**
Yes. h-categoriser on the sense Kernel (12,142 nodes), two variants:
- *support edges as attacks* (the sign-correct re-run of the lemma-level finding, now on the sense graph): ρ(h-cat score, −in-degree) = **0.828**; top words: `positive`-s, `line`-n, `rhizomatous`-a, `wavelike`-s, `change`-n, `canvas`-n, `micro`-s, `moist`-s, `pawn`-v, `divinely`-r, `waxed`-a, `occupation`-n, `information`-n, … — definitional *leaves* / low-in-degree words, the sign still "wrong" for "foundational."
- *support + rival-sense attacks, both as attacks*: ρ(h-cat score, −#attackers) = **0.778**; ρ between this ranking and the support-only ranking = **0.807**; top words: `rhizomatous`, `wavelike`, `micro`, `moist`, `pawn`, `divinely`, `waxed`, `buddhist`, `semantic_role`, `rowing`, … — essentially the same list with the few high-in-degree words (`positive`, `line`, `change`, `information`) dropped (they pick up rival-sense attackers and fall). Adding the attack layer does not give the ranking semantics anything to chew on; it remains an arithmetic re-skin of degree, exactly as on the `lemma::pos` graph (`reports/ranking-valuation-oewn.md`). (The "right" h-categorizer import — bipolar/support side, scoring *high* the words many things depend on — would need a support-aware gradual semantics; plain h-categoriser-on-attacks ranks the leaves whichever attack relation you feed it.)

---

## 4. The honest verdict — (ii)

**(ii) The sense level does *not* rebut the relabeling charge.** Even with the attack layer:
- stable-extension multiplicity is real but **vacuous** (disjoint rival cliques; no grounding-set content);
- `enforce_skeptical` gives **nothing MinSet-shaped**;
- the ranking semantics is **still degree-dominated** (ρ ≈ 0.78–0.83) with the **still-wrong sign**;
- the structure the attack layer adds is genuine *only* on the rare small SCCs where rival senses co-occur in a definitional loop, and there it is a **degenerate near-complete-conflict gadget** (grounded empties, k preferred extensions all singletons), not a feedback-vertex-set family;
- the support-coupled bipolar AF (the version that *would* be a result) is **computationally infeasible at Kernel scale** (Cayrol closure → 9 GB RSS without terminating).

So the relabeling charge stands at the sense level too — with one piece of nuance Gemini's review already anticipated: the reframing is *not vacuous* at the sense level the way it is at the lemma level (the bipolar/ADF semantics are no longer the identity function, because there are now non-empty attacks). Its net-new content is conceptual and architectural — "WSD inside a definitional loop is a `gunray`-shaped defeasible-reasoning problem with these specific attack edges," and "the sibling libraries are per-SCC oracles + a type system" — not computational. **The argumentation tools are a conceptual frame, not a lever; the FVS / Kernel / MinSet machinery remains the only layer that actually answers the dictionary-bootstrap question.** (Net-new *result* candidate, weak: "the sense-Kernel admits stable extensions where the lemma-Kernel does not" — but this is an artifact of swapping the attack relation, so it should be reported as a structural observation, not sold as a discovery.)

---

## 5. What this run could not do

- **The support-coupled bipolar AF (Model B) on the whole Kernel.** The Cayrol derived-defeat closure OOM'd (> 9 GB RSS, no termination) — the Kernel's giant support SCC makes the derived defeat relation near-complete. Done only per small SCC (269 of them have internal attacks; 6 in the slice). An incremental / SCC-condensed Cayrol closure (or an ADF encoding that avoids materializing the closure) would be needed for the whole-Kernel version.
- **Preferred-extension enumeration on the Kernel.** Π₂ᵖ-complete; brute-forced only on the ≤ 14-node slices.
- **A WSD / admission step.** This run builds the attack edges; it does *not* decide which rival sense survives (the Nobelium-artifact resolution). That is the `gunray`/`AdmissionPolicy` work (synthesis agenda #6), unbuilt.
- **An exact stable-extension count.** `argumentation` has no SAT-backed model count; the count is reported analytically (∏ clique sizes) for the attacks-only AF, and z3 only decides *existence*.
- **`enforce_skeptical` at scale.** Run only on slice nodes (per-argument, brute-force edit search at `max_cost=2`).

---

## 6. Files & commits (branch `sense-attack-layer`)

- `src/meanings/wordnet_pipeline.py` — `SenseLevelGraphWithAttacks`, `add_rival_sense_attacks`, `build_sense_level_paper_wordnet_graph_with_attacks` (existing `build_sense_level_paper_wordnet_graph` untouched).
- `src/meanings/argumentation_bridge.py` — `bipolar_with_attacks_framework`, `derived_dung_framework`.
- `scripts/sense_level_argumentation.py` — the reproducer.
- `tests/test_sense_attack_layer.py` — 6 tests (tiny 2-form/2-sense graph: 1 attack pair, bipolar round-trip, support-into-rival breaks the clique symmetry, bare clique = k stable, chain support propagates attack forward). Full suite: `uv run pytest` → 66 passed.
- `reports/sense-level-argumentation.json` — all numbers.
- `notes/sense-level-argumentation.md` — working notes.

Commits: `b3daa8a` (attack-layer builder + bridge + tests), `777618b` (script v1 + notes), `36ae806` (script patched: scalable whole-Kernel attacks-only AF after the Cayrol-closure OOM; slice picks SCCs with internal rival attacks; unbuffered), plus this report.
