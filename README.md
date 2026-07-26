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

Generate a compact Grad-CAM evidence set from this frozen scratch test result.
It reuses the existing prediction and confused-pair artifacts, runs only on the
selected images, and writes figures plus an auditable summary outside Git:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/generate_scratch_gradcam.py \
  --checkpoint /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/augmentation_v1/best_checkpoint.pt \
  --image-root /content/inat_data_fresh \
  --predictions /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/predictions.csv \
  --confused-pairs /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/most_confused_pairs.csv \
  --output-dir /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/gradcam_results
```

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

基于已冻结的 scratch test 结果生成一组小型 Grad-CAM 证据。它只复用既有的预测和混淆对产物，
仅对选中的图片前向计算，并将图和可审计汇总写在 Git 之外：

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/generate_scratch_gradcam.py \
  --checkpoint /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/augmentation_v1/best_checkpoint.pt \
  --image-root /content/inat_data_fresh \
  --predictions /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/predictions.csv \
  --confused-pairs /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/most_confused_pairs.csv \
  --output-dir /content/drive/MyDrive/COMP9517/outputs/scratch_resnet18/final_evaluation/gradcam_results
```

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
|   |-- advanced/            # Advanced directions such as CL, Grad-CAM, or robustness
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
- The pretrained-CNN path completed its 500-class ResNet18 training, ablations, and held-out evaluation. The main model reached validation Top-1 0.6310 and test Top-1 0.6390; its Grad-CAM analysis covers correct predictions, incorrect predictions, and frequent confused species pairs.
- The 100-class continual-learning study completed fixed-configuration held-out no-replay and class-balanced replay comparisons, offline result figures, and an E04 extended comparison notebook. These advanced experiments remain separate from the required 500-class baselines.

### Delivery Notes and Report Guardrails

- The pretrained 500-class baseline, held-out test evaluation, and Grad-CAM are complete. Keep the resulting local artifacts available to the group for the report and video; they remain intentionally outside Git.
- `src.evaluation.evaluate_class_scores` defines the common scratch and continual-learning metric fields. Traditional and pretrained final artifacts record comparable Top-1, Top-5, macro precision, macro recall, and macro F1 values for report assembly.
- The lightweight CI checks syntax and manifests only. A separate dependency-installed synthetic deep-learning/evaluation smoke job remains a follow-up, not a full training job.

### Continual Learning: Next-Stage Plan

Based on course discussion in July 2026, the D-owned scratch class-incremental continual-learning direction fixes a deterministic 100-class subset and 10 tasks. It now includes the shared task dataset adapter, no-replay and class-balanced replay trainers, held-out evaluation, and offline report artifacts; it does not replace the required baseline methods.

- `data/processed/continual_100/class_tasks_100.csv` records the selected source labels, fixed 0-99 continual labels, task-local labels, and species metadata. `src.data.create_continual_dataset(split, task_ids)` filters the existing shared manifests using this compact map rather than duplicating image lists.
- Use a fixed 100-class scratch ResNet18 head and class-incremental evaluation over all seen classes, without providing a task ID at inference.
- Compare sequential fine-tuning without replay against class-balanced experience replay with 2 and 5 stored images per earlier class.
- After every task, save the task-by-task accuracy matrix, current-task accuracy, old-class accuracy, seen-class accuracy, and average forgetting. Tune settings only on validation data, then evaluate fixed configurations on test.
- The plan follows the task-sequence and forgetting analysis in De Lange et al. and the small episodic-memory replay baseline in Chaudhry et al. Grad-CAM remains an independent E-owned advanced direction.

Create or verify the committed plan without GPU or image files:

```bash
python scripts/create_continual_task_plan.py --check
```

Run the validation-only sequential baseline on CUDA; it saves a task-boundary checkpoint, `accuracy_matrix.json`, `task_metrics.csv`, and `training_history.csv` locally:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_no_replay.py \
  --image-root /path/to/inat_data \
  --output-dir outputs/continual_100/no_replay_v1
