# -*- coding: utf-8 -*-

import torch
import torch.nn as nn


class Model(nn.Module):
    def __init__(self, config):
        super(Model, self).__init__()

        self.vocab_size      = config["vocab_size"]
        self.word_dim        = config["word_dim"]
        self.document_length = config["document_length"]
        self.sentence_length = config["sentence_length"]
        self.hidden_size_rnn = config["hidden_size_rnn"]
        self.hidden_size_att = config["hidden_size_att"]
        self.hidden_size_cls = config["hidden_size_cls"]
        self.num_labels      = config["num_labels"]
        self.dropout_prob    = config["dropout_prob"]

        self.word_embedding = nn.Embedding(self.vocab_size, self.word_dim)

        self.sentence_vector = nn.Parameter(torch.rand(2*self.hidden_size_rnn))
        self.document_vector = nn.Parameter(torch.rand(2*self.hidden_size_rnn))

        self.sentence_encoder = SentenceEncoder(sentence_length=self.sentence_length,
                                                input_size=self.word_dim,
                                                hidden_size_rnn=self.hidden_size_rnn,
                                                hidden_size_att=self.hidden_size_att)

        self.document_encoder = DocumentEncoder(document_length=self.document_length,
                                                input_size=2*self.hidden_size_rnn,
                                                hidden_size_rnn=self.hidden_size_rnn,
                                                hidden_size_att=self.hidden_size_att)

        self.classifier = Classifier(feature_size=4*self.hidden_size_rnn,
                                     hidden_size=self.hidden_size_cls,
                                     num_labels=self.num_labels,
                                     dropout_prob=self.dropout_prob)

    def forward(self, sequences_ttl, sequences_cnt):
        """
        sequences_ttl: [batch_size, sentence_length]
        sequences_cnt: [batch_size, document_length, sentence_length]
        logits       : [batch_size, num_labels]
        """
        # word embedding
        embeddings_ttl = self.word_embedding(sequences_ttl) # [batch_size, sentence_length, word_dim]
        embeddings_cnt = self.word_embedding(sequences_cnt) # [batch_size, document_length, sentence_length, word_dim]

        # title encoding
        features_ttl = self.sentence_encoder(embeddings_ttl, self.sentence_vector) # [batch_size, 2*hidden_size_rnn]

        # content encoding
        inputs_sen  = embeddings_cnt.view(-1, self.sentence_length, self.word_dim) # [batch_size*document_length, sentence_length, word_dim]
        outputs_sen = self.sentence_encoder(inputs_sen, self.sentence_vector) # [batch_size*document_length, 2*hidden_size_rnn]

        inputs_doc   = outputs_sen.view(-1, self.document_length, 2*self.hidden_size_rnn) # [batch_size, document_length, 2*hidden_size_rnn]
        features_cnt = self.document_encoder(inputs_doc, self.document_vector) # [batch_size, 2*hidden_size_rnn]

        # classification
        features = torch.cat((features_ttl, features_cnt), 1) # [batch_size, 4*hidden_size_rnn]
        logits = self.classifier(features) # [batch_size, num_labels]
        return logits


class SentenceEncoder(nn.Module):
    def __init__(self, sentence_length, input_size, hidden_size_rnn, hidden_size_att):
        super(SentenceEncoder, self).__init__()

        self.sentence_length = sentence_length
        self.input_size      = input_size
        self.hidden_size_rnn = hidden_size_rnn
        self.hidden_size_att = hidden_size_att

        self.rnn = nn.GRU(input_size=self.input_size,
                          hidden_size=self.hidden_size_rnn,
                          batch_first=True,
                          bidirectional=True)

        self.fc_layer_0 = nn.Linear(4*self.hidden_size_rnn, self.hidden_size_att)
        self.tanh       = nn.Tanh()
        self.fc_layer_1 = nn.Linear(self.hidden_size_att, 1)

    def forward(self, inputs, sentence_vector):
        """
        inputs         : [num_sentences, sentence_length, input_size]
        sentence_vector: [2*hidden_size_rnn]
        outputs        : [num_sentences, 2*hidden_size_rnn]
        """
        num_sentences = inputs.shape[0]

        rnn_output, _ = self.rnn(inputs) # [num_sentences, sentence_length, 2*hidden_size_rnn]

        extended_sentence_vector = sentence_vector.unsqueeze(0) # [1, 2*hidden_size_rnn]
        extended_sentence_vector = extended_sentence_vector.unsqueeze(0) # [1, 1, 2*hidden_size_rnn]
        extended_sentence_vector = extended_sentence_vector.repeat(num_sentences, self.sentence_length, 1) # [num_sentences, sentence_length, 2*hidden_size_rnn]

        attention_query = torch.cat((rnn_output, extended_sentence_vector), 2) # [num_sentences, sentence_length, 4*hidden_size_rnn]
        attention_temp  = self.fc_layer_0(attention_query) # [num_sentences, sentence_length, hidden_size_att]
        attention_temp  = self.tanh(attention_temp)
        attention_score = self.fc_layer_1(attention_temp) # [num_sentences, sentence_length, 1]
        attention_prob  = nn.Softmax(dim=1)(attention_score) # [num_sentences, sentence_length, 1]
        extended_attention_prob = attention_prob.repeat(1, 1, 2*self.hidden_size_rnn) # [num_sentences, sentence_length, 2*hidden_size_rnn]
        attention_rnn_output = rnn_output * extended_attention_prob # [num_sentences, sentence_length, 2*hidden_size_rnn]
        attention_rnn_output = torch.sum(attention_rnn_output, dim=1) # [num_sentences, 2*hidden_size_rnn]

        outputs = attention_rnn_output # [num_sentences, 2*hidden_size_rnn]
        return outputs


