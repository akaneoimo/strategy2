# -*- coding: utf-8 -*-

import numpy as np
from torch.utils.data import DataLoader

from core.config import Config
from core.dataset import Dataset
from core.embedding import Embedding
from core.factory import Factory
from core.model import Model


class Demo(object):
    def __init__(self, config_filename):
        # configuration
        config = Config()
        config_file = "{}/{}".format(config.config_dir, config_filename)
        config.update_config(config_file)

        # word embedding
        print("setting word embedding...")
        word_embedding = Embedding()

        word_embedding_file = "{}/word_embedding_{}.pkl".format(config.cache_dir, config.config_name)
        print("loading word embedding from {}...".format(word_embedding_file))
        word_embedding.load_word_embedding(word_embedding_file)

        # demo dataset
        print("setting demo dataset...")
        self.demo_dataset = Dataset(config.data_config)

        self.demo_dataset.set_word_to_index(word_embedding.word2index)

        label_mapping_file = "{}/label_mapping_{}.pkl".format(config.cache_dir, config.config_name)
        print("loading label mapping from {}...".format(label_mapping_file))
        self.demo_dataset.load_label_mapping(label_mapping_file)

        # model
        new_model_config = {
            "vocab_size": word_embedding.vocab_size,
            "word_dim"  : word_embedding.word_dim,
            "document_length": self.demo_dataset.document_length,
            "sentence_length": self.demo_dataset.sentence_length,
            "num_labels"     : self.demo_dataset.num_labels
            }
        config.update_model_config(new_model_config)

        model = Model(config.model_config)

        # model factory
        self.network = Factory(model)

        self.network.set_test_module()
        print("number of GPUs: {}".format(self.network.num_gpus))
        print("device: {}".format(self.network.device))

        # load model
        model_file = "{}/model_{}.pkl".format(config.cache_dir, config.config_name)
        print("loading model from {}...".format(model_file))
        self.network.load_model(model_file)

        self.network.model_to_device()
        self.network.eval_mode()

    def predict(self, data_list):
        """
        data_list  : [{"title": str, "content": str}]
        result_list: [{"strategy_ids": [str]}]
        """
        self.demo_dataset.load_data_from_list(data_list)
        self.demo_dataset.process_data_from_list()

        demo_data_loader = DataLoader(self.demo_dataset, batch_size=50, shuffle=False)

        demo_preds = np.zeros([0, self.demo_dataset.num_labels], dtype=np.int)
        for batch, data in enumerate(demo_data_loader):
            sequences_ttl, sequences_cnt, labels = data
            preds = self.network.test(sequences_ttl, sequences_cnt)
            demo_preds = np.concatenate((demo_preds, preds), axis=0)

        result_list = []
        for index in range(self.demo_dataset.num_samples):
            strategy_ids = []
            for label in range(self.demo_dataset.num_labels):
                if demo_preds[index, label] == 1:
                    strategy_ids.append(self.demo_dataset.label2strategy[label])
            result = {"strategy_ids": strategy_ids}
            result_list.append(result)
        return result_list
