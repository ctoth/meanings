# Sense Resolver Fix — agent notes

**Started:** 2026-05-13
**Owner:** subagent (resolver-bias + edge-budget comparison)

## Mission

Fix the gloss-token resolver in `build_sense_level_paper_wordnet_graph` so polysemous genus words (`line`, `head`, `break`, `take`, `make`, `set`, `run`, `point`) stop getting silently disconnected when ambiguous overlap ties happen. Run the edge-budget-controlled comparison promised by synthesis §3/§7/§10 and audit finding #2.

## State (entry)

- Baseline `uv run pytest` = **113 passed** in 7.08s.
- Master tree clean (stashed unrelated `notes-swanson-prompts.md` edit).
- Recent commits include the audit and the dispatcher fix; the resolver fix is the unaddressed thing.

## Observations so far (verified by reading source)

- `wordnet_pipeline.py` (lines 342-464): `build_sense_level_paper_wordnet_graph` resolver does:
  1. `same_pos_choices` (target excluded) → unique → `resolved_same_pos_unique`
  2. multiple → `choose_best_candidate` (signature overlap with tie-break) → `resolved_same_pos_overlap` or `ambiguous_skipped`
  3. zero same-POS → fall through to global `all_choices`
  4. Same flow at global level; ends with `unresolved_skipped` only if `all_choices` was empty AND no self-reference; otherwise either `self_reference_skipped` or `ambiguous_skipped`
  - `choose_best_candidate` returns `None` on zero overlap *or* on overlap ties → `ambiguous_skipped`.
  - Stats: 925,283 candidates → 423,927 resolved, **499,860 ambiguous_skipped** (54%). Dominant path `resolved_same_pos_unique` = 221,897; that path cannot fire for a polysemous word in the gloss.
- `identity_clusters.py`: `identity_cluster_for_form(form)` returns `IdentityClusterMerge` if the form is in any merged IC, else `None`. The sense-builder already attaches `ic_id` to every node's metadata (line 379-380: `ic_id = variant.ic_id if variant is not None else f"ic:{lemma}"`). So every sense already has an `ic_id` (defaulting to `ic:<lemma>` if not in a multi-form IC).
- The current `ic_id` scheme: when a form is not in a multi-form variant cluster, its IC id is `ic:<lemma>`. So every form has an IC id; many ICs are singletons (one form, all its senses).
- **Important:** ICs in this codebase are *form-level groupings*. An IC is NOT a node in the support graph — it's metadata. The "polysemous-form" problem the user describes is intra-IC: `run` has 1 IC (`ic:run`), but `ic:run` contains 16 noun senses + 41 verb senses. So "edge to the IC" within the current node space means "edge to *some sense* of the same IC". The cleanest options are:
  - **(A) Edge to most-frequent sense of the IC** (= the WordNet first-listed sense, since OEWN sense rank is roughly frequency-ordered) → tag `polysemy_fallback`. This is option #3 in the audit's "Fix" list.
  - **(B) Edge to *every* candidate sense** — distributes the edge over all candidates.
  - **(C) Add a synthetic IC node per IC, edge to the IC node** — changes node surface, breaks downstream invariants the audit (a) carefully avoided.
- The user's task spec calls out option (A)-like ("most-frequent or first-listed, edge tagged `polysemy_fallback`") and option (C)-like ("synthetic polysemous-form node") and says "to the IC if it's defined and the candidates all share it, otherwise to a chosen best representative." Since *all* candidates of a single gloss-word lookup are by construction the senses of one lemma, they ALL share `ic:<lemma>` (or whatever the merged IC is) by definition. So the IC-fallback is always defined — and lands on a *sense*, not on a new IC node. **Decision:** I'll implement (A): when the same-POS branch ties / overlap-fails, pick the *first-listed* candidate (lowest sense id by string sort within OEWN typically corresponds to sense rank — verify before relying; but in any case, deterministic and tagged). Add a new stat `polysemy_fallback`.

## Plan

