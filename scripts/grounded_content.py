"""Compute grounded content G = I(X;V) across base-assembler validation snapshots.

Frame: X is a target sense drawn uniformly from the selected target set; V is the
verdict the apparatus C emits per target (one of {closed, artifact, background,
external, circular}). The validator is deterministic in X, so H(V|X) = 0 and
I(X;V) = H(V). G in bits is therefore H(V) in bits per row times the row count.

The script also reports G under coarsened verdict alphabets to expose the
H(V) <= log K apparatus-resolution ceiling, and computes Delta-G per added base
entry across the two completed rule-promotion cycles (artifact-bucket,
background-bucket BR1).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

BAND = "closure_size_le_200"

SNAPSHOTS = [
    ("pre",      "reports/base-assembler-validation.pre.json",    "pre-artifact baseline"),
    ("bg-pre",   "reports/base-assembler-validation.bg-pre.json", "post-artifact / pre-background"),
    ("current",  "reports/base-assembler-validation.json",        "post-BR1 (current)"),
]

COARSENINGS = {
    "fine (5)":          None,
    "closed-vs-not (2)": {"closed": "closed", "*": "not-closed"},
    "triage (3)":        {"closed": "closed", "artifact": "noise", "background": "noise",
                          "external": "edge", "circular": "edge"},
}


def shannon_entropy_bits(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0, 0
    h = 0.0
    for n in counts.values():
        if n == 0:
            continue
        p = n / total
        h -= p * math.log2(p)
    return h, total


def coarsen(counts, mapping):
    if mapping is None:
        return dict(counts)
    out = {}
    for k, n in counts.items():
        new_k = mapping.get(k, mapping.get("*", k))
        out[new_k] = out.get(new_k, 0) + n
    return out


def load_band(path):
    data = json.loads(Path(path).read_text())
    l0 = data["evaluation"]["l0_only"]["bands"][BAND]["counts"]
    aug = data["evaluation"]["augmented"]["bands"][BAND]["counts"]
    base_l0 = data["evaluation"]["l0_only"]["base_size"]
    base_aug = data["evaluation"]["augmented"]["base_size"]
    return l0, aug, base_l0, base_aug


def fmt(x, w=10, p=4):
    return f"{x:>{w}.{p}f}"


def main():
    rows = []
    for label, path, descr in SNAPSHOTS:
        l0, aug, base_l0, base_aug = load_band(path)
        rows.append({
            "label": label, "descr": descr, "path": path,
            "l0_counts": l0, "aug_counts": aug,
            "base_l0": base_l0, "base_aug": base_aug,
        })

    print(f"# Grounded content G = I(X;V) across validation snapshots")
    print(f"# Band: {BAND}; X uniform over selected target rows; V deterministic; G = H(V)")
    print()

    for coarse_name, mapping in COARSENINGS.items():
        print(f"## Verdict coarsening: {coarse_name}")
        if mapping is not None:
            print(f"#   mapping: {mapping}")
        print()
        header = f"{'snapshot':<10} {'base':>6} {'H(V) bits/row':>14} {'G total bits':>14} {'rows':>7} {'K':>3} {'ceiling':>9}"
        print(header)
        print("-" * len(header))
        for r in rows:
            c = coarsen(r["aug_counts"], mapping)
            h, n = shannon_entropy_bits(c)
            g = h * n
            k = len(c)
            ceil = math.log2(k) if k > 1 else 0.0
            print(f"{r['label']:<10} {r['base_aug']:>6d} {fmt(h, 14, 4)} {fmt(g, 14, 1)} {n:>7d} {k:>3d} {fmt(ceil, 9, 4)}")
        print()

    print("## Per-cycle Delta-G under fine coarsening (augmented base)")
    print()
    print(f"{'cycle':<28} {'Delta base':>10} {'Delta G (bits)':>15} {'bits/base entry':>17} {'Delta rate@200':>15}")
    print("-" * 88)
    for (a, b, name) in [(0, 1, "artifact-bucket (Phase 2)"),
                          (1, 2, "background-bucket (BR1)")]:
        ra, rb = rows[a], rows[b]
        ha, na = shannon_entropy_bits(coarsen(ra["aug_counts"], None))
        hb, nb = shannon_entropy_bits(coarsen(rb["aug_counts"], None))
        dG = hb * nb - ha * na
        dB = rb["base_aug"] - ra["base_aug"]
        per = dG / dB if dB else float("nan")
        # closure rate from histogram (closed / non_truncated_total)
        rate_a = ra["aug_counts"].get("closed", 0) / na if na else 0.0
        rate_b = rb["aug_counts"].get("closed", 0) / nb if nb else 0.0
        d_rate = rate_b - rate_a
        print(f"{name:<28} {dB:>10d} {fmt(dG, 15, 2)} {fmt(per, 17, 2)} {fmt(d_rate, 15, 5)}")
    print()

    print("## L0-only sanity (apparatus held fixed; verdicts should be ~stable across snapshots)")
    print()
    header = f"{'snapshot':<10} {'base':>6} {'H(V) bits/row':>14} {'G total bits':>14} {'rows':>7}"
    print(header)
    print("-" * len(header))
    for r in rows:
        h, n = shannon_entropy_bits(r["l0_counts"])
        print(f"{r['label']:<10} {r['base_l0']:>6d} {fmt(h, 14, 4)} {fmt(h * n, 14, 1)} {n:>7d}")
    print()

    print("## Status histograms (augmented, fine)")
    print()
    keys = ["closed", "artifact", "background", "external", "circular"]
    print(f"{'snapshot':<10} " + " ".join(f"{k:>11}" for k in keys))
    for r in rows:
        cells = " ".join(f"{r['aug_counts'].get(k, 0):>11d}" for k in keys)
        print(f"{r['label']:<10} {cells}")


if __name__ == "__main__":
    main()
