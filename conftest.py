"""Ensure the ``src`` layout is importable when tests run under an external pytest
(the project venv does not bundle pytest)."""
import sys
from pathlib import Path

_SRC = str(Path(__file__).parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
