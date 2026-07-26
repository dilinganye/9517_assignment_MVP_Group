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

- 完成传统特征和分类 baseline。
- 完成 Scratch CNN 的完整训练、checkpoint 和训练曲线。
- 使用已新增的 Pretrained ResNet18 Notebook 运行完整训练和消融实验。
- 增加统一评估入口。
- 生成真实的训练曲线、metrics、predictions 和混淆矩阵。
- 完成 Grad-CAM 可解释性分析。

## 后续执行建议（按任务计划书分工）

以下内容用于将下一阶段的实现范围写清楚。课程正式 Specification 优先；本节仅记录组内协作约定，避免把不同方法或不同成员的职责混在一起。

### 统一实验契约

- 所有方法复用同一套 500 类 `train`、`val`、`test` manifest 和 label mapping。
- 只使用 `train` 和 `val` 调参；`test` 只用于固定方案的最终评估，不能根据 test 结果反复修改模型。
- 统一报告 Top-1、Top-5、Macro Precision、Macro Recall、Macro F1、混淆矩阵和运行时间。
- 每次完整实验记录随机种子、配置、Git commit、最佳 epoch、运行环境和运行时间；主要产物统一为 `metrics.json`、`history.csv`、`predictions.csv` 和必要图表。

### 五人职责与边界

| 成员 | 主要职责 | 主要产物 | 边界 |
| --- | --- | --- | --- |
| A：公共平台 | 数据划分、统一评估、集成、CI、manifest | `data/`、评估接口、CI | 公共接口由 A 统一维护 |
| B：传统特征 | HOG、颜色直方图、特征缓存 | `traditional/features` | 不修改 Dataset 或 metrics 接口 |
| C：传统分类 | Linear SVM、调参、传统方法分析 | `traditional/classifier`、传统结果表 | 复用 B 的固定特征接口 |
| D：Scratch CNN | 随机初始化 ResNet18、trainer、checkpoint | `deep/scratch`、训练曲线 | 公共 trainer 接口变更单独开 PR |
| E：Pretrained + CAM | ImageNet 预训练微调、冻结/解冻和增强消融、Grad-CAM | `deep/transfer`、`explainability` | 通过固定评估接口接入 |

其中 D 的 `Scratch CNN` 使用随机初始化，即旧接口的 `pretrained=False` 或新版 torchvision 的 `weights=None`；这不是迁移学习。E 负责加载 ImageNet 预训练权重后的微调与 Grad-CAM，不应与 D 的 scratch 训练范围混淆。

### 推荐集成顺序

1. A 先确认统一评估输入/输出格式，B/C/D/E 在不改公共接口的前提下分别提交最小可运行 baseline。
2. D 完成可恢复的 scratch 训练与训练曲线；E 完成预训练微调，并以已固定的模型 checkpoint 进行 Grad-CAM 和控制变量实验。
3. 全部方法使用同一 test 集生成统一结果表，再选择正确、错误和高混淆类别样本进行分析。
4. 主方案稳定后再考虑 28+ 的测试时图像退化鲁棒性扩展，避免扩展工作影响基本训练收敛、统一评估和报告质量。

## 项目进度更新：CNN 持续学习 Advanced Direction

### 当前进度

- 共享 500 类 manifest、Dataset/DataLoader、轻量 smoke test 和 CI 已完成。
- B/C 的 HOG、颜色直方图、特征缓存、Linear SVM 和 Random Forest baseline 已提交。最终报告需要只用验证集解释 SVM 的超参数选择；当前 notebook 不应再以 test 集比较支撑该选择。
- D 的 scratch 路线已完成随机初始化 ResNet18、训练/验证 epoch、loss 与 Top-1 history、曲线绘图、best/last checkpoint 与 resume guard、最终 test 评估和结果后处理。`augmentation_v1` 在 Colab Tesla T4、batch size 64、two workers、20 epochs 下，cell 显示约 46 分钟 wall-clock time；这是手动观察的历史记录。最佳 validation Top-1 为 0.2458（epoch 19），固定 checkpoint 的 held-out test Top-1 为 0.2440、Top-5 为 0.4912。后续训练会自动记录逐 epoch 和累计训练时间。
- E 的预训练 ResNet18 训练与消融 Notebook 已提交，并完成小规模端到端流程验证；完整 500 类训练结果、test 集最终评估和 Grad-CAM 仍待完成。

### 阶段性复查后的待办与约束

