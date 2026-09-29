"""Four-wheel motor control via two L298N drivers."""

from gpiozero import OutputDevice, PWMOutputDevice

import config


class _Motor:
    def __init__(self, in1, in2, en):
        self._in1 = OutputDevice(in1)
        self._in2 = OutputDevice(in2)
        self._en = PWMOutputDevice(en, frequency=1000)

    def forward(self, speed):
        self._in1.on()
        self._in2.off()
        self._en.value = speed

    def backward(self, speed):
        self._in1.off()
        self._in2.on()
        self._en.value = speed

    def stop(self):
        self._in1.off()
        self._in2.off()
        self._en.value = 0

    def close(self):
        self.stop()
        self._in1.close()
        self._in2.close()
        self._en.close()


class Motors:
    ACTION_FORWARD = "forward"
    ACTION_BACKWARD = "backward"
    ACTION_TURN_LEFT = "turn_left"
    ACTION_TURN_RIGHT = "turn_right"
    ACTION_STOP = "stop"

    def __init__(self):
        self._back_left = _Motor(**config.BACK_LEFT)
        self._back_right = _Motor(**config.BACK_RIGHT)
        self._front_left = _Motor(**config.FRONT_LEFT)
        self._front_right = _Motor(**config.FRONT_RIGHT)

    def forward(self, speed=None):
        speed = config.MOTOR_SPEED if speed is None else speed
        for motor in self._all_motors():
            motor.forward(speed)

    def backward(self, speed=None):
        speed = config.MOTOR_SPEED if speed is None else speed
        for motor in self._all_motors():
            motor.backward(speed)

    def turn_left(self, speed=None):
        speed = config.TURN_SPEED if speed is None else speed
        for motor in self._left_motors():
            motor.backward(speed)
        for motor in self._right_motors():
            motor.forward(speed)

    def turn_right(self, speed=None):
        speed = config.TURN_SPEED if speed is None else speed
        for motor in self._left_motors():
            motor.forward(speed)
        for motor in self._right_motors():
            motor.backward(speed)

    def stop(self):
        for motor in self._all_motors():
            motor.stop()

    def apply(self, action, speed=None):
        if action == self.ACTION_FORWARD:
            self.forward(speed)
        elif action == self.ACTION_BACKWARD:
            self.backward(speed)
        elif action == self.ACTION_TURN_LEFT:
            self.turn_left(speed)
        elif action == self.ACTION_TURN_RIGHT:
            self.turn_right(speed)
        elif action == self.ACTION_STOP:
            self.stop()
        else:
            raise ValueError(f"Unknown motor action: {action}")

    def turn_180(self, direction="left", duration=None):
        import time

        duration = config.TURN_DURATION_SEC if duration is None else duration
        if direction == "left":
            self.turn_left()
        else:
            self.turn_right()
        time.sleep(duration)
        self.stop()

    def cleanup(self):
        self.stop()
        for motor in self._all_motors():
            motor.close()

    def _all_motors(self):
        return (
            self._back_left,
            self._back_right,
            self._front_left,
            self._front_right,
        )

    def _left_motors(self):
        return self._back_left, self._front_left

    def _right_motors(self):
        return self._back_right, self._front_right
