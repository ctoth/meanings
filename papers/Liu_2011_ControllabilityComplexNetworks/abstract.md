# Abstract

## Original Text (Verbatim)

The ultimate proof of our understanding of natural or technological systems is reflected in our ability to control them. Although control theory offers mathematical tools for steering engineered and natural systems towards a desired state, a framework to control complex self-organized systems is lacking. Here we develop analytical tools to study the controllability of an arbitrary complex directed network, identifying the set of driver nodes with time-dependent control that can guide the system's entire dynamics. We apply these tools to several real networks, finding that the number of driver nodes is determined mainly by the network's degree distribution. We show that sparse inhomogeneous networks, which emerge in many real complex systems, are the hardest to control, but that dense and homogeneous networks can be controlled using a few driver nodes. Counterintuitively, we find that in both model and real systems the driver nodes tend to avoid the high-degree nodes.

---

## Our Interpretation

Under linear time-invariant dynamics ẋ = Ax + Bu, controlling a directed network reduces to a maximum-matching problem: the minimum number of independent control inputs (driver nodes) N_D equals the number of nodes left unmatched by a maximum matching of the wiring digraph, computable in O(N^{1/2}L). Empirically n_D = N_D/N spans six orders of magnitude across real networks, is set by the degree distribution P(k_in,k_out) (degree-preserving randomization leaves it unchanged), is largest for sparse heterogeneous networks like gene-regulatory networks (~80% drivers), and the driver nodes preferentially avoid hubs. This is the linear-dynamics, full-state-controllability counterpart to the feedback-vertex-set control results — and on a dictionary's definition digraph the matching driver set (~74% of words on OEWN) dwarfs the FVS grounding seed (~1.5%), the gap being exactly the difference between "reach every state" and "steer between attractors".
