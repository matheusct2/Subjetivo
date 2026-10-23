"""Montagem dos links de uma música reconhecida."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus


@dataclass
class Track:
    title: str
    artist: str
    album: str = ""
    release_date: str = ""
    links: dict[str, str] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.artist}|{self.title}".casefold()

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"


def search_links(artist: str, title: str) -> dict[str, str]:
    """Links de busca que sempre funcionam, mesmo sem a API devolver links diretos."""
    q = quote_plus(f"{artist} {title}")
    return {
        "YouTube": f"https://www.youtube.com/results?search_query={q}",
        "YouTube Music": f"https://music.youtube.com/search?q={q}",
        "Spotify": f"https://open.spotify.com/search/{q}",
        "Deezer": f"https://www.deezer.com/search/{q}",
        "Apple Music": f"https://music.apple.com/br/search?term={q}",
    }


def merge_links(artist: str, title: str, direct: dict[str, str]) -> dict[str, str]:
    """Links diretos têm prioridade sobre os de busca."""
    merged = search_links(artist, title)
    merged.update({k: v for k, v in direct.items() if v})
    return merged
