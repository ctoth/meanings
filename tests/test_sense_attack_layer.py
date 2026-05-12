"""Tests for the sense-level rival-sense attack layer and its bipolar AF round-trip."""

from argumentation.dung import stable_extensions

from meanings.argumentation_bridge import (
    bipolar_with_attacks_framework,
    derived_dung_framework,
    edges_of,
)
from meanings.wordnet_pipeline import (
    SenseLevelGraphBuild,
    add_rival_sense_attacks,
)


def _tiny_build() -> SenseLevelGraphBuild:
    # Two forms. "bank" has two senses (s1 riverbank, s2 financial); "river" has one.
    # Support edges: river -> s1 (river occurs in the gloss of the riverbank sense).
    nodes = {"s1", "s2", "r1"}
    adjacency = {"s1": set(), "s2": set(), "r1": {"s1"}}
    node_metadata = {
        "s1": {"lemma": "bank", "pos": "n", "sense_id": "s1"},
        "s2": {"lemma": "bank", "pos": "v", "sense_id": "s2"},
        "r1": {"lemma": "river", "pos": "n", "sense_id": "r1"},
    }
    return SenseLevelGraphBuild(
        lexicon_id="toy",
        nodes=nodes,
        adjacency=adjacency,
        labels={n: n for n in nodes},
        pos_by_node={"s1": "n", "s2": "v", "r1": "n"},
        node_metadata=node_metadata,
        resolution_stats={},
    )


def test_two_senses_of_one_form_make_one_unordered_attack_pair():
    g = add_rival_sense_attacks(_tiny_build())
    assert g.attacks["s1"] == {"s2"}
    assert g.attacks["s2"] == {"s1"}
    assert g.attacks["r1"] == set()  # only one sense for "river"
    assert g.attack_edge_count == 2  # ordered
    assert g.unordered_attack_pair_count == 1
    assert g.rivalry_cliques == {"bank": ["s1", "s2"]}
    assert g.rivalry_key_by_node == {"s1": "bank", "s2": "bank"}


def test_per_pos_rivalry_drops_cross_pos_pairs():
    # s1 is "bank::n", s2 is "bank::v" -> per-POS they are not rivals.
    g = add_rival_sense_attacks(_tiny_build(), per_pos=True)
    assert g.attacks["s1"] == set()
    assert g.attacks["s2"] == set()
    assert g.rivalry_cliques == {}


def test_bipolar_af_round_trips_supports_and_attacks():
    g = add_rival_sense_attacks(_tiny_build())
    baf = bipolar_with_attacks_framework(g.nodes, g.supports, g.attacks)
    assert baf.arguments == frozenset({"s1", "s2", "r1"})
    assert baf.supports == frozenset({("r1", "s1")})
    assert baf.defeats == edges_of(g.nodes, g.attacks) == frozenset({("s1", "s2"), ("s2", "s1")})


def test_support_into_a_rival_breaks_the_clique_symmetry():
    # river -> s1 (support), s1 <-> s2 (attack). Cayrol *mediated/indirect* defeat:
    # r1 supports s1 and s1 attacks s2  =>  r1 attacks s2. So {r1, s2} is not
    # conflict-free; the only stable extension is {r1, s1} -- the reading that the
    # rest of the lexicon "grounds" wins, the symmetry of the bare 2-clique is gone.
    g = add_rival_sense_attacks(_tiny_build())
    af = derived_dung_framework(g.nodes, g.supports, g.attacks)
    assert ("r1", "s2") in af.defeats
    stables = sorted((tuple(sorted(s)) for s in stable_extensions(af)))
    assert stables == [("r1", "s1")]


def test_bare_rival_clique_with_no_support_has_k_stable_extensions():
    # Two senses of a form, nothing else: a bare 2-clique. Two stable extensions
    # (each singleton). This is the multiplicativity story in its purest form.
    nodes = {"s1", "s2"}
    supports = {"s1": set(), "s2": set()}
    attacks = {"s1": {"s2"}, "s2": {"s1"}}
    af = derived_dung_framework(nodes, supports, attacks)
    stables = sorted((tuple(sorted(s)) for s in stable_extensions(af)))
    assert stables == [("s1",), ("s2",)]


def test_chain_support_propagates_attack_forward():
    # a -> b -> c support chain; x attacks a. Cayrol supported defeat: x attacks b, x attacks c.
    nodes = {"a", "b", "c", "x"}
    supports = {"a": {"b"}, "b": {"c"}, "c": set(), "x": set()}
    attacks = {"a": {"x"}, "x": {"a"}, "b": set(), "c": set()}
    af = derived_dung_framework(nodes, supports, attacks)
    assert ("x", "b") in af.defeats
    assert ("x", "c") in af.defeats
