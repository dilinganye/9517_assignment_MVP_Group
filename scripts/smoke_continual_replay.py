"""Check deterministic class-balanced replay memory without torch or images."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.advanced.continual_replay import (
    REPLAY_RESUME_FIELDS,
    update_class_balanced_memory,
    validate_class_balanced_memory,
    validate_replay_resume_config,
)


def fail(message):
    raise SystemExit(f"[continual-replay] FAIL: {message}")


def main():
    """Verify stable memory selection, class balance, and resume protection."""

    task_zero = [(f"task0/class{label}/{index}.jpg", label) for label in range(2) for index in range(4)]
    task_one = [(f"task1/class{label}/{index}.jpg", label) for label in range(2, 4) for index in range(4)]
    first_memory = update_class_balanced_memory([], task_zero, memory_per_class=2, seed=56)
    second_memory = update_class_balanced_memory(first_memory, task_one, memory_per_class=2, seed=56)

    if first_memory != update_class_balanced_memory([], task_zero, memory_per_class=2, seed=56):
        fail("memory selection is not deterministic")
    validate_class_balanced_memory(first_memory, 2, expected_labels=range(2))
    validate_class_balanced_memory(second_memory, 2, expected_labels=range(4))

    config = {field: f"value-{field}" for field in REPLAY_RESUME_FIELDS}
    validate_replay_resume_config(config, config)
    changed_config = dict(config)
    changed_config["memory_per_class"] = "changed"
    try:
        validate_replay_resume_config(config, changed_config)
    except ValueError as error:
        if "memory_per_class" not in str(error):
            fail("mismatch error does not identify the replay memory setting")
    else:
        fail("mismatched replay memory setting was accepted")

    print("[continual-replay] PASS: memory and resume guard are consistent")


if __name__ == "__main__":
    main()
