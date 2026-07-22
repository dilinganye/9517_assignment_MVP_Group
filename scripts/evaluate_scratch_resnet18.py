"""Evaluate a selected scratch-ResNet18 checkpoint on the held-out test manifest."""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.data import create_dataloader, create_dataset
from src.deep_learning import create_scratch_resnet18, load_model_weights
from src.evaluation import evaluate_class_scores


def parse_args():
    """Parse the reproducible final-evaluation settings for scratch ResNet18."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, default=config.DATA_RAW_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_ROOT / "scratch_resnet18" / "final_evaluation",
    )
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--num-workers", type=int, default=4)
    return parser.parse_args()


def create_eval_transform():
    """Create the deterministic image transform used for validation and test data."""

    return transforms.Compose(
        [
            transforms.Resize(config.IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(config.IMG_MEAN, config.IMG_STD),
        ]
    )


def save_predictions(path: Path, samples, targets, predictions, scores):
    """Write per-image predictions and Top-5 labels in shared manifest order."""

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["file_path", "label", "predicted_label", "correct", "top5_labels"],
        )
        writer.writeheader()
        for sample, target, prediction, sample_scores in zip(
            samples,
            targets,
            predictions,
            scores,
        ):
            top5_labels = np.argsort(sample_scores)[-5:][::-1]
            writer.writerow(
                {
                    "file_path": sample[0],
                    "label": int(target),
                    "predicted_label": int(prediction),
                    "correct": bool(prediction == target),
                    "top5_labels": " ".join(map(str, top5_labels)),
                }
            )


def save_confusion_matrix_plot(confusion, path: Path):
    """Save a label-free full-class heatmap for high-level confusion inspection."""

    figure, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(confusion, interpolation="nearest", cmap="Blues")
    axis.set(title="Test confusion matrix", xlabel="Predicted label", ylabel="True label")
    axis.set_xticks([])
    axis.set_yticks([])
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main():
    """Run one held-out test evaluation and write the common output artifacts."""

    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the scratch evaluation entry point")

    device = torch.device("cuda")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    test_dataset = create_dataset(
        "test",
        image_root=args.image_root,
        transform=create_eval_transform(),
    )
    test_loader = create_dataloader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    model = create_scratch_resnet18()
    checkpoint = load_model_weights(args.checkpoint, model, device)
    model.eval()
    all_scores = []
    all_targets = []
    start_time = time.perf_counter()

    with torch.inference_mode():
        for inputs, targets in test_loader:
            all_scores.append(model(inputs.to(device)).cpu().numpy())
            all_targets.append(targets.numpy())

    evaluation_seconds = time.perf_counter() - start_time
    scores = np.concatenate(all_scores)
    targets = np.concatenate(all_targets)
    evaluation = evaluate_class_scores(targets, scores, config.NUM_CLASSES)
    metrics = evaluation["metrics"]
    metrics["evaluation_seconds"] = evaluation_seconds
    metrics["samples_per_second"] = len(targets) / evaluation_seconds

    with (args.output_dir / "metrics.json").open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
    with (args.output_dir / "evaluation_config.json").open("w", encoding="utf-8") as file:
        json.dump(
            {
                "batch_size": args.batch_size,
                "checkpoint": str(args.checkpoint),
                "checkpoint_epoch": checkpoint["epoch"] + 1,
                "device": str(device),
                "image_root": str(args.image_root),
                "num_workers": args.num_workers,
                "split": "test",
            },
            file,
            indent=2,
        )

    save_predictions(
        args.output_dir / "predictions.csv",
        test_dataset.samples,
        targets,
        evaluation["predictions"],
        scores,
    )
    np.savetxt(
        args.output_dir / "confusion_matrix.csv",
        evaluation["confusion_matrix"],
        fmt="%d",
        delimiter=",",
    )
    save_confusion_matrix_plot(
        evaluation["confusion_matrix"],
        args.output_dir / "confusion_matrix.png",
    )

    print(json.dumps(metrics, indent=2))
    print(f"Outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
