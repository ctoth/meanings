from __future__ import annotations

from meanings.identity_clusters import (
    HIGH_CONFIDENCE_SPELLING_VARIANTS,
    identity_cluster_for_form,
    spelling_variant_index,
)


def test_spelling_variant_records_keep_all_forms() -> None:
    index = spelling_variant_index()

    assert index["color"].ic_id == "ic:color"
    assert index["colour"].ic_id == "ic:color"
    assert index["color"].forms == frozenset({"color", "colour"})
    assert index["color"].rationale


def test_expected_variant_pairs_share_identity_cluster() -> None:
    expected_pairs = (
        ("color", "colour"),
        ("center", "centre"),
        ("theater", "theatre"),
        ("ax", "axe"),
    )

    for left, right in expected_pairs:
        left_record = identity_cluster_for_form(left)
        right_record = identity_cluster_for_form(right)
        assert left_record is not None
        assert right_record is not None
        assert left_record.ic_id == right_record.ic_id
        assert {left, right}.issubset(left_record.forms)


def test_variant_forms_are_unique_across_records() -> None:
    all_forms = [form for record in HIGH_CONFIDENCE_SPELLING_VARIANTS for form in record.forms]

    assert len(all_forms) == len(set(all_forms))
