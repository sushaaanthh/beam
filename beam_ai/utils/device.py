"""Device resolution: auto-detect CUDA, fall back to CPU, allow overrides."""

from __future__ import annotations


def resolve_device(preference: str = "auto") -> str:
    """Return a torch device string.

    ``auto``   -> cuda if available else cpu (development default).
    ``cpu``    -> force CPU.
    ``cuda``   -> require CUDA; raises RuntimeError when unavailable.
    """
    preference = (preference or "auto").lower()

    try:
        import torch
    except ImportError as exc:  # pragma: no cover - guarded by requirements
        raise RuntimeError(
            "PyTorch is required for training/inference. "
            "Install it from beam-ai/requirements.txt."
        ) from exc

    if preference == "cpu":
        return "cpu"
    if preference in {"cuda", "gpu"}:
        if not torch.cuda.is_available():
            raise RuntimeError(
                "device='cuda' requested but no CUDA-capable GPU is available. "
                "Use 'auto' or 'cpu'."
            )
        return "cuda"
    if preference == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    raise ValueError(f"Unknown device preference: {preference!r}")
