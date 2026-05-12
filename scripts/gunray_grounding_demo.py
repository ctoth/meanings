"""gunray grounding demo: recursive definability is not meaning, mechanized.

Connection #5 from ``reports/sibling-tools-connection.md``. We use the DeLP
engine ``gunray`` (Garcia & Simari 2004, defeasible logic programming) to show,
in working code, the thesis the meanings repo studies graph-theoretically:

  * an ungrounded circular definition core evaluates to UNDECIDED -- not an
    error, not an arbitrary pick (this is the "Kernel": the un-grounded
    circular core);
  * supplying a minimal grounding set (a feedback-vertex-set hitting every
    cycle) flips every dependent literal to YES (the "Satellites" become
    derivable);
  * the dialectical tree gunray builds *is* the merge/exclusion rationale --
    you can render it before and after grounding.

Four parts:
  1. toy circular core ``a -< b``, ``b -< a``, no facts -> both UNDECIDED.
  2. add the grounding fact ``b`` -> ``b`` YES, ``a`` resolves to YES.
  3. a real ~9-word strongly-connected slice of the OEWN definition graph
     (a circular Greek-mythology cluster pulled from the actual Kernel SCC),
     encoded as defeasible rules: ungrounded -> a pile of UNDECIDED; ground
     the slice's local feedback-vertex-set (from ``meanings.minset``) -> the
     rest resolves to YES. Dialectical tree for one node rendered before and
     after.
  4. the polysemy case: ``sense_negation`` vs ``sense_Nobelium`` as competing
     readings of the form ``no``; a gloss-type-check argument plus a
     superiority that lets it defeat ``sense_Nobelium`` -> ``no`` resolves to
     the negation reading. Tree shown.

Run:  uv run python scripts/gunray_grounding_demo.py
It writes mermaid renders into reports/ and prints the trees to stdout. The
companion narrative is reports/gunray-grounding-demo.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gunray import (
    CompositePreference,
    DefeasibleTheory,
    GeneralizedSpecificity,
    GunrayEvaluator,
    Rule,
    SuperiorityPreference,
    answer,
    build_arguments,
    build_tree,
    render_tree,
    render_tree_mermaid,
)
from gunray.types import GroundAtom

from meanings.graph_analysis import induced_subgraph
from meanings.minset import solve_minset

REPORTS = Path(__file__).resolve().parent.parent / "reports"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _crit(theory: DefeasibleTheory):
    return CompositePreference(SuperiorityPreference(theory), GeneralizedSpecificity(theory))


def evaluate_atoms(theory: DefeasibleTheory, atoms: list[str]) -> dict[str, str]:
    """Return {atom_text: answer-name} for ground 0-ary atoms."""
    crit = _crit(theory)
    return {a: answer(theory, GroundAtom(a, ()), crit).name for a in atoms}


def tree_for_atom(theory: DefeasibleTheory, atom: str):
    """Build the dialectical tree for the (first) argument concluding ``atom``.

    Returns (tree, unicode_render, mermaid_render) or (None, None, None) if no
    argument for the atom exists -- which is itself the UNDECIDED signature for
    the circular-no-grounding case.
    """
    crit = _crit(theory)
    target = GroundAtom(atom, ())
    for arg in sorted(build_arguments(theory), key=lambda a: (str(a.conclusion), len(a.rules))):
        if arg.conclusion == target:
            tree = build_tree(arg, crit, theory)
            return tree, render_tree(tree), render_tree_mermaid(tree)
    return None, None, None


def banner(text: str) -> None:
    print()
    print("=" * 76)
    print(text)
    print("=" * 76)


def write_mermaid(name: str, mermaid: str | None) -> None:
    if mermaid is None:
        return
    path = REPORTS / name
    path.write_text("```mermaid\n" + mermaid + "\n```\n", encoding="utf-8")
    print(f"  [wrote {path}]")


# --------------------------------------------------------------------------
# Part 1 + 2: toy circular core, then grounded
# --------------------------------------------------------------------------
def part1_2_toy() -> None:
    banner("PART 1 -- toy circular core: a -< b, b -< a, NO facts -> UNDECIDED")
    ungrounded = DefeasibleTheory(
        facts={},
        strict_rules=(),
        defeasible_rules=(
            Rule(id="def_a", head="a", body=["b"]),
            Rule(id="def_b", head="b", body=["a"]),
        ),
    )
    print("rules: def_a: a -< b ;  def_b: b -< a ;  facts: (none)")
    print("answers:", evaluate_atoms(ungrounded, ["a", "b"]))
    print("-> both UNDECIDED. build_arguments produced:", build_arguments(ungrounded) or "(empty)")
    print("   The circular core supports no minimal argument -> nothing warranted,")
    print("   but the predicates are in the language -> UNDECIDED, not UNKNOWN, not error.")

    banner("PART 2 -- add ONE grounding fact (b) -> b YES, a resolves to YES")
    grounded = DefeasibleTheory(
        facts={"b": {()}},
        strict_rules=(),
        defeasible_rules=(
            Rule(id="def_a", head="a", body=["b"]),
            Rule(id="def_b", head="b", body=["a"]),
        ),
    )
    print("rules: def_a: a -< b ;  def_b: b -< a ;  facts: b")
    print("answers:", evaluate_atoms(grounded, ["a", "b"]))
    print("-> b YES (fact), a YES (def_a fires off the grounded b).")
    _, uni, mer = tree_for_atom(grounded, "a")
    print("dialectical tree for `a` after grounding:")
    print(uni)
    write_mermaid("gunray-demo-toy-a-grounded.mmd", mer)
    print("\nThis is the whole grounding thesis in ~10 lines: the Kernel is the")
    print("UNDECIDED circular core; choose a minimal grounding set; the Satellites")
    print("become derivable -- and the tree is the rationale.")


# --------------------------------------------------------------------------
# Part 3: a real OEWN Kernel-SCC slice
# --------------------------------------------------------------------------
# A 9-node strongly-connected component pulled from the actual OEWN:2024
# lemma-level Kernel (the smallest cyclic SCC in the 25,185-node Kernel as of
# 2026-05-12). Every word in this set is "defined" -- in WordNet's gloss -- using
# other words in the set: a self-contained mythological loop with no exit to
# grounded vocabulary. Edge w -> u means "u appears in w's gloss" (so knowing w
# defeasibly follows from knowing its definiens). Adjacency restricted to the SCC:
OEWN_SCC_ADJ: dict[str, set[str]] = {
    "andromeda": {"andromeda", "andromeda_galaxy", "cassiopeia", "perseus"},
    "andromeda_galaxy": {"andromeda"},
    "bellerophon": {"pegasus"},
    "cassiopeia": {"andromeda", "cepheus", "perseus"},
    "cepheus": {"cassiopeia"},
    "coelenterate": {"medusa"},
    "medusa": {"coelenterate", "pegasus", "perseus"},
    "pegasus": {"andromeda", "bellerophon"},
    "perseus": {"andromeda", "medusa"},
}
OEWN_SCC_NODES = set(OEWN_SCC_ADJ)


def _atom(word: str) -> str:
    # 0-ary propositional atom per word (not known(word)/1): with variable
    # predicates and an empty Herbrand universe gunray grounds to nothing and
    # reports UNKNOWN; a 0-ary predicate that appears in a rule head is "in the
    # language" and so an un-supported circular core comes back UNDECIDED.
    return f"known_{word}"


def _rules_from_adjacency(adj: dict[str, set[str]]) -> tuple[Rule, ...]:
    """One defeasible rule per word: known_w -< known_u1, known_u2, ...

    Self-loops (w -> w, a WordNet gloss artifact) are dropped from the body --
    a rule whose own head sits in its body can never fire and would just be
    noise; the *cycle through other nodes* is what carries the circularity.
    """
    rules: list[Rule] = []
    for word in sorted(adj):
        body = sorted(_atom(u) for u in adj[word] if u != word)
        rules.append(Rule(id=f"def_{word}", head=_atom(word), body=body))
    return tuple(rules)


def part3_oewn_slice() -> None:
    banner("PART 3 -- a real OEWN Kernel SCC: 9-word circular mythology cluster")
    print("slice (smallest cyclic SCC in the OEWN:2024 lemma-level Kernel):")
    for w in sorted(OEWN_SCC_ADJ):
        print(f"  {w:18s} <- {', '.join(sorted(OEWN_SCC_ADJ[w]))}")
    rules = _rules_from_adjacency(OEWN_SCC_ADJ)
    atoms = [_atom(w) for w in sorted(OEWN_SCC_NODES)]

    # ungrounded
    ungrounded = DefeasibleTheory(facts={}, strict_rules=(), defeasible_rules=rules)
    print("\n-- ungrounded (no facts) --")
    ans_u = evaluate_atoms(ungrounded, atoms)
    for a in atoms:
        print(f"  {a:28s} {ans_u[a]}")
    assert all(v == "UNDECIDED" for v in ans_u.values()), ans_u
    print("  -> every word UNDECIDED. The whole SCC is one un-grounded circular core.")
    tree_u, uni_u, mer_u = tree_for_atom(ungrounded, _atom("perseus"))
    print("  dialectical tree for", _atom("perseus"), "ungrounded:",
          "(no argument exists -> UNDECIDED)" if tree_u is None else "")
    if uni_u:
        print(uni_u)
    write_mermaid("gunray-demo-oewn-perseus-ungrounded.mmd", mer_u)

    # local feedback-vertex-set via the meanings minset solver
    scc_graph = induced_subgraph(OEWN_SCC_NODES, OEWN_SCC_ADJ)
    minset = solve_minset(OEWN_SCC_NODES, scc_graph, "bounded-scc")
    fvs = sorted(minset.nodes)
    print(f"\n-- local feedback-vertex-set (meanings.minset, method={minset.method}) --")
    print(f"  FVS = {fvs}   (residual cyclic SCCs after removal: {minset.residual_cyclic_scc_count})")
    print("  This is the minimal external grounding: fix these words from outside")
    print("  and recursive unfolding determines every other word in the slice.")

    # grounded
    grounded = DefeasibleTheory(
        facts={_atom(w): {()} for w in fvs},
        strict_rules=(),
        defeasible_rules=rules,
    )
    print("\n-- grounded (facts: the FVS atoms given) --")
    ans_g = evaluate_atoms(grounded, atoms)
    for a in atoms:
        flip = "  <- flipped" if ans_u[a] != ans_g[a] else ""
        print(f"  {a:28s} {ans_g[a]}{flip}")
    yes = [a for a, v in ans_g.items() if v == "YES"]
    print(f"  -> {len(yes)}/{len(atoms)} words now YES. The Satellites became derivable.")
    tree_g, uni_g, mer_g = tree_for_atom(grounded, _atom("perseus"))
    print(f"  dialectical tree for {_atom('perseus')} AFTER grounding:")
    if uni_g:
        print(uni_g)
    write_mermaid("gunray-demo-oewn-perseus-grounded.mmd", mer_g)


# --------------------------------------------------------------------------
# Part 4: polysemy -- competing readings of the form "no"
# --------------------------------------------------------------------------
def part4_polysemy() -> None:
    banner('PART 4 -- polysemy: "no" reads as negation, not Nobelium')
    # Two competing readings of the surface form "no":
    #   r_neg : reading(no, negation)  -< form(no)
    #   r_nob : reading(no, nobelium)  -< form(no)
    # made mutually exclusive via the `conflicts` declaration on the predicates'
    # ground forms. WordNet has both: "no" the function word (negation) and
    # "No" the chemical symbol for Nobelium. A gloss-type-check argument fires
    # when the gloss looks like a function word ("used to express negation..."),
    # not a chemical-element gloss; and an explicit superiority makes that check
    # beat the raw bare-form reading r_nob.
    #
    # We encode the type check as a defeasible rule that *also* concludes
    # reading(no, negation) but from a stronger antecedent (the type evidence),
    # and we declare r_check superior to r_nob. Because reading(no,negation) and
    # reading(no,nobelium) conflict, warranting one defeats the other.
    # (0-ary propositional atoms: a bare lowercase identifier in term position
    #  is parsed as a Datalog variable, so we flatten reading(no,X) into atoms.)
    theory = DefeasibleTheory(
        facts={"form_no": {()}, "gloss_is_function_word_no": {()}},
        strict_rules=(),
        defeasible_rules=(
            Rule(id="r_neg", head="reading_no_negation", body=["form_no"]),
            Rule(id="r_nob", head="reading_no_nobelium", body=["form_no"]),
            Rule(
                id="r_check",
                head="reading_no_negation",
                body=["form_no", "gloss_is_function_word_no"],
            ),
        ),
        superiority=(("r_check", "r_nob"),),
        conflicts=(("reading_no_negation", "reading_no_nobelium"),),
    )
    print("rules:")
    print("  r_neg   : reading_no_negation -< form_no")
    print("  r_nob   : reading_no_nobelium -< form_no")
    print("  r_check : reading_no_negation -< form_no, gloss_is_function_word_no")
    print("superiority: r_check > r_nob ;  conflict: reading_no_negation >< reading_no_nobelium")
    print("facts: form_no, gloss_is_function_word_no")
    ans = evaluate_atoms(theory, ["reading_no_negation", "reading_no_nobelium"])
    print("answers:", ans)
    _, uni, mer = tree_for_atom(theory, "reading_no_negation")
    print("dialectical tree for reading_no_negation:")
    print(uni)
    write_mermaid("gunray-demo-polysemy-no.mmd", mer)
    print('-> "no" resolves to the negation reading; the type-check argument defeats')
    print("   the Nobelium reading. The tree is the merge/exclusion rationale.")


def main() -> int:
    part1_2_toy()
    part3_oewn_slice()
    part4_polysemy()
    banner("DONE -- see reports/gunray-grounding-demo.md and reports/gunray-demo-*.mmd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
