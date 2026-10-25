# Base pinned by digest (python:3.12-slim as pulled 2026-10-25).
FROM python:3.12-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/cache \
    DENO_DIR=/tmp/deno

# ffmpeg: remux only (DASH m4a fixup, webm -> opus); never used to re-encode.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check -r requirements.txt
COPY ytmusic_discography ./ytmusic_discography

# Non-root default; override at runtime with --user <uid>:<gid>.
USER 10001:10001
ENTRYPOINT ["python", "-m", "ytmusic_discography"]