- E 必须完成 pretrained 500 类训练、验证集选择、held-out test 统一评估和 Grad-CAM。CL 的任务计划可与这些工作并行准备，但完整 CL 训练不得延误必做 baseline。
- `src.evaluation.evaluate_class_scores` 目前只由 scratch 最终评估直接使用。传统和 pretrained 路线需要在最终结果汇总前对齐 Top-1、Top-5、overall accuracy、macro precision、macro recall、macro F1 及可审计的输出文件。
- scratch 的 `analyze_scratch_evaluation.py` 只读取已保存的 `predictions.csv` 和 test manifest，不重新运行模型；它输出每类指标、最高频混淆物种对和最低 recall 类别的可读混淆图，供报告使用。
- 当前 CI 仅覆盖语法和 manifest。后续可新增安装依赖的合成 deep-learning/evaluation smoke job，但不应在 CI 中下载数据或运行完整训练。

### 课程沟通结论

根据 2026 年 7 月与课程教师的沟通，以下小规模 CNN class-incremental continual-learning 设计被认为合理，可作为 advanced direction。它不替代必做 baseline；当前已固定任务计划、数据适配器和指标契约，训练与 replay 尚未实现。

- 从共享的固定 500 类中选定并记录 100 个 class ID。
- 将 100 类划分为 10 个顺序任务，每个任务 10 类。
- 以 ResNet18 为 backbone，对比 no-replay 顺序训练与 class-balanced replay；replay memory 初始范围为每个已见类 2-5 张图片。
- 每个任务后在所有已见类别上评估，报告 current-task accuracy、old-class accuracy、seen-class accuracy 和 average forgetting。
- 算力允许时比较 scratch ResNet18 与 ImageNet-pretrained ResNet18；同一 100 类的 joint training 可以作为可选 upper bound。

### 初始范围边界和执行顺序

- 首先完成并固定传统、scratch CNN 与 pretrained CNN 的可比 baseline；CL 任务计划可并行准备，但训练不能影响主任务交付。
- 初始实验只做 100 类、10 个任务和 no-replay / class-balanced replay 两组核心比较；不同 replay 策略可在主结果稳定后再扩展。
- 不将 ImageNet 数据保留能力评估、复杂 memory selection、Bayesian/adapter 方法或 500 类持续学习纳入初始实现。
- 每次 CL 实验应保存固定 class/task 划分、随机种子、模型来源（scratch 或 pretrained）、memory 预算、每任务指标和遗忘曲线，以便报告复现。

## Scratch CNN 起始 PR 记录

## PR #44 - Add scratch Grad-CAM evidence

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-gradcam`
- PR 创建时间：2026-07-26 21:46:42 AEST
- PR 合并时间：2026-07-26 21:50:12 AEST
- 摘要：为已冻结的 scratch augmentation checkpoint 新增一套小型 Grad-CAM 证据生成流程。它复用已保存的 held-out prediction 与高频混淆对，校验 checkpoint 可复现每个选中样本的预测，并在 Git 之外输出正确、错误和混淆物种对图以及可审计 CSV。
- 验证：完整 CI 等价的 manifest、持续学习和 result-analysis smoke suite，零深度学习依赖的 Grad-CAM 选样 smoke test、Python 语法编译、干净 Notebook JSON 和 `git diff --check` 均通过。未提交原始图片、checkpoint、预测文件或生成图。

## PR #43 - Add continual result analysis

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-result-analysis`
- PR 创建时间：2026-07-25 23:54:21 AEST
- PR 合并时间：2026-07-25 23:56:28 AEST
- 摘要：新增离线 held-out CL artifact 汇总脚本，输出最终指标表、old/seen/forgetting 曲线，以及 no-replay 和 inverse-frequency replay 各自的 task-accuracy matrix 图。
- 验证：manifest、continual-dataset、continual-metrics、no-replay、replay 和 result-analysis smoke test，本地合成 PNG/CSV 生成，干净 Notebook JSON，以及 `git diff --check` 均通过。未提交原始图片、GPU 训练、checkpoint、预测文件或生成结果。

## PR #42 - Add held-out continual evaluation

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-heldout-evaluation`
- PR 创建时间：2026-07-25 23:01:28 AEST
- PR 合并时间：2026-07-25 23:03:33 AEST
- 摘要：为 no-replay 和 replay trainer 新增显式的 task-boundary evaluation split；默认仍使用 validation，配置冻结后可在独立输出目录写入 held-out test accuracy matrix。
- 验证：manifest、continual-dataset、continual-metrics、no-replay 和 replay smoke test，两个 CLI help，合成 test-split artifact 检查，干净 Notebook JSON，以及 `git diff --check` 均通过。未提交原始图片、GPU 训练、checkpoint、预测文件或生成结果。

## PR #41 - Add inverse-frequency replay sampling

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-balanced-sampling`
- PR 创建时间：2026-07-25 22:26:35 AEST
- PR 合并时间：2026-07-25 22:29:01 AEST
- 摘要：为 current-task 与 replay memory 合并后的训练集新增 opt-in 的 inverse-frequency 抽样；保留随机打乱的 M=2/M=5 baseline，并在 D Colab Notebook 中增加独立的、只使用 validation 的 M=5 follow-up 执行与对比单元。
- 验证：replay、manifest、continual-dataset、continual-metrics 和 no-replay smoke test，weighted sampler/DataLoader 集成检查，replay 入口 help，干净 Notebook JSON，以及 `git diff --check` 均通过。未提交原始图片、GPU 训练、checkpoint、预测文件或生成结果。

