"""Train the scratch 100-class continual-learning baseline without replay."""

import argparse
import csv
import hashlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import optim
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.advanced.continual_learning import get_seen_task_ids
from src.advanced.continual_metrics import (
    create_accuracy_matrix,
    record_accuracy_row,
    summarize_after_task,
)
from src.advanced.continual_no_replay import validate_no_replay_resume_config
from src.data import create_continual_dataset, create_dataloader
from src.deep_learning import create_scratch_resnet18, train_one_epoch, validate_one_epoch


def parse_args():
    """Parse the fixed sequential no-replay experiment settings."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", type=Path, default=config.DATA_RAW_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_ROOT / "continual_100" / "no_replay",
    )
    parser.add_argument("--epochs-per-task", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--train-augmentation", action="store_true")
    parser.add_argument(
        "--evaluation-split",
        choices=("val", "test"),
        default="val",
        help="evaluate seen tasks at each task boundary on this held-out split",
    )
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def set_seed(seed: int):
    """Seed the CUDA run as consistently as practical."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def create_transform(train_augmentation: bool = False):
    """Create the train or deterministic validation transform."""

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


def get_git_commit():
    """Return the current commit when running from a Git checkout."""

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=config.PROJECT_ROOT,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def task_plan_sha256():
    """Fingerprint the committed mapping used to define the task sequence."""

    return hashlib.sha256(config.CONTINUAL_CLASS_TASKS_CSV.read_bytes()).hexdigest()


def create_run_config(args):
    """Collect the settings that must match when resuming at a task boundary."""

    return {
        "approach": "sequential_no_replay",
        "batch_size": args.batch_size,
        "classes_per_task": config.CONTINUAL_CLASSES_PER_TASK,
        "continual_num_classes": config.CONTINUAL_NUM_CLASSES,
        "evaluation_split": args.evaluation_split,
        "epochs_per_task": args.epochs_per_task,
        "git_commit": get_git_commit(),
        "image_mean": config.IMG_MEAN,
        "image_root": str(args.image_root),
        "image_size": list(config.IMG_SIZE),
        "image_std": config.IMG_STD,
        "learning_rate": args.learning_rate,
        "model_name": "scratch_resnet18",
        "momentum": 0.9,
        "num_workers": args.num_workers,
        "optimizer": "SGD",
        "random_seed": config.RANDOM_SEED,
        "task_plan": str(config.CONTINUAL_CLASS_TASKS_CSV),
        "task_plan_sha256": task_plan_sha256(),
        "train_augmentation": args.train_augmentation,
        "weight_decay": 1e-4,
    }


def capture_rng_state():
    """Capture RNG state so a task-boundary resume keeps the task sequence stable."""

    return {
        "numpy": np.random.get_state(),
        "python": random.getstate(),
        "torch": torch.get_rng_state(),
        "torch_cuda": torch.cuda.get_rng_state_all(),
    }


def restore_rng_state(state):
    """Restore the RNG state saved after the preceding completed task."""

    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    torch.cuda.set_rng_state_all(state["torch_cuda"])


def write_csv(path: Path, rows, fieldnames):
    """Write a stable CSV, including an empty header-only table when needed."""

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_artifacts(output_dir: Path, run_config, evaluation_split, matrix, history_rows, summary_rows):
    """Write local task-boundary artifacts after a completed task."""

    with (output_dir / "run_config.json").open("w", encoding="utf-8") as file:
        json.dump(run_config, file, indent=2)
    with (output_dir / "accuracy_matrix.json").open("w", encoding="utf-8") as file:
        json.dump({"split": evaluation_split, "matrix": matrix}, file, indent=2)
    write_csv(
        output_dir / "training_history.csv",
        history_rows,
        [
            "task_id",
            "epoch_in_task",
            "global_epoch",
            "train_loss",
            "train_top1",
            "current_val_loss",
            "current_val_top1",
            "epoch_seconds",
        ],
    )
    write_csv(
        output_dir / "task_metrics.csv",
        summary_rows,
        [
            "task_id",
            "current_task_accuracy",
            "old_task_accuracy",
            "seen_task_accuracy",
            "average_forgetting",
        ],
    )


def save_task_checkpoint(
    path: Path,
    completed_task_id: int,
    model,
    optimizer,
    run_config,
    matrix,
    history_rows,
    summary_rows,
):
    """Save enough state to resume from the next task, never mid-task."""

    torch.save(
        {
            "checkpoint_type": "continual_task_boundary_last",
            "completed_task_id": completed_task_id,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "run_config": run_config,
            "accuracy_matrix": matrix,
            "history_rows": history_rows,
            "summary_rows": summary_rows,
            "rng_state": capture_rng_state(),
        },
        path,
    )


