from __future__ import annotations

import gzip
import json
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, TextIO

from meanings.lexical_graph import LexicalGraphBuild
from meanings.normalize import extract_lemma_candidates, normalize_lemma


ProgressCallback = Callable[[str], None]


def normalize_wiktextract_pos(pos: str) -> str:
    value = pos.strip().lower()
    if value in {"noun", "name", "proper-noun", "proper noun", "pronoun"}:
        return "n"
    if value in {"verb"}:
        return "v"
    if value in {"adj", "adjective", "det", "determiner"}:
        return "a"
    if value in {"adv", "adverb"}:
        return "r"
    return "x"


def open_jsonl_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open(encoding="utf-8")


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with open_jsonl_text(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected object on {path}:{line_number}")
            yield value


def sense_glosses(sense: dict[str, Any]) -> list[str]:
    glosses = sense.get("glosses", [])
    if not isinstance(glosses, list):
        return []
    return [str(gloss).strip() for gloss in glosses if str(gloss).strip()]


def iter_english_entries(rows: Iterable[dict[str, Any]], max_entries: int | None = None) -> Iterator[dict[str, Any]]:
    emitted = 0
    for row in rows:
        if row.get("lang_code") != "en":
            continue
        word = str(row.get("word", "")).strip()
        pos = str(row.get("pos", "")).strip()
        senses = row.get("senses", [])
        if not word or not pos or not isinstance(senses, list):
            continue
        if not any(isinstance(sense, dict) and sense_glosses(sense) for sense in senses):
            continue
        yield row
        emitted += 1
        if max_entries is not None and emitted >= max_entries:
            return


def build_wiktextract_graph(
    rows: Iterable[dict[str, Any]],
    *,
    lexicon_id: str,
    source_name: str,
    source_url: str | None = None,
    max_entries: int | None = None,
    progress: ProgressCallback | None = None,
) -> LexicalGraphBuild:
    definition_by_node: dict[str, str] = {}
    labels: dict[str, str] = {}
    pos_by_node: dict[str, str] = {}
    lemma_to_nodes: dict[str, set[str]] = {}
    stats: Counter[str] = Counter()

    for row in iter_english_entries(rows, max_entries=max_entries):
        stats["english_entries_seen"] += 1
        lemma = normalize_lemma(str(row["word"]))
        pos = normalize_wiktextract_pos(str(row["pos"]))
        key = f"{lemma}::{pos}"
        senses = [sense for sense in row.get("senses", []) if isinstance(sense, dict)]
        glosses: list[str] = []
        for sense in senses:
            glosses.extend(sense_glosses(sense))
        if not glosses:
            stats["entries_without_glosses"] += 1
            continue
        if key in definition_by_node:
            definition_by_node[key] = f"{definition_by_node[key]} ; {' ; '.join(glosses)}"
            stats["merged_duplicate_nodes"] += 1
        else:
            definition_by_node[key] = " ; ".join(glosses)
            labels[key] = f"{lemma} [{pos}] :: {glosses[0][:72]}"
            pos_by_node[key] = pos
            lemma_to_nodes.setdefault(lemma, set()).add(key)
        if progress is not None and stats["english_entries_seen"] % 100_000 == 0:
            progress(f"Parsed {stats['english_entries_seen']} English entries into {len(definition_by_node)} nodes")

    nodes = set(definition_by_node)
    adjacency = {node: set() for node in nodes}
    lemma_set = set(lemma_to_nodes)
    stats["definition_count"] = len(definition_by_node)

    for index, (target_node, definition) in enumerate(definition_by_node.items(), start=1):
        target_pos = pos_by_node[target_node]
        for candidate in extract_lemma_candidates(definition, lemma_set):
            stats["candidate_matches"] += 1
            same_pos = f"{candidate}::{target_pos}"
            if same_pos in nodes:
                adjacency[same_pos].add(target_node)
                stats["resolved_same_pos"] += 1
                continue
            choices = lemma_to_nodes.get(candidate, set())
            if len(choices) == 1:
                adjacency[next(iter(choices))].add(target_node)
                stats["resolved_unambiguous_pos"] += 1
            elif choices:
                stats["ambiguous_skipped"] += 1
            else:
                stats["missing_skipped"] += 1
        if progress is not None and index % 100_000 == 0:
            progress(f"Resolved definitions for {index} / {len(definition_by_node)} nodes")

    return LexicalGraphBuild(
        lexicon_id=lexicon_id,
        graph_type="wiktextract_english_lemma_pos",
        nodes=nodes,
        adjacency=adjacency,
        labels=labels,
        pos_by_node=pos_by_node,
        metadata={
            "language": "en",
            "resource_id": "kaikki-wiktextract",
            "source_name": source_name,
            "source_url": source_url,
            "construction": "wiktextract English entries, node=normalized_word::normalized_pos, definitions=all sense glosses concatenated",
            "resolution_stats": dict(stats),
        },
        language="en",
        resource_id="kaikki-wiktextract",
    )
