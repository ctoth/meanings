# Abstract

## Original Text (Verbatim)

We present a time `O(1.7548^n)` algorithm finding a minimum feedback vertex set in an undirected graph on `n` vertices. We also prove that a graph on `n` vertices can contain at most `1.8638^n` minimal feedback vertex sets and that there exist graphs having `105^{n/10} ≈ 1.5926^n` minimal feedback vertex sets.

---

## Our Interpretation

This is a pure algorithms paper, but it matters directly to the kernel project because it sharpens what it means to compute or enumerate minimum cycle-breaking seeds. The most important takeaway is not only the runtime bound; it is that minimal feedback vertex sets can be numerous, which matches the dictionary result that there are many valid `MinSets`, not one uniquely privileged core.
