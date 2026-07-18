"""Minimal training utilities for the scratch CNN baseline."""

import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.optim import Optimizer

from src.deep_learning.checkpoint import save_checkpoint


def _run_epoch(model, data_loader, criterion, device, optimizer=None):
    """Run one training or validation epoch and return loss and Top-1 metrics."""

    is_training = optimizer is not None
    model.train(is_training)
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    context = torch.enable_grad() if is_training else torch.inference_mode()

    with context:
        for inputs, targets in data_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            if is_training:
                optimizer.zero_grad(set_to_none=True)

            outputs = model(inputs)
            loss = criterion(outputs, targets)

            if is_training:
                loss.backward()
                optimizer.step()

            batch_size = targets.size(0)
            total_loss += loss.item() * batch_size
            total_correct += (outputs.argmax(dim=1) == targets).sum().item()
            total_samples += batch_size

    if total_samples == 0:
        raise ValueError("data_loader must contain at least one sample")

    return {
        "loss": total_loss / total_samples,
        "top1": total_correct / total_samples,
    }


def train_one_epoch(model, data_loader, optimizer: Optimizer, device, criterion=None):
    """Train a model for one epoch using cross-entropy by default."""

    criterion = criterion or nn.CrossEntropyLoss()
    return _run_epoch(model, data_loader, criterion, torch.device(device), optimizer)


def validate_one_epoch(model, data_loader, device, criterion=None):
    """Validate a model for one epoch using cross-entropy by default."""

    criterion = criterion or nn.CrossEntropyLoss()
    return _run_epoch(model, data_loader, criterion, torch.device(device))


def fit_scratch_model(
    model,
    train_loader,
    val_loader,
    optimizer: Optimizer,
    device,
    epochs: int,
    criterion=None,
    checkpoint_path=None,
    start_epoch: int = 0,
    history=None,
    best_val_top1=None,
):
    """Train and validate a scratch model, optionally saving the best checkpoint."""

    if epochs < 1:
        raise ValueError("epochs must be at least 1")
    if start_epoch < 0:
        raise ValueError("start_epoch must be non-negative")

    device = torch.device(device)
    criterion = criterion or nn.CrossEntropyLoss()
    model.to(device)
    history = history or {"train_loss": [], "train_top1": [], "val_loss": [], "val_top1": []}
    best_val_top1 = (
        max(history["val_top1"], default=float("-inf"))
        if best_val_top1 is None
        else best_val_top1
    )

    for epoch in range(start_epoch, start_epoch + epochs):
        train_metrics = train_one_epoch(model, train_loader, optimizer, device, criterion)
        val_metrics = validate_one_epoch(model, val_loader, device, criterion)
        history["train_loss"].append(train_metrics["loss"])
        history["train_top1"].append(train_metrics["top1"])
        history["val_loss"].append(val_metrics["loss"])
        history["val_top1"].append(val_metrics["top1"])

        if checkpoint_path and val_metrics["top1"] > best_val_top1:
            best_val_top1 = val_metrics["top1"]
            save_checkpoint(
                checkpoint_path,
                epoch,
                model,
                optimizer,
                history,
                best_val_top1,
            )

    return history


def plot_training_curves(history):
    """Create loss and Top-1 training curves from a trainer history dictionary."""

    epochs = range(1, len(history["train_loss"]) + 1)
    figure, (loss_axis, top1_axis) = plt.subplots(1, 2, figsize=(10, 4))

    loss_axis.plot(epochs, history["train_loss"], label="train")
    loss_axis.plot(epochs, history["val_loss"], label="validation")
    loss_axis.set(title="Loss", xlabel="Epoch", ylabel="Cross-entropy")
    loss_axis.legend()

    top1_axis.plot(epochs, history["train_top1"], label="train")
    top1_axis.plot(epochs, history["val_top1"], label="validation")
    top1_axis.set(title="Top-1 accuracy", xlabel="Epoch", ylabel="Accuracy")
    top1_axis.legend()

    figure.tight_layout()
    return figure
