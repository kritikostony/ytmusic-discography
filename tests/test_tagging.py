import shutil
import subprocess

import pytest
from mutagen.mp4 import MP4
from mutagen.oggopus import OggOpus

from ytmusic_discography import tagging

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")

TAGS = tagging.TrackTags(title="Katamata", artist="Thodoris Ferris", album_artist="Θοδωρής Φέρρης",
                         album="Oso Tha Gyrizei I Gi", track_number=2, track_total=11, year="2026")
JPEG = b"\xff\xd8\xff\xe0fakejpeg"


def _make(path, codec):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "1", "-c:a", codec, str(path)], check=True)


def test_m4a(tmp_path):
    p = tmp_path / "t.m4a"
    _make(p, "aac")
    tagging.write(p, TAGS, JPEG)
    f = MP4(p)
    assert f["\xa9nam"] == ["Katamata"]
    assert f["aART"] == ["Θοδωρής Φέρρης"]
    assert f["trkn"] == [(2, 11)]
    assert f["\xa9day"] == ["2026"]
    assert bytes(f["covr"][0]) == JPEG


def test_opus(tmp_path):
    p = tmp_path / "t.opus"
    _make(p, "libopus")
    tagging.write(p, TAGS, JPEG)
    f = OggOpus(p)
    assert f["albumartist"] == ["Θοδωρής Φέρρης"]
    assert f["tracknumber"] == ["2"] and f["tracktotal"] == ["11"]
    assert "metadata_block_picture" in f


def test_unsupported(tmp_path):
    with pytest.raises(ValueError):
        tagging.write(tmp_path / "t.webm", TAGS, None)
