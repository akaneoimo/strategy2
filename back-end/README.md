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