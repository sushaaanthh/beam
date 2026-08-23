"""Evaluation metrics — thin, honest wrappers around scikit-learn.

Every number returned here is computed from real predictions passed in by
the caller. Nothing is synthesised.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def compute_classification_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    labels: Sequence[str],
) -> dict:
    """Full classification report for one evaluation pass."""
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        precision_recall_fscore_support,
    )

    if len(y_true) == 0:
        raise ValueError("No samples to evaluate: y_true is empty.")

    y_true_arr = np.asarray(y_true, dtype=int)
    y_pred_arr = np.asarray(y_pred, dtype=int)
    label_ids = list(range(len(labels)))

    accuracy = float(accuracy_score(y_true_arr, y_pred_arr))
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true_arr, y_pred_arr, average="macro", zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true_arr, y_pred_arr, average="weighted", zero_division=0
    )
    p_per, r_per, f_per, support = precision_recall_fscore_support(
        y_true_arr, y_pred_arr, labels=label_ids, zero_division=0
    )
    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=label_ids)

    return {
        "accuracy": accuracy,
        "precision_macro": float(precision_macro),
        "precision_weighted": float(precision_weighted),
        "recall_macro": float(recall_macro),
        "recall_weighted": float(recall_weighted),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "confusion_matrix": cm.tolist(),
        "per_class": {
            label: {
                "precision": float(p_per[i]),
                "recall": float(r_per[i]),
                "f1": float(f_per[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(labels)
        },
        "sample_count": int(len(y_true_arr)),
    }
