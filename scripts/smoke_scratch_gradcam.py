"""Verify deterministic scratch Grad-CAM sample selection without model dependencies."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.gradcam_selection import select_samples


def fail(message):
    raise SystemExit(f"[scratch-gradcam] FAIL: {message}")


def main():
    """Check correct, incorrect, and confused-pair selection remains auditable."""

    rows = [
        {"file_path": "a.jpg", "true_label": 0, "true_name": "a", "predicted_label": 0, "predicted_name": "a", "correct": 1},
        {"file_path": "b.jpg", "true_label": 1, "true_name": "b", "predicted_label": 2, "predicted_name": "c", "correct": 0},
        {"file_path": "c.jpg", "true_label": 1, "true_name": "b", "predicted_label": 2, "predicted_name": "c", "correct": 0},
        {"file_path": "d.jpg", "true_label": 2, "true_name": "c", "predicted_label": 1, "predicted_name": "b", "correct": 0},
    ]
    selected = select_samples(
        rows,
        confused_pairs=[(1, 2, 2), (2, 1, 1)],
        correct_count=1,
        incorrect_count=1,
        pair_count=2,
        examples_per_pair=1,
    )
    by_path = {row["file_path"]: row for row in selected}
    if set(by_path) != {"a.jpg", "b.jpg", "d.jpg"}:
        fail("selection did not retain the expected compact example set")
    if "incorrect_example" not in by_path["b.jpg"]["selection_reasons"]:
        fail("overlapping selections did not preserve the initial reason")
    if "confused_pair_1" not in by_path["b.jpg"]["selection_reasons"]:
        fail("confused-pair provenance was not retained")
    print("[scratch-gradcam] PASS: compact Grad-CAM selection is deterministic")


if __name__ == "__main__":
    main()
