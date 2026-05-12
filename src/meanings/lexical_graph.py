from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from meanings.graph_analysis import Adjacency


@dataclass(slots=True)
class LexicalGraphBuild:
    lexicon_id: str
    graph_type: str
    nodes: set[str]
    adjacency: Adjacency
    labels: dict[str, str] = field(default_factory=dict)
    pos_by_node: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    resource_id: str = "oewn"

