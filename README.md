# pep2md

Tool for mirroring the `python/peps` repository into Markdown files.

## Features

- Filename format: `PEP {Num:04d} – {Title}.md` (4-digit zero padding)
- YAML frontmatter: original PEP metadata + normalized fields
- Index generation: `output/index/peps.json`, `output/index/status_final.json`
- Status query: `pep2md query --status Final`
- Incremental sync: `pep2md sync`
- On-demand HTTP fetch for PEP `.rst` files (no full repo clone required)
- Internal PEP links rewritten to relative paths

## Install

With `uv`:

```bash
uv sync --extra dev
```

With `pip`:

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
# sync
pep2md sync  # Incremental sync: fetch changed PEPs and update outputs/index
pep2md sync --full  # Force full regeneration for the current selection
pep2md sync --peps 8,20,333  # Sync only specific PEP numbers
pep2md sync --no-index --no-cache  # Skip index and cache state for this run
pep2md sync --suppress-pandoc-warnings  # Suppress pandoc warnings (--quiet)

# query
pep2md query --status Final --format table  # Show Final PEPs in table format
pep2md query --meta source_path=pep-0008.rst --meta author=Guido --format json  # Filter by metadata (AND) and print JSON
pep2md query --status Active --format jsonl  # Emit one JSON object per line
```

> [!TIP]
> If you installed with `uv`, add `uv run` in front.  
> Such as:
> ```
> uv run pep2md sync --full
> ```


## Outputs

- `output/peps/*.md`
- `output/index/peps.json`
- `output/index/status_final.json`
- `cache/state.json`

## Notes

- Default dependency is `pypandoc_binary`; system `pandoc` can also be used when available.
- As an alternative, you can use `pypandoc.pandoc_download.download_pandoc()`.
- `--full` forces full rebuild but still reads/updates `cache/state.json`.
- `--no-cache` runs without reading/writing `cache/state.json` (stateless run).
- `--suppress-pandoc-warnings` runs pandoc with `--quiet` to suppress warnings.
