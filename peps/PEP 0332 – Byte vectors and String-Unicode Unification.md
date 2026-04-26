---
pep: 332
title: Byte vectors and String/Unicode Unification
author:
- Skip Montanaro <skip@pobox.com>
status: Rejected
type: Standards Track
created: 11-Aug-2004
python_version: '2.5'
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0332/
source_path: https://github.com/python/peps/blob/main/peps/pep-0332.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:15+00:00'
---

# Abstract

This PEP outlines the introduction of a raw `bytes` sequence object and
the unification of the current `str` and `unicode` objects.

# Rejection Notice

This PEP is rejected in this form. The author has expressed lack of time
to continue to shepherd it, and discussion on python-dev has moved to a
slightly different proposal which will (eventually) be written up as a
new PEP. See the thread starting at
<https://mail.python.org/pipermail/python-dev/2006-February/060930.html>.

# Rationale

Python\'s current string objects are overloaded. They serve both to hold
ASCII and non-ASCII character data and to also hold sequences of raw
bytes which have no reasonable interpretation as displayable character
sequences. This overlap hasn\'t been a big problem in the past, but as
Python moves closer to requiring source code to be properly encoded, the
use of strings to represent raw byte sequences will be more problematic.
In addition, as Python\'s Unicode support has improved, it\'s easier to
consider strings as ASCII-encoded Unicode objects.

# Proposed Implementation

The number in parentheses indicates the Python version in which the
feature will be introduced.

- Add a `bytes` builtin which is just a synonym for `str`. (2.5)
- Add a `b"..."` string literal which is equivalent to raw string
  literals, with the exception that values which conflict with the
  source encoding of the containing file not generate warnings. (2.5)
- Warn about the use of variables named \"bytes\". (2.5 or 2.6)
- Introduce a `bytes` builtin which refers to a sequence distinct from
  the `str` type. (2.6)
- Make `str` a synonym for `unicode`. (3.0)

# Bytes Object API

TBD.

# Issues

- Can this be accomplished before Python 3.0?
- Should `bytes` objects be mutable or immutable? (Guido seems to like
  them to be mutable.)

# Copyright

This document has been placed in the public domain.
