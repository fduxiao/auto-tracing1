#!/usr/bin/env python3
import time

from main import settings_from_argument
from motion import Motion


if __name__ == '__main__':
    settings = settings_from_argument()
    motion = Motion(**settings.motion_settings)

    for i in range(0, 180, 10):
        motion.x = i
        time.sleep(0.5)

    for i in range(0, 180, 10):
        motion.y = i
        time.sleep(0.5)
