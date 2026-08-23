"""Thin script wrapper: python beam-ai/scripts/train.py --config ..."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from beam_ai.training.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
