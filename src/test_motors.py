"""Interactive motor test — run on the Raspberry Pi with GPIO wired."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motors import Motors


def run_sequence():
    motors = Motors()
    tests = [
        ("Forward", lambda: motors.forward(), 2),
        ("Backward", lambda: motors.backward(), 2),
        ("Turn left", lambda: motors.turn_left(), 2),
        ("Turn right", lambda: motors.turn_right(), 2),
    ]

    print("Motor test starting in 2 seconds. Ctrl+C to abort.")
    time.sleep(2)

    try:
        for name, action, duration in tests:
            print(f"  {name} for {duration}s...")
            action()
            time.sleep(duration)
            motors.stop()
            time.sleep(0.5)
    finally:
        motors.cleanup()
        print("Motors stopped and GPIO cleaned up.")


def interactive_menu():
    motors = Motors()
    actions = {
        "1": ("Forward", motors.forward),
        "2": ("Backward", motors.backward),
        "3": ("Turn left", motors.turn_left),
        "4": ("Turn right", motors.turn_right),
        "5": ("Stop", motors.stop),
        "6": ("180 turn left", lambda: motors.turn_180("left")),
        "7": ("180 turn right", lambda: motors.turn_180("right")),
    }

    print("Motor test menu:")
    for key, (label, _) in actions.items():
        print(f"  {key}. {label}")
    print("  q. Quit")

    try:
        while True:
            choice = input("\nSelect action: ").strip().lower()
            if choice == "q":
                break
            if choice not in actions:
                print("Invalid choice.")
                continue
            label, action = actions[choice]
            print(f"Running: {label}")
            action()
            if choice in {"1", "2", "3", "4"}:
                input("Press Enter to stop...")
                motors.stop()
    except KeyboardInterrupt:
        pass
    finally:
        motors.cleanup()
        print("Motors stopped and GPIO cleaned up.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sequence":
        run_sequence()
    else:
        interactive_menu()
