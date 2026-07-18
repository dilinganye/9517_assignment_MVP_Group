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

Both notebooks use the shared project configuration:

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

The notebook functions will later be moved into `.py` files for use by the full pipeline