## PR #40 - Add replay cells to D Colab notebook

- 作者：xuanzhougu
- 分支：`xuanzhou-d-colab-replay`
- PR 创建时间：2026-07-25 20:55:12 AEST
- PR 合并时间：2026-07-25 21:30:08 AEST
- 摘要：在 D Colab Notebook 中新增固定 M=2、M=5 class-balanced replay 的执行、task 边界 resume 和 validation-only 对比单元。
- 验证：Notebook JSON 结构、35 个无保存输出的单元、与已合并 replay trainer 的命令路径核对，以及 `git diff --check` 均通过。未提交数据、模型权重、预测文件或结果图。

## PR #39 - Add continual replay trainer

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-replay`
- PR 创建时间：2026-07-25 20:32:22 AEST
- PR 合并时间：2026-07-25 20:35:50 AEST
- 摘要：新增确定性的 class-balanced replay memory 和 CUDA scratch replay trainer；训练每个 task 时混合当前 task 与每个旧类的 M 张记忆样本，保存 validation 指标、memory manifest 与 task 边界恢复状态。
- 验证：Python compile-all、共享 manifest smoke test、持续学习任务计划、数据适配器、指标、no-replay 和 replay-memory smoke test、replay 入口 help、当前 task 加旧类 memory 的数据集检查，以及 CPU replay checkpoint 往返均通过。未运行原始图片、GPU 训练、replay 结果或 test 评估。

## PR #38 - Add D Colab execution notebook

- 作者：xuanzhougu
- 分支：`xuanzhou-d-colab-execution`
- PR 创建时间：2026-07-25 20:19:04 AEST
- PR 合并时间：2026-07-25 20:21:25 AEST
- 摘要：新增干净的 D 部分 Colab 执行 Notebook，记录 scratch smoke、baseline、augmentation、held-out test、离线错误分析和 CL no-replay 的完整执行流程；原始数据和 Drive 生成产物不进入 Git。
- 验证：Notebook JSON 结构、29 个无保存输出的单元、对现有 D 脚本命令路径的核对，以及 `git diff --check` 均通过。未提交数据、模型权重、预测文件或结果图。

## PR #35 - Add continual no-replay trainer

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-no-replay`
- PR 创建时间：2026-07-24 22:21:10 AEST
- PR 合并时间：2026-07-24 22:29:34 AEST
- 摘要：新增固定 100 类、10 个顺序 task 的 CUDA-only sequential no-replay trainer；每完成一个 task 后仅在 validation 的所有已见 task 上评估，保存 accuracy matrix、本地训练记录和 task 边界恢复 checkpoint。
- 验证：Python compile-all、共享 manifest smoke test、持续学习任务计划、数据适配器、指标和 resume guard smoke test、训练入口 help、合成 100-way 输出头，以及 CPU task-boundary checkpoint 往返均通过。未运行原始图片、GPU 训练、replay 或 test 评估。

## PR #34 - Add continual learning metrics

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-metrics`
- PR 创建时间：2026-07-24 21:40:00 AEST
- PR 合并时间：2026-07-24 22:13:05 AEST
- 摘要：新增无第三方依赖的 class-incremental accuracy matrix 指标契约；每完成一个 task 后统一产出 current-task、old-task、seen-task accuracy 和 average forgetting。
- 验证：Python compile-all、确定性的合成指标 smoke test、共享 manifest smoke test、持续学习任务计划检查和持续学习数据适配器 smoke test 均通过。未运行原始图片、GPU、trainer、replay、模型权重或 test 评估。

## PR #33 - Add continual task dataset adapter

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-task-dataset`
- PR 创建时间：2026-07-24 20:55:31 AEST
- PR 合并时间：2026-07-24 21:02:01 AEST
- 摘要：新增共享的持续学习数据适配器：按当前 task 或已见 tasks 过滤已提交 manifest，并将 source label 映射到固定 0-99 continual label。
- 验证：`git diff --check`、Python compile-all、共享 manifest smoke test、持续学习任务计划检查、无依赖的当前/已见任务过滤 smoke test，以及本地 torch Dataset 对单 task 和已见 tasks 的标签重映射初始化检查均通过。未运行原始图片、GPU、trainer、replay、模型权重或 test 评估。

