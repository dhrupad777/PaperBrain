import torch
import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self, num_classes=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.fc = nn.Linear(32, num_classes)

    def forward(self, x):
        feat = self.net(x).squeeze(-1).squeeze(-1)
        return self.fc(feat)

