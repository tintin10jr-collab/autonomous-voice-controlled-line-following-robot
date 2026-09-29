"""Main state machine: listen → line-follow → 180° turn → play sound → idle."""

import queue
import signal
import time

import config
from audio import play_mp3
from line_follower import LineFollower
from motors import Motors
from voice import VoiceListener


class Robot:
    def __init__(self):
        self.motors = Motors()
        self.line_follower = LineFollower(motors=self.motors)
        self.voice = VoiceListener()
        self._running = True

    def run(self):
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        print("Robot ready. Say 'canteen' or 'gate'. Ctrl+C to quit.")
        self.voice.start()

        try:
            while self._running:
                try:
                    command = self.voice.wait_for_command(timeout=0.5)
                except queue.Empty:
                    continue
                self._execute_mission(command)
        finally:
            self.shutdown()

    def _execute_mission(self, command):
        print(f"\n[robot] Starting mission: {command}")
        self._navigate_with_line_follow()
        self.motors.turn_180(direction="left")
        self._play_destination_sound(command)
        print(f"[robot] Mission complete: {command}\n")

    def _navigate_with_line_follow(self):
        deadline = time.monotonic() + config.MOVE_DURATION_SEC
        while time.monotonic() < deadline and self._running:
            self.line_follower.step()
            time.sleep(config.LINE_FOLLOW_INTERVAL)
        self.motors.stop()

    def _play_destination_sound(self, command):
        sound_path = config.SOUNDS.get(command)
        if not sound_path:
            print(f"[robot] No sound configured for command: {command}")
            return
        print(f"[robot] Playing sound: {sound_path}")
        play_mp3(sound_path)

    def _handle_shutdown(self, signum, frame):
        print("\n[robot] Shutting down...")
        self._running = False

    def shutdown(self):
        self.motors.stop()
        self.line_follower.cleanup()
        self.voice.stop()
        self.motors.cleanup()


def main():
    robot = Robot()
    robot.run()


if __name__ == "__main__":
    main()
