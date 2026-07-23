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

## Scratch Experiment Record - augmentation_v1

- Owner: xuanzhougu
- Environment: Google Colab Tesla T4, batch size 64, two DataLoader workers, 20 epochs, training-only augmentation.
- Training time: approximately 46 minutes of wall-clock time shown by the completed Colab cell. This is a manually observed record because the original run predated automatic epoch timing.
- Selection: best validation Top-1 was 0.2458 at epoch 19.
- Final test: the selected checkpoint achieved Top-1 0.2440 and Top-5 0.4912 on the held-out test set. Do not tune or rerun test-based model selection.

## PR #30 - Add continual learning task plan

- Author: xuanzhougu
- Branch: `xuanzhou-cl-task-setup`
- PR created: 2026-07-23 22:40:43 AEST
- PR merged: pending
- Summary: start the D-owned scratch continual-learning direction with a deterministic committed 100-class, 10-task map, plan verification command, minimal CI coverage, and bilingual documentation for class-incremental no-replay versus class-balanced replay experiments.
- Validation: `git diff --check`, Python compile-all, manifest smoke test, manifest summary generation, deterministic default and alternate-seed task-plan checks, and verification that every task filters to 400 train, 100 validation, and 100 test samples passed. No GPU training, replay, model weights, or test evaluation was run.

## PR #29 - Add scratch timing and evaluation analysis

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-analysis-timing`
- PR created: 2026-07-23 21:27:16 AEST
- PR merged: 2026-07-23 21:32:37 AEST
- Summary: add post-hoc scratch test analysis from saved predictions, record per-epoch and cumulative training time for future scratch runs, document the completed Colab timing observation, and refresh project status and known report guardrails.
- Validation: `git diff --check`, Python compile-all, manifest smoke test, CPU synthetic trainer timing check, synthetic 500-class prediction-analysis artifacts, and both entry-point `--help` checks passed. No raw images, model weights, or test inference were run.

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
- PR merged: 2026-07-17 23:49:26 AEST
- Summary: add the D-owned factory for a randomly initialized ResNet18 using the shared 500-class setting; no pretrained weights, trainer, checkpoint, or transfer-learning behavior are included.
- Validation: `git diff --check`, Python syntax compilation, and `python scripts/smoke_test.py` passed. Local model construction was not run because PyTorch is not installed in this environment.

## PR #15 - Add scratch trainer

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-trainer`
- PR created: 2026-07-18 22:18:55 AEST
- PR merged: 2026-07-18 22:21:32 AEST
- Summary: add minimal scratch-CNN training and validation epochs with cross-entropy, device handling, loss and Top-1 metrics, per-epoch history, and training-curve plotting.
- Validation: `git diff --check`, Python syntax compilation, two synthetic CPU train/validation epochs with 500-class labels and curve creation, and `python scripts/smoke_test.py` passed.

## PR #16 - Add scratch checkpoint support

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-checkpoint`
- PR created: 2026-07-18 22:52:57 AEST
- PR merged: 2026-07-18 22:58:16 AEST
- Summary: add best-validation-Top-1 checkpoints and a resume helper that restores model, optimizer, history, and the next epoch.
- Validation: `git diff --check`, Python syntax compilation, a synthetic CPU checkpoint round trip including model and SGD momentum restoration followed by one resumed epoch, and `python scripts/smoke_test.py` passed.

## PR #20 - Add CUDA scratch training entry point

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-training-entry`
- PR created: 2026-07-21 22:49:02 AEST
- PR merged: 2026-07-21 23:20:53 AEST
- Summary: add a CUDA-only entry point that connects the shared manifests, scratch ResNet18, trainer, best-checkpoint resume, and local run artifacts.
- Validation: `git diff --check`, Python syntax compilation, direct `--help` invocation, a history CSV and transform helper smoke test, a CUDA-unavailable guard check, and `python scripts/smoke_test.py` passed. Full training requires NVIDIA CUDA and local raw images, which are unavailable in this environment.

## PR #25 - Add scratch training augmentation

- Author: xuanzhougu
- Branch: `xuanzhou-scratch-train-augmentation`
- PR created: 2026-07-22 22:54:42 AEST
- PR merged: 2026-07-22 22:58:07 AEST
- Summary: add an opt-in training-only augmentation flag for controlled scratch ResNet18 comparison against the completed no-augmentation baseline.
- Validation: `git diff --check`, Python syntax compilation, direct `--help` invocation, helper checks for the deterministic and augmented transforms plus history CSV output, a CUDA-unavailable guard check, and `python scripts/smoke_test.py` passed. Full CUDA training remains for Colab.

## PR #26 - Add unified final evaluation

