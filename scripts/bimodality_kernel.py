from __future__ import annotations
import json, math, statistics
from collections import Counter
import numpy as np
from meanings.wordnet_pipeline import build_paper_wordnet_graph
from meanings.graph_analysis import analyze_kernel

b = build_paper_wordnet_graph("oewn:2024")
adj = b.adjacency
nodes = set(b.nodes)
outdeg = {u: len([v for v in adj.get(u,()) if v!=u]) for u in nodes}

ka = analyze_kernel(nodes, adj, seed_method="exact-small-greedy", core_policy="source-union")
kernel = set(ka.kernel_nodes); core = set(ka.core_nodes); sats = set(ka.satellite_nodes); rest = nodes - kernel
print("kernel",len(kernel),"core",len(core),"sats",len(sats),"rest",len(rest))
kern_outdeg = {u: len([v for v in adj.get(u,()) if v in kernel and v!=u]) for u in kernel}

def st(lbl, members, src):
    vv=[src[u] for u in members]
    print(f"  {lbl}: n={len(vv)} mean={statistics.mean(vv):.2f} median={statistics.median(vv)} max={max(vv)} min={min(vv)}")
print("global out-degree by membership:")
st("CORE",core,outdeg); st("SATELLITE",sats,outdeg); st("REST",rest,outdeg)
print("kernel-internal out-degree by membership:")
st("CORE",core,kern_outdeg); st("SATELLITE",sats,kern_outdeg)
print("kernel-internal outdeg histogram (0..20):", {k:Counter(kern_outdeg.values()).get(k,0) for k in range(21)})

def dip(arr, lbl):
    try:
        import diptest
        d,p=diptest.diptest(np.asarray(arr,dtype=float))
        print(f"  dip {lbl}: dip={d:.5f} p={p:.4f} n={len(arr)}")
    except Exception as e:
        print("  diptest err",e)
def gmm(arr,lbl):
    try:
        from sklearn.mixture import GaussianMixture
        X=np.asarray(arr,dtype=float).reshape(-1,1)
        for k in (1,2,3):
            g=GaussianMixture(n_components=k,n_init=3,random_state=0).fit(X)
            print(f"  GMM {lbl} k={k}: BIC={g.bic(X):.1f} means={sorted(g.means_.flatten().round(3))} w={g.weights_.round(3)}")
    except Exception as e:
        print("  gmm err",e)

allnz=[v for v in outdeg.values() if v>0]
logall=[math.log10(1+v) for v in allnz]
print("\n-- RAW out-degree, all nodes (incl 74% zeros) --"); dip(list(outdeg.values()),"raw-all")
print("-- RAW out-degree, nonzero only --"); dip(allnz,"raw-nz")
print("-- log10(1+outdeg), nonzero only --"); dip(logall,"log-nz"); gmm(logall,"log-nz")
kn=list(kern_outdeg.values())
print("-- kernel-internal outdeg, raw --"); dip(kn,"kern-raw")
print("-- log10(1+kernel-internal outdeg) --"); dip([math.log10(1+v) for v in kn],"kern-log"); gmm([math.log10(1+v) for v in kn],"kern-log")
