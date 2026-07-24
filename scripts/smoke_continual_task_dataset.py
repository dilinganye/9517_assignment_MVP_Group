"""Check continual-task manifest filtering without image or torch dependencies."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.advanced.continual_learning import (
    filter_manifest_samples,
    get_seen_task_ids,
    get_task_label_mapping,
    load_class_task_plan,
)


SPLITS = {
    "train": (config.TRAIN_CSV, config.NUM_TRAIN_PER_CLASS),
    "val": (config.VAL_CSV, config.NUM_VAL_PER_CLASS),
    "test": (config.TEST_CSV, config.NUM_TEST_PER_CLASS),
}


def fail(message):
    raise SystemExit(f"[continual-dataset] FAIL: {message}")


def main():
    """Verify current-task and seen-task filters against shared manifest counts."""

    plan_rows = load_class_task_plan(
        config.CONTINUAL_CLASS_TASKS_CSV,
        config.CONTINUAL_NUM_CLASSES,
        config.CONTINUAL_CLASSES_PER_TASK,
    )
    num_tasks = config.CONTINUAL_NUM_CLASSES // config.CONTINUAL_CLASSES_PER_TASK

    for task_id in range(num_tasks):
        current_mapping = get_task_label_mapping(plan_rows, [task_id])
        seen_mapping = get_task_label_mapping(plan_rows, get_seen_task_ids(task_id, num_tasks))
        current_labels = set(current_mapping.values())
        if current_labels != set(
            range(task_id * config.CONTINUAL_CLASSES_PER_TASK, (task_id + 1) * config.CONTINUAL_CLASSES_PER_TASK)
        ):
            fail(f"task {task_id} continual labels are not in the expected range")

        for split, (manifest_path, images_per_class) in SPLITS.items():
            current_samples = filter_manifest_samples(manifest_path, current_mapping)
            seen_samples = filter_manifest_samples(manifest_path, seen_mapping)
            expected_current = config.CONTINUAL_CLASSES_PER_TASK * images_per_class
            expected_seen = (task_id + 1) * expected_current
            if len(current_samples) != expected_current:
                fail(f"{split} task {task_id} has {len(current_samples)} rows, expected {expected_current}")
            if len(seen_samples) != expected_seen:
                fail(f"{split} seen tasks through {task_id} have {len(seen_samples)} rows, expected {expected_seen}")

    print("[continual-dataset] PASS: task and seen-task manifest filters are consistent")


if __name__ == "__main__":
    main()
