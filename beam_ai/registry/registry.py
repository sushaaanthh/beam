"""Lightweight model registry (JSON file, no external services).

Deliberately simple so MLflow can replace it later without touching
callers: everything goes through the functions below.

Status lifecycle: training -> validated -> production -> archived.
Guard: a model can NEVER become 'production' unless it has real metrics
(i.e. a successful evaluation) and is currently 'validated'.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from beam_ai.utils.paths import MODELS_DIR

REGISTRY_FILE = MODELS_DIR / "registry.json"

ModelStatus = Literal["training", "validated", "production", "archived"]
VALID_STATUSES: tuple[str, ...] = ("training", "validated", "production", "archived")

REQUIRED_FIELDS = (
    "model_name",
    "model_version",
    "task",
    "dataset_version",
    "created_at",
    "metrics",
    "artifact_path",
    "status",
)


class RegistryError(ValueError):
    pass


class Registry:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else REGISTRY_FILE

    # ---------- persistence ----------

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise RegistryError(f"Registry file {self.path} must contain a JSON list.")
        return data

    def _write(self, entries: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(entries, handle, indent=2, ensure_ascii=False)
            os.replace(tmp_name, self.path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    # ---------- operations ----------

    def register(
        self,
        *,
        model_name: str,
        model_version: str,
        task: str,
        dataset_version: str,
        artifact_path: str | Path,
        status: ModelStatus = "training",
        metrics: dict | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        if status not in VALID_STATUSES:
            raise RegistryError(f"Invalid status {status!r}; expected {VALID_STATUSES}")
        entry = {
            "model_name": model_name,
            "model_version": model_version,
            "task": task,
            "dataset_version": dataset_version,
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "artifact_path": str(artifact_path),
            "status": status,
        }
        entries = self._read()
        key = (entry["model_name"], entry["model_version"])
        entries = [e for e in entries if (e["model_name"], e["model_version"]) != key]
        entries.append(entry)
        self._write(entries)
        return entry

    def get(self, model_name: str, model_version: str) -> dict[str, Any] | None:
        for entry in self._read():
            if entry["model_name"] == model_name and entry["model_version"] == model_version:
                return entry
        return None

    def require(self, model_name: str, model_version: str) -> dict[str, Any]:
        entry = self.get(model_name, model_version)
        if entry is None:
            raise RegistryError(
                f"No registry entry for {model_name} {model_version}. "
                f"Register artifacts before referencing them."
            )
        return entry

    def list_entries(self, status: ModelStatus | None = None) -> list[dict[str, Any]]:
        entries = self._read()
        if status:
            entries = [e for e in entries if e["status"] == status]
        return sorted(entries, key=lambda e: (e["model_name"], e["model_version"]))

    def set_metrics(self, model_name: str, model_version: str, metrics: dict) -> dict[str, Any]:
        entries = self._read()
        for entry in entries:
            if (entry["model_name"], entry["model_version"]) == (model_name, model_version):
                entry["metrics"] = metrics
                if entry["status"] == "training":
                    entry["status"] = "validated"
                self._write(entries)
                return entry
        raise RegistryError(f"Unknown model {model_name} {model_version}")

    def update_status(
        self, model_name: str, model_version: str, new_status: ModelStatus
    ) -> dict[str, Any]:
        if new_status not in VALID_STATUSES:
            raise RegistryError(f"Invalid status {new_status!r}; expected {VALID_STATUSES}")
        entries = self._read()
        for entry in entries:
            if (entry["model_name"], entry["model_version"]) == (model_name, model_version):
                if new_status == "production":
                    if entry["status"] != "validated":
                        raise RegistryError(
                            f"{model_name} {model_version} cannot be promoted to "
                            f"'production' from status '{entry['status']}'; "
                            f"run evaluation first (validated + real metrics required)."
                        )
                    if not entry.get("metrics"):
                        raise RegistryError(
                            "Promotion to production requires measured metrics; "
                            "none are recorded."
                        )
                entry["status"] = new_status
                self._write(entries)
                _sync_production_pointer(entry, new_status, self.path.parent / "production")
                return entry
        raise RegistryError(f"Unknown model {model_name} {model_version}")

    def get_production(self, model_name: str | None = None) -> dict[str, Any] | None:
        """Latest production entry (optionally for one model)."""
        candidates = [
            e
            for e in self.list_entries(status="production")
            if model_name is None or e["model_name"] == model_name
        ]
        return candidates[-1] if candidates else None


def _sync_production_pointer(
    entry: dict[str, Any], status: str, pointer_dir: Path | None = None
) -> None:
    """Maintain <models-root>/production/<name>_<version>.json pointers."""
    directory = pointer_dir or (MODELS_DIR / "production")
    directory.mkdir(parents=True, exist_ok=True)
    pointer = directory / f"{entry['model_name']}_{entry['model_version']}.json"
    if status == "production":
        pointer.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    elif pointer.exists():
        pointer.unlink()


def default_registry() -> Registry:
    return Registry()
