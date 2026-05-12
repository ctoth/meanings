# Abstract

## Original Text (Verbatim)

The study of network structure has uncovered signatures of the organization of complex systems. However, there is also a need to understand how to control them; for example, identifying strategies to revert a diseased cell to a healthy state, or a mature cell to a pluripotent state. Two recent methodologies suggest that the controllability of complex systems can be predicted solely from the graph of interactions between variables, without considering their dynamics: structural controllability and minimum dominating sets. We demonstrate that such structure-only methods fail to characterize controllability when dynamics are introduced. We study Boolean network ensembles of network motifs as well as three models of biochemical regulation: the segment polarity network in Drosophila melanogaster, the cell cycle of budding yeast Saccharomyces cerevisiae, and the floral organ arrangement in Arabidopsis thaliana. We demonstrate that structure-only methods both undershoot and overshoot the number and which sets of critical variables best control the dynamics of these models, highlighting the importance of the actual system dynamics in determining control. Our analysis further shows that the logic of automata transition functions, namely how canalizing they are, plays an important role in the extent to which structure predicts dynamics.

---

## Our Interpretation

Structural controllability (maximum matching) and minimum dominating set claim to identify the driver nodes that control a network from its interaction graph alone; this paper proves, via fully enumerated Boolean-network ensembles and three real biochemical models, that they get both the count and the identity of driver variables wrong once any nonlinear dynamics is present, with canalization of the transition functions controlling how badly. It matters here because it is the direct argument that the repo's maximum-matching driver words for lexical grounding are spurious, whereas the feedback-vertex-set framing already in the collection transfers — FVS-control is dynamics-agnostic by theorem, so it does not suffer the failure mode this paper documents.
