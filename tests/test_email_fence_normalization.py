from __future__ import annotations

from pathlib import Path

from pep2md.builder import _convert_one_text


def test_email_fence_is_normalized_to_yaml(tmp_path):
    out_dir = tmp_path / "peps"
    pep_map = {12: "PEP 12 – Template.md"}
    rst_text = "PEP: 12\nTitle: Template\nStatus: Draft\n\nBody\n====\n\nx\n"

    # Inject markdown directly by monkeypatching convert_text in module namespace.
    import pep2md.builder as builder

    original = builder.pypandoc.convert_text
    builder.pypandoc.convert_text = lambda *_args, **_kwargs: "``` email\nA: B\n```\n"
    try:
        out = _convert_one_text(
            pep_num=12,
            rst_text=rst_text,
            source_path="https://github.com/python/peps/blob/main/peps/pep-0012.rst",
            out_dir=out_dir,
            source_commit="abc",
            pep_map=pep_map,
        )
    finally:
        builder.pypandoc.convert_text = original

    text = out.read_text(encoding="utf-8")
    assert "``` email" not in text
    assert "``` yaml" in text
