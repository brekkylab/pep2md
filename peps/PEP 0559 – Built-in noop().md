---
pep: 559
title: Built-in noop()
author:
- Barry Warsaw <barry@python.org>
status: Rejected
type: Standards Track
created: 08-Sep-2017
python_version: '3.7'
post_history:
- 09-Sep-2017
resolution: https://mail.python.org/pipermail/python-dev/2017-September/149438.html
python_status: Rejected
url: https://peps.python.org/pep-0559/
source_path: https://github.com/python/peps/blob/main/peps/pep-0559.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:37+00:00'
---

# Abstract

This PEP proposes adding a new built-in function called `noop()` which
does nothing but return `None`.

# Rationale

It is trivial to implement a no-op function in Python. It\'s so easy in
fact that many people do it many times over and over again. It would be
useful in many cases to have a common built-in function that does
nothing.

One use case would be for `553`{.interpreted-text role="pep"}, where you
could set the breakpoint environment variable to the following in order
to effectively disable it:

    $ setenv PYTHONBREAKPOINT=noop

# Implementation

The Python equivalent of the `noop()` function is exactly:

    def noop(*args, **kws):
        return None

The C built-in implementation is available as a pull request[^1].

# Rejected alternatives

## `noop()` returns something

YAGNI.

This is rejected because it complicates the semantics. For example, if
you always return both `*args` and `**kws`, what do you return when none
of those are given? Returning a tuple of `((), {})` is kind of ugly, but
provides consistency. But you might also want to just return `None`
since that\'s also conceptually what the function was passed.

Or, what if you pass in exactly one positional argument, e.g. `noop(7)`.
Do you return `7` or `((7,), {})`? And so on.

The author claims that you won\'t ever need the return value of `noop()`
so it will always return `None`.

Coghlan\'s Dialogs (edited for formatting):

> My counterargument to this would be `map(noop, iterable)`,
> `sorted(iterable, key=noop)`, etc. (`filter`, `max`, and `min` all
> accept callables that accept a single argument, as do many of the
> itertools operations).
>
> Making `noop()` a useful default function in those cases just needs
> the definition to be:
>
>     def noop(*args, **kwds):
>         return args[0] if args else None
>
> The counterargument to the counterargument is that using `None` as the
> default in all these cases is going to be faster, since it lets the
> algorithm skip the callback entirely, rather than calling it and
> having it do nothing useful.

# References

# Copyright

This document has been placed in the public domain.

[^1]: <https://github.com/python/cpython/pull/3480>
