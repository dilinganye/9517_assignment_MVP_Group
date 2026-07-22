# Traditional Classifiers

This folder contains the classical-classifier training and evaluation work
for the project. It reads the combined HOG + colour histogram features
produced under `../features/` and trains/evaluates classifiers on them.

## Current Files

### `traditional_classifier.ipynb`

Branch: `Hengyi_TraditionalClassifier2`

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

## Results

Test-set results (500 classes, 40 train / 10 val / 10 test images per class):

| Model | Top-1 | Top-5 | Macro F1 | Train time |
| --- | --- | --- | --- | --- |
| Nearest-centroid (baseline) | 2.84% | 8.24% | – | – |
| Linear SVM (PCA + `C=1.0`) | 2.42% | 7.54% | 0.018 | ~100s |
| Random Forest | 3.32% | 10.04% | 0.020 | ~407s |

The Linear SVM does not exceed the trivial baseline on this feature
representation, while Random Forest does. See the report for discussion.

All outputs (metrics, confusion matrices, most-confused species pairs,
misclassified test images, and the fitted models) are saved under
`outputs/traditional_classifier/`.

## Current Branch

Current branch:

`Hengyi_TraditionalClassifier2`
