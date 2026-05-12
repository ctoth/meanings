# Swanson-4: Yoneda vs Harnad

Date: 2026-05-12

## Task
Execute reports/research-swanson-4-yoneda-harnad.md. Deliverable: reports/swanson-yoneda-harnad-findings.md.
Verdict A (compatible/synthesis) / B (genuine fight) / C (data adjudicates).

## State
- No partial findings file existed.
- Read: Harnad/Masse/Vincent-Lamarre paper notes (thin), annotation-sources.md, synthesis-minimal-core-to-expansion.md, src/meanings/annotations.py.
- annotations.py: optional CSV overlays (frequency, concreteness, age_of_acquisition, imageability). "No psycholinguistic values are bundled" -> repo has NO AoA/concreteness data. So the regression cannot be run on real psycholinguistic data without supplying CSVs.
- BUT: layers JSON exists: reports/oewn-paper-wordnet-layers.json (310KB), oewn-synset-layers.json. These have which-layer-each-word. Structural graph features (in/out degree, etc.) computable from the graph itself.

## Blocker / decision
- Extra-graph features (AoA, concreteness) not in repo -> the "variance explained by extra-graph vs structural" regression CANNOT be fully run. Options: (a) check papers/ dir for any psycholx CSV; (b) run the structural-only half and specify the extra-graph half precisely; (c) note Vincent-Lamarre's own published correlations as the evidence.

## TODO
- Web research: Yoneda-as-philosophy, Marquis structuralism, Harnad 1990, DisCoCat/Coecke-Sadrzadeh, inferentialism/Brandom/Block, citation disjointness both directions.
- Check papers/ for psycholx data + check what layers JSON contains.
- Land verdict, write deliverable.

## Update 2 (after web research)
Disjointness CONFIRMED both directions:
- Categorical structuralism (Marquis, Awodey, Landry, McLarty 1990s; Hellman critique) -> no Harnad.
- Symbol grounding (Harnad 1990; Taddeo&Floridi 2005 review; Wikipedia/Scholarpedia) -> no Yoneda/cat theory.
- DisCoCat (Coecke-Sadrzadeh-Clark 2010) -> uses compact closed cats, NO grounding discussion (it presupposes distributional vectors as "meaning", doesn't ask where they come from).
- Inferentialism/CRS (Sellars, Brandom, Block, Harman) = "meaning is relations" -> does NOT cite Yoneda.
- Near-miss: Seremeti & Kameas 2013 "Yoneda Philosophy in Engineering" (Wiley Intl J Eng Math) uses Yoneda embedding for ontology/concept formalization. Peripheral. Also Tao blog, math3ma, Milewski as Yoneda-as-philosophy expositions.

## Empirical adjudication - DECISION
Repo has ZERO psycholinguistic data (annotation_sources=[], all coverage 0). layers JSON has 12853 kernel-node layers (~9897 single-word lemmas). To run the real regression need external norms (Brysbaert concreteness 2014, Kuperman AoA 2012, SUBTLEX freq). Decision: (a) run structural-only descriptive (layer IS a structural feature; show kernel/core/satellite is graph-derived) (b) cite Vincent-Lamarre 2014 published correlations as the standing evidence (c) specify the regression precisely in deliverable. NOT fetching big norm CSVs - unreliable + scope.

## Verdict landing: A with a C-flavored caveat
Lean Resolution A (compatible: grounding = constructing/choosing the base category; Yoneda then operates within it). Harnad's residue = the choice of ambient category (which relata exist, which morphisms count), which Yoneda *presupposes*. MinSet arbitrariness <-> many equivalent presentations/generating sets of the same category. The dictionary-graph evidence (V-L correlations) is real but WEAK as anti-Yoneda because: those extra-graph features could just be *causes* of graph position, not evidence of semantic residue; and the dict graph isn't actually a category (no composition/identities in the relevant sense). So: A is best-supported. Mention B's live bullet: if you ARE a thoroughgoing structuralist, math owes the same grounding story (Benacerraf access problem) - symmetry argument.

## REMAINING: write deliverable reports/swanson-yoneda-harnad-findings.md

## DONE 2026-05-12
Deliverable written: reports/swanson-yoneda-harnad-findings.md. Verdict A + symmetry rider toward B; C = light thumb. Empirical: ran structural-only descriptive on layers JSON; full regression spec'd (needs external norm CSVs not in repo).
