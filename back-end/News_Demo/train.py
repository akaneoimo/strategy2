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


def train(config_filename):
    # configuration
    config = Config()
    config_file = "{}/{}".format(config.config_dir, config_filename)
    config.update_config(config_file)

    # logger
    log_file = "{}/train_{}.txt".format(config.log_dir, config.config_name)
    logger = Logger(log_file)

    # word embedding
    logger.info("setting word embedding...")
    word_embedding = Embedding()

    train_data_file     = "{}/{}".format(config.data_dir, config.train_data_file)
    word_vector_file    = "{}/{}".format(config.src_dir, config.word_vector_file)
    vocab_list_file     = "{}/vocab_list_{}.txt".format(config.cache_dir, config.config_name)
    word_embedding_file = "{}/word_embedding_{}.pkl".format(config.cache_dir, config.config_name)

    if not os.path.exists(word_embedding_file):
        logger.info("building word embedding...")
        word_embedding.build_word_embedding(train_data_file, word_vector_file, vocab_list_file, word_embedding_file)

    logger.info("loading word embedding from {}...".format(word_embedding_file))
    word_embedding.load_word_embedding(word_embedding_file)

    logger.info("vocab_size: {}".format(word_embedding.vocab_size))
    logger.info("word_dim  : {}".format(word_embedding.word_dim))

    # training dataset
    logger.info("setting training dataset...")
    train_dataset = Dataset(config.data_config)

    train_dataset.set_word_to_index(word_embedding.word2index)

    train_data_file = "{}/{}".format(config.data_dir, config.train_data_file)
    logger.info("loading data from {}...".format(train_data_file))
    train_dataset.load_data_from_file(train_data_file)
    logger.info("number of samples: {}".format(train_dataset.num_samples))

    label_list_file    = "{}/label_list_{}.txt".format(config.cache_dir, config.config_name)
    label_mapping_file = "{}/label_mapping_{}.pkl".format(config.cache_dir, config.config_name)
    logger.info("building label mapping...")
    train_dataset.build_label_mapping(label_list_file, label_mapping_file)

    logger.info("processing data...")
    train_dataset.process_data_from_file()

    # validation dataset
    logger.info("setting validation dataset...")
    valid_dataset = Dataset(config.data_config)

    valid_dataset.set_word_to_index(word_embedding.word2index)

    label_mapping_file = "{}/label_mapping_{}.pkl".format(config.cache_dir, config.config_name)
    logger.info("loading label mapping from {}...".format(label_mapping_file))
    valid_dataset.load_label_mapping(label_mapping_file)

    valid_data_file = "{}/{}".format(config.data_dir, config.valid_data_file)
    logger.info("loading data from {}...".format(valid_data_file))
    valid_dataset.load_data_from_file(valid_data_file)
    logger.info("number of samples: {}".format(valid_dataset.num_samples))

    logger.info("processing data...")
    valid_dataset.process_data_from_file()

    # model
    new_model_config = {
        "vocab_size": word_embedding.vocab_size,
        "word_dim"  : word_embedding.word_dim,
        "document_length": train_dataset.document_length,
        "sentence_length": train_dataset.sentence_length,
        "num_labels"     : train_dataset.num_labels
        }
    config.update_model_config(new_model_config)

    model = Model(config.model_config)

    # metric
    metric = Metric()

    # train configuration
    logger.info("configuration: {}".format(config))

    # data loader
    train_data_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    valid_data_loader = DataLoader(valid_dataset, batch_size=config.batch_size, shuffle=False)

    # model factory
    network = Factory(model)
    network.set_train_module()
    logger.info("number of GPUs: {}".format(network.num_gpus))
    logger.info("device: {}".format(network.device))

    # set word embedding
    network.set_word_embedding(word_embedding.matrix)

    network.model_to_device()

    # train and validate
    max_mf = 0
    epoch_count = 0
    for epoch in range(config.num_epochs):
        logger.info("----------------------------------------")

        # train
        network.train_mode()
        for batch, data in enumerate(train_data_loader):
            sequences_ttl, sequences_cnt, labels = data
            loss = network.train(sequences_ttl, sequences_cnt, labels)
            if batch > 0 and batch % config.info_interval == 0:
                logger.info("epoch: {} | batch: {} | loss: {:.6f}".format(epoch, batch, loss))

        # validate
        network.eval_mode()
        valid_preds  = np.zeros([0, valid_dataset.num_labels], dtype=np.int)
        valid_labels = np.zeros([0, valid_dataset.num_labels], dtype=np.int)
        for batch, data in enumerate(valid_data_loader):
            sequences_ttl, sequences_cnt, labels = data
            preds, loss = network.validate(sequences_ttl, sequences_cnt, labels)
            valid_preds  = np.concatenate((valid_preds, preds), axis=0)
            valid_labels = np.concatenate((valid_labels, labels.numpy().astype(np.int)), axis=0)

        # metrics
        ac, mp, mr, mf = metric.all_metrics(valid_preds, valid_labels)
        logger.info("Acc: {:.4f}".format(ac))
        logger.info("MP : {:.4f}".format(mp))
        logger.info("MR : {:.4f}".format(mr))
        logger.info("MF : {:.4f}".format(mf))

        # early stop
        if mf >= max_mf:
            max_mf = mf
            epoch_count = 0
            model_file = "{}/model_{}.pkl".format(config.cache_dir, config.config_name)
            logger.info("saving model to {}...".format(model_file))
            network.save_model(model_file)
        else:
            epoch_count += 1
            if epoch_count == config.early_stop:
                logger.info("stop training process.")
                logger.info("best epoch: {}".format(epoch - epoch_count))
                break


if __name__ == "__main__":
    args = parse_args()
    train(args.config_file)
