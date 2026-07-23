# Traditional Classifiers

This folder contains the classical-classifier training and evaluation work
for the project. It reads the combined HOG + colour histogram features
produced under `../features/` and trains/evaluates classifiers on them.

## Current Files

### `traditional_classifier.ipynb`

Merged into `main` via PR #23 (developed on `Hengyi_TraditionalClassifier2`).

Trains and evaluates two classical classifiers — a Linear SVM and a Random
Forest — on the cached combined features, alongside a nearest-centroid
trivial baseline.

Pipeline:

- Loads the cached features (train/validation/test) and re-checks data
  integrity / split leakage.
- `StandardScaler` (fit on train only) + `PCA` (150 components), then a
  `LinearSVC` trained across a `C` grid selected by validation macro-F1.
- `RandomForestClassifier` (`max_depth=30`, `min_samples_leaf=3`,
  `n_estimators=300`) trained on the full-dimensional scaled features.
- A nearest-centroid classifier evaluated as a trivial, hyperparameter-free
  baseline for reference.

## Shared Configuration

Like the feature-extraction notebooks, this notebook uses the shared project
configuration:

```python
from src import config
```

Paths, the random seed, and the number of classes all come from
`config.py`, so the notebook runs unmodified on any teammate's machine.

## Feature Cache

`outputs/` is git-ignored, so the cached feature files are not in the repo.
The notebook automatically checks several known cache locations (including
`outputs/`, `outputs/traditional_features/`, and `outputs/traditional/features/`),
so it works regardless of where the cache lands. If none of these contain the
cache on a fresh clone, regenerate it by running `../features/features.ipynb`
and `../features/cache.ipynb`, or download the pre-computed feature files from
the OneDrive link in `cache.ipynb` and place them under
`outputs/traditional_features/`.

## Results

Test-set results (500 classes, 40 train / 10 val / 10 test images per class).
All three rows are evaluated on the same held-out test set:

| Model | Top-1 | Top-5 | Macro F1 | Train time |
| --- | --- | --- | --- | --- |
| Nearest-centroid (baseline) | 2.24% | 7.26% | – | – |
| Linear SVM (PCA + `C=1.0`) | 2.42% | 7.54% | 0.018 | ~98s |
| Random Forest | 3.32% | 10.04% | 0.020 | ~398s |

Both classifiers exceed the trivial baseline, but by very different margins:
the Linear SVM only marginally beats it (+0.18pp top-1, +0.28pp top-5),
while Random Forest beats it convincingly (+1.08pp top-1, +2.78pp top-5),
suggesting a non-linear decision boundary extracts more useful structure
from the same features than a linear one can. See the report for discussion.

Note: an earlier version of this table used a baseline computed on the
*validation* set (2.84%/8.24%) instead of the test set, which understated
how close the Linear SVM actually is to trivial performance. The table
above is the corrected, test-set-only comparison.

A descriptor ablation (nearest-centroid, validation set) isolates each
feature's own contribution:

| Descriptor | Dimensions | Top-1 | Top-5 |
| --- | --- | --- | --- |
| HOG only | 6084 | 2.66% | 7.46% |
| Colour histogram only | 96 | 1.38% | 5.42% |
| Combined (HOG + colour) | 6180 | 2.92% | 8.06% |

HOG carries most of the signal; the colour histogram alone is weak, but
combining the two still helps slightly over HOG alone.

Random Forest's own confusion matrix, hardest-class breakdown, and
most-confused species pairs are also reported (alongside the Linear SVM's),
and a sample of misclassified test images is visualised for qualitative
failure analysis.

All outputs (metrics, confusion matrices, most-confused species pairs,
misclassified test images, and the fitted models) are saved under
`outputs/traditional_classifier/`.
