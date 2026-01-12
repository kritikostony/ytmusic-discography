FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        python3 \
        bash \
        nodejs \
        npm && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    -o /usr/local/bin/yt-dlp && \
    chmod +x /usr/local/bin/yt-dlp

COPY download_playlist.sh /usr/local/bin/download_playlist.sh
RUN chmod +x /usr/local/bin/download_playlist.sh

WORKDIR /app
