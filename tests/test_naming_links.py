from pathlib import Path

from pep2md.links import rewrite_internal_links
from pep2md.naming import pep_filename


def test_pep_filename():
    assert pep_filename(8, "Style Guide for Python Code") == "PEP 0008 – Style Guide for Python Code.md"
    assert pep_filename(1, 'Bad:/Name*?"<>|') == "PEP 0001 – Bad-Name-.md"


def test_rewrite_internal_links():
    current = Path("/tmp/output/peps/PEP 0001 – One.md")
    mapping = {
        8: Path("/tmp/output/peps/PEP 0008 – Style Guide for Python Code.md"),
        20: Path("/tmp/output/peps/PEP 0020 – Zen.md"),
    }
    md = (
        "[A](pep-0008)\n"
        "[B](https://peps.python.org/pep-0020/)\n"
        "[ref]: /pep-0008/\n"
        "<pep-0020>\n"
    )
    out = rewrite_internal_links(md, current_file=current, pep_to_file=mapping)
    assert "(PEP 0008 – Style Guide for Python Code.md)" in out
    assert "(PEP 0020 – Zen.md)" in out
    assert "[ref]: PEP 0008 – Style Guide for Python Code.md" in out
    assert "<PEP 0020 – Zen.md>" in out
