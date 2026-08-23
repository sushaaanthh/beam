"""Metrics tests — expected values computed by hand from a fixed case.

Case: labels [a, b, c]; y_true=[0,0,1,1,2]; y_pred=[0,1,1,1,2]
  accuracy = 4/5 = 0.8
  per class (p, r, f1): a=(1, .5, 2/3) b=(2/3, 1, .8) c=(1, 1, 1)
"""

from __future__ import annotations

import pytest

from beam_ai.evaluation.metrics import compute_classification_metrics

LABELS = ["a", "b", "c"]
Y_TRUE = [0, 0, 1, 1, 2]
Y_PRED = [0, 1, 1, 1, 2]


@pytest.fixture(scope="module")
def metrics():
    return compute_classification_metrics(Y_TRUE, Y_PRED, LABELS)


class TestComputedValues:
    def test_accuracy(self, metrics):
        assert metrics["accuracy"] == pytest.approx(0.8)

    def test_macro_averages(self, metrics):
        assert metrics["precision_macro"] == pytest.approx((1 + 2 / 3 + 1) / 3)
        assert metrics["recall_macro"] == pytest.approx((0.5 + 1 + 1) / 3)
        assert metrics["f1_macro"] == pytest.approx((2 / 3 + 0.8 + 1) / 3)

    def test_weighted_averages(self, metrics):
        assert metrics["precision_weighted"] == pytest.approx(
            (1 * 2 + (2 / 3) * 2 + 1 * 1) / 5
        )
        assert metrics["recall_weighted"] == pytest.approx((0.5 * 2 + 1 * 2 + 1 * 1) / 5)
        assert metrics["f1_weighted"] == pytest.approx(((2 / 3) * 2 + 0.8 * 2 + 1 * 1) / 5)

    def test_confusion_matrix_layout(self, metrics):
        # rows=true class, cols=predicted
        assert metrics["confusion_matrix"] == [[1, 1, 0], [0, 2, 0], [0, 0, 1]]

    def test_per_class_block(self, metrics):
        assert metrics["per_class"]["a"] == {
            "precision": pytest.approx(1.0),
            "recall": pytest.approx(0.5),
            "f1": pytest.approx(2 / 3),
            "support": 2,
        }
        assert metrics["per_class"]["c"]["support"] == 1

    def test_sample_count_recorded(self, metrics):
        assert metrics["sample_count"] == 5


class TestEdgeCases:
    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="empty"):
            compute_classification_metrics([], [], LABELS)

    def test_zero_division_guarded_not_crashing(self):
        # Class 'b' never predicted nor true -> zero_division handled as 0.
        result = compute_classification_metrics([0], [0], ["a", "b"])
        assert result["per_class"]["b"] == {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "support": 0,
        }
