"""
This module is about controlling the servo motors via PCA9685
"""

from dataclasses import dataclass

try:
    from board import SDA, SCL
except NotImplementedError:
    SDA = SCL = 0


import busio


from adafruit_motor.servo import Servo
from adafruit_pca9685 import PCA9685


epsilon = 0.001  # used to compare between float


@dataclass
class ServoChannel:
    """
    Each servo is specified by (the index of) a channel (of PCA9685), the start and end angle,
    and the corresponding pulse width. Besides, the current angle is also maintained by this class
    """
    index: int
    actual_range: int = 0
    min_pulse: int = 500
    max_pulse: int = 2500

    start_angle: float = 0
    end_angle: float = 180

    angle: float = None
    servo: Servo = None

    def __post_init__(self):
        if self.angle is None:
            self.angle = (self.start_angle + self.end_angle) / 2

    def set_angle(self, angle):
        if angle < self.start_angle:
            angle = self.start_angle
        if angle > self.end_angle:
            angle = self.end_angle
        self.angle = angle
        if self.servo:
            self.servo.angle = angle
        return self.angle

    def set_offset(self, offset):
        return self.set_offset(self.angle + offset)

    @property
    def is_min(self):
        return self.angle <= self.start_angle + epsilon

    @property
    def is_max(self):
        return self.angle >= self.end_angle - epsilon

    def set_servo(self, servo: Servo):
        servo.actuation_range = self.actual_range
        servo.set_pulse_width_range(self.min_pulse, self.max_pulse)
        self.servo = servo
        self.set_angle(self.angle)
        return self


class Motion:
    def __init__(self, scl=SCL, sda=SDA,
                 frequency=50,
                 x_channel=(0, 180, 500, 2500, 10, 170),
                 y_channel=(1, 180, 500, 2500, 10, 170)):
        """
        initialize necessary bits

        :param scl: I2C clock
        :param sda: I2C data
        :param x_channel: can either be a tuple of :py:class:`ServoChannel`
        :param y_channel: can either be a tuple of :py:class:`ServoChannel`
        """
        # set up PCA9685
        self.i2c = busio.I2C(scl, sda)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = frequency

        # set up the two servos
        if not isinstance(x_channel, ServoChannel):
            x_channel = ServoChannel(*x_channel)
        if not isinstance(y_channel, ServoChannel):
            y_channel = ServoChannel(*y_channel)

        self.x_channel = x_channel.set_servo(Servo(self.pca.channels[x_channel.index]))
        self.y_channel = y_channel.set_servo(Servo(self.pca.channels[y_channel.index]))

    @property
    def x(self):
        return self.x_channel.angle

    @x.setter
    def x(self, v):
        self.x_channel.set_angle(v)

    @property
    def y(self):
        return self.y_channel.angle

    @y.setter
    def y(self, v):
        self.y_channel.set_angle(v)

    def set_x_offset(self, offset):
        self.x_channel.set_offset(offset)

    def set_y_offset(self, offset):
        self.y_channel.set_offset(offset)
