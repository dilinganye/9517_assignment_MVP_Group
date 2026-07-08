# Processed Data Manifests

This directory contains the committed CSV manifests for the selected 500-class iNaturalist-2021 subset.

本目录保存已提交的 CSV 数据清单，对应当前选定的 iNaturalist-2021 500 类子集。

The full image archive is not stored in Git. The current packaged subset is around 2.5 GB and is stored externally:

完整图片压缩包不存放在 Git 中。当前打包好的子集约 2.5 GB，存放在外部链接：

<https://unsw-my.sharepoint.com/:u:/g/personal/z5708767_ad_unsw_edu_au/IQCd2kjjFMcQQZvZZBUCLM74AUqhSjweb5B1IQGVrewxcrQ?e=5OEx5p>

## Committed Files

- `class_list_500.csv`: selected class metadata, including `category_id`, `category_name`, `common_name`, `kingdom`, and `supercategory`.
- `train.csv`: training manifest with `file_path`, `label`, `category_id`, and `category_name`.
- `val.csv`: validation manifest with the same columns as `train.csv`.
- `test.csv`: held-out test manifest based on the official iNaturalist validation split.

已提交文件：

- `class_list_500.csv`: 最终抽中的 500 个类别元信息，包括 `category_id`、`category_name`、`common_name`、`kingdom` 和 `supercategory`。
- `train.csv`: 训练集清单，包含 `file_path`、`label`、`category_id` 和 `category_name`。
- `val.csv`: 验证集清单，字段与 `train.csv` 相同。
- `test.csv`: 独立测试集清单，基于官方 iNaturalist validation split。

The notebook that created these manifests also used a label mapping internally. A standalone `label_mapping.json` is not currently committed.

生成这些清单的 notebook 内部使用了 label mapping；目前没有单独提交 `label_mapping.json` 文件。

## 中文文件用途说明

- `class_list_500.csv` 用于列出最终抽中的 500 个类别。它保存类别元信息，主要包括 `category_id`、`category_name`、`common_name`、`kingdom` 和 `supercategory`，相当于当前 500 类实验子集的总目录。
- label mapping 的作用是保存“原始类别 ID”和“训练标签编号”的对应关系。模型训练时使用连续编号 `label`，后续分析时可以通过映射还原到原始物种类别。当前映射关系已经体现在各 CSV 的 `category_id` 和 `label` 字段中，但没有单独提交 `label_mapping.json`。
- `train.csv` 是训练集清单。每一行对应一张训练图片，包含图片相对路径、训练标签、原始类别 ID 和类别名，用于模型训练阶段读取样本。
- `val.csv` 是验证集清单。字段与 `train.csv` 相同，用于训练过程中的验证、调参和选择 checkpoint。
- `test.csv` 是独立测试集清单。它基于官方 iNaturalist validation split，用于最终固定方案的测试评估；不应在训练调参阶段反复使用。

## Expected Split Sizes

| Split | Rows | Classes | Images per class |
| --- | ---: | ---: | ---: |
| `train.csv` | 20,000 | 500 | 40 |
| `val.csv` | 5,000 | 500 | 10 |
| `test.csv` | 5,000 | 500 | 10 |

预期划分规模：

| 划分 | 行数 | 类别数 | 每类图片数 |
| --- | ---: | ---: | ---: |
| `train.csv` | 20,000 | 500 | 40 |
| `val.csv` | 5,000 | 500 | 10 |
| `test.csv` | 5,000 | 500 | 10 |

## Packaged Subset Layout

```text
tiny_inat_500.tar.gz
|-- annotations/
|   |-- class_list_500.csv
|   |-- test.csv
|   |-- train.csv
|   `-- val.csv
|-- train_mini/
|   |-- 00006_Animalia_Arthropoda_Arachnida_Araneae_Araneidae_Aculepeira_ceropegia/
|   `-- ...
`-- val/
    |-- 00006_Animalia_Arthropoda_Arachnida_Araneae_Araneidae_Aculepeira_ceropegia/
    `-- ...
```

## Script Evidence

Summarize the committed notebook outputs with:

用以下命令汇总已提交的 notebook 输出：

```bash
python scripts/summarize_data_manifests.py
```

Run the lightweight consistency check with:

用以下命令运行轻量一致性检查：

```bash
python scripts/smoke_test.py
```
