from __future__ import annotations

from dataclasses import dataclass

from meanings.normalize import normalize_lemma


@dataclass(frozen=True, slots=True)
class IdentityClusterMerge:
    ic_id: str
    forms: frozenset[str]
    rationale: str
    evidence: tuple[str, ...]


HIGH_CONFIDENCE_SPELLING_VARIANTS: tuple[IdentityClusterMerge, ...] = (
    IdentityClusterMerge(
        ic_id="ic:color",
        forms=frozenset({"color", "colour"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.or_our",),
    ),
    IdentityClusterMerge(
        ic_id="ic:center",
        forms=frozenset({"center", "centre"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.er_re",),
    ),
    IdentityClusterMerge(
        ic_id="ic:theater",
        forms=frozenset({"theater", "theatre"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.er_re",),
    ),
    IdentityClusterMerge(
        ic_id="ic:ax",
        forms=frozenset({"ax", "axe"}),
        rationale="Standard spelling variants for the same ordinary lexical tool sense.",
        evidence=("spelling.variant.short_token",),
    ),
    IdentityClusterMerge(
        ic_id="ic:gray",
        forms=frozenset({"gray", "grey"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.a_e",),
    ),
    IdentityClusterMerge(
        ic_id="ic:honor",
        forms=frozenset({"honor", "honour"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.or_our",),
    ),
    IdentityClusterMerge(
        ic_id="ic:organize",
        forms=frozenset({"organize", "organise"}),
        rationale="US/UK spelling variants with shared ordinary lexical sense.",
        evidence=("spelling.us_uk.ize_ise",),
    ),
)


def spelling_variant_index(
    records: tuple[IdentityClusterMerge, ...] = HIGH_CONFIDENCE_SPELLING_VARIANTS,
) -> dict[str, IdentityClusterMerge]:
    index: dict[str, IdentityClusterMerge] = {}
    for record in records:
        for form in record.forms:
            normalized = normalize_lemma(form)
            if normalized in index:
                raise ValueError(f"Duplicate IC spelling variant form: {normalized}")
            index[normalized] = record
    return index


def identity_cluster_for_form(form: str) -> IdentityClusterMerge | None:
    return spelling_variant_index().get(normalize_lemma(form))
