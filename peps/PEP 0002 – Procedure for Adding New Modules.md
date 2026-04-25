---
pep: 2
title: Procedure for Adding New Modules
author:
- Brett Cannon <brett@python.org>
- Martijn Faassen <faassen@infrae.com>
status: Active
type: Process
created: 07-Jul-2001
post_history:
- 07-Jul-2001
- 09-Mar-2002
python_status: Active
url: https://peps.python.org/pep-0002/
source_path: https://github.com/python/peps/blob/main/peps/pep-0002.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:21+00:00'
---

# Introduction

The Python Standard Library contributes significantly to Python\'s
success. The language comes with \"batteries included\", so it is easy
for people to become productive with just the standard library alone. It
is therefore important that the usefulness of the standard library be
maintained.

Due to the visibility and importance of the standard library, it must be
maintained thoughtfully. As such, any code within it must be maintained
by Python\'s development team which leads to a perpetual cost to each
addition made. There is also added cognitive load for users in
familiarizing themselves with what is in the standard library to be
considered.

New functionality is commonly added to the library in the form of new
modules. This PEP will describe the procedure for the *addition* of new
modules. `4`{.interpreted-text role="pep"} deals with procedures for
deprecation of modules; the *removal* of old and unused modules from the
standard library.

# Acceptance Procedure

For top-level modules/packages, a PEP is required. The procedure for
writing a PEP is covered in `1`{.interpreted-text role="pep"}.

For submodules of a preexisting package in the standard library,
additions are at the discretion of the general Python development team
and its members.

General guidance on what modules typically are accepted into the
standard library, the overall process, etc. are covered in the
[developer\'s guide](https://devguide.python.org/stdlibchanges/).

# Maintenance Procedure

Anything accepted into the standard library is expected to be primarily
maintained there, within Python\'s development infrastructure. While
some members of the development team may choose to maintain a backport
of a module outside of the standard library, it is up to them to keep
their external code in sync as appropriate.

# Copyright

This document has been placed in the public domain.
