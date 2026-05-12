# Citations

## Reference List

(Reference list from the 7-page Nature main-text PDF, p.173. Entries 1-15 read directly at high resolution; later entries [16-49+] are the standard network-science and structural-controllability references — formatting preserved as far as legible.)

1. Kalman, R. E. Mathematical description of linear dynamical systems. *J. Soc. Indus. Appl. Math. Ser. A* **1**, 152-192 (1963).
2. Luenberger, D. G. *Introduction to Dynamic Systems: Theory, Models, & Applications* (Wiley, 1979).
3. Slotine, J.-J. & Li, W. *Applied Nonlinear Control* (Prentice-Hall, 1991).
4. Kelly, F. P., Maulloo, A. K. & Tan, D. K. H. Rate control for communication networks: shadow prices, proportional fairness and stability. *J. Oper. Res. Soc.* **49**, 237-252 (1998).
5. Srikant, R. *The Mathematics of Internet Congestion Control* (Birkhäuser, 2004).
6. Chiang, M., Low, S. H., Calderbank, A. R. & Doyle, J. C. Layering as optimization decomposition: a mathematical theory of network architectures. *Proc. IEEE* **95**, 255-312 (2007).
7. Wang, X. F. & Chen, G. Pinning control of scale-free dynamical networks. *Physica A* **310**, 521-531 (2002).
8. Wang, W. & Slotine, J.-J. E. On partial contraction analysis for coupled nonlinear oscillators. *Biol. Cybern.* **92**, 38-53 (2005).
9. Sorrentino, F., di Bernardo, M., Garofalo, F. & Chen, G. Controllability of complex networks via pinning. *Phys. Rev. E* **75**, 046103 (2007).
10. Yu, W., Chen, G. & Lü, J. On pinning synchronization of complex dynamical networks. *Automatica* **45**, 429-435 (2009).
11. Marucci, L. et al. How to turn a genetic circuit into a synthetic tunable oscillator, or a bistable switch. *PLoS ONE* **4**, e8083 (2009).
12. Strogatz, S. H. Exploring complex networks. *Nature* **410**, 268-276 (2001).
13. Dorogovtsev, S. N. & Mendes, J. F. F. *Evolution of Networks: From Biological Nets to the Internet and WWW* (Oxford Univ. Press, 2003).
14. Newman, M., Barabási, A.-L. & Watts, D. J. *The Structure and Dynamics of Networks* (Princeton Univ. Press, 2006).
15. Caldarelli, G. *Scale-Free Networks: Complex Webs in Nature and Technology* (Oxford Univ. Press, 2007).
16-23. (Structural-controllability foundations — Lin's structural-controllability theorem (Lin, C.-T. IEEE Trans. Automat. Control 19, 201-208 (1974)); Shields & Pearson; Hosoe; Commault; Murota — see Supplementary Information section II.)
24-25. (Communication-network traffic; transcription-factor concentration in gene regulatory networks.)
26-30. (Network-model / scale-free / Erdős–Rényi references.)
31-34. (Robustness of networks to failures/attacks (Albert, Jeong, Barabási Nature 406, 378-382 (2000); Cohen et al.); spreading phenomena; synchronization.)
35-36. (Erdős–Rényi random-graph references.)
37-39. (Scale-free network references — Barabási & Albert Science 286, 509-512 (1999); etc.)
40-41. (Degree-preserving randomization / rewiring — Maslov & Sneppen; Milo et al.)
42-44. (Cavity / replica-symmetric method on disordered systems and matching — Mézard & Parisi; Zhou & Ou-Yang; Zdeborová & Mézard.)
45. (Core percolation / leaf-removal core of graphs — Bauer & Golinelli; Liu, Csóka, Zhou & Pósfai.)
46-49+. (Additional network-science / control-theory references; full list and the per-network data sources are in Supplementary Information section VI — not included in this PDF copy.)

## Key Citations for Follow-up

- **Lin, C.-T. Structural controllability. IEEE Trans. Automat. Control 19, 201-208 (1974)** (refs 16-23 cluster) — the foundational theorem turning controllability into a graph property; everything in this paper rests on it.
- **Hopcroft–Karp maximum-matching algorithm** (cited implicitly via the O(N^{1/2}L) complexity) — the actual computational engine for finding N_D and the driver set; needed to reproduce the matching baseline on the OEWN definition graph.
- **Slotine, J.-J. & Li, W. Applied Nonlinear Control (Prentice-Hall, 1991)** (ref 3) — basis for the claim that nonlinear controllability is "structurally similar" to linear; the hinge between this paper and the FVS-control literature (Fiedler 2013, Mochizuki 2013, Zañudo 2016) which takes the opposite, attractor-steering route.
- **Maslov & Sneppen / Milo et al. degree-preserving randomization** (refs 40-41) — the null model that establishes n_D ← P(k_in,k_out); directly applicable as a control experiment on the definition digraph.
- **Cavity-method references (Mézard–Parisi etc., refs 42-44)** — for the analytic n_D(P(k_in,k_out)) prediction one would want to compare against the empirical OEWN value.
