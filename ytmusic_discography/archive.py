"""Record of completed tracks, keyed per release so a song shared by an album and a single is fetched for both."""
import os
from pathlib import Path


class Archive:
    def __init__(self, path: Path):
        self.path = path
        self._done: set[str] = set()
        if path.exists():
            self._done = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}

    @staticmethod
    def _key(release_id: str, video_id: str) -> str:
        return f"{release_id} {video_id}"

    def has(self, release_id: str, video_id: str) -> bool:
        return self._key(release_id, video_id) in self._done

    def add(self, release_id: str, video_id: str) -> None:
        key = self._key(release_id, video_id)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(key + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._done.add(key)
