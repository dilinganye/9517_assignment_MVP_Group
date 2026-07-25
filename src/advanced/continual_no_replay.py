"""Run-configuration guards for sequential no-replay training."""


NO_REPLAY_RESUME_FIELDS = (
    "approach",
    "batch_size",
    "classes_per_task",
    "continual_num_classes",
    "evaluation_split",
    "epochs_per_task",
    "image_mean",
    "image_size",
    "image_std",
    "learning_rate",
    "model_name",
    "momentum",
    "optimizer",
    "random_seed",
    "task_plan_sha256",
    "train_augmentation",
    "weight_decay",
)


def validate_no_replay_resume_config(saved_config, current_config):
    """Reject task-boundary resumes whose training-defining settings differ."""

    if not isinstance(saved_config, dict):
        raise ValueError("Checkpoint has no continual-learning run configuration")

    saved_config = dict(saved_config)
    saved_config.setdefault("evaluation_split", "val")

    missing = [field for field in NO_REPLAY_RESUME_FIELDS if field not in saved_config]
    mismatches = {
        field: {"saved": saved_config[field], "current": current_config.get(field)}
        for field in NO_REPLAY_RESUME_FIELDS
        if field not in missing and saved_config[field] != current_config.get(field)
    }
    if missing or mismatches:
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if mismatches:
            details.append(f"mismatched fields: {', '.join(sorted(mismatches))}")
        raise ValueError(f"Continual resume configuration mismatch ({'; '.join(details)})")
