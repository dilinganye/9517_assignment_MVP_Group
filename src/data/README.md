# Data Module

Dataset preparation, manifest loading, and shared data access utilities belong here.

Use `src.data.create_dataset(split)` for the shared `train`, `val`, and `test` CSV manifests, then wrap the returned dataset with `src.data.create_dataloader(...)`.
