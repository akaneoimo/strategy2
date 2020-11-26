# -*- coding: utf-8 -*-

import json

from demo_str import Demo


def main():
    # 载入数据
    print("loading data...")
    data_list = []
    file_path = "data/data_test.json"
    file = open(file_path, "r", encoding="utf-8")
    for line in file:
        line = line.strip()
        data = json.loads(line)
        data_item = {"title": data["title"], "content":data["content"]}
        data_list.append(data_item)
    file.close()

    # 建立Demo类
    print("initializing demo...")
    config_filename = "HAN_0.json"
    demo = Demo(config_filename)

    # 预测
    print("predict...")
    """
    data_list  : 输入数据列表, 每项为一个字典{"title": 新闻标题(str), "content": 新闻内容(str)}
    result_list: 预测结果列表, 每项为一个字典{"strategy_ids": [策略ID(str)]}, result与data一一对应
    """
    result_list = demo.predict(data_list)

    # 打印预测结果
    while True:
        print("----------------------------------------")
        index = input("index (1~{}): ".format(len(data_list)))
        index = int(index) - 1

        if (index >= 0) and (index < len(data_list)):
            print("【新闻标题】")
            print(data_list[index]["title"])

            print("【新闻内容】")
            print(data_list[index]["content"])

            print("【应对策略】")
            for strategy_id in result_list[index]["strategy_ids"]:
                print(strategy_id)
        else:
            print("退出")
            break


if __name__ == "__main__":
    main()
