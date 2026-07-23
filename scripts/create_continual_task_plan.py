"""Create or verify the fixed 100-class continual-learning task assignment."""

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.advanced.continual_learning import (
    PLAN_FIELDS,
    build_class_task_plan,
    validate_class_task_plan,
)


def parse_args():
    """Parse deterministic task-plan settings without requiring image files."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=config.CONTINUAL_CLASS_TASKS_CSV)
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED)
    parser.add_argument("--num-classes", type=int, default=config.CONTINUAL_NUM_CLASSES)
    parser.add_argument(
        "--classes-per-task",
        type=int,
        default=config.CONTINUAL_CLASSES_PER_TASK,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that an existing task plan matches the deterministic inputs.",
    )
    return parser.parse_args()


def load_label_metadata(manifest_path: Path):
    """Load the stable label-to-species metadata from the shared test manifest."""

    required_columns = {"label", "category_id", "category_name"}
    with manifest_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")

        metadata = {}
        for row in reader:
            label = int(row["label"])
            value = {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
            }
            existing = metadata.setdefault(label, value)
            if existing != value:
                raise ValueError(f"Manifest has inconsistent metadata for label {label}")

    if set(metadata) != set(range(config.NUM_CLASSES)):
        raise ValueError("Manifest labels do not match the shared 500-class range")
    return metadata


def normalise_rows(rows):
    """Convert numeric plan fields to strings for deterministic CSV comparison."""

    return [{field: str(row[field]) for field in PLAN_FIELDS} for row in rows]


def read_existing_plan(path: Path):
    """Read a committed plan with its exact expected CSV schema."""

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if tuple(reader.fieldnames or []) != PLAN_FIELDS:
            raise ValueError("Task plan columns do not match the expected schema")
        return list(reader)


def write_plan(path: Path, rows):
    """Write the compact committed task mapping used by later CL code."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(normalise_rows(rows))


def main():
    """Create or validate the reproducible fixed class-incremental task plan."""

    args = parse_args()
    metadata = load_label_metadata(config.TEST_CSV)
    expected_rows = build_class_task_plan(
        metadata,
        seed=args.seed,
        num_classes=args.num_classes,
        classes_per_task=args.classes_per_task,
    )
    validate_class_task_plan(
        expected_rows,
        num_classes=args.num_classes,
        classes_per_task=args.classes_per_task,
    )

    if args.check:
        if not args.output.exists():
            raise FileNotFoundError(f"Task plan not found: {args.output}")
        actual_rows = read_existing_plan(args.output)
        validate_class_task_plan(
            actual_rows,
            num_classes=args.num_classes,
            classes_per_task=args.classes_per_task,
        )
        if actual_rows != normalise_rows(expected_rows):
            raise ValueError("Task plan does not match the deterministic inputs")
        print(f"[continual-plan] PASS: {args.output}")
        return

    write_plan(args.output, expected_rows)
    print(
        f"Wrote {len(expected_rows)} classes across "
        f"{args.num_classes // args.classes_per_task} tasks to: {args.output}"
    )


if __name__ == "__main__":
    main()
