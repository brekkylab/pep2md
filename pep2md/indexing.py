from __future__ import annotations

import json
from pathlib import Path

import yaml

def _extract_frontmatter(md_text: str) -> dict:
    if not md_text.startswith("---\n"):
        return {}
    end = md_text.find("\n---\n", 4)
    if end < 0:
        return {}
    block = md_text[4:end]
    loaded = yaml.safe_load(block)
    return loaded if isinstance(loaded, dict) else {}


def build_indexes(peps_dir: Path, index_dir: Path) -> tuple[Path, Path]:
    index_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for md_path in sorted(peps_dir.glob("PEP *.md")):
        meta = _extract_frontmatter(md_path.read_text(encoding="utf-8"))
        if not meta:
            continue
        row = {
            "pep": int(meta.get("pep", 0) or 0),
            "title": meta.get("title", ""),
            "status": meta.get("status", ""),
            "python_status": meta.get("python_status", meta.get("status", "")),
            "path": str(md_path),
            "source_commit": meta.get("source_commit", ""),
            "updated_at": meta.get("generated_at", meta.get("source_commit", "")),
        }
        row.update(meta)
        rows.append(row)

    rows.sort(key=lambda x: x["pep"])
    peps_json = index_dir / "peps.json"
    peps_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    finals = [
        {"pep": r["pep"], "title": r["title"], "path": r["path"]}
        for r in rows
        if str(r.get("status", "")).lower() == "final"
    ]
    final_json = index_dir / "status_final.json"
    final_json.write_text(json.dumps(finals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return peps_json, final_json
