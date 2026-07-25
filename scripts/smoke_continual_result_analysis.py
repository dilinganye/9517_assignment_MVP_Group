"""Verify continual-result artifact validation without images, torch, or matplotlib."""

import csv
import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.summarize_continual_results import read_run, write_final_metrics


def fail(message):
    raise SystemExit(f"[continual-result-analysis] FAIL: {message}")


def write_run(output_dir: Path, values):
    """Write one small valid test artifact set for the dependency-light smoke test."""

    output_dir.mkdir()
    with (output_dir / "task_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["task_id", "current_task_accuracy", "old_task_accuracy", "seen_task_accuracy", "average_forgetting"])
        writer.writeheader()
        writer.writerows(values)
    matrix = [[float(values[0]["seen_task_accuracy"]), None], [float(values[1]["old_task_accuracy"]), float(values[1]["current_task_accuracy"])]]
    (output_dir / "accuracy_matrix.json").write_text(json.dumps({"split": "test", "matrix": matrix}), encoding="utf-8")


def main():
    """Verify validated inputs produce a stable compact final-results table."""

    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        no_replay_values = [
            {"task_id": 0, "current_task_accuracy": 0.5, "old_task_accuracy": "", "seen_task_accuracy": 0.5, "average_forgetting": ""},
            {"task_id": 1, "current_task_accuracy": 0.2, "old_task_accuracy": 0.0, "seen_task_accuracy": 0.1, "average_forgetting": 0.5},
        ]
        replay_values = [
            {"task_id": 0, "current_task_accuracy": 0.5, "old_task_accuracy": "", "seen_task_accuracy": 0.5, "average_forgetting": ""},
            {"task_id": 1, "current_task_accuracy": 0.3, "old_task_accuracy": 0.1, "seen_task_accuracy": 0.2, "average_forgetting": 0.4},
        ]
        write_run(root / "no_replay", no_replay_values)
        write_run(root / "replay", replay_values)
        runs = [read_run("no_replay", root / "no_replay"), read_run("replay", root / "replay")]
        final_metrics_path = root / "final_metrics.csv"
        write_final_metrics(final_metrics_path, runs)
        with final_metrics_path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        if len(rows) != 2 or rows[1]["old_task_accuracy"] != "0.1":
            fail("final metrics table does not contain the validated final rows")

    print("[continual-result-analysis] PASS: held-out artifacts and final table are consistent")


if __name__ == "__main__":
    main()
