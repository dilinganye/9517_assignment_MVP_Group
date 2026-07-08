import os
from pathlib import Path

# ——————————————————————————————————————————————————
'''
Entire group should use this part(or add stuff at this part):

all paths, random seeds, and hyperparameters 

are defined here, 
so others can directly import and use them.
'''
# ——————————————————————————————————————————————————

# ================= PATH [Only need to change this to change all] ==============
# PROJECT_ROOT 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 原始数据根目录：
DATA_ROOT = PROJECT_ROOT / "data"
    # DATA_RAW_ROOT 原始数据目录（官方提供的原始数据，Git不提交）
DATA_RAW_ROOT = PROJECT_ROOT / "data" / "raw"

        # 训练集TAR
TRAIN_IMG_DIR_TAR = DATA_RAW_ROOT / "train_mini.tar.gz"
TRAIN_ANNOTATION_TAR = DATA_RAW_ROOT / "train_mini.json.tar.gz"
        # 如果你解压了的话，默认没解压
TRAIN_IMG_DIR = DATA_RAW_ROOT / "train_mini"
TRAIN_ANNOTATION_FILE = DATA_RAW_ROOT / "train_mini.json"

        # 测试集TAR（官方val集，项目中作为测试集）
VAL_TAR_PATH = DATA_RAW_ROOT / "val.tar.gz"
VAL_JSON_TAR_PATH = DATA_RAW_ROOT / "val.json.tar.gz"
        # 如果你解压了的话，默认没解压
TEST_IMG_DIR = DATA_RAW_ROOT / "val"
TEST_ANNOTATION_FILE = DATA_RAW_ROOT / "val.json"

    # DATA_PROCESSED_ROOT 处理后的数据目录（划分好的标签文件等，Git提交）
DATA_PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"
DATA_SPLITS_DIR = DATA_PROCESSED_ROOT  # 数据集划分文件
CLASS_LIST_CSV = DATA_SPLITS_DIR / "class_list_500.csv"
TRAIN_CSV = DATA_SPLITS_DIR / "train.csv"
VAL_CSV = DATA_SPLITS_DIR / "val.csv"
TEST_CSV = DATA_SPLITS_DIR / "test.csv"

# OUTPUT_ROOT 输出目录（本地生成，Git忽略）
OUTPUT_ROOT = PROJECT_ROOT / "outputs"

# ...... add more output subdirs here if needed




# ============= 数据集全局参数（所有人必须共用，禁止私自修改） =====
RANDOM_SEED = 56  # Just a global seed 全局随机种子，所有随机操作必须用这个
NUM_CLASSES = 500  # Number of experiment categories 实验类别数
IMG_SIZE = (224, 224)  # global image input size统一输入图像尺寸

# 每类样本数划分
NUM_TRAIN_PER_CLASS = 40  # training set    每类训练集数量（从train_mini的50张里分）
NUM_VAL_PER_CLASS = 10    # validation set  每类验证集数量（从train_mini的50张里分）
NUM_TEST_PER_CLASS = 10   # test set        每类测试集数量（官方val集，固定10张/类）

# 图像归一化参数（ImageNet预训练默认值，迁移学习直接用；从零训练也复用这套保证一致）
# ///////////////////////////
# # 谁负责这个谁自己调整
# ///////////////////////////
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]
# ///////////////////////////

# ====================== 原始数据集文件名（按官方解压后的结构） ======================
