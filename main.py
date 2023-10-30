#!/usr/bin/env python3
"""
The main program maintaining the video capturing and displaying window
"""
import argparse
from types import ModuleType

import cv2

from video import VideoCapture


class Loop:
    def __init__(self, cap: VideoCapture, title="video"):
        self.cap = cap
        self.title = title

    def run(self):
        while True:
            if not self.loop():
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def loop(self) -> bool:
        ret, frame = self.cap.read()
        if not ret:
            print(f"cannot read {self.cap}")
            return False

        # show frame:
        cv2.imshow(self.title, frame)
        if cv2.waitKey(1) == ord('q'):
            return False
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs='?', default="settings.py",
                        help="a python module containing everything")

    args = parser.parse_args()
    with open(args.settings, "r") as file:
        content = file.read()
    settings = ModuleType("settings")
    exec(content, settings.__dict__)

    loop = Loop(
        cap=VideoCapture(settings.device, api_preference=settings.api_preference).set(**settings.camera_settings)
    )
    loop.run()


if __name__ == '__main__':
    main()
