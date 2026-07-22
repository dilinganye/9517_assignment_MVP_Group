"""Checkpoint helpers for resuming scratch-CNN training."""

from pathlib import Path

import torch
from torch.optim import Optimizer


def save_checkpoint(path, epoch: int, model, optimizer: Optimizer, history, best_val_top1):
    """Save the completed epoch, model, optimizer, history, and best Top-1."""

    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "history": history,
            "best_val_top1": best_val_top1,
        },
        checkpoint_path,
    )


def load_model_weights(path, model, device):
    """Load model weights from a checkpoint for inference or resumed training."""

    checkpoint = torch.load(path, map_location=torch.device(device))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    return checkpoint


def load_checkpoint(path, model, optimizer: Optimizer, device):
    """Restore a checkpoint and return the state needed to resume training."""

    checkpoint = load_model_weights(path, model, device)
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return {
        "next_epoch": checkpoint["epoch"] + 1,
        "history": checkpoint["history"],
        "best_val_top1": checkpoint["best_val_top1"],
    }
