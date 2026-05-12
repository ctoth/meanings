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

| Contributor | Invocation | Role |
|---|---|---|
| Orchestrator (this Claude) | — | Dispatch, collect, write the integration draft, adjudicate disagreements, run the verification gate, present to Q. Does not do facet deep-dives itself (delegates) — keeps context clean for integration. |
| Sub-Claude × 4 (facet deep-dives) | `Agent` (subagent_type `claude`) — managed, notified on completion. | One each: **(a) math/complexity** (Perron–Frobenius across fields; the scaling complexity story — what's poly, what's NP/Π₂ᵖ, why this graph is tractable; the SCC+FVS-backdoor+z3 architecture); **(b) philosophy** (grounding; foundationalism vs coherentism = grounded vs preferred; Yoneda/Harnad; what the psycholinguistic regression does and doesn't show; "recursive definability ≠ meaning" mechanized via `gunray`); **(c) the data model** (form/sense/IC/reading/admission as a typed defeasible system; the sense-level rebuild; ADF over sense nodes; IC merge as belief-merge with provenance); **(d) the engineering** (the `meanings` ↔ `argumentation` boundary; what to build, in what order; the upstream fixes to `../argumentation`; the deliverable surfaces — strict seed, human list). Each writes `reports/synthesis-facet-{math,philosophy,datamodel,engineering}.md`. |
| Scout | `Agent` (subagent_type `scout`) | One pass: re-inventory `reports/` and `notes/` and `workstreams/` and `papers/index.md` and the `src/` modules for *what has already been concluded / built / decided* — so the integration doesn't contradict or re-litigate settled things. Writes `reports/synthesis-inventory.md`. (Most of this exists across the sibling-tool reports + `swanson-synthesis.md`; the scout's job is the cross-cutting "here is the current state of truth" digest.) |
| Analyst | `Agent` (subagent_type `analyst`) | Reads the four facet files + the inventory + the integration draft (once it exists) and finds: contradictions between facets, claims with no cited support, places where the argumentation reframing contradicts the spectral/Swanson findings, where the upgoer note contradicts the self-loop fix, what's load-bearing vs speculative, what numbers are stale (the post-self-loop-fix Kernel numbers vs the old ones quoted in `swanson-synthesis.md` / `spectral-valuation-oewn.md`). Writes `reports/synthesis-analyst-findings.md`. Does not fix; flags. |
| Codex | `codex exec --dangerously-bypass-approvals-and-sandbox "Read reports/synthesis.md and reports/synthesis-facet-*.md; attack the synthesis from <the biggest risk angle>; write reports/synthesis-review-codex.md"` | Adversarial review of the integration draft, plus: it's the natural one to *implement* whatever load-bearing prototype the synthesis identifies (e.g. the `meanings.argumentation_bridge` divide-and-conquer dispatcher, or the sense-level ingestion classifier) — but that's a follow-up task, not part of the synthesis pass. |
| Gemini | `gemini --yolo "Read reports/synthesis.md ... attack from <a different risk angle> ... write reports/synthesis-review-gemini.md"` (verify output — Gemini sometimes copies instead of executing). | Second adversarial review, from a *different* angle than Codex (assign the angles explicitly so they don't overlap). |
| Claude-as-peer | `claude -p --effort high --dangerously-skip-permissions --permission-mode bypassPermissions "Do not restate the task. Read reports/synthesis.md ... attack from <a third risk angle> ... return exactly N sections ... write reports/synthesis-review-claude.md"` (run via `Bash`, poll up to 10 min, use the result the moment it returns). | Third adversarial review. Using `claude -p` rather than the `Agent` tool here puts it on the same footing as Codex and Gemini — three peer critics, three distinct angles. |
| Verifier | `Agent` (subagent_type `verifier`) | Final gate: reads the revised synthesis + the three reviews + the analyst findings; decides whether the synthesis is internally consistent, every load-bearing claim is cited, the stale numbers are fixed, and the open-questions / next-steps are honest. Verdict: SHIP / NO-SHIP with reasons. Default NO-SHIP. |

## Pipeline (phases — filesystem artifacts hand off between them)

0. **Inventory** (scout, parallel-with-nothing). → `reports/synthesis-inventory.md`. Orchestrator reads it.
1. **Facet deep-dives** (4 sub-Claudes, parallel). Each gets: the inventory, the relevant existing reports, its facet brief. → `reports/synthesis-facet-{math,philosophy,datamodel,engineering}.md`. Orchestrator reads all four.
2. **Integration draft** (orchestrator, solo). Writes `reports/synthesis.md` — the five-question structure above, woven from the four facets + the inventory + the source reports, with explicit "open / contested / load-bearing-but-unverified" callouts. Plus `reports/synthesis-research-agenda.md` (the prioritized backlog) and `reports/synthesis-paper-outline.md` (the "Discrete Grounding and Spectral Valuation in Dictionary Graphs" outline + the two-or-three subsidiary papers).
3. **Adversarial multi-review** (Codex + Gemini + Claude-peer + Analyst, parallel; the three external critics get *distinct* assigned angles — e.g. "the argumentation reframing is over-claimed / it's a relabeling not a result", "the scaling claim is wrong / the hard SCC will kill it", "the whole project is reinventing distributional semantics with extra steps", "the sense-level rebuild is unfalsifiable hand-waving"). → `reports/synthesis-review-{codex,gemini,claude}.md` + `reports/synthesis-analyst-findings.md`. Orchestrator reads all.
4. **Revision** (orchestrator, solo). Folds the critiques into `reports/synthesis.md` (and the agenda / outline). Every critique either gets addressed in-text or gets an explicit "we disagree because …" or "noted, follow-up task X." Nothing silently dropped.
5. **Verification gate** (verifier, solo). → SHIP / NO-SHIP. If NO-SHIP, back to step 4 with the verifier's blockers. Cap: two revision rounds, then escalate to Q.
6. **Present to Q** — the orchestrator's summary + `reports/synthesis.md` + the verdict.

## Conventions

- Everything is a file in `reports/` (or `notes/`). No contributor's output lives only in a tool-result message — the orchestrator relays summaries to Q, but the artifacts are on disk.
- Subagent prompts: observations only, no theorizing beyond cited support (per house rules); each is told *not* to commit.
- Orchestrator commits the synthesis artifacts in coherent chunks after each phase, pulling first (Q co-edits this repo in parallel; expect interleaving).
- The three peer critics (`codex exec`, `gemini --yolo`, `claude -p`) are given **non-overlapping** attack angles, written into their prompts, so the reviews don't all hit the same soft spot.
- If the thread limit blocks spawning the 4 facet sub-Claudes + scout + analyst at once, wave it: spawn what fits, wait, spawn the rest (the `Agent` thread-limit is not a failure).

## Open questions for Q (before launching)

- Scope of the synthesis: just the *intellectual* synthesis (what is this, what have we learned, what next), or also a *plan* with milestones/owners? The spec above does the former + a research agenda; a full project plan is a bigger thing.
- Do you want the four facets as I've cut them (math / philosophy / data model / engineering), or a different cut (e.g. add a fifth "the cross-domain Swanson links as a standalone facet" rather than folding it into math+philosophy)?
- The peer critics' attack angles — do you want to assign them, or shall I?
- Timing: launch the whole pipeline now (it'll run for a while across many agents), or do phases 0–1 first, look at the facets, then decide?
