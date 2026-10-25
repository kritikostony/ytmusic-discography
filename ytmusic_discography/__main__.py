"""Entry point: python -m ytmusic_discography."""
import argparse
import logging
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

from ytmusicapi import YTMusic

from . import artists, resolve, tracks

log = logging.getLogger("ytmusic_discography")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="ytmusic-discography")
    p.add_argument("--artists-file", type=Path,
                   default=Path(os.environ.get("ARTISTS_FILE", "/input/artists.txt")))
    p.add_argument("--artist", help="only process this artist (exact name from the list)")
    p.add_argument("--dry-run", action="store_true",
                   help="resolve artists and list releases; download nothing")
    p.add_argument("--request-delay", type=float,
                   default=float(os.environ.get("REQUEST_DELAY", "1.5")),
                   help="average seconds between YouTube Music requests (±50%% jitter)")
    p.add_argument("--location", default=os.environ.get("YTM_LOCATION") or None,
                   help="YouTube Music region, e.g. GR")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        stream=sys.stdout)
    if not args.dry_run:
        log.error("downloading is not implemented yet; use --dry-run")
        return 2

    entries = artists.load(args.artists_file)
    if args.artist:
        entries = [e for e in entries if e.name.casefold() == args.artist.casefold()]
        if not entries:
            log.error("artist %r not found in %s", args.artist, args.artists_file)
            return 2

    def pause() -> None:
        time.sleep(random.uniform(0.5, 1.5) * args.request_delay)

    yt = YTMusic(language="en", location=args.location) if args.location else YTMusic(language="en")
    failed = 0
    skipped: list[str] = []
    for entry in entries:
        log.info("ARTIST %s (line %d)", entry.name, entry.line_no)
        try:
            ra = resolve.resolve(yt, entry, pause)
            if not ra:
                log.warning("  UNRESOLVED: no YouTube Music artist found")
                failed += 1
                continue
            log.info("  via=%s name=%s browseId=%s", ra.via, ra.name, ra.browse_id)
            for section, rel in resolve.list_releases(yt, ra.page, pause):
                album = yt.get_album(rel["browseId"])
                pause()
                planned = tracks.plan(yt, album, ra.name, pause)
                counts = Counter(p.status for p in planned)
                log.info("  %-7s %s | %s | type=%s | tracks=%d %s | playlist=%s",
                         section, album.get("year"), album.get("title"), album.get("type"),
                         len(planned), dict(counts), album.get("audioPlaylistId"))
                for p in planned:
                    if p.status == "replaced":
                        log.info("    %s. %s -> audio %s (was %s)", p.number, p.title, p.video_id, p.reason)
                    elif p.status == "skipped":
                        log.warning("    %s. %s SKIPPED: %s", p.number, p.title, p.reason)
                        skipped.append(f"{entry.name} / {album.get('title')} / {p.number}. {p.title}: {p.reason}")
        except Exception:
            log.exception("  FAILED")
            failed += 1
    if skipped:
        log.warning("skipped tracks (%d):", len(skipped))
        for line in skipped:
            log.warning("  %s", line)
    log.info("done: %d artists, %d failed, %d tracks skipped", len(entries), failed, len(skipped))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
