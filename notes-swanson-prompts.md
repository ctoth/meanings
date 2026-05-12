# notes: meanings repo setup + Swanson research prompts

## 2026-05-12

### Repo bootstrap (done)
- `meanings` was an uncommitted working dir. Grokked it: dictionary-kernel tooling — builds OEWN gloss digraph via `wn`, extracts Kernel/Core/Satellite layers + feedback-vertex-set seeds (Massé 2008 / Picard 2013 / Vincent-Lamarre 2014 lineage), `papers/` = literature notes, `reports/` = generated output + research dossier.
- Wrote `README.md`. Updated `.gitignore` (added `.venv/`, `__pycache__/`, `*.pyc`, `pyghidra_mcp_projects/` [stray Ghidra project, Q confirmed exclude], `unused-papers/`).
- Initial commit `0b57023`, 125 files. Created public repo `ctoth/meanings` (Q confirmed public), pushed. Remote = `origin` = `git@github.com:ctoth/meanings.git`. Default branch is `master` (flagged to Q; left as-is).

### Swanson research prompts (done)
Q asked to turn the cross-domain "what's defined by its neighbors" ideas into deep-research-agent prompts, one markdown each. In `reports/`:
- `research-swanson-1-money-numeraire.md` — symbol grounding ≡ gold-standard/numéraire problem; MinSets ≡ arbitrariness of numéraire (Sraffa standard commodity).
- `research-swanson-2-core-satellite-ecology.md` — Hanski core-satellite hypothesis (ecology 1982) ↔ dictionary Core/Satellite (2014); has a runnable bimodality check on existing OEWN JSON.
- `research-swanson-3-controllability-driver-nodes.md` — lexical grounding sets (FVS) ↔ structural controllability driver nodes (Liu-Slotine-Barabási 2011, max matching); runnable max-matching comparison on OEWN graphs.
- `research-swanson-4-yoneda-harnad.md` — is meaning Yoneda-complete? category-theory structuralism vs Harnad's grounding residue; adjudicate via extra-graph variance (AoA/concreteness) in layer membership.
- `research-swanson-5-perron-frobenius-valuation.md` — **the central one.** Dominant eigenvector of a non-negative relational matrix as canonical-anchor algorithm, rediscovered ~6× (Sraffa standard commodity, LSA semantic axes, PageRank, Bonacich/Hubbell/Katz/Pinski-Narin centrality, Markov stationary dist) with near-empty cross-citation. Repo payoff: spectral anchor (unique `v*`) dissolves the combinatorial MinSet arbitrariness; and the two compose — run PF on the strongly-connected Kernel, recursion on the reducible Rest. Has the headline runnable deliverable (Perron/PageRank ranking vs MinSet membership vs layers vs psycholinguistic overlays on existing OEWN data).
- Commits: `1e89bff` (prompts 1-4), `78d0ea4` (prompt 5). Both pushed.

### Execution launched (2026-05-12)
Q said "run all prompts with their own subagents, also ask codex, go hard." Dispatched 6 background streams:
- 5 `researcher` subagents, one per prompt file, each told to read the brief, do web research, run the in-repo computation the brief specifies (2/3/5 each have one), write `reports/swanson-<topic>-findings.md`. Agent IDs: ab71d377b6a89aa17 (1 money), a8856df375d1d1161 (2 ecology), a6b1f8872f063e1ad (3 controllability), a0b72c025bed3532b (4 yoneda), afddb8bdf1837f5e3 (5 perron-frobenius).
- Codex via `protocols:external-agents`: `codex exec --dangerously-bypass-approvals-and-sandbox`, background bash ID bvklzfk33, log `codex-swanson.log`, writing `reports/codex-swanson-review.md` — skeptical review of all 5 briefs + independent contribution to the 2 it judges strongest. No web, own knowledge.

