# SRRS Download

This project runs `yt-dlp` in a container to download videos from a YouTube
playlist (the "Reddit Stories" playlist) into the directory where you run the
Compose file. It keeps small state files in the same directory as the script to
remember what has already been downloaded so future runs only fetch new videos.

## How it works

- `download_playlist.sh` calls `yt-dlp` with:
  - a download archive (`downloaded.txt`) to skip previously downloaded videos,
  - a counter (`counter.txt`) to keep numbering consistent between runs,
  - thumbnails + metadata embedded into the video files,
  - a YouTube web client profile and extra fragment retries to reduce 403 fragment errors,
  - optional YouTube cookies or PO Token support via environment variables (cookies are
    only loaded when the file is non-empty).
- `docker-compose.yaml` mounts the current directory to `/downloads` in the
  container, so downloads land next to the compose file.
  - `download_playlist.sh` always downloads into the directory containing the
    script, and the counter/download archive live alongside it.

## Usage

From the folder where you want videos stored:

```bash
docker compose up --build --remove-orphans
```

For a scheduled job (like a TrueNAS cron task), make sure you `cd` into the
target download folder before running the command. A typical TrueNAS cron
command looks like this:

```bash
cd /path/to/srrs-download && docker compose up --build --remove-orphans
```

## Handling YouTube bot checks / 403s

Some videos now require authentication or a PO Token. You can provide these by
setting environment variables for the container:

| Variable | Purpose | Example |
| --- | --- | --- |
| `YTDLP_COOKIES_FILE` | Path to an exported cookies.txt file (must be non-empty). Defaults to `/downloads/cookies.txt`. | `/downloads/cookies.txt` |
| `YTDLP_PO_TOKEN` | GVS PO Token value for the selected player client. | `abc123` |
| `YTDLP_PLAYER_CLIENT` | Override the player client (defaults to `android,web`). | `android` |

Example (local file mounted in the download folder):

```bash
YTDLP_PO_TOKEN=your-token \
docker compose up --build --remove-orphans
```

If you see warnings about the Android client being skipped due to cookies, double
check that `cookies.txt` actually contains exported cookies and is not a zero-byte
file. Remove or populate the file to allow the Android client to run. If the
web client reports SABR streaming or missing formats, try `YTDLP_PLAYER_CLIENT=android`
first, since it avoids the web-only SABR challenge in many cases.

## Files created

- `### - <title>.mkv` video files (with embedded metadata and thumbnails)
- `downloaded.txt` (download archive)
- `counter.txt` (autonumbering state)
