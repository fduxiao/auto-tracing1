"""
PID control
"""
from dataclasses import dataclass
from timer import Timer
from motion import Motion


@dataclass
class PID:
    e: float = 0  # execution amount

    p: float = 0
    i: float = 0
    d: float = 0

    error: float = 0
    prev_error: float = 0

    # coefficients
    kp: float = 0
    ki: float = 0
    kd: float = 0
    # lower and upper bound of i
    min_i: float = -10
    max_i: float = 10

    # target value
    target: float = 0

    def execute(self, x, dt, time_epsilon=0.0001):
        self.error = x - self.target
        self.p = self.kp * self.error
        # update d
        self.d = (self.error - self.prev_error) / (dt + time_epsilon)
        self.prev_error = self.error

        # update i
        self.i += self.error * dt
        if self.i < self.min_i:
            self.i = self.min_i
        if self.i > self.max_i:
            self.i = self.max_i

        p_and_d = self.p + self.kd * self.d
        if self.p * self. d < 0 and abs(self.p) < abs(self.d):
            p_and_d = 0
        self.e = p_and_d + self.ki * self.i
        return self.e

    def reset(self):
        self.i = 0
        return self


class Controller:
    """
    PID control class, which has an instance of :py:class:`Motion`, an instance of :py:class:`Timer` and
    the pos of the box of face. The goal of PID is to adjust the servo motors so that the center of the
    box will be at the predefined target point.
    """
    def __init__(self, motion: Motion = None, target_point=(0.5, 0.3),
                 pid_x: dict = None, pid_y: dict = None):
        self.motion = motion
        self.target_point = target_point
        self.timer = Timer()
        self.time_diff = 0

        if pid_x is None:
            pid_x = dict(kp=0, ki=0, kd=0)
        if pid_y is None:
            pid_y = dict(kp=0, ki=0, kd=0)
        self.x = PID(target=target_point[0], **pid_x)
        self.y = PID(target=target_point[1], **pid_y)

    def reset(self):
        self.x.reset()
        self.y.reset()
        return self

    def execute(self, box, width, height):
        self.time_diff = time_diff = self.timer.diff()
        if time_diff is None:
            return

        x1, y1, x2, y2 = box
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        # use ratio instead of pixel
        x /= width
        y /= height

        ex = self.x.execute(x, time_diff)
        ey = self.y.execute(y, time_diff)

        if self.motion is None:
            return

        self.motion.set_x_offset(ex)
        self.motion.set_y_offset(ey)
