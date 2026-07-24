# Data Module

Dataset preparation, manifest loading, and shared data access utilities belong here.

Use `src.data.create_dataset(split)` for the shared `train`, `val`, and `test` CSV manifests, then wrap the returned dataset with `src.data.create_dataloader(...)`.

For the scratch continual-learning study, use
`src.data.create_continual_dataset(split, task_ids)`. It filters the existing
manifest with the committed task plan and remaps source labels to fixed 0-99
continual labels without duplicating image-path CSV files.
