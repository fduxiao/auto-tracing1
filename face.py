"""
This module is used to detect the faces in the video
"""
import torch
from facenet_pytorch import MTCNN
import numpy as np


class Face:
    def __init__(self, device='cpu'):
        device = torch.device(device)
        self.mtcnn = MTCNN(keep_all=True, device=device)
        self.mtcnn.eval()

    def detect(self, img: np.ndarray):
        box, ps = self.mtcnn.detect(img)
        if box is None or ps is None:
            return None
        max_p = 0
        max_b = np.array([[0, 0, 0, 0]])
        for b, p in zip(box, ps):
            if p > max_p:
                max_p = p
                max_b = b
        return max_b
