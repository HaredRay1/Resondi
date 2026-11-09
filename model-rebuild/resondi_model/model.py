"""The classifier: the same 1-D CNN as the deployed Edge Impulse model.

Input:  (batch, frames, 13) MFCC, frames = 50 for a 1 s window at a 20 ms stride.
Output: (batch, 4) probabilities in config label order.
"""
import torch
from torch import nn


class LungCNN(nn.Module):
    def __init__(self, n_mfcc, n_frames, n_classes, filters=(8, 16), kernel=3, pool=2, dropout=0.25):
        super().__init__()
        layers, ch, length = [], n_mfcc, n_frames
        for f in filters:
            layers += [nn.Conv1d(ch, f, kernel, padding="same"), nn.ReLU(),
                       nn.MaxPool1d(pool, pool, ceil_mode=True), nn.Dropout(dropout)]
            ch, length = f, -(-length // pool)
        self.features = nn.Sequential(*layers)
        self.head = nn.Linear(ch * length, n_classes)

    def forward(self, x):            # x: (batch, frames, mfcc)
        x = self.features(x.transpose(1, 2))
        return self.head(x.flatten(1))  # logits; softmax is applied at export and evaluation


def build(cfg, n_frames):
    m = cfg["model"]
    return LungCNN(cfg["mfcc"]["num_cepstral"], n_frames, len(cfg["labels"]), tuple(m["conv_filters"]),
                   m["kernel_size"], m["pool"], m["dropout"])
