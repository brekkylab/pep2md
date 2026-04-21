from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


META_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 _/-]*):\s*(.*)$")


@dataclass(slots=True)
class ParsedPep:
    metadata: dict[str, str]
    body: str


def normalize_key(key: str) -> str:
    key = key.strip().lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    key = re.sub(r"_+", "_", key)
    return key


def parse_pep_rst(text: str) -> ParsedPep:
    lines = text.splitlines()
    metadata: dict[str, str] = {}
    idx = 0
    current_key: str | None = None
    started = False

    while idx < len(lines):
        line = lines[idx]
        if not line.strip():
            if started:
                idx += 1
                break
            idx += 1
            continue

        match = META_LINE_RE.match(line)
        if match:
            started = True
            current_key = normalize_key(match.group(1))
            metadata[current_key] = match.group(2).strip()
            idx += 1
            continue

        if started and current_key and line.startswith((" ", "\t")):
            continuation = line.strip()
            if continuation:
                existing = metadata[current_key]
                metadata[current_key] = f"{existing}\n{continuation}" if existing else continuation
            idx += 1
            continue

        if started:
            break

        idx += 1

    body = "\n".join(lines[idx:]).strip() + "\n"
    return ParsedPep(metadata=metadata, body=body)


def read_pep_metadata(path: Path) -> dict[str, str]:
    return parse_pep_rst(path.read_text(encoding="utf-8")).metadata