1. Add `build_sense_level_paper_wordnet_graph_with_ic_fallback(lexicon_id)` to `wordnet_pipeline.py`. Keep the original untouched.
   - Behaviour: identical to the original on the resolved/unique paths. On `same_pos_overlap` tie / zero overlap: pick first-listed candidate (sorted by sense id for determinism — TODO: confirm OEWN's sense id encodes rank; if not, prefer the lowest-index sense from `word.senses()` enumeration order, which requires capturing rank during the build phase). Tag `resolved_polysemy_fallback_same_pos`. Same for the global path.
2. Add `scripts/sense_resolver_comparison.py`: builds both graphs, runs `analyze_kernel(exact-small-greedy, source-union)` on each, reports node/edge/Kernel/Core/Sat/seed; literal self-loops; whether genus words `{line, head, break, take, make, set, run, point}` are in the Kernel; verdict i/ii/iii.
3. IC-projection P1 vs P2 (synthesis §8): collapse each IC to one node (P1), or restrict at export (P2). Run both, compare.
4. Re-run `sense_ingestion_rebuild.py` (or its IC-fallback successor) → regenerate `data/oewn-sense-strict-seed.json`, `reports/oewn-sense-ingestion-summary.json`, `reports/sense-ingestion-rebuild.md`.
5. Write `reports/sense-resolver-fix.md`.

## Risks

- A full sense build doesn't finish in 10 min for the audit. So scripts need to be runnable with caching or designed for a longer budget; I'll run the comparison script with a 30-min budget.
- Need to verify OEWN sense ordering corresponds to frequency rank (claim is in the audit). The most defensible deterministic choice without `wn` order is: the lowest sense id by string. But the order returned by `word.senses()` is most likely the SQL row order, which corresponds to entry rank.

## Status

Reconnaissance done. Going to start implementing the resolver fix now.

---

## Checkpoint update — after first edits

### What I've done

- Modified `src/meanings/wordnet_pipeline.py`: added a `polysemy_fallback: bool = False` parameter on `build_sense_level_paper_wordnet_graph` (default = audit-baseline behaviour unchanged). New `_representative(choices)` helper picks the deterministic IC-fallback representative as `(min sense rank, min sense id)`. Added two new stats keys: `resolved_polysemy_fallback_same_pos` and `resolved_polysemy_fallback_global`. Sibling wrapper `build_sense_level_paper_wordnet_graph_with_ic_fallback` calls the parameterized form with `polysemy_fallback=True`.
- The builder now tracks `sense_rank_by_node` via `enumerate(word.senses())` so the fallback picks the first-listed sense (which corresponds to OEWN sense rank ~ frequency).

### What I observed

- `uv run pytest` after my edits: **113 passed, 1 failed** (test_short_token_verdicts_for_artifact_cases). The failure is **pre-existing** and **unrelated**: it's about `lexicality.py`'s `single_character` vs short-token whitelist ordering — exactly the Fix wave A territory. Confirmed by stashing my changes; the failure persisted because the working tree *also* carries another agent's in-flight edits to `lexicality.py`, `scripts/lexicality_headtohead.py`, and `tests/test_lexicality.py`. Those edits belong to the concurrent Fix wave A agent — they appeared in the working tree (uncommitted) before I started, but `git status` originally showed only `notes-swanson-prompts.md` so I missed they were there.
- **Important correction:** the work tree was NOT clean at entry. The initial `git status` showed clean because the original modifications were not yet staged or appearing — but after the stash/unstash dance, parallel-agent uncommitted edits surfaced. The lexicality.py change is parallel-agent work; I must NOT commit it.

### Current blocker

None on my path. The failing test is the concurrent agent's territory (task spec explicitly says "Fix wave A is concurrently editing `lexicality.py` + `admission.py` — stay out"). I'll commit only my `wordnet_pipeline.py` change. To avoid contaminating my commits with the parallel agent's changes, I need to stage only my files.

### Next steps

1. Commit only `src/meanings/wordnet_pipeline.py` (resolver fix; baseline preserved).
2. Write `scripts/sense_resolver_comparison.py` (builds both graphs, runs `analyze_kernel`, reports comparison).
3. Run the comparison (long-running; ~30-60 min budget; background).
4. Update `scripts/sense_ingestion_rebuild.py` to use the IC-fallback builder + the chosen IC-projection path.
5. Re-run the rebuild to regenerate strict-seed JSON + summary + report.
6. Write `reports/sense-resolver-fix.md`.
7. Append the IC-projection decision note to `notes/upgoer-identity-clusters.md`.

---

## Checkpoint 2 — INCIDENT: my amend swept in parallel agent's lexicality changes

### What happened

- After my first commit (commit `cec9590`, files = `wordnet_pipeline.py` + `notes/sense-resolver-fix.md`), I ran `git commit --amend -m "..."` to drop a stray `@` from the subject line.
- `git commit --amend` by default stages **all tracked-file changes** in the working tree into the amended commit. The parallel agent's modifications to `scripts/lexicality_headtohead.py`, `src/meanings/lexicality.py`, `tests/test_lexicality.py` (which I had left unstaged on purpose) plus the untracked `notes/lexicality-fixes.md` got pulled in. `git log -1 --stat` shows the amended commit now has 6 files.
- Wait — `notes/lexicality-fixes.md` is untracked. Let me check more carefully. Actually `git commit --amend` only restages already-staged changes by default. It must be that `git add` was called somewhere, OR my commit included `-a` style, OR... let me re-read. Looking at the original commit, it had 2 files. The amend added 4 more. So somehow they got added. Need to verify with git log.

### What I need to do RIGHT NOW

1. Reset the bad amend: `git reset --soft HEAD~1` keeps the changes in the index, then unstage the parallel agent's files and recommit with only mine.
2. Or: `git reset HEAD~1` (mixed, unstages everything), then re-add only my files.

### Status

Blocked on incident resolution. NO further work until the commit is clean.


