"""Resolve list entries to YouTube Music artists and list their releases."""
import logging
from collections.abc import Callable
from dataclasses import dataclass

from ytmusicapi import YTMusic

from .artists import ArtistEntry

log = logging.getLogger(__name__)


@dataclass
class ResolvedArtist:
    entry: ArtistEntry
    via: str  # "channel" or "search"
    browse_id: str
    name: str
    page: dict


def resolve(yt: YTMusic, entry: ArtistEntry, pause: Callable[[], None]) -> ResolvedArtist | None:
    for cid in entry.channel_ids:
        try:
            page = yt.get_artist(cid)
        except Exception as e:
            log.info("  channel %s is not a YouTube Music artist page (%s)", cid, type(e).__name__)
            pause()
            continue
        pause()
        return ResolvedArtist(entry, "channel", cid, page.get("name", ""), page)

    results = yt.search(entry.name, filter="artists", limit=1)
    pause()
    if not results:
        return None
    bid = results[0]["browseId"]
    page = yt.get_artist(bid)
    pause()
    return ResolvedArtist(entry, "search", bid, page.get("name", ""), page)


def list_releases(yt: YTMusic, page: dict, pause: Callable[[], None]) -> list[tuple[str, dict]]:
    """Return (section, release) pairs for the Albums and Singles sections only."""
    releases, seen = [], set()
    for section in ("albums", "singles"):
        data = page.get(section)
        if not data:
            continue
        items = data.get("results", [])
        # A "more" link means the page shows only the first few; fetch the full list.
        if data.get("browseId") and data.get("params"):
            items = yt.get_artist_albums(data["browseId"], data["params"], limit=None)
            pause()
        for item in items:
            bid = item.get("browseId")
            if bid and bid not in seen:
                seen.add(bid)
                releases.append((section, item))
    return releases
