"""Run the CUDA scratch-ResNet18 baseline on the shared manifests."""

import argparse
import csv
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from torch import optim
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.data import create_dataloader, create_dataset
from src.deep_learning import (
    create_scratch_resnet18,
    fit_scratch_model,
    load_checkpoint,
    plot_training_curves,
)


def parse_args():
    """Parse the small set of reproducible scratch-baseline settings."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", type=Path, default=config.DATA_RAW_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_ROOT / "scratch_resnet18",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--train-augmentation", action="store_true")
    return parser.parse_args()


def set_seed(seed: int):
    """Seed the CUDA training run as consistently as practical."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def create_transform(train_augmentation: bool = False):
    """Create the training or deterministic evaluation transform."""

    if train_augmentation:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(config.IMG_SIZE, scale=(0.75, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(config.IMG_MEAN, config.IMG_STD),
            ]
        )

    return transforms.Compose(
        [
            transforms.Resize(config.IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(config.IMG_MEAN, config.IMG_STD),
        ]
    )


def save_history(history, path: Path):
    """Write the epoch history in a simple table for later analysis."""

    fieldnames = ["epoch", "train_loss", "train_top1", "val_loss", "val_top1", "epoch_seconds"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for epoch, values in enumerate(
            zip(
                history["train_loss"],
                history["train_top1"],
                history["val_loss"],
                history["val_top1"],
                history.get("epoch_seconds", [None] * len(history["train_loss"])),
            ),
            start=1,
        ):
            writer.writerow(dict(zip(fieldnames, (epoch, *values))))


def get_git_commit():
    """Return the current commit when the script is run from a Git checkout."""

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=config.PROJECT_ROOT,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main():
    """Train or resume the CUDA scratch baseline and save local artifacts."""

    args = parse_args()
    if args.epochs < 1:
        raise ValueError("epochs must be at least 1")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the scratch baseline entry point")

    device = torch.device("cuda")
    set_seed(config.RANDOM_SEED)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_transform = create_transform(args.train_augmentation)
    eval_transform = create_transform()
    train_dataset = create_dataset(
        "train",
        image_root=args.image_root,
        transform=train_transform,
    )
    val_dataset = create_dataset("val", image_root=args.image_root, transform=eval_transform)
    train_loader = create_dataloader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True,
    )
    val_loader = create_dataloader(
        val_dataset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    model = create_scratch_resnet18()
    optimizer = optim.SGD(
        model.parameters(),
        lr=args.learning_rate,
        momentum=0.9,
        weight_decay=1e-4,
    )
    best_checkpoint_path = args.output_dir / "best_checkpoint.pt"
    last_checkpoint_path = args.output_dir / "last_checkpoint.pt"
    start_epoch = 0
    history = None
    best_val_top1 = None

    run_config = {
        "batch_size": args.batch_size,
        "device": str(device),
        "epochs_this_run": args.epochs,
        "git_commit": get_git_commit(),
        "image_mean": config.IMG_MEAN,
        "image_root": str(args.image_root),
        "image_size": list(config.IMG_SIZE),
        "image_std": config.IMG_STD,
        "learning_rate": args.learning_rate,
        "model_name": "scratch_resnet18",
        "momentum": 0.9,
        "num_classes": config.NUM_CLASSES,
        "num_workers": args.num_workers,
        "optimizer": "SGD",
        "random_seed": config.RANDOM_SEED,
        "resume": args.resume,
        "start_epoch": start_epoch,
        "train_augmentation": args.train_augmentation,
        "weight_decay": 1e-4,
    }

    if args.resume:
        if not last_checkpoint_path.exists():
            raise FileNotFoundError(f"Last checkpoint not found: {last_checkpoint_path}")
        resume_state = load_checkpoint(
            last_checkpoint_path,
            model,
            optimizer,
            device,
            expected_run_config=run_config,
        )
        start_epoch = resume_state["next_epoch"]
        history = resume_state["history"]
        best_val_top1 = resume_state["best_val_top1"]
        run_config["start_epoch"] = start_epoch

    history = fit_scratch_model(
        model,
        train_loader,
        val_loader,
        optimizer,
        device,
        args.epochs,
        best_checkpoint_path=best_checkpoint_path,
        last_checkpoint_path=last_checkpoint_path,
        run_config=run_config,
        start_epoch=start_epoch,
        history=history,
        best_val_top1=best_val_top1,
    )
    completed_epoch_seconds = [
        seconds for seconds in history.get("epoch_seconds", []) if seconds is not None
    ]
    current_run_seconds = [
        seconds for seconds in history.get("epoch_seconds", [])[start_epoch:] if seconds is not None
    ]
    run_config["epochs_completed"] = len(history["train_loss"])
    run_config["training_seconds_this_run"] = sum(current_run_seconds)
    run_config["training_seconds_total"] = sum(completed_epoch_seconds)
    with (args.output_dir / "run_config.json").open("w", encoding="utf-8") as file:
        json.dump(run_config, file, indent=2)
    save_history(history, args.output_dir / "history.csv")
    figure = plot_training_curves(history)
    figure.savefig(args.output_dir / "training_curves.png", dpi=150)

    best_epoch = max(range(len(history["val_top1"])), key=history["val_top1"].__getitem__) + 1
    print(f"Best validation Top-1: {history['val_top1'][best_epoch - 1]:.4f} at epoch {best_epoch}")
    print(f"Outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
