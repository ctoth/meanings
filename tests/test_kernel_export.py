from __future__ import annotations

from meanings.annotations import AnnotationStore
from meanings.kernel_export import (
    KernelMembership,
    collapse_seed_surfaces,
    label_gloss,
    row_for_node,
    suspicion_reasons,
    write_seed_surfaces_csv,
    write_seed_words,
)


def test_label_gloss_extracts_definition_fragment() -> None:
    assert label_gloss("make [v] :: bring into existence") == "bring into existence"
    assert label_gloss("make::v") == ""


def test_row_for_node_joins_membership_degrees_labels_and_annotations() -> None:
    annotations = AnnotationStore()
    annotations.add("make", "frequency", 6.4)
    annotations.add("make", "age_of_acquisition", 4.2)
    annotations.add("make", "concreteness", 2.1)
    membership = KernelMembership(
        layer_by_node={"make::v": 0},
        seed_nodes={"make::v"},
        core_nodes={"make::v"},
        satellite_nodes=set(),
    )

    row = row_for_node(
        node="make::v",
        membership=membership,
        labels={"make::v": "make [v] :: bring into existence"},
        seed_method="exact-small-greedy",
        candidate_seed_id="exact-small-greedy:n1:r0",
        indegree={"make::v": 3},
        outdegree={"make::v": 2},
        annotations=annotations,
    )

    assert row["lemma"] == "make"
    assert row["pos"] == "v"
    assert row["is_seed"] is True
    assert row["component"] == "core"
    assert row["degree_score"] == 5
    assert row["gloss"] == "bring into existence"
    assert row["frequency"] == 6.4


def test_collapse_seed_surfaces_groups_pos_nodes_and_prefers_common_early_words() -> None:
    rows = [
        {
            "node_id": "thing::n",
            "lemma": "thing",
            "surface_word": "thing",
            "pos": "n",
            "is_seed": True,
            "degree_score": 4,
            "frequency": 5.0,
            "age_of_acquisition": 4.0,
            "concreteness": 3.0,
        },
        {
            "node_id": "thing::v",
            "lemma": "thing",
            "surface_word": "thing",
            "pos": "v",
            "is_seed": True,
            "degree_score": 9,
            "frequency": 5.0,
            "age_of_acquisition": 5.0,
            "concreteness": 1.0,
        },
        {
            "node_id": "rare::n",
            "lemma": "rare",
            "surface_word": "rare",
            "pos": "n",
            "is_seed": True,
            "degree_score": 100,
            "frequency": None,
            "age_of_acquisition": None,
            "concreteness": None,
        },
        {
            "node_id": "child::n",
            "lemma": "child",
            "surface_word": "child",
            "pos": "n",
            "is_seed": False,
            "degree_score": 50,
            "frequency": 7.0,
            "age_of_acquisition": 3.0,
            "concreteness": 4.0,
        },
    ]

    surfaces = collapse_seed_surfaces(rows)

    assert [surface["lemma"] for surface in surfaces] == ["thing", "rare"]
    assert surfaces[0]["seed_node_count"] == 2
    assert surfaces[0]["parts_of_speech"] == ["n", "v"]
    assert surfaces[0]["max_degree_score"] == 9
    assert surfaces[0]["mean_concreteness"] == 2.0


def test_suspicion_reasons_flags_unannotated_multiword_self_loop_seed() -> None:
    row = {
        "node_id": "foo_bar::n",
        "lemma": "foo_bar",
        "gloss": "a taxonomic family",
        "frequency": None,
        "age_of_acquisition": None,
        "concreteness": None,
    }

    reasons = suspicion_reasons(row, {"foo_bar::n": {"foo_bar::n"}})

    assert reasons == [
        "multiword",
        "missing_frequency",
        "missing_age_of_acquisition",
        "missing_concreteness",
        "self_loop",
        "domain_or_named_entity_like",
    ]


def test_seed_surface_outputs_are_directly_consumable(tmp_path) -> None:
    surfaces = [
        {
            "lemma": "make",
            "surface_word": "make",
            "seed_node_count": 2,
            "source_node_ids": ["make::n", "make::v"],
            "parts_of_speech": ["n", "v"],
            "max_degree_score": 12,
            "best_frequency": 6.1,
            "earliest_age_of_acquisition": 3.4,
            "mean_concreteness": 2.0,
        }
    ]
    surfaces_path = tmp_path / "surfaces.csv"
    words_path = tmp_path / "words.txt"

    write_seed_surfaces_csv(surfaces_path, surfaces)
    write_seed_words(words_path, surfaces)

    assert surfaces_path.read_text(encoding="utf-8").splitlines() == [
        "lemma,surface_word,seed_node_count,source_node_ids,parts_of_speech,max_degree_score,best_frequency,earliest_age_of_acquisition,mean_concreteness",
        "make,make,2,make::n;make::v,n;v,12,6.1,3.4,2.0",
    ]
    assert words_path.read_text(encoding="utf-8") == "make\n"
