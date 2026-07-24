"""Verify continual-learning metric definitions with a synthetic matrix."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.advanced.continual_metrics import (
    average_forgetting,
    create_accuracy_matrix,
    record_accuracy_row,
    summarize_after_task,
)


def fail(message):
    raise SystemExit(f"[continual-metrics] FAIL: {message}")


def assert_close(actual, expected, label):
    if abs(actual - expected) > 1e-9:
        fail(f"{label} is {actual}, expected {expected}")


def main():
    """Check a known three-task accuracy matrix and invalid partial rows."""

    matrix = create_accuracy_matrix(3)
    record_accuracy_row(matrix, 0, {0: 0.80})
    record_accuracy_row(matrix, 1, {0: 0.50, 1: 0.90})
    record_accuracy_row(matrix, 2, {0: 0.40, 1: 0.70, 2: 0.85})

    first_summary = summarize_after_task(matrix, 0)
    final_summary = summarize_after_task(matrix, 2)
    if first_summary["old_task_accuracy"] is not None or first_summary["average_forgetting"] is not None:
        fail("first task metrics should not define old-task accuracy or forgetting")
    assert_close(final_summary["current_task_accuracy"], 0.85, "current-task accuracy")
    assert_close(final_summary["old_task_accuracy"], 0.55, "old-task accuracy")
    assert_close(final_summary["seen_task_accuracy"], 0.65, "seen-task accuracy")
    assert_close(final_summary["average_forgetting"], 0.30, "average forgetting")
    assert_close(average_forgetting(matrix, 2), 0.30, "standalone forgetting")

    try:
        record_accuracy_row(create_accuracy_matrix(2), 1, {0: 0.5})
    except ValueError:
        pass
    else:
        fail("partial seen-task rows must be rejected")

    print("[continual-metrics] PASS: matrix summaries and forgetting are consistent")


if __name__ == "__main__":
    main()
