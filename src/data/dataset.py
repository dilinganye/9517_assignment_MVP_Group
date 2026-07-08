import csv
from pathlib import Path
from typing import Callable, Optional, Union

from PIL import Image
from torch.utils.data import DataLoader, Dataset

from src import config

PathLike = Union[str, Path]

SPLIT_TO_CSV = {
    "train": config.TRAIN_CSV,
    "val": config.VAL_CSV,
    "test": config.TEST_CSV,
}


class InatCsvDataset(Dataset):
    """Dataset backed by one of the shared iNaturalist CSV manifests."""

    def __init__(
        self,
        manifest_csv: PathLike,
        image_root: Optional[PathLike] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ):
        self.manifest_csv = Path(manifest_csv)
        self.image_root = Path(image_root) if image_root is not None else config.DATA_RAW_ROOT
        self.transform = transform
        self.target_transform = target_transform
        self.samples = self._load_samples(self.manifest_csv)

    @staticmethod
    def _load_samples(manifest_csv: Path):
        with manifest_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_columns = {"file_path", "label"}
            missing = required_columns.difference(reader.fieldnames or [])
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise ValueError(f"{manifest_csv} is missing required columns: {missing_text}")

            return [(row["file_path"], int(row["label"])) for row in reader]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        relative_path, label = self.samples[index]
        image_path = self.image_root / relative_path
        image = Image.open(image_path).convert("RGB")

        if self.transform is not None:
            image = self.transform(image)
        if self.target_transform is not None:
            label = self.target_transform(label)

        return image, label


def get_manifest_path(split: str) -> Path:
    """Return the shared manifest path for train, val, or test."""

    try:
        return SPLIT_TO_CSV[split]
    except KeyError as exc:
        valid = ", ".join(sorted(SPLIT_TO_CSV))
        raise ValueError(f"Unknown split '{split}'. Expected one of: {valid}") from exc


def create_dataset(
    split: str,
    image_root: Optional[PathLike] = None,
    transform: Optional[Callable] = None,
    target_transform: Optional[Callable] = None,
) -> InatCsvDataset:
    """Create a dataset using the shared manifest for a split."""

    return InatCsvDataset(
        get_manifest_path(split),
        image_root=image_root,
        transform=transform,
        target_transform=target_transform,
    )


def create_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool = False,
    num_workers: int = 0,
    pin_memory: bool = False,
    drop_last: bool = False,
) -> DataLoader:
    """Create a DataLoader with project-default explicit options."""

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
    )
