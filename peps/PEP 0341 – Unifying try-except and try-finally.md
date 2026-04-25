---
pep: 341
title: Unifying try-except and try-finally
author:
- Georg Brandl <georg@python.org>
status: Final
type: Standards Track
created: 04-May-2005
python_version: '2.5'
post_history: []
python_status: Final
url: https://peps.python.org/pep-0341/
source_path: https://github.com/python/peps/blob/main/peps/pep-0341.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:27+00:00'
---

# Abstract

This PEP proposes a change in the syntax and semantics of try statements
to allow combined try-except-finally blocks. This means in short that it
would be valid to write:

    try:
        <do something>
    except Exception:
        <handle the error>
    finally:
        <cleanup>

# Rationale/Proposal

There are many use cases for the try-except statement and for the
try-finally statement per se; however, often one needs to catch
exceptions and execute some cleanup code afterwards. It is slightly
annoying and not very intelligible that one has to write:

    f = None
    try:
        try:
            f = open(filename)
            text = f.read()
        except IOError:
            print 'An error occurred'
    finally:
        if f:
            f.close()

So it is proposed that a construction like this:

    try:
        <suite 1>
    except Ex1:
        <suite 2>
    <more except: clauses>
    else:
        <suite 3>
    finally:
        <suite 4>

be exactly the same as the legacy:

    try:
        try:
            <suite 1>
        except Ex1:
            <suite 2>
        <more except: clauses>
        else:
            <suite 3>
    finally:
        <suite 4>

This is backwards compatible, and every try statement that is legal
today would continue to work.

# Changes to the grammar

The grammar for the try statement, which is currently:

    try_stmt: ('try' ':' suite (except_clause ':' suite)+
            ['else' ':' suite] | 'try' ':' suite 'finally' ':' suite)

would have to become:

    try_stmt: 'try' ':' suite
            (
                (except_clause ':' suite)+
                ['else' ':' suite]
                ['finally' ':' suite]
            |
                'finally' ':' suite
            )

# Implementation

As the PEP author currently does not have sufficient knowledge of the
CPython implementation, he is unfortunately not able to deliver one.
Thomas Lee has submitted a patch[^1].

However, according to Guido, it should be a piece of cake to
implement[^2] \-- at least for a core hacker.

This patch was committed 17 December 2005, SVN revision 41740[^3].

# References

# Copyright

This document has been placed in the public domain.

[^1]: <https://bugs.python.org/issue1355913>

[^2]: <https://mail.python.org/pipermail/python-dev/2005-May/053319.html>

[^3]: <https://mail.python.org/pipermail/python-checkins/2005-December/048457.html>
