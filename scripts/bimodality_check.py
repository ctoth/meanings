"""Bimodality check on OEWN paper-wordnet definitional graph.

Hanski occupancy analogue = out-degree of a node u in G (u -> v means u occurs in
definition of v), i.e. the number of definitions u appears in as a definer.
Also reports in-degree, total degree, and the kernel-restricted out-degree.
Tests for bimodality: Hartigan dip test (if available), Gaussian-mixture BIC
(1 vs 2 components) on log10(1+degree), and simple histogram peaks.
"""
from __future__ import annotations
import json, math, statistics
from collections import Counter
from meanings.wordnet_pipeline import build_paper_wordnet_graph
from meanings.graph_analysis import analyze_kernel

b = build_paper_wordnet_graph("oewn:2024")
adj = b.adjacency  # dict: node -> iterable of successors
nodes = list(b.nodes)
N = len(nodes)

# out-degree (exclude self loops)
outdeg = {}
indeg = Counter()
for u in nodes:
    succ = [v for v in adj.get(u, ()) if v != u]
    outdeg[u] = len(succ)
    for v in succ:
        indeg[v] += 1
indeg = {u: indeg.get(u, 0) for u in nodes}
totdeg = {u: outdeg[u] + indeg[u] for u in nodes}

def summarize(name, dvals):
    vals = list(dvals.values())
    vals_sorted = sorted(vals)
    n = len(vals)
    nz = [v for v in vals if v > 0]
    print(f"\n=== {name} ===")
    print(f"  n={n}  zeros={n-len(nz)} ({100*(n-len(nz))/n:.1f}%)  max={max(vals)}  mean={statistics.mean(vals):.3f}  median={statistics.median(vals)}")
    # quantiles
    for q in (0.5,0.9,0.99,0.999):
        print(f"  q{q}={vals_sorted[min(n-1,int(q*n))]}")
    # histogram on small values
    c = Counter(vals)
    print("  count by degree (0..15):", {k: c.get(k,0) for k in range(16)})

for name, d in [("OUT-DEGREE (occupancy analogue: # definitions word appears in)", outdeg),
                ("IN-DEGREE (# definer-words in this word's definition)", indeg),
                ("TOTAL DEGREE", totdeg)]:
    summarize(name, d)

# kernel restricted
ka = analyze_kernel(adj, seed_method="exact-small-greedy", core_policy="source-union")
kernel = set(ka.kernel_nodes)
core = set(ka.core_nodes)
sats = kernel - core
print(f"\nkernel size={len(kernel)} core={len(core)} satellites={len(sats)}")

# out-degree within kernel subgraph
kern_outdeg = {}
for u in kernel:
    kern_outdeg[u] = len([v for v in adj.get(u,()) if v in kernel and v != u])
summarize("KERNEL-INTERNAL OUT-DEGREE (all kernel nodes)", kern_outdeg)

# global out-degree split by membership
def stats_of(label, members, dsrc):
    vv = [dsrc[u] for u in members]
    if not vv:
        print(f"  {label}: empty"); return
    print(f"  {label}: n={len(vv)} mean={statistics.mean(vv):.2f} median={statistics.median(vv)} max={max(vv)}")
print("\nGlobal out-degree by layer membership:")
stats_of("CORE", core, outdeg)
stats_of("SATELLITE", sats, outdeg)
rest = set(nodes) - kernel
stats_of("REST (non-kernel)", rest, outdeg)

# --- bimodality tests on log10(1+outdeg), nonzero only ---
import numpy as np
x = np.array([math.log10(1+v) for v in outdeg.values() if v > 0], dtype=float)
print(f"\nlog10(1+outdeg), nonzero: n={len(x)} min={x.min():.3f} max={x.max():.3f} mean={x.mean():.3f}")

# Gaussian mixture BIC
try:
    from sklearn.mixture import GaussianMixture
    Xr = x.reshape(-1,1)
    for k in (1,2,3):
        gm = GaussianMixture(n_components=k, n_init=3, random_state=0).fit(Xr)
        print(f"  GMM k={k}: BIC={gm.bic(Xr):.1f}  means={sorted(gm.means_.flatten().round(3))}  weights={gm.weights_.round(3)}")
except Exception as e:
    print("  sklearn GMM unavailable:", e)

# Hartigan dip test
try:
    import diptest
    d, pval = diptest.diptest(x)
    print(f"  Hartigan dip test on log10(1+outdeg): dip={d:.5f} p={pval:.4f}  (p<0.05 => reject unimodality)")
except Exception as e:
    print("  diptest unavailable:", e)

# also dip on the kernel-internal out-degree (nonzero)
xk = np.array([v for v in kern_outdeg.values()], dtype=float)
print(f"\nkernel-internal outdeg: n={len(xk)} mean={xk.mean():.2f} max={xk.max():.0f}")
try:
    import diptest
    d, pval = diptest.diptest(np.log10(1+xk))
    print(f"  dip on log10(1+kernel-internal-outdeg): dip={d:.5f} p={pval:.4f}")
    d2, p2 = diptest.diptest(xk)
    print(f"  dip on raw kernel-internal-outdeg: dip={d2:.5f} p={p2:.4f}")
except Exception as e:
    print("  diptest unavailable:", e)

# raw outdeg dip (the actual occupancy variable, Hanski-style)
xa = np.array([v for v in outdeg.values()], dtype=float)
try:
    import diptest
    d,p = diptest.diptest(xa)
    print(f"\n  dip on RAW outdeg (all nodes incl zeros): dip={d:.5f} p={p:.4f}")
    xanz = np.array([v for v in outdeg.values() if v>0],dtype=float)
    d,p = diptest.diptest(xanz)
    print(f"  dip on RAW outdeg (nonzero only): dip={d:.5f} p={p:.4f}")
except Exception as e:
    print("  diptest unavailable", e)

out = {
  "n_nodes": N,
  "outdeg_zeros": sum(1 for v in outdeg.values() if v==0),
  "outdeg_max": max(outdeg.values()),
  "outdeg_mean": statistics.mean(outdeg.values()),
  "kernel": len(kernel), "core": len(core), "satellites": len(sats),
  "core_outdeg_mean": statistics.mean(outdeg[u] for u in core) if core else None,
  "sat_outdeg_mean": statistics.mean(outdeg[u] for u in sats) if sats else None,
}
print("\nJSON:", json.dumps(out))
