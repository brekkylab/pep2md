---
pep: 271
title: Prefixing sys.path by command line option
author:
- Frédéric B. Giacometti <fred@arakne.com>
status: Rejected
type: Standards Track
created: 15-Aug-2001
python_version: '2.2'
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0271/
source_path: https://github.com/python/peps/blob/main/peps/pep-0271.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:26+00:00'
---

# Abstract

At present, setting the `PYTHONPATH` environment variable is the only
method for defining additional Python module search directories.

This PEP introduces the \'-P\' valued option to the python command as an
alternative to `PYTHONPATH`.

# Rationale

On Unix:

    python -P $SOMEVALUE

will be equivalent to:

    env PYTHONPATH=$SOMEVALUE python

On Windows 2K:

    python -P %SOMEVALUE%

will (almost) be equivalent to:

    set __PYTHONPATH=%PYTHONPATH% && set PYTHONPATH=%SOMEVALUE%\
       && python && set PYTHONPATH=%__PYTHONPATH%

# Other Information

This option is equivalent to the \'java -classpath\' option.

# When to use this option

This option is intended to ease and make more robust the use of Python
in test or build scripts, for instance.

# Reference Implementation

A patch implementing this is available from SourceForge:

    http://sourceforge.net/tracker/download.php?group_id=5470&atid=305470&file_id=6916&aid=429614

with the patch discussion at:

    http://sourceforge.net/tracker/?func=detail&atid=305470&aid=429614&group_id=5470

# Copyright

This document has been placed in the public domain.
