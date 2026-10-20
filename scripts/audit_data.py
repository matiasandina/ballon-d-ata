#!/usr/bin/env python3
"""Repository-root entry point for the offline data-quality audit."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_quality import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
