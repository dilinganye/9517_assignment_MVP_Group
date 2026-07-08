# Project Log

Every PR must add a short entry to this file before review. Keep entries concise and include the PR title, branch, summary, and validation notes.

## Current PR - Stabilize data path convention

- Previous PR title: `Add project infrastructure skeleton: Fix requirements.txt and Add README.md as placeholder`
- Branch: `xuanzhou-data-path-log`
- Summary: align the shared split directory with the committed `data/processed/` manifests and add explicit constants for `class_list_500.csv`, `train.csv`, `val.csv`, and `test.csv`.
- Harness: this log is now the required lightweight PR record; future PRs should update it with their own entry.
- Validation: `git diff --check`, `python3 -m compileall src/config.py`, and config path existence checks passed.
