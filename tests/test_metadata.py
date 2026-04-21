from pep2md.metadata import parse_pep_rst


def test_parse_pep_rst_metadata_and_body():
    text = """PEP: 9999
Title: Test PEP
Status: Final
Requires: 1234
  5678

Heading
=======

Body
"""
    parsed = parse_pep_rst(text)
    assert parsed.metadata["pep"] == "9999"
    assert parsed.metadata["title"] == "Test PEP"
    assert parsed.metadata["status"] == "Final"
    assert parsed.metadata["requires"] == "1234\n5678"
    assert parsed.body.startswith("Heading")
