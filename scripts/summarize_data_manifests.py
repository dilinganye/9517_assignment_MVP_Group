import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config  # noqa: E402


SPLITS = {
    "train": config.TRAIN_CSV,
    "val": config.VAL_CSV,
    "test": config.TEST_CSV,
}


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_values(rows, column):
    counts = {}
    for row in rows:
        value = row[column]
        counts[value] = counts.get(value, 0) + 1
    return counts


def summarize_split(name, rows):
    label_counts = count_values(rows, "label")
    category_counts = count_values(rows, "category_id")
    counts = list(label_counts.values())
    return {
        "rows": len(rows),
        "labels": len(label_counts),
        "categories": len(category_counts),
        "min_images_per_label": min(counts) if counts else 0,
        "max_images_per_label": max(counts) if counts else 0,
        "first_file_path": rows[0]["file_path"] if rows else None,
        "split": name,
    }


def build_summary():
    class_rows = read_csv(config.CLASS_LIST_CSV)
    split_rows = {name: read_csv(path) for name, path in SPLITS.items()}
    paths_by_split = {
        name: {row["file_path"] for row in rows}
        for name, rows in split_rows.items()
    }

    summary = {
        "source_notebooks": [
            "src/data/data00_choosing500.ipynb",
            "src/data/data01_json_wash.ipynb",
        ],
        "selection_config": {
            "random_seed": config.RANDOM_SEED,
            "num_classes": config.NUM_CLASSES,
            "train_per_class": config.NUM_TRAIN_PER_CLASS,
            "val_per_class": config.NUM_VAL_PER_CLASS,
            "test_per_class": config.NUM_TEST_PER_CLASS,
        },
        "class_list": {
            "path": str(config.CLASS_LIST_CSV.relative_to(PROJECT_ROOT)),
            "rows": len(class_rows),
            "kingdom_counts": count_values(class_rows, "kingdom"),
        },
        "splits": {
            name: {
                "path": str(SPLITS[name].relative_to(PROJECT_ROOT)),
                **summarize_split(name, rows),
            }
            for name, rows in split_rows.items()
        },
        "overlap_counts": {
            "train_val": len(paths_by_split["train"].intersection(paths_by_split["val"])),
            "train_test": len(paths_by_split["train"].intersection(paths_by_split["test"])),
            "val_test": len(paths_by_split["val"].intersection(paths_by_split["test"])),
        },
    }
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the committed iNaturalist manifest outputs from the data notebooks."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Prints to stdout when omitted.",
    )
    args = parser.parse_args()

    summary = build_summary()
    text = json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
