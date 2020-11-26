# -*- coding: utf-8 -*-

import jieba
import logging
import re

from textrank4zh import TextRank4Keyword, TextRank4Sentence


class Demo(object):
    def __init__(self):
        self.num_sentences     = 2
        self.num_key_words     = 100
        self.num_key_sentences = 5

        jieba.setLogLevel(logging.INFO)

    def predict(self, data_list):
        """
        data_list    : [{"title": str, "content": str}]
        key_words    : [(str, float)]
        key_sentences: [(str, float)]
        """
        print("processing data...")
        text_list = []
        for data in data_list:
            text = data["content"]
            segs = re.split("。|？|！", text)
            while "" in segs:
                segs.remove("")
            if len(segs) > self.num_sentences:
                segs = segs[0:self.num_sentences]
            text_list += segs
        all_text = "。".join(text_list)

        print("extracting key words...")
        tr4w = TextRank4Keyword()
        tr4w.analyze(text=all_text, lower=True, window=2)
        key_words = [(item.word, item.weight) for item in tr4w.get_keywords(num=self.num_key_words, word_min_len=2)]
        
        print("extracting key sentences...")
        tr4s = TextRank4Sentence()
        tr4s.analyze(text=all_text, lower=True, source="all_filters")
        key_sentences = [(item.sentence + "。", item.weight) for item in tr4s.get_key_sentences(num=self.num_key_sentences, sentence_min_len=10)]

        return key_words, key_sentences
