#!/bin/bash
set -euo pipefail

PLAYLIST_URL="https://www.youtube.com/playlist?list=PLOTbwrNJHj_JA2fTN9t_-20DH9q_ydf07"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOAD_DIR="$SCRIPT_DIR"

COUNTER_FILE="$DOWNLOAD_DIR/counter.txt"
ARCHIVE_FILE="$DOWNLOAD_DIR/downloaded.txt"

# clean leftovers
find "$DOWNLOAD_DIR" -maxdepth 1 -name '*.part' -delete

# init counter
[ -f "$COUNTER_FILE" ] || echo 1 > "$COUNTER_FILE"
START_NUM=$(cat "$COUNTER_FILE")
BEFORE_COUNT=0
if [ -f "$ARCHIVE_FILE" ]; then
  BEFORE_COUNT=$(wc -l < "$ARCHIVE_FILE")
fi

PLAYER_CLIENT="${YTDLP_PLAYER_CLIENT:-android}"
COOKIES_FILE="${YTDLP_COOKIES_FILE:-$DOWNLOAD_DIR/cookies.txt}"
EXTRACTOR_ARGS="youtube:player_client=${PLAYER_CLIENT}"
if [ -n "${YTDLP_PO_TOKEN:-}" ]; then
  EXTRACTOR_ARGS="${EXTRACTOR_ARGS};po_token=${PLAYER_CLIENT}.gvs+${YTDLP_PO_TOKEN}"
fi

YTDLP_ARGS=(
  --extractor-args "$EXTRACTOR_ARGS"
)

if [ -f "$COOKIES_FILE" ]; then
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
