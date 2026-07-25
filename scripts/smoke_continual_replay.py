"""Check deterministic class-balanced replay memory without torch or images."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.advanced.continual_replay import (
    REPLAY_RESUME_FIELDS,
    inverse_frequency_sample_weights,
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

    imbalanced_samples = [(f"old/{index}.jpg", 0) for index in range(2)]
    imbalanced_samples.extend((f"new/{index}.jpg", 1) for index in range(40))
    weights = inverse_frequency_sample_weights(imbalanced_samples)
    class_weight_mass = {}
    for (_, label), weight in zip(imbalanced_samples, weights):
        class_weight_mass[label] = class_weight_mass.get(label, 0.0) + weight
    if any(abs(mass - 1.0) > 1e-12 for mass in class_weight_mass.values()):
        fail("inverse-frequency sampling does not balance class probability")

    config = {
        field: False
        if field == "class_balanced_sampling"
        else "val"
        if field == "evaluation_split"
        else f"value-{field}"
        for field in REPLAY_RESUME_FIELDS
    }
    validate_replay_resume_config(config, config)
    legacy_config = dict(config)
    legacy_config.pop("class_balanced_sampling")
    legacy_config.pop("evaluation_split")
    validate_replay_resume_config(legacy_config, config)
    changed_config = dict(config)
    changed_config["memory_per_class"] = "changed"
    try:
        validate_replay_resume_config(config, changed_config)
    except ValueError as error:
        if "memory_per_class" not in str(error):
            fail("mismatch error does not identify the replay memory setting")
    else:
        fail("mismatched replay memory setting was accepted")

    changed_split = dict(config)
    changed_split["evaluation_split"] = "test"
    try:
        validate_replay_resume_config(config, changed_split)
    except ValueError as error:
        if "evaluation_split" not in str(error):
            fail("mismatch error does not identify the evaluation split")
    else:
        fail("mismatched evaluation split was accepted")

    print("[continual-replay] PASS: memory, sampling weights, and resume guard are consistent")


if __name__ == "__main__":
    main()
