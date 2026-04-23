from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from pep2md.builder import query_index, sync_incremental
from pep2md.source_http import RemotePepFile


def _set_remote(monkeypatch, *, branch: str, head: str, files: dict[int, tuple[str, str]], texts: dict[str, str]):
    class FakeSource:
        def __init__(self, _repo_url: str):
            pass

        def default_branch(self) -> str:
            return branch

        def head_commit(self, _branch: str) -> str:
            return head

        def list_peps(self, _branch: str) -> dict[int, RemotePepFile]:
            return {
                pep: RemotePepFile(pep=pep, path=path, sha=sha)
                for pep, (path, sha) in files.items()
            }

        def fetch_pep_text(self, _branch: str, path: str) -> str:
            return texts[path]

        def blob_url(self, branch_name: str, path: str) -> str:
            return f"https://github.com/python/peps/blob/{branch_name}/{path}"

    monkeypatch.setattr("pep2md.builder.GitHubPepSource", FakeSource)
    monkeypatch.setattr("pep2md.builder.validate_dependencies", lambda: None)
    monkeypatch.setattr("pep2md.builder.pypandoc.convert_text", lambda body, *_args, **_kwargs: body)


def test_sync_incremental_and_query(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    output = tmp_path / "output"
    repo_url = "https://github.com/python/peps.git"

    _set_remote(
        monkeypatch,
        branch="main",
        head="h1",
        files={
            1: ("peps/pep-0001.rst", "s1"),
            8: ("peps/pep-0008.rst", "s8"),
        },
        texts={
            "peps/pep-0001.rst": "PEP: 1\nTitle: One\nStatus: Draft\n\nbody\n====\n\nx\n",
            "peps/pep-0008.rst": (
                "PEP: 8\n"
                "Title: Eight\n"
                "Status: Final\n"
                "Author: Alice <a@example.com>\n"
                "  Bob <b@example.com>\n"
                "Requires: 333\n"
                "  344, 345\n"
                "Post-History: 2001-03-01\n"
                "  2001-03-02, 2001-03-03\n\n"
                "body\n====\n\nx\n"
            ),
        },
    )
    out1 = sync_incremental(repo_url=repo_url, cache_dir=cache, output_dir=output)
    assert int(out1["converted"]) == 2
    assert int(out1["deleted"]) == 0

    rows = query_index(output / "index" / "peps.json", "Final")
    assert len(rows) == 1
    assert rows[0]["pep"] == 8
    rows_meta_string = query_index(
        output / "index" / "peps.json",
        metadata_filters={"title": "eig"},
    )
    assert [r["pep"] for r in rows_meta_string] == [8]
    rows_meta_list = query_index(
        output / "index" / "peps.json",
        metadata_filters={"requires": "344"},
    )
    assert [r["pep"] for r in rows_meta_list] == [8]
    rows_combined = query_index(
        output / "index" / "peps.json",
        status="final",
        metadata_filters={"author": "alice"},
    )
    assert [r["pep"] for r in rows_combined] == [8]
    pep8 = output / "peps" / "PEP 0008 – Eight.md"
    content = pep8.read_text(encoding="utf-8")
    end = content.find("\n---\n", 4)
    front = yaml.safe_load(content[4:end])
    assert front["author"] == ["Alice <a@example.com>", "Bob <b@example.com>"]
    assert front["requires"] == ["333", "344", "345"]
    assert front["post_history"] == ["2001-03-01", "2001-03-02", "2001-03-03"]
    assert front["url"] == "https://peps.python.org/pep-0008/"
    assert front["source_path"] == "https://github.com/python/peps/blob/main/peps/pep-0008.rst"

    _set_remote(
        monkeypatch,
        branch="main",
        head="h2",
        files={1: ("peps/pep-0001.rst", "s1b")},
        texts={
            "peps/pep-0001.rst": "PEP: 1\nTitle: One Updated\nStatus: Final\n\nbody\n====\n\nx\n",
        },
    )
    out2 = sync_incremental(repo_url=repo_url, cache_dir=cache, output_dir=output)
    assert int(out2["converted"]) == 1
    assert int(out2["deleted"]) == 1

    md_files = sorted((output / "peps").glob("PEP *.md"))
    assert len(md_files) == 1
    assert md_files[0].name == "PEP 0001 – One Updated.md"


def test_sync_with_pep_selection_and_limit(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    output = tmp_path / "output"
    repo_url = "https://github.com/python/peps.git"

    _set_remote(
        monkeypatch,
        branch="main",
        head="h1",
        files={
            1: ("peps/pep-0001.rst", "s1"),
            8: ("peps/pep-0008.rst", "s8"),
            20: ("peps/pep-0020.rst", "s20"),
        },
        texts={
            "peps/pep-0001.rst": "PEP: 1\nTitle: One\nStatus: Draft\n\nbody\n====\n\nx\n",
            "peps/pep-0008.rst": "PEP: 8\nTitle: Eight\nStatus: Final\n\nbody\n====\n\nx\n",
            "peps/pep-0020.rst": "PEP: 20\nTitle: Twenty\nStatus: Final\n\nbody\n====\n\nx\n",
        },
    )
    out1 = sync_incremental(repo_url=repo_url, cache_dir=cache, output_dir=output, pep_numbers={8, 20})
    assert int(out1["converted"]) == 2
    names = sorted(path.name for path in (output / "peps").glob("PEP *.md"))
    assert names == ["PEP 0008 – Eight.md", "PEP 0020 – Twenty.md"]

    out2 = sync_incremental(repo_url=repo_url, cache_dir=cache, output_dir=output, limit=1)
    assert int(out2["converted"]) == 1
    names2 = sorted(path.name for path in (output / "peps").glob("PEP *.md"))
    assert names2 == ["PEP 0001 – One.md", "PEP 0008 – Eight.md", "PEP 0020 – Twenty.md"]


def test_sync_raises_for_unknown_requested_pep(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    output = tmp_path / "output"
    repo_url = "https://github.com/python/peps.git"

    _set_remote(
        monkeypatch,
        branch="main",
        head="h1",
        files={8: ("peps/pep-0008.rst", "s8")},
        texts={"peps/pep-0008.rst": "PEP: 8\nTitle: Eight\nStatus: Final\n\nx\n"},
    )
    with pytest.raises(ValueError):
        sync_incremental(repo_url=repo_url, cache_dir=cache, output_dir=output, pep_numbers={8, 333})


def test_sync_no_index_and_no_cache(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    output = tmp_path / "output"
    repo_url = "https://github.com/python/peps.git"

    _set_remote(
        monkeypatch,
        branch="main",
        head="h1",
        files={8: ("peps/pep-0008.rst", "s8")},
        texts={"peps/pep-0008.rst": "PEP: 8\nTitle: Eight\nStatus: Final\n\nx\n"},
    )
    out = sync_incremental(
        repo_url=repo_url,
        cache_dir=cache,
        output_dir=output,
        build_index=False,
        use_cache=False,
    )
    assert int(out["converted"]) == 1
    assert not (output / "index" / "peps.json").exists()
    assert not (cache / "state.json").exists()
