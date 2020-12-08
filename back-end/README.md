# 部署说明

## 1 环境配置

- MySQL >= 5.7
- Python >= 3.7

## 2 安装依赖

执行

```shell
pip install -r requirements.txt
```

## 3 修改数据库配置

修改 `config.yml` 中的相关字段


## 4 新建数据库

登录 mysql，新建 `config.yml` 中 `db.mysql.database` 所指的数据库，例如

```
create database science2;
```

## 5 导入数据

将 `data/science.sql` 导入至刚刚新建的数据库中，导入成功后数据库会有4张表 `news`，`topic`，`strategy`，`status`。

## 6 启动服务

执行

```
uvicorn main:app --host 0.0.0.0
```
启动服务

如果GPU可用，执行
```
CUDA_VISIBLE_DEVICES=0 uvicorn main:app --host 0.0.0.0
```

启动服务

# GPU相关要求

- 支持cuda9.0的nvidia显卡
- nvidia显卡驱动
- cuda=9.0

如果使用原生的python，cuda9.0可参照 `https://developer.nvidia.com/cuda-90-download-archive` 方式安装

如果是基于conda环境的python，可以用

```
conda install pytorch==1.1.0 cudatoolkit=9.0
```
安装（注意此时不需要通过pip安装 `requirements.txt` 中的 `torch==1.1.0`）