"""Write tags and cover art in place; audio is never re-encoded."""
import base64
from dataclasses import dataclass
from pathlib import Path

from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus


@dataclass
class TrackTags:
    title: str
    artist: str
    album_artist: str
    album: str
    track_number: int | None
    track_total: int
    year: str | None


def _is_png(data: bytes) -> bool:
    return data.startswith(b"\x89PNG")


def write(path: Path, tags: TrackTags, cover: bytes | None) -> None:
    if path.suffix == ".m4a":
        f = MP4(path)
        f["\xa9nam"] = [tags.title]
        f["\xa9ART"] = [tags.artist]
        f["aART"] = [tags.album_artist]
        f["\xa9alb"] = [tags.album]
        if tags.track_number:
            f["trkn"] = [(tags.track_number, tags.track_total)]
        if tags.year:
            f["\xa9day"] = [tags.year]
        if cover:
            fmt = MP4Cover.FORMAT_PNG if _is_png(cover) else MP4Cover.FORMAT_JPEG
            f["covr"] = [MP4Cover(cover, imageformat=fmt)]
        f.save()
    elif path.suffix == ".opus":
        f = OggOpus(path)
        f["title"] = tags.title
        f["artist"] = tags.artist
        f["albumartist"] = tags.album_artist
        f["album"] = tags.album
        if tags.track_number:
            f["tracknumber"] = str(tags.track_number)
            f["tracktotal"] = str(tags.track_total)
        if tags.year:
            f["date"] = tags.year
        if cover:
            pic = Picture()
            pic.type = 3  # front cover
            pic.mime = "image/png" if _is_png(cover) else "image/jpeg"
            pic.data = cover
            f["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("ascii")]
        f.save()
    else:
        raise ValueError(f"unsupported container: {path.suffix}")
