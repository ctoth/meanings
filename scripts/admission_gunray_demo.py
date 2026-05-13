"""gunray demonstrator: the admission dialectical tree is the rationale.

For a handful of ICs -- chiefly ``ic:no`` -- we build the equivalent small
``DefeasibleTheory`` and render the dialectical tree showing the symbol-only
block rule (``r_block_symbol_only``) defeating the lexical-admit rule
(``r_admit_lexical``) for the *Nobelium* reading, and *not* defeating it for the
*negation* reading.

The per-IC admission evaluator in ``meanings.admission`` does the same thing by
ordered-rule evaluation (no argument enumeration needed at scale); this script
shows that the small case is exactly a DeLP dialectical tree, so "the dialectical
tree is the rationale" is concrete, not hand-wave.

Run::  uv run python scripts/admission_gunray_demo.py
Writes the mermaid renders into reports/ and prints the trees to stdout.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gunray import (
    CompositePreference,
    DefeasibleTheory,
    GeneralizedSpecificity,
    Rule,
    SuperiorityPreference,
    answer,
    build_arguments,
    build_tree,
    render_tree,
    render_tree_mermaid,
)
from gunray.types import GroundAtom

REPORTS = Path(__file__).resolve().parent.parent / "reports"


def _crit(theory: DefeasibleTheory):
    return CompositePreference(SuperiorityPreference(theory), GeneralizedSpecificity(theory))


def tree_for_atom(theory: DefeasibleTheory, atom: str):
    crit = _crit(theory)
    target = GroundAtom(atom, ())
    for arg in sorted(build_arguments(theory), key=lambda a: (str(a.conclusion), len(a.rules))):
        if arg.conclusion == target:
            t = build_tree(arg, crit, theory)
            return t, render_tree(t), render_tree_mermaid(t)
    return None, None, None


def write_mermaid(name: str, mermaid: str | None) -> None:
    if mermaid is None:
        return
    (REPORTS / name).write_text("```mermaid\n" + mermaid + "\n```\n", encoding="utf-8")
    print(f"  [wrote {REPORTS / name}]")


def banner(text: str) -> None:
    print()
    print("=" * 76)
    print(text)
    print("=" * 76)


def no_theory() -> DefeasibleTheory:
    """The ``ic:no`` admission case as a DeLP theory.

    Facts (the IC's member-sense observations):
      - ``lexical_reading_negation``  -- the form ``no`` has a lexical-word
        reading (the negation adverb), tagged via the surface short-token
        whitelist (high precision).
      - ``symbol_reading_nobelium``   -- the form ``No`` has a symbol-code
        reading (Nobelium), tagged via the surface short-token-case-rejection
        rule.
      - ``evidence_explicit``         -- the IC has source senses, glosses,
        tags, classifier rationale, and a (single-clean-form) provenance note.
      - ``every_reading_blocked_for_nobelium``  -- *if* we restrict attention to
        the Nobelium reading alone, every reading of *that* sub-cluster is in the
        blocked set (it is the only sense there).

    Rules:
      - ``r_admit_lexical : admit(ic_no) -< lexical_reading_negation, evidence_explicit``
      - ``r_admit_lexical_nob : admit(nobelium_only) -< symbol_reading_nobelium`` -- a
        (deliberately weak) admit-from-bare-form rule for the Nobelium-only view.
      - ``r_block_symbol_only : ~admit(nobelium_only) -< every_reading_blocked_for_nobelium``
        -- and ``r_block_symbol_only > r_admit_lexical_nob``.

    So: ``admit(ic_no)`` is warranted (the negation reading is lexical and
    surface-backed, nothing attacks it); ``admit(nobelium_only)`` is NOT warranted
    -- the symbol-only block defeats it. The Nobelium *sense* is therefore
    excluded from ``ic:no``'s admitted reading set; the negation reading is the
    admitted one.
    """
    return DefeasibleTheory(
        facts={
            "lexical_reading_negation": {()},
            "symbol_reading_nobelium": {()},
            "evidence_explicit": {()},
            "every_reading_blocked_for_nobelium": {()},
        },
        strict_rules=(),
        defeasible_rules=(
            Rule(id="r_admit_lexical", head="admit_ic_no",
                 body=["lexical_reading_negation", "evidence_explicit"]),
            Rule(id="r_admit_lexical_nob", head="admit_nobelium_only",
                 body=["symbol_reading_nobelium"]),
            Rule(id="r_block_symbol_only", head="~admit_nobelium_only",
                 body=["every_reading_blocked_for_nobelium"]),
        ),
        superiority=(("r_block_symbol_only", "r_admit_lexical_nob"),),
        conflicts=(),
    )


def main() -> int:
    banner("gunray demonstrator -- ic:no admission as a DeLP dialectical tree")
    theory = no_theory()
    crit = _crit(theory)
    print("rules:")
    print("  r_admit_lexical    : admit_ic_no          -< lexical_reading_negation, evidence_explicit")
    print("  r_admit_lexical_nob: admit_nobelium_only  -< symbol_reading_nobelium")
    print("  r_block_symbol_only: ~admit_nobelium_only -< every_reading_blocked_for_nobelium")
    print("superiority: r_block_symbol_only > r_admit_lexical_nob")
    print("facts: lexical_reading_negation, symbol_reading_nobelium, evidence_explicit,")
    print("       every_reading_blocked_for_nobelium")
    print()
    a_no = answer(theory, GroundAtom("admit_ic_no", ()), crit).name
    a_nob = answer(theory, GroundAtom("admit_nobelium_only", ()), crit).name
    n_a_nob = answer(theory, GroundAtom("~admit_nobelium_only", ()), crit).name
    print(f"answer admit_ic_no          : {a_no}")
    print(f"answer admit_nobelium_only  : {a_nob}")
    print(f"answer ~admit_nobelium_only : {n_a_nob}")
    assert a_no == "YES", a_no
    assert a_nob == "NO", a_nob
    assert n_a_nob == "YES", n_a_nob

    print()
    print("dialectical tree for admit_ic_no (the negation reading -- nothing attacks it):")
    t1, uni1, mer1 = tree_for_atom(theory, "admit_ic_no")
    print(uni1)
    write_mermaid("gunray-demo-admission-no-negation.mmd", mer1)

    print()
    print("dialectical tree for admit_nobelium_only (the Nobelium reading -- r_block_symbol_only defeats r_admit_lexical_nob):")
    t2, uni2, mer2 = tree_for_atom(theory, "admit_nobelium_only")
    print(uni2)
    write_mermaid("gunray-demo-admission-no-nobelium.mmd", mer2)

    print()
    print("dialectical tree for ~admit_nobelium_only (the block itself, warranted):")
    t3, uni3, mer3 = tree_for_atom(theory, "~admit_nobelium_only")
    print(uni3)
    write_mermaid("gunray-demo-admission-no-block.mmd", mer3)

    banner("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
