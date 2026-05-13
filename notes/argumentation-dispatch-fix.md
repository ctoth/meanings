# argumentation_dispatch.py finding-1 fix (2026-05-12)

## What was wrong
`dispatch_stable` greedy topological sweep picks ONE stable ext per SCC; if a downstream SCC is
UNSAT under that greedy upstream choice it clamped `stable_exists=False`, `exact_count=0`,
`witness=None` — never running the correct DAG-DP. Wrong on context-dependent graphs (audit case:
a<->b, x->y->z->x, b->x; monolithic SAT {b,y}, dispatcher said False).

## Fix (hybrid: option-1 DAG-DP + option-2 monolithic fallback)
- Greedy sweep now sets `greedy_concluded_sat=False` instead of clamping when it hits a
  UNSAT-in-context SCC.
- Corrective exact pass: if all SCCs <= _BRUTE_FORCE_MAX (12) -> `_exact_stable_search` (new:
  witness-producing DAG-DP over condensation); else -> monolithic `find_stable_extension` on whole AF.
- `structural_minset_count` -> None after a short-circuit (downstream forced-OUT contexts stale).
- `credulous_accepts`/`skeptical_accepts` rewritten: `stable_exists` fast check, then monolithic
  z3 `require_in`/`require_out` (SCC-local check was unsound — cross-SCC question).
- Contract documented: dispatch_stable is exact; fast when greedy concludes, falls back to
  monolithic z3 otherwise.

## Verified
- `scratch/test_stable_exists.py`: case 1 now stable_exists=True, exact_count=1, witness={b,y}.
- 9-case battery (context-dependent, genuinely-UNSAT, chained-context, DAG, even cycle): all
  stable_exists/witness/credulous/skeptical match monolithic af_sat. "ALL OK".
- `uv run pytest -q`: 102 passed (lexicality failures the task warned about not present now).

## Done
- reports/argumentation-dispatch-oewn.md Caveats rewritten + re-confirmation section added.
- tests/test_argumentation_dispatch.py: 5 new context-dependent regression tests; 29 pass.

## OEWN re-confirm: DONE (it just took 188s; tee log only flushed at end)
- nodes=160010 edges=677823, kernel_nodes=18151.
- FIXED dispatch_stable(Kernel): stable_exists=False, exact_count=0 (greedy short-circuits,
  giant SCC too large to enumerate -> monolithic z3 fallback -> UNSAT). Still UNSAT.
- Fresh monolithic z3 find_stable_extension on whole 18,151-node Kernel attack-AF
  (kernel_attack_framework) -> UNSAT (7.6s). Re-verifies the bridge claim from scratch.
- Log: scratch/reconfirm_oewn_kernel.log. Final pytest: 107 passed.
