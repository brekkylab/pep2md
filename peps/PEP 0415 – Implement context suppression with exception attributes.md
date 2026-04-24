---
pep: 415
title: Implement context suppression with exception attributes
author:
- Benjamin Peterson <benjamin@python.org>
bdfl_delegate: Alyssa Coghlan
status: Final
type: Standards Track
created: 26-Feb-2012
python_version: '3.3'
post_history:
- 26-Feb-2012
replaces: '409'
resolution: https://mail.python.org/pipermail/python-dev/2012-May/119467.html
python_status: Final
url: https://peps.python.org/pep-0415/
source_path: https://github.com/python/peps/blob/main/peps/pep-0415.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:27:51+00:00'
---

# Abstract

`409`{.interpreted-text role="pep"} introduced support for the
`raise exc from None` construct to allow the display of the exception
context to be explicitly suppressed. This PEP retains the language level
changes already implemented in `409`{.interpreted-text role="pep"}, but
replaces the underlying implementation mechanism with a simpler approach
based on a new `__suppress_context__` attribute on all `BaseException`
instances.

# PEP Acceptance

This PEP was accepted by Alyssa Coghlan on the 14th of May, 2012.

# Rationale

`409`{.interpreted-text role="pep"} changes `__cause__` to be `Ellipsis`
by default. Then if `__cause__` is set to `None` by
`raise exc from None`, no context or cause will be printed should the
exception be uncaught.

The main problem with this scheme is it complicates the role of
`__cause__`. `__cause__` should indicate the cause of the exception not
whether `__context__` should be printed or not. This use of `__cause__`
is also not easily extended in the future. For example, we may someday
want to allow the programmer to select which of `__context__` and
`__cause__` will be printed. The `409`{.interpreted-text role="pep"}
implementation is not amenable to this.

The use of `Ellipsis` is a hack. Before `409`{.interpreted-text
role="pep"}, `Ellipsis` was used exclusively in extended slicing.
Extended slicing has nothing to do with exceptions, so it\'s not clear
to someone inspecting an exception object why `__cause__` should be set
to `Ellipsis`. Using `Ellipsis` by default for `__cause__` makes it
asymmetrical with `__context__`.

# Proposal

A new attribute on `BaseException`, `__suppress_context__`, will be
introduced. Whenever `__cause__` is set, `__suppress_context__` will be
set to `True`. In particular, `raise exc from cause` syntax will set
`exc.__suppress_context__` to `True`. Exception printing code will check
for that attribute to determine whether context and cause will be
printed. `__cause__` will return to its original purpose and values.

There is precedence for `__suppress_context__` with the
`print_line_and_file` exception attribute.

To summarize, `raise exc from cause` will be equivalent to:

    exc.__cause__ = cause
    raise exc

where `exc.__cause__ = cause` implicitly sets
`exc.__suppress_context__`.

# Patches

There is a patch on [Issue 14133](http://bugs.python.org/issue14133).

# References

# Copyright

This document has been placed in the public domain.
