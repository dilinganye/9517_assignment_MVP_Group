"""Dependency-light metrics for class-incremental continual learning."""


def create_accuracy_matrix(num_tasks: int):
    """Create an empty task-by-task accuracy matrix.

    Row ``t`` records evaluations made immediately after learning task ``t``.
    Only columns ``0`` through ``t`` may contain values.
    """

    if num_tasks < 1:
        raise ValueError("num_tasks must be positive")
    return [[None] * num_tasks for _ in range(num_tasks)]


def record_accuracy_row(matrix, task_id: int, task_accuracies):
    """Record accuracy on every seen task after completing ``task_id``."""

    num_tasks = _validate_matrix_shape(matrix)
    if not 0 <= task_id < num_tasks:
        raise ValueError(f"task_id must be between 0 and {num_tasks - 1}")

    expected_task_ids = set(range(task_id + 1))
    provided_task_ids = set(task_accuracies)
    if provided_task_ids != expected_task_ids:
        raise ValueError("task_accuracies must contain exactly the seen task IDs")
    if any(value is not None for value in matrix[task_id]):
        raise ValueError(f"Accuracy row for task {task_id} is already recorded")

    for evaluated_task_id, accuracy in task_accuracies.items():
        matrix[task_id][evaluated_task_id] = _validate_accuracy(accuracy)
    return matrix


def summarize_after_task(matrix, task_id: int):
    """Summarize current, old, seen, and forgetting metrics after one task."""

    _validate_recorded_row(matrix, task_id)
    row = matrix[task_id][: task_id + 1]
    old_accuracies = row[:task_id]
    return {
        "task_id": task_id,
        "current_task_accuracy": row[task_id],
        "old_task_accuracy": _mean(old_accuracies) if old_accuracies else None,
        "seen_task_accuracy": _mean(row),
        "average_forgetting": average_forgetting(matrix, task_id),
    }


def average_forgetting(matrix, task_id: int):
    """Return mean loss from each old task's prior best accuracy.

    Forgetting is undefined after the first task because no old task exists.
    """

    _validate_recorded_row(matrix, task_id)
    if task_id == 0:
        return None

    forgetting = []
    for old_task_id in range(task_id):
        historical_scores = [
            _recorded_accuracy(matrix, evaluated_after, old_task_id)
            for evaluated_after in range(old_task_id, task_id)
        ]
        forgetting.append(max(historical_scores) - matrix[task_id][old_task_id])
    return _mean(forgetting)


def _validate_matrix_shape(matrix):
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("matrix must be a non-empty square list")
    return len(matrix)


def _validate_recorded_row(matrix, task_id: int):
    num_tasks = _validate_matrix_shape(matrix)
    if not 0 <= task_id < num_tasks:
        raise ValueError(f"task_id must be between 0 and {num_tasks - 1}")
    for evaluated_task_id in range(task_id + 1):
        _recorded_accuracy(matrix, task_id, evaluated_task_id)


def _recorded_accuracy(matrix, after_task_id: int, evaluated_task_id: int):
    accuracy = matrix[after_task_id][evaluated_task_id]
    if accuracy is None:
        raise ValueError(
            f"Missing accuracy after task {after_task_id} on task {evaluated_task_id}"
        )
    return _validate_accuracy(accuracy)


def _validate_accuracy(accuracy):
    accuracy = float(accuracy)
    if not 0.0 <= accuracy <= 1.0:
        raise ValueError("accuracy must be between 0 and 1")
    return accuracy


def _mean(values):
    return sum(values) / len(values)
