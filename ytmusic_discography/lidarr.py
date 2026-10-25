"""Ask Lidarr to import a finished artist folder. The API key is never logged."""
import json
import urllib.request


def scan_request(base_url: str, api_key: str, path: str) -> urllib.request.Request:
    body = json.dumps({"name": "DownloadedAlbumsScan", "path": path, "importMode": "move"}).encode()
    return urllib.request.Request(
        base_url.rstrip("/") + "/api/v1/command", data=body, method="POST",
        headers={"X-Api-Key": api_key, "Content-Type": "application/json"})


def scan(base_url: str, api_key: str, path: str) -> int:
    with urllib.request.urlopen(scan_request(base_url, api_key, path), timeout=30) as r:
        return json.load(r)["id"]
