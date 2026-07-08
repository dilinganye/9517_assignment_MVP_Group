# Project Log

Every PR must add a short entry to this file before review. Keep entries concise and include the PR title, branch, summary, and validation notes.

## PR Harness

- Every PR must keep implementation changes as small as practical.
- Prefer one focused behavior change per PR.
- Avoid unrelated cleanup, broad refactors, or formatting churn.
- Update this log with the PR title, branch, summary, and validation notes.

## Stabilize data path convention

- Previous PR title: `Add project infrastructure skeleton: Fix requirements.txt and Add README.md as placeholder`
- Branch: `xuanzhou-data-path-log`
- Summary: align the shared split directory with the committed `data/processed/` manifests and add explicit constants for `class_list_500.csv`, `train.csv`, `val.csv`, and `test.csv`.
- Harness: this log is now the required lightweight PR record; future PRs should update it with their own entry.
- Validation: `git diff --check`, `python3 -m compileall src/config.py`, and config path existence checks passed.

## Current PR - Add unified dataset loader

- Previous PR title: `Stabilize data path convention`
- Branch: `xuanzhou-dataset-loader`
- Summary: add a shared CSV-backed iNaturalist Dataset, split-to-manifest helper, and thin DataLoader factory for future traditional and deep learning work.
- Harness: adds the minimal-implementation rule above and follows it by limiting this PR to data loading infrastructure only.
- Validation: `git diff --check`, `py_compile` for data/config modules, and CSV required-column checks passed. Full DataLoader iteration still requires installed project dependencies and local image data.
