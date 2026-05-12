"""Transform raw psycholinguistic norm spreadsheets into the CSV shape that
``meanings.annotations`` consumes (``word,<field>`` with normalized keys).

Run from the repo root after the raw files are present in
``data/psycholinguistic/``::

    uv run python scripts/build_psycholinguistic_csvs.py

Raw sources expected (see data/psycholinguistic/README.md for provenance):
  - subtlexus.xlsx  (sheet "out1g", columns Word, Zipf-value)
  - aoa.xlsx        (sheet "Sheet1", columns Word, Rating.Mean)
  - conc.xlsx       (sheet "Sheet1", columns Word, Conc.M)
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data" / "psycholinguistic"


def normalize_key(text: object) -> str:
    return str(text).strip().lower().replace("-", "_").replace(" ", "_").replace("'", "")


def write_csv(out_name: str, frame: pd.DataFrame, word_col: str, value_col: str, field: str) -> int:
    out_path = DATA / out_name
    seen: set[str] = set()
    rows = 0
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["word", field])
        for _, row in frame.iterrows():
            word = row[word_col]
            if word is None or (isinstance(word, float) and math.isnan(word)):
                continue
            try:
                value = float(row[value_col])
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            key = normalize_key(word)
            if not key or key in seen:
                continue
            seen.add(key)
            writer.writerow([key, value])
            rows += 1
    print(f"{out_path.name}: {rows} rows")
    return rows


def main() -> None:
    write_csv(
        "frequency.csv",
        pd.read_excel(DATA / "subtlexus.xlsx", sheet_name="out1g"),
        "Word",
        "Zipf-value",
        "frequency",
    )
    write_csv(
        "age_of_acquisition.csv",
        pd.read_excel(DATA / "aoa.xlsx", sheet_name="Sheet1"),
        "Word",
        "Rating.Mean",
        "age_of_acquisition",
    )
    write_csv(
        "concreteness.csv",
        pd.read_excel(DATA / "conc.xlsx", sheet_name="Sheet1"),
        "Word",
        "Conc.M",
        "concreteness",
    )


if __name__ == "__main__":
    main()