```

Use `--resume` with the same output directory only after a completed task. Run the two fixed replay budgets in separate directories while keeping all other settings equal to the no-replay baseline:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 2 \
  --output-dir outputs/continual_100/replay_m2_v1

CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --output-dir outputs/continual_100/replay_m5_v1
```

If a random-shuffle replay run leaves old classes under-sampled, run this separate validation-only M=5 follow-up. It preserves the memory budget but samples the combined dataset with equal class probability; it does not replace the M=2/M=5 memory-budget baselines:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --class-balanced-sampling \
  --output-dir outputs/continual_100/replay_m5_inverse_frequency_v1
```

After freezing the validation-selected no-replay and inverse-frequency M=5 configurations, rerun each once in a new directory with `--evaluation-split test`. Training remains on `train`, per-epoch monitoring remains on `val`, and the held-out test split is used only for task-boundary report metrics. Do not change a setting after reading these results.

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_no_replay.py \
  --image-root /path/to/inat_data \
  --evaluation-split test \
  --output-dir outputs/continual_100/final_test/no_replay_v1

CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --class-balanced-sampling \
  --evaluation-split test \
  --output-dir outputs/continual_100/final_test/replay_m5_inverse_frequency_v1
```

Create report tables and figures from those saved test artifacts without rerunning either model:

```bash
python scripts/summarize_continual_results.py \
  --no-replay-dir outputs/continual_100/final_test/no_replay_v1 \
  --replay-dir outputs/continual_100/final_test/replay_m5_inverse_frequency_v1 \
  --output-dir outputs/continual_100/final_test/report_analysis
```

ImageNet-retention evaluation, complex replay selection, and 500-class continual learning are outside this initial scope. After validation comparisons, use the fixed-configuration held-out evaluation and offline report-artifact workflow above.

### 当前进度

- 已具备共享的 500 类数据清单、Dataset/DataLoader 入口、manifest 检查和轻量 CI。
- 传统 HOG 与颜色直方图特征、Linear SVM 和 Random Forest 分类 baseline 已具备。最终报告必须只用验证集说明 SVM 选择；当前 notebook 的说明不应再以 test 集比较来支撑超参数取舍。
- Scratch CNN 已具备随机初始化 ResNet18、按 epoch 的 trainer、loss 和 Top-1 history、训练耗时记录、曲线绘图、best/last checkpoint 与 resume guard，以及最终 test 评估。已完成的 augmentation run 在第 19 个 epoch 达到 validation Top-1 0.2458，并取得 held-out test Top-1 0.2440。Colab Tesla T4 cell 显示约 46 分钟 wall-clock time；这是手动观察到的历史记录，后续运行会自动保存每个 epoch 和总训练耗时。
- Pretrained CNN 已完成 500 类 ResNet18 训练、消融和 held-out 评估。主模型的 validation Top-1 为 0.6310、test Top-1 为 0.6390；Grad-CAM 已覆盖正确预测、错误预测和高频混淆物种对。
- 100 类持续学习研究已完成固定配置的 held-out no-replay 与 class-balanced replay 对比、离线结果图，以及 E04 扩展对比 Notebook。这些 advanced 实验仍与必做的 500 类 baseline 分开。

### 交付说明与报告约束

- pretrained 500 类 baseline、held-out test 评估和 Grad-CAM 已完成。请让小组持续保留对应的本地实验产物，供报告和视频使用；它们仍按约定不提交 Git。
- `src.evaluation.evaluate_class_scores` 规定 scratch 和持续学习共享的指标字段。传统和 pretrained 最终产物也记录了可用于报告汇总的 Top-1、Top-5、macro precision、macro recall 和 macro F1。
- 轻量 CI 只检查语法和 manifest。一项安装依赖的合成 deep-learning/evaluation smoke job 仍是后续工作，但不应在 CI 中加入完整训练。

