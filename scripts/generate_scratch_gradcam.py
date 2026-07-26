"""Generate a small Grad-CAM evidence set for the fixed scratch test result.

This script reuses the Grad-CAM procedure used by E, while keeping D's scratch
checkpoint, test predictions, and error-analysis artifacts separate. It does
not rerun whole-test inference or change model selection.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.deep_learning import create_scratch_resnet18, load_model_weights
from src.gradcam_selection import select_samples


def parse_args():
    """Parse immutable test artifacts and the small Grad-CAM selection size."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, default=config.DATA_RAW_ROOT)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--confused-pairs", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=config.TEST_CSV)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--correct-count", type=int, default=4)
    parser.add_argument("--incorrect-count", type=int, default=6)
    parser.add_argument("--confused-pair-count", type=int, default=5)
    parser.add_argument("--examples-per-pair", type=int, default=2)
    return parser.parse_args()


def read_manifest(path: Path):
    """Read species names and validate the committed label mapping."""

    required_columns = {"file_path", "label", "category_name"}
    metadata_by_label = {}
    labels_by_path = {}
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            label = int(row["label"])
            metadata = {"category_name": row["category_name"]}
            existing = metadata_by_label.setdefault(label, metadata)
            if existing != metadata:
                raise ValueError(f"Manifest has inconsistent metadata for label {label}")
            labels_by_path[row["file_path"]] = label
    if set(metadata_by_label) != set(range(len(metadata_by_label))):
        raise ValueError("Manifest labels must be contiguous from 0")
    return metadata_by_label, labels_by_path


def read_predictions(path: Path, labels_by_path, metadata_by_label):
    """Read fixed test predictions and enrich them with manifest species names."""

    required_columns = {"file_path", "label", "predicted_label"}
    rows = []
    seen_paths = set()
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Predictions are missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            file_path = row["file_path"]
            if file_path in seen_paths:
                raise ValueError(f"Predictions contain a duplicate path: {file_path}")
            seen_paths.add(file_path)
            true_label = int(row["label"])
            predicted_label = int(row["predicted_label"])
            if labels_by_path.get(file_path) != true_label:
                raise ValueError(f"Prediction label does not match the test manifest: {file_path}")
            if predicted_label not in metadata_by_label:
                raise ValueError(f"Prediction has an invalid label: {predicted_label}")
            rows.append(
                {
                    "file_path": file_path,
                    "true_label": true_label,
                    "true_name": metadata_by_label[true_label]["category_name"],
                    "predicted_label": predicted_label,
                    "predicted_name": metadata_by_label[predicted_label]["category_name"],
                    "correct": int(true_label == predicted_label),
                }
            )
    if not rows:
        raise ValueError("Predictions are empty")
    return rows


def read_confused_pairs(path: Path, valid_labels):
    """Read the existing post-hoc error-analysis pairs without recomputing them."""

    required_columns = {"true_label", "predicted_label", "count"}
    pairs = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Confused pairs are missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            true_label = int(row["true_label"])
            predicted_label = int(row["predicted_label"])
            count = int(row["count"])
            if true_label not in valid_labels or predicted_label not in valid_labels:
                raise ValueError("Confused pairs contain an invalid label")
            if true_label == predicted_label or count < 1:
                raise ValueError("Confused pairs must be positive off-diagonal errors")
            pairs.append((true_label, predicted_label, count))
    return sorted(pairs, key=lambda pair: (-pair[2], pair[0], pair[1]))


