"""Reproducibility helpers.

Sets seeds for Python ``random``, NumPy and PyTorch (CPU + all CUDA
devices when present) and disables cuDNN autotuning so repeated runs on
the same machine/versions are as deterministic as practical.

Known irreducible sources of nondeterminism (documented in beam-ai/README):
- GPU kernels using atomic adds (some backward passes) even with
  deterministic algorithms requested;
- different hardware / library versions producing different floating
  point results;
- dropout during training is seeded but still varies the *training*
  trajectory across framework versions.
"""

from __future__ import annotations

import os
import random


def set_seeds(seed: int, deterministic_torch: bool = True) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:  # pragma: no cover - numpy ships with torch stack
        pass

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():  # pragma: no cover - CPU dev machines
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.benchmark = False
        if deterministic_torch:
            try:
                torch.use_deterministic_algorithms(True, warn_only=True)
            except TypeError:  # older torch without warn_only
                torch.use_deterministic_algorithms(True)
    except ImportError:
        # Torch-free environments (e.g. pure config tests) are fine.
        pass