### 持续学习：下一阶段计划

根据 2026 年 7 月的课程沟通，D 负责的 scratch class-incremental continual learning 固定使用可复现的 100 类子集和 10 个任务。当前已具备共享 task dataset adapter、no-replay 与 class-balanced replay trainer、held-out 评估和离线报告产物；它不替代必做 baseline。

- `data/processed/continual_100/class_tasks_100.csv` 记录被选中的 source label、固定的 0-99 continual label、任务内标签和物种元信息。`src.data.create_continual_dataset(split, task_ids)` 会用这份紧凑映射过滤既有共享 manifest，而不复制图片路径清单。
- 使用固定 100 类输出头的 scratch ResNet18，在推理时不提供 task ID，并对所有已见类别进行 class-incremental 评估。
- 对比无 replay 的顺序微调与 class-balanced experience replay；每个旧类保留 2 和 5 张图片作为两个 memory budget。
- 每完成一个 task 后保存 task-by-task accuracy matrix、current-task accuracy、old-class accuracy、seen-class accuracy 和 average forgetting。调参只用 validation，固定方案再进行 test 评估。
- 方案参考 De Lange 等人的 task sequence/forgetting 分析，以及 Chaudhry 等人的小型 episodic-memory replay baseline。Grad-CAM 是 E 独立负责的 advanced direction。

无需 GPU 或图片文件，即可创建或核对已提交计划：

```bash
python scripts/create_continual_task_plan.py --check
```

在 CUDA 上运行只使用 validation 的 sequential baseline；它会在每个 task 边界本地保存 checkpoint、`accuracy_matrix.json`、`task_metrics.csv` 和 `training_history.csv`：

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_no_replay.py \
  --image-root /path/to/inat_data \
  --output-dir outputs/continual_100/no_replay_v1
```

只可在完成某个 task 后，对同一输出目录使用 `--resume`。在保持其余设置与 no-replay baseline 一致的前提下，使用独立目录运行两个固定 replay budget：

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 2 \
  --output-dir outputs/continual_100/replay_m2_v1

CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --output-dir outputs/continual_100/replay_m5_v1
```

若随机打乱的 replay 仍让旧类在训练中被明显欠采样，可运行下面独立的、只用 validation 的 M=5 follow-up。它保持 memory budget 不变，但让合并数据集中的每个类别具有相同抽样概率；它不替代 M=2/M=5 的 memory-budget baseline：

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --class-balanced-sampling \
  --output-dir outputs/continual_100/replay_m5_inverse_frequency_v1
```

当 no-replay 与 inverse-frequency M=5 配置已经由 validation 固定后，分别在新的输出目录重跑一次，并传入 `--evaluation-split test`。训练仍只使用 `train`，逐 epoch 监控仍使用 `val`，held-out test 仅用于 task 边界的报告指标；读取结果后不得再改动设置。

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_no_replay.py \
  --image-root /path/to/inat_data \
  --evaluation-split test \
  --output-dir outputs/continual_100/final_test/no_replay_v1

CUDA_VISIBLE_DEVICES=0 python scripts/train_continual_replay.py \
  --image-root /path/to/inat_data \
  --memory-per-class 5 \
  --class-balanced-sampling \
  --evaluation-split test \
  --output-dir outputs/continual_100/final_test/replay_m5_inverse_frequency_v1
```

无需重新运行模型，即可从以上保存的 test artifacts 生成报告表格与图片：

```bash
python scripts/summarize_continual_results.py \
  --no-replay-dir outputs/continual_100/final_test/no_replay_v1 \
  --replay-dir outputs/continual_100/final_test/replay_m5_inverse_frequency_v1 \
  --output-dir outputs/continual_100/final_test/report_analysis
```

ImageNet 保留能力评估、复杂 replay 选择策略和 500 类持续学习不属于初始范围。完成 validation 对比后，按上述固定配置的 held-out test 与离线报告产物流程执行。

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
