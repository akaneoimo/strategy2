# -*- coding: utf-8 -*-

import json
import os

class Config(object):
    def __init__(self):
        self.configs = {}

        # config name
        self.configs["config_name"] = None

        # directories
        self.configs["src_dir"]    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
        self.configs["data_dir"]   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.configs["cache_dir"]  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        self.configs["config_dir"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.configs["log_dir"]    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")

        # files
        self.configs["word_vector_file"] = None

        # data config
        self.configs["train_data_file"] = None
        self.configs["valid_data_file"] = None
        self.configs["test_data_file"]  = None
        self.configs["data_config"]     = {}

        # model config
        self.configs["model_name"]   = None
        self.configs["model_config"] = {}

        # training config
        self.configs["batch_size"]    = 100
        self.configs["num_epochs"]    = 40
        self.configs["early_stop"]    = 5
        self.configs["info_interval"] = 1

    def __str__(self):
        return json.dumps(self.configs, indent=4)

    def update_config(self, config_file):
        with open(config_file, "r") as file:
            new_config = json.load(file)
        for key in new_config:
            if key in self.configs:
                self.configs[key] = new_config[key]

    def update_data_config(self, new_data_config):
        for key in new_data_config:
            self.configs["data_config"][key] = new_data_config[key]

    def update_model_config(self, new_model_config):
        for key in new_model_config:
            self.configs["model_config"][key] = new_model_config[key]

    @property
    def config_name(self):
        return self.configs["config_name"]

    @property
    def src_dir(self):
        return self.configs["src_dir"]

    @property
    def data_dir(self):
        return self.configs["data_dir"]

    @property
    def cache_dir(self):
        return self.configs["cache_dir"]

    @property
    def config_dir(self):
        return self.configs["config_dir"]

    @property
    def log_dir(self):
        return self.configs["log_dir"]

    @property
    def word_vector_file(self):
        return self.configs["word_vector_file"]

    @property
    def train_data_file(self):
        return self.configs["train_data_file"]

    @property
    def valid_data_file(self):
        return self.configs["valid_data_file"]

    @property
    def test_data_file(self):
        return self.configs["test_data_file"]

    @property
    def data_config(self):
        return self.configs["data_config"]

    @property
    def model_name(self):
        return self.configs["model_name"]

    @property
    def model_config(self):
        return self.configs["model_config"]

    @property
    def batch_size(self):
        return self.configs["batch_size"]

    @property
    def num_epochs(self):
        return self.configs["num_epochs"]

    @property
    def early_stop(self):
        return self.configs["early_stop"]

    @property
    def info_interval(self):
        return self.configs["info_interval"]
