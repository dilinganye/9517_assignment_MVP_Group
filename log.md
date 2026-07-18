# Project Log

This file is an optional project record. Routine PRs do not need automatic entries; update it manually when a PR changes an important workflow, shared convention, delivery note, or maintenance decision.

## PR Harness

- Keep each PR as small and focused as practical.
- Prefer one focused behavior change per PR.
- Avoid unrelated cleanup, broad refactors, or formatting churn.
- Update this log only when the PR needs a durable project record.

When this file is updated, use this format:

```md
## PR #<number> - <title>

- Author: xuanzhougu
- Branch: `<branch-name>`
- PR created: YYYY-MM-DD HH:MM:SS AEST
- PR merged: YYYY-MM-DD HH:MM:SS AEST
- Summary: ...
- Validation: ...
```

## PR #1 - Add project infrastructure skeleton: Fix requirements.txt and Add README.md as placeholder

- Author: xuanzhougu
- Branch: `xuanzhou-infra-supplement`
- PR created: 2026-07-08 22:57:31 AEST
- PR merged: 2026-07-08 22:57:48 AEST
- Summary: add the first infrastructure skeleton, including `requirements.txt`, lightweight README placeholders, and output ignore rules.
- Validation: `git diff --check` and Python compile checks passed before push.

## PR #2 - Stabilize data path convention

- Author: xuanzhougu
- Branch: `xuanzhou-data-path-log`
- PR created: 2026-07-08 23:05:36 AEST
- PR merged: 2026-07-08 23:09:11 AEST
- Summary: align the shared split directory with the committed `data/processed/` manifests and add explicit constants for `class_list_500.csv`, `train.csv`, `val.csv`, and `test.csv`.
- Validation: `git diff --check`, `python3 -m compileall src/config.py`, and config path existence checks passed.

## PR #3 - Add unified dataset loader

- Author: xuanzhougu
- Branch: `xuanzhou-dataset-loader`
- PR created: 2026-07-08 23:15:32 AEST
- PR merged: 2026-07-08 23:17:22 AEST
- Summary: add a shared CSV-backed iNaturalist Dataset, split-to-manifest helper, and thin DataLoader factory for future traditional and deep learning work.
- Validation: `git diff --check`, `py_compile` for data/config modules, and CSV required-column checks passed. Full DataLoader iteration still requires installed project dependencies and local image data.

## PR #4 - Add lightweight smoke test

- Author: xuanzhougu
- Branch: `xuanzhou-smoke-test`
- PR created: 2026-07-08 23:21:13 AEST
- PR merged: 2026-07-08 23:23:56 AEST
- Summary: add a standard-library smoke test for shared config paths, CSV schema, expected split sizes, per-class counts, and split overlap.
- Validation: `python scripts/smoke_test.py`, `py_compile`, and `git diff --check` passed.

## PR #5 - Add manifest summary script

- Author: xuanzhougu
- Branch: `xuanzhou-data-processing-script`
- PR created: 2026-07-08 23:28:44 AEST
- PR merged: 2026-07-08 23:31:45 AEST
- Summary: add a standard-library script that summarizes the committed data manifests produced from the data notebooks.
- Validation: `python scripts/summarize_data_manifests.py`, `--output` JSON write/read check, `python scripts/smoke_test.py`, `py_compile`, and `git diff --check` passed.

## PR #6 - Add minimal CI

- Author: xuanzhougu
- Branch: `xuanzhou-minimal-ci`
- PR created: 2026-07-08 23:36:35 AEST
- PR merged: 2026-07-08 23:37:31 AEST
- Summary: add a GitHub Actions workflow that runs only dependency-light checks for PRs and pushes to `main`.
- Validation: local CI-equivalent commands passed: `py_compile`, `python scripts/smoke_test.py`, `python scripts/summarize_data_manifests.py --output ...`, and `git diff --check`.

## PR #7 - Polish README files

- Author: xuanzhougu
- Branch: `xuanzhou-readme-polish`
- PR created: 2026-07-08 23:45:37 AEST
- PR merged: 2026-07-09 00:51:42 AEST
- Summary: fix README formatting, remove outdated draft wording, align processed data documentation with committed files, expand the root README with current project entry points, add Chinese explanations, preserve useful original data-processing notes, and add a Chinese infrastructure PR summary.
- Validation: `python scripts/smoke_test.py`, `python scripts/summarize_data_manifests.py --output ...`, README cleanup search, and `git diff --check` passed.

## PR #10 - Add scratch ResNet18 factory

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-resnet18`
- PR created: 2026-07-17 23:46:17 AEST
- PR merged: pending
- Summary: add the D-owned factory for a randomly initialized ResNet18 using the shared 500-class setting; no pretrained weights, trainer, checkpoint, or transfer-learning behavior are included.
- Validation: `git diff --check`, Python syntax compilation, and `python scripts/smoke_test.py` passed. Local model construction was not run because PyTorch is not installed in this environment.

## PR #11 - Extraction of HOG (Histogram of Oriented Gradients)

- Author: Chaohao Liu
- Branch: `Chaohao_TraditionalFeature1`
- PR created: 2026-07-18 13:24 AEST
- PR merged: 2026-07-18 15:40 AEST
- Summary: Added `hog.ipynb` for the traditional feature extraction pipeline. The notebook loads sample images using the shared project configuration, resizes them to 224 × 224, converts them to grayscale, extracts HOG features, displays the HOG visualisation, and provides a reusable HOG extraction function.
- Validation: The notebook ran successfully on sample images from different classes. All tested images produced `float32` HOG feature vectors with the same fixed shape of (6084,).

## PR #12 - Extraction of Colour Histogram Features

- Author: Chaohao Liu
- Branch: `Chaohao_TraditionalFeature2`
- PR created: 2026-07-18 16:40 AEST
- PR merged: pending
- Summary: Added `color.ipynb` for colour histogram feature extraction. The notebook loads sample images, resizes them to 224 × 224, calculates a normalised 32-bin histogram for each RGB channel, and combines the three histograms into one feature vector. It also includes a histogram visualisation and a reusable function for later feature extraction.
- Validation: The notebook ran successfully on images from different classes. Each image produced a `float32` feature vector with shape `(96,)`. The histogram for each RGB channel was normalised to sum to `1.0`, and all tested images produced the same feature length.