"""Saída: terminal, notificação Android e histórico em arquivo."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from .links import Track


def format_track(track: Track) -> str:
    lines = [f"♪ {track.artist} - {track.title}"]
    if track.album:
        lines.append(f"  Álbum: {track.album}")
    lines += [f"  {name}: {url}" for name, url in track.links.items()]
    return "\n".join(lines)


def notify(track: Track) -> None:
    print(format_track(track), flush=True)
    if shutil.which("termux-notification"):
        link = track.links.get("Todas as plataformas") or track.links["YouTube"]
        subprocess.run(
            [
                "termux-notification",
                "--title", f"♪ {track.title}",
                "--content", f"{track.artist} · toque para abrir",
                "--action", f"termux-open-url '{link}'",
            ],
            capture_output=True,
        )


def save_history(track: Track, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "artist": track.artist,
        "title": track.title,
        "album": track.album,
        "links": track.links,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
