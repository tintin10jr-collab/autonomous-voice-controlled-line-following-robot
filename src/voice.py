"""Offline speech recognition using Vosk."""

import json
import queue
import threading
import time
from pathlib import Path

import config

try:
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model
except ImportError as exc:
    raise ImportError(
        "voice module requires sounddevice and vosk. "
        "Install with: pip install -r requirements.txt"
    ) from exc


class VoiceListener:
    def __init__(self, command_queue=None):
        self.command_queue = command_queue or queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self._model = None
        self._recognizer = None
        self._last_command_time = 0.0

    def start(self):
        model_path = Path(config.VOSK_MODEL_PATH)
        if not model_path.is_dir():
            raise FileNotFoundError(
                f"Vosk model not found at {model_path}. "
                "Download vosk-model-small-en-us-0.15 into the models/ folder."
            )

        self._model = Model(str(model_path))
        self._recognizer = KaldiRecognizer(self._model, config.SAMPLE_RATE)
        self._recognizer.SetWords(False)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _listen_loop(self):
        with sd.RawInputStream(
            samplerate=config.SAMPLE_RATE,
            blocksize=config.AUDIO_BLOCK_SIZE,
            dtype="int16",
            channels=1,
        ) as stream:
            while not self._stop_event.is_set():
                data, _overflowed = stream.read(config.AUDIO_BLOCK_SIZE)
                if self._recognizer.AcceptWaveform(bytes(data)):
                    self._handle_result(self._recognizer.Result())
                else:
                    partial = json.loads(self._recognizer.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        print(f"[voice] ... {partial_text}")

    def _handle_result(self, result_json):
        result = json.loads(result_json)
        text = result.get("text", "").lower()
        if text:
            print(f"[voice] Heard: {text!r}")
            self._check_keywords(text)

    def _check_keywords(self, text):
        now = time.monotonic()
        if now - self._last_command_time < config.COMMAND_COOLDOWN_SEC:
            return

        for keyword in config.VOICE_KEYWORDS:
            if keyword in text:
                self._last_command_time = now
                self._enqueue_command(keyword, text)
                return

    def _enqueue_command(self, keyword, text):
        try:
            self.command_queue.put_nowait(keyword)
            print(f"[voice] Detected command: {keyword!r} (heard: {text!r})")
        except queue.Full:
            pass

    def wait_for_command(self, timeout=None):
        return self.command_queue.get(timeout=timeout)
