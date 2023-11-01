#!/usr/bin/env python3
"""
The main program maintaining the video capturing and displaying window
"""
import argparse
import platform
from types import ModuleType

import cv2

from timer import Timer
from video import VideoCapture
from face import Face
from pid import Controller
from motion import Motion


def int_round(x):
    return int(round(x))


def put_text(mat, text, origin, scale: float = 1, color=(0, 255, 0), thickness=2):
    cv2.putText(mat, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


class Loop:
    def __init__(self, cap: VideoCapture, face: Face, resize_ratio,
                 pid: Controller, title="video", draw_scale=1, draw_thickness=2):
        self.cap = cap
        self.title = title
        self.face = face
        self.debug = True
        self.draw_scale = draw_scale
        self.draw_thickness = draw_thickness
        self.timer = Timer()
        self.pid = pid
        self.resize_ratio = resize_ratio

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

        height, width = frame.shape[:2]
        resized = cv2.resize(frame, (int_round(width * self.resize_ratio), int_round(height * self.resize_ratio)))
        box = self.face.detect(resized)

        if box is not None:
            box_height, box_width = resized.shape[:2]
            box[0] /= box_width
            box[2] /= box_width

            box[1] /= box_height
            box[3] /= box_height
            self.pid.execute(box)
        else:
            self.pid.reset()

        # drawing
        if self.debug:
            thickness = self.draw_thickness
            tx, ty = self.pid.target_point
            cv2.circle(frame, (int_round(tx * width), int_round(ty * height)),
                       radius=50, color=(0, 0, 255), thickness=thickness)

            def draw_text(text, origin, color=(0, 255, 0)):
                put_text(frame, text, origin, scale=self.draw_scale, color=color, thickness=thickness)

            if frame_rate:
                draw_text(f"fps: {frame_rate:.1f}", (width - 200, 50))
            draw_text("debug", (50, 50))

            if box is not None:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame,
                              (int_round(x1 * width), int_round(y1 * height)),
                              (int_round(x2 * width), int_round(y2 * height)),
                              (255, 0, 0), thickness)

            draw_text(f"pid info: time diff {self.pid.time_diff}", (50, 100))
            draw_text(f"x: {self.pid.x}", (50, 150))
            draw_text(f"y: {self.pid.y}", (50, 200))

        # show frame:
        cv2.imshow(self.title, frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            return False
        elif key == ord('d'):
            self.debug = not self.debug
        return True


class Settings(ModuleType):
    resize_ratio = 0.5
    device: str = ""
    draw_scale = 1
    draw_thickness: int = 2
    api_preference = cv2.CAP_ANY
    camera_settings = dict()

    face_detection_device = "cpu"

    motion_settings = dict()
    pid_settings = dict()


def load_settings(path):
    with open(path, "r") as file:
        content = file.read()
    settings = Settings("settings")
    exec(content, settings.__dict__)
    return settings


def settings_from_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs='?', default="settings.py",
                        help="a python module containing everything")

    args = parser.parse_args()
    settings = load_settings(args.settings)
    return settings


def main():
    settings = settings_from_argument()

    # on OS X, I currently don't want to support the motion control on my macbook.
    motion = None
    if platform.system() != "Darwin":
        motion = Motion(**settings.motion_settings)

    loop = Loop(
        resize_ratio=settings.resize_ratio,
        cap=VideoCapture(settings.device, api_preference=settings.api_preference).set(**settings.camera_settings),
        face=Face(settings.face_detection_device),
        pid=Controller(motion, **settings.pid_settings),
        draw_scale=settings.draw_scale, draw_thickness=settings.draw_thickness
    )
    loop.run()


if __name__ == '__main__':
    main()
