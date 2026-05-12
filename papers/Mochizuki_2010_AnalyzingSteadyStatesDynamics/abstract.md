# Abstract

## Original Text (Verbatim)

Regulatory relations between biological molecules constitute complex network systems and realize diverse biological functions through the dynamics of molecular activities. However, we currently have very little understanding of the relationship between the structure of a regulatory network and its dynamical properties. In this paper we introduce a new method, named "linkage logic" to analyze the dynamics of network systems. By this method, we can restrict possible steady states of a given system from the knowledge of regulatory linkages alone. The regulatory linkage simply specifies the list of variables that affect the dynamics of each variable. We formalize two aspects of the linkage logic: the "Principle of Compatibility" determines the upper limit of the diversity of possible steady states; the "Principle of Dependency" determines the possible combinations of steady states of the system. We show that these principles can be applied to steady states of a wide class of formulae of the ODE systems. We illustrate the use of the method by several examples including an experimentally determined regulatory network for biological functions.

(Note: verbatim text reconstructed from the article's abstract block on p.323; minor wording may differ from the publisher's exact copy.)

---

## Our Interpretation

The paper asks how much of a regulatory network's steady-state behaviour is forced by its wiring alone — no signs, no rate constants. The answer is captured by the "informative nodes": a graph-determined node subset whose steady-state activities uniquely determine the whole steady state for every admissible nonlinearity, so steady-state diversity has dimension at most |informative nodes| (Principle of Compatibility) and any observed set of steady states must satisfy a wiring-derived consistency equation (Principle of Dependency). This is directly relevant to definition digraphs: the informative nodes are the minimal lexical grounding set, and this paper is the origin of the concept that the later Fiedler–Mochizuki 2013 work identifies with the graph-theoretic feedback vertex set.
