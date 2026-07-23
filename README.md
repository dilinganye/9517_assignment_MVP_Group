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

## Final Evaluation

Select a model using validation results, then run the held-out test set once. For the
scratch ResNet18 candidate trained with augmentation on Colab:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/evaluate_scratch_resnet18.py \
  --checkpoint /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/augmentation_v1/best_checkpoint.pt \
  --image-root /content/inat_data \
  --output-dir /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation
```

The command writes `metrics.json`, `evaluation_config.json`, per-image
`predictions.csv`, and the full confusion matrix as CSV and PNG. Analyse the
saved predictions without rerunning test inference:

```bash
python scripts/analyze_scratch_evaluation.py \
  --predictions /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/predictions.csv
```

This writes per-class precision/recall/F1, the most frequent species-confusion
pairs, and a readable confusion plot for the lowest-recall classes. The shared
`src.evaluation.evaluate_class_scores` helper defines the common Top-1, Top-5,
overall accuracy, macro precision, macro recall, and macro F1 fields.

先根据验证集选择模型，再只在保留的 test 集上运行一次最终评估。上面的 Colab
命令使用带增强的 scratch ResNet18 候选模型。它会写入 `metrics.json`、
`evaluation_config.json`、逐图片的 `predictions.csv`，以及 CSV 和 PNG 格式的完整
混淆矩阵。无需再次运行 test 推理，即可分析已保存的预测：

```bash
python scripts/analyze_scratch_evaluation.py \
  --predictions /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/predictions.csv
```

该脚本会写入每类 precision/recall/F1、最常见物种混淆对，以及针对 recall 最低类别的可读混淆图。共享的
`src.evaluation.evaluate_class_scores` 规定 Top-1、Top-5、overall accuracy、macro
precision、macro recall 和 macro F1 字段。

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

## Project Progress and Advanced Direction

### Current Status

- The shared 500-class manifests, Dataset/DataLoader entry points, manifest checks, and lightweight CI are in place.
- Traditional HOG and colour-histogram features, plus Linear SVM and Random Forest classifier baselines, are available. The final report must document SVM selection from validation results only; the current notebook commentary should not use test-set comparisons to justify a hyperparameter choice.
- The scratch-CNN path now includes a randomly initialized ResNet18 factory, epoch-level trainer, loss and Top-1 history, training-time recording, curve plotting, best/last checkpoints with resume guards, and final test evaluation. The completed augmentation run reached validation Top-1 0.2458 at epoch 19 and held-out test Top-1 0.2440. Its Colab Tesla T4 cell showed approximately 46 minutes of wall-clock time; this is a manually observed historical record, while future runs write per-epoch and total timing automatically.
- The pretrained-CNN path has a ResNet18 training and ablation notebook with a small end-to-end validation run. Full 500-class results and final evaluation remain outstanding.

### Known Gaps and Report Guardrails

- The pretrained 500-class baseline, its held-out test evaluation, and Grad-CAM remain incomplete; continual learning must wait for this required baseline.
- `src.evaluation.evaluate_class_scores` is used by scratch evaluation. Traditional and pretrained routes must emit the same metric fields and comparable final artifacts before the final result table is assembled.
- The lightweight CI checks syntax and manifests only. A separate dependency-installed synthetic deep-learning/evaluation smoke job remains a follow-up, not a full training job.

### Instructor-Supported Continual Learning Direction

Based on course discussion in July 2026, a small class-incremental continual-learning experiment is a reasonable advanced direction. It is not implemented yet and does not replace the required baseline methods.

- Select a fixed 100-class subset from the shared 500 classes and record the selected class IDs.
- Split it into 10 sequential tasks with 10 classes per task.
- Use ResNet18 and compare sequential training without replay against a small class-balanced replay memory of 2-5 images per previously seen class.
- After each task, report current-task accuracy, old-class accuracy, seen-class accuracy, and average forgetting.
- Where compute permits, compare scratch and ImageNet-pretrained ResNet18; joint training on the same 100 classes is an optional upper bound.

ImageNet-retention evaluation, complex replay selection, and 500-class continual learning are outside this initial scope. The continual-learning work should start only after the required baselines have stable, comparable results.

### 当前进度

- 已具备共享的 500 类数据清单、Dataset/DataLoader 入口、manifest 检查和轻量 CI。
- 传统 HOG 与颜色直方图特征、Linear SVM 和 Random Forest 分类 baseline 已具备。最终报告必须只用验证集说明 SVM 选择；当前 notebook 的说明不应再以 test 集比较来支撑超参数取舍。
- Scratch CNN 已具备随机初始化 ResNet18、按 epoch 的 trainer、loss 和 Top-1 history、训练耗时记录、曲线绘图、best/last checkpoint 与 resume guard，以及最终 test 评估。已完成的 augmentation run 在第 19 个 epoch 达到 validation Top-1 0.2458，并取得 held-out test Top-1 0.2440。Colab Tesla T4 cell 显示约 46 分钟 wall-clock time；这是手动观察到的历史记录，后续运行会自动保存每个 epoch 和总训练耗时。
- Pretrained CNN 已具备 ResNet18 训练和消融 Notebook，并完成小规模端到端流程验证；完整 500 类结果和最终评估仍未完成。

### 已知缺口与报告约束

- pretrained 500 类 baseline、其 held-out test 评估和 Grad-CAM 尚未完成；在此之前不应启动持续学习主体实验。
- `src.evaluation.evaluate_class_scores` 目前由 scratch 评估使用。传统和 pretrained 路线在最终结果表汇总前，必须输出相同指标字段和可比较的最终产物。
- 轻量 CI 只检查语法和 manifest。一项安装依赖的合成 deep-learning/evaluation smoke job 仍是后续工作，但不应在 CI 中加入完整训练。

### 教师认可的持续学习方向

根据 2026 年 7 月的课程沟通，小规模 class-incremental continual learning 是合理的 advanced direction。该方向尚未实现，也不替代必做 baseline。

- 从共享的 500 类中固定选取 100 类，并记录选中的 class ID。
- 划分为 10 个顺序任务，每个任务包含 10 类。
- 使用 ResNet18，对比无 replay 的顺序训练与 class-balanced replay；每个已见类别保留 2-5 张图片。
- 每完成一个任务后，报告当前任务准确率、旧类准确率、已见类准确率和平均遗忘量。
- 算力允许时，对比 scratch 与 ImageNet-pretrained ResNet18；同一 100 类上的 joint training 仅作为可选 upper bound。

ImageNet 保留能力评估、复杂 replay 选择策略和 500 类持续学习不属于初始范围。持续学习工作应在必做 baseline 得到稳定且可比较的结果后再开始。

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
