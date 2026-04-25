---
pep: 281
title: Loop Counter Iteration with range and xrange
author:
- Magnus Lie Hetland <magnus@hetland.org>
status: Rejected
type: Standards Track
created: 11-Feb-2002
python_version: '2.3'
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0281/
source_path: https://github.com/python/peps/blob/main/peps/pep-0281.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:25+00:00'
---

# Abstract

This PEP describes yet another way of exposing the loop counter in
for-loops. It basically proposes that the functionality of the function
`indices()` from `212`{.interpreted-text role="pep"} be included in the
existing functions `range()` and `xrange()`.

# Pronouncement

In commenting on `279`{.interpreted-text role="pep"}\'s `enumerate()`
function, this PEP\'s author offered, \"I\'m quite happy to have it make
`281`{.interpreted-text role="pep"} obsolete.\" Subsequently,
`279`{.interpreted-text role="pep"} was accepted into Python 2.3.

On 17 June 2005, the BDFL concurred with it being obsolete and hereby
rejected the PEP. For the record, he found some of the examples to
somewhat jarring in appearance:

    >>> range(range(5), range(10), range(2))
    [5, 7, 9]

# Motivation

It is often desirable to loop over the indices of a sequence. PEP 212
describes several ways of doing this, including adding a built-in
function called indices, conceptually defined as:

    def indices(sequence):
        return range(len(sequence))

On the assumption that adding functionality to an existing built-in
function may be less intrusive than adding a new built-in function, this
PEP proposes adding this functionality to the existing functions
`range()` and `xrange()`.

# Specification

It is proposed that all three arguments to the built-in functions
`range()` and `xrange()` are allowed to be objects with a length (i.e.
objects implementing the `__len__` method). If an argument cannot be
interpreted as an integer (i.e. it has no `__int__` method), its length
will be used instead.

Examples:

    >>> range(range(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> range(range(5), range(10))
    [5, 6, 7, 8, 9]
    >>> range(range(5), range(10), range(2))
    [5, 7, 9]
    >>> list(xrange(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(xrange(xrange(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Number the lines of a file:
    lines = file.readlines()
    for num in range(lines):
        print num, lines[num]

# Alternatives

A natural alternative to the above specification is allowing `xrange()`
to access its arguments in a lazy manner. Thus, instead of using their
length explicitly, `xrange` can return one index for each element of the
stop argument until the end is reached. A similar lazy treatment makes
little sense for the start and step arguments since their length must be
calculated before iteration can begin. (Actually, the length of the step
argument isn\'t needed until the second element is returned.)

A pseudo-implementation (using only the stop argument, and assuming that
it is iterable) is:

    def xrange(stop):
        i = 0
        for x in stop:
            yield i
            i += 1

Testing whether to use `int()` or lazy iteration could be done by
checking for an `__iter__` attribute. (This example assumes the presence
of generators, but could easily have been implemented as a plain
iterator object.)

It may be questionable whether this feature is truly useful, since one
would not be able to access the elements of the iterable object inside
the for loop through indexing.

Example:

    # Printing the numbers of the lines of a file:
    for num in range(file):
        print num # The line itself is not accessible

A more controversial alternative (to deal with this) would be to let
`range()` behave like the function `irange()` of `212`{.interpreted-text
role="pep"} when supplied with a sequence.

Example:

    >>> range(5)
    [0, 1, 2, 3, 4]
    >>> range('abcde')
    [(0, 'a'), (1, 'b'), (2, 'c'), (3, 'd'), (4, 'e')]

# Backwards Compatibility

The proposal could cause backwards incompatibilities if arguments are
used which implement both `__int__` and `__len__` (or `__iter__` in the
case of lazy iteration with `xrange`). The author does not believe that
this is a significant problem.

# Copyright

This document has been placed in the public domain.
