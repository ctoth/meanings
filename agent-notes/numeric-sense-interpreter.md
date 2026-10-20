# Numeric sense interpreter

## Goal

Implement Q's approved bounded numeric interpreter, run its focused tests and
experiment, and push tested commits directly to the verified default `master`.
No PR, physical acquisition, parser, or changes to the dependency-graph pipeline.

## State

Isolated clone based on remote `master` c80f9a5. Original checkout at
`C:/Users/Q/code/meanings` has unpublished history through e0062ab and pre-existing
dirty/untracked files; leave all of it untouched. Remote is
`git@github.com:ctoth/meanings.git`; SSH network access was approved after the
sandbox blocked the first read-only probe.

Implemented explicit AST/evaluation, five source records, numeric runner and
focused tests. Focused pytest: 21 passed in 0.76s. Experiment exact-reference check
passed: held-out 9,900 judgments, correct 0 errors, wrong binding 5,940 errors,
operator erasure 2,970 errors; no unknown judgments in any complete-fixture arm.
Independent read-only database comparison: 5/5 source records matched exactly.
Reports retain the captured JSON and explain the authored-interpretation limit.

## Decisions and why

Smallest change: about 200-300 source lines for an explicit sense-keyed expression
evaluator and numeric runner, plus five source records, focused tests and a report.
Reuse `admission.SenseRecord`; keep source glosses separate from manually authored
interpretations. Use exact integer references, development -10..10 and held-out
-1000..-11 / 11..1000, wrong primitive bindings and erased operators. These are
engineering controls, not an empirical claim of intrinsic grounding.

## Surprises

Remote master predates local campaign documentation. Building on remote master
avoids publishing unrelated, unverified local commits with this experiment.

## Next step

Inspect intended files and captured results, commit them, integrate into a fresh
remote master and push without force. Verify the remote commit. Do not push the
original checkout's unpublished campaign history or modify its dirty files.
