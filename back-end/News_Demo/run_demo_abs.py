# -*- coding: utf-8 -*-

import json

from demo_abs import Demo


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
    demo = Demo()

    # 预测
    print("predict...")
    """
    data_list   : 输入数据列表, 每项为一个字典{"title": 新闻标题(str), "content": 新闻内容(str)}
    result_list : 聚类结果列表, 每项为一个字典{"label": 聚类类别(int)}, result与data一一对应
    cluster_list: 类别信息列表, 每项为一个字典{"title": 类别标题(str), "key_words": 关键字及权重列表[(str, float)], "key_sentences": 关键句及权重列表[(str, float)]}
    """
    result_list, cluster_list = demo.predict(data_list)

    num_clusters = len(cluster_list)

    # 打印预测结果
    while True:
        print("----------------------------------------")
        index = input("cluster index (1~{}): ".format(num_clusters))
        index = int(index) - 1

        if (index >= 0) and (index < num_clusters):
            print("【标题】")
            print(cluster_list[index]["title"])

            print("【关键词】")
            for word, weight in cluster_list[index]["key_words"][0:10]:
                print("{:.6f} {}".format(weight, word))

            print("【关键句】")
            for sentence, weight in cluster_list[index]["key_sentences"]:
                print("{:.6f} {}".format(weight, sentence))

            title_list = []
            for result, data in zip(result_list, data_list):
                if result["label"] == index:
                    title_list.append(data["title"])

            print("【新闻标题】")
            for title in title_list:
                print(title)
        else:
            print("退出")
            break


if __name__ == "__main__":
    main()