### Progress
- ~16:27 transient DNS outage on Q's machine (~30s) killed researcher agents 3 & 4 and disrupted Codex. Network recovered. Re-dispatched 3 (ab395758bbc9dff5a) and 4 (a6a6bf774fcc6664d).
- Prompt 1 (money/numéraire) DONE — `reports/swanson-money-numeraire-findings.md`: 13-row correspondence table, disjointness evidence (closest near-miss = Sraffa–Wittgenstein/Ajit Sinha thread), 5 ranked transferable tools (top = Sraffa standard commodity → PF eigenvector of weighted Core as canonical-MinSet algorithm; runnable on existing pipeline), 6 falsifiers (the prompt's headline falsifier does NOT fire — Sraffa basics/non-basics IS an SCC decomposition), proposed paper "Meaning Has No Gold Standard" → Cognitive Science / Topics in CogSci. Couldn't get clean text of Sraffa 1960 or Patinkin — quoted via secondaries, flagged.
- Agents 2 (ecology, wrote scripts/bimodality_check.py — has missing-import bugs: sklearn/diptest not installed) and 5 (perron-frobenius, wrote scripts/perron_frobenius_oewn.py) still running. Re-run agent 3 wrote scripts/maximum_matching_oewn.py.
- Codex: check codex-swanson.log + reports/codex-swanson-review.md; may have died in outage — re-run if so.

### Completions log
- DONE: prompt 1 (money), prompt 4 (yoneda → verdict Resolution A + symmetry rider), Codex review (ranks: PF #1, controllability #2, ecology #3, money #4, yoneda #5; proposes lead paper "Discrete Grounding and Spectral Valuation in Dictionary Graphs"), prompt 5 (perron-frobenius).
- KEY RESULT prompt 5: naive hypothesis (Perron eigenvector = canonical soft grounding vocab) FALSIFIED on OEWN. Authority PageRank ranks definitional SINKS at top; seed hubs (small/large/body/plant) sit in bottom decile (median PR rank ~48k/160k). Un-damped Perron on 8138-node kernel SCC localises on technical micro-cliques (potassium/rubidium/...), λ*≈3.744, ~degree re-skin. DIAGNOSIS = surviving paper: FVS heuristic is an OUT-flow object → matching spectral object is REVERSE-PageRank on the kernel, not authority PageRank. Predicted (not run): reverse-PR ranks small/large/white/plant/body near top, ρ>0.6 with seed degree-score. Codex Prediction C called this. Files: reports/swanson-perron-frobenius-findings.md, reports/perron-frobenius-oewn.json, scripts/perron_frobenius_oewn.py.
- BLOCKER noted by multiple agents: repo ships NO psycholinguistic CSVs (annotation_sources: [], coverage 0). Need SUBTLEX-US / Kuperman 2012 AoA / Brysbaert 2014 concreteness → data/psycholinguistic/*.csv. Codex also flagged: top-definer lists polluted by sense-resolution/gloss-parsing artifacts (large[n]=garment size, born=Max Born) — clean before any occupancy/frequency test.
- STILL RUNNING: prompt 2 (ecology, ab... a8856df375d1d1161 + scripts/bimodality_check.py has missing-deps bug sklearn/diptest), prompt 3 re-run (ab395758bbc9dff5a, scripts/maximum_matching_oewn.py).

### More completions
- DONE prompt 3 (controllability re-run): computation ran. Full digraph → 118,744 drivers (74.2%); kernel subgraph → 2,785 drivers (21.7%, comparable in size to 2,370 FVS-seed but only 255 in common, Jaccard 0.052). FVS and driver sets genuinely diverge — confirms prediction. Driver-not-grounder = morphological derivatives + numeral/proper-noun acyclic frontier; grounder-not-driver = abstract relational vocab + proper-noun islands. Top transferable tool: FVS-control (Fiedler–Mochizuki / Zañudo–Yang–Albert) — unexploited bridge. Flagged: self-loop handling inconsistency in compute_kernel (`target != node` filter). Files: reports/swanson-controllability-findings.md, reports/maximum-matching-oewn.json, scripts/maximum_matching_oewn.py.
- Q said "kick those off" → launched 2 follow-up `claude` agents (background): a1f0cfc8414c31a55 = ingest psycholinguistic norms (SUBTLEX-US, Kuperman AoA, Brysbaert concreteness → data/psycholinguistic/, wire to CLI, verify coverage>0); a90c63e203ee554c6 = confirm reverse-PageRank diagnosis from prompt 5 + build src/meanings/spectral_analysis.py per Codex spec + reports/spectral-valuation-oewn.md.
- STILL RUNNING: prompt 2 (ecology) a8856df375d1d1161; the 2 follow-ups above.

### Prompt 2 (ecology) DONE — negative result
Disjointness genuine (canonical Swanson signature, both directions). But bimodality falsifier TRIGGERED: OEWN out-degree (Hanski occupancy analogue) is 74.3% zero + monotone heavy tail (log-series-like), no second hump; dip test "rejects" only because of zero-spike at huge n; GMM BIC keeps falling = straining to fit one skew. Sharpest extra falsifier: Core (n=288) and Satellite (n=12565) have ~identical out-degree distributions (means 43.8 vs 42.5) — the lexical Core/Satellite split is condensation topology (source vs downstream SCC), NOT common-vs-rare like Hanski's. Naming analogy shallower than it looks. Weak form survives (colonization-extinction process view of defining vocab across dictionary editions) but the strong prediction is contradicted by current data; testing needs diachronic definition text (LDOCE controlled-defining-vocab revisions = near-perfect natural experiment). Honest paper = cautionary cross-disciplinary note "Core and Satellite, Twice Over". Files: reports/swanson-core-satellite-findings.md, scripts/bimodality_check.py, scripts/bimodality_kernel.py (re-run: `uv run --with scikit-learn --with diptest python scripts/bimodality_kernel.py`).

ALL 5 RESEARCH PROMPTS + CODEX DONE. Still running: psycholinguistic ingest (a1f0cfc8414c31a55), spectral module re-run (aae8a900ddef8da59, actively writing src/meanings/spectral_analysis.py + scripts/spectral_report.py + tests/test_spectral_analysis.py — minor pyright issues, agent will resolve).

### Scoreboard (after the swarm)
- #1 Perron-Frobenius: naive form FALSIFIED on OEWN; surviving result = "The Wrong Eigenvector" — FVS heuristic is out-flow → matching object is REVERSE-PageRank on kernel (being confirmed now). Plus a real history-of-science paper (convergent rediscovery; Bidard-Erreygers-Parys "All but one" / Potron 1911).
- #2 Controllability: genuine divergence FVS≠driver-nodes confirmed on OEWN (Jaccard 0.05 on kernel); surviving bridge = FVS-control (Mochizuki/Zañudo), unexploited.
- #3 Ecology: bimodality falsifier triggered; analogy shallow; only diachronic weak form survives, untested.
- #4 Yoneda/Harnad: verdict Resolution A (compatible; grounding = constructing the base category) + symmetry rider (Benacerraf access problem = Harnad's problem); empirical leg blocked on missing norms (ingest agent fixing).
- #5(money): partly real, conflates 4 things, subsumed by PF valuation line; demote to interpretive preface. (this was prompt 1)
- Codex's synthesis: 3-layer architecture (well-foundedness / valuation / dynamics); lead paper = "Discrete Grounding and Spectral Valuation in Dictionary Graphs".

### Psycholinguistic ingest DONE — but in a WORKTREE
Agent a1f0cfc8414c31a55 ran in worktree `.claude/worktrees/agent-a1f0cfc8414c31a55` (branch worktree-agent-a1f0cfc8414c31a55), changes UNCOMMITTED there. Got all 3 datasets: SUBTLEX-US (OSF mirror), Kuperman 2012 AoA (OSF), Brysbaert 2014 concreteness (Springer ESM). Produced loadable CSVs data/psycholinguistic/{frequency,age_of_acquisition,concreteness}.csv (74284/31104/39953 rows, format `word,<field>` matching annotations.py). Verified via CLI: OEWN paper-wordnet coverage now 28.99% freq / 24.11% conc / 21.44% AoA over 160010 nodes (was 0). Also: data/psycholinguistic/README.md, scripts/build_psycholinguistic_csvs.py, rewrote reports/annotation-sources.md, regenerated reports/oewn-paper-wordnet-kernel-{report.md,summary.json}, added pandas+openpyxl to pyproject/uv.lock, notes/psycholinguistic-data.md.
ACTION NEEDED at commit time: bring this worktree's changes into master (commit in worktree + merge, or copy files over). Don't lose it.

### ALL DONE — committing now
Spectral agent done: reverse-PageRank prediction PARTIALLY confirmed (top words yes — large/body/small/water/plant/white all top 0.3%; ρ vs FVS degree-key = 0.316 not >0.6 because reverse-PR ≈ pure out-degree while FVS key sums out+in). Null models: degree alone recovers ρ≈0.68 of the real ranking → neither spectral nor combinatorial object adds much over degree (stated plainly). Added src/meanings/spectral_analysis.py, scripts/spectral_report.py, tests/test_spectral_analysis.py, conftest.py, reports/spectral-valuation-oewn.{md,json}. Repo had NO test suite before; now 7 tests pass (`uv run pytest`). Fixed one brittle test assertion (forward_vs_reverse order-equality → score-delta check) + tidied another.
Reconciled the psycholinguistic worktree into master (copied files over, removed worktree+branch). codex auto-committed 2 extra commits earlier (e15143e codex review, 85cd368 a "workstream-5 minset" report it generated) — harmless, left in place.
Wrote reports/swanson-synthesis.md (the master reconciliation doc — scoreboard, the spectral numbers, controllability divergence, ecology falsifier, yoneda verdict, money demotion, what changed in repo, 6 recommended next steps).
Updated .gitignore: added .claude/ and *.log.
Done — committed in 4 chunks (e6ce622 psycholinguistic data, d096051 spectral module+tests, ecb5147 findings+synthesis, 86b51a3 notes+gitignore), pushed. Working tree was clean.

### Round 2 (2026-05-12 cont.) — bio papers + Q's external deep-research
- Q: "do the bio shit / paper retriever/paper reader on that material" → launched 3 `claude` subagents (background) to retrieve+read the FVS-control biology papers via research-papers:paper-retriever then paper-reader (NO heavy propstore ingestion — repo uses light papers/<name>/notes.md convention): af484a41d34b47ca5 = Fiedler-Mochizuki "Dynamics and control at FVS I" (J Dyn Diff Eq 2013, paywalled Springer), ae3e93dab03e96465 = Mochizuki-Fiedler "...II" (J Theor Biol 2013, paywalled Elsevier), a647a0be4ff625a3c = Zañudo-Yang-Albert "Structure-based control of complex networks with nonlinear dynamics" (PNAS 2017, open access). All 3 told to update papers/index.md + list leads without chasing. Still running.
- Q dropped `C:\Users\Q\Downloads\swanson-money-numeraire-findings.md` = Q's own deep-research thread's output for the money/numéraire link, then said "copy that into the current directory at least under reports". Copied → `reports/swanson-money-numeraire-findings-deepresearch.md`. It's a strong independent twin of our `reports/swanson-money-numeraire-findings.md` — converges hard (same demotion of "MinSet=numéraire", same Sraffa-standard-commodity=PF-eigenvector move, same "Nixon shock line is loose", same proposed title) but adds: an actual publishable THEOREM (c(v)=g(v)/π_v over irreducible weighted Kernel; c-min FVS = "standard MinSet", canonical relative to stated standard not semantically ultimate) and a 4-experiment research agenda (weighted-MinSet frontier / Core fixed-point diagnostics / anchor-swap natural experiments / monetary-graph back-transfer).

Done: provenance header added, synthesis updated with the standard-MinSet theorem + convergence note, committed f356438 + pushed.

### Bio papers status
- DONE: Part II → papers/Mochizuki_2013_DynamicsControlFeedbackVertex/ (PDF via sci-hub.ru, notes.md 27KB). Faithful-monitor/determining-nodes theorem; case studies FVS 5/1/7.
- DONE: Part I → papers/Fiedler_2013_DynamicsControlFeedbackVertex/ (PDF via sci-hub.st, 42pp, notes.md 236 lines). Foundational FVS-control theorem; §8.3 cyclicity-set/Morse decomposition ≈ Rest/Kernel/Core/Satellites; only-if direction proved constructively. Caveat: decay/dissipativity assumption has no clean lexical analogue → for static-fixpoint reading use the combinatorial "informative set" def. Cross-refs wired between Parts I/II/Zañudo. index.md updated.
- STILL RUNNING: a647a0be4ff625a3c (Zañudo-Yang-Albert — agent created papers/Zañudo_2016_Structure-basedControlComplexNetworks/ i.e. the 2016 PLoS Comp Bio / arXiv 1605.08415 version, not PNAS 2017; other 2 agents already cross-ref it so the dir exists on disk).
- NONE committed yet — commit all 3 (or 4) papers/ dirs + index.md + cross-ref edits in one commit once Zañudo agent finishes.

### Round 3 (2026-05-12 cont.): "go go go make all fixes and improvements"
Q is ACTIVELY editing the repo in parallel — MinSet solver work (commits bfe7ae8/faa8a6d/f1543e6/c8b98dc/ee2a43b/e5724d8 + uncommitted cli.py change adding `exact-cutting` seed method). My commits interleave cleanly (different files). Be careful NOT to touch graph_analysis.py / cli.py / anything seed/MinSet-solver-related.

DECISION on compute_kernel self-loop "bug": NOT fixing it. Line 88 excludes self-loops (`target != node`) so a word appearing only in its own gloss gets peeled out of the Kernel. Whether self-loops belong in the Kernel is a SEMANTIC MODELING decision (1-node self-loop = forced FVS member by std defn, but the dict-graph papers may deliberately exclude gloss self-loops as parsing artifacts) — I haven't verified what Massé/V-L do, and Q is editing this exact area. Flagged to Q, left alone.

DONE this round so far:
- Committed bio papers (6a931a8, pushed).
- Cleaned up src/meanings/spectral_analysis.py: added SCCEigenvector dataclass (was returning list[dict[str,object]] → pyright noise + clunky indexing), updated call site + scripts/spectral_report.py + tests/test_spectral_analysis.py to use attrs not dict-keys, added to __all__, removed unused `deque` import, rewrote the confused half-corrected orientation docstring. `uv run pytest` → 10 passed.
- LAUNCHED 4 background agents: af242e58f214a5470 = psycholinguistic regressions (Yoneda/PF empirical legs → reports/psycholinguistic-regression-findings.md + scripts/psycholinguistic_regression.py); a78d96229295735d3 = paper Liu-Slotine-Barabási 2011 Nature "Controllability of complex networks"; af122daf195d41291 = paper Mochizuki-Saito 2010 "informative nodes" (J Theor Biol); a46ad51649a269e51 = paper Gates-Rocha 2016 Sci Rep "Control...requires both structure and dynamics". All told to stay out of src/.

### Next step
Commit the spectral_analysis cleanup. Wait for the 4 agents. Commit their outputs (papers/ additions; regression report+script). Fold regression results into reports/swanson-synthesis.md (Yoneda/PF sections — turn "blocked on data" into "result is X"). Summarize to Q. (compute_kernel: still flagged, not fixed — Q's call.)

### Note for future agents
The "research-papers" plugin skills are available here; `papers/` follows that convention (`notes.md`/`abstract.md`/`description.md`/`citations.md` per paper, `papers/index.md`). PDFs and PNGs are gitignored.
