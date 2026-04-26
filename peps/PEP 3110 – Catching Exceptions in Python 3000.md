---
pep: 3110
title: Catching Exceptions in Python 3000
author:
- Collin Winter <collinwinter@google.com>
status: Final
type: Standards Track
created: 16-Jan-2006
python_version: '3.0'
post_history: []
python_status: Final
url: https://peps.python.org/pep-3110/
source_path: https://github.com/python/peps/blob/main/peps/pep-3110.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:34+00:00'
---

# Abstract

This PEP introduces changes intended to help eliminate ambiguities in
Python\'s grammar, simplify exception classes, simplify garbage
collection for exceptions and reduce the size of the language in Python
3.0.

# Rationale

1.  `except` clauses in Python 2.x present a syntactic ambiguity where
    the parser cannot differentiate whether :

        except <expression>, <expression>:

    should be interpreted as :

        except <type>, <type>:

    or :

        except <type>, <name>:

    Python 2 opts for the latter semantic, at the cost of requiring the
    former to be parenthesized, like so :

        except (<type>, <type>):

2.  As specified in `352`{.interpreted-text role="pep"}, the ability to
    treat exceptions as tuples will be removed, meaning this code will
    no longer work :

        except os.error, (errno, errstr):

    Because the automatic unpacking will no longer be possible, it is
    desirable to remove the ability to use tuples as `except` targets.

3.  As specified in `344`{.interpreted-text role="pep"}, exception
    instances in Python 3 will possess a `__traceback__` attribute. The
    Open Issues section of that PEP includes a paragraph on garbage
    collection difficulties caused by this attribute, namely a
    \"exception -\> traceback -\> stack frame -\> exception\" reference
    cycle, whereby all locals are kept in scope until the next GC run.
    This PEP intends to resolve this issue by adding a cleanup semantic
    to `except` clauses in Python 3 whereby the target name is deleted
    at the end of the `except` suite.

4.  In the spirit of `"there should be one -- and preferably only one
    -- obvious way to do it" <20>`{.interpreted-text role="pep"}, it is
    desirable to consolidate duplicate functionality. To this end, the
    `exc_value`, `exc_type` and `exc_traceback` attributes of the `sys`
    module[^1] will be removed in favor of `sys.exc_info()`, which
    provides the same information. These attributes are already listed
    in `3100`{.interpreted-text role="pep"} as targeted for removal.

# Grammar Changes

In Python 3, the grammar for `except` statements will change from[^2] :

    except_clause: 'except' [test [',' test]]

to :

    except_clause: 'except' [test ['as' NAME]]

The use of `as` in place of the comma token means that :

    except (AttributeError, os.error):

can be clearly understood as a tuple of exception classes. This new
syntax was first proposed by Greg Ewing[^3] and endorsed ([^4],[^5]) by
the BDFL.

Further, the restriction of the token following `as` from `test` to
`NAME` means that only valid identifiers can be used as `except`
targets.

Note that the grammar above always requires parenthesized tuples as
exception classes. That way, the ambiguous :

    except A, B:

which would mean different things in Python 2.x and 3.x \-- leading to
hard-to-catch bugs \-- cannot legally occur in 3.x code.

# Semantic Changes

In order to resolve the garbage collection issue related to
`344`{.interpreted-text role="pep"}, `except` statements in Python 3
will generate additional bytecode to delete the target, thus eliminating
the reference cycle. The source-to-source translation, as suggested by
Phillip J. Eby [^6], is :

    try:
        try_body
    except E as N:
        except_body
    ...

gets translated to (in Python 2.5 terms) :

    try:
        try_body
    except E, N:
        try:
            except_body
        finally:
            N = None
            del N
    ...

An implementation has already been checked into the py3k (formerly
\"p3yk\") branch[^7].

# Compatibility Issues

Nearly all `except` clauses will need to be changed. `except` clauses
with identifier targets will be converted from :

    except E, N:

to :

    except E as N:

`except` clauses with non-tuple, non-identifier targets (e.g.,
`a.b.c[d]`) will need to be converted from :

    except E, T:

to :

    except E as t:
        T = t

Both of these cases can be handled by Guido van Rossum\'s `2to3`
utility[^8] using the `except` fixer[^9].

`except` clauses with tuple targets will need to be converted manually,
on a case-by-case basis. These changes will usually need to be
accompanied by changes to the exception classes themselves. While these
changes generally cannot be automated, the `2to3` utility is able to
point out cases where the target of an `except` clause is a tuple,
simplifying conversion.

Situations where it is necessary to keep an exception instance around
past the end of the `except` suite can be easily translated like so :

    try:
        ...
    except E as N:
        ...
    ...

becomes :

    try:
        ...
    except E as N:
        n = N
        ...
    ...

This way, when `N` is deleted at the end of the block, `n` will persist
and can be used as normal.

Lastly, all uses of the `sys` module\'s `exc_type`, `exc_value` and
`exc_traceback` attributes will need to be removed. They can be replaced
with `sys.exc_info()[0]`, `sys.exc_info()[1]` and `sys.exc_info()[2]`
respectively, a transformation that can be performed by `2to3`\'s
`sysexcattrs` fixer.

## 2.6 - 3.0 Compatibility

In order to facilitate forwards compatibility between Python 2.6 and
3.0, the `except ... as ...:` syntax will be backported to the 2.x
series. The grammar will thus change from:

    except_clause: 'except' [test [',' test]]

to:

    except_clause: 'except' [test [('as' | ',') test]]

The end-of-suite cleanup semantic for `except` statements will not be
included in the 2.x series of releases.

# Open Issues

## Replacing or Dropping \"sys.exc_info()\"

The idea of dropping `sys.exc_info()` or replacing it with a
`sys.exception` attribute or a `sys.get_exception()` function has been
raised several times on python-3000 ([^10], [^11]) and mentioned in
`344`{.interpreted-text role="pep"}\'s \"Open Issues\" section.

While a `2to3` fixer to replace calls to `sys.exc_info()` and some
attribute accesses would be trivial, it would be far more difficult for
static analysis to find and fix functions that expect the values from
`sys.exc_info()` as arguments. Similarly, this does not address the need
to rewrite the documentation for all APIs that are defined in terms of
`sys.exc_info()`.

# Implementation

This PEP was implemented in revisions 53342[^12] and 53349 [^13].
Support for the new `except` syntax in 2.6 was implemented in revision
55446[^14].

# References

# Copyright

This document has been placed in the public domain.

[^1]: <http://docs.python.org/library/sys.html>

[^2]: <http://docs.python.org/reference/compound_stmts.html#try>

[^3]: <https://mail.python.org/pipermail/python-dev/2006-March/062449.html>

[^4]: <https://mail.python.org/pipermail/python-dev/2006-March/062449.html>

[^5]: <https://mail.python.org/pipermail/python-dev/2006-March/062640.html>

[^6]: <https://mail.python.org/pipermail/python-3000/2007-January/005395.html>

[^7]: <http://svn.python.org/view?rev=53342&view=rev>

[^8]: <https://hg.python.org/sandbox/guido/file/2.7/Lib/lib2to3/>

[^9]: <https://hg.python.org/sandbox/guido/file/2.7/Lib/lib2to3/fixes/fix_except.py>

[^10]: <https://mail.python.org/pipermail/python-3000/2007-January/005385.html>

[^11]: <https://mail.python.org/pipermail/python-3000/2007-January/005604.html>

[^12]: <http://svn.python.org/view?view=revision&revision=53342>

[^13]: <http://svn.python.org/view?view=revision&revision=53349>

[^14]: <http://svn.python.org/view/python/trunk/?view=rev&rev=55446>
