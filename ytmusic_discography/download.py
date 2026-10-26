"""yt-dlp wrapper: audio-only formats, Premium cookies from a private temporary copy."""
import logging
import os
import re
import shutil
import tempfile
import urllib.request
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

log = logging.getLogger(__name__)

FORMAT = "141/774/251"  # AAC 256k (Premium) -> Opus 256k (Premium) -> Opus ~145k; never bestaudio
_BLOCKED = ("Sign in to confirm", "HTTP Error 429")


class Blocked(Exception):
    """YouTube is rate-limiting or bot-checking this account; stop the whole run."""


class CookiesInvalid(Exception):
    """YouTube rejected the cookies; continuing would silently drop to non-Premium formats."""


class FormatUnavailable(Exception):
    pass


class _Logger:
    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        if "cookies are no longer valid" in msg:
            # Raised from inside yt-dlp before the download starts, so nothing is fetched.
            raise CookiesInvalid(msg)
        log.warning("yt-dlp: %s", msg)

    def error(self, msg: str) -> None:
        log.error("yt-dlp: %s", msg)


class Downloader:
    """Use as a context manager. The cookies file is copied (yt-dlp writes cookies back) and the copy is deleted on exit."""

    def __init__(self, cookies: Path, tmp_dir: Path):
        self._cookies = cookies
        self._tmp_dir = tmp_dir

    def __enter__(self) -> "Downloader":
        self._private = Path(tempfile.mkdtemp(prefix="ytmd-"))
        os.chmod(self._private, 0o700)
        cookie_copy = self._private / "cookies.txt"
        shutil.copyfile(self._cookies, cookie_copy)
        os.chmod(cookie_copy, 0o600)
        self._ydl = YoutubeDL({
            "format": FORMAT,
            "cookiefile": str(cookie_copy),
            "outtmpl": str(self._tmp_dir / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "cachedir": False,
            "quiet": True,
            "noprogress": True,
            "logger": _Logger(),
            "retries": 10,
            "fragment_retries": 20,
            "retry_sleep_functions": {"fragment": lambda n: 1},
            # 141 arrives as DASH m4a and is fixed up by ffmpeg automatically; webm -> .opus is a remux, not a re-encode
            "postprocessors": [{"key": "FFmpegVideoRemuxer", "preferedformat": "webm>opus"}],
        })
        self._ydl.__enter__()
        return self

    def __exit__(self, *exc) -> None:
        try:
            self._ydl.__exit__(*exc)
        finally:
            shutil.rmtree(self._private, ignore_errors=True)

    def fetch(self, video_id: str) -> Path:
        try:
            info = self._ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        except DownloadError as e:
            msg = str(e)
            if any(b in msg for b in _BLOCKED):
                raise Blocked(msg) from e
            if "Requested format is not available" in msg:
                raise FormatUnavailable(msg) from e
            raise
        return Path(info["requested_downloads"][0]["filepath"])


def fetch_cover(album: dict) -> bytes | None:
    thumbs = album.get("thumbnails") or []
    if not thumbs:
        return None
    url = max(thumbs, key=lambda t: t.get("width", 0))["url"]
    url = re.sub(r"=w\d+-h\d+", "=w1200-h1200", url)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read()
    except OSError as e:
        log.warning("  cover download failed: %s", e)
        return None
