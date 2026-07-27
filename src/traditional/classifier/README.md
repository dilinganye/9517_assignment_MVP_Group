# Traditional Classifiers

This folder contains the classical-classifier training and evaluation work
for the project. It reads the combined HOG + colour histogram features
produced under `../features/` and trains/evaluates classifiers on them.

## Current Files

### `traditional_classifier.ipynb`

Merged into `main` via PR #23 (developed on `Hengyi_TraditionalClassifier2`).
A follow-up fix — the trivial baseline in the comparison table was
originally evaluated on the validation set instead of the test set — was
added on `Hengyi_TraditionalClassifier3`.

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

### `sift_bovw_classifier.ipynb`

Developed on `Hengyi_TraditionalClassifier3`.

Adds a third handcrafted descriptor: SIFT keypoints encoded as a
Bag-of-Visual-Words (BoVW) histogram. Self-contained — does not depend on
`../features/sift.ipynb`'s kernel, but reuses the same SIFT settings
(`cv2.SIFT_create(nfeatures=500)`, grayscale, `config.IMG_SIZE`-resized) so
results are directly comparable.

Pipeline:

- Builds a `MiniBatchKMeans` visual vocabulary (300 words) from a sample of
  training-image SIFT descriptors.
- Encodes every train/validation/test image as an L2-normalised
  word-frequency histogram and caches the result
  (`outputs/*_sift_bovw_features.npz`).
- Evaluates a nearest-centroid baseline, Linear SVM, and Random Forest on the
  SIFT-BoVW features, using the same validation-only hyperparameter
  selection and single test-set evaluation methodology as
  `traditional_classifier.ipynb`.
- Optional final section: concatenates SIFT-BoVW with the cached HOG +
  colour feature and retrains a Linear SVM, to test whether SIFT improves on
  HOG + colour alone.

Outputs are saved under `outputs/sift_bovw_classifier/`.

**Results** (test set, 500 classes, 5,000 test images):

| Model | Top-1 | Top-5 | Macro F1 |
| --- | --- | --- | --- |
| Nearest-centroid (baseline) | 3.58% | 11.80% | – |
| Linear SVM (`C=0.001`) | 3.72% | 10.24% | 0.0258 |
| Random Forest | 2.64% | 8.72% | 0.0183 |

SIFT-BoVW's baseline alone (3.58%/11.80%) already beats the HOG + colour
baseline (2.24%/7.26%), and its Linear SVM (3.72% top-1) is the best top-1
result of any traditional-classifier configuration so far. Unlike the
HOG + colour pipeline, Random Forest performs *worse* here than its own
trivial baseline — the same regularised hyperparameters that worked well on
HOG + colour do not automatically transfer to this feature space; see the
report for discussion, and treat re-tuning Random Forest for this feature
set as future work rather than something resolved here.

Concatenating SIFT-BoVW with HOG + colour and retraining (PCA(150) + Linear
SVM) reaches 2.96% top-1 / 10.10% top-5 / 0.0219 macro F1 — *worse* than
SIFT-BoVW alone on top-1, likely because the shared PCA is dominated by the
much larger (6180-D vs 300-D) HOG + colour block. Full numbers in
`outputs/sift_bovw_classifier/descriptor_comparison_with_sift.csv`.

Same error-analysis visuals as `traditional_classifier.ipynb`: a full
confusion matrix, a focused confusion-matrix plot for the 15 hardest
classes, and a most-confused-pairs table for the Linear SVM and Random
Forest, plus a sample of misclassified test images with true/predicted
labels. With only 10 test images per class, 381 of 500 classes (76%) have
0% test accuracy under the Linear SVM, and 411 of 500 (82%) under Random
Forest. As with HOG + colour, the misclassified examples and most-confused
pairs are frequently between visually and taxonomically unrelated species
(e.g. a fish predicted as a primate, a butterfly predicted as a bear),
reinforcing that the handcrafted feature representation — not just the
classifier — is the main bottleneck on this fine-grained task.

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
