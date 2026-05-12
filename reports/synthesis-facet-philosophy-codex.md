# Synthesis Facet: Philosophy

The project should make a sharp distinction and then refuse to blur it:

1. A dictionary graph can tell us which words are recursively definable from which other words.
2. It cannot, by that fact alone, tell us which words mean anything to an agent.

That distinction is Harnad's constraint on the whole program. The monolingual dictionary-go-round is not a joke about bad dictionaries; it is the core negative result. A closed symbol system can be internally consistent, richly connected, even mathematically minimal, and still have only interpreter-relative meaning. Recursive definability is a property of a formal dependency graph. Grounding is a relation between some symbolic/categorical states and the nonsymbolic capacities by which an agent discriminates, identifies, acts, and learns in the world.

Massé, Picard, and Vincent-Lamarre make Harnad computable without refuting him. In their graph, an edge from definer to defined word lets us ask exactly which cycles must be hit so the rest of the lexicon unfolds. A grounding set is a feedback vertex set; a MinSet is a small cycle-breaking basis; the Kernel is the recursively irreducible residue after leaf-stripping; Core and Satellites separate different regions of that residue. This is real progress. It turns "dictionary regress" into an object one can compute.

But the word "grounding" is dangerous here. A MinSet grounds the graph only in the internal, conditional sense: if these nodes are already available, the rest can be reached by definitions. It does not show that the MinSet words are grounded for a mind. The graph can identify where external grounding would have to enter; it cannot supply the external grounding. The project over-claims whenever it treats "belongs to a MinSet", "is in the Kernel", or "has high definitional productivity" as equivalent to being a human semantic primitive.

## Foundationalism And Coherentism

The strongest philosophical reading of the dictionary graph is that it turns the old foundationalism/coherentism dispute into competing semantics over the same cyclic structure.

The foundationalist reading cuts cycles. Harnad is the relevant pressure here: some words must be learned by means other than verbal definition, or the dictionary never bottoms out. Massé's feedback-vertex theorem is the formal analogue: hit every directed cycle, and recursive definability becomes well-founded. On this reading, a MinSet is not optional decoration; it is the place where non-symbolic contact must enter if the symbolic system is to stop borrowing meaning from an outside interpreter.

The coherentist reading inhabits cycles. Levary's result matters because loops are not merely defects in need of excision. Short definitional loops are often semantically coherent, disproportionately present relative to randomized controls, and historically clustered. Distributional and structuralist semantics push in the same direction: a word's role in a web of relations is not a regrettable circularity but the thing to be studied. The loop ecology may be semantic signal.

Dung-style argumentation semantics gives the clean bridge. Grounded semantics is the skeptical, well-founded, foundationalist reading: accept only what is forced from the bottom. Preferred or stable semantics are coherentist readings: accept maximal self-consistent stances through the cycles. This does not settle which philosophy is right, but it makes the disagreement precise. "Cut the Kernel" and "study the loops" are not two unrelated project moods; they are two semantics over circular support.

This also explains why MinSet non-uniqueness should not be embarrassing. Multiple MinSets mean there are multiple ways to present or enforce a well-founded unfolding of the same cyclic substrate. Philosophically, that is not a unique list of ultimate atoms; it is a family of admissible grounding choices. If the project wants to rank them, it needs an explicit cost function: psycholinguistic plausibility, pedagogical utility, sensorimotor accessibility, cross-dictionary stability, or some other standard. "Smallest" is not the same as "best grounded."

## Yoneda And Harnad

The Yoneda/Harnad confrontation should be stated as compatibility, not contradiction.

Yoneda says that, inside a fixed category, an object is determined by its relations to all other objects. Harnad says that, for a cognitive agent, the relevant category is not given in advance. Which relata exist, which distinctions are real, which morphisms or inferential links count: those have to be carved out by nonsymbolic capacities before the symbolic web can have intrinsic content for the agent. Yoneda presupposes the ambient category; Harnad asks how an agent gets one.

So the clean synthesis is:

- grounding constructs or selects the base category;
- once that category is fixed, structural identity can do real work inside it.

The dictionary graph is only an analogy to a category, not a category in the strict sense. Its edges do not supply identities, composition, or functoriality. That limitation matters. Still, the analogy is useful if kept in scope: a MinSet resembles a generating set; different MinSets resemble different presentations; Kernel/Core/Satellite structure resembles a graded account of where the symbolic system depends on its cyclic base.

The symmetry rider is important. A thoroughgoing structuralist who says "relations are all there is" for concepts owes mathematics the same story. Benacerraf's access problem is the mathematical version of Harnad's question: if objects are only positions in structures, how do we know which structure we are accessing, and how does that access get fixed? One cannot use structuralism to dissolve grounding in cognitive semantics while treating mathematical access as a separate mystery. Either selection/access residues are real in both domains, or one accepts a very strong structuralism in both.

## What The Regression Shows

The psycholinguistic regression gives a useful negative result, but not the metaphysical victory one might want.

