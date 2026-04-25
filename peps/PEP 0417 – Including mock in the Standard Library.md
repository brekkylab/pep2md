---
pep: 417
title: Including mock in the Standard Library
author:
- Michael Foord <michael@python.org>
status: Final
type: Standards Track
created: 12-Mar-2012
python_version: '3.3'
post_history:
- 12-Mar-2012
resolution: https://mail.python.org/pipermail/python-dev/2012-March/117507.html
python_status: Final
url: https://peps.python.org/pep-0417/
source_path: https://github.com/python/peps/blob/main/peps/pep-0417.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:29+00:00'
---

# Abstract

This PEP proposes adding the mock[^1] testing library to the Python
standard library as `unittest.mock`.

# Rationale

Creating mock objects for testing is a common need in Python. Many
developers create ad-hoc mocks, as needed, in their test suites. This is
currently what we do in the Python test suite, where a standardised mock
object library would be helpful.

There are many mock object libraries available for Python[^2]. Of these,
mock is overwhelmingly the most popular, with as many downloads on PyPI
as the other mocking libraries combined.

An advantage of mock is that it is a mocking library and not a
framework. It provides a configurable and flexible mock object, without
being opinionated about how you write your tests. The mock api is now
well battle-tested and stable.

mock also handles safely monkeypatching and unmonkeypatching objects
during the scope of a test. This is hard to do safely and many
developers / projects mimic this functionality (often incorrectly). A
standardised way to do this, handling the complexity of patching in the
presence of the descriptor protocol (etc) is useful. People are asking
for a \"patch\"[^3] feature to unittest. Doing this via mock.patch is
preferable to re-implementing part of this functionality in unittest.

# Background

Addition of mock to the Python standard library was discussed and agreed
to at the Python Language Summit 2012.

# Open Issues

As of release 0.8, which is current at the time of writing, mock is
compatible with Python 2.4-3.2. Moving into the Python standard library
will allow for the removal of some Python 2 specific \"compatibility
hacks\".

mock 0.8 introduced a new feature, \"auto-speccing\", obsoletes an older
mock feature called \"mocksignature\". The \"mocksignature\"
functionality can be removed from mock altogether prior to inclusion.

# References

# Copyright

This document has been placed in the public domain.

[^1]: [mock library on PyPI](http://pypi.python.org/pypi/mock)

[^2]: <http://pypi.python.org/pypi?%3Aaction=search&term=mock&submit=search>

[^3]: <http://bugs.python.org/issue11664>
