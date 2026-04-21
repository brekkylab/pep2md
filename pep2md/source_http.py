from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.request import Request, urlopen


PEP_PATH_RE = re.compile(r"^(?:peps/)?pep-(\d{4})\.rst$")


@dataclass(slots=True)
class RemotePepFile:
    pep: int
    path: str
    sha: str


def _http_json(url: str) -> dict:
    req = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "pep2md"})
    with urlopen(req, timeout=30) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def _http_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "pep2md"})
    with urlopen(req, timeout=30) as resp:  # nosec B310
        return resp.read().decode("utf-8")


def parse_github_repo(repo_url: str) -> tuple[str, str]:
    cleaned = repo_url.strip().rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    prefix = "https://github.com/"
    if not cleaned.startswith(prefix):
        raise ValueError(f"Unsupported repo URL (GitHub only): {repo_url}")
    parts = cleaned[len(prefix) :].split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    return parts[0], parts[1]


class GitHubPepSource:
    def __init__(self, repo_url: str):
        owner, repo = parse_github_repo(repo_url)
        self.owner = owner
        self.repo = repo

    def default_branch(self) -> str:
        data = _http_json(f"https://api.github.com/repos/{self.owner}/{self.repo}")
        return str(data["default_branch"])

    def head_commit(self, branch: str) -> str:
        data = _http_json(f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{branch}")
        return str(data["sha"])

    def list_peps(self, branch: str) -> dict[int, RemotePepFile]:
        data = _http_json(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{branch}?recursive=1"
        )
        mapping: dict[int, RemotePepFile] = {}
        for entry in data.get("tree", []):
            if entry.get("type") != "blob":
                continue
            path = str(entry.get("path", ""))
            match = PEP_PATH_RE.match(path)
            if not match:
                continue
            pep = int(match.group(1))
            candidate = RemotePepFile(pep=pep, path=path, sha=str(entry.get("sha", "")))
            current = mapping.get(pep)
            if current is None:
                mapping[pep] = candidate
                continue
            # Prefer "peps/pep-XXXX.rst" over root if both exist.
            if current.path.startswith("pep-") and path.startswith("peps/"):
                mapping[pep] = candidate
        return mapping

    def fetch_pep_text(self, branch: str, path: str) -> str:
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{branch}/{path}"
        return _http_text(raw_url)

    def blob_url(self, branch: str, path: str) -> str:
        return f"https://github.com/{self.owner}/{self.repo}/blob/{branch}/{path}"
