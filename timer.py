"""
A simple timer util
"""

import time


class Timer:
    def __init__(self):
        self.prev = None

    def diff(self):
        now = time.time()
        diff = None
        if self.prev:
            diff = now - self.prev
        self.prev = now
        return diff

    def rate(self, epsilon=0.001):
        diff = self.diff()
        if diff is None:
            return None
        return 1 / (diff + epsilon)
