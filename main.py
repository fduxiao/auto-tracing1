#!/usr/bin/env python3
"""
The main program maintaining the video capturing and displaying window
"""
import argparse
import platform
from types import ModuleType

# I don't know why without this I encountered an ImportError on Nvidia Jetpack
import torch as _
import cv2

from timer import Timer
from video import VideoCapture
from face import Face
from pid import MatPID
from motion import Motion


def int_round(x):
    return int(round(x))


def put_text(mat, text, origin, scale=1, color=(0, 255, 0), thickness=2):
    cv2.putText(mat, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


class Loop:
    def __init__(self, cap: VideoCapture, face: Face, pid: MatPID, title="video"):
        self.cap = cap
        self.title = title
        self.face = face
        self.debug = True
        self.timer = Timer()
        self.pid = pid

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
        if box is not None:
            self.pid.execute(box)

        # drawing
        if self.debug:
            cv2.circle(frame, self.pid.target_point, 50, (0, 0, 255), 2)
            h, w = frame.shape[:2]
            if frame_rate:
                put_text(frame, f"fps: {frame_rate:.1f}", (w - 200, 50))
            put_text(frame, "debug", (50, 50))

            if box is not None:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (int_round(x1), int_round(y1)), (int_round(x2), int_round(y2)), (255, 0, 0), 2)

            put_text(frame, f"pid info: time diff {self.pid.time_diff}", (50, 100))
            put_text(frame, f"x: {self.pid.x}", (50, 150))
            put_text(frame, f"y: {self.pid.y}", (50, 200))

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

    motion_settings = dict()
    pid_settings = dict()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs='?', default="settings.py",
                        help="a python module containing everything")

    args = parser.parse_args()
    with open(args.settings, "r") as file:
        content = file.read()
    settings = Settings("settings")
    exec(content, settings.__dict__)

    # on OS X, I currently don't want to support the motion control on my macbook.
    motion = None
    if platform.system() != "Darwin":
        motion = Motion(**settings.motion_settings)

    loop = Loop(
        cap=VideoCapture(settings.device, api_preference=settings.api_preference).set(**settings.camera_settings),
        face=Face(settings.face_detection_device),
        pid=MatPID(motion, **settings.pid_settings)
    )
    loop.run()


if __name__ == '__main__':
    main()
