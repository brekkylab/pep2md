from __future__ import annotations

import argparse
import json
from pathlib import Path

from .builder import query_index, sync_incremental


DEFAULT_REPO_URL = "https://github.com/python/peps.git"
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_CACHE_DIR = Path("cache")


def _parse_pep_args(raw_values: list[str] | None) -> set[int] | None:
    if not raw_values:
        return None
    result: set[int] = set()
    for raw in raw_values:
        for part in raw.split(","):
            value = part.strip()
            if not value:
                continue
            if not value.isdigit():
                raise SystemExit(f"Invalid PEP number: {value}")
            result.add(int(value))
    if not result:
        raise SystemExit("--peps requires at least one number")
    return result


def _sync_cmd(args: argparse.Namespace) -> int:
    try:
        result = sync_incremental(
            repo_url=args.repo_url,
            cache_dir=Path(args.cache),
            output_dir=Path(args.output),
            pep_numbers=_parse_pep_args(args.peps),
            limit=args.limit,
            full=args.full,
            build_index=not args.no_index,
            use_cache=not args.no_cache,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _parse_meta_filters(raw_values: list[str] | None) -> dict[str, str]:
    if not raw_values:
        return {}
    filters: dict[str, str] = {}
    for raw in raw_values:
        if "=" not in raw:
            raise SystemExit(f"Invalid --meta format: {raw} (expected key=value)")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(f"Invalid --meta format: {raw} (empty key)")
        if not value:
            raise SystemExit(f"Invalid --meta format: {raw} (empty value)")
        filters[key] = value
    return filters


def _query_cmd(args: argparse.Namespace) -> int:
    index = Path(args.index)
    if not index.exists():
        raise SystemExit(f"Index not found: {index}")
    rows = query_index(
        index_file=index,
        status=args.status,
        metadata_filters=_parse_meta_filters(args.meta),
    )
    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if args.format == "jsonl":
        for row in rows:
            print(json.dumps(row, ensure_ascii=False))
        return 0

    if not rows:
        print("(no results)")
        return 0

    print("pep\tstatus\ttitle\tpath")
    for row in rows:
        print(f"{row.get('pep')}\t{row.get('status')}\t{row.get('title')}\t{row.get('path')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pep2md")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sync_p = sub.add_parser("sync")
    sync_p.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    sync_p.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR))
    sync_p.add_argument("--cache", default=str(DEFAULT_CACHE_DIR))
    sync_p.add_argument("--peps", nargs="+", help="Specific PEP numbers (space or comma separated).")
    sync_p.add_argument("--limit", type=int, help="Build only first N PEPs by number.")
    sync_p.add_argument("--full", action="store_true", help="Force full rebuild before indexing.")
    sync_p.add_argument("--no-index", action="store_true", help="Skip index generation.")
    sync_p.add_argument("--no-cache", action="store_true", help="Do not read/write cache state (disables incremental cache usage).")
    sync_p.set_defaults(func=_sync_cmd)

    query_p = sub.add_parser("query")
    query_p.add_argument("--status")
    query_p.add_argument(
        "--meta",
        action="append",
        help="Metadata filter in key=value format. Can be provided multiple times.",
    )
    query_p.add_argument("--index", default=str(DEFAULT_OUTPUT_DIR / "index" / "peps.json"))
    query_p.add_argument("--format", choices=["table", "json", "jsonl"], default="table")
    query_p.set_defaults(func=_query_cmd)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)
