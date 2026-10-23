"""Linha de comando: `python -m subjetivo`."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .notifier import format_track, notify, save_history
from .recognizer import AuddRecognizer, RecognitionError
from .recorder import RecordingError, pick_recorder


def listen_once(recorder, recognizer, seconds: int):
    clip = recorder.record(seconds)
    try:
        return recognizer.recognize(clip)
    finally:
        clip.unlink(missing_ok=True)


def run(recorder, recognizer, *, seconds: int, pause: int, history: Path, once: bool,
        sleep=time.sleep) -> None:
    last_key = None
    while True:
        try:
            track = listen_once(recorder, recognizer, seconds)
        except (RecordingError, RecognitionError) as exc:
            print(f"[erro] {exc}", file=sys.stderr, flush=True)
            track = None
            if once:
                raise SystemExit(1)
        if track and track.key != last_key:
            last_key = track.key
            notify(track)
            save_history(track, history)
        elif track is None and not once:
            print("[...] nenhuma música reconhecida", flush=True)
        if once:
            if track is None:
                raise SystemExit(2)
            return
        sleep(pause)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="subjetivo", description=__doc__)
    p.add_argument("--seconds", type=int, default=12, help="duração de cada gravação (padrão 12)")
    p.add_argument("--pause", type=int, default=20, help="espera entre ciclos (padrão 20)")
    p.add_argument("--once", action="store_true", help="identifica uma vez e sai")
    p.add_argument("--file", type=Path, help="identifica um arquivo de áudio em vez de gravar")
    p.add_argument("--history", type=Path, default=Path.home() / ".subjetivo" / "historico.jsonl")
    args = p.parse_args(argv)

    try:
        recognizer = AuddRecognizer()
        if args.file:
            track = recognizer.recognize(args.file)
            print(format_track(track) if track else "Nenhuma música reconhecida.")
            raise SystemExit(0 if track else 2)
        recorder = pick_recorder()
    except (RecognitionError, RecordingError) as exc:
        raise SystemExit(f"Erro: {exc}")

    print("Escutando... (Ctrl+C para parar)", flush=True)
    try:
        run(recorder, recognizer, seconds=args.seconds, pause=args.pause,
            history=args.history, once=args.once)
    except KeyboardInterrupt:
        print("\nEncerrado.")
