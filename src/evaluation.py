"""Shared classification metrics for final project evaluation."""

import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support


def evaluate_class_scores(targets, scores, num_classes: int, top_k: int = 5):
    """Evaluate class-score arrays with the project's common result fields.

    Args:
        targets: Ground-truth integer labels with shape ``(num_samples,)``.
        scores: Per-class scores or logits with shape
            ``(num_samples, num_classes)``. Scores do not need to be
            probabilities.
        num_classes: Number of classes represented by the shared manifests.
        top_k: Number of highest-scoring classes used for Top-k accuracy.

    Returns:
        A dictionary containing JSON-ready metrics, predicted labels, and the
        full confusion matrix. Callers write the large matrix separately from
        the compact metrics JSON.
    """

    targets = np.asarray(targets, dtype=np.int64)
    scores = np.asarray(scores)
    class_ids = np.arange(num_classes)

    if targets.ndim != 1:
        raise ValueError("targets must be a one-dimensional array")
    if scores.ndim != 2:
        raise ValueError("scores must be a two-dimensional array")
    if len(targets) != len(scores):
        raise ValueError("targets and scores must contain the same number of samples")
    if scores.shape[1] != num_classes:
        raise ValueError(f"scores must contain {num_classes} class columns")
    if not 1 <= top_k <= num_classes:
        raise ValueError("top_k must be between 1 and num_classes")
    if len(targets) == 0:
        raise ValueError("evaluation requires at least one sample")
    if targets.min() < 0 or targets.max() >= num_classes:
        raise ValueError("targets contain labels outside the configured class range")

    predictions = scores.argmax(axis=1)
    top_k_predictions = np.argsort(scores, axis=1)[:, -top_k:]
    precision, recall, f1, _ = precision_recall_fscore_support(
        targets,
        predictions,
        labels=class_ids,
        average="macro",
        zero_division=0,
    )

    return {
        "metrics": {
            "num_classes": int(num_classes),
            "num_samples": int(len(targets)),
            "top1": float((predictions == targets).mean()),
            "overall_accuracy": float((predictions == targets).mean()),
            f"top{top_k}": float(np.any(top_k_predictions == targets[:, None], axis=1).mean()),
            "macro_precision": float(precision),
            "macro_recall": float(recall),
            "macro_f1": float(f1),
        },
        "predictions": predictions,
        "confusion_matrix": confusion_matrix(targets, predictions, labels=class_ids),
    }
