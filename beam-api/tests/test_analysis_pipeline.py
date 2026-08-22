"""
End-to-End Tests for B.E.A.M. Analysis, Models, Dashboard, Datasets, and Insights.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root / "beam-api"))
sys.path.insert(0, str(root / "beam-ai"))

from app.main import app

client = TestClient(app)


def test_root_and_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

    health = client.get("/api/v1/health")
    assert health.status_code == 200


def test_analyze_roberta():
    payload = {
        "text": "After benchmarking the transformer pipeline against our previous baseline, the inference latency dropped from 120ms to 16ms with zero degradation in accuracy! I am so thrilled with this result.",
        "source_type": "Discussion Forum",
        "model_name": "RoBERTa-v1.2 (Fine-tuned)",
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "primaryEmotion" in data
    assert data["confidence"] > 0
    assert len(data["distribution"]) > 0
    assert len(data["tokens"]) > 0
    assert len(data["signals"]) > 0


def test_analyze_bert_and_deberta():
    for model in ["BERT-Base-Emotion", "DeBERTa-v3-Affect"]:
        payload = {
            "text": "Super thrilled to announce B.E.A.M. v1.0 public release!",
            "source_type": "Social Feed",
            "model_name": model,
        }
        res = client.post("/api/v1/analyze", json=payload)
        assert res.status_code == 200
        assert res.json()["model"] == model


def test_dashboard_metrics():
    res = client.get("/api/v1/dashboard/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "analyses_metric" in data
    assert "emotion_distribution" in data
    assert len(data["recent_analyses"]) > 0


def test_datasets_and_models_endpoints():
    datasets = client.get("/api/v1/datasets")
    assert datasets.status_code == 200
    assert len(datasets.json()) > 0

    models = client.get("/api/v1/models")
    assert models.status_code == 200
    assert len(models.json()) >= 3


def test_insights_and_reports():
    insights = client.get("/api/v1/insights")
    assert insights.status_code == 200
    assert len(insights.json()["temporal_trends"]) == 7

    reports = client.get("/api/v1/reports")
    assert reports.status_code == 200


def test_csv_export():
    res = client.get("/api/v1/analyses/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "ID,Title,Source" in res.text


if __name__ == "__main__":
    print("Testing B.E.A.M. End-to-End Analysis Pipeline...")
    test_root_and_health()
    print("[PASS] test_root_and_health")
    test_analyze_roberta()
    print("[PASS] test_analyze_roberta")
    test_analyze_bert_and_deberta()
    print("[PASS] test_analyze_bert_and_deberta")
    test_dashboard_metrics()
    print("[PASS] test_dashboard_metrics")
    test_datasets_and_models_endpoints()
    print("[PASS] test_datasets_and_models_endpoints")
    test_insights_and_reports()
    print("[PASS] test_insights_and_reports")
    test_csv_export()
    print("[PASS] test_csv_export")
    print("\nALL 7 TESTS PASSED SUCCESSFULLY!")
