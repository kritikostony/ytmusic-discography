"""Entry point: python -m ytmusic_discography."""
import argparse
import logging
import os
import posixpath
import random
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

from ytmusicapi import YTMusic

from . import artists, lidarr, paths, resolve, tagging, tracks
from .archive import Archive

log = logging.getLogger("ytmusic_discography")

EXIT_FAILURES = 1
EXIT_USAGE = 2
EXIT_BLOCKED = 3


def parse_args(argv: list[str]) -> argparse.Namespace:
    env = os.environ.get
    p = argparse.ArgumentParser(prog="ytmusic-discography")
    p.add_argument("--artists-file", type=Path, default=Path(env("ARTISTS_FILE", "/input/artists.txt")))
    p.add_argument("--cookies", type=Path, default=Path(env("COOKIES_FILE", "/input/cookies.txt")))
    p.add_argument("--dest", type=Path, default=Path(env("DEST", "/output")))
    p.add_argument("--artist", help="only process this artist (exact name from the list)")
    p.add_argument("--release", help="only process releases with this exact title (use with --artist)")
    p.add_argument("--dry-run", action="store_true",
                   help="resolve artists and list releases; download nothing")
    p.add_argument("--request-delay", type=float, default=float(env("REQUEST_DELAY", "1.5")),
                   help="average seconds between YouTube Music API requests (±50%% jitter)")
    p.add_argument("--track-delay", type=float, default=float(env("TRACK_DELAY", "7")),
                   help="average seconds between track downloads (±50%% jitter)")
    p.add_argument("--release-delay", type=float, default=float(env("RELEASE_DELAY", "30")),
                   help="average seconds between releases that downloaded something (±50%% jitter)")
    p.add_argument("--location", default=env("YTM_LOCATION") or None, help="YouTube Music region, e.g. GR")
    return p.parse_args(argv)


def jitter_sleep(avg: float) -> None:
    time.sleep(random.uniform(0.5, 1.5) * avg)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        stream=sys.stdout)

    entries = artists.load(args.artists_file)
    if args.artist:
        entries = [e for e in entries if e.name.casefold() == args.artist.casefold()]
        if not entries:
            log.error("artist %r not found in %s", args.artist, args.artists_file)
            return EXIT_USAGE

    lidarr_url, lidarr_key = os.environ.get("LIDARR_URL"), os.environ.get("LIDARR_API_KEY")
    lidarr_path = os.environ.get("LIDARR_STAGING_PATH")
    use_lidarr = bool(lidarr_url and lidarr_key and not args.dry_run)
    if use_lidarr and not lidarr_path:
        log.error("LIDARR_STAGING_PATH is required when LIDARR_URL and LIDARR_API_KEY are set")
        return EXIT_USAGE

    downloader = None
    if not args.dry_run:
        if not args.cookies.is_file() or args.cookies.stat().st_size == 0:
            log.error("cookies file missing or empty: %s", args.cookies)
            return EXIT_USAGE
        if not args.dest.is_dir():
            log.error("destination is not a directory: %s", args.dest)
            return EXIT_USAGE
        # Imported lazily so --dry-run works without yt-dlp/ffmpeg installed.
        from . import download
        tmp_dir = args.dest / ".tmp"
        shutil.rmtree(tmp_dir, ignore_errors=True)  # leftovers from an interrupted run
        tmp_dir.mkdir()
        archive = Archive(args.dest / ".archive.txt")
        downloader = download.Downloader(args.cookies, tmp_dir)
        downloader.__enter__()
        log.info("lidarr hand-off: %s", "on" if use_lidarr else "off")

    def pause() -> None:
        jitter_sleep(args.request_delay)

    yt = YTMusic(language="en", location=args.location) if args.location else YTMusic(language="en")
    failed, skipped, errors = 0, [], []
    try:
        for entry in entries:
            log.info("ARTIST %s (line %d)", entry.name, entry.line_no)
            try:
                ra = resolve.resolve(yt, entry, pause)
                if not ra:
                    log.warning("  UNRESOLVED: no YouTube Music artist found")
                    failed += 1
                    continue
                log.info("  via=%s name=%s browseId=%s", ra.via, ra.name, ra.browse_id)
                artist_dir = paths.sanitize(entry.name)
                used_dirs: set[str] = set()
                new_files = 0
                for section, rel in resolve.list_releases(yt, ra.page, pause):
                    if args.release and rel.get("title", "").casefold() != args.release.casefold():
                        continue
                    release_id = rel["browseId"]
                    album = yt.get_album(release_id)
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
                    if args.dry_run:
                        continue

                    release_dir = args.dest / artist_dir / paths.release_dir_name(
                        album.get("title", ""), album.get("year"), album.get("type"), used_dirs)
                    pending = [p for p in planned if p.video_id and not archive.has(release_id, p.video_id)]
                    if not pending:
                        continue
                    cover = download.fetch_cover(album)
                    track_artists = {t.get("trackNumber"): ", ".join(a["name"] for a in t.get("artists") or [])
                                     for t in album.get("tracks", [])}
                    for p in pending:
                        try:
                            tmp = downloader.fetch(p.video_id)
                        except download.FormatUnavailable:
                            log.warning("    %s. %s SKIPPED: none of formats %s", p.number, p.title, download.FORMAT)
                            skipped.append(f"{entry.name} / {album.get('title')} / {p.number}. {p.title}: no allowed format")
                            continue
                        tagging.write(tmp, tagging.TrackTags(
                            title=p.title,
                            artist=track_artists.get(p.number) or entry.name,
                            album_artist=entry.name,
                            album=album.get("title", ""),
                            track_number=p.number,
                            track_total=len(planned),
                            year=album.get("year"),
                        ), cover)
                        final = release_dir / paths.track_file_name(p.number, len(planned), p.title, tmp.suffix)
                        release_dir.mkdir(parents=True, exist_ok=True)
                        tmp.replace(final)
                        archive.add(release_id, p.video_id)
                        new_files += 1
                        log.info("    %s. %s -> %s", p.number, p.title, final.name)
                        jitter_sleep(args.track_delay)
                    jitter_sleep(args.release_delay)

                if use_lidarr and new_files:
                    target = posixpath.join(lidarr_path, artist_dir)
                    cmd_id = lidarr.scan(lidarr_url, lidarr_key, target)
                    log.info("  lidarr: DownloadedAlbumsScan %s queued (command %d)", target, cmd_id)
            except Exception as e:
                if downloader and isinstance(e, download.Blocked):
                    raise
                log.exception("  FAILED")
                errors.append(entry.name)
                failed += 1
    except Exception as e:
        if downloader and isinstance(e, download.Blocked):
            log.error("STOPPED: YouTube is blocking or rate-limiting this account: %s", e)
            return EXIT_BLOCKED
        raise
    finally:
        if downloader:
            downloader.__exit__(None, None, None)

    if skipped:
        log.warning("skipped tracks (%d):", len(skipped))
        for line in skipped:
            log.warning("  %s", line)
    if errors:
        log.warning("failed artists: %s", ", ".join(errors))
    log.info("done: %d artists, %d failed, %d tracks skipped", len(entries), failed, len(skipped))
    return EXIT_FAILURES if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