def load_task_checkpoint(path: Path, model, optimizer, device, run_config):
    """Restore a validated no-replay task-boundary checkpoint."""

    checkpoint = torch.load(path, map_location=device, weights_only=False)
    if checkpoint.get("checkpoint_type") != "continual_task_boundary_last":
        raise ValueError("Checkpoint is not a continual no-replay task-boundary checkpoint")
    validate_no_replay_resume_config(checkpoint.get("run_config"), run_config)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    restore_rng_state(checkpoint["rng_state"])
    return checkpoint


def create_loader(split, task_ids, image_root, transform, args, shuffle=False):
    """Create a loader for one current task or a seen-task validation slice."""

    dataset = create_continual_dataset(
        split,
        task_ids,
        image_root=image_root,
        transform=transform,
    )
    return create_dataloader(
        dataset,
        batch_size=args.batch_size,
        shuffle=shuffle,
        num_workers=args.num_workers,
        pin_memory=True,
    )


def main():
    """Run sequential task training with fixed task-boundary CL measurement."""

    args = parse_args()
    if args.epochs_per_task < 1:
        raise ValueError("--epochs-per-task must be at least 1")
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1")
    if args.learning_rate <= 0:
        raise ValueError("--learning-rate must be positive")
    if args.num_workers < 0:
        raise ValueError("--num-workers must be non-negative")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the continual no-replay entry point")

    num_tasks = config.CONTINUAL_NUM_CLASSES // config.CONTINUAL_CLASSES_PER_TASK
    device = torch.device("cuda")
    set_seed(config.RANDOM_SEED)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output_dir / "last_checkpoint.pt"
    run_config = create_run_config(args)
    run_config["resume"] = args.resume

    train_transform = create_transform(args.train_augmentation)
    eval_transform = create_transform()
    model = create_scratch_resnet18(config.CONTINUAL_NUM_CLASSES)
    optimizer = optim.SGD(
        model.parameters(),
        lr=args.learning_rate,
        momentum=run_config["momentum"],
        weight_decay=run_config["weight_decay"],
    )
    model.to(device)
    matrix = create_accuracy_matrix(num_tasks)
    history_rows = []
    summary_rows = []
    start_task_id = 0

    if args.resume:
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"No task-boundary checkpoint found: {checkpoint_path}")
        checkpoint = load_task_checkpoint(checkpoint_path, model, optimizer, device, run_config)
        start_task_id = checkpoint["completed_task_id"] + 1
        matrix = checkpoint["accuracy_matrix"]
        history_rows = checkpoint["history_rows"]
        summary_rows = checkpoint["summary_rows"]
    elif checkpoint_path.exists():
        raise FileExistsError(
            f"Checkpoint already exists: {checkpoint_path}. Use --resume or a new --output-dir."
        )

    if start_task_id >= num_tasks:
        raise ValueError("All continual tasks are already complete in this output directory")

    global_epoch = len(history_rows)
    for task_id in range(start_task_id, num_tasks):
        seen_class_count = (task_id + 1) * config.CONTINUAL_CLASSES_PER_TASK
        train_loader = create_loader(
            "train",
            task_id,
            args.image_root,
            train_transform,
            args,
            shuffle=True,
        )
        current_val_loader = create_loader(
            "val",
            task_id,
            args.image_root,
            eval_transform,
            args,
        )
        for epoch_in_task in range(1, args.epochs_per_task + 1):
            epoch_start = time.perf_counter()
            train_metrics = train_one_epoch(model, train_loader, optimizer, device)
            current_val_metrics = validate_one_epoch(
                model,
                current_val_loader,
                device,
                seen_class_count=seen_class_count,
            )
            global_epoch += 1
            history_rows.append(
                {
                    "task_id": task_id,
                    "epoch_in_task": epoch_in_task,
                    "global_epoch": global_epoch,
                    "train_loss": train_metrics["loss"],
                    "train_top1": train_metrics["top1"],
                    "current_val_loss": current_val_metrics["loss"],
                    "current_val_top1": current_val_metrics["top1"],
                    "epoch_seconds": time.perf_counter() - epoch_start,
                }
            )

        task_accuracies = {}
        for evaluated_task_id in get_seen_task_ids(task_id, num_tasks):
            evaluation_loader = create_loader(
                args.evaluation_split,
                evaluated_task_id,
                args.image_root,
                eval_transform,
                args,
            )
            task_accuracies[evaluated_task_id] = validate_one_epoch(
                model,
                evaluation_loader,
                device,
                seen_class_count=seen_class_count,
            )["top1"]
        record_accuracy_row(matrix, task_id, task_accuracies)
        summary_rows.append(summarize_after_task(matrix, task_id))
        run_config["completed_task_id"] = task_id
        run_config["epochs_completed"] = global_epoch
        save_artifacts(
            args.output_dir,
            run_config,
            args.evaluation_split,
            matrix,
            history_rows,
            summary_rows,
        )
        save_task_checkpoint(
            checkpoint_path,
            task_id,
            model,
            optimizer,
            run_config,
            matrix,
            history_rows,
            summary_rows,
        )
        print(json.dumps(summary_rows[-1], sort_keys=True))

    print(f"Task-boundary {args.evaluation_split} no-replay outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
