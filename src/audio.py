"""MP3 playback through the Pi default audio output (e.g. Bluetooth speaker)."""

import subprocess
import sys
from pathlib import Path

try:
    import pygame
except ImportError as exc:
    raise ImportError(
        "audio module requires pygame. Install with: pip install pygame"
    ) from exc


def play_mp3(path, use_mpg123_fallback=True):
    """Play an MP3 file and block until playback finishes."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Sound file not found: {file_path}")

    try:
        _play_with_pygame(file_path)
    except Exception as exc:
        if not use_mpg123_fallback:
            raise
        print(f"[audio] pygame failed ({exc}), trying mpg123...")
        _play_with_mpg123(file_path)


def _play_with_pygame(file_path):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(str(file_path))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    pygame.mixer.music.unload()


def _play_with_mpg123(file_path):
    result = subprocess.run(
        ["mpg123", "-q", str(file_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"mpg123 failed: {result.stderr.strip() or result.stdout.strip()}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audio.py <path-to-mp3>")
        sys.exit(1)
    play_mp3(sys.argv[1])
