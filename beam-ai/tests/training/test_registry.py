"""Registry tests — isolated to tmp_path (never touches beam-models/)."""

from __future__ import annotations

import json

import pytest

from beam_ai.registry.registry import Registry, RegistryError


@pytest.fixture()
def registry(tmp_path):
    return Registry(path=tmp_path / "registry.json")


def _register(registry, version="v001", status="training", metrics=None):
    return registry.register(
        model_name="roberta-emotion",
        model_version=version,
        task="emotion_classification",
        dataset_version="v001",
        artifact_path=f"beam-models/roberta-emotion/{version}",
        status=status,
        metrics=metrics,
    )


class TestRegistration:
    def test_register_and_get_roundtrip(self, registry):
        entry = _register(registry)
        fetched = registry.get("roberta-emotion", "v001")
        assert fetched == entry
        for field in (
            "model_name",
            "model_version",
            "task",
            "dataset_version",
            "created_at",
            "metrics",
            "artifact_path",
            "status",
        ):
            assert field in entry
        assert entry["metrics"] is None  # nothing measured yet -> None

    def test_re_register_replaces_same_version(self, registry):
        _register(registry)
        _register(registry, metrics={"f1_macro": 0.5})
        assert len(registry.list_entries()) == 1

    def test_unknown_model_raises(self, registry):
        with pytest.raises(RegistryError, match="No registry entry"):
            registry.require("ghost", "v999")


class TestStatusLifecycle:
    def test_metrics_flip_training_to_validated(self, registry):
        _register(registry)
        updated = registry.set_metrics("roberta-emotion", "v001", {"accuracy": 0.7})
        assert updated["status"] == "validated"

    def test_production_requires_validated(self, registry):
        _register(registry)  # status=training, no metrics
        with pytest.raises(RegistryError, match="production"):
            registry.update_status("roberta-emotion", "v001", "production")

    def test_production_requires_real_metrics(self, registry):
        _register(registry)
        registry.set_metrics("roberta-emotion", "v001", {})
        with pytest.raises(RegistryError, match="measured metrics"):
            registry.update_status("roberta-emotion", "v001", "production")

    def test_valid_promotion_to_production(self, tmp_path):
        registry = Registry(path=tmp_path / "r.json")
        _register(registry)
        registry.set_metrics("roberta-emotion", "v001", {"f1_macro": 0.61})
        promoted = registry.update_status("roberta-emotion", "v001", "production")
        assert promoted["status"] == "production"
        pointer = tmp_path / "production" / "roberta-emotion_v001.json"
        assert json.loads(pointer.read_text(encoding="utf-8"))["status"] == "production"

    def test_archived_cannot_jump_to_production(self, registry):
        _register(registry)
        registry.set_metrics("roberta-emotion", "v001", {"f1_macro": 0.6})
        registry.update_status("roberta-emotion", "v001", "production")
        registry.update_status("roberta-emotion", "v001", "archived")
        with pytest.raises(RegistryError, match="production"):
            registry.update_status("roberta-emotion", "v001", "production")

    def test_invalid_status_rejected(self, registry):
        with pytest.raises(RegistryError, match="Invalid status"):
            _register(registry, status="beta")

    def test_get_production_latest_wins(self, registry):
        _register(registry, version="v001")
        _register(registry, version="v002")
        registry.set_metrics("roberta-emotion", "v001", {"f1_macro": 0.5})
        registry.set_metrics("roberta-emotion", "v002", {"f1_macro": 0.6})
        registry.update_status("roberta-emotion", "v001", "production")
        registry.update_status("roberta-emotion", "v002", "production")
        assert registry.get_production()["model_version"] == "v002"


class TestPersistence:
    def test_registry_file_is_json_list(self, registry):
        _register(registry)
        data = json.loads(registry.path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
