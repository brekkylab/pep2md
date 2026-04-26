---
pep: 251
title: Python 2.2 Release Schedule
author:
- Barry Warsaw <barry@python.org>
- Guido van Rossum <guido@python.org>
status: Final
type: Informational
topic: Release
created: 17-Apr-2001
python_version: '2.2'
post_history:
- 14-Aug-2001
python_status: Final
url: https://peps.python.org/pep-0251/
source_path: https://github.com/python/peps/blob/main/peps/pep-0251.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:13+00:00'
---

# Abstract

This document describes the Python 2.2 development and release schedule.
The schedule primarily concerns itself with PEP-sized items. Small bug
fixes and changes will occur up until the first beta release.

The schedule below represents the actual release dates of Python 2.2.
Note that any subsequent maintenance releases of Python 2.2 should be
covered by separate PEPs.

# Release Schedule

Tentative future release dates. Note that we\'ve slipped this compared
to the schedule posted around the release of 2.2a1.

- 21-Dec-2001: 2.2 \[Released\] (final release)
- 14-Dec-2001: 2.2c1 \[Released\]
- 14-Nov-2001: 2.2b2 \[Released\]
- 19-Oct-2001: 2.2b1 \[Released\]
- 28-Sep-2001: 2.2a4 \[Released\]
- 7-Sep-2001: 2.2a3 \[Released\]
- 22-Aug-2001: 2.2a2 \[Released\]
- 18-Jul-2001: 2.2a1 \[Released\]

# Release Manager

Barry Warsaw was the Python 2.2 release manager.

# Release Mechanics

We experimented with a new mechanism for releases: a week before every
alpha, beta or other release, we forked off a branch which became the
release. Changes to the branch are limited to the release manager and
his designated \'bots. This experiment was deemed a success and should
be observed for future releases. See `101`{.interpreted-text role="pep"}
for the actual release mechanics.

# New features for Python 2.2

The following new features are introduced in Python 2.2. For a more
detailed account, see Misc/NEWS[^1] in the Python distribution, or
Andrew Kuchling\'s \"What\'s New in Python 2.2\" document[^2].

- iterators (`234`{.interpreted-text role="pep"})
- generators (`255`{.interpreted-text role="pep"})
- unifying long ints and plain ints (`237`{.interpreted-text
  role="pep"})
- division (`238`{.interpreted-text role="pep"})
- unification of types and classes (`252`{.interpreted-text role="pep"},
  `253`{.interpreted-text role="pep"})

# References

# Copyright

This document has been placed in the public domain.

[^1]: Misc/NEWS file from CVS
    <http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/python/python/dist/src/Misc/NEWS?rev=1.337.2.4&content-type=text/vnd.viewcvs-markup>

[^2]: Andrew Kuchling, What\'s New in Python 2.2
    <http://www.python.org/doc/2.2.1/whatsnew/whatsnew22.html>
