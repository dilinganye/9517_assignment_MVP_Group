from torchvision.models import resnet18

from src import config


def create_scratch_resnet18():
    """Create a randomly initialized ResNet18 for the shared class set."""

    return resnet18(weights=None, num_classes=config.NUM_CLASSES)
