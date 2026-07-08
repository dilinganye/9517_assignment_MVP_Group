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

## Add unified dataset loader

- Previous PR title: `Stabilize data path convention`
- Branch: `xuanzhou-dataset-loader`
- Summary: add a shared CSV-backed iNaturalist Dataset, split-to-manifest helper, and thin DataLoader factory for future traditional and deep learning work.
- Harness: adds the minimal-implementation rule above and follows it by limiting this PR to data loading infrastructure only.
- Validation: `git diff --check`, `py_compile` for data/config modules, and CSV required-column checks passed. Full DataLoader iteration still requires installed project dependencies and local image data.

## Add lightweight smoke test

- Previous PR title: `Add unified dataset loader`
- Branch: `xuanzhou-smoke-test`
- Summary: add a standard-library smoke test for shared config paths, CSV schema, expected split sizes, per-class counts, and split overlap.
- Harness: keeps the first smoke test minimal and dependency-light so it can run before heavier training setup.
- Validation: `python scripts/smoke_test.py`, `py_compile`, and `git diff --check` passed.

## Current PR - Add manifest summary script

- Previous PR title: `Add lightweight smoke test`
- Branch: `xuanzhou-data-processing-script`
- Summary: add a standard-library script that summarizes the committed data manifests produced from the data notebooks.
- Harness: keeps notebook-to-script work minimal by documenting and summarizing existing manifests instead of reprocessing large raw archives.
- Validation: `python scripts/summarize_data_manifests.py`, `--output` JSON write/read check, `python scripts/smoke_test.py`, `py_compile`, and `git diff --check` passed.
