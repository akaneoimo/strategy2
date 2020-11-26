# -*- coding: utf-8 -*-

import argparse
import copy
import json
import os
import random

from .langconv import Converter


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_path", type=str)
    args = parser.parse_args()
    return args


def main(paper_path, output_dir):
    print("extracting data...")
    extract_data(paper_path, output_dir)

    print("dividing data...")
    divide_data(output_dir)


def extract_data(paper_path, output_dir):
    assert os.path.exists(paper_path), "file not found: {}".format(paper_path)
    with open(paper_path, "r", encoding="utf-8") as file:
        data_list = json.load(file)

    converter = Converter("zh-hans")

    data_list_pro = []
    for data in data_list:
        news_id      = data["id"]
        topic_id     = data["topic_id"]
        strategy_ids = data["strategy_id"]
        title        = data["title"]
        content      = data["content"]

        if (strategy_ids == "0") or (title == "") or (content == "") or (len(content) < 20) or (strategy_ids == ""):
            continue

        news_id  = str(news_id)
        topic_id = str(topic_id)

        # strategy_ids = strategy_ids.split(",")
        strategy_ids = json.loads(strategy_ids)
        strategy_ids = [int(strategy_id) for strategy_id in strategy_ids]
        strategy_ids = sorted(strategy_ids)
        strategy_ids = [str(strategy_id) for strategy_id in strategy_ids]

        title = title.replace("\r", "")
        title = title.replace("\n", "")
        title = converter.convert(title)

        content = content.replace("\r", "")
        content = content.replace("\n", "")
        content = converter.convert(content)

        data_pro = {}
        data_pro["news_id"]      = news_id
        data_pro["topic_id"]     = topic_id
        data_pro["strategy_ids"] = strategy_ids
        data_pro["title"]        = title
        data_pro["content"]      = content
        data_list_pro.append(data_pro)

    data_list_pro = sorted(data_list_pro, key=lambda item: (item["topic_id"], item["news_id"]), reverse=False)

    file_path = os.path.join(output_dir, "data_all.json")
    file = open(file_path, "w", encoding="utf-8")
    for data in data_list_pro:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
    file.close()


def divide_data(output_dir):
    MAX_TRAIN = 10000
    MAX_VALID = 10

    strategy2data = {}
    file_path = os.path.join(output_dir, "data_all.json")
    file = open(file_path, "r", encoding="utf-8")
    for line in file:
        line = line.strip()
        data = json.loads(line)
        strategy = "_".join(data["strategy_ids"])
        if strategy not in strategy2data:
            strategy2data[strategy] = []
        strategy2data[strategy].append(data)
    file.close()

    data_list_train = []
    data_list_valid = []
    for strategy in strategy2data:
        data_list = strategy2data[strategy]
        random.seed(0)
        random.shuffle(data_list)
        new_data_list = copy.deepcopy(data_list)
        num_samples = len(new_data_list)
        num_valid = min(int(num_samples * 0.1), MAX_VALID)
        num_train = min(num_samples - num_valid, MAX_TRAIN)
        data_list_valid += new_data_list[0:num_valid]
        data_list_train += new_data_list[num_valid:num_valid+num_train]

    data_list_train = sorted(data_list_train, key=lambda item: (item["topic_id"], item["news_id"]), reverse=False)
    data_list_valid = sorted(data_list_valid, key=lambda item: (item["topic_id"], item["news_id"]), reverse=False)

    file_path = os.path.join(output_dir, "data_train.json")
    file = open(file_path, "w", encoding="utf-8")
    for data in data_list_train:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
    file.close()

    file_path = os.path.join(output_dir, "data_valid.json")
    file = open(file_path, "w", encoding="utf-8")
    for data in data_list_valid:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
    file.close()

    file_path = os.path.join(output_dir, "data_test.json")
    file = open(file_path, "w", encoding="utf-8")
    for data in data_list_valid:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
    file.close()


if __name__ == "__main__":
    args = parse_args()
    main(args.paper_path)
