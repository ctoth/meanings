# Spec (draft): the multi-contributor synthesis

**Date:** 2026-05-12
**Status:** draft for Q's review — "let's start speccing that out"

## Goal

Produce one coherent synthesis (a document, possibly with a short companion "research agenda" and a "paper outline") that integrates every thread this project has accumulated, written by several contributors — the orchestrating Claude, sub-Claudes, specialized subagents (scout / analyst / verifier), Gemini, and Codex — each pulling on the facet it's best at, then adversarially cross-checked, then gated.

The synthesis must answer, in order:
1. **What is this project?** — dictionaries as definition digraphs; the Kernel / Core / Satellites / MinSet (feedback-vertex-set) decomposition; Harnad's symbol-grounding problem; the "human Up-Goer vocabulary" deliverable.
2. **What has the cross-domain (Swanson) pass found?** — Perron–Frobenius valuation (the spectral object ≈ laundered out-degree); structural controllability vs FVS-control (the FVS-control biology lineage is the cleanest link); core–satellite ecology (falsified); Yoneda/Harnad (compatibility, not contradiction; the psycholinguistic regression refuted only the strong residue claim); money/numéraire (Sraffa standard commodity = Perron eigenvector; demoted). Per `reports/swanson-synthesis.md`.
3. **What is the argumentation-framework reframing?** — the definition digraph is a bipolar AF / ADF; MinSet = minimal enforcement set; "many MinSets" = stable-extension multiplicity; Kernel-vs-loop-ecology = grounded-vs-preferred; the sibling tools (`../argumentation`, `../belief-set`, `../gunray`); the scaling result (grounded in 0.8s at 160k via labelling, the library's own impls are quadratic, the SCC+z3+FVS-backdoor divide-and-conquer is the path; the Kernel AF has no stable extension — UNSAT). Per `reports/sibling-tools-connection.md`, `reports/argumentation-bridge-oewn.md`.
4. **What is the ingestion redesign?** — form → token → reading → sense → IC → admission as a typed defeasible system; the sense-level rebuild; the self-loop-artifact prediction. Per `notes/upgoer-identity-clusters.md`, §7 of `reports/sibling-tools-connection.md`.
5. **What is the architecture, and what do we build next?** — the layered picture (well-foundedness / valuation / dynamics / ingestion), the prioritized backlog, the paper(s).

Non-goal: re-deriving anything already in the reports. The synthesis *cites and integrates*; it does not re-run the experiments. (Where a contributor finds a gap or contradiction, it flags it for a follow-up task — it does not silently patch.)

## Contributors and roles

**Principle (rev. after Q's note):** the *only* role that has to be Claude is the **orchestrator/integrator**, because that role needs the full accumulated conversation context and Codex/Gemini start cold every invocation. Everything else — facet authorship, scouting, analysis, critique, verification, prototype implementation — rotates across all three model families. Reason: a synthesis three Claudes converge on is weak evidence (shared training, shared blind spots); a synthesis Claude + Codex + Gemini converge on is strong. The two highest-stakes / most-prone-to-over-claiming facets are written **twice, by different families**, and the divergence between the two drafts is itself an input the integration must reconcile. Verification invariant: any load-bearing output is checked by a *different agent, ideally a different model* — never "Claude audits the others."

| Contributor | Invocation | Role |
|---|---|---|
| **Orchestrator** (this Claude) | — | Dispatch, collect, write the integration draft + revision, adjudicate divergences (including the deliberate twin-draft divergences), present to Q. Necessarily Claude (context). Does not author facets. |
| **Facet — math/complexity** | Codex: `codex exec --dangerously-bypass-approvals-and-sandbox "Read <inventory + the relevant reports>; write reports/synthesis-facet-math.md covering: Perron–Frobenius valuation across fields; the scaling complexity story (what's poly, what's NP/Π₂ᵖ, why this graph is tractable — SCC + FVS-backdoor + z3); cross-check the claim that grounded is poly by actually running it. Do not restate the task. Do not commit."` | Single author — Codex, because it can *run the scaling sanity-check* while writing. |
| **Facet — engineering** | Claude: `Agent` (subagent_type `claude`) | Single author — Claude. The `meanings` ↔ `argumentation` boundary; what to build in what order; the upstream `../argumentation` fixes (done — record them); the deliverable surfaces (strict seed, human Up-Goer list). → `reports/synthesis-facet-engineering.md`. |
| **Facet — data model** (twin) | Draft A: Claude `Agent` (subagent_type `claude`). Draft B: `gemini --yolo "Read <inventory + notes/upgoer-identity-clusters.md + §7 of reports/sibling-tools-connection.md>; write reports/synthesis-facet-datamodel-gemini.md covering: form/sense/IC/reading/admission as a typed defeasible system; the sense-level rebuild; ADF over sense nodes; IC merge as belief-merge with provenance. Do not restate the task."` (verify Gemini actually wrote the file, didn't just copy). | **Two independent drafts** (`...-datamodel-claude.md`, `...-datamodel-gemini.md`). Highest-stakes facet (most prone to "this is just an LLM with extra steps" and to unfalsifiable hand-waving) — the divergence is a finding. |
| **Facet — philosophy** (twin) | Draft A: `gemini --yolo "... write reports/synthesis-facet-philosophy-gemini.md covering: grounding; foundationalism vs coherentism = grounded vs preferred; Yoneda/Harnad; what the psycholinguistic regression does and doesn't show; 'recursive definability ≠ meaning' mechanized via gunray. ..."`. Draft B: `codex exec ... "... write reports/synthesis-facet-philosophy-codex.md covering [same] ..."`. | **Two independent drafts**, neither by Claude (this is the facet where Claude is *most* likely to be eloquently wrong). Divergence is a finding. |
| **Scout / inventory** | `Agent` (subagent_type `scout`) — or Codex if the family load needs balancing. | Re-inventory `reports/`, `notes/`, `workstreams/`, `papers/index.md`, `src/` for *what is already concluded / built / decided*, so the integration doesn't re-litigate settled things. → `reports/synthesis-inventory.md`. Runs first; everyone else gets it. |
| **Analyst** | `Agent` (subagent_type `analyst`) — or Gemini. | Reads the facet drafts (incl. both halves of each twin) + inventory + integration draft; finds contradictions, uncited claims, places where the argumentation reframing contradicts the Swanson findings, where the upgoer note contradicts the self-loop fix, what's load-bearing-but-unverified, what numbers are stale (post-self-loop-fix Kernel numbers vs the old ones in `swanson-synthesis.md` / `spectral-valuation-oewn.md`). → `reports/synthesis-analyst-findings.md`. Flags; does not fix. |
| **Critics × 3** (all families, distinct angles, no self-review) | Codex: `codex exec ... "attack from <angle 1>"` → `reports/synthesis-review-codex.md`; Gemini: `gemini --yolo "attack from <angle 2>"` → `reports/synthesis-review-gemini.md`; Claude-peer: `claude -p --effort high --dangerously-skip-permissions --permission-mode bypassPermissions "Do not restate the task. ... attack from <angle 3>; return exactly N sections; write reports/synthesis-review-claude.md"` (via Bash, poll up to 10 min). | Adversarial review of the *integration draft*. Each gets a different assigned angle; **a model never critiques a facet it co-authored** (so Codex — which wrote the math facet and half the philosophy facet — critiques the data-model or engineering content, etc.). |
| **Verifier gate** | Rotates by load — whichever of `claude -p` / `codex exec` / the `Agent` `verifier` authored the *least* this run. | Final gate: revised synthesis + the three reviews + analyst findings → SHIP / NO-SHIP, default NO-SHIP, reasons. |
| **Prototype implementation** (follow-up, not the synthesis pass) | Codex or Claude `Agent`, whichever fits; verified by the other (or Gemini). | The ADF-over-sense-nodes encoding / the SCC+z3+FVS-backdoor dispatcher / the sense-level ingestion classifier — once the synthesis prioritizes one. |

## Pipeline (phases — filesystem artifacts hand off between them)

0. **Inventory** (scout). → `reports/synthesis-inventory.md`. Orchestrator reads it.
1. **Facet deep-dives** (parallel, all three families authoring): math/complexity → Codex (1 draft); engineering → Claude (1 draft); data model → Claude + Gemini (2 drafts); philosophy → Gemini + Codex (2 drafts). Each author gets the inventory + the relevant existing reports + its brief. → `reports/synthesis-facet-{math,engineering}.md`, `reports/synthesis-facet-datamodel-{claude,gemini}.md`, `reports/synthesis-facet-philosophy-{gemini,codex}.md`. Orchestrator reads all six.
2. **Integration draft** (orchestrator, solo). Writes `reports/synthesis.md` — the five-question structure above, woven from the facets (reconciling each twin pair, divergences flagged) + the inventory + the source reports, with explicit "open / contested / load-bearing-but-unverified" callouts. Plus `reports/synthesis-research-agenda.md` and `reports/synthesis-paper-outline.md`.
3. **Adversarial multi-review** (parallel; 3 critics, distinct assigned angles, no self-review of co-authored facets — Codex/Gemini critique content they didn't write; + Analyst). → `reports/synthesis-review-{codex,gemini,claude}.md` + `reports/synthesis-analyst-findings.md`. Orchestrator reads all.
4. **Revision** (orchestrator, solo). Folds the critiques in. Every critique either addressed in-text, or "we disagree because …", or "noted, follow-up task X." Nothing silently dropped.
5. **Verification gate** (rotating: whichever of `claude -p` / `codex exec` / the `verifier` agent authored least). → SHIP / NO-SHIP, default NO-SHIP. If NO-SHIP, back to step 4. Cap: two revision rounds, then escalate to Q.
6. **Present to Q** — the orchestrator's summary + `reports/synthesis.md` + the verdict.

## Conventions

- Everything is a file in `reports/` (or `notes/`). No contributor's output lives only in a tool-result message — the orchestrator relays summaries to Q, but the artifacts are on disk.
- Subagent prompts: observations only, no theorizing beyond cited support (per house rules); each is told *not* to commit.
- Orchestrator commits the synthesis artifacts in coherent chunks after each phase, pulling first (Q co-edits this repo in parallel; expect interleaving).
- The three peer critics (`codex exec`, `gemini --yolo`, `claude -p`) are given **non-overlapping** attack angles, written into their prompts, so the reviews don't all hit the same soft spot.
- If the thread limit blocks spawning the 4 facet sub-Claudes + scout + analyst at once, wave it: spawn what fits, wait, spawn the rest (the `Agent` thread-limit is not a failure).

## Open questions for Q (before launching)

- Scope: just the *intellectual* synthesis (what is this / what have we learned / what next) + a research agenda + a paper outline (what the spec does), or also a full project plan with milestones/owners (bigger)?
- The facet cut: math/complexity, engineering, data-model, philosophy as drawn (with the cross-domain Swanson links folded into math+philosophy)? Or split the Swanson links into a fifth facet? If a fifth: who authors it — Claude (it's been the one closest to that material), or hand it to whichever family has spare load?
- The contributor rebalance above (only the orchestrator is necessarily Claude; facets distributed; data-model + philosophy written twice by different families; verifier rotates) — good as is, or do you want a different distribution? (E.g. you might want the *engineering* facet not on Claude either, given Claude built the bridge.)
- Critic attack angles — you assign the three, or I do?
- Timing: launch phases 0–1 (scout + the six facet drafts) now and look at them before committing the rest, or launch the whole pipeline?
