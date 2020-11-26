# -*- coding: utf-8 -*-

import jieba
import json
import logging
import pickle

import numpy as np


class Embedding(object):
    def __init__(self):
        self.vocab_size = 0
        self.word_dim   = 0
        self.word2index = {}
        self.index2word = {}
        self.matrix     = None
        self.min_word_number = 10

        jieba.setLogLevel(logging.INFO)

    def build_word_embedding(self, data_file, word_vector_file, vocab_list_file, word_embedding_file):
        # vocabulary
        word2num = {}
        print("reading {}...".format(data_file))
        file = open(data_file, "r", encoding="utf-8")
        for index, line in enumerate(file):
            if index % 1000 == 0:
                print("\r>> line: {}".format(index), end="", flush=True)
            line = line.strip()
            data = json.loads(line)
            text_0 = data["title"]
            words_0 = jieba.lcut(text_0)
            text_1 = data["content"]
            words_1 = jieba.lcut(text_1)
            words = words_0 + words_1
            for word in words:
                if word in word2num:
                    word2num[word] += 1
                else:
                    word2num[word] = 1
        file.close()
        print("")

        vocab_list = []
        vocab_set = set()
        word_num_list = sorted(word2num.items(), key=lambda item: (item[1], item[0]), reverse=True)
        for word, num in word_num_list:
            if num >= self.min_word_number:
                vocab_list.append(word)
                vocab_set.add(word)
        if "[PAD]" in vocab_set:
            vocab_set.remove("[PAD]")
            vocab_list.remove("[PAD]")
        if "[UNK]" in vocab_set:
            vocab_set.remove("[UNK]")
            vocab_list.remove("[UNK]")

        # word vector
        word2vec = {}
        print("reading {}...".format(word_vector_file))
        file = open(word_vector_file, "r", encoding="utf-8")
        line = file.readline().strip()
        segs = line.split(" ")
        vocab_size = int(segs[0])
        word_dim   = int(segs[1])
        print("vocab_size = {}".format(vocab_size))
        print("word_dim   = {}".format(word_dim))
        for index, line in enumerate(file):
            if index % 1000 == 0:
                print("\r>> line: {}".format(index), end="", flush=True)
            line = line.strip()
            segs = line.split(" ")
            if len(segs) == word_dim + 1:
                word   = segs[0]
                vector = segs[1:]
                if word in vocab_set:
                    word2vec[word] = vector
        file.close()
        print("")

        # word embedding
        vocab_size = len(word2vec) + 2
        word_dim   = word_dim
        word2index = {"[PAD]": 0, "[UNK]": 1}
        index2word = {0: "[PAD]", 1: "[UNK]"}
        matrix     = np.zeros([vocab_size, word_dim], dtype=np.float)

        index = 2
        new_vocab_list = []
        for word in vocab_list:
            if word in word2vec:
                word2index[word]  = index
                index2word[index] = word
                matrix[index]     = np.array(word2vec[word], dtype=np.float)
                index += 1
                new_vocab_list.append(word)
        matrix[1] = np.mean(matrix[2:], axis=0) # [UNK]

        word_embedding = {}
        word_embedding["vocab_size"] = vocab_size
        word_embedding["word_dim"]   = word_dim
        word_embedding["word2index"] = word2index
        word_embedding["index2word"] = index2word
        word_embedding["matrix"]     = matrix
        with open(word_embedding_file, "wb") as file:
            pickle.dump(word_embedding, file)

        file = open(vocab_list_file, "w", encoding="utf-8")
        file.write("[PAD]\n")
        file.write("[UNK]\n")
        for word in new_vocab_list:
            file.write("{}\n".format(word))
        file.close()

    def load_word_embedding(self, word_embedding_file):
        with open(word_embedding_file, "rb") as file:
            word_embedding = pickle.load(file)
        self.vocab_size = word_embedding["vocab_size"]
        self.word_dim   = word_embedding["word_dim"]
        self.word2index = word_embedding["word2index"]
        self.index2word = word_embedding["index2word"]
        self.matrix     = word_embedding["matrix"]
