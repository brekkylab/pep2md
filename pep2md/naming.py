from __future__ import annotations

import re


INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]+')
SPACE_RE = re.compile(r"\s+")


def sanitize_title(title: str) -> str:
    title = INVALID_FILENAME_CHARS.sub("-", title).strip()
    title = SPACE_RE.sub(" ", title)
    return title.rstrip(".")


def pep_filename(pep_num: int, title: str) -> str:
    return f"PEP {pep_num:04d} – {sanitize_title(title)}.md"