## PR #30 - Add continual learning task plan

- 作者：xuanzhougu
- 分支：`xuanzhou-cl-task-setup`
- PR 创建时间：2026-07-23 22:40:43 AEST
- PR 合并时间：2026-07-23 22:48:02 AEST
- 摘要：启动 D 负责的 scratch 持续学习方向：提交确定性的 100 类、10 任务映射，新增任务计划生成/校验命令和最小 CI 覆盖，并在中英文 README 记录 class-incremental、no-replay 与 class-balanced replay 的后续实验契约。
- 验证：`git diff --check`、Python compile-all、manifest smoke test、manifest summary 生成、默认 seed 与替代 seed 的确定性任务计划检查，以及每个任务过滤后得到 400 train、100 validation、100 test 样本的检查均通过。未运行 GPU 训练、replay、模型权重或 test 评估。

## PR #29 - Add scratch timing and evaluation analysis

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-analysis-timing`
- PR 创建时间：2026-07-23 21:27:16 AEST
- PR 合并时间：2026-07-23 21:32:37 AEST
- 摘要：新增对已保存 scratch test 预测的离线结果分析；为后续 scratch 训练记录逐 epoch 和累计耗时；记录已完成 Colab 训练的观察耗时；同步项目状态和报告约束。
- 验证：`git diff --check`、Python compile-all、manifest smoke test、CPU 合成 trainer 计时检查、合成 500 类 prediction-analysis 产物检查，以及两个入口的 `--help` 检查均通过。未运行原始图片、模型权重或 test 推理。

## PR #10 - Add scratch ResNet18 factory

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-resnet18`
- PR 创建时间：2026-07-17 23:46:17 AEST
- PR 合并时间：2026-07-17 23:49:26 AEST
- 摘要：新增 D 负责的随机初始化 ResNet18 工厂，使用共享的 500 类配置和 `weights=None`；本 PR 不包含 trainer、checkpoint、预训练模型或 Grad-CAM。
- 验证：`git diff --check`、Python 语法编译和 `python scripts/smoke_test.py` 通过。由于本机环境未安装 PyTorch，未在本地实例化模型。

## PR #15 - Add scratch trainer

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-trainer`
- PR 创建时间：2026-07-18 22:18:55 AEST
- PR 合并时间：2026-07-18 22:21:32 AEST
- 摘要：新增 D 负责的最小 scratch trainer：训练与验证 epoch、默认交叉熵、device 管理、loss 与 Top-1 指标、逐 epoch history，以及训练曲线绘图。
- 验证：`git diff --check`、Python 语法编译、使用 500 类合成标签进行两轮 CPU 训练/验证及曲线生成，以及 `python scripts/smoke_test.py` 均通过。

## PR #16 - Add scratch checkpoint support

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-checkpoint`
- PR 创建时间：2026-07-18 22:52:57 AEST
- PR 合并时间：2026-07-18 22:58:16 AEST
- 摘要：新增基于最佳验证集 Top-1 的 checkpoint 保存，以及恢复模型、optimizer、history 和下一轮 epoch 的 helper。
- 验证：`git diff --check`、Python 语法编译、合成 CPU checkpoint 保存与恢复（含模型和 SGD momentum state）并继续训练一轮，以及 `python scripts/smoke_test.py` 均通过。

