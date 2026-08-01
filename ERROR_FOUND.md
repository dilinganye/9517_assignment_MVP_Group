# 项目代码合规检查结果

检查依据：

- `COMP9517_26T2_Group_Project_Specification-v1.pdf`
- `COMP9517_26T2_Group_Project_Marking_Criteria-1_0.pdf`

检查范围为当前仓库内的 Python 源码、Jupyter notebooks、CSV 清单、README、依赖文件与 CI 配置。本文件只记录能够由当前仓库内容直接证明的不符合项；报告、视频以及未提交到仓库的外部实验产物不在本次检查范围内。

## 1. 明确使用测试集结果参与了 SVM 超参数选择（严重）

**对应要求：** Specification 第 5 页要求只使用训练/验证数据进行超参数调优，测试集只能用于最终性能评估；不得让测试数据参与训练或 fine-tuning。

**证据：** `src/traditional/classifier/traditional_classifier.ipynb` 第 21 个 cell。

该 cell 的注释明确写出：验证集 macro-F1 的最优值原本对应 `C=10.0` 或 `C=100.0`，但这些配置在测试集上的表现不如 nearest-centroid baseline，随后人工将 `best_c` 改成 `1.0`：

```python
# selected C=10.0, which ... actually
# scored worse than the trivial nearest-centroid baseline on the test set.
# Manually selecting C=1.0 instead
best_c = 1.0
```

这不是单纯的最终测试，而是查看测试表现后重新选择模型配置，属于测试集泄漏。即使 `C=1.0` 与验证集最优值很接近，也不能用测试集结果作为更改配置的理由。

## 2. 源代码提交中包含大量嵌入式结果图片（明确不符合提交要求）

**对应要求：** Specification 第 8 页要求代码 ZIP 不包含 trained models、input images 或 result images，并规定代码上传上限为 40 MB。

多个 notebook 保留了已执行输出和以 base64 形式嵌入的结果图片。嵌入 notebook 的图片仍然是源代码包中的 result images，并不会因为没有单独的 `.png` 文件而不计入。静态统计发现约 24 MB 的嵌入图片，其中主要包括：

| Notebook | 嵌入图片数 | 估算图片数据大小 |
| --- | ---: | ---: |
| `src/deep_learning/Task_E03_GradCAM_analysis.ipynb` | 20 | 14.58 MB |
| `src/traditional/features/sift.ipynb` | 8 | 3.56 MB |
| `src/traditional/classifier/traditional_classifier.ipynb` | 4 | 2.11 MB |
| `src/traditional/classifier/sift_bovw_classifier.ipynb` | 4 | 2.08 MB |
| 其他 notebooks 合计 | 21 | 约 1.98 MB |

当前仓库全部文件的未压缩总大小约为 38.66 MB，已经非常接近 40 MB 上限；最终 ZIP 的实际大小仍取决于压缩效果，但“不要包含 result images”这一条已经被违反。

## 3. README 没有清楚说明所有外部库/代码来源（明确文档缺口）

**对应要求：** Specification 第 8 页要求：从其他来源获得的 libraries 或 code 必须在 README 中清楚描述，并且所有使用过的 papers、tools 和 repositories 都应引用（第 3 页）。

当前根目录 `README.md`：

- 有论文参考文献，也有 `requirements.txt` 的安装命令；
- 但没有逐项说明哪些实现来自或依赖哪些外部库/代码；
- 没有明确说明 `torchvision.models.resnet18`、`ResNet18_Weights.DEFAULT`、OpenCV SIFT、scikit-image HOG、scikit-learn classifiers/metrics、Grad-CAM 实现等外部组件的来源、用途或改写关系；
- `requirements.txt` 只列包名，不能替代 README 中的来源说明。

因此无法从 README 清楚区分“本组自行实现的代码”和“基于第三方库/实现的部分”。

## 4. 运行文档不完整且存在失效信息（不符合 proper documentation 要求）

**对应要求：** Specification 第 8 页要求提供 proper documentation about how to run the code；Marking Criteria 要求代码 well structured and documented。

发现的问题：

