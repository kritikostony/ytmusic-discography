import json

from ytmusic_discography import lidarr, paths
from ytmusic_discography.archive import Archive


def test_sanitize_keeps_greek_and_replaces_unsafe():
    assert paths.sanitize("Θοδωρής Φέρρης") == "Θοδωρής Φέρρης"
    assert paths.sanitize('AC/DC: "Live"?') == "AC_DC_ _Live__"
    assert paths.sanitize("  ..hidden.  ") == "hidden"
    assert paths.sanitize("///") == "___"
    assert paths.sanitize("") == "_"


def test_sanitize_byte_limit_does_not_split_characters():
    s = paths.sanitize("Ω" * 300)  # 2 bytes each
    assert len(s.encode()) <= paths.MAX_BYTES
    s.encode().decode()  # still valid UTF-8


def test_release_dir_name_collision():
    used = set()
    assert paths.release_dir_name("Eipes", "2025", "Album", used) == "Eipes (2025)"
    assert paths.release_dir_name("Eipes", "2025", "Single", used) == "Eipes (2025) [Single]"
    assert paths.release_dir_name("NoYear", None, "EP", used) == "NoYear"


def test_track_file_name():
    assert paths.track_file_name(3, 11, "Katamata", ".m4a") == "03 - Katamata.m4a"
    assert paths.track_file_name(7, 120, "X/Y", ".opus") == "007 - X_Y.opus"


def test_archive_roundtrip(tmp_path):
    a = Archive(tmp_path / ".archive.txt")
    assert not a.has("MPREb_1", "vid")
    a.add("MPREb_1", "vid")
    b = Archive(tmp_path / ".archive.txt")
    assert b.has("MPREb_1", "vid")
    assert not b.has("MPREb_2", "vid")  # same song on another release is fetched again


def test_lidarr_request():
    r = lidarr.scan_request("http://lidarr:8686/", "secret", "/mess/ytmusic/Άννα Βίσση")
    assert r.full_url == "http://lidarr:8686/api/v1/command"
    assert r.get_method() == "POST"
    assert r.headers["X-api-key"] == "secret"
    assert json.loads(r.data) == {"name": "DownloadedAlbumsScan", "path": "/mess/ytmusic/Άννα Βίσση", "importMode": "move"}


def test_invalid_cookies_warning_raises():
    import pytest

    from ytmusic_discography.download import CookiesInvalid, _Logger
    with pytest.raises(CookiesInvalid):
        _Logger().warning("[youtube] The provided YouTube account cookies are no longer valid. They have likely been rotated")
    _Logger().warning("some other warning")  # does not raise
