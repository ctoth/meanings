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
Remaining: stage + commit everything in logical chunks, push, tell Q. Then DONE. (compute_kernel self-loop bug = separate future fix, noted in synthesis §3.)

### Note for future agents
The "research-papers" plugin skills are available here; `papers/` follows that convention (`notes.md`/`abstract.md`/`description.md`/`citations.md` per paper, `papers/index.md`). PDFs and PNGs are gitignored.
