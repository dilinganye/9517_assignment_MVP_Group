# 基础设施 PR 汇总

本文档概括从原始仓库状态到当前基础设施整理后的主要变化。它用于人工交接和复盘，不要求每个 PR 自动更新；只有在需要记录重要阶段、交付说明或维护决策时再手动补充。

## 维护约定

- 每个 PR 仍应尽量保持小而聚焦。
- `log.md` 不再要求每个 PR 自动更新。
- 当某次 PR 涉及重要流程、公共约定、交付说明或需要留痕的决策时，再手动更新 `log.md` 或本文档。
- 开 PR 前仍建议运行轻量检查：`python scripts/smoke_test.py`。

## 手动记录格式

当需要在 `log.md` 或本文档中记录重要 PR 时，建议使用以下格式：

```md
## PR #<编号> - <标题>

- 作者：xuanzhougu
- 分支：`<branch-name>`
- PR 创建时间：YYYY-MM-DD HH:MM:SS AEST
- PR 合并时间：YYYY-MM-DD HH:MM:SS AEST
- 摘要：...
- 验证：...
```

## 基础设施 PR 时间线

| PR | 标题 | 作者 | 分支 | 创建时间 (AEST) | 合并时间 (AEST) |
| ---: | --- | --- | --- | --- | --- |
| #1 | Add project infrastructure skeleton: Fix requirements.txt and Add README.md as placeholder | xuanzhougu | `xuanzhou-infra-supplement` | 2026-07-08 22:57:31 | 2026-07-08 22:57:48 |
| #2 | Stabilize data path convention | xuanzhougu | `xuanzhou-data-path-log` | 2026-07-08 23:05:36 | 2026-07-08 23:09:11 |
| #3 | Add unified dataset loader | xuanzhougu | `xuanzhou-dataset-loader` | 2026-07-08 23:15:32 | 2026-07-08 23:17:22 |
| #4 | Add lightweight smoke test | xuanzhougu | `xuanzhou-smoke-test` | 2026-07-08 23:21:13 | 2026-07-08 23:23:56 |
| #5 | Add manifest summary script | xuanzhougu | `xuanzhou-data-processing-script` | 2026-07-08 23:28:44 | 2026-07-08 23:31:45 |
| #6 | Add minimal CI | xuanzhougu | `xuanzhou-minimal-ci` | 2026-07-08 23:36:35 | 2026-07-08 23:37:31 |
| #7 | Polish README files | xuanzhougu | `xuanzhou-readme-polish` | 2026-07-08 23:45:37 | 2026-07-09 00:51:42 |

## 原始仓库状态

原始仓库已经完成了最关键的数据准备工作：

- 选定 500 个 iNaturalist-2021 类别。
- 提交了 `class_list_500.csv`、`train.csv`、`val.csv`、`test.csv`。
- 数据划分符合 40/10/10：
  - train: 20,000 张图片，每类 40 张。
  - val: 5,000 张图片，每类 10 张。
  - test: 5,000 张图片，每类 10 张。

当时的主要欠缺是：

- README 仍是草稿风格，缺少可执行入口。
- 缺少依赖清单和明确目录说明。
- 数据路径常量和实际 CSV 位置不完全一致。
- 没有统一 Dataset/DataLoader。
- 没有 smoke test。
- notebook 的数据处理结果缺少脚本化证据层。
- 没有 CI。

## 已完成的基础设施改动

### 1. 项目结构和依赖骨架

新增并整理了基础项目结构：

- 增加 `requirements.txt`。
- 为 `data/`、`outputs/`、`src/data/`、`src/traditional/`、`src/deep_learning/`、`src/advanced/`、`src/utils/` 增加说明文件。
- 更新 `.gitignore`，保留 `outputs/README.md`，但默认忽略实验输出。

### 2. 稳定数据路径约定

更新 `src/config.py`，让共享路径和实际提交的 CSV 对齐：

- `DATA_SPLITS_DIR`
- `CLASS_LIST_CSV`
- `TRAIN_CSV`
- `VAL_CSV`
- `TEST_CSV`

这样后续 Dataset、训练脚本和评估脚本都可以引用统一配置，减少硬编码路径。

### 3. 统一 Dataset/DataLoader

新增 `src/data/dataset.py`，提供最小统一数据入口：

- `InatCsvDataset`
- `get_manifest_path(split)`
- `create_dataset(split)`
- `create_dataloader(...)`

这一步让传统方法和深度学习方法都能基于同一套 manifest 读取逻辑继续开发。

### 4. 轻量 smoke test

新增 `scripts/smoke_test.py`，用于快速检查项目基础是否被破坏：

- CSV 路径是否存在。
- 必要字段是否齐全。
- train/val/test 行数是否符合预期。
- label 是否覆盖 `0..499`。
- 每类样本数是否正确。
- train/val/test 是否存在路径重叠。

这个测试不依赖图片、不训练模型、不需要 PyTorch。

### 5. notebook 数据处理结果的脚本证据

新增 `scripts/summarize_data_manifests.py`，用于汇总已经提交的数据清单：

- 类别数量。
- split 行数。
- 每类样本范围。
- kingdom 分布。
- split overlap 数量。
- source notebook 路径。

它不重新处理大型原始压缩包，只对已提交的 CSV 产物生成可复查摘要。

### 6. 最小 CI

新增 `.github/workflows/ci.yml`，让 GitHub Actions 在 PR 和 push 到 `main` 时运行轻量检查：

- `py_compile`
- `python scripts/smoke_test.py`
- `python scripts/summarize_data_manifests.py --output /tmp/manifest_summary.json`

CI 不安装训练依赖、不下载图片、不跑模型训练、不做完整评估。

### 7. README 文档整理

整理根 README 和 `data/processed/README.md`：

- 去掉草稿说明和过时占位内容。
- 补充项目目标、数据规模、快速命令、数据布局、项目结构、协作规则、CI 范围。
- 补充中文说明，方便组内阅读。
- 将原 README 中有价值的中文提示正式化保留：大型 JSON 应使用流式处理，`ijson` 用于流式解析，`tqdm` 用于进度显示。
- 将原 README 中的 `.gitignore` 意图整理为正式说明：原始数据、实验输出、模型权重、压缩包和视频默认不提交。
- 将原 `data/processed/README.md` 中有价值的中文文件用途说明补回：类别清单、label mapping、train/val/test 清单的作用。
- 修复 `data/processed/README.md` 的 Markdown 格式。
- 明确 `label_mapping.json` 目前不是独立提交文件。

## 当前项目基础设施状态

当前仓库已经具备以下基础能力：

- 有固定且经过检查的 500 类数据 manifest。
- 有统一数据路径配置。
- 有最小 Dataset/DataLoader 入口。
- 有轻量 smoke test。
- 有数据 manifest 摘要脚本。
- 有最小 GitHub Actions CI。
- 有中英文根 README 和数据说明。

接下来可以在这个基础上继续做：

- 传统特征 baseline。
- Scratch CNN 训练入口。
- Pretrained CNN 训练入口。
- 统一评估脚本。
- 训练曲线、metrics、predictions 输出规范。
