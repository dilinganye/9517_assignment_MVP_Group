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

## Validation

| Feature | Shape | Data type |
| --- | --- | --- |
| HOG | `(6084,)` | `float32` | Fixed |
| RGB colour histogram | `(96,)` | `float32` | Fixed |
| Combined HOG and colour | `(6180,)` | `float32` | Fixed |
| SIFT descriptors | `(N, 128)` | `float32` | Variable |

HOG and colour features describe the image using one fixed-length vector.

SIFT describes multiple local regions in an image, so the number of descriptors depends on the detected keypoints.


## Maintenance

When adding a new feature:

- use the shared settings from `config.py`
- accept a PIL image as input
- return a one-dimensional `float32` NumPy array
- keep the output length fixed
- test the method on images from different classes
