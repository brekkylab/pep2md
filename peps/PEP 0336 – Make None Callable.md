---
pep: 336
title: Make None Callable
author:
- Andrew McClelland <eternalsquire@comcast.net>
status: Rejected
type: Standards Track
created: 28-Oct-2004
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0336/
source_path: https://github.com/python/peps/blob/main/peps/pep-0336.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:26+00:00'
---

# Abstract

`None` should be a callable object that when called with any arguments
has no side effect and returns `None`.

# BDFL Pronouncement

This PEP is rejected. It is considered a feature that `None` raises an
error when called. The proposal falls short in tests for obviousness,
clarity, explicitness, and necessity. The provided Switch example is
nice but easily handled by a simple lambda definition. See python-dev
discussion on 17 June 2005[^1].

# Motivation

To allow a programming style for selectable actions that is more in
accordance with the minimalistic functional programming goals of the
Python language.

# Rationale

Allow the use of `None` in method tables as a universal no effect rather
than either (1) checking a method table entry against `None` before
calling, or (2) writing a local no effect method with arguments similar
to other functions in the table.

The semantics would be effectively:

    class None:

        def __call__(self, *args):
            pass

# How To Use

Before, checking function table entry against `None`:

    class Select:

        def a(self, input):
            print 'a'

        def b(self, input):
            print 'b'

        def c(self, input):
            print 'c'

        def __call__(self, input):
         function = { 1 : self.a,
               2 : self.b,
               3 : self.c
            }.get(input, None)
         if function:  return function(input)

Before, using a local no effect method:

    class Select:

        def a(self, input):
            print 'a'

        def b(self, input):
            print 'b'

        def c(self, input):
            print 'c'

        def nop(self, input):
         pass

        def __call__(self, input):
            return { 1 : self.a,
            2 : self.b,
            3 : self.c
            }.get(input, self.nop)(input)

After:

    class Select:

        def a(self, input):
            print 'a'

        def b(self, input):
            print 'b'

        def c(self, input):
            print 'c'

        def __call__(self, input):
         return { 1 : self.a,
            2 : self.b,
            3 : self.c
            }.get(input, None)(input)

# References

# Copyright

This document has been placed in the public domain.

[^1]: Raymond Hettinger, Propose to reject PEP 336 \-- Make None
    Callable
    <https://mail.python.org/pipermail/python-dev/2005-June/054280.html>
