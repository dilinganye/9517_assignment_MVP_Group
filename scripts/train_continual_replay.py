"""Train the scratch 100-class continual-learning baseline with replay."""

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from torch import optim

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.advanced.continual_learning import get_seen_task_ids
from src.advanced.continual_metrics import (
    create_accuracy_matrix,
    record_accuracy_row,
    summarize_after_task,
)
from src.advanced.continual_replay import (
    update_class_balanced_memory,
    validate_class_balanced_memory,
    validate_replay_resume_config,
)
from src.data import create_continual_dataset, create_dataloader
from src.deep_learning import create_scratch_resnet18, train_one_epoch, validate_one_epoch
from train_continual_no_replay import (
    capture_rng_state,
    create_transform,
    get_git_commit,
    restore_rng_state,
    set_seed,
    task_plan_sha256,
    write_csv,
)


def parse_args():
    """Parse the class-balanced replay experiment settings."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", type=Path, default=config.DATA_RAW_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_ROOT / "continual_100" / "replay",
    )
    parser.add_argument("--memory-per-class", type=int, required=True)
    parser.add_argument("--epochs-per-task", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--train-augmentation", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def create_run_config(args):
    """Collect settings that must match at every replay task-boundary resume."""

    return {
        "approach": "class_balanced_replay",
        "batch_size": args.batch_size,
        "classes_per_task": config.CONTINUAL_CLASSES_PER_TASK,
        "continual_num_classes": config.CONTINUAL_NUM_CLASSES,
        "epochs_per_task": args.epochs_per_task,
        "git_commit": get_git_commit(),
        "image_mean": config.IMG_MEAN,
        "image_root": str(args.image_root),
        "image_size": list(config.IMG_SIZE),
        "image_std": config.IMG_STD,
        "learning_rate": args.learning_rate,
        "memory_per_class": args.memory_per_class,
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


def create_replay_train_loader(task_id, memory_samples, image_root, transform, args):
    """Train on current-task samples plus a fixed class-balanced old-class memory."""

    dataset = create_continual_dataset(
        "train",
        task_id,
        image_root=image_root,
        transform=transform,
    )
    current_samples = list(dataset.samples)
    dataset.samples = [*current_samples, *memory_samples]
    return (
        create_dataloader(
            dataset,
            batch_size=args.batch_size,
            shuffle=True,
            num_workers=args.num_workers,
            pin_memory=True,
        ),
        current_samples,
    )


def create_validation_loader(task_id, image_root, transform, args):
    """Create deterministic validation data for exactly one continual task."""

    dataset = create_continual_dataset(
        "val",
        task_id,
        image_root=image_root,
        transform=transform,
    )
    return create_dataloader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
    )


def save_artifacts(output_dir, run_config, matrix, history_rows, summary_rows, memory_rows, memory_samples):
    """Write auditable validation and class-balanced-memory artifacts."""

    with (output_dir / "run_config.json").open("w", encoding="utf-8") as file:
        json.dump(run_config, file, indent=2)
    with (output_dir / "accuracy_matrix.json").open("w", encoding="utf-8") as file:
        json.dump({"split": "validation", "matrix": matrix}, file, indent=2)
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
    write_csv(
        output_dir / "memory_summary.csv",
        memory_rows,
        ["task_id", "memory_per_class", "memory_classes", "memory_samples"],
    )
    write_csv(
        output_dir / "memory_samples.csv",
        [
            {"file_path": relative_path, "continual_label": label}
            for relative_path, label in memory_samples
        ],
        ["file_path", "continual_label"],
    )


def save_task_checkpoint(
    path,
    completed_task_id,
    model,
    optimizer,
    run_config,
    matrix,
    history_rows,
    summary_rows,
    memory_rows,
    memory_samples,
):
    """Save model, optimizer, metrics, memory, and RNG state after one task."""

    torch.save(
        {
            "checkpoint_type": "continual_replay_task_boundary_last",
            "completed_task_id": completed_task_id,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "run_config": run_config,
            "accuracy_matrix": matrix,
            "history_rows": history_rows,
            "summary_rows": summary_rows,
            "memory_rows": memory_rows,
            "memory_samples": memory_samples,
            "rng_state": capture_rng_state(),
        },
        path,
    )


def load_task_checkpoint(path, model, optimizer, device, run_config):
    """Restore a validated class-balanced replay task-boundary checkpoint."""

    checkpoint = torch.load(path, map_location=device, weights_only=False)
    if checkpoint.get("checkpoint_type") != "continual_replay_task_boundary_last":
        raise ValueError("Checkpoint is not a continual replay task-boundary checkpoint")
    validate_replay_resume_config(checkpoint.get("run_config"), run_config)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    restore_rng_state(checkpoint["rng_state"])
    return checkpoint


def main():
    """Run sequential class-balanced replay and validation-only CL measurement."""

    args = parse_args()
    if args.memory_per_class < 1:
        raise ValueError("--memory-per-class must be at least 1")
    if args.epochs_per_task < 1:
        raise ValueError("--epochs-per-task must be at least 1")
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1")
    if args.learning_rate <= 0:
        raise ValueError("--learning-rate must be positive")
    if args.num_workers < 0:
        raise ValueError("--num-workers must be non-negative")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the continual replay entry point")

    num_tasks = config.CONTINUAL_NUM_CLASSES // config.CONTINUAL_CLASSES_PER_TASK
    device = torch.device("cuda")
    set_seed(config.RANDOM_SEED)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output_dir / "last_checkpoint.pt"
    run_config = create_run_config(args)
    run_config["resume"] = args.resume

    train_transform = create_transform(args.train_augmentation)
    eval_transform = create_transform()
    model = create_scratch_resnet18(config.CONTINUAL_NUM_CLASSES).to(device)
    optimizer = optim.SGD(
        model.parameters(),
        lr=args.learning_rate,
        momentum=run_config["momentum"],
        weight_decay=run_config["weight_decay"],
    )
    matrix = create_accuracy_matrix(num_tasks)
    history_rows = []
    summary_rows = []
    memory_rows = []
    memory_samples = []
    start_task_id = 0

    if args.resume:
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"No task-boundary checkpoint found: {checkpoint_path}")
        checkpoint = load_task_checkpoint(checkpoint_path, model, optimizer, device, run_config)
        start_task_id = checkpoint["completed_task_id"] + 1
        matrix = checkpoint["accuracy_matrix"]
        history_rows = checkpoint["history_rows"]
        summary_rows = checkpoint["summary_rows"]
        memory_rows = checkpoint["memory_rows"]
        memory_samples = checkpoint["memory_samples"]
    elif checkpoint_path.exists():
        raise FileExistsError(
            f"Checkpoint already exists: {checkpoint_path}. Use --resume or a new --output-dir."
        )

    if start_task_id >= num_tasks:
        raise ValueError("All continual tasks are already complete in this output directory")

    global_epoch = len(history_rows)
    for task_id in range(start_task_id, num_tasks):
        train_loader, current_samples = create_replay_train_loader(
            task_id,
            memory_samples,
            args.image_root,
            train_transform,
            args,
        )
        current_val_loader = create_validation_loader(
            task_id,
            args.image_root,
            eval_transform,
            args,
        )
        for epoch_in_task in range(1, args.epochs_per_task + 1):
            epoch_start = time.perf_counter()
            train_metrics = train_one_epoch(model, train_loader, optimizer, device)
            current_val_metrics = validate_one_epoch(model, current_val_loader, device)
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
            validation_loader = create_validation_loader(
                evaluated_task_id,
                args.image_root,
                eval_transform,
                args,
            )
            task_accuracies[evaluated_task_id] = validate_one_epoch(
                model,
                validation_loader,
                device,
            )["top1"]
        record_accuracy_row(matrix, task_id, task_accuracies)
        summary_rows.append(summarize_after_task(matrix, task_id))

        memory_samples = update_class_balanced_memory(
            memory_samples,
            current_samples,
            args.memory_per_class,
            config.RANDOM_SEED,
        )
        seen_labels = range((task_id + 1) * config.CONTINUAL_CLASSES_PER_TASK)
        validate_class_balanced_memory(memory_samples, args.memory_per_class, seen_labels)
        memory_rows.append(
            {
                "task_id": task_id,
                "memory_per_class": args.memory_per_class,
                "memory_classes": len(seen_labels),
                "memory_samples": len(memory_samples),
            }
        )
        run_config["completed_task_id"] = task_id
        run_config["epochs_completed"] = global_epoch
        save_artifacts(
            args.output_dir,
            run_config,
            matrix,
            history_rows,
            summary_rows,
            memory_rows,
            memory_samples,
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
            memory_rows,
            memory_samples,
        )
        print(json.dumps({**summary_rows[-1], **memory_rows[-1]}, sort_keys=True))

    print(f"Validation-only replay outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
