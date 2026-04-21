from __future__ import annotations

import datetime as dt
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import pypandoc
import yaml

from .indexing import build_indexes
from .links import rewrite_internal_links
from .metadata import parse_pep_rst
from .naming import pep_filename
from .source_http import GitHubPepSource, RemotePepFile
from .state import load_state, save_state


OUTPUT_PEP_RE = re.compile(r"^PEP (\d+) – .+\.md$")
EMAIL_FENCE_RE = re.compile(r"^(```+)\s*email\s*$", re.MULTILINE)


def _select_pep_numbers(
    available: Iterable[int],
    pep_numbers: set[int] | None = None,
    limit: int | None = None,
    strict: bool = True,
) -> set[int]:
    all_numbers = sorted(set(available))
    selected = all_numbers
    if pep_numbers is not None:
        missing = sorted(pep_numbers.difference(all_numbers))
        if missing and strict:
            raise ValueError(f"Requested PEPs not found in repository: {missing}")
        selected = [num for num in selected if num in pep_numbers]
    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be >= 1")
        selected = selected[:limit]
    return set(selected)


def remove_deleted_outputs(out_dir: Path, deleted_pep_nums: set[int]) -> None:
    for pep_num in deleted_pep_nums:
        for path in out_dir.glob(f"PEP {pep_num} – *.md"):
            path.unlink(missing_ok=True)


def prune_non_selected_outputs(out_dir: Path, selected: set[int]) -> None:
    if not out_dir.exists():
        return
    for path in out_dir.glob("PEP *.md"):
        match = OUTPUT_PEP_RE.match(path.name)
        if not match:
            continue
        pep_num = int(match.group(1))
        if pep_num not in selected:
            path.unlink(missing_ok=True)


def has_output_for_pep(out_dir: Path, pep_num: int) -> bool:
    return any(out_dir.glob(f"PEP {pep_num} – *.md"))


def validate_dependencies() -> None:
    try:
        pypandoc.get_pandoc_version()
    except OSError as exc:
        raise RuntimeError("Pandoc not found. Install pypandoc_binary or system pandoc.") from exc


def _split_field_by_comma(value: str) -> list[str]:
    parts: list[str] = []
    for line in value.splitlines():
        for token in line.split(","):
            item = token.strip()
            if item:
                parts.append(item)
    return parts


def _normalize_frontmatter_meta(meta: dict[str, str]) -> dict[str, object]:
    normalized: dict[str, object] = dict(meta)
    for key in ("author", "authors", "requires"):
        raw = normalized.get(key)
        if isinstance(raw, str):
            normalized[key] = _split_field_by_comma(raw)
    raw_post_history = normalized.get("post_history")
    if isinstance(raw_post_history, str):
        normalized["post_history"] = _split_field_by_comma(raw_post_history)
    return normalized


def _filename_map_from_texts(pep_texts: dict[int, str]) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for pep_num, text in pep_texts.items():
        parsed = parse_pep_rst(text)
        title = parsed.metadata.get("title", f"PEP {pep_num}")
        mapping[pep_num] = pep_filename(pep_num, title)
    return mapping


def _convert_one_text(
    pep_num: int,
    rst_text: str,
    source_path: str,
    out_dir: Path,
    source_commit: str,
    pep_map: dict[int, str],
) -> Path:
    parsed = parse_pep_rst(rst_text)
    meta = dict(parsed.metadata)
    title = meta.get("title", f"PEP {pep_num}")
    filename = pep_map.get(pep_num) or pep_filename(pep_num, title)
    out_path = out_dir / filename
    for stale in out_dir.glob(f"PEP {pep_num} – *.md"):
        if stale != out_path:
            stale.unlink(missing_ok=True)

    markdown_body = pypandoc.convert_text(parsed.body, "md", format="rst")
    markdown_body = EMAIL_FENCE_RE.sub(r"\1 yaml", markdown_body)
    pep_to_file = {k: out_dir / v for k, v in pep_map.items()}
    markdown_body = rewrite_internal_links(markdown_body, out_path, pep_to_file)

    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    normalized = {
        "pep": pep_num,
        "title": title,
        "status": meta.get("status", ""),
        "python_status": meta.get("status", ""),
        "url": f"https://peps.python.org/pep-{pep_num:04d}/",
        "source_path": source_path,
        "source_commit": source_commit,
        "generated_at": generated_at,
    }
    frontmatter = {**_normalize_frontmatter_meta(meta), **normalized}

    content = "---\n"
    content += yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
    content += "---\n\n"
    content += markdown_body.rstrip() + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def _fetch_texts_for(
    source: GitHubPepSource,
    branch: str,
    files: dict[int, RemotePepFile],
    selected: set[int],
) -> dict[int, str]:
    if not selected:
        return {}
    texts: dict[int, str] = {}
    workers = _int_env("PEP2MD_FETCH_WORKERS", default=8, minimum=1)
    with ThreadPoolExecutor(max_workers=min(workers, len(selected))) as pool:
        future_to_pep = {
            pool.submit(source.fetch_pep_text, branch, files[pep_num].path): pep_num
            for pep_num in sorted(selected)
        }
        for future in as_completed(future_to_pep):
            pep_num = future_to_pep[future]
            texts[pep_num] = future.result()
    return texts


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, value)


