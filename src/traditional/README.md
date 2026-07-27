# Traditional Methods

Handcrafted-feature computer vision pipeline for the project: feature
extraction and classical classifiers.

- [`features/`](features/README.md) — HOG, colour-histogram, and SIFT
  keypoint feature extraction, and the cached combined feature files used
  for training.
- [`classifier/`](classifier/README.md) — Linear SVM and Random Forest
  classifiers trained on three feature representations (HOG + colour,
  SIFT encoded as Bag-of-Visual-Words, and the two combined), plus
  evaluation and error analysis.

See each subfolder's README for details on the notebooks, pipeline, and
results.
