"""Pick an audio-only source for each album track; never a music video."""
import logging
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

from ytmusicapi import YTMusic

log = logging.getLogger(__name__)

ATV = "MUSIC_VIDEO_TYPE_ATV"
OMV = "MUSIC_VIDEO_TYPE_OMV"
DURATION_TOLERANCE = 1  # seconds


@dataclass
class PlannedTrack:
    number: int | None
    title: str
    video_id: str | None  # audio-only source to download; None if skipped
    status: str  # "audio", "replaced" (OMV -> ATV), "skipped"
    reason: str = ""


def _norm(title: str) -> str:
    s = unicodedata.normalize("NFKD", title.casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w]+", " ", s).split())


def titles_match(album_title: str, candidate: str) -> bool:
    """Equal, or the album title only adds a suffix such as "(00s Version)"."""
    a, c = _norm(album_title), _norm(candidate)
    return bool(c) and (a == c or a.startswith(c + " "))


def find_audio(yt: YTMusic, artist_name: str, track: dict, pause: Callable[[], None]) -> dict | None:
    """Search songs for an ATV with a matching title and the same duration (±1 s)."""
    want = track.get("duration_seconds")
    if want is None:
        return None
    results = yt.search(f"{artist_name} {track['title']}", filter="songs", limit=5)
    pause()
    for r in results:
        if r.get("videoType") != ATV or r.get("duration_seconds") is None:
            continue
        if abs(r["duration_seconds"] - want) <= DURATION_TOLERANCE and titles_match(track["title"], r.get("title", "")):
            return r
    return None


def plan(yt: YTMusic, album: dict, artist_name: str, pause: Callable[[], None]) -> list[PlannedTrack]:
    planned = []
    for t in album.get("tracks", []):
        num, title, vtype = t.get("trackNumber"), t.get("title", ""), t.get("videoType")
        if t.get("isAvailable") is False or not t.get("videoId"):
            planned.append(PlannedTrack(num, title, None, "skipped", "unavailable"))
        elif vtype == ATV:
            planned.append(PlannedTrack(num, title, t["videoId"], "audio"))
        elif (match := find_audio(yt, artist_name, t, pause)):
            planned.append(PlannedTrack(num, title, match["videoId"], "replaced", f"{vtype} {t['videoId']}"))
        else:
            planned.append(PlannedTrack(num, title, None, "skipped", f"{vtype} with no matching audio-only version"))
    return planned
