"""Advanced-method utilities kept separate from the required baselines."""

from src.advanced.continual_learning import (
    build_class_task_plan,
    filter_manifest_samples,
    get_seen_task_ids,
    get_task_label_mapping,
    load_class_task_plan,
    normalise_task_ids,
    validate_class_task_plan,
)
from src.advanced.continual_metrics import (
    average_forgetting,
    create_accuracy_matrix,
    record_accuracy_row,
    summarize_after_task,
)

__all__ = [
    "build_class_task_plan",
    "create_accuracy_matrix",
    "filter_manifest_samples",
    "get_seen_task_ids",
    "get_task_label_mapping",
    "load_class_task_plan",
    "normalise_task_ids",
    "record_accuracy_row",
    "summarize_after_task",
    "validate_class_task_plan",
    "average_forgetting",
]
