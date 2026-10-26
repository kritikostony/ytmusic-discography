# ytmusic-discography

Download full artist discographies (albums + singles) from YouTube Music as tagged audio files, optionally handing them to Lidarr for import. Runs as a Docker container.

Private repo. Keep it free of deployment-specific details anyway (hosts, IPs, real paths, API keys): the owner's actual run configuration lives in a separate private infra repo. Use generic defaults and documented env vars.

## Requirements (decided)

### Source
- Resolve each artist to their **YouTube Music artist page** and download only its **Albums** and **Singles** releases.
- Never download from channel uploads, music videos or Shorts (video clips contain extra sounds; Shorts are unwanted).
- Artist resolution: use the channel URL from the input list when it maps to a YouTube Music artist; otherwise fall back to a YouTube Music artist search by name. Log which path was used and the resolved artist name/browseId so mismatches can be reviewed.

### Download
- Tools: `ytmusicapi` (artist → albums/singles listing, release playlist IDs) and `yt-dlp` (download).
- Audio only. Format selector: `141/774/251` — `141` (AAC ~256 kbps, Premium) → `774` (Opus ~256 kbps, Premium) → `251` (Opus ~145 kbps). No `bestaudio` fallback: if none of these exist, skip the track and log it.
- An album may mix `.m4a` and `.opus` when individual tracks lack `141`.
- `ffmpeg` (Debian package) is required in the image: `141` arrives as DASH m4a and is fixed up by yt-dlp; `774`/`251` webm is remuxed to `.opus` (Ogg). Tags and cover art are written with `mutagen`. No re-encoding anywhere.
- **No re-encoding.** Remux only if the container requires it.
- Embed metadata (artist, album artist, album, title, track number, total tracks, year) and cover art.
- Download archive (`--archive`/`ARCHIVE_FILE`, default `<DEST>/.archive.txt`; own format, one `<release browseId> <videoId>` per line) so re-runs skip completed tracks. Not yt-dlp's archive: that is keyed by video ID only and would skip a song on a single after it was fetched for an album. Back it up (e.g. ZFS snapshots): losing it means re-downloading everything.
- Cookies are required for downloading (Premium formats). yt-dlp writes cookies back, so it gets a private temporary copy (`/tmp`, mode 600) deleted at exit; the mounted file is never modified.
- Pace requests (sleep between tracks and between releases, configurable) to reduce the risk of the account being flagged.

