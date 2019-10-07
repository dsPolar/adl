# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pnOcMyobH9Ik1NRdfnqZ4Qtw0Unb6B-p
"""

import torch
torch.__version__

import numpy as np

from sklearn import datasets
iris = datasets.load_iris()


import seaborn as sns
import pandas as pd

features_df = pd.DataFrame(
  iris['data'],
  columns=iris['feature_names']
)
features_df['label'] = iris['target_names'][iris['target']]


preprocessed_features = (iris['data'] - iris['data'].mean(axis=0)) / iris['data'].std(axis=0)

from sklearn.model_selection import train_test_split

labels = iris['target']
train_features, test_features, train_labels, test_labels = train_test_split(preprocessed_features, labels, test_size=1/3)

features = {
    'train': torch.tensor(train_features, dtype=torch.float32),
    'test': torch.tensor(test_features, dtype=torch.float32),
}
labels = {
    'train': torch.tensor(train_labels, dtype=torch.long),
    'test': torch.tensor(test_labels, dtype=torch.long),
}

from torch import nn
from torch.nn import functional as F
from typing import Callable

class MLP(nn.Module):
  def __init__(self,
              input_size: int,
              hidden_layer_size: int,
              output_size: int,
              activation_fn: Callable[[torch.Tensor], torch.Tensor] = F.relu):
    super().__init__()
    self.l1 = nn.Linear(input_size, hidden_layer_size)
    self.l2 = nn.Linear(hidden_layer_size, output_size)
    self.activation_fn = activation_fn

  def forward(self, inputs: torch.Tensor) -> torch.Tensor:
    x = self.l1(inputs)
    x = self.activation_fn(x)
    x = self.l2(x)
    return x

feature_count = 4
hidden_layer_size = 100
class_count = 3
model = MLP(feature_count, hidden_layer_size, class_count)

logits = model.forward(features['train'])

lossCE = nn.CrossEntropyLoss()
loss = lossCE(logits,labels['train'])

loss.backward()

"""Compute Accuracy of probs Tensor compared to targets Tensor"""

def accuracy(probs: torch.FloatTensor,
             targets:torch.LongTensor) -> float:
  predLabels = torch.argmax(probs, 1)
  correct = torch.eq(predLabels,targets).sum().float()
  correctVal = correct/targets.size()[0]
  return correctVal

from torch import optim

model = MLP(feature_count, hidden_layer_size, class_count)

optimizer = optim.SGD(model.parameters(), lr=0.05)

criterion = nn.CrossEntropyLoss()

for epoch in range(0,100):
  logits = model.forward(features['train'])
  loss = criterion(logits, labels['train'])

  print("epoch: {} train accuracy: {:2.2f}, loss: {:5.5f}".format(
        epoch,
        accuracy(logits, labels['train']) * 100,
        loss.item()
    ))

  loss.backward()

  optimizer.step()

  optimizer.zero_grad()

logits = model.forward(features['test'])
test_accuracy = accuracy(logits, labels['test']) * 100
print("test accuracy: {:2.2f}".format(test_accuracy))
