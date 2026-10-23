"""Identificação de música via API AudD (https://audd.io)."""

from __future__ import annotations

import json
import mimetypes
import os
import uuid
import urllib.request
from pathlib import Path

from .links import Track, merge_links

AUDD_URL = "https://api.audd.io/"


class RecognitionError(Exception):
    pass


def _multipart(fields: dict[str, str], file_field: str, path: Path) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
        )
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
            f'filename="{path.name}"\r\nContent-Type: {ctype}\r\n\r\n'
        ).encode()
        + path.read_bytes()
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def parse_response(data: dict) -> Track | None:
    """Converte a resposta da AudD em Track. Retorna None se não houve correspondência."""
    if data.get("status") != "success":
        err = (data.get("error") or {}).get("error_message", "erro desconhecido")
        raise RecognitionError(f"AudD: {err}")
    r = data.get("result")
    if not r:
        return None

    direct = {"Todas as plataformas": r.get("song_link", "")}
    spotify = r.get("spotify") or {}
    direct["Spotify"] = (spotify.get("external_urls") or {}).get("spotify", "")
    direct["Apple Music"] = (r.get("apple_music") or {}).get("url", "")
    deezer = r.get("deezer") or {}
    direct["Deezer"] = deezer.get("link", "")

    artist, title = r.get("artist", ""), r.get("title", "")
    return Track(
        title=title,
        artist=artist,
        album=r.get("album", "") or "",
        release_date=r.get("release_date", "") or "",
        links=merge_links(artist, title, direct),
    )


class AuddRecognizer:
    def __init__(self, api_token: str | None = None, timeout: int = 30):
        self.api_token = api_token or os.environ.get("AUDD_API_TOKEN", "")
        self.timeout = timeout
        if not self.api_token:
            raise RecognitionError(
                "Defina AUDD_API_TOKEN (token gratuito em https://dashboard.audd.io)."
            )

    def recognize(self, audio_path: Path) -> Track | None:
        body, ctype = _multipart(
            {"api_token": self.api_token, "return": "spotify,apple_music,deezer"},
            "file",
            Path(audio_path),
        )
        req = urllib.request.Request(AUDD_URL, data=body, headers={"Content-Type": ctype})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return parse_response(json.load(resp))
        except OSError as exc:
            raise RecognitionError(f"Falha de rede: {exc}") from exc
