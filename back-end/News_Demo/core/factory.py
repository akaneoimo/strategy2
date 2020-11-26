# -*- coding: utf-8 -*-

import numpy as np

import torch
import torch.nn as nn


class Factory(object):
    def __init__(self, model):
        self.model     = model
        self.num_gpus  = None
        self.device    = None
        self.loss_fun  = None
        self.optimizer = None

    def set_train_module(self):
        self.num_gpus  = torch.cuda.device_count()
        self.device    = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.loss_fun  = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters())

    def set_test_module(self):
        self.num_gpus = torch.cuda.device_count()
        self.device   = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def set_word_embedding(self, matrix):
        self.model.word_embedding.weight = nn.Parameter(torch.FloatTensor(matrix))

    def model_to_device(self):
        if self.num_gpus > 1:
            self.model = nn.DataParallel(self.model)
        self.model.to(self.device)

    def train_mode(self):
        self.model.train()

    def eval_mode(self):
        self.model.eval()

    def train(self, sequences_ttl, sequences_cnt, labels):
        sequences_ttl = sequences_ttl.to(self.device)
        sequences_cnt = sequences_cnt.to(self.device)
        labels        = labels.to(self.device)

        logits = self.model(sequences_ttl, sequences_cnt)
        loss   = self.loss_fun(logits, labels)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        loss_value = loss.item()
        return loss_value

    def validate(self, sequences_ttl, sequences_cnt, labels):
        with torch.no_grad():
            sequences_ttl = sequences_ttl.to(self.device)
            sequences_cnt = sequences_cnt.to(self.device)
            labels        = labels.to(self.device)

            logits = self.model(sequences_ttl, sequences_cnt)
            loss   = self.loss_fun(logits, labels)
            preds  = np.array(logits.detach().cpu().numpy() > 0, dtype=np.int)

            loss_value = loss.item()
            return preds, loss_value

    def test(self, sequences_ttl, sequences_cnt):
        with torch.no_grad():
            sequences_ttl = sequences_ttl.to(self.device)
            sequences_cnt = sequences_cnt.to(self.device)

            logits = self.model(sequences_ttl, sequences_cnt)
            preds  = np.array(logits.detach().cpu().numpy() > 0, dtype=np.int)

            return preds

    def load_model(self, model_file):
        with open(model_file, "rb") as file:
            params = torch.load(file, map_location=self.device)
        self.model.load_state_dict(params)

    def save_model(self, model_file):
        if self.num_gpus > 1:
            params = self.model.module.state_dict()
        else:
            params = self.model.state_dict()
        with open(model_file, "wb") as file:
            torch.save(params, file)
