"""Voice recognition test — prints live transcripts from the USB mic."""

import queue
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from voice import VoiceListener


def main():
    listener = VoiceListener()
    print("Voice test — say 'canteen' or 'gate' (Ctrl+C to stop)")
    print(f"Keywords: {config.VOICE_KEYWORDS}\n")

    try:
        listener.start()
        while True:
            try:
                cmd = listener.wait_for_command(timeout=0.5)
                print(f">>> Command detected: {cmd!r}")
            except queue.Empty:
                pass
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        print("\nVoice listener stopped.")


if __name__ == "__main__":
    main()
