#!/bin/bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

PLAYLIST_URL="https://www.youtube.com/playlist?list=PLOTbwrNJHj_JA2fTN9t_-20DH9q_ydf07"

COUNTER_FILE="$SCRIPT_DIR/counter.txt"
ARCHIVE_FILE="$SCRIPT_DIR/downloaded.txt"

# clean leftovers
find "$SCRIPT_DIR" -name '*.part' -delete

# init counter
[ -f "$COUNTER_FILE" ] || echo 1 > "$COUNTER_FILE"
START_NUM=$(cat "$COUNTER_FILE")

yt-dlp \
  --playlist-reverse \
  --autonumber-start "$START_NUM" \
  -f "bv*[ext=mp4]+ba[ext=m4a]/b" \
  --merge-output-format mkv \
  --embed-metadata \
  --embed-thumbnail \
  --write-thumbnail \
  --convert-thumbnails png \
  --no-write-info-json \
  --no-write-playlist-metafiles \
  --download-archive "$ARCHIVE_FILE" \
  --output "$SCRIPT_DIR/%(autonumber)03d - %(title)s.%(ext)s" \
  --exec 'bash -c "echo $(( $(cat \"'"$COUNTER_FILE"'\" ) + 1 )) > \"'"$COUNTER_FILE"'\""' \
  "$PLAYLIST_URL"