- Author: xuanzhougu
- Branch: `xuanzhou-unified-final-evaluation`
- PR created: 2026-07-23 00:02:25 AEST
- PR merged: 2026-07-23 00:06:35 AEST
- Summary: add shared classification metrics and a CUDA scratch-ResNet18 test entry that writes a common local evaluation artifact format.
- Validation: `git diff --check`, CI-equivalent Python syntax compilation, synthetic 500-class shared-metric checks, prediction CSV and confusion-plot artifact checks, checkpoint compatibility, missing-checkpoint and CUDA-unavailable guards, and `python scripts/smoke_test.py` passed. Full CUDA test evaluation remains for Colab.

## PR #28 - Add safe scratch resume checkpoints

- Author: xuanzhougu
- Branch: `xuanzhou-last-checkpoint-resume-guard`
- PR created: 2026-07-23 20:45:46 AEST
- PR merged: 2026-07-23 20:48:12 AEST
- Summary: save separate best and latest scratch checkpoints, and reject resumes with training-defining configuration mismatches.
- Validation: `git diff --check`, CI-equivalent Python syntax compilation, direct training-entry `--help`, synthetic CPU best/last checkpoint round trips, resume configuration mismatch rejection, legacy-checkpoint evaluation compatibility with resume rejection, and `python scripts/smoke_test.py` passed. Full CUDA training remains for Colab.

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
- PR merged: 2026-07-18 16:45 AEST
- Summary: Added `color.ipynb` for colour histogram feature extraction. The notebook loads sample images, resizes them to 224 × 224, calculates a normalised 32-bin histogram for each RGB channel, and combines the three histograms into one feature vector. It also includes a histogram visualisation and a reusable function for later feature extraction.
- Validation: The notebook ran successfully on images from different classes. Each image produced a `float32` feature vector with shape `(96,)`. The histogram for each RGB channel was normalised to sum to `1.0`, and all tested images produced the same feature length.

## PR #14 - Combined HOG and Colour Feature Extraction

- Author: Chaohao Liu
- Branch: `Chaohao_TraditionalFeature3`
- PR created: 2026-07-18 21:34 AEST
- PR merged: 2026-07-18 21:38 AEST
- Summary: Added `combine.ipynb` to combine the HOG feature and RGB colour histogram into one fixed-length feature vector. The notebook extracts 6084 HOG values and 96 colour histogram values, then concatenates them into a single reusable feature vector using `extract_combined_feature(image)`. It also checks the feature order, output shape, data type, and validity.
- Validation: The notebook ran successfully on images from different classes. Each image produced a `float32` feature vector with shape `(6180,)`. The HOG and colour sections matched the original feature vectors, all tested images produced the same feature length, and no missing or infinite values were found.There is no error.


## PR #17 - Full Dataset Feature Extraction

- Author: Chaohao Liu
- Branch: `Chaohao_TraditionalFeature5`
- PR created: 2026-07-20 20:35 AEST
- PR merged: 2026-07-20 21:09 AEST
- Summary: Added `features.ipynb` to apply the combined HOG and RGB colour feature extractor to the complete training, validation, and test datasets. The notebook loads each image, extracts 6084 HOG values and 96 colour histogram values, combines them into one `float32` feature vector with shape `(6180,)`, and stores the corresponding labels and image paths. The extracted results are saved as compressed `.npz` files in `outputs/traditional_features/`.
- Validation: The notebook first tested the feature extractor on a small group of images before processing the complete dataset. Every image produced a feature vector with shape `(6180,)` and data type `float32`. The numbers of features, labels, and image paths matched for all dataset splits. No missing or infinite values were found, and the saved `.npz` files were loaded successfully with the same data. There is no error.

## PR #24 - Full Dataset Feature Extraction and Cache Loading

- Author: Chaohao Liu
- Branch: `Chaohao_TraditionalFeature5`
- PR created: pending
- PR merged: pending
- Summary: Added `features.ipynb` to apply the combined HOG and RGB colour feature extractor to the complete training, validation, and test datasets. Each image is converted into a `float32` feature vector with shape `(6180,)`, containing 6084 HOG values and 96 RGB colour histogram values. The extracted features, labels, and image paths are saved as compressed `.npz` files in `outputs/traditional_features/`. Added `cache.ipynb` to load these feature files and prepare `X_train`, `X_val`, and `X_test` with their corresponding labels and image paths for `traditional_classifier.ipynb`. The notebook also includes simple visualisations of the dataset split sizes and a sample cached feature vector.
- Validation: `features.ipynb` successfully produced fixed-length feature matrices for the training, validation, and test datasets. All feature matrices used the `float32` data type, contained no missing or infinite values, and matched the numbers of labels and image paths. The saved `.npz` files were loaded successfully by `cache.ipynb`, and the returned variable names and shapes matched the inputs expected by `traditional_classifier.ipynb`. There is no error.
