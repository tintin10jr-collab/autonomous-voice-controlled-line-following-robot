"""IR sensor test — place robot on black tape vs white floor and note values."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gpiozero import DigitalInputDevice

import config


def main():
    ir_left = DigitalInputDevice(config.IR_LEFT, pull_up=True)
    ir_right = DigitalInputDevice(config.IR_RIGHT, pull_up=True)

    print("IR sensor test (Ctrl+C to stop)")
    print(f"Current IR_ON_BLACK setting in config: {config.IR_ON_BLACK}")
    print("Place sensors on BLACK tape, then WHITE surface, and compare values.\n")

    try:
        while True:
            left = ir_left.value
            right = ir_right.value
            left_status = "ON LINE" if left == config.IR_ON_BLACK else "OFF LINE"
            right_status = "ON LINE" if right == config.IR_ON_BLACK else "OFF LINE"
            print(f"Left: {left} ({left_status})  |  Right: {right} ({right_status})")
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        ir_left.close()
        ir_right.close()
        print("\nDone. Update IR_ON_BLACK in config.py to match the value on black tape.")


if __name__ == "__main__":
    main()
