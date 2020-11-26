# -*- coding: utf-8 -*-

import argparse
import os

import numpy as np
from torch.utils.data import DataLoader

from core.config import Config
from core.dataset import Dataset
from core.embedding import Embedding
from core.factory import Factory
from core.logger import Logger
from core.metric import Metric
from core.model import Model


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    return args


def test(config_filename):
    # configuration
    config = Config()
    config_file = "{}/{}".format(config.config_dir, config_filename)
    config.update_config(config_file)

    # logger
    log_file = "{}/test_{}.txt".format(config.log_dir, config.config_name)
    logger = Logger(log_file)

    # word embedding
    logger.info("setting word embedding...")
    word_embedding = Embedding()

    word_embedding_file = "{}/word_embedding_{}.pkl".format(config.cache_dir, config.config_name)
    logger.info("loading word embedding from {}...".format(word_embedding_file))
    word_embedding.load_word_embedding(word_embedding_file)

    logger.info("vocab_size: {}".format(word_embedding.vocab_size))
    logger.info("word_dim  : {}".format(word_embedding.word_dim))

    # testing dataset
    logger.info("setting testing dataset...")
    test_dataset = Dataset(config.data_config)

    test_dataset.set_word_to_index(word_embedding.word2index)

    label_mapping_file = "{}/label_mapping_{}.pkl".format(config.cache_dir, config.config_name)
    logger.info("loading label mapping from {}...".format(label_mapping_file))
    test_dataset.load_label_mapping(label_mapping_file)

    test_data_file = "{}/{}".format(config.data_dir, config.test_data_file)
    logger.info("loading data from {}...".format(test_data_file))
    test_dataset.load_data_from_file(test_data_file)
    logger.info("number of samples: {}".format(test_dataset.num_samples))

    logger.info("processing data...")
    test_dataset.process_data_from_file()

    # model
    new_model_config = {
        "vocab_size": word_embedding.vocab_size,
        "word_dim"  : word_embedding.word_dim,
        "document_length": test_dataset.document_length,
        "sentence_length": test_dataset.sentence_length,
        "num_labels"     : test_dataset.num_labels
        }
    config.update_model_config(new_model_config)

    model = Model(config.model_config)

    # metric
    metric = Metric()

    # test configuration
    logger.info("configuration: {}".format(config))

    # data loader
    test_data_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)

    # model factory
    network = Factory(model)
    network.set_test_module()
    logger.info("number of GPUs: {}".format(network.num_gpus))
    logger.info("device: {}".format(network.device))

    # load model
    model_file = "{}/model_{}.pkl".format(config.cache_dir, config.config_name)
    logger.info("loading model from {}...".format(model_file))
    network.load_model(model_file)

    network.model_to_device()

    # test
    network.eval_mode()
    test_preds  = np.zeros([0, test_dataset.num_labels], dtype=np.int)
    test_labels = np.zeros([0, test_dataset.num_labels], dtype=np.int)
    for batch, data in enumerate(test_data_loader):
        sequences_ttl, sequences_cnt, labels = data
        preds = network.test(sequences_ttl, sequences_cnt)
        test_preds  = np.concatenate((test_preds, preds), axis=0)
        test_labels = np.concatenate((test_labels, labels.numpy().astype(np.int)), axis=0)

    # metrics
    ac, mp, mr, mf = metric.all_metrics(test_preds, test_labels)
    logger.info("Acc: {:.4f}".format(ac))
    logger.info("MP : {:.4f}".format(mp))
    logger.info("MR : {:.4f}".format(mr))
    logger.info("MF : {:.4f}".format(mf))


if __name__ == "__main__":
    args = parse_args()
    test(args.config_file)
