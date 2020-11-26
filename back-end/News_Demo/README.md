# 依赖

## 设置镜像源

```shell
conda config --set show_channel_urls yes
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
```

## 安装依赖包

```shell
conda create -n news python=3.7
conda activate news
conda install --channel https://conda.anaconda.org/conda-forge jieba
conda install pytorch==1.1.0 torchvision==0.3.0 cudatoolkit=9.0
conda install scikit-learn
conda install networkx
```

# 调用

## 训练策略预测模型

**调用命令**

```shell
CUDA_VISIBLE_DEVICES=0 python train.py HAN_0.json
```

**数据依赖**

config/HAN_0.json: 配置文件
data/data_train.json: 训练数据集
data/data_valid.json: 验证数据集
src/Tencent_AILab_ChineseEmbedding.txt: 预训练词向量文件

## 测试策略预测模型

**调用命令**

```shell
CUDA_VISIBLE_DEVICES=0 python test.py HAN_0.json
```

**数据依赖**

config/HAN_0.json: 配置文件
data/data_test.json: 测试数据集

## 调用策略预测模块

**调用语句**

```python
from demo_str import Demo

# 建立Demo类
config_filename = "HAN_0.json"
demo = Demo(config_filename)

# 预测
result_list = demo.predict(data_list)
```

data_list: 输入数据列表, 每项为一个字典{"title": 新闻标题(str), "content": 新闻内容(str)}
result_list: 预测结果列表, 每项为一个字典{"strategy_ids": [策略ID(str)]}, result与data一一对应

**演示程序**

```shell
CUDA_VISIBLE_DEVICES=0 python run_demo_str.py
```

## 调用事件聚类模块

**调用语句**

```python
from demo_abs import Demo

# 建立Demo类
demo = Demo()

# 预测
result_list, cluster_list = demo.predict(data_list)
```

data_list: 输入数据列表, 每项为一个字典{"title": 新闻标题(str), "content": 新闻内容(str)}
result_list: 聚类结果列表, 每项为一个字典{"label": 聚类类别(int)}, result与data一一对应
cluster_list: 类别信息列表, 每项为一个字典{"title": 类别标题(str), "key_words": 关键字及权重列表[(str, float)], "key_sentences": 关键句及权重列表[(str, float)]}

**演示程序**

```shell
python run_demo_abs.py
```
