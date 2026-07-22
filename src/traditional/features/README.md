# Traditional Feature Extraction

This folder contains the traditional feature extraction work for the project.

## Current Files

### `hog.ipynb`

Branch: `Chaohao_TraditionalFeature1`

This notebook extracts HOG features from a PIL image.

```python
extract_hog_feature(image)
```

Output:

- Data type: `float32`
- Shape: `(6084,)`

HOG settings:

```python
orientations=9
pixels_per_cell=(16, 16)
cells_per_block=(2, 2)
block_norm="L2-Hys"
```

### `color.ipynb`

Branch: `Chaohao_TraditionalFeature2`

This notebook extracts a normalised RGB colour histogram from a PIL image.

```python
extract_colour_feature(image, bins=32)
```

Output:

- Data type: `float32`
- Shape: `(96,)`

Each RGB channel uses 32 bins. The three normalised histograms are combined into one feature vector.

### `combine.ipynb`

Branch: `Chaohao_TraditionalFeature3`

This notebook combines the HOG feature and RGB colour histogram into one fixed-length feature vector.

```python
extract_combined_feature(image)
```

Output:

- Data type: `float32`
- Shape: `(6180,)`

The combined feature contains 6084 HOG values and 96 RGB colour histogram values. The notebook also checks that the output length is fixed and contains no missing or infinite values.

### `features.ipynb`

Branch: `Chaohao_TraditionalFeature5`

This notebook applies the combined HOG and RGB colour feature extractor to the complete training, validation, and test datasets.

For each image, it:

- loads the image from the dataset path
- resizes the image using `config.IMG_SIZE`
- extracts the HOG feature with shape `(6084,)`
- extracts the RGB colour histogram with shape `(96,)`
- combines both features into one vector with shape `(6180,)`

The notebook then creates the full feature matrices:

```text
X_train
X_validation
X_test
```

It also stores the corresponding labels and image paths.

Output files are saved in:

```text
outputs/traditional_features/
```

The generated files are:

- `train_combined_features.npz`
- `validation_combined_features.npz`
- `test_combined_features.npz`

Each `.npz` file contains:

- `features`
- `labels`
- `file_paths`

The notebook checks that all feature vectors have length `6180`, use the `float32` data type, contain no missing or infinite values, and match the number of labels and image paths.

### `cache.ipynb`

Branch: `Chaohao_TraditionalFeature5`

This notebook loads the combined HOG and RGB colour feature files created by `features.ipynb`.

The feature files are loaded from:

```text
outputs/traditional_features/
```

Because the `outputs` folder is ignored by Git, the generated `.npz` files are shared separately through OneDrive.

After downloading, the following files should be placed in `outputs/traditional_features/`:

- `train_combined_features.npz`
- `validation_combined_features.npz`
- `test_combined_features.npz`

The notebook loads and prepares:

```text
X_train, y_train, train_paths
X_val, y_val, val_paths
X_test, y_test, test_paths
```

These variables match the inputs expected by `traditional_classifier.ipynb`.

The notebook also displays the dataset split sizes and a sample cached feature vector. It does not repeat the complete feature validation already performed in `features.ipynb`.

## Shared Configuration

All notebooks use the shared project configuration:

```python
from src import config
```

The main settings are:

```python
config.IMG_SIZE
config.DATA_RAW_ROOT
config.TRAIN_CSV
config.VAL_CSV
config.TEST_CSV
```

Images are resized using `config.IMG_SIZE`, and all dataset paths come from `config.py`.

## Validation

| Feature | Shape | Data type |
| --- | --- | --- |
| HOG | `(6084,)` | `float32` |
| RGB colour histogram | `(96,)` | `float32` |
| Combined feature | `(6180,)` | `float32` |
| Full dataset feature matrix | `(N, 6180)` | `float32` |

The feature extraction methods were tested on images from different classes.

The dataset feature notebook also checks that:

- every image produces a feature vector with length `6180`
- all feature values are finite
- the numbers of features, labels, and image paths match
- the saved `.npz` files can be loaded correctly

## Current Branch

Current branch: `Chaohao_TraditionalFeature3`

This branch continues the pipeline by combining the HOG and colour features.

```text
HOG:      6084
Colour:     96
Combined:    6180
```

Current branch: `Chaohao_TraditionalFeature5`

This branch applies the combined HOG and colour feature extractor to the complete dataset.

```text
Single image:        (6180,)
Full dataset:        (N, 6180)
```

The extracted train, validation, and test features are saved in:

```text
outputs/traditional_features/
```

These files can be used directly for traditional classifier training.

## Downloading Cached Features

The generated traditional feature files are shared through OneDrive:

[Download traditional feature files](https://unsw-my.sharepoint.com/:f:/g/personal/z5528581_ad_unsw_edu_au/IgAsAxZV1fJQSbL1AAmSgGoaAU-ZRhVTJmVLsHFxH7leipA?e=beAfW7)

After downloading, place the files in:

```text
outputs/traditional_features/
```

## Maintenance

When adding a new feature:

- use the shared settings from `config.py`
- accept a PIL image as input
- return a one-dimensional `float32` NumPy array
- keep the output length fixed
- test the method on images from different classes
