from __future__ import annotations

import re
from pathlib import Path


INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
REF_LINK_RE = re.compile(r"^(\[[^\]]+\]:\s+)(\S+)(.*)$", re.MULTILINE)
AUTO_LINK_RE = re.compile(r"<([^ >]+)>")

ABS_PEP_RE = re.compile(r"^https?://peps\.python\.org/pep-(\d{4})/?$")
ROOT_PEP_RE = re.compile(r"^/pep-(\d{4})/?$")
SHORT_PEP_RE = re.compile(r"^pep-(\d{1,4})(?:\.rst|\.html|/)?$")


def pep_from_target(target: str) -> int | None:
    value = target.strip().strip("'\"")
    for pattern in (ABS_PEP_RE, ROOT_PEP_RE, SHORT_PEP_RE):
        match = pattern.match(value)
        if match:
            return int(match.group(1))
    return None


def rewrite_internal_links(markdown: str, current_file: Path, pep_to_file: dict[int, Path]) -> str:
    def rewrite_target(raw_target: str) -> str:
        pep_num = pep_from_target(raw_target)
        if pep_num is None or pep_num not in pep_to_file:
            return raw_target
        target_path = pep_to_file[pep_num]
        rel = Path(target_path.name) if target_path.parent == current_file.parent else Path(
            Path(target_path).relative_to(current_file.parent)
        )
        return str(rel).replace("\\", "/")

    def inline_repl(match: re.Match[str]) -> str:
        text = match.group(1)
        target = match.group(2)
        return f"[{text}]({rewrite_target(target)})"

    def ref_repl(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        return f"{prefix}{rewrite_target(target)}{suffix}"

    def auto_repl(match: re.Match[str]) -> str:
        target = match.group(1)
        rewritten = rewrite_target(target)
        if rewritten == target:
            return match.group(0)
        return f"<{rewritten}>"

    markdown = INLINE_LINK_RE.sub(inline_repl, markdown)
    markdown = REF_LINK_RE.sub(ref_repl, markdown)
    markdown = AUTO_LINK_RE.sub(auto_repl, markdown)
    return markdown
