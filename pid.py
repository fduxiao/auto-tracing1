"""
PID control
"""
from dataclasses import dataclass
from timer import Timer
from motion import Motion


@dataclass
class PID:
    target: float = 0
    diff: float = 0
    p: float = 0
    i: float = 0
    d: float = 0
    e: float = 0  # execution amount

    def execute(self, x, time, time_epsilon=0.001):
        self.diff = x - self.target
        self.d = self.diff / (time + time_epsilon)
        # a naive strategy
        if self.diff > 100:
            self.e = 1
        if self.diff < -100:
            self.e = -1
        return self.e


class Controller:
    """
    PID control class, which has an instance of :py:class:`Motion`, an instance of :py:class:`Timer` and
    the pos of the box of face. The goal of PID is to adjust the servo motors so that the center of the
    box will be at the predefined target point.
    """
    def __init__(self, motion: Motion = None, target_point=(10, 10)):
        self.motion = motion
        self.target_point = target_point
        self.timer = Timer()
        self.time_diff = 0

        self.x = PID(target_point[0])
        self.y = PID(target_point[1])

    def execute(self, box):
        self.time_diff = time_diff = self.timer.diff()
        if time_diff is None:
            return

        x1, y1, x2, y2 = box
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        ex = self.x.execute(x, time_diff)
        ey = self.y.execute(y, time_diff)

        if self.motion is None:
            return

        self.motion.set_x_offset(ex)
        self.motion.set_y_offset(ey)
