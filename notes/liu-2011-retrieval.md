
## 2026-05-12
- PDF downloaded: papers/Liu_2011_ControllabilityComplexNetworks/paper.pdf (arXiv 1102.3490 preprint, 17pp, 284KB) via curl https://arxiv.org/pdf/1102.3490
- fetch_paper.py hangs on Semantic Scholar 429 backoff; writing metadata.json by hand from known biblio (Nature 473:167-173, 2011, DOI 10.1038/nature10011)
- Next: write metadata.json, run paper-reader, update index.md, add reciprocal crossrefs to Fiedler_2013/Mochizuki_2013/Zañudo_2016
- Note: concurrent agent created Gates_2016_ControlComplexNetworksRequires dir

## 2026-05-12 BLOCKER
- arXiv 1102.3490 PDF is "Abelian Decomposition of General Relativity" (Cho, Oh, Kim) gr-qc — NOT Liu/Slotine/Barabasi. The arXiv ID in the task is WRONG.
- Liu-Slotine-Barabasi "Controllability of complex networks" is Nature 473:167-173 (2011), DOI 10.1038/nature10011. Need to find correct arXiv ID or other open source.
- Deleting the wrong PDF. metadata.json already written (correct biblio). Need to re-retrieve.

## 2026-05-12 RESOLVED
- Correct PDF obtained from UVM mirror: https://cdanfort.w3.uvm.edu/csc-reading-group/barabasi-network-controllability-nature-2011.pdf (7pp Nature published main text, 1.1MB)
- Confirmed NOT on arXiv (S2 externalIds has no arXiv). Task's "arXiv 1102.3490" was a wrong ID.

## 2026-05-12 reading progress
- Read pages 0-3 of 7. Key content captured: eq(1) dx/dt=Ax+Bu, eq(2) controllability matrix C=(B,AB,...,A^{N-1}B), eq(3) rank(C)=N (Kalman), minimum-input/maximum-matching theorem (N_D = N - |max matching| or 1 if perfect matching), n_D scaling eqs(4)(5) for ER and scale-free, Table 1 (real networks: regulatory n_D^real ~0.8-0.97, trust/social low, food web ~0.3-0.5). Pages 4-6 remain (node classification: critical/redundant/ordinary links; degree-of-freedom; control robustness; methods).
- No blocker. PDF correct (7pp Nature main text).

## 2026-05-12 done reading, writing artifacts
- All 7 pages read. Refs 1-15 read clearly; remainder are standard network-science refs (Albert-Barabasi, Newman, Watts-Strogatz, Pastor-Satorras, Dorogovtsev, etc.) visible in full-page render. Writing notes.md/abstract.md/description.md/citations.md, then index.md + crossrefs.

## 2026-05-12 artifacts written
- notes.md, abstract.md, description.md, citations.md, metadata.json all written. index.md entry appended. Reciprocal crossrefs added to Fiedler_2013, Mochizuki_2013, Zañudo_2016. Temp PNGs cleaned. Remaining: optional reconcile skill.

## 2026-05-12 reconcile in progress
- Added Cited By + Conceptual Links section to Liu notes. Updated reciprocal refs in Fiedler/Mochizuki/Zañudo/Gates. Now adding reciprocal conceptual-link bullets to Steyvers-Tenenbaum_2005 and Vincent-Lamarre_2014. Then done.

## 2026-05-12 COMPLETE
- All artifacts written and validated. Removed junk papers/Cho_2011_AbelianDecompositionGeneralRelativity/ (created by the wrong-arXiv-ID fetch). Reciprocal crossrefs done in Fiedler/Mochizuki/Zañudo/Gates/Steyvers/Vincent-Lamarre. metadata.json valid JSON. index.md updated. No src/ touched.
