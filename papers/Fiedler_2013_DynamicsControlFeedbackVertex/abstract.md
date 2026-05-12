# Abstract

## Original Text (Verbatim)

We consider systems of differential equations which model complex regulatory networks by a graph structure of dependencies. We show that the concepts of informative nodes (Mochizuki and Saito, J Theor Biol 266:323–335, 2010) and determining nodes (Foias and Temam, Math Comput 43:117–133, 1984) coincide with the notion of feedback vertex sets from graph theory. As a result we can determine the long-time dynamics of the entire network from observations on only a feedback vertex set. We also indicate how open loop control at a feedback vertex set, only, forces the remaining network to stably follow prescribed stable or unstable trajectories. We present three examples of biological networks which motivated this work: a specific gene regulatory network of ascidian cell differentiation (Imai et al., Science 312:1183–1187, 2006), a signal transduction network involving the epidermal growth factor in mammalian cells (Oda et al., Mol Syst Biol 1:1–17, 2005), and a mammalian gene regulatory network of circadian rhythms (Mirsky et al., Proc Natl Acad Sci USA 106:11107–11112, 2009). In each example the required observation set is much smaller than the entire network. For further details on biological aspects see the companion paper (Mochizuki et al., J Theor Biol, 2013, in press). The mathematical scope of our approach is not limited to biology. Therefore we also include many further examples to illustrate and discuss the broader mathematical aspects.

Keywords: Differential equations on graphs · Reaction network · Determining node · Global attractor · Takens embedding · Biological network · Gene regulation

---

## Our Interpretation

The paper identifies the *feedback vertex set* (FVS) of a regulatory network's directed graph as the right small "observation/control set": for any admissible nonlinear dynamics on the graph (subject to a decay/dissipativity condition), two solutions that agree asymptotically on the FVS agree everywhere, and clamping the FVS to a chosen trajectory drags the whole network onto it — even onto otherwise-unstable orbits. This matters here because a definition digraph's lexical grounding set / MinSet is precisely a feedback vertex set, so this is the foundational dynamical-systems result behind the claim that overriding the grounding set (plus source nodes) determines the rest of the lexicon independent of the compositional rule.
