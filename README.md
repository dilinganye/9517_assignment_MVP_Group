# 说明 -提交时此段会删除- #
data - 项目整体包含许多大块，包括但不限于
- 数据：“数据源[大概会外置，太大了这东西]”，“索引表[CSV]”，“处理中介[可能的某些数据导出]”
- 方法：“基础实现[各种传统视觉方法]”，“深度实现[各种分析和深度学习]”，“进阶实现[加分项的部分]”
- 模型：“模型培养[需要大量用到各种专门的分支]”



## 小组提示表 ##
- 无论如何，记得安装 ijson，这处理数据需求太大了，尤其是我这数据清洗，不流式真会把我电脑干碎
 pip install ijson
- 如果想要流程可视化，使用tqdm
 pip install tqdm

## Smoke test ##
Run the lightweight project check before opening a PR:

```bash
python scripts/smoke_test.py
```

The same lightweight checks also run in GitHub Actions for pull requests and pushes to `main`.

To summarize the committed data manifests that came from the data notebooks:

```bash
python scripts/summarize_data_manifests.py
```


## 项目结构 ##
comp9517-26t2-group-project/    # 仓库根目录
├── README.md                   # 项目说明 [你正在看这个]
├── .git....                    # github的各种文件和文件夹，忽略
├── requirements.txt            # 全项目依赖
│
├── data/                       # 外层数据目录（原始数据+处理好的数据）
│
├── src/                        # 核心源代码（模块化，全员协作开发）
│   │
│   ├── config.py               # 全局参数：随机种子、每类样本数等，所有人都得引用这里的数据从而保证项目统一
│   │
│   ├── data/                   # 数据模块
│   │
│   ├── traditional/            # 传统计算机视觉方法
│   │
│   ├── deep_learning/          # 深度学习方法
│   │
│   ├── advanced/               # 进阶研究方向（每个方向也要独立子目录）
│   │
│   ├── utils/                  # 通用工具，一些比较方便的方法或者库什么的
│
├── notebooks/                  # 实验 Notebook（仅做调用与可视化，不会上传到github）
│   ├── abababab
│
├── docs/                       # 个人留痕（不会上传到github）
│
├── outputs/                    # 输出目录（一些算法什么的可以把结果扔在这儿，扔在自己的开发目录也可以）
│
└── submission/                 # 最终打包（Git 完全忽略）

## gitignore ##
/data/raw/ [因为过大]
/notebooks/ [具体项目的notebooks会在src内部，外置在此处的都为调参和测试用品，不会进入项目文件的github]
/submission/ [此项目只由固定人员上传，以防误触覆盖]
/docs/ [开发过程，建议每人都准备一下，从而留痕方便最终答辩]
/outputs/* [本地实验输出默认不提交，保留 outputs/README.md 说明目录用途]
*.tar.gz [Github限制]
*.zip
*.npz
*.pth
*.pt
*.pkl
*.joblib
*.mp4
*.mov
... [若有需求，请自行添加]
