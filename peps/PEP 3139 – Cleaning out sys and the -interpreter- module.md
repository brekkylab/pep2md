---
pep: 3139
title: Cleaning out sys and the "interpreter" module
author:
- Benjamin Peterson <benjamin@python.org>
status: Rejected
type: Standards Track
created: 04-Apr-2008
python_version: '3.0'
python_status: Rejected
url: https://peps.python.org/pep-3139/
source_path: https://github.com/python/peps/blob/main/peps/pep-3139.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:51+00:00'
---

# Rejection Notice

Guido\'s -0.5 put an end to this PEP. See
<https://mail.python.org/pipermail/python-3000/2008-April/012977.html>.

# Abstract

This PEP proposes a new low-level module for CPython-specific
interpreter functions in order to clean out the sys module and separate
general Python functionality from implementation details.

# Rationale

The sys module currently contains functions and data that can be put
into two major groups:

1.  Data and functions that are available in all Python implementations
    and deal with the general running of a Python virtual machine.
    - argv
    - byteorder
    - path, path_hooks, meta_path, path_importer_cache, and modules
    - copyright, hexversion, version, and version_info
    - displayhook, \_\_displayhook\_\_
    - excepthook, \_\_excepthook\_\_, exc_info, and exc_clear
    - exec_prefix and prefix
    - executable
    - exit
    - flags, py3kwarning, dont_write_bytecode, and warn_options
    - getfilesystemencoding
    - get/setprofile
    - get/settrace, call_tracing
    - getwindowsversion
    - maxint and maxunicode
    - platform
    - ps1 and ps2
    - stdin, stderr, stdout, \_\_stdin\_\_, \_\_stderr\_\_,
      \_\_stdout\_\_
    - tracebacklimit
2.  Data and functions that affect the CPython interpreter.
    - get/setrecursionlimit
    - get/setcheckinterval
    - [getframe]{#getframe} and [current_frame]{#current_frame}
    - getrefcount
    - get/setdlopenflags
    - settscdumps
    - api_version
    - winver
    - dllhandle
    - float_info
    - [compact_freelists]{#compact_freelists}
    - [clear_type_cache]{#clear_type_cache}
    - subversion
    - builtin_module_names
    - callstats
    - intern

The second collections of items has been steadily increasing over the
years causing clutter in sys. Guido has even said he doesn\'t recognize
some of things in it[^1]!

Moving these items off to another module would send a clear message to
other Python implementations about what functions need and need not be
implemented.

It has also been proposed that the contents of types module be
distributed across the standard library[^2]; the interpreter module
would provide an excellent resting place for internal types like frames
and code objects.

# Specification

A new builtin module named \"interpreter\" (see [Naming](#naming)) will
be added.

The second list of items above will be split into the stdlib as follows:

The interpreter module

:   - get/setrecursionlimit
    - get/setcheckinterval
    - [getframe]{#getframe} and [current_frame]{#current_frame}
    - get/setdlopenflags
    - settscdumps
    - api_version
    - winver
    - dllhandle
    - float_info
    - [clear_type_cache]{#clear_type_cache}
    - subversion
    - builtin_module_names
    - callstats
    - intern

The gc module:

:   - getrefcount
    - [compact_freelists]{#compact_freelists}

# Transition Plan

Once implemented in 3.x, the interpreter module will be back-ported to
2.6. Py3k warnings will be added to the sys functions it replaces.

# Open Issues

## What should move?

### dont_write_bytecode

Some believe that the writing of bytecode is an implementation detail
and should be moved[^3]. The counterargument is that all current,
complete Python implementations do write some sort of bytecode, so it is
valuable to be able to disable it. Also, if it is moved, some wish to
put it in the imp module.

## Move to some to imp?

It was noted that dont_write_bytecode or maybe builtin_module_names
might fit nicely in the imp module.

## Naming

The author proposes the name \"interpreter\" for the new module.
\"pyvm\" has also been suggested[^4]. The name \"cpython\" was well
liked [^5].

# References

# Copyright

This document has been placed in the public domain.

[^1]: <http://bugs.python.org/issue1522>

[^2]: <https://mail.python.org/pipermail/stdlib-sig/2008-April/000172.html>

[^3]: <https://mail.python.org/pipermail/stdlib-sig/2008-April/000217.html>

[^4]: <https://mail.python.org/pipermail/python-3000/2007-November/011351.html>

[^5]: <https://mail.python.org/pipermail/stdlib-sig/2008-April/000223.html>
