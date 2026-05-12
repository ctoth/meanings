# Argumentation semantics over the full OEWN definition graph

**Date:** 2026-05-12
**Inputs:** `src/meanings/argumentation_bridge.py`, `scripts/argumentation_bridge_oewn.py`,
`reports/argumentation-bridge-oewn.json` (raw numbers), the sibling library
`formal-argumentation` (pinned to commit `8d28624` of `github.com/ctoth/argumentation`).
**Question:** can the formal-argumentation library's semantics run on the whole ~160k-node
`paper-wordnet` OEWN definition digraph, and how do they line up with this repo's
leaf-stripping Kernel decomposition?

## TL;DR

* **Polynomial semantics: yes, but not via the library.** The grounded extension is
  trivial to compute at this scale — *if you compute it yourself*. A standard linear
  worklist labelling does it in **0.8 s** on 160 010 nodes / 677 823 edges. The library's
  `argumentation.dung.grounded_extension` does **not** scale here: its `defends()` re-scans
  the growing accepted set, making it super-quadratic in the extension size; it burned
  >200 s CPU on the full graph still inside its first iterations and was killed. It *does*
  finish on the 18 151-node Kernel subgraph (2.5 s). So: the algorithm is trivial, the
  library's implementation is not — a thin scaling layer (or a labelling-based reimpl) is
  the missing piece.
* **The grounded extension is not the Kernel decomposition, under either edge reading,
  and that's the expected answer.** Under the *attack* reading (`u→v` = "u attacks v") the
  grounded extension has **5 043 nodes (3.15 %)** — 4 575 of them in the acyclic *Rest*,
  468 inside the Kernel. It is an IN/OUT/UNDEC *labelling* of the graph, not a "which nodes
  survive leaf-stripping" set: 137 284 of the 141 859 Rest nodes are OUT (attacked), and
  `grounded ∪ Rest` is exactly "all nodes minus the 17 683 Kernel nodes left UNDEC". Under
  the *support* reading (`u→v` = "u supports v", the more honest reading) the bipolar AF has
  an empty defeat relation, so its grounded extension is the whole 160 010-node argument set
  — analytically, and the library can't even compute it (its `defends()` recomputes the
  Cayrol defeat closure once per argument).
* **Stable semantics on the Kernel: feasible per-SCC, infeasible whole, and the answer is
  "no stable extension exists".** z3 (via `argumentation.af_sat.find_stable_extension`)
  decides the whole 18 151-node Kernel AF as **UNSAT in 8 s**, and its largest SCC (8 138
  nodes) as **UNSAT in 3.3 s**. Of the ~693 non-singleton Kernel SCCs, 630 are SAT (have a
  stable extension) and 63 are UNSAT (odd cycles). Because the big core SCC and 63 others
  are UNSAT, the Kernel as a whole has **no stable extension at all** — so the repo's
  `seed`/MinSet does **not** correspond to "the outsiders of a stable extension"; there is
  no stable extension whose outsider set could be the MinSet.
* **Verdict: feasible today for grounded; feasible-with-a-divide-and-conquer-layer for the
  rest; the library is the bottleneck, not the maths.** Nothing here is blocked on a hard
  SCC; the blockers are all implementation (the library's quadratic `defends`, no SCC
  decomposition front-end). z3 sails through the 8k-node core. The natural next module is
  exactly the SCC + backdoor + z3 divide-and-conquer front-end the connection report
  sketched.

## Encoding decisions

A `meanings` definition digraph is an `Adjacency` mapping `u → {v, …}`, edge `u → v`
meaning "the word `u` occurs in the definition (gloss) of `v`". `meanings.argumentation_bridge`
gives two readings:

* `dung_attack_framework(nodes, adjacency)` → `argumentation.dung.ArgumentationFramework`
  with `defeats` = the edge set, **attack reading**: `u → v` ⇒ "u attacks v". Self-loops
  (`u → u`, a word in its own gloss) become legal self-attacks (such a node is never IN).
  This is the reading under which "grounded extension" is a non-trivial object.
