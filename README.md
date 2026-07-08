# COMP9517 2026 T2 Group Project

This repository contains the shared code and lightweight data manifests for the COMP9517 group project on iNaturalist-2021 species classification.

本仓库用于保存 COMP9517 小组项目的共享代码和轻量数据清单，任务是基于 iNaturalist-2021 做物种图像分类。

The project currently uses a fixed 500-class subset:

- `train.csv`: 20,000 images, 500 classes, 40 images per class.
- `val.csv`: 5,000 images, 500 classes, 10 images per class.
- `test.csv`: 5,000 images, 500 classes, 10 images per class from the official validation split.

当前项目使用固定的 500 类子集：

- `train.csv`: 20,000 张图片，500 类，每类 40 张。
- `val.csv`: 5,000 张图片，500 类，每类 10 张。
- `test.csv`: 5,000 张图片，500 类，每类 10 张，来自官方 validation split。

Large raw images and generated experiment outputs are intentionally not committed.

大型原始图片和实验生成结果默认不提交到 Git。

## Quick Start

Install project dependencies:

安装项目依赖：

```bash
pip install -r requirements.txt
```

Run the lightweight project check before opening a PR:

开 PR 前运行轻量项目检查：

```bash
python scripts/smoke_test.py
```

Summarize the committed data manifests that came from the data notebooks:

汇总由数据处理 notebook 生成并已提交的数据清单：

```bash
python scripts/summarize_data_manifests.py
```

The same lightweight checks run in GitHub Actions for pull requests and pushes to `main`.

同一组轻量检查也会在 GitHub Actions 中对 PR 和推送到 `main` 的提交自动运行。

## Data Processing Notes

数据处理提示：

- 原始 iNaturalist 标注和图片压缩包很大，处理 JSON 标注时应优先使用流式读取，避免一次性读入内存。
- `ijson` 用于流式解析大型 JSON 标注文件。
- `tqdm` 可用于长时间数据处理任务的进度显示。
- 这些依赖已经写入 `requirements.txt`，通常只需要运行 `pip install -r requirements.txt`。

## Data Layout

Raw iNaturalist files should be placed locally under `data/raw/`, which is ignored by Git:

原始 iNaturalist 文件应放在本地 `data/raw/` 下；该目录被 Git 忽略：

```text
data/raw/
|-- train_mini/
|-- val/
|-- train_mini.tar.gz
|-- train_mini.json.tar.gz
|-- val.tar.gz
`-- val.json.tar.gz
```

Committed data manifests live in `data/processed/`.

已提交的数据清单位于 `data/processed/`。

## Git Ignore Policy

忽略规则说明：

- `data/raw/`：原始数据和解压图片体积过大，不提交。
- `outputs/`：本地实验输出默认不提交，只保留 `outputs/README.md` 说明目录用途。
- `notebooks/`、`docs/`、`submission/`：组内临时实验、个人留痕和最终打包目录默认不提交。
- `*.tar.gz`、`*.zip`、`*.npz`、`*.pth`、`*.pt`、`*.pkl`、`*.joblib`、`*.mp4`、`*.mov`：大型压缩包、模型权重、缓存和视频默认不提交。

## Project Structure

```text
.
|-- .github/workflows/       # Lightweight CI
|-- data/
|   |-- processed/           # Committed CSV manifests
|   `-- raw/                 # Local raw data, ignored by Git
|-- outputs/                 # Local experiment outputs, ignored by Git except README
|-- scripts/                 # Lightweight project checks and manifest scripts
|-- src/
|   |-- advanced/            # Advanced directions such as Grad-CAM or robustness
|   |-- data/                # Dataset and DataLoader utilities
|   |-- deep_learning/       # CNN models and training code
|   |-- traditional/         # Handcrafted features and classical classifiers
|   `-- utils/               # Shared helpers
|-- log.md                   # Required PR log
|-- PR_SUMMARY_CN.md         # Chinese infrastructure summary
`-- requirements.txt
```

## Collaboration Rules

- Keep each PR focused on one small change.
- Update `log.md` or `PR_SUMMARY_CN.md` manually when a PR needs an important record; routine PRs do not need automatic log entries.
- Run `python scripts/smoke_test.py` before opening a PR.
- Do not commit raw data, model checkpoints, generated media, or large experiment outputs.
- Use `src/config.py` for shared paths, random seed, image size, and split constants.

协作规则：

- 每个 PR 尽量只处理一个小改动。
- 只有当 PR 需要记录重要流程、公共约定或交付说明时，才手动更新 `log.md` 或 `PR_SUMMARY_CN.md`；普通 PR 不需要自动写日志。
- 开 PR 前运行 `python scripts/smoke_test.py`。
- 不提交原始数据、模型 checkpoint、生成媒体或大型实验输出。
- 共享路径、随机种子、图片尺寸和 split 常量统一使用 `src/config.py`。

## Current Lightweight CI

The current GitHub Actions workflow only checks the project foundation:

- Python syntax for lightweight scripts and config.
- Data manifest consistency through `scripts/smoke_test.py`.
- Manifest summary generation through `scripts/summarize_data_manifests.py`.

Full training, model evaluation, Grad-CAM, and robustness experiments should run outside CI.

当前 GitHub Actions 只检查项目基础：

- 轻量脚本和配置文件的 Python 语法。
- 通过 `scripts/smoke_test.py` 检查数据清单一致性。
- 通过 `scripts/summarize_data_manifests.py` 生成数据清单摘要。

完整训练、模型评估、Grad-CAM 和鲁棒性实验应在 CI 之外运行。
