"""Verify continual-trajectory history parsing without GPU or plotting."""

import csv
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.plot_continual_trajectories import read_training_history, task_boundary_epochs


def fail(message):
    raise SystemExit(f"[continual-trajectory] FAIL: {message}")


def main():
    """Check contiguous history parsing and task-boundary detection."""

    rows = [
        {"task_id": 0, "epoch_in_task": 1, "global_epoch": 1, "train_loss": 2.0, "train_top1": 0.2, "current_val_loss": 2.1, "current_val_top1": 0.1},
        {"task_id": 0, "epoch_in_task": 2, "global_epoch": 2, "train_loss": 1.8, "train_top1": 0.3, "current_val_loss": 2.0, "current_val_top1": 0.2},
        {"task_id": 1, "epoch_in_task": 1, "global_epoch": 3, "train_loss": 1.7, "train_top1": 0.4, "current_val_loss": 1.9, "current_val_top1": 0.25},
    ]
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "training_history.csv"
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        history = read_training_history(path)

    if task_boundary_epochs(history) != [2]:
        fail("task boundary detection did not identify the first completed task")
    if history[-1]["current_val_top1"] != 0.25:
        fail("history parsing changed the recorded validation accuracy")
    print("[continual-trajectory] PASS: training histories and task boundaries are consistent")


if __name__ == "__main__":
    main()
