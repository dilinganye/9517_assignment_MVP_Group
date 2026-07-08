# tiny_inat_500.tar.gz #

tiny_inat_500.tar.gz. is around 2.5GB, can't store in Github, thus it been stored in a cloudDrive
However, for convenient with later confirmation, the CSV files are still displayed in this Folder.

It's been stored in: 
https://unsw-my.sharepoint.com/:u:/g/personal/z5708767_ad_unsw_edu_au/IQCd2kjjFMcQQZvZZBUCLM74AUqhSjweb5B1IQGVrewxcrQ?e=5OEx5p

## desc ##
~ 文件格式 ~
~ This file format is: ~

tiny_inat_500.tar.gz
    |L annotations
    |   |F class_list_500.csv
    |   |F label_mapping.json
    |   |F test.csv
    |   |F train.csv
    |   |F val.csv
    |L train_mini
    |   |L 00006_Animalia_Arthropoda_Arachnida_Araneae_Araneidae_Aculepeira_ceropegia
    |   |   |F 0acbaf31-89b2-4768-8bd3-bf279a7b2f60.jpg
    |   |   |F ...
    |   |L 00079_Animalia_Arthropoda_Arachnida_Araneae_Salticidae_Helpis_minitabunda
    |   |L ...
    |L val
    |   |L 00006_Animalia_Arthropoda_Arachnida_Araneae_Araneidae_Aculepeira_ceropegia
    |   |   |F 4f539364-22bd-4215-a264-dbdae49330a8.jpg
    |   |   |F ...
    |   |L 00079_Animalia_Arthropoda_Arachnida_Araneae_Salticidae_Helpis_minitabunda
    |   |L ...

________________________________________
        说         明
________________________________________
    |   |F class_list_500.csv
作用是列出最终抽中的 500 个类别。里面保存的是类别元信息，主要包括 category_id、category_name、common_name、kingdom、supercategory。它相当于这 500 类的总目录。

    |   |F label_mapping.json
作用是保存“原始类别 ID”和“训练标签编号”的对应关系。
在src/data/data00_choosing500.ipynb 里面的 category_to_label 表示原始 category_id -> label，label_to_category 则是反过来。
这个文件的意义是：模型训练时用的是连续编号 label，但后面也可以还原回原始物种 ID。

    |   |F test.csv
作用是测试集清单，里面每一行对应一张训练图片，通常包含 file_path、label、category_id，并补了 category_name。
它记录测试阶段要用的图片及其对应标签。
    |   |F train.csv
作用是训练集清单。字段一样。
它告诉你训练时每张图应该读哪一个类别。
    |   |F val.csv
作用是验证集清单，字段和另外那俩也是一样。
它用来做验证集评估，标签编号和训练集是同一套映射。

________________________________________
Explanation
________________________________________

| |F class_list_500.csv
This file lists the 500 categories selected in the final selection. It stores category metadata, mainly including category_id, category_name, common_name, kingdom, and supercategory. It's essentially a directory of these 500 categories.

| |F label_mapping.json
This file stores the mapping between "original category ID" and "training label number".

In src/data/data00_choosing500.ipynb, category_to_label represents the original category_id -> label, and label_to_category is the reverse.

The significance of this file is that while the model uses consecutively numbered labels during training, it can later be restored to the original species ID.

| |F test.csv
This file is a test set list. Each line corresponds to a training image and typically includes file_path, label, category_id, and supplemented with category_name.

It records the images used during the testing phase and their corresponding labels.

| |F train.csv This is a list of training set data. The fields are the same.

It tells you which category each image should be read during training.

| |F val.csv This is a list of validation set data. The fields are the same as the other two.

It's used for validation set evaluation; the label numbers and training set data share the same mapping.

## Script evidence

The notebook outputs can be summarized with:

```bash
python scripts/summarize_data_manifests.py
```

This script reports the selected class count, split sizes, per-label counts, kingdom distribution, and split overlap counts from the committed CSV manifests.
