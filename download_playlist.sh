#!/bin/bash
set -euo pipefail

# ensure yt-dlp is up to date (needed for --no-write-cookies)
yt-dlp -U

PLAYLIST_URL="https://www.youtube.com/playlist?list=PLOTbwrNJHj_JA2fTN9t_-20DH9q_ydf07"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOAD_DIR="$SCRIPT_DIR"

COUNTER_FILE="$DOWNLOAD_DIR/counter.txt"
ARCHIVE_FILE="$DOWNLOAD_DIR/downloaded.txt"

COOKIES_FILE="${YTDLP_COOKIES_FILE:-/downloads/cookies.txt}"
PLAYER_CLIENT="${YTDLP_PLAYER_CLIENT:-web}"
PO_TOKEN="${YTDLP_PO_TOKEN:-}"

# clean leftovers
find "$DOWNLOAD_DIR" -maxdepth 1 -name '*.part' -delete

# init counter
[ -f "$COUNTER_FILE" ] || echo 1 > "$COUNTER_FILE"
START_NUM=$(cat "$COUNTER_FILE")

BEFORE_COUNT=0
if [ -f "$ARCHIVE_FILE" ]; then
  BEFORE_COUNT=$(wc -l < "$ARCHIVE_FILE")
fi

YTDLP_ARGS=(
  --extractor-args "youtube:player_client=${PLAYER_CLIENT}"
)

if [ -n "$PO_TOKEN" ]; then
  YTDLP_ARGS+=(--extractor-args "youtube:po_token=${PO_TOKEN}")
fi

if [ -s "$COOKIES_FILE" ]; then
  YTDLP_ARGS+=(--cookies "$COOKIES_FILE")
fi

yt-dlp \
  "${YTDLP_ARGS[@]}" \
  --fragment-retries 20 \
  --retry-sleep fragment:1 \
  --playlist-reverse \
  --autonumber-start "$START_NUM" \
  -f "bv*+ba/b" \
  --merge-output-format mkv \
  --remux-video mkv \
  --embed-metadata \
  --embed-thumbnail \
  --write-thumbnail \
  --convert-thumbnails png \
  --no-write-info-json \
  --no-write-playlist-metafiles \
  --download-archive "$ARCHIVE_FILE" \
  --output "$DOWNLOAD_DIR/%(autonumber)03d - %(title)s.%(ext)s" \
  "$PLAYLIST_URL"

AFTER_COUNT=0
if [ -f "$ARCHIVE_FILE" ]; then
  AFTER_COUNT=$(wc -l < "$ARCHIVE_FILE")
fi

NEW_COUNT=$((AFTER_COUNT - BEFORE_COUNT))
echo $((START_NUM + NEW_COUNT)) > "$COUNTER_FILE"
