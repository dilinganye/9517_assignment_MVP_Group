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

### `sift.ipynb`

Branch: `Chaohao_TraditionalFeature4`

This notebook detects SIFT keypoints and extracts local descriptors from a PIL image.

Reusable function:

```python
extract_sift_feature(image, max_features=500)
```

Main processing steps:

1. Convert the image to RGB.
2. Resize the image using `config.IMG_SIZE`.
3. Convert the image to grayscale.
4. Detect SIFT keypoints.
5. Extract one 128-value descriptor for each keypoint.
6. Visualise the detected keypoints.
7. Test the extractor on images from different classes.
8. Check descriptor shape, data type, and values.

Output:

```text
Data type: float32
Descriptor shape: (N, 128)
```

`N` is the number of detected keypoints and may be different for every image.

The parameter:

```python
max_features=500
```

requests approximately 500 of the strongest keypoints. The returned number may be slightly different because SIFT can create multiple keypoints with different orientations at the same image location.

Every valid SIFT descriptor contains 128 values.


## Shared Configuration

All notebooks use the shared project configuration:

```python
from src import config
```

The shared configuration provides:

- project paths
- dataset CSV paths
- image size
- random seed
- number of classes

Images are resized using:

```python
config.IMG_SIZE
```

Dataset manifests are loaded using:

```python
config.TRAIN_CSV
config.VAL_CSV
config.TEST_CSV
```

Raw images are loaded from:

```python
config.DATA_RAW_ROOT
```

Personal absolute paths should not be added to the notebooks.

## Data Location

Raw images should be stored locally under:

```text
data/raw/
├── train_mini/
└── val/
```

Dataset manifests are stored under:

```text
data/processed/
├── train.csv
├── val.csv
└── test.csv
```

The raw image files are not committed to Git.

## Validation

| Feature | Shape | Data type |
| --- | --- | --- |
| HOG | `(6084,)` | `float32` | Fixed |
| RGB colour histogram | `(96,)` | `float32` | Fixed |
| Combined HOG and colour | `(6180,)` | `float32` | Fixed |
| SIFT descriptors | `(N, 128)` | `float32` | Variable |

Both methods were tested on images from different classes and produced fixed-length feature vectors.

## Current Branch

Current branch:

`Chaohao_TraditionalFeature3`

This branch continues the pipeline by combining the HOG and colour features.

```text
HOG:      6084
Colour:     96
Combined:    6180
```

## Maintenance

When adding a new feature:

- use the shared settings from `config.py`
- accept a PIL image as input
- return a one-dimensional `float32` NumPy array
- keep the output length fixed
- test the method on images from different classes
