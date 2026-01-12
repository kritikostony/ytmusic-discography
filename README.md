# SRRS Download

This project runs `yt-dlp` in a container to download videos from a YouTube
playlist (the "Reddit Stories" playlist) into the directory where you run the
Compose file. It keeps a small state directory (`.yt-dlp`) to remember what has
already been downloaded so future runs only fetch new videos.

## How it works

- `download_playlist.sh` calls `yt-dlp` with:
  - a download archive (`.yt-dlp/downloaded.txt`) to skip previously downloaded
    videos,
  - a counter (`.yt-dlp/counter.txt`) to keep numbering consistent between runs,
  - thumbnails + metadata embedded into the video files.
- `docker-compose.yaml` mounts the current directory to `/downloads` in the
  container, so downloads land next to the compose file.

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

## Files created

- `### - <title>.mkv` video files (with embedded metadata and thumbnails)
- `.yt-dlp/downloaded.txt` (download archive)
- `.yt-dlp/counter.txt` (autonumbering state)