def create_eval_transform():
    """Match the deterministic Resize/normalisation used by scratch evaluation."""

    return transforms.Compose(
        [
            transforms.Resize(config.IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(config.IMG_MEAN, config.IMG_STD),
        ]
    )


def resolve_image_path(file_path: str, image_root: Path):
    """Resolve the relative image path stored in the committed test manifest."""

    path = Path(file_path)
    candidates = [path] if path.is_absolute() else [image_root / path, PROJECT_ROOT / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Image file not found: {file_path}")


class GradCAM:
    """Standard gradient-weighted class activation maps for one convolutional layer."""

    def __init__(self, model, target_layer):
        self.model = model
        self.activations = None
        self.gradients = None
        self.forward_handle = target_layer.register_forward_hook(self._save_activations)
        self.backward_handle = target_layer.register_full_backward_hook(self._save_gradients)

    def _save_activations(self, module, inputs, output):
        self.activations = output.detach()

    def _save_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, target_label):
        """Return one normalised heatmap and model probabilities for target_label."""

        self.model.zero_grad(set_to_none=True)
        logits = self.model(input_tensor)
        logits[:, target_label].sum().backward()
        if self.activations is None or self.gradients is None:
            raise RuntimeError("Grad-CAM hooks did not capture activations and gradients")
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = torch.nn.functional.interpolate(
            cam,
            size=input_tensor.shape[-2:],
            mode="bilinear",
            align_corners=False,
        ).squeeze(1)
        cam_min = cam.amin(dim=(1, 2), keepdim=True)
        cam_max = cam.amax(dim=(1, 2), keepdim=True)
        heatmap = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        return heatmap[0].cpu().numpy(), torch.softmax(logits.detach(), dim=1)[0]

    def close(self):
        """Remove hooks after the selected evidence set has been generated."""

        self.forward_handle.remove()
        self.backward_handle.remove()


def create_overlay(image: Image.Image, heatmap):
    """Blend a normalised Grad-CAM heatmap onto the model-input image size."""

    image_array = np.asarray(image, dtype=np.float32) / 255.0
    colours = plt.get_cmap("jet")(heatmap)[..., :3]
    return np.clip(0.55 * image_array + 0.45 * colours, 0.0, 1.0)


def save_figure(row, image_path, image, predicted_heatmap, true_heatmap, predicted_confidence, output_dir):
    """Write original, predicted-class, and true-class Grad-CAM views for one image."""

    output_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = "".join(character if character.isalnum() or character in "-_" else "_" for character in image_path.stem)
    figure_path = output_dir / f"{safe_stem}_true_{row['true_label']}_pred_{row['predicted_label']}.png"
    panel_count = 3 if row["correct"] else 4
    figure, axes = plt.subplots(1, panel_count, figsize=(5 * panel_count, 5))
    axes[0].imshow(image)
    axes[0].set(title="Original image")
    axes[1].imshow(predicted_heatmap, cmap="jet", vmin=0.0, vmax=1.0)
    axes[1].set(title=f"Predicted heatmap\n{row['predicted_name']}")
    axes[2].imshow(create_overlay(image, predicted_heatmap))
    axes[2].set(title=f"Predicted overlay\nConfidence: {predicted_confidence:.4f}")
    if not row["correct"]:
        axes[3].imshow(create_overlay(image, true_heatmap))
        axes[3].set(title=f"True-class overlay\n{row['true_name']}")
    for axis in axes:
        axis.axis("off")
    status = "Correct" if row["correct"] else "Incorrect"
    figure.suptitle(f"{status} | True: {row['true_name']} | Predicted: {row['predicted_name']}")
    figure.tight_layout()
    figure.savefig(figure_path, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return figure_path


def main():
    """Generate a compact scratch Grad-CAM evidence set from frozen test artifacts."""

    args = parse_args()
    counts = [args.correct_count, args.incorrect_count, args.confused_pair_count, args.examples_per_pair]
    if any(count < 0 for count in counts) or not any(counts):
        raise ValueError("Selection counts must be non-negative and cannot all be zero")
    for path, name in [
        (args.checkpoint, "Checkpoint"),
        (args.predictions, "Predictions"),
        (args.confused_pairs, "Confused pairs"),
        (args.manifest, "Manifest"),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"{name} not found: {path}")

    metadata_by_label, labels_by_path = read_manifest(args.manifest)
    rows = read_predictions(args.predictions, labels_by_path, metadata_by_label)
    pairs = read_confused_pairs(args.confused_pairs, set(metadata_by_label))
    selected_rows = select_samples(
        rows,
        pairs,
        args.correct_count,
        args.incorrect_count,
        args.confused_pair_count,
        args.examples_per_pair,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_scratch_resnet18()
    checkpoint = load_model_weights(args.checkpoint, model, device)
    model.eval()
    gradcam = GradCAM(model, model.layer4[-1])
    transform = create_eval_transform()
    figures_dir = args.output_dir / "figures"
    output_rows = []
    try:
        for row in selected_rows:
            image_path = resolve_image_path(row["file_path"], args.image_root)
            original_image = Image.open(image_path).convert("RGB")
            display_image = original_image.resize((config.IMG_SIZE[1], config.IMG_SIZE[0]))
            input_tensor = transform(original_image).unsqueeze(0).to(device)
            predicted_heatmap, probabilities = gradcam.generate(input_tensor, row["predicted_label"])
            reloaded_prediction = int(probabilities.argmax().item())
            if reloaded_prediction != row["predicted_label"]:
                raise RuntimeError(
                    "Saved prediction does not match the supplied checkpoint and input transform: "
                    f"{row['file_path']}"
                )
            true_heatmap = None
            if not row["correct"]:
                true_heatmap, _ = gradcam.generate(input_tensor, row["true_label"])
            figure_path = save_figure(
                row,
                image_path,
                display_image,
                predicted_heatmap,
                true_heatmap,
                float(probabilities[row["predicted_label"]].item()),
                figures_dir,
            )
            output_rows.append(
                {
                    **row,
                    "selection_reasons": ";".join(row["selection_reasons"]),
                    "predicted_confidence": float(probabilities[row["predicted_label"]].item()),
                    "gradcam_path": str(figure_path),
                }
            )
    finally:
        gradcam.close()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gradcam_summary.csv"
    fieldnames = [
        "file_path",
        "true_label",
        "true_name",
        "predicted_label",
        "predicted_name",
        "correct",
        "selection_reasons",
        "predicted_confidence",
        "gradcam_path",
    ]
    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    (args.output_dir / "gradcam_config.json").write_text(
        json.dumps(
            {
                "checkpoint": str(args.checkpoint),
                "checkpoint_epoch": checkpoint.get("epoch", -1) + 1,
                "predictions": str(args.predictions),
                "confused_pairs": str(args.confused_pairs),
                "manifest": str(args.manifest),
                "image_root": str(args.image_root),
                "device": str(device),
                "selected_samples": len(output_rows),
                "selection": {
                    "correct_count": args.correct_count,
                    "incorrect_count": args.incorrect_count,
                    "confused_pair_count": args.confused_pair_count,
                    "examples_per_pair": args.examples_per_pair,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Generated {len(output_rows)} scratch Grad-CAM figures on {device}.")
    print(f"Outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
