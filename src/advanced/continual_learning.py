"""Deterministic class-task planning for the scratch continual-learning study."""

import random


PLAN_FIELDS = (
    "task_id",
    "task_label",
    "continual_label",
    "source_label",
    "category_id",
    "category_name",
)


def build_class_task_plan(label_metadata, seed: int, num_classes: int, classes_per_task: int):
    """Assign a seeded subset of source labels to equally sized sequential tasks."""

    if num_classes < 1 or classes_per_task < 1:
        raise ValueError("num_classes and classes_per_task must be positive")
    if num_classes % classes_per_task:
        raise ValueError("num_classes must be divisible by classes_per_task")

    source_labels = sorted(label_metadata)
    if num_classes > len(source_labels):
        raise ValueError("num_classes exceeds the available source labels")

    selected_labels = random.Random(seed).sample(source_labels, num_classes)
    return [
        {
            "task_id": continual_label // classes_per_task,
            "task_label": continual_label % classes_per_task,
            "continual_label": continual_label,
            "source_label": source_label,
            "category_id": label_metadata[source_label]["category_id"],
            "category_name": label_metadata[source_label]["category_name"],
        }
        for continual_label, source_label in enumerate(selected_labels)
    ]


def validate_class_task_plan(rows, num_classes: int, classes_per_task: int):
    """Validate the task partition before a CL training run consumes it."""

    if len(rows) != num_classes:
        raise ValueError(f"Plan has {len(rows)} rows, expected {num_classes}")
    if num_classes % classes_per_task:
        raise ValueError("num_classes must be divisible by classes_per_task")

    expected_tasks = num_classes // classes_per_task
    source_labels = set()
    continual_labels = set()
    task_labels = {task_id: set() for task_id in range(expected_tasks)}
    for row in rows:
        task_id = int(row["task_id"])
        task_label = int(row["task_label"])
        continual_label = int(row["continual_label"])
        source_label = int(row["source_label"])
        if task_id not in task_labels:
            raise ValueError(f"Plan has an invalid task_id: {task_id}")
        source_labels.add(source_label)
        continual_labels.add(continual_label)
        task_labels[task_id].add(task_label)

    if len(source_labels) != num_classes:
        raise ValueError("Plan source labels are not unique")
    if continual_labels != set(range(num_classes)):
        raise ValueError("Plan continual labels must be contiguous from 0")
    expected_task_labels = set(range(classes_per_task))
    if any(labels != expected_task_labels for labels in task_labels.values()):
        raise ValueError("Every task must contain each task-local label exactly once")
