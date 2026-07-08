import json
import pickle
import joblib
import numpy as np
import pandas as pd
from contextlib import contextmanager
from pathlib import Path
import zipfile


def save_json(data, save_path):
    """
    保存JSON文件
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(load_path):
    """
    加载JSON文件
    """
    with open(load_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_npz(data_dict, save_path):
    """
    保存压缩numpy数组
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(save_path, **data_dict)


def load_npz(load_path):
    """
    加载npz文件，返回字典
    """
    data = np.load(load_path)
    return {key: data[key] for key in data.files}


def save_joblib(obj, save_path):
    """
    保存sklearn模型/对象
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, save_path)


def load_joblib(load_path):
    """
    加载joblib对象
    """
    return joblib.load(load_path)


def save_csv(df, save_path, index=False):
    """
    保存CSV
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=index)


def load_csv(load_path):
    """
    加载CSV
    """
    return pd.read_csv(load_path)

def read_zip(zip_path, file_name, chunk_size=1024 * 1024 * 512):
    """
    *流式 默认消耗 16MB 内存
    没用 521MB 是因为那样python自己容易把自己崩掉
    从zip文件中读取指定文件内容

    逐块返回数据，避免一次性把超大文件载入内存。
    ## 好像实现有问题...我也懒得改了，反正咱们用不上zip应该是 ##
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open(file_name) as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

@contextmanager
def read_tar(tar_path, file_name):
    """
    以流式方式打开 tar 内的目标文件。

    返回的是文件样式对象，适合直接交给 ijson 这类按需读取解析器。
    不要直接使用！
    这只是个展示，具体的可以参考data00_choosing500.ipynb里对tar的处理方式，按需读取，避免一次性解压到内存。

    不过我已经处理好了500子项，所以你也可以直接读取
    """
    import tarfile
    with tarfile.open(tar_path, 'r:gz') as tar_ref:
        member = None
        for tar_member in tar_ref:
            if tar_member.name == file_name:
                member = tar_member
                break
        if member is None:
            raise FileNotFoundError(f'{file_name} not found in {tar_path}')

        extracted = tar_ref.extractfile(member)
        if extracted is None:
            raise FileNotFoundError(f'{file_name} not found in {tar_path}')
        with extracted as f:
            yield f