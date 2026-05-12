# Core Mismatch Verdict

**Date:** 2026-05-12

## Question

Why does our paper-wordnet baseline report a Core of `288` nodes when Vincent-Lamarre reports WordNet Core `6,392`?

## Paper Constraint

The notes pin the target as:

- edge orientation: defining word -> defined word
- WordNet size: `132,477` word meanings
- WordNet Kernel: `9,802`
- WordNet Core: `6,392`
- WordNet Satellites: `3,410`
- preprocessing: first/common meaning per stemmed word/POS, content words only

The notes also expose a practical ambiguity:

- Picard summary language often describes Core as the largest SCC inside the Kernel.
- Vincent-Lamarre methodology language says the largest/source SCC is Core, and source SCCs define the C-hierarchy.

## Diagnostic Result

Diagnostics are in [core-mismatch-diagnostics.md](/C:/Users/Q/code/meanings/reports/core-mismatch-diagnostics.md).

For `paper-wordnet`:

- Kernel: `12,853`
- Source-SCC union: `288`
- Sink-SCC union: `1,276`
- Largest SCC: `8,138`
- Largest SCC indegree/outdegree: `907` / `14,168`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`

For the same kernel with reversed orientation:

- Source-SCC union: `1,276`
- Sink-SCC union: `288`
- Largest SCC: `8,138`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`

For the full graph with all edges reversed:

- Kernel explodes to `155,350` nodes.
- This is not a plausible reproduction of the paper pipeline.

## Verdict

This is not a simple edge-orientation bug.

If it were, reversing the same kernel would make the largest SCC become a source or sink SCC. It does not. Reversing the full graph also changes the kernel radically, which confirms that edge reversal is not the missing paper convention.

The most likely causes are:

- our representative `lemma::pos` mapping differs materially from the paper's "first and most common meaning per stemmatized part of speech"
- our OEWN 2024 resource has a different sense/lemma inventory than the WordNet version used in the paper
- our definition token mapping is too permissive or resolves definers differently
- the paper's operational Core may be closer to "largest SCC" in the reported tables than to "source-SCC union" in our current implementation

The strongest clue is quantitative:

- source-SCC Core: `288`, clearly not paper-like
- largest-SCC Core: `8,138`, much closer in scale to paper Core `6,392`

That does not prove largest-SCC is the correct definition, but it makes it the next thing to test explicitly.

## Next Correction

Add `core_policy` as an explicit analysis parameter:

- `source-union`: Core is the union of source SCCs inside Kernel.
- `largest-scc`: Core is the largest SCC inside Kernel.

Then generate comparison reports with both policies.

Do not silently replace one definition with the other. The right move is to make the ambiguity executable and compare it against paper reference values.

## Next Commands

After implementing `core_policy`:

```powershell
uv run python -m meanings.cli --graph-type paper-wordnet --core-policy source-union --seed-method exact-small-greedy --top 25
uv run python -m meanings.cli --graph-type paper-wordnet --core-policy largest-scc --seed-method exact-small-greedy --top 25 --report reports/oewn-paper-wordnet-largest-core-report.md --json reports/oewn-paper-wordnet-largest-core-summary.json
uv run python -m meanings.compare_reports --left reports/oewn-paper-wordnet-kernel-summary.json --right reports/oewn-paper-wordnet-largest-core-summary.json --output reports/oewn-core-policy-comparison.md
```

