#!/usr/bin/env python3
"""
The main program maintaining the video capturing and displaying window
"""
import argparse
import time
from types import ModuleType

# I don't know why without this I encountered an ImportError on Nvidia Jetpack
import torch as _
import cv2

from video import VideoCapture
from face import Face


def int_round(x):
    return int(round(x))


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


class Loop:
    def __init__(self, cap: VideoCapture, face: Face, title="video"):
        self.cap = cap
        self.title = title
        self.face = face
        self.debug = True
        self.timer = Timer()

    def run(self):
        while True:
            if not self.loop():
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def loop(self) -> bool:
        frame_rate = None
        if self.debug:
            # calculate time for frame rate
            frame_rate = self.timer.rate()
        ret, frame = self.cap.read()
        if not ret:
            print(f"cannot read {self.cap}")
            return False

        box = self.face.detect(frame)

        # drawing
        if self.debug:
            h, w = frame.shape[:2]
            if frame_rate:
                cv2.putText(frame, f"fps: {frame_rate:.1f}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)
            cv2.putText(frame, "debug", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if box is not None:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (int_round(x1), int_round(y1)), (int_round(x2), int_round(y2)), (255, 0, 0), 2)

        # show frame:
        cv2.imshow(self.title, frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            return False
        elif key == ord('d'):
            self.debug = not self.debug
        return True


class Settings(ModuleType):
    device: str = ""
    api_preference = cv2.CAP_ANY
    camera_settings = dict()
    face_detection_device = "cpu"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs='?', default="settings.py",
                        help="a python module containing everything")

    args = parser.parse_args()
    with open(args.settings, "r") as file:
        content = file.read()
    settings = Settings("settings")
    exec(content, settings.__dict__)

    loop = Loop(
        cap=VideoCapture(settings.device, api_preference=settings.api_preference).set(**settings.camera_settings),
        face=Face(settings.face_detection_device),
    )
    loop.run()


if __name__ == '__main__':
    main()
