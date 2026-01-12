#!/bin/bash
set -euo pipefail

PLAYLIST_URL="https://www.youtube.com/playlist?list=PLOTbwrNJHj_JA2fTN9t_-20DH9q_ydf07"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${DOWNLOAD_DIR:-}" ]; then
  if [ -d /downloads ] && [ -w /downloads ]; then
    DOWNLOAD_DIR="/downloads"
  else
    DOWNLOAD_DIR="$SCRIPT_DIR"
  fi
fi

mkdir -p "$DOWNLOAD_DIR"

STATE_DIR="${STATE_DIR:-$DOWNLOAD_DIR}"
mkdir -p "$STATE_DIR"

COUNTER_FILE="$STATE_DIR/counter.txt"
ARCHIVE_FILE="$STATE_DIR/downloaded.txt"

# clean leftovers
find "$DOWNLOAD_DIR" -name '*.part' -delete

# init counter
[ -f "$COUNTER_FILE" ] || echo 1 > "$COUNTER_FILE"
START_NUM=$(cat "$COUNTER_FILE")

yt-dlp \
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
  --exec 'after_move:bash -c "echo $(( $(cat \"'"$COUNTER_FILE"'\" ) + 1 )) > \"'"$COUNTER_FILE"'\""' \
  "$PLAYLIST_URL"
