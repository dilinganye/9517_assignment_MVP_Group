"""Summarize fixed held-out continual-learning artifacts without rerunning models."""

import argparse
import csv
import json
from pathlib import Path


REQUIRED_METRIC_COLUMNS = (
    "task_id",
    "current_task_accuracy",
    "old_task_accuracy",
    "seen_task_accuracy",
    "average_forgetting",
)


def parse_args():
    """Parse two fixed test runs and one local report-artifact directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-replay-dir", type=Path, required=True)
    parser.add_argument("--replay-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def read_run(name: str, output_dir: Path):
    """Read and validate one task-boundary test artifact set."""

    metrics = read_task_metrics(output_dir / "task_metrics.csv")
    matrix = read_accuracy_matrix(output_dir / "accuracy_matrix.json", len(metrics))
    return {"name": name, "metrics": metrics, "matrix": matrix}


def read_task_metrics(path: Path):
    """Read a complete, ordered continual-learning task-metrics CSV."""

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = set(REQUIRED_METRIC_COLUMNS).difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")

        rows = []
        for row in reader:
            rows.append(
                {
                    "task_id": int(row["task_id"]),
                    "current_task_accuracy": float(row["current_task_accuracy"]),
                    "old_task_accuracy": optional_float(row["old_task_accuracy"]),
                    "seen_task_accuracy": float(row["seen_task_accuracy"]),
                    "average_forgetting": optional_float(row["average_forgetting"]),
                }
            )

    if not rows:
        raise ValueError(f"{path} has no task metrics")
    if [row["task_id"] for row in rows] != list(range(len(rows))):
        raise ValueError(f"{path} task_id values must be contiguous from 0")
    for row in rows:
        for field in ("current_task_accuracy", "seen_task_accuracy"):
            validate_accuracy(row[field], f"{path} {field}")
        for field in ("old_task_accuracy", "average_forgetting"):
            if row[field] is not None:
                validate_accuracy(row[field], f"{path} {field}")
    if rows[0]["old_task_accuracy"] is not None or rows[0]["average_forgetting"] is not None:
        raise ValueError(f"{path} first task must leave old-task metrics empty")
    if any(row["old_task_accuracy"] is None or row["average_forgetting"] is None for row in rows[1:]):
        raise ValueError(f"{path} later tasks must include old-task metrics")
    return rows


def optional_float(value):
    """Convert CSV values while preserving the undefined first-task fields."""

    return None if value in (None, "") else float(value)


def validate_accuracy(value, description: str):
    """Require a finite accuracy-like value in the unit interval."""

    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{description} must be between 0 and 1")


def read_accuracy_matrix(path: Path, num_tasks: int):
    """Read a lower-triangular held-out task accuracy matrix."""

    with path.open(encoding="utf-8") as file:
        artifact = json.load(file)
    if artifact.get("split") != "test":
        raise ValueError(f"{path} must identify the held-out test split")

    matrix = artifact.get("matrix")
    if not isinstance(matrix, list) or len(matrix) != num_tasks:
        raise ValueError(f"{path} matrix does not match the task-metrics length")
    for task_id, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != num_tasks:
            raise ValueError(f"{path} matrix must be square")
        for evaluated_task_id, value in enumerate(row):
            if evaluated_task_id <= task_id:
                if value is None:
                    raise ValueError(f"{path} is missing a seen-task accuracy")
                validate_accuracy(float(value), f"{path} matrix value")
            elif value is not None:
                raise ValueError(f"{path} contains an evaluation before a task was learned")
    return matrix


def write_final_metrics(path: Path, runs):
    """Write one compact report table from the final task of each run."""

    fieldnames = (
        "experiment",
        "evaluation_split",
        "current_task_accuracy",
        "old_task_accuracy",
        "seen_task_accuracy",
        "average_forgetting",
    )
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            final_row = run["metrics"][-1]
            writer.writerow(
                {
                    "experiment": run["name"],
                    "evaluation_split": "test",
                    **{field: final_row[field] for field in fieldnames[2:]},
                }
            )


def save_metric_curves(runs, path: Path):
    """Plot old, seen, and forgetting trajectories for two fixed test runs."""

    import matplotlib.pyplot as plt

    fields = (
        ("old_task_accuracy", "Old-task accuracy"),
        ("seen_task_accuracy", "Seen-task accuracy"),
        ("average_forgetting", "Average forgetting"),
    )
    figure, axes = plt.subplots(1, len(fields), figsize=(15, 4), sharex=True)
    for axis, (field, title) in zip(axes, fields):
        for run in runs:
            task_ids = [row["task_id"] for row in run["metrics"]]
            values = [row[field] for row in run["metrics"]]
            axis.plot(task_ids, values, marker="o", linewidth=2, label=run["name"])
        axis.set(title=title, xlabel="Task boundary", ylim=(-0.02, 1.02))
        axis.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Accuracy")
    axes[-1].set_ylabel("Forgetting")
    axes[0].legend()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def save_accuracy_matrix(run, path: Path):
    """Plot one held-out task-by-task accuracy matrix."""

    import matplotlib.pyplot as plt
    import numpy as np

    matrix = np.asarray(
        [[float("nan") if value is None else float(value) for value in row] for row in run["matrix"]],
        dtype=float,
    )
    figure, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(np.ma.masked_invalid(matrix), vmin=0.0, vmax=1.0, cmap="Blues")
    task_ids = range(len(matrix))
    axis.set(
        title=f"Held-out task accuracy matrix: {run['name']}",
        xlabel="Evaluated task",
        ylabel="After learning task",
        xticks=task_ids,
        yticks=task_ids,
    )
    for row_index, column_index in zip(*np.where(~np.isnan(matrix))):
        axis.text(column_index, row_index, f"{matrix[row_index, column_index]:.2f}", ha="center", va="center", fontsize=7)
    figure.colorbar(image, ax=axis, label="Top-1 accuracy", fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main():
    """Create local report tables and figures from two frozen CL test runs."""

    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs = [
        read_run("no_replay", args.no_replay_dir),
        read_run("replay_m5_inverse_frequency", args.replay_dir),
    ]
    write_final_metrics(args.output_dir / "final_metrics.csv", runs)
    save_metric_curves(runs, args.output_dir / "metric_curves.png")
    for run in runs:
        save_accuracy_matrix(run, args.output_dir / f"{run['name']}_accuracy_matrix.png")
    print(f"Continual-learning report artifacts saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
