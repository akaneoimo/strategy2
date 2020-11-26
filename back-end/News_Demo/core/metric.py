# -*- coding: utf-8 -*-

import sklearn.metrics as metrics


class Metric(object):
    def accuracy(self, preds, labels):
        """
        preds : [num_samples]
        labels: [num_samples]
        accuracy: float
        """
        accuracy = metrics.accuracy_score(labels, preds)
        return accuracy

    def macro_precision(self, preds, labels):
        """
        preds : [num_samples]
        labels: [num_samples]
        macro_precision: float
        """
        macro_precision = metrics.precision_score(labels, preds, average="micro")
        return macro_precision

    def macro_recall(self, preds, labels):
        """
        preds : [num_samples]
        labels: [num_samples]
        macro_recall: float
        """
        macro_recall = metrics.recall_score(labels, preds, average="micro")
        return macro_recall

    def macro_f1(self, preds, labels):
        """
        preds : [num_samples]
        labels: [num_samples]
        macro_f1: float
        """
        macro_f1 = metrics.f1_score(labels, preds, average="micro")
        return macro_f1

    def all_metrics(self, preds, labels):
        ac = self.accuracy(preds, labels)
        mp = self.macro_precision(preds, labels)
        mr = self.macro_recall(preds, labels)
        mf = self.macro_f1(preds, labels)
        return ac, mp, mr, mf
