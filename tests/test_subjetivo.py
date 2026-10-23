import json
from pathlib import Path

import pytest

from subjetivo.cli import run
from subjetivo.links import Track, search_links
from subjetivo.notifier import save_history
from subjetivo.recognizer import RecognitionError, parse_response

SAMPLE = {
    "status": "success",
    "result": {
        "artist": "Tim Maia", "title": "Azul da Cor do Mar", "album": "Tim Maia",
        "release_date": "1970-01-01", "song_link": "https://lis.tn/xyz",
        "spotify": {"external_urls": {"spotify": "https://open.spotify.com/track/1"}},
        "apple_music": {"url": "https://music.apple.com/x"},
    },
}


def test_parse_success_prefers_direct_links():
    t = parse_response(SAMPLE)
    assert t.title == "Azul da Cor do Mar"
    assert t.links["Spotify"] == "https://open.spotify.com/track/1"
    assert t.links["Todas as plataformas"] == "https://lis.tn/xyz"
    assert "youtube.com" in t.links["YouTube"]  # busca como fallback


def test_parse_no_match():
    assert parse_response({"status": "success", "result": None}) is None


def test_parse_error():
    with pytest.raises(RecognitionError):
        parse_response({"status": "error", "error": {"error_message": "token inválido"}})


def test_search_links_encode():
    assert "Beyonc%C3%A9" in search_links("Beyoncé", "Halo")["Spotify"]


def test_history(tmp_path):
    f = tmp_path / "h.jsonl"
    save_history(Track("A", "B", links={"x": "y"}), f)
    assert json.loads(f.read_text())["title"] == "A"



def test_run_dedupes_consecutive_same_track(tmp_path, capsys):
    clip = tmp_path / "clip.wav"

    class Rec:
        def record(self, s):
            clip.write_bytes(b"x")
            return clip

    results = iter([parse_response(SAMPLE), parse_response(SAMPLE), None])

    class Reco:
        def recognize(self, p):
            return next(results)

    calls = {"n": 0}

    def sleep(_):
        calls["n"] += 1
        if calls["n"] == 3:
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        run(Rec(), Reco(), seconds=1, pause=0, history=tmp_path / "h.jsonl", once=False, sleep=sleep)

    out = capsys.readouterr().out
    assert out.count("Azul da Cor do Mar") == 1  # notificou só uma vez
    assert len((tmp_path / "h.jsonl").read_text().splitlines()) == 1
    assert not clip.exists()  # clipe temporário removido
