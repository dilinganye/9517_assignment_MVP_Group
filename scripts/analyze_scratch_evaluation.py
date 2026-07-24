"""Analyze saved scratch-ResNet18 test predictions without rerunning inference."""

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config


def parse_args():
    """Parse paths for post-hoc analysis of one saved final evaluation."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=config.TEST_CSV)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--top-pairs", type=int, default=20)
    parser.add_argument("--hardest-classes", type=int, default=15)
    return parser.parse_args()


def read_manifest(path: Path):
    """Read the label and species metadata needed to explain predictions."""

    required_columns = {"file_path", "label", "category_id", "category_name"}
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")

        metadata_by_label = {}
        labels_by_path = {}
        for row in reader:
            label = int(row["label"])
            metadata = {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
            }
            existing = metadata_by_label.setdefault(label, metadata)
            if existing != metadata:
                raise ValueError(f"Manifest has inconsistent metadata for label {label}")
            labels_by_path[row["file_path"]] = label

    expected_labels = set(range(len(metadata_by_label)))
    if set(metadata_by_label) != expected_labels:
        raise ValueError("Manifest labels must be contiguous from 0")
    return metadata_by_label, labels_by_path


def read_predictions(path: Path, labels_by_path, num_classes: int):
    """Read saved predictions and verify they still match the test manifest."""

    required_columns = {"file_path", "label", "predicted_label"}
    targets = []
    predictions = []
    seen_paths = set()
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Predictions are missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            target = int(row["label"])
            prediction = int(row["predicted_label"])
            if row["file_path"] in seen_paths:
                raise ValueError(f"Predictions contain a duplicate path: {row['file_path']}")
            seen_paths.add(row["file_path"])
            manifest_label = labels_by_path.get(row["file_path"])
            if manifest_label is None:
                raise ValueError(f"Prediction path is absent from the manifest: {row['file_path']}")
            if target != manifest_label:
                raise ValueError(f"Prediction label does not match manifest: {row['file_path']}")
            if not 0 <= prediction < num_classes:
                raise ValueError(f"Prediction has an invalid label: {prediction}")
            targets.append(target)
            predictions.append(prediction)

    if seen_paths != set(labels_by_path):
        raise ValueError("Prediction paths do not match the manifest")
    return np.asarray(targets), np.asarray(predictions)


def per_class_rows(confusion, metadata_by_label):
    """Return per-class precision, recall, F1, and support rows."""

    rows = []
    for label in range(len(metadata_by_label)):
        support = int(confusion[label].sum())
        predicted = int(confusion[:, label].sum())
        correct = int(confusion[label, label])
        precision = correct / predicted if predicted else 0.0
        recall = correct / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append(
            {
                "label": label,
                **metadata_by_label[label],
                "support": support,
                "correct": correct,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return rows


def write_rows(path: Path, rows, fieldnames):
    """Write a small analysis table with stable column order."""

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def confused_pair_rows(confusion, metadata_by_label, limit: int):
    """Return the most frequent off-diagonal true-to-predicted class pairs."""

    pairs = []
    for true_label, predicted_label in zip(*np.nonzero(confusion)):
        if true_label == predicted_label:
            continue
        pairs.append(
            {
                "true_label": int(true_label),
                "true_category_id": metadata_by_label[true_label]["category_id"],
                "true_category_name": metadata_by_label[true_label]["category_name"],
                "predicted_label": int(predicted_label),
                "predicted_category_id": metadata_by_label[predicted_label]["category_id"],
                "predicted_category_name": metadata_by_label[predicted_label]["category_name"],
                "count": int(confusion[true_label, predicted_label]),
            }
        )
    pairs.sort(key=lambda row: (-row["count"], row["true_label"], row["predicted_label"]))
    return pairs[:limit]


def display_name(row):
    """Keep species labels legible in a compact confusion plot."""

    name = row["category_name"]
    return name if len(name) <= 28 else f"{name[:25]}..."


def save_hardest_confusion_plot(confusion, hardest_rows, path: Path):
    """Save the within-subset confusion matrix for the lowest-recall classes."""

    labels = [row["label"] for row in hardest_rows]
    selected = confusion[np.ix_(labels, labels)]
    figure_size = max(10, len(labels) * 0.75)
    figure, axis = plt.subplots(figsize=(figure_size, figure_size))
    image = axis.imshow(selected, interpolation="nearest", cmap="Blues")
    axis.set(
        title="Held-out test confusion among the lowest-recall classes",
        xlabel="Predicted species",
        ylabel="True species",
    )
    names = [display_name(row) for row in hardest_rows]
    axis.set_xticks(range(len(labels)), names, rotation=90, fontsize=8)
    axis.set_yticks(range(len(labels)), names, fontsize=8)
    for row_index, column_index in zip(*np.nonzero(selected)):
        axis.text(column_index, row_index, str(selected[row_index, column_index]), ha="center", va="center", fontsize=7)
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main():
    """Write report-ready error-analysis artifacts from an existing final evaluation."""

    args = parse_args()
    if args.top_pairs < 1 or args.hardest_classes < 1:
        raise ValueError("--top-pairs and --hardest-classes must be at least 1")
    if not args.predictions.exists():
        raise FileNotFoundError(f"Predictions not found: {args.predictions}")
    if not args.manifest.exists():
        raise FileNotFoundError(f"Manifest not found: {args.manifest}")

    output_dir = args.output_dir or args.predictions.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_by_label, labels_by_path = read_manifest(args.manifest)
    targets, predictions = read_predictions(args.predictions, labels_by_path, len(metadata_by_label))
    confusion = np.zeros((len(metadata_by_label), len(metadata_by_label)), dtype=np.int64)
    np.add.at(confusion, (targets, predictions), 1)

    class_rows = per_class_rows(confusion, metadata_by_label)
    hardest_rows = sorted(class_rows, key=lambda row: (row["recall"], row["f1"], row["label"]))[
        : min(args.hardest_classes, len(class_rows))
    ]
    pairs = confused_pair_rows(confusion, metadata_by_label, args.top_pairs)
    write_rows(
        output_dir / "per_class_metrics.csv",
        class_rows,
        ["label", "category_id", "category_name", "support", "correct", "precision", "recall", "f1"],
    )
    write_rows(
        output_dir / "hardest_classes.csv",
        hardest_rows,
        ["label", "category_id", "category_name", "support", "correct", "precision", "recall", "f1"],
    )
    write_rows(
        output_dir / "most_confused_pairs.csv",
        pairs,
        [
            "true_label",
            "true_category_id",
            "true_category_name",
            "predicted_label",
            "predicted_category_id",
            "predicted_category_name",
            "count",
        ],
    )
    save_hardest_confusion_plot(
        confusion,
        hardest_rows,
        output_dir / "hardest_classes_confusion.png",
    )
    with (output_dir / "analysis_config.json").open("w", encoding="utf-8") as file:
        json.dump(
            {
                "predictions": str(args.predictions),
                "manifest": str(args.manifest),
                "num_samples": int(len(targets)),
                "num_classes": len(metadata_by_label),
                "top_pairs": args.top_pairs,
                "hardest_classes": len(hardest_rows),
            },
            file,
            indent=2,
        )

    print(f"Analysis outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