## PR #20 - Add CUDA scratch training entry point

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-training-entry`
- PR 创建时间：2026-07-21 22:49:02 AEST
- PR 合并时间：2026-07-21 23:20:53 AEST
- 摘要：新增仅使用 CUDA 的 scratch ResNet18 训练入口，串接共享 manifest、数据加载、随机初始化模型、trainer、最佳 checkpoint 恢复和本地实验产物。
- 验证：`git diff --check`、Python 语法编译、直接运行 `--help`、history CSV 与 transform helper smoke test、CUDA 不可用保护检查，以及 `python scripts/smoke_test.py` 均通过。完整训练需要 NVIDIA CUDA 和本地原始图片，当前环境不具备。

## PR #25 - Add scratch training augmentation

- 作者：xuanzhougu
- 分支：`xuanzhou-scratch-train-augmentation`
- PR 创建时间：2026-07-22 22:54:42 AEST
- PR 合并时间：2026-07-22 22:58:07 AEST
- 摘要：新增 opt-in 的训练集增强开关，用于与已完成的无增强 scratch ResNet18 baseline 进行受控比较；验证集保持固定 Resize，不使用随机增强。
- 验证：`git diff --check`、Python 语法编译、直接运行 `--help`、固定及增强 transform 与 history CSV helper 检查、CUDA 不可用保护检查，以及 `python scripts/smoke_test.py` 均通过。完整 CUDA 训练留在 Colab 执行。

## PR #26 - Add unified final evaluation

- 作者：xuanzhougu
- 分支：`xuanzhou-unified-final-evaluation`
- PR 创建时间：2026-07-23 00:02:25 AEST
- PR 合并时间：2026-07-23 00:06:35 AEST
- 摘要：新增共享分类指标，以及 CUDA scratch ResNet18 的 test 集入口；输出统一的本地评估产物格式。
- 验证：`git diff --check`、与 CI 等价的 Python 语法编译、合成 500 类共享指标检查、prediction CSV 与混淆矩阵图产物检查、checkpoint 兼容性、缺少 checkpoint 与 CUDA 不可用保护检查，以及 `python scripts/smoke_test.py` 均通过。完整 CUDA test 集评估留在 Colab 执行。

## PR #28 - Add safe scratch resume checkpoints

- 作者：xuanzhougu
- 分支：`xuanzhou-last-checkpoint-resume-guard`
- PR 创建时间：2026-07-23 20:45:46 AEST
- PR 合并时间：2026-07-23 20:48:12 AEST
- 摘要：分别保存 scratch 的最佳和最新 checkpoint，并拒绝训练关键配置不一致的 resume。
- 验证：`git diff --check`、与 CI 等价的 Python 语法编译、直接运行训练入口 `--help`、合成 CPU best/last checkpoint 往返、resume 配置不匹配拒绝、旧 checkpoint 可评估但被拒绝 resume，以及 `python scripts/smoke_test.py` 均通过。完整 CUDA 训练留在 Colab 执行。



## Pretrained CNN 起始 PR 记录

## PR #<13> - Add pretrained ResNet18 training and ablation notebook

- 作者：Guohao Lin
- 分支：`<guohao_lin-pretrained+CAM>`
- PR 创建时间：2026-7-18 20:56 AEST
- PR 合并时间：待合并后补充
- 摘要：新增 E 负责的 `E01_Pretrained_Training_and_Ablations.ipynb`，使用 ImageNet 预训练 ResNet18 和共享的 500 类数据配置。Notebook 包含图像预处理、数据增强、500 类分类头替换、冻结与解冻控制、分阶段微调、训练与验证循环、checkpoint、断点续训、训练历史保存，以及 main、no augmentation 和 head only 三组实验入口。Colab 默认直接从 Google Drive 按需读取图片，不要求复制完整训练集到 `/content`。
- 范围：本 PR 只提供预训练模型训练和消融实验入口，不包含完整训练结果、test set 最终评估、混淆矩阵、Grad-CAM 或报告中的最终实验结论。
- 验证：Notebook 文件格式和 Python code cell 语法检查通过；运行 `python scripts/smoke_test.py` 检查共享数据 manifest。完整模型训练和真实性能结果将在后续实验中生成。



## PR #18 - Add pretrained ResNet18 training and ablation notebook

- 作者：Guohao Lin
- 分支：`guohaolin_E01.1`
- PR 创建时间：2026-07-21 15:49:01 AEST
- PR 合并时间：2026-07-21 15:49:34 AEST
- 摘要：新增 E 负责的 `E01_Pretrained_Training_and_Ablations.ipynb`，使用 ImageNet 预训练 ResNet18 和共享的 500 类数据配置。Notebook 包含数据路径检查、图像预处理、数据增强、500 类分类层替换、冻结与分阶段解冻、训练与验证循环、Top-1、Top-5 和 Macro-F1 指标计算、checkpoint 保存、断点续训、训练历史保存，以及 `main`、`no_augmentation` 和 `head_only` 三组实验入口。
- 范围：本 PR 只提供预训练 ResNet18 的训练和消融实验流程，不包含完整 500 类训练结果、test set 最终评估、混淆矩阵、predictions.csv、Grad-CAM、鲁棒性实验或报告中的最终实验结论。
- 验证：Notebook 文件格式和 Python code cell 语法检查通过；运行 `python scripts/smoke_test.py` 检查共享数据 manifest；使用 64 张训练图片和 32 张验证图片完成 1 epoch 小规模训练测试，确认数据读取、模型前向传播、反向传播、验证、checkpoint、`history.csv` 和训练曲线生成流程正常。完整训练和真实性能结果将在后续 Colab GPU 实验中生成。
