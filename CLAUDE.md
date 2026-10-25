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
- Audio only. Format preference: `141` (AAC 256 kbps, requires YouTube Premium cookies) → fallback `251` (Opus) → `bestaudio`.
- **No re-encoding.** Remux only if the container requires it.
- Embed metadata (artist, album artist, album, title, track number, total tracks, year) and cover art.
- Use a yt-dlp download archive so re-runs skip completed tracks.
- Pace requests (sleep between tracks and between releases, configurable) to reduce the risk of the account being flagged.

### Output layout (staging)
```
<DEST>/<Artist>/<Album> (<Year>)/<NN> - <Title>.<ext>
```
Sanitize names for filesystem safety; keep Unicode (Greek etc.) intact.

### Lidarr hand-off (optional)
- If `LIDARR_URL` and `LIDARR_API_KEY` are set, after each artist completes, trigger Lidarr's `DownloadedAlbumsScan` command for that artist's staging folder, using the path **as Lidarr sees it** (`LIDARR_STAGING_PATH`, which may differ from the container's `<DEST>`).
- Lidarr moves matched albums into its library and renames them. Unmatched files (duplicates of better-quality albums, releases missing from MusicBrainz) stay in staging for manual review.
- If unset, just download.

### Inputs
| Input | How | Notes |
|---|---|---|
| Artist list | file mount, read-only | Lines: `Name — URL` (em dash separator). URL may be `(none)` → name search. Ignore blank lines and `#` comments. |
| Destination | dir mount, read-write | Staging root (`<DEST>`) |
| Cookies | file mount, **read-only** | Netscape cookies.txt from a logged-in YouTube Premium session |
| `LIDARR_URL`, `LIDARR_API_KEY`, `LIDARR_STAGING_PATH` | env | Optional |
| Pacing / dry-run / artist filter | env or CLI flags | |

### Security
- Cookies grant full Google account access: never log them, never copy them into the image, image layers or output dir; mount read-only.
- Never log the Lidarr API key.
- Run as a non-root user in the container; output file ownership configurable via `PUID`/`PGID`.
- Pin dependency versions; `yt-dlp` updates often and breaks on YouTube changes, so make updating it a single, documented step.

### Packaging
- Python, single Docker image, slim base. Entry point runs the whole list; flags for a single artist and `--dry-run` (resolve + list releases, no download).

## To verify early (unknowns, do not assume)
- Whether format `141` is actually served via yt-dlp with Premium cookies for YouTube Music release playlists today, and whether a PO token is required.
- Whether channel IDs from the list (official artist channels and `- Topic` channels) are accepted by `ytmusicapi.get_artist()` or need mapping.
- Which metadata fields yt-dlp populates for YouTube Music album playlists (`album`, `track_number`, `release_year`, `artist`), and what ytmusicapi must supply instead.
- Lidarr API: exact payload for `DownloadedAlbumsScan` (path field, import mode) on the deployed Lidarr version.

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
