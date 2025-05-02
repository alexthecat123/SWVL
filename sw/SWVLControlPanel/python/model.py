import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights


class RegHead(nn.Module):
    def __init__(self, in_channels, S, B, dropout=0.0):
        super().__init__()
        self.conv0_depthwise = nn.Conv2d(in_channels, in_channels, 3, padding=1, groups=in_channels)
        self.conv0_pointwise = nn.Conv2d(in_channels, 960, 1)
        
        self.conv1_depthwise = nn.Conv2d(960, 960, 3, padding=1, groups=960)
        self.conv1_pointwise = nn.Conv2d(960, 960, 1)
        
        self.conv2_depthwise = nn.Conv2d(960, 960, 3, padding=1, groups=960)
        self.conv2_pointwise = nn.Conv2d(960, 960, 1)
        
        self.conv3_depthwise = nn.Conv2d(960, 960, 3, padding=1, groups=960)
        self.conv3_pointwise = nn.Conv2d(960, 960, 1)

        self.l0 = nn.Linear(188160, 4096)
        self.drop = nn.Dropout(dropout)
        self.act = nn.LeakyReLU(0.1)
        self.l1 = nn.Linear(4096, (S * S * (B * 5)))

    def forward(self, x):
        x = self.conv0_depthwise(x)
        x = self.conv0_pointwise(x)
        
        x = self.conv1_depthwise(x)
        x = self.conv1_pointwise(x)
        
        x = self.conv2_depthwise(x)
        x = self.conv2_pointwise(x)
        
        x = self.conv3_depthwise(x)
        x = self.conv3_pointwise(x)

        x = x.flatten(start_dim=1)
        x = self.l0(x)
        x = self.drop(x)
        x = self.act(x)
        x = self.l1(x)
        return x




class FaceDetector(nn.Module):
    def __init__(self, S=7, B=2, dropout=0.0):
        super(FaceDetector, self).__init__()

        backbone = mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)
        self.backbone = torch.nn.Sequential(*(list(backbone.children())[:-2]))
        
        self.regression_head = RegHead(960, S, B, dropout=dropout)
    
    def forward(self, x):
        features = self.backbone(x)
        out = self.regression_head(features)
        return out