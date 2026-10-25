# ytmusic-discography

Downloads artists' full discographies (albums and singles) from YouTube Music as tagged audio, without music videos or Shorts. Optionally hands each finished artist to Lidarr for import.

> **Status:** early development.

> **Disclaimer:** downloading from YouTube violates YouTube's Terms of Service. You are responsible for whether your use is lawful where you live. AAC 256 kbps requires a YouTube Premium account and its session cookies; using them ties all requests to that Google account, which Google may restrict.

## How it works
1. Reads a list of artists (`Name — URL` per line).
2. Resolves each to a YouTube Music artist page (`ytmusicapi`).
3. Downloads every album and single release with `yt-dlp`: best audio, no re-encoding, tags and cover art embedded.
4. Writes `Artist/Album (Year)/NN - Title.ext` into the destination folder.
5. If Lidarr is configured, triggers an import of that artist's folder.

## Usage (planned)
```bash
docker run --rm \
  -v /path/to/artists.txt:/input/artists.txt:ro \
  -v /path/to/cookies.txt:/input/cookies.txt:ro \
  -v /path/to/staging:/output \
  -e PUID=1000 -e PGID=1000 \
  -e LIDARR_URL=http://lidarr:8686 \
  -e LIDARR_API_KEY=... \
  -e LIDARR_STAGING_PATH=/downloads/ytmusic \
  ytmusic-discography
```

## Third-party software
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (Unlicense)
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) (MIT)

Network access: YouTube / YouTube Music, and your Lidarr instance if configured. No telemetry.
