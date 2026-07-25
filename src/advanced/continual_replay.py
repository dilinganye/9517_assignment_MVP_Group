"""Class-balanced replay memory and resume guards for continual learning."""

import random

from src.advanced.continual_no_replay import NO_REPLAY_RESUME_FIELDS


REPLAY_RESUME_FIELDS = (
    *NO_REPLAY_RESUME_FIELDS,
    "memory_per_class",
    "class_balanced_sampling",
)


def inverse_frequency_sample_weights(samples):
    """Return per-sample weights that give every observed class equal mass."""

    if not samples:
        raise ValueError("samples must not be empty")

    counts = {}
    for _, label in samples:
        label = int(label)
        counts[label] = counts.get(label, 0) + 1

    return [1.0 / counts[int(label)] for _, label in samples]


def update_class_balanced_memory(memory_samples, current_samples, memory_per_class: int, seed: int):
    """Keep at most a deterministic number of samples for every seen class."""

    if memory_per_class < 1:
        raise ValueError("memory_per_class must be positive")

    samples_by_label = {}
    for relative_path, label in [*memory_samples, *current_samples]:
        samples_by_label.setdefault(int(label), set()).add(str(relative_path))

    selected = []
    for label, paths in sorted(samples_by_label.items()):
        candidates = sorted(paths)
        selected_paths = random.Random(f"{seed}:{label}").sample(
            candidates,
            min(memory_per_class, len(candidates)),
        )
        selected.extend((relative_path, label) for relative_path in sorted(selected_paths))
    return selected


def validate_class_balanced_memory(memory_samples, memory_per_class: int, expected_labels):
    """Verify that every expected class has the requested memory capacity."""

    expected_labels = {int(label) for label in expected_labels}
    paths_by_label = {}
    for relative_path, label in memory_samples:
        label = int(label)
        paths_by_label.setdefault(label, set()).add(str(relative_path))

    if set(paths_by_label) != expected_labels:
        raise ValueError("Replay memory labels do not match the seen continual labels")
    if any(len(paths) != memory_per_class for paths in paths_by_label.values()):
        raise ValueError("Replay memory is not class-balanced at the configured capacity")


def validate_replay_resume_config(saved_config, current_config):
    """Reject replay resumes with incompatible task or memory settings."""

    if not isinstance(saved_config, dict):
        raise ValueError("Checkpoint has no continual-learning run configuration")

    saved_config = dict(saved_config)
    saved_config.setdefault("class_balanced_sampling", False)

    missing = [field for field in REPLAY_RESUME_FIELDS if field not in saved_config]
    mismatches = {
        field: {"saved": saved_config[field], "current": current_config.get(field)}
        for field in REPLAY_RESUME_FIELDS
        if field not in missing and saved_config[field] != current_config.get(field)
    }
    if missing or mismatches:
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if mismatches:
            details.append(f"mismatched fields: {', '.join(sorted(mismatches))}")
        raise ValueError(f"Continual replay resume configuration mismatch ({'; '.join(details)})")
