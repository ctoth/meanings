from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


ANNOTATION_FIELDS = ("frequency", "concreteness", "age_of_acquisition", "imageability")


@dataclass(slots=True)
class AnnotationStore:
    values: dict[str, dict[str, float]] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)

    def add(self, key: str, field: str, value: float) -> None:
        self.values.setdefault(key, {})[field] = value

    def get(self, key: str, field: str) -> float | None:
        return self.values.get(key, {}).get(field)


def normalize_annotation_key(text: str) -> str:
    return text.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "")


def first_present(row: dict[str, str], names: tuple[str, ...]) -> str | None:
    lower = {key.lower(): value for key, value in row.items()}
    for name in names:
        value = lower.get(name)
        if value not in (None, ""):
            return value
    return None


def load_annotation_csvs(paths: list[Path]) -> AnnotationStore:
    store = AnnotationStore()
    for path in paths:
        if not path.exists():
            continue
        store.sources.append(str(path))
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                key_value = first_present(row, ("word", "lemma", "term", "node", "key"))
                if not key_value:
                    continue
                key = normalize_annotation_key(key_value)
                for field in ANNOTATION_FIELDS:
                    raw = first_present(row, (field, field.replace("_", ""), field.replace("_", " ")))
                    if not raw:
                        continue
                    try:
                        store.add(key, field, float(raw))
                    except ValueError:
                        continue
    return store


def annotation_coverage(nodes: set[str], annotations: AnnotationStore) -> dict[str, dict[str, int | float]]:
    coverage: dict[str, dict[str, int | float]] = {}
    total = len(nodes)
    for field in ANNOTATION_FIELDS:
        count = sum(1 for node in nodes if annotations.get(node.split("::", 1)[0], field) is not None)
        coverage[field] = {
            "count": count,
            "total": total,
            "fraction": count / total if total else 0.0,
        }
    return coverage


def component_annotation_summary(
    components: dict[str, set[str]],
    annotations: AnnotationStore,
) -> dict[str, dict[str, dict[str, float | int]]]:
    summary: dict[str, dict[str, dict[str, float | int]]] = {}
    for component_name, nodes in components.items():
        field_summary: dict[str, dict[str, float | int]] = {}
        for field in ANNOTATION_FIELDS:
            vals = [
                value
                for node in nodes
                if (value := annotations.get(node.split("::", 1)[0], field)) is not None
            ]
            field_summary[field] = {
                "count": len(vals),
                "mean": sum(vals) / len(vals) if vals else 0.0,
            }
        summary[component_name] = field_summary
    return summary