* `bipolar_support_framework(nodes, adjacency)` → `argumentation.bipolar.BipolarArgumentationFramework`
  with `supports` = the edge set and `defeats` empty, **support reading**: `u → v` ⇒
  "u supports v" — the honest reading of a definition ("you cannot accept `v` until you
  accept its definiens"). The attacks that a richer model would carry — polysemy,
  prototype exceptions — are exactly what the `paper-wordnet` build discards by collapsing
  to `lemma::pos`, so `defeats` is empty here by construction.
* `kernel_attack_framework(analysis, adjacency)` / `scc_attack_framework(scc, adjacency)`
  restrict the attack-reading AF to the leaf-stripped Kernel, or to one SCC's induced
  subgraph (for the per-SCC stable probe). All graph work (SCC, kernel, induced subgraph)
  is reused from `meanings.graph_analysis` / `meanings.minset`; nothing is reimplemented.

The script (`scripts/argumentation_bridge_oewn.py`) additionally carries a
`grounded_extension_fast` (standard linear worklist labelling) used for the full-graph
grounded computation, with an in-script assertion that it agrees with
`argumentation.dung.grounded_extension` on small graphs. It is experiment-only and
deliberately *not* in the reusable module.

## The graph and the leaf-stripping decomposition (baseline)

`build_paper_wordnet_graph("oewn:2024")`, then `analyze_kernel`:

| quantity | value |
|---|---|
| nodes | 160 010 |
| edges | 677 823 |
| Rest = nodes − Kernel | 141 859 |
| Kernel (leaf-stripped) | 18 151 |
| — Core (union of source SCCs) | 510 |
| — Satellites (Kernel − Core) | 17 641 |
| Kernel SCC count | 9 139 (8 446 singletons — of which 2 804 are self-loops, i.e. a word in its own gloss, and 5 642 plain singletons; ~693 non-singleton SCCs, one giant of 8 138) |
| `seed` / MinSet (bounded-scc heuristic) | 3 620 |
| residual cyclic SCCs after heuristic | 1 (layering therefore skipped) |
| graph build | ~83–93 s | `analyze_kernel` | ~2 s |

(This is the post-self-loop-fix Kernel size, 18 151.)

## Grounded extension — sizes, timing, alignment with the Kernel

### Attack reading (`u → v` = "u attacks v"), full 160 010-node graph

* AF construction: **0.83 s** (160 010 args, 677 823 defeats).
* Grounded extension via the fast linear labelling: **|grounded| = 5 043** (3.15 % of
  nodes), **0.81 s**.
* `argumentation.dung.grounded_extension` on the full graph: **did not finish** — >200 s CPU
  and killed, still inside its early iterations. Bottleneck: `dung.defends()` does
  `any((d, attacker) in defeats for d in s)` for every argument and every attacker, i.e. a
  linear scan of the growing accepted set `s`; on a 160k graph that is super-quadratic.
* Same library function on the 18 151-node **Kernel subgraph**: **completes, 468 IN nodes,
  2.5 s** (the fast labelling gives the same 468 in 0.05 s). So the library's grounded is
  usable up to ~20k nodes here but not at 160k.

How the 5 043-node grounded extension sits against the `{Rest, Kernel, Core, Satellites, seed}`
partition (Jaccard / overlap, "only-A" = in grounded not in the set, "only-B" = the reverse):

| set B | \|B\| | grounded ∩ B | Jaccard | only-grounded | only-B |
|---|---:|---:|---:|---:|---:|
| Rest (acyclic shell) | 141 859 | 4 575 | 0.032 | 468 | 137 284 |
| Kernel | 18 151 | 468 | 0.021 | 4 575 | 17 683 |
| Core | 510 | 326 | 0.062 | 4 717 | 184 |
| Satellites | 17 641 | 142 | 0.006 | 4 901 | 17 499 |
| seed / MinSet | 3 620 | 2 | 0.0002 | 5 041 | 3 618 |
| **Rest ∪ grounded** | — (142 327) | — | **0.889** vs all nodes | 0 | 17 683 |

**Reading:** the grounded extension is *not* "Rest" and *not* any clean piece of the Kernel.
4 575 of its 5 043 nodes lie in the acyclic Rest; 468 lie inside the Kernel (a tiny
acyclic-from-outside fringe of the Kernel that the attack labelling resolves to IN). The
last row is the cleanest statement: `grounded ∪ Rest` covers every node except the **17 683
Kernel nodes left UNDEC** (= 18 151 − 468). So the *determinate* part under the attack
reading is "the acyclic Rest, IN/OUT-labelled, plus the 468 forced Kernel nodes", and the
*undetermined* part is "almost the whole Kernel". That is a *different* decomposition from
leaf-stripping: leaf-stripping says "141 859 nodes are acyclically reducible (Rest)";
grounded labelling says "of those 141 859, only ~5 % (4 575) end up IN; the rest are OUT —
attacked by something IN — and a further 468 Kernel nodes are also forced IN". The two
agree on *which nodes are touched at all* (Rest ∪ 468), they disagree on the *verdict per
node*. `seed`/MinSet and the grounded extension are essentially disjoint (overlap 2) — a
feedback-vertex-set member is a node you'd ground from *outside*; the grounded extension is
what the graph forces *from inside* with no outside input, so there is no reason for them to
coincide and they don't.

*Why they don't coincide (the conceptual point).* Under the attack reading, "in the
grounded extension" means "every word in my gloss is OUT, recursively from the unattacked
up". That is an alternating-layer labelling of the acyclic shell, not the shell itself.
Under the support reading, "grounded" in the Cayrol/Dung sense means "defended against
set-defeat" — and with no defeats *everything* is vacuously defended, so the grounded
extension is the whole vocabulary and says nothing. The honest "you can't accept a word
until you accept its definiens" closure — the thing that would actually mirror leaf-stripping
on the support side — is **not** what plain bipolar AF grounded semantics computes; it is a
downward-closure under definiens, and the library has no operator for it. (The repo's own
`compute_kernel` is the closest existing thing, in the opposite direction.)

### Support reading (`u → v` = "u supports v"), full graph

* BAF construction: **0.78 s** (160 010 args, 677 823 supports, 0 defeats).
* Grounded extension: **160 010 = all nodes** (1.00), by construction — empty defeat
  relation ⇒ empty Cayrol defeat closure ⇒ every argument vacuously defended ⇒ grounded =
  everything. Computed analytically; `argumentation.bipolar.bipolar_grounded_extension`
  cannot do it at scale (it recomputes `_defeat_closure(defeats, supports)` once per
  argument, ~160k recomputations over 677k support edges — does not finish; verified
  against a tiny graph instead).

So the plain bipolar grounded extension is a *non-finding* at this scale: it is trivially
the whole graph. The interesting support-side structure lives in the leaf-stripping the
repo already does, or in semantics the library does not implement.

## Stable-extension probe (z3)

`argumentation.af_sat.find_stable_extension` (z3 backend), attack reading:

* **Whole Kernel subgraph** (18 151 nodes, 73 654 edges): **UNSAT in 8.1 s** — the Kernel
  AF has *no* stable extension.
* **Largest Kernel SCC** (8 138 nodes — the giant cyclic core): **UNSAT in 3.3 s.**
* Of the **~693 non-singleton Kernel SCCs**: **630 SAT** (a stable extension exists),
  **63 UNSAT** (odd-cycle SCCs). All SCC checks were sub-millisecond except the 8 138-node
  one (3.3 s). The 8 446 singleton SCCs were not z3-probed: 5 642 are plain singletons (not
  cyclic) and 2 804 are self-loops (cyclic but trivially have no stable extension and are
  never IN in any extension). Cumulative z3 time for all non-singleton per-SCC probes: ~4 s.
* **No SCC choked** — z3 decided every one, including the 8k-node core, in seconds.

**Relation to `seed`/MinSet.** Because the whole Kernel is UNSAT (the 8 138-node core plus
63 small SCCs have no stable extension), there is *no* stable extension of the Kernel, hence
no "outsider set of a stable extension" to compare the 3 620-node MinSet against. The
correspondence "MinSet ↔ stable-extension outsiders" that holds for nice (e.g. bipartite /
even-cycle) graphs does **not** hold here: odd cycles in the Kernel kill stable existence.
The well-defined sceptical object on the Kernel is the grounded extension (468 IN, ~17 683
UNDEC) — and that, as shown above, is not the MinSet either. (If one wanted a per-SCC
MinSet ↔ stable comparison, the 630 SAT SCCs are where it could be done; the 63 UNSAT ones
are where it provably can't.)

Full-graph stable was not attempted as a single z3 call: the full AF has 160 010 args /
677 823 attacks and contains the same UNSAT odd-cycle SCCs, so it is necessarily UNSAT and a
monolithic SAT call would be wasteful; the per-SCC decomposition already answers it (UNSAT,
witnessed by any of the 63 UNSAT SCCs).

## Verdict

| computation | feasible on full 160k OEWN graph? |
|---|---|
| **grounded extension** | **Yes, trivially** (0.8 s) — but with a labelling algorithm, *not* `argumentation.dung.grounded_extension`, which is super-quadratic in extension size and does not finish. |
| **bipolar/support grounded** | Trivially = all nodes (analytic). Library impl does not scale (per-argument closure recomputation). |
| **stable existence** | **Yes, with divide-and-conquer**: decompose into SCCs, z3-decide each; the whole graph is UNSAT, witnessed cheaply by odd-cycle SCCs. z3 handled the 8k-node core in 3.3 s. A monolithic z3 call on 160k args was not run (unnecessary). |
| **preferred / semi-stable / ideal / enumerate-all-stable** | Not attempted. The library's enumerators are brute-force over subsets — hopeless monolithically; would need the same SCC + SAT decomposition, and per-SCC enumeration is plausible (SCCs are tiny except the 8k core, and the core is UNSAT for stable so "enumerate all stable" is trivially empty there). |

Nothing is **blocked on a hard SCC**: the one large SCC (8 138 nodes) is decided by z3 in
seconds. The blockers are all *library implementation* — `dung.grounded_extension`'s
quadratic `defends`, `bipolar.*`'s per-call closure recomputation, the lack of any SCC /
condensation front-end. So: **"argumentation semantics over the full OEWN graph" is feasible
today for grounded (with our own linear pass), and feasible-with-a-thin-divide-and-conquer-
layer for stable and probably for preferred — provided that layer (a) decomposes into SCCs
using `meanings.graph_analysis` and (b) hands each SCC to z3 / a labelling routine rather
than to the library's brute-force monolithic functions.**

## Next module

The natural follow-on is the **SCC + feedback-vertex-set-backdoor + z3 divide-and-conquer
front-end** the connection report sketched, made concrete by these numbers:

1. **Condense.** Use `meanings.graph_analysis.strongly_connected_components` to get the
   condensation DAG. Acyclic part (the 141 859 Rest nodes + the 5 642 plain-singleton Kernel
   SCCs) gets the linear grounded/preferred labelling directly — no SAT needed, ~0.8 s; the
   2 804 self-loop singletons are trivially OUT-or-UNDEC.
2. **Per-SCC SAT only where it matters.** For each non-singleton SCC (here ~693, with one
   8 138-node giant and the rest ≤ 11 nodes), build `scc_attack_framework` and call
   `argumentation.af_sat` (z3) for stable / `find_preferred_extension` etc. Cache by SCC
   isomorphism class — many of the tiny SCCs are structurally identical (2-cycles, etc.).
3. **Backdoor for the giant SCC.** The 8 138-node core is the only one where a single SAT
   call is non-instant (3.3 s) and where enumeration would explode; use the repo's MinSet /
   feedback-vertex-set machinery as a *backdoor* — fix the ≤ few-hundred FVS nodes' labels,
   the residual is acyclic, enumerate over the backdoor assignments. (Vincent-Lamarre's
   MinSet is exactly the backdoor; this is the FVS ⇔ enforcement-set theorem made
   operational.)
4. **Stitch.** Combine per-SCC results bottom-up along the condensation DAG (grounded is
   compositional; stable existence is the conjunction; preferred needs a cross-SCC pass).
5. **Replace, don't wrap.** Either upstream a labelling-based `grounded_extension` and an
   SCC-aware dispatcher into `argumentation`, or keep this front-end in `meanings` as the
   "scale layer the library lacks" — the connection report's framing — and treat the
   library as the per-SCC oracle.

## Hygiene notes

* `formal-argumentation` is added to `pyproject.toml` as
  `formal-argumentation @ git+https://github.com/ctoth/argumentation@8d28624` — **pinned to a
  specific commit**; this is an experiment-only choice and should be re-pinned (to a tag /
  PyPI release) or dropped if the bridge doesn't graduate. `z3-solver` was added as a direct
  dependency (for the stable probe) and `pytest` as a dev dependency (the project venv had no
  pytest, which meant `uv run pytest` was silently using an unrelated external interpreter
  that can't see the venv's site-packages — so the new `argumentation`-importing test
  couldn't run there).
* New files only: `src/meanings/argumentation_bridge.py`, `scripts/argumentation_bridge_oewn.py`,
  `tests/test_argumentation_bridge.py`, `reports/argumentation-bridge-oewn.{json,md}`,
  `reports/argumentation-bridge-oewn.run.log`, `notes/argumentation-bridge.md`. No edits to
  `minset.py`, `graph_analysis.py`, `cli.py`, or `workstreams/`. `uv run pytest`: 15 on a
  clean checkout, 24 now — the 4 added here are `tests/test_argumentation_bridge.py` (chain,
  2-cycle, self-loop, support edges); the remaining increase is concurrent work, not this
  change. No regressions from this change.
