"""Filesystem-safe names for the staging layout <Artist>/<Album> (<Year>)/<NN> - <Title>.<ext>."""
import re
import unicodedata

_BAD = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')
MAX_BYTES = 200  # ZFS/ext4 allow 255 bytes per name; leave room for suffixes


def sanitize(name: str) -> str:
    s = _BAD.sub("_", unicodedata.normalize("NFC", name))
    s = " ".join(s.split()).strip(" .")
    if len(s.encode()) > MAX_BYTES:
        s = s.encode()[:MAX_BYTES].decode("utf-8", "ignore").rstrip(" .")
    return s or "_"


def release_dir_name(title: str, year: str | None, release_type: str | None, used: set[str]) -> str:
    """Name for a release folder; adds the release type if the name is already taken this run."""
    base = f"{title} ({year})" if year else title
    name = sanitize(base)
    if name in used:
        name = sanitize(f"{base} [{release_type or 'Release'}]")
    used.add(name)
    return name


def track_file_name(number: int | None, total: int, title: str, ext: str) -> str:
    width = max(2, len(str(total)))
    prefix = f"{number:0{width}d} - " if number else ""
    return sanitize(f"{prefix}{title}") + ext
