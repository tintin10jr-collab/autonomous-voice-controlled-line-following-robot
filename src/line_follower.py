"""Two-sensor digital line following logic."""

from gpiozero import DigitalInputDevice

import config
from motors import Motors


class LineFollower:
    def __init__(self, motors=None):
        self._motors = motors or Motors()
        self._ir_left = DigitalInputDevice(config.IR_LEFT, pull_up=True)
        self._ir_right = DigitalInputDevice(config.IR_RIGHT, pull_up=True)
        self._last_action = Motors.ACTION_FORWARD

    def read_sensors(self):
        return self._ir_left.value, self._ir_right.value

    def on_line(self, value):
        return value == config.IR_ON_BLACK

    def step(self):
        left_val, right_val = self.read_sensors()
        left_on = self.on_line(left_val)
        right_on = self.on_line(right_val)

        if left_on and right_on:
            action = Motors.ACTION_FORWARD
            speed = config.MOTOR_SPEED
        elif not left_on and right_on:
            action = Motors.ACTION_TURN_LEFT
            speed = config.CORRECTION_SPEED
        elif left_on and not right_on:
            action = Motors.ACTION_TURN_RIGHT
            speed = config.CORRECTION_SPEED
        else:
            if config.LOST_LINE_ACTION == "last_turn":
                action = self._last_action
            else:
                action = Motors.ACTION_FORWARD
            speed = config.CORRECTION_SPEED

        self._last_action = action
        self._motors.apply(action, speed)
        return action, left_val, right_val

    def cleanup(self):
        self._motors.stop()
        self._ir_left.close()
        self._ir_right.close()
