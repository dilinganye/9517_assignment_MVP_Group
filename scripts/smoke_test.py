import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config  # noqa: E402


EXPECTED_SPLITS = {
    "train": (config.TRAIN_CSV, config.NUM_CLASSES * config.NUM_TRAIN_PER_CLASS),
    "val": (config.VAL_CSV, config.NUM_CLASSES * config.NUM_VAL_PER_CLASS),
    "test": (config.TEST_CSV, config.NUM_CLASSES * config.NUM_TEST_PER_CLASS),
}

REQUIRED_COLUMNS = {"file_path", "label", "category_id", "category_name"}


def fail(message):
    raise SystemExit(f"[smoke] FAIL: {message}")


def read_manifest(split, csv_path, expected_rows):
    if not csv_path.exists():
        fail(f"{split} manifest not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            fail(f"{split} manifest missing columns: {', '.join(sorted(missing))}")

        rows = list(reader)

    if len(rows) != expected_rows:
        fail(f"{split} row count is {len(rows)}, expected {expected_rows}")

    labels = [int(row["label"]) for row in rows]
    unique_labels = set(labels)
    expected_labels = set(range(config.NUM_CLASSES))
    if unique_labels != expected_labels:
        fail(f"{split} labels do not match 0..{config.NUM_CLASSES - 1}")

    return rows


def check_split_counts(split, rows, expected_per_class):
    counts = {}
    for row in rows:
        label = int(row["label"])
        counts[label] = counts.get(label, 0) + 1

    wrong = {label: count for label, count in counts.items() if count != expected_per_class}
    if wrong:
        sample = sorted(wrong.items())[:5]
        fail(f"{split} per-class counts differ from {expected_per_class}: {sample}")


def main():
    manifests = {}

    for split, (csv_path, expected_rows) in EXPECTED_SPLITS.items():
        rows = read_manifest(split, csv_path, expected_rows)
        manifests[split] = rows

    check_split_counts("train", manifests["train"], config.NUM_TRAIN_PER_CLASS)
    check_split_counts("val", manifests["val"], config.NUM_VAL_PER_CLASS)
    check_split_counts("test", manifests["test"], config.NUM_TEST_PER_CLASS)

    paths_by_split = {
        split: {row["file_path"] for row in rows}
        for split, rows in manifests.items()
    }
    for left, right in [("train", "val"), ("train", "test"), ("val", "test")]:
        overlap = paths_by_split[left].intersection(paths_by_split[right])
        if overlap:
            fail(f"{left}/{right} file_path overlap: {len(overlap)}")

    print("[smoke] PASS: config paths and CSV manifests are consistent")


if __name__ == "__main__":
    main()