class DocumentEncoder(nn.Module):
    def __init__(self, document_length, input_size, hidden_size_rnn, hidden_size_att):
        super(DocumentEncoder, self).__init__()

        self.document_length = document_length
        self.input_size      = input_size
        self.hidden_size_rnn = hidden_size_rnn
        self.hidden_size_att = hidden_size_att

        self.rnn = nn.GRU(input_size=self.input_size,
                          hidden_size=self.hidden_size_rnn,
                          batch_first=True,
                          bidirectional=True)

        self.fc_layer_0 = nn.Linear(4*self.hidden_size_rnn, self.hidden_size_att)
        self.tanh       = nn.Tanh()
        self.fc_layer_1 = nn.Linear(self.hidden_size_att, 1)

    def forward(self, inputs, document_vector):
        """
        inputs         : [num_documents, document_length, input_size]
        document_vector: [2*hidden_size_rnn]
        outputs        : [num_documents, 2*hidden_size_rnn]
        """
        num_documents = inputs.shape[0]

        rnn_output, _ = self.rnn(inputs) # [num_documents, document_length, 2*hidden_size_rnn]

        extended_document_vector = document_vector.unsqueeze(0) # [1, 2*hidden_size_rnn]
        extended_document_vector = extended_document_vector.unsqueeze(0) # [1, 1, 2*hidden_size_rnn]
        extended_document_vector = extended_document_vector.repeat(num_documents, self.document_length, 1) # [num_documents, document_length, 2*hidden_size_rnn]

        attention_query = torch.cat((rnn_output, extended_document_vector), 2) # [num_documents, document_length, 4*hidden_size_rnn]
        attention_temp  = self.fc_layer_0(attention_query) # [num_documents, document_length, hidden_size_att]
        attention_temp  = self.tanh(attention_temp)
        attention_score = self.fc_layer_1(attention_temp) # [num_documents, document_length, 1]
        attention_prob  = nn.Softmax(dim=1)(attention_score) # [num_documents, document_length, 1]
        extended_attention_prob = attention_prob.repeat(1, 1, 2*self.hidden_size_rnn) # [num_documents, document_length, 2*hidden_size_rnn]
        attention_rnn_output = rnn_output * extended_attention_prob # [num_documents, document_length, 2*hidden_size_rnn]
        attention_rnn_output = torch.sum(attention_rnn_output, dim=1) # [num_documents, 2*hidden_size_rnn]

        outputs = attention_rnn_output # [num_documents, 2*hidden_size_rnn]
        return outputs


class Classifier(nn.Module):
    def __init__(self, feature_size, hidden_size, num_labels, dropout_prob):
        super(Classifier, self).__init__()

        self.feature_size = feature_size
        self.hidden_size  = hidden_size
        self.num_labels   = num_labels
        self.dropout_prob = dropout_prob

        self.fc_layer_0 = nn.Linear(self.feature_size, self.hidden_size)
        self.tanh       = nn.Tanh()
        self.dropout    = nn.Dropout(self.dropout_prob)
        self.fc_layer_1 = nn.Linear(self.hidden_size, self.num_labels)

    def forward(self, features):
        """
        features: [batch_size, feature_size]
        logits  : [batch_size, num_labels]
        """
        output = self.fc_layer_0(features) # [batch_size, hidden_size]
        output = self.tanh(output)
        output = self.dropout(output)
        logits = self.fc_layer_1(output) # [batch_size, num_labels]
        return logits
