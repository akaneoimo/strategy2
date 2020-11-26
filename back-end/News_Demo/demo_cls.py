# -*- coding: utf-8 -*-

import jieba
import logging
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AffinityPropagation


class Demo(object):
    def __init__(self):
        self.max_features = 3000
        self.preference   = -4

        jieba.setLogLevel(logging.INFO)

    def predict(self, data_list):
        """
        data_list   : [{"title": str, "content": str}]
        result_list : [{"label": int}]
        cluster_list: [{"title": str}]
        """
        print("processing data...")
        text_list = []
        for data in data_list:
            text = data["content"]
            text = text.lower()
            text = re.sub("[0-9]", "", text)
            text = re.sub("[a-z]", "", text)
            text = re.sub("[A-Z]", "", text)
            text_list.append(text)
        corpus = [" ".join(jieba.lcut(text)) for text in text_list]

        print("vectorizing...")
        vectorizer = TfidfVectorizer(max_features=self.max_features)
        sparse_result = vectorizer.fit_transform(corpus)
        features = sparse_result.todense()

        print("clustering...")
        clustering = AffinityPropagation(preference=self.preference)
        labels  = clustering.fit_predict(features)
        centers = clustering.cluster_centers_indices_

        num_samples = len(data_list)
        result_list = []
        for index in range(num_samples):
            result = {"label": labels[index]}
            result_list.append(result)

        num_clusters = len(centers)
        cluster_list = []
        for index in range(num_clusters):
            cluster = {"title": data_list[centers[index]]["title"]}
            cluster_list.append(cluster)

        return result_list, cluster_list
