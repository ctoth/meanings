"""Bridge between ``meanings`` definition digraphs and the ``argumentation`` library.

A ``meanings`` definition digraph is an :data:`~meanings.graph_analysis.Adjacency`
mapping ``u -> {v, ...}`` where the edge ``u -> v`` means "the word ``u`` occurs in
the definition (gloss) of the word ``v``". Two readings of that edge make sense as an
abstract argumentation framework:

* **Attack reading.** Treat ``u -> v`` as "``u`` attacks ``v``". This is a *Dung*
  ``ArgumentationFramework``. The grounded extension is then the unique
  least-fixed-point sceptical set: a word is *in* iff every word occurring in its
  definition is *out*, recursively. This is a formal cousin of leaf-stripping, but it
  is not the same set (see ``scripts/argumentation_bridge_oewn.py`` for the comparison).

* **Support reading.** Treat ``u -> v`` as "``u`` supports ``v``" -- the more honest
  reading of a definition ("you cannot accept ``v`` until you accept its definiens").
  This is a bipolar AF with an empty attack relation; the Cayrol set-defeat grounded
  extension of a support-only bipolar AF is trivially the whole argument set (nothing
  attacks anything), which is itself a finding about how little plain bipolar grounded
  semantics says here. The interesting structure on the support side lives in the
  *closure* / leaf-stripping the ``meanings`` repo already computes.

This module only constructs the ``argumentation`` data structures; it reuses
:mod:`meanings.graph_analysis` for SCC / kernel information and does not reimplement
any graph algorithms.
"""

from __future__ import annotations

from argumentation.bipolar import BipolarArgumentationFramework
from argumentation.dung import ArgumentationFramework

from meanings.graph_analysis import Adjacency, KernelAnalysis, induced_subgraph

__all__ = [
    "edges_of",
    "dung_attack_framework",
    "bipolar_support_framework",
    "kernel_attack_framework",
    "scc_attack_framework",
]


def edges_of(nodes: set[str], adjacency: Adjacency) -> frozenset[tuple[str, str]]:
    """All directed edges ``(u, v)`` with both endpoints in ``nodes``."""
    return frozenset(
        (source, target)
        for source, targets in adjacency.items()
        if source in nodes
        for target in targets
        if target in nodes
    )


def dung_attack_framework(nodes: set[str], adjacency: Adjacency) -> ArgumentationFramework:
    """Build a Dung AF under the *attack* reading: ``u -> v`` means "u attacks v".

    Self-loops (``u -> u``: a word in its own definition) become self-attacks, which is
    legal in a Dung AF and means such a node can never be in any extension.
    """
    return ArgumentationFramework(
        arguments=frozenset(nodes),
        defeats=edges_of(nodes, adjacency),
    )


def bipolar_support_framework(
    nodes: set[str], adjacency: Adjacency
) -> BipolarArgumentationFramework:
    """Build a bipolar AF under the *support* reading: ``u -> v`` means "u supports v".

    The attack relation is empty -- a plain definition digraph carries no conflict; the
    polysemy/prototype-exception attacks the ``meanings`` pipeline collapses away are
    exactly what would populate ``defeats`` if they were kept.
    """
    return BipolarArgumentationFramework(
        arguments=frozenset(nodes),
        defeats=frozenset(),
        supports=edges_of(nodes, adjacency),
    )


def kernel_attack_framework(analysis: KernelAnalysis, adjacency: Adjacency) -> ArgumentationFramework:
    """Dung AF (attack reading) restricted to the leaf-stripped Kernel subgraph."""
    kernel_adj = induced_subgraph(analysis.kernel_nodes, adjacency)
    return dung_attack_framework(analysis.kernel_nodes, kernel_adj)


def scc_attack_framework(scc: set[str], adjacency: Adjacency) -> ArgumentationFramework:
    """Dung AF (attack reading) restricted to one SCC's induced subgraph."""
    return dung_attack_framework(scc, induced_subgraph(scc, adjacency))
