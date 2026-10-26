# ytmusic-discography

Downloads artists' full discographies (albums, EPs and singles) from YouTube Music as tagged audio files, without music videos or Shorts. Writes into a music library as `<Artist>/<Album> (<Year>)/<NN> - <Title>.<ext>`.

> **Disclaimer:** downloading from YouTube violates YouTube's Terms of Service. You are responsible for whether your use is lawful where you live. AAC 256 kbps requires a YouTube Premium account and its session cookies; using them ties all download requests to that Google account, which Google may restrict.

## How it works
1. Reads a list of artists (`Name — URL [URL ...]` per line; `#` comments allowed).
2. Resolves each to a YouTube Music artist page (channel ID from the list, else name search) with `ytmusicapi`.
3. Lists the artist's Albums and Singles. Music-video tracks in a release are swapped for the matching audio-only track (same title, same length ±1 s) or skipped.
4. Downloads each track with `yt-dlp`: format `141` (AAC 256k) → `774` (Opus 256k) → `251` (Opus 145k). No re-encoding; ffmpeg only remuxes.
5. Writes tags (title, artist, album artist = name from the list, album, track n/total, year) and cover art with `mutagen`.
6. Records each finished track in an archive file, so re-runs only fetch new releases.
7. Optional: asks Lidarr to import each artist folder (`LIDARR_URL`, `LIDARR_API_KEY`, `LIDARR_STAGING_PATH`). Lidarr only imports releases that exist in MusicBrainz.

## Build
```bash
docker build -t ytmusic-discography:dev .
```
Dependencies are pinned in `requirements.txt`. **Updating yt-dlp** (needed when YouTube changes break downloads): change its version there, rebuild, run a `--dry-run` and a one-release test.

## Run
```bash
docker run --rm --user <uid>:<gid> -e YTM_LOCATION=<country code> \
  -e ARCHIVE_FILE=/state/archive.txt \
  --mount type=bind,src=/path/to/artists.txt,dst=/input/artists.txt,readonly \
  --mount type=bind,src=/path/to/cookies.txt,dst=/input/cookies.txt,readonly \
  --mount type=bind,src=/path/to/archive.txt,dst=/state/archive.txt \
  --mount type=bind,src=/path/to/music,dst=/output \
  ytmusic-discography:dev [--artist "Name"] [--release "Title"] [--dry-run]
```
- `--dry-run`: resolve artists and list releases only; needs no cookies or output mount.
- The archive file must exist before the first run (`touch` it) and be writable by `<uid>`.
- Cookies: Netscape `cookies.txt` for `youtube.com` only, exported from a private browser window that is closed right after, otherwise YouTube rotates them.
- Pacing (seconds, ±50 % jitter): `REQUEST_DELAY` (1.5), `TRACK_DELAY` (7), `RELEASE_DELAY` (30).

Exit codes: 0 ok, 1 some artists failed, 2 config error, 3 YouTube bot-check/HTTP 429, 4 cookies rejected.

## Third-party software
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (Unlicense), with [deno](https://github.com/denoland/deno) (MIT) as its JavaScript runtime
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) (MIT)
- [mutagen](https://github.com/quodlibet/mutagen) (GPL-2.0+)
- [FFmpeg](https://ffmpeg.org/) (Debian package, LGPL/GPL)

Network access: YouTube / YouTube Music, cover images from Google's image CDN, and your Lidarr instance if configured. No telemetry.