### Output layout (staging)
```
<DEST>/<Artist>/<Album> (<Year>)/<NN> - <Title>.<ext>
```
`<Artist>` and the album-artist tag use the name from the input list (Greek); album and track titles and track artists come from YouTube Music (Latin). Sanitize names for filesystem safety; keep Unicode (Greek etc.) intact. If two releases of one artist map to the same folder name in a run, append ` [<type>]`. Partial downloads go to `<DEST>/.ytmusic-discography-tmp/` (same mount, so finished files are renamed into place) and the folder is removed at exit.
`<DEST>` may be an existing music library root (e.g. Lidarr's): files then land in the existing `<Artist>` folders, which only works when list names match the library's folder names exactly. Keep the archive outside the library via `ARCHIVE_FILE`.

### Lidarr hand-off (optional)
- If `LIDARR_URL` and `LIDARR_API_KEY` are set, after each artist completes, trigger Lidarr's `DownloadedAlbumsScan` command for that artist's staging folder, using the path **as Lidarr sees it** (`LIDARR_STAGING_PATH`, which may differ from the container's `<DEST>`).
- Lidarr moves matched albums into its library and renames them. Unmatched files (duplicates of better-quality albums, releases missing from MusicBrainz) stay in staging for manual review.
- If unset, just download.

### Inputs
| Input | How | Notes |
|---|---|---|
| Artist list | file mount, read-only | Lines: `Name — URL [URL ...]` (em dash separator; one or more space-separated URLs). URL forms seen: `youtube.com/channel/UC…`, `music.youtube.com/channel/UC…`, `youtube.com/user/…`, `youtube.com/@…`. URL may be `(none)` → name search. Ignore blank lines and `#` comments. |
| Destination | dir mount, read-write | Staging root (`<DEST>`) |
| Cookies | file mount, **read-only** | Netscape cookies.txt from a logged-in YouTube Premium session |
| `LIDARR_URL`, `LIDARR_API_KEY`, `LIDARR_STAGING_PATH` | env | Optional |
| Pacing / dry-run / artist filter | env or CLI flags | |

### Security
- Cookies grant full Google account access: never log them, never copy them into the image, image layers or output dir; mount read-only.
- Never log the Lidarr API key.
- Run as a non-root user in the container; output file ownership is set with `docker run --user <uid>:<gid>` (image default 10001:10001).
- Pin dependency versions; `yt-dlp` updates often and breaks on YouTube changes, so make updating it a single, documented step.

### Packaging
- Python, single Docker image, slim base. Entry point runs the whole list; flags `--artist`, `--release` and `--dry-run` (resolve + list releases, no download, no cookies needed).
- Exit codes: 0 ok, 1 some artists failed, 2 usage/config error, 3 stopped because YouTube bot-checked or rate-limited (HTTP 429), 4 stopped because YouTube rejected the cookies (yt-dlp "cookies are no longer valid"; never continue without Premium).

## To verify early (unknowns, do not assume)
- ~~Format `141` with Premium cookies; PO token~~ — **verified 2026-10-25** (yt-dlp 2026.10.21, deno 2.9.8, `yt-dlp[default]`): with cookies yt-dlp reports "Detected YouTube Premium subscription" and lists `141` and `774` (client `TV-S`); without cookies neither appears. One track downloaded as `141` with no PO token provider and no 403. A JS runtime (deno) is required. Re-check if downloads start failing at scale.
- ~~Channel IDs → `ytmusicapi.get_artist()`~~ — **verified 2026-10-25** (ytmusicapi 1.12.3, unauthenticated) on a 109-artist list: 76 `UC…` IDs resolved directly; 28 `UC…` IDs raised `KeyError` (not YouTube Music artist pages: VEVO/label/plain channels); 5 `/user/` or `@` URLs cannot be passed to `get_artist()`. Name search (`filter="artists"`) returned a plausible artist for all 33 fallbacks. Resolution order: each `UC…` ID in the line → name search. A direct hit can still be wrong (one returned "X feat. Y"), so log name + browseId for review.
- **Metadata language (verified 2026-10-25):** for Greek artists, YouTube Music album and track metadata is Latin transliteration regardless of requested language. ytmusicapi rejects `language="el"`; forcing `hl=el` returns the Greek artist name but breaks artist-page parsing (no albums/singles). Use `language="en"`. Album `year` is the release's (often digital re-release) year, not the original.
- ~~Lidarr matching of Latin-tagged files~~ — **tested 2026-10-26** (Lidarr 3.1.6.5078, "Full" metadata profile): the artist matched via the Greek album-artist tag, but both test EPs were rejected with "Couldn't find similar album". One EP is absent from MusicBrainz (MusicBrainz listed 1 release vs ~30 on YouTube Music); the other exists there with Greek titles and still did not match. Conclusion: Lidarr hand-off is unusable for this catalogue; the owner writes directly into the library's artist folders instead. Hand-off stays as an optional feature.
- ~~yt-dlp metadata for album playlists~~ — **verified 2026-10-25** (yt-dlp 2026.10.21): `track_number` and `album_artist` are `None`; `artist`/`artists` are malformed (duplicated joined entry, full-width comma `，`); `album`, `title`, `release_year` are present. Decision: ytmusicapi `get_album()` is the sole metadata source (album, album artist, year, track number, track title, track artists, total tracks, `videoId`); yt-dlp only downloads by `videoId`; tags are written from ytmusicapi data without re-encoding. Album track lists can contain music videos (`MUSIC_VIDEO_TYPE_OMV`; verified: 3 of 11 tracks on one album, whole singles). ytmusicapi `counterpart` is empty for them. Rule: for each OMV track, search songs for `<artist> <title>` and use the first `ATV` result whose duration is within ±1 s and whose title matches (equal, or the album title only adds a suffix such as `(00s Version)`); keep the album's track number and tags. No match → skip the track and log it (never download OMV audio). Summary of skipped tracks at the end of the run.
- ~~Lidarr `DownloadedAlbumsScan` payload~~ — **verified 2026-10-25** (Lidarr 3.1.6.5078): `POST /api/v1/command` with header `X-Api-Key` and body `{"name":"DownloadedAlbumsScan","path":"<LIDARR_STAGING_PATH>/<Artist>","importMode":"move"}`. `importMode` defaults to `auto` when omitted; send `move` explicitly. Response is the queued command with an `id`; poll `GET /api/v1/command/<id>` for `status`/`result`.

## Prior art in this repo
The previous project (a yt-dlp video playlist downloader) is preserved at tag `srrs-final`. Lessons worth reusing:
- `--extractor-args "youtube:player_client=android,web"` and an optional `youtube:po_token=...` worked around 403 / SABR / missing-format errors.
- Only pass `--cookies` when the file exists and is non-empty.
- `--fragment-retries 20 --retry-sleep fragment:1` reduced fragment 403s.
Do not carry over: cookies mounted read-write, unpinned `yt-dlp` (`-U`, `latest` download at build), running as root.

## Working agreements
- Optimization order: Security → Stability → Simplicity → Performance.
- FOSS only; disclose any telemetry, network calls or account requirements.
- State assumptions explicitly (OS, versions, paths). When something is unknown, ask or provide a command to find out; do not guess.
- Debugging: one hypothesis → one fix → one verification step.
- Flag destructive or irreversible actions and get explicit confirmation first.
- Commands and code must be complete and copy-paste safe. Minimal responses, no filler.
