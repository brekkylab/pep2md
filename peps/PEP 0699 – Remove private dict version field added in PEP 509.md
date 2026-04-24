---
pep: 699
title: Remove private dict version field added in PEP 509
author:
- Ken Jin <kenjin@python.org>
discussions_to: https://discuss.python.org/t/pep-699-remove-private-dict-version-field-added-in-pep-509/19724
status: Accepted
type: Standards Track
created: 03-Oct-2022
python_version: '3.12'
post_history:
- '`05-Oct-2022 <https://discuss.python.org/t/pep-699-remove-private-dict-version-field-added-in-pep-509/19724>`__'
replaces: '509'
resolution: https://discuss.python.org/t/pep-699-remove-private-dict-version-field-added-in-pep-509/19724/13
python_status: Accepted
url: https://peps.python.org/pep-0699/
source_path: https://github.com/python/peps/blob/main/peps/pep-0699.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:04+00:00'
---

# Abstract

`509`{.interpreted-text role="pep"} introduced a private
`ma_version_tag` field for dictionaries to allow optimizations in
CPython and extension libraries. This PEP proposes to rescind
`509`{.interpreted-text role="pep"} and declare the field an
implementation detail, as it has already been superseded by
alternatives. This will further allow the field to be reused for future
optimization.

# Motivation

`509`{.interpreted-text role="pep"} introduced the `ma_version_tag`
field to dictionaries. This 64-bit field stored a version counter that
updates every time a dictionary was modified. The original proposal was
to use this version counter as a guard for optimizations.

Since CPython 3.11, this field has become unused by internal
optimization efforts. `659`{.interpreted-text role="pep"}-specialized
instructions use other methods of verifying that certain optimizations
are safe.

To enable further optimizations in CPython, this PEP proposes that the
`ma_version_tag` field no longer conform to the `509`{.interpreted-text
role="pep"} specification. This will allow the CPython developers to
store other optimization information, such as dictionary write watchers.

# Rationale

This PEP does not specify what the field may be used for in the future.
This is intentional, as implementation details are subject to change,
and the field should be used only for internal consumption by CPython.

# Specification

This specification rescinds that in `509`{.interpreted-text role="pep"}.
The `ma_version_tag` field of the Python `dict`{.interpreted-text
role="class"} class is declared to be an internal implementation detail
and may be removed altogether, or may have a different representation. C
extensions should not rely on this field.

# Backwards Compatibility

Certain extensions use `ma_version_tag` for fast dictionary or globals
lookups. For example, [Cython uses the field for fast dynamic module
variable
lookups](https://github.com/cython/cython/blob/169876872f3cb6198971a1db07e5b8a9d12b3dac/Cython/Utility/ObjectHandling.c#L1556).

This PEP proposes to emit a compiler warning when accessing
`ma_version_tag`. After two consecutive version releases with warnings,
`ma_version_tag` will be removed, in line with `387`{.interpreted-text
role="pep"}.

The biggest user the author could find for this field was Cython.
Discussions with a Cython maintainer indicated that [removing support
for it from Cython is
trivial](https://github.com/faster-cpython/ideas/issues/461#issuecomment-1250358596).

# Security Implications

`509`{.interpreted-text role="pep"} was concerned with integer overflow.
However, this PEP does not introduce any additional security concerns.

# Rejected Ideas

A possible alternative is to preserve the field for backwards
compatibility. This PEP rejects that alternative as future optimizations
will consume more memory, and the field was always considered private
and undocumented aside from the PEP, with no backward compatibility
guarantees. Dictionaries in Python are commonly used, and any increase
in their memory consumption will adversely affect Python's performance.

# Reference Implementation

A reference implementation can be found in
[python/cpython#101193](https://github.com/python/cpython/pull/101193).

# Special Thanks

Thanks to C.A.M. Gerlach for edits and wording changes to this document.
Thanks also to Mark Shannon and Kumar Aditya for providing possible
implementations.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