- 根目录 `README.md` 的 Reproducibility 章节只给出了 smoke checks 和清单检查命令，没有给出从数据准备到传统方法、scratch CNN、pretrained CNN、评估和 Grad-CAM 的完整执行顺序及具体命令。
- `README.md` 的 Repository Layout 声称根目录存在 `log.md`，但仓库中没有该文件。
- 根目录存在一个只有注释的 `config.py`，实际配置位于 `src/config.py`。文档没有解释根目录文件的作用，容易导致使用者导入错误配置模块。
- `src/deep_learning/README.md` 只具体说明了 scratch 路线，未说明 pretrained 路线各 notebook 的必需执行顺序和开关；相关信息分散在 notebook cells 中。
- 传统路线依赖未提交的 `.npz` 特征缓存；虽然子目录 README 提供了外部链接，但根目录端到端流程没有明确说明何时下载缓存、何时重新生成，以及各 notebook 的先后关系。

这些问题使新环境中的使用者无法只依靠主 README 稳定复现实验。

## 5. 部分文档文本已损坏，影响可读性（不符合 clean / easy to read）
**已修复data/processed处，请大伙检查各自的.md文件中是否存在中文，如果有请删除。**

**对应要求：** Specification 第 8 页要求 proper documentation、inline comments 和 well structured code；Marking Criteria 要求代码 clean、concise、well-organized、easy to read。

`data/processed/README.md` 中的大段中文已经发生明显乱码，例如开头出现：

```text
鏈洰褰曚繚瀛樺凡鎻愪氦鐨?CSV...
```

同一文件后续的中文文件说明、数据划分说明和脚本说明也大面积乱码。该文件承担数据清单、标签映射、划分用途和运行方式的说明职责，因此乱码属于实质性的文档可读性问题。

## 6. 存在明显的占位、冗余和自称有问题的工具代码（影响代码结构与质量评分）

**对应要求：** Marking Criteria 要求代码 clean、concise、well-organized、easy to read，并避免 unnecessary redundancy；Specification 第 8 页要求 well structured 和 inline comments。

具体证据：

- 根目录 `config.py` 只有一行占位注释，与真正的 `src/config.py` 重名，属于无功能且有误导性的冗余文件。
- `src/utils/filesUtil.py` 导入了未使用的 `pickle`；`src/config.py` 导入了未使用的 `os`。
- `src/utils/filesUtil.py` 的 `read_zip` 文档注释直接写明“好像实现有问题...我也懒得改了”，却仍将该函数保留在公共工具模块中。一个已知可能有问题、没有测试、且项目不使用的函数不符合 clean/concise 的要求。
- 多条深度学习路线分别在 notebook 和 `.py` 模块中重复实现模型创建、训练、验证、checkpoint 和指标逻辑；例如 pretrained notebook 自行重复实现一套训练/checkpoint 代码，而仓库同时已有 `src/deep_learning/trainer.py`、`checkpoint.py` 和 `src/evaluation.py`。这种重复增加了行为不一致和维护错误的风险。

## 7. 若将 continual learning 作为高级方向提交，当前结果没有证明 replay 减少 forgetting（高级方向不达标风险）

**对应要求：** Specification 第 4-5 页的 continual learning 方向要求先验证 catastrophic forgetting，再应用 replay，并展示 replay 在多大程度上减少 forgetting，同时讨论 memory size 与 forgetting 的权衡。

根目录 `README.md` 把 continual learning 声明为已完成的 advanced study，但其结果表为：

- no replay average forgetting：`0.2600`
- replay（5 images per old class）average forgetting：`0.3322`

按仓库自己报告的标准 average forgetting，replay 后 forgetting 反而更高，未展示该方法“减少 forgetting”。README 也没有解释这一矛盾，却仍将其描述为完成的 replay study。如果该方向用于申请 26 分以上的高级方法分档，这是明显的不达标风险。此项不影响基础项目的两种完整方法要求，因为高级方向本身是高分档选择性内容。

## 已核实但未发现违规的项目

为避免误报，以下项目已检查并确认当前代码/清单具备相应证据：

