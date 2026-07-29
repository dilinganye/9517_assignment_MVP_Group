"""Plot continual-learning loss and Top-1 trajectories from saved histories."""

import argparse
import csv
from pathlib import Path


REQUIRED_HISTORY_COLUMNS = (
    "task_id",
    "epoch_in_task",
    "global_epoch",
    "train_loss",
    "train_top1",
    "current_val_loss",
    "current_val_top1",
)


def parse_args():
    """Parse two saved validation-run directories and one local figure directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-replay-dir", type=Path, required=True)
    parser.add_argument("--replay-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def read_training_history(path: Path):
    """Read a complete continual training-history CSV without model access."""

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = set(REQUIRED_HISTORY_COLUMNS).difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
        rows = [
            {
                "task_id": int(row["task_id"]),
                "epoch_in_task": int(row["epoch_in_task"]),
                "global_epoch": int(row["global_epoch"]),
                "train_loss": float(row["train_loss"]),
                "train_top1": float(row["train_top1"]),
                "current_val_loss": float(row["current_val_loss"]),
                "current_val_top1": float(row["current_val_top1"]),
            }
            for row in reader
        ]

    if not rows:
        raise ValueError(f"{path} has no training-history rows")
    if [row["global_epoch"] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(f"{path} global_epoch values must start at 1 and be contiguous")
    if any(row["task_id"] < 0 or row["epoch_in_task"] < 1 for row in rows):
        raise ValueError(f"{path} task and epoch values must be non-negative")
    if any(not 0.0 <= row[field] <= 1.0 for row in rows for field in ("train_top1", "current_val_top1")):
        raise ValueError(f"{path} Top-1 values must be between 0 and 1")
    return rows


def task_boundary_epochs(history):
    """Return the final global epoch before each transition to a new task."""

    return [
        row["global_epoch"]
        for row, next_row in zip(history, history[1:])
        if row["task_id"] != next_row["task_id"]
    ]


def read_run(name: str, run_dir: Path):
    """Load one named run from its saved training history."""

    return {"name": name, "history": read_training_history(run_dir / "training_history.csv")}


def add_task_boundaries(axis, history):
    """Draw the completed-task boundaries without assuming a fixed epoch budget."""

    for epoch in task_boundary_epochs(history):
        axis.axvline(epoch + 0.5, color="0.45", linestyle="--", linewidth=0.8, alpha=0.7)


def plot_trajectories(runs, path: Path):
    """Write a four-panel loss and Top-1 figure for the supplied saved runs."""

    import matplotlib.pyplot as plt

    metrics = (
        ("train_loss", "Training loss", "Loss"),
        ("current_val_loss", "Current-task validation loss", "Loss"),
        ("train_top1", "Training Top-1", "Top-1 accuracy"),
        ("current_val_top1", "Current-task validation Top-1", "Top-1 accuracy"),
    )
    figure, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    for axis, (field, title, ylabel) in zip(axes.flat, metrics):
        for run in runs:
            history = run["history"]
            axis.plot(
                [row["global_epoch"] for row in history],
                [row[field] for row in history],
                linewidth=1.8,
                label=run["name"],
            )
        add_task_boundaries(axis, runs[0]["history"])
        axis.set(title=title, ylabel=ylabel)
        axis.grid(axis="y", alpha=0.25)
    for axis in axes[1]:
        axis.set_xlabel("Global epoch")
    axes[1, 0].set_ylim(-0.02, 1.02)
    axes[1, 1].set_ylim(-0.02, 1.02)
    axes[0, 0].legend()
    figure.suptitle("Continual-learning training trajectories (dashed lines: task boundaries)")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main():
    """Create a no-GPU trajectory figure from two existing validation runs."""

    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs = [
        read_run("no replay", args.no_replay_dir),
        read_run("M=5 replay", args.replay_dir),
    ]
    output_path = args.output_dir / "continual_training_trajectories.png"
    plot_trajectories(runs, output_path)
    print(f"Continual-learning trajectories saved to: {output_path}")


if __name__ == "__main__":
    main()