def sync_incremental(
    repo_url: str,
    cache_dir: Path,
    output_dir: Path,
    pep_numbers: set[int] | None = None,
    limit: int | None = None,
    full: bool = False,
    build_index: bool = True,
    use_cache: bool = True,
) -> dict[str, int | str]:
    state_path = cache_dir / "state.json"
    peps_dir = output_dir / "peps"
    index_dir = output_dir / "index"
    peps_dir.mkdir(parents=True, exist_ok=True)

    source = GitHubPepSource(repo_url)
    branch = source.default_branch()
    head = source.head_commit(branch)
    remote_files = source.list_peps(branch)
    available = set(remote_files.keys())

    filtered_mode = pep_numbers is not None or limit is not None
    selected = _select_pep_numbers(
        available,
        pep_numbers=pep_numbers,
        limit=limit,
        strict=pep_numbers is not None,
    )

    state = load_state(state_path) if use_cache else {}
    prev_shas: dict[str, str] = state.get("pep_sha", {}) if isinstance(state.get("pep_sha", {}), dict) else {}
    prev_all = {int(k): str(v) for k, v in prev_shas.items() if str(k).isdigit()}

    converted = 0
    deleted = 0
    to_convert: list[int] = []

    if full or not state or not use_cache:
        to_convert = sorted(selected)
    else:
        for pep in sorted(selected):
            sha_now = remote_files[pep].sha
            if prev_all.get(pep) != sha_now or not has_output_for_pep(peps_dir, pep):
                to_convert.append(pep)

    if to_convert:
        validate_dependencies()
        to_convert_set = set(to_convert)
        texts = _fetch_texts_for(source, branch, remote_files, to_convert_set)
        current_selected_texts = texts.copy()
        if filtered_mode:
            # Needed for stable file naming when selected items already exist but unchanged.
            missing_name_context = selected.difference(to_convert_set)
            if missing_name_context:
                current_selected_texts.update(_fetch_texts_for(source, branch, remote_files, missing_name_context))
        pep_map = _filename_map_from_texts(current_selected_texts)
        convert_workers = _int_env("PEP2MD_CONVERT_WORKERS", default=4, minimum=1)
        with ThreadPoolExecutor(max_workers=min(convert_workers, len(to_convert))) as pool:
            futures = [
                pool.submit(
                    _convert_one_text,
                    pep,
                    texts[pep],
                    source.blob_url(branch, remote_files[pep].path),
                    peps_dir,
                    head,
                    pep_map,
                )
                for pep in to_convert
            ]
            for future in as_completed(futures):
                future.result()
                converted += 1

    if not filtered_mode:
        removed = set(prev_all.keys()).difference(available)
        if removed:
            remove_deleted_outputs(peps_dir, removed)
            deleted += len(removed)

    if build_index:
        build_indexes(peps_dir, index_dir)

    merged = prev_all.copy()
    for pep, remote in remote_files.items():
        merged[pep] = remote.sha
    for pep in set(merged.keys()).difference(available):
        merged.pop(pep, None)

    if use_cache:
        save_state(
            state_path,
            {
                "source": "github-http",
                "repo_url": repo_url,
                "branch": branch,
                "head_commit": head,
                "pep_sha": {str(k): v for k, v in sorted(merged.items())},
            },
        )

    return {
        "converted": converted,
        "deleted": deleted,
        "commit": head,
    }


def _contains_match(field: object, query: str) -> bool:
    needle = query.lower()
    if isinstance(field, list):
        return any(needle in str(item).lower() for item in field)
    if field is None:
        return False
    return needle in str(field).lower()


def query_index(
    index_file: Path,
    status: str | None = None,
    metadata_filters: dict[str, str] | None = None,
) -> list[dict]:
    rows = json.loads(index_file.read_text(encoding="utf-8"))
    filtered = rows

    if status:
        wanted = status.strip().lower()
        filtered = [row for row in filtered if str(row.get("status", "")).lower() == wanted]

    if metadata_filters:
        for key, value in metadata_filters.items():
            filtered = [row for row in filtered if _contains_match(row.get(key), value)]

    return filtered