- 三份清单为 500 类，每类分别为 40 train、10 validation、10 held-out test；总计使用 train_mini 的每类 50 张图片，并使用官方 validation 的每类 10 张图片作为 test。
- 清单 smoke test 通过，训练、验证、测试路径无重叠。
- 存在传统 handcrafted-feature/classical-classifier 路线，以及 random-initialisation ResNet18 和 ImageNet-pretrained ResNet18 路线。
- 公共评估函数包含 Top-1、Top-5、overall accuracy、macro precision、macro recall、macro F1 和完整 confusion matrix。
- Python 文件和可静态解析的 notebook code cells 均通过语法检查。
- continual task plan、continual metrics、replay memory、resume guard 和 Grad-CAM sample selection 的仓库 smoke checks 均通过。

上述通过项不抵消前面列出的测试集泄漏、提交内容、来源说明和代码文档问题。

## 补充检查：`scripts/` 目录

### 8. `scripts/` 不是稳定的 Python package，模块运行方式会破坏 replay 入口

`scripts/` 没有 `__init__.py`，同时混用了三种导入方式：

```python
from src... import ...
from scripts.summarize_continual_results import ...
from train_continual_no_replay import ...
```

其中 `scripts/train_continual_replay.py` 第 31 行使用：

```python
from train_continual_no_replay import ...
```

该写法依赖“直接执行 `python scripts/train_continual_replay.py` 时，Python 把 `scripts/` 放入搜索路径”这一偶然行为。若使用标准模块方式 `python -m scripts.train_continual_replay`，或者把目录移动至 `src/commands/`，这个 import 将无法解析。其他两个 smoke scripts 却使用 `from scripts...`，说明目录的 package 设计并不一致。

### 9. 14 个脚本依靠重复的 `sys.path` 修改，移动目录会整体失效

14 个文件重复包含：

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
```

这不仅是重复代码，也把“脚本恰好位于项目根目录下一层”写死。若直接把目录移到 `src/commands/`，`parents[1]` 会变成 `src/` 而不是项目根目录，配置导入、Git commit 获取、相对路径输出和图像路径回退都会受到影响。规范要求代码 well structured；当前结构对物理目录层级存在不必要的强耦合。

### 10. replay 训练入口直接复用另一个 CLI 脚本的内部实现，分层不合理

`scripts/train_continual_replay.py` 从 `scripts/train_continual_no_replay.py` 导入以下内部函数/常量：

- `DEVICE`
- `capture_rng_state`
- `create_transform`
- `get_git_commit`
- `restore_rng_state`
- `set_seed`
- `task_plan_sha256`
- `write_csv`

命令行入口应当调用共享库，而不应把另一个命令行入口当作公共模块。上述公共逻辑应位于 `src/advanced/` 或 `src/deep_learning/`。当前结构使 replay 和 no-replay 的文件移动、重命名或单独测试高度耦合，也与仓库声称的模块化结构不一致。

### 11. CI 只做语法编译，没有验证主要 CLI 能否成功导入和显示帮助

`.github/workflows/ci.yml` 对主要训练/评估文件只运行 `py_compile`。`py_compile` 不执行 import，因此无法发现：

- package/import 路径错误；
- `torch`、`torchvision`、`matplotlib` 等运行依赖不兼容；
- CLI 在解析参数前就因 import 失败；
- 移动或重命名后 notebook 命令仍指向旧路径。

当前 smoke tests 主要覆盖数据清单和 dependency-light 函数，没有覆盖 `train_scratch_resnet18.py`、`evaluate_scratch_resnet18.py`、`train_continual_no_replay.py`、`train_continual_replay.py`、`generate_scratch_gradcam.py` 的真实入口导入。因此 CI 绿色不能证明提交的主要软件入口可运行。

### 12. 依赖没有锁定版本，无法保证提交环境可复现

`requirements.txt` 中所有依赖均未指定版本，例如：

```text
torch
torchvision
opencv-python
scikit-learn
```

项目使用了对版本较敏感的接口，例如 torchvision weights API、`torch.amp.GradScaler`、SIFT、scikit-learn classifier 参数和 notebook 输出格式，但 README 也没有规定 Python、PyTorch、Torchvision、CUDA 或 scikit-learn 的已验证版本组合。重新安装时会自动获取当时的最新版，不能保证与组员执行实验时的环境一致。这与项目强调的 reproducibility 目标不一致，也会增加代码无法运行或数值变化的风险。

### 13. 目录问题

目前我发现大伙有人没太用明白gitignore，如果你有使用AI，请让AI将一些临时文件和说明文件丢在docs/或者notebooks/文件夹，这样不会上传。