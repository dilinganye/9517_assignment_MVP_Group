"""Deterministic task planning and manifest filtering for scratch CL."""

import csv
import random
from pathlib import Path


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


def load_class_task_plan(path: Path, num_classes: int, classes_per_task: int):
    """Read and validate the committed class-to-task mapping."""

    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if tuple(reader.fieldnames or []) != PLAN_FIELDS:
            raise ValueError("Task plan columns do not match the expected schema")
        rows = list(reader)
    validate_class_task_plan(rows, num_classes, classes_per_task)
    return rows


def get_seen_task_ids(task_id: int, num_tasks: int):
    """Return task IDs visible after completing the given sequential task."""

    if not 0 <= task_id < num_tasks:
        raise ValueError(f"task_id must be between 0 and {num_tasks - 1}")
    return tuple(range(task_id + 1))


def normalise_task_ids(task_ids):
    """Accept one task ID or an iterable of task IDs in a stable order."""

    if isinstance(task_ids, int):
        task_ids = (task_ids,)
    return tuple(sorted({int(task_id) for task_id in task_ids}))


def get_task_label_mapping(rows, task_ids):
    """Map source labels to fixed 0-99 continual labels for selected tasks."""

    task_ids = normalise_task_ids(task_ids)
    if not task_ids:
        raise ValueError("task_ids must not be empty")

    available_task_ids = {int(row["task_id"]) for row in rows}
    unknown = set(task_ids).difference(available_task_ids)
    if unknown:
        raise ValueError(f"Unknown task IDs: {', '.join(map(str, sorted(unknown)))}")

    return {
        int(row["source_label"]): int(row["continual_label"])
        for row in rows
        if int(row["task_id"]) in task_ids
    }


def filter_manifest_samples(manifest_path: Path, source_to_continual):
    """Filter a shared manifest and return samples with remapped CL labels."""

    required_columns = {"file_path", "label"}
    samples = []
    with Path(manifest_path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            source_label = int(row["label"])
            continual_label = source_to_continual.get(source_label)
            if continual_label is not None:
                samples.append((row["file_path"], continual_label))

    if not samples:
        raise ValueError(f"No samples matched the task plan in {manifest_path}")
    return samples
