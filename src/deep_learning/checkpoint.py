"""Checkpoint helpers for resuming scratch-CNN training."""

from pathlib import Path

import torch
from torch.optim import Optimizer


RESUME_CRITICAL_FIELDS = (
    "model_name",
    "random_seed",
    "num_classes",
    "image_size",
    "image_mean",
    "image_std",
    "learning_rate",
    "batch_size",
    "optimizer",
    "momentum",
    "weight_decay",
    "train_augmentation",
)


def save_checkpoint(
    path,
    epoch: int,
    model,
    optimizer: Optimizer,
    history,
    best_val_top1,
    run_config=None,
    checkpoint_type: str = "best",
):
    """Save the completed epoch and state required for a reproducible resume."""

    if checkpoint_type not in {"best", "last"}:
        raise ValueError("checkpoint_type must be 'best' or 'last'")

    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "history": history,
            "best_val_top1": best_val_top1,
            "run_config": run_config,
            "checkpoint_type": checkpoint_type,
        },
        checkpoint_path,
    )


def validate_resume_config(saved_config, current_config):
    """Reject a resume when training-defining settings no longer match."""

    if not isinstance(saved_config, dict):
        raise ValueError(
            "Checkpoint has no run configuration and cannot be safely resumed. "
            "Start a new run instead."
        )

    missing = [key for key in RESUME_CRITICAL_FIELDS if key not in saved_config]
    mismatches = {
        key: {"saved": saved_config[key], "current": current_config.get(key)}
        for key in RESUME_CRITICAL_FIELDS
        if key not in missing and saved_config[key] != current_config.get(key)
    }
    if missing or mismatches:
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if mismatches:
            details.append(f"mismatched fields: {', '.join(sorted(mismatches))}")
        raise ValueError(f"Resume configuration mismatch ({'; '.join(details)})")


def load_model_weights(path, model, device, expected_run_config=None, checkpoint_type=None):
    """Load model weights from a checkpoint for inference or resumed training."""

    checkpoint = torch.load(path, map_location=torch.device(device))
    if checkpoint_type and checkpoint.get("checkpoint_type") != checkpoint_type:
        raise ValueError(
            f"Expected a {checkpoint_type} checkpoint, found "
            f"{checkpoint.get('checkpoint_type', 'an untyped checkpoint')}"
        )
    if expected_run_config is not None:
        validate_resume_config(checkpoint.get("run_config"), expected_run_config)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    return checkpoint


def load_checkpoint(path, model, optimizer: Optimizer, device, expected_run_config=None):
    """Restore a checkpoint and return the state needed to resume training."""

    checkpoint = load_model_weights(
        path,
        model,
        device,
        expected_run_config=expected_run_config,
        checkpoint_type="last" if expected_run_config is not None else None,
    )
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return {
        "next_epoch": checkpoint["epoch"] + 1,
        "history": checkpoint["history"],
        "best_val_top1": checkpoint["best_val_top1"],
    }
