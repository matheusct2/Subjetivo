"""Captura de trechos de áudio do microfone."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
import wave
from pathlib import Path


class RecordingError(Exception):
    pass


class TermuxRecorder:
    """Android (Termux + app Termux:API): termux-microphone-record."""

    suffix = ".m4a"

    @staticmethod
    def available() -> bool:
        return shutil.which("termux-microphone-record") is not None

    def record(self, seconds: int) -> Path:
        out = Path(tempfile.mkdtemp()) / f"clip{self.suffix}"
        subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
        res = subprocess.run(
            ["termux-microphone-record", "-f", str(out), "-l", str(seconds), "-e", "aac"],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            raise RecordingError(res.stderr.strip() or "falha ao iniciar a gravação")
        time.sleep(seconds + 1)
        subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
        if not out.exists() or out.stat().st_size == 0:
            raise RecordingError("gravação vazia (permissão de microfone concedida?)")
        return out


class SoundDeviceRecorder:
    """Desktop: usa o pacote opcional `sounddevice`."""

    suffix = ".wav"
    rate = 44100

    @staticmethod
    def available() -> bool:
        try:
            import sounddevice  # noqa: F401
        except (ImportError, OSError):
            return False
        return True

    def record(self, seconds: int) -> Path:
        import sounddevice as sd

        frames = sd.rec(int(seconds * self.rate), samplerate=self.rate, channels=1, dtype="int16")
        sd.wait()
        out = Path(tempfile.mkdtemp()) / f"clip{self.suffix}"
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.rate)
            w.writeframes(frames.tobytes())
        return out


def pick_recorder():
    for cls in (TermuxRecorder, SoundDeviceRecorder):
        if cls.available():
            return cls()
    raise RecordingError(
        "Nenhum gravador disponível. No Android instale `pkg install termux-api` "
        "(e o app Termux:API); no desktop `pip install sounddevice`."
    )
