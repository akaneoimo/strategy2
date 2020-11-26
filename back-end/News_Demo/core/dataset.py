# -*- coding: utf-8 -*-

import json
import logging
import pickle
import re

import jieba
import numpy as np

from torch.utils.data import Dataset as TorchDataset


class Dataset(TorchDataset):
    def __init__(self, config):
        super(Dataset, self).__init__()

        self.document_length = config["document_length"]
        self.sentence_length = config["sentence_length"]

        self.word2index = {}

        self.strategy2label = {}
        self.label2strategy = {}
        self.num_labels     = 0

        self.num_samples = 0
        self.data_list   = []

        self.sequences_ttl = None
        self.sequences_cnt = None
        self.labels        = None

        jieba.setLogLevel(logging.INFO)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, index):
        return self.sequences_ttl[index], self.sequences_cnt[index], self.labels[index]

    def set_word_to_index(self, word2index):
        self.word2index = word2index

    def build_label_mapping(self, label_list_file, label_mapping_file):
        strategy2num = {}
        for strategy_ids, title, content in self.data_list:
            for strategy in strategy_ids:
                if strategy in strategy2num:
                    strategy2num[strategy] += 1
                else:
                    strategy2num[strategy] = 1
        strategy_num_list = sorted(strategy2num.items(), key=lambda item: (item[1], item[0]), reverse=True)
        for index, (strategy, num) in enumerate(strategy_num_list):
            self.strategy2label[strategy] = index
            self.label2strategy[index] = strategy
        self.num_labels = len(strategy_num_list)

        file = open(label_list_file, "w", encoding="utf-8")
        for strategy, num in strategy_num_list:
            file.write("{}\n".format(strategy))
        file.close()

        label_mappings = (self.strategy2label, self.label2strategy, self.num_labels)
        with open(label_mapping_file, "wb") as file:
            pickle.dump(label_mappings, file)

    def load_label_mapping(self, label_mapping_file):
        with open(label_mapping_file, "rb") as file:
            label_mappings = pickle.load(file)
        self.strategy2label, self.label2strategy, self.num_labels = label_mappings

    def load_data_from_file(self, data_file):
        # initialize
        self.num_samples = 0
        self.data_list   = []
        # load
        file = open(data_file, "r", encoding="utf-8")
        for line in file:
            line = line.strip()
            data = json.loads(line)
            data_item = (data["strategy_ids"], data["title"], data["content"])
            self.data_list.append(data_item)
            self.num_samples += 1
        file.close()

    def process_data_from_file(self):
        sequences_ttl = []
        sequences_cnt = []
        labels        = []
        for strategy_ids, title, content in self.data_list:
            # sequence (title)
            tokenized_title = jieba.lcut(title)
            title_length = len(tokenized_title)
            if title_length < self.sentence_length:
                tokenized_title = tokenized_title + ["[PAD]"] * (self.sentence_length - title_length)
            else:
                tokenized_title = tokenized_title[0 : self.sentence_length]
            sequence_ttl = []
            for word in tokenized_title:
                if word not in self.word2index:
                    word = "[UNK]"
                sequence_ttl.append(self.word2index[word])
            sequences_ttl.append(sequence_ttl)
            # sequence (content)
            sentences = re.split("。|！|？|：|；", content)
            while "" in sentences:
                sentences.remove("")
            num_sentences = len(sentences)
            if num_sentences < self.document_length:
                sentences = sentences + [""] * (self.document_length - num_sentences)
            else:
                sentences = sentences[0 : self.document_length]
            document_ids = []
            for sentence in sentences:
                words = jieba.lcut(sentence)
                num_words = len(words)
                if num_words < self.sentence_length:
                    words = words + ["[PAD]"] * (self.sentence_length - num_words)
                else:
                    words = words[0 : self.sentence_length]
                sentence_ids = []
                for word in words:
                    if word not in self.word2index:
                        word = "[UNK]"
                    sentence_ids.append(self.word2index[word])
                document_ids.append(sentence_ids)
            sequences_cnt.append(document_ids)
            # label (strategy)
            label = [0] * self.num_labels
            for strategy in strategy_ids:
                label[self.strategy2label[strategy]] = 1
            labels.append(label)
        self.sequences_ttl = np.array(sequences_ttl, dtype=np.int)
        self.sequences_cnt = np.array(sequences_cnt, dtype=np.int)
        self.labels        = np.array(labels, dtype=np.float32)

    def load_data_from_list(self, data_list):
        # initialize
        self.num_samples = 0
        self.data_list   = []
        # load
        for data in data_list:
            data_item = ("NULL", data["title"], data["content"])
            self.data_list.append(data_item)
            self.num_samples += 1

    def process_data_from_list(self):
        sequences_ttl = []
        sequences_cnt = []
        labels        = []
        for strategy_ids, title, content in self.data_list:
            # sequence (title)
            tokenized_title = jieba.lcut(title)
            title_length = len(tokenized_title)
            if title_length < self.sentence_length:
                tokenized_title = tokenized_title + ["[PAD]"] * (self.sentence_length - title_length)
            else:
                tokenized_title = tokenized_title[0 : self.sentence_length]
            sequence_ttl = []
            for word in tokenized_title:
                if word not in self.word2index:
                    word = "[UNK]"
                sequence_ttl.append(self.word2index[word])
            sequences_ttl.append(sequence_ttl)
            # sequence (content)
            sentences = re.split("。|！|？|：|；", content)
            while "" in sentences:
                sentences.remove("")
            num_sentences = len(sentences)
            if num_sentences < self.document_length:
                sentences = sentences + [""] * (self.document_length - num_sentences)
            else:
                sentences = sentences[0 : self.document_length]
            document_ids = []
            for sentence in sentences:
                words = jieba.lcut(sentence)
                num_words = len(words)
                if num_words < self.sentence_length:
                    words = words + ["[PAD]"] * (self.sentence_length - num_words)
                else:
                    words = words[0 : self.sentence_length]
                sentence_ids = []
                for word in words:
                    if word not in self.word2index:
                        word = "[UNK]"
                    sentence_ids.append(self.word2index[word])
                document_ids.append(sentence_ids)
            sequences_cnt.append(document_ids)
            # label (strategy)
            label = [0] * self.num_labels
            labels.append(label)
        self.sequences_ttl = np.array(sequences_ttl, dtype=np.int)
        self.sequences_cnt = np.array(sequences_cnt, dtype=np.int)
        self.labels        = np.array(labels, dtype=np.float32)