The narrow result is strong. On the OEWN `lemma::pos` definition digraph, structural features already explain the layer and membership outcomes almost completely. Adding the psycholinguistic block, frequency, age of acquisition, and concreteness, buys at most about 0.01 incremental R-squared or AUC over the structural block. Kernel membership, Core/Satellite status, seed membership, and layer depth are all overwhelmingly screened off by graph-derived features such as degree, SCC structure, cycle participation, and PageRank-like scores. The follow-up on ranking-based argumentation semantics confirms the same pattern from another direction: every principled centrality or defensibility score tried on the bare definition digraph collapses back to degree, often with the wrong sign for "foundationalness."

That refutes a strong claim: there is no large independent psycholinguistic residue, measured by these norms, that the bare relational structure obviously misses for these graph outcomes. If someone predicted that concreteness, frequency, and age of acquisition would add a large residual signal after graph structure, the prediction failed.

But the causal conclusion does not follow. Lexicographers write definitions for learners. Concrete, early-acquired, frequent words become definers because readers are expected to know them. That editorial practice creates the very structural features that then screen off the psycholinguistic variables. The same regression signature is compatible with two opposite causal stories:

1. Meaning is mostly relational, so once the graph is known there is little left for psycholinguistic norms to explain.
2. The graph was built from human psycholinguistic salience, so the structure already encodes those norms.

The regression cannot distinguish these. It therefore cannot show that meaning is Yoneda-complete. It only defeats the strong extra-graph-residue claim for this artifact and these variables. The project over-claims if it presents the result as "meaning is just the graph." The defensible statement is narrower: on the current OEWN definition graph, these three psycholinguistic variables add little independent predictive power for graph-defined membership and depth once structural features are included.

This is still philosophically valuable. It says the dictionary graph is not arbitrary notation. Its topology captures much of the learner-facing salience that earlier papers associated with frequency, concreteness, and acquisition. But that may be because the graph is a cultural artifact made by humans for humans, not because relations alone constitute meaning.

## Harnad In Executable Form

The `gunray` demonstrator is the cleanest mechanization of "recursive definability is not meaning."

A circular definition theory such as `a <- b` and `b <- a`, with no external fact, does not explode and does not arbitrarily choose a winner. It comes out `UNDECIDED`. That is exactly the right philosophical result. The system has a rule-language place for the literals, but no grounded support from which an argument can be built. Add a grounding fact, and dependent literals can become `YES`.

This is Harnad in code. A circular symbolic structure is not an error in syntax, and it is not semantically self-sufficient. It is underdetermined until something outside the circle is admitted. That admission need not be magical; it can be a fact, a presumption, a sensorimotor category, or an externally chosen seed. But without it, recursive definition remains suspended.

The limitation is scale. `gunray` is a small-theory defeasible-logic engine, not a WordNet-scale graph engine. Its role is demonstrator and explanatory model, not production kernel computation. The meanings repo's SCC/FVS machinery remains the scalable side.

## The Up-Goer Invariants

The Up-Goer identity-cluster note is not just data-cleaning advice. It is an epistemological stance.

Its invariants are the right antidote to both naive graph worship and vector-soup semantics:

- form is not sense;
- sense is not identity cluster;
- referential meaning is not indexical signal;
- definition dependency is not usage correlation;
- graph necessity is not human primitive admission;
- embeddings and corpus statistics are evidence, not authority.

These distinctions protect the project from a common category mistake. The raw `lemma::pos` graph is a useful computational projection, but it conflates forms, senses, identity clusters, constructions, readings, and admission policy. `no::n` as Nobelium is not ordinary `no`; `color` and `colour` may be separate forms for one referential identity cluster; `warsh` may share referential content with `wash` while carrying indexical evidence; an idiom such as `bless her heart` is not exhausted by a word-by-word literal parse.

This is why the future target is not "ask an LLM for the primitive words." Correlations can propose merges, splits, readings, or exclusions. They cannot be the authority. The target artifact has to be typed, inspectable, provenance-bearing, and defeasible: a sense-level or identity-cluster graph with admission rules, not a flattened list of strings.

The self-loop issue is a good test case. Treating a gloss self-loop as cyclic is correct for the current lemma-level graph. But many self-loops may dissolve when gloss occurrences are resolved to intended senses or identity clusters. If the sense-level rebuild does not shrink the artifact-inflated kernel or at least explain why the self-loops survive, the redesign has not earned its keep.

## Where The Project Should Stay Skeptical

The project can defend several claims:

- A dictionary graph makes recursive definability measurable.
- Grounding sets are feedback vertex sets.
- The Kernel/Core/Satellite/MinSet anatomy is stable and useful.
- Loops are semantic structure as well as obstacles to well-founded unfolding.
- Psycholinguistic salience is largely mirrored in graph structure on the current OEWN artifact.
- `UNDECIDED` is the right formal status for circular ungrounded definitions.

It should not claim:

- that a MinSet is a set of ultimate semantic primitives;
- that recursive definability is intrinsic meaning;
- that degree, PageRank, ranking semantics, or FVS membership gives a deep continuous measure of groundedness on the bare `lemma::pos` graph;
- that the psycholinguistic regression proves meaning is relationally complete;
- that a raw graph node is already a human word.

The strongest philosophical position is modest but durable: dictionary graphs locate the places where a symbolic lexicon cannot justify itself from within. They also reveal that some loops are meaningful coherent structures rather than mere bugs. Grounding and coherence are therefore not enemies. Grounding supplies the nonsymbolic category-selection without which the system is parasitic; coherence supplies the internal relational identity once the system has something to be about.
