"""Parse the artist list: one `Name — URL [URL ...]` per line."""
import re
from dataclasses import dataclass
from pathlib import Path

SEPARATOR = " — "
CHANNEL_ID = re.compile(r"/channel/(UC[\w-]{22})")


@dataclass(frozen=True)
class ArtistEntry:
    name: str
    channel_ids: tuple[str, ...]
    line_no: int


def parse_line(line: str, line_no: int) -> ArtistEntry | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    name, sep, rest = line.partition(SEPARATOR)
    name = name.strip()
    if not sep or not name:
        raise ValueError(f"line {line_no}: expected 'Name — URL', got {line!r}")
    # dict.fromkeys de-duplicates while keeping order
    ids = tuple(dict.fromkeys(CHANNEL_ID.findall(rest)))
    return ArtistEntry(name, ids, line_no)


def load(path: Path) -> list[ArtistEntry]:
    entries = []
    with path.open(encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            entry = parse_line(line, line_no)
            if entry:
                entries.append(entry)
    return entries
