from torchvision.models import resnet18

from src import config


def create_scratch_resnet18(num_classes: int = config.NUM_CLASSES):
    """Create a randomly initialized ResNet18 with the requested output head."""

    if num_classes < 1:
        raise ValueError("num_classes must be positive")
    return resnet18(weights=None, num_classes=num_classes)
