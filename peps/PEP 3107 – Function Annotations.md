---
pep: 3107
title: Function Annotations
author:
- Collin Winter <collinwinter@google.com>
- Tony Lownds <tony@lownds.com>
status: Final
type: Standards Track
created: 02-Dec-2006
python_version: '3.0'
post_history: []
python_status: Final
url: https://peps.python.org/pep-3107/
source_path: https://github.com/python/peps/blob/main/peps/pep-3107.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:50+00:00'
---

# Abstract

This PEP introduces a syntax for adding arbitrary metadata annotations
to Python functions[^1].

# Rationale

Because Python\'s 2.x series lacks a standard way of annotating a
function\'s parameters and return values, a variety of tools and
libraries have appeared to fill this gap. Some utilise the decorators
introduced in `318`{.interpreted-text role="pep"}, while others parse a
function\'s docstring, looking for annotations there.

This PEP aims to provide a single, standard way of specifying this
information, reducing the confusion caused by the wide variation in
mechanism and syntax that has existed until this point.

# Fundamentals of Function Annotations

Before launching into a discussion of the precise ins and outs of Python
3.0\'s function annotations, let\'s first talk broadly about what
annotations are and are not:

1.  Function annotations, both for parameters and return values, are
    completely optional.

2.  Function annotations are nothing more than a way of associating
    arbitrary Python expressions with various parts of a function at
    compile-time.

    By itself, Python does not attach any particular meaning or
    significance to annotations. Left to its own, Python simply makes
    these expressions available as described in [Accessing Function
    Annotations](#accessing-function-annotations) below.

    The only way that annotations take on meaning is when they are
    interpreted by third-party libraries. These annotation consumers can
    do anything they want with a function\'s annotations. For example,
    one library might use string-based annotations to provide improved
    help messages, like so:

        def compile(source: "something compilable",
                    filename: "where the compilable thing comes from",
                    mode: "is this a single statement or a suite?"):
            ...

    Another library might be used to provide typechecking for Python
    functions and methods. This library could use annotations to
    indicate the function\'s expected input and return types, possibly
    something like:

        def haul(item: Haulable, *vargs: PackAnimal) -> Distance:
            ...

    However, neither the strings in the first example nor the type
    information in the second example have any meaning on their own;
    meaning comes from third-party libraries alone.

3.  Following from point 2, this PEP makes no attempt to introduce any
    kind of standard semantics, even for the built-in types. This work
    will be left to third-party libraries.

# Syntax

## Parameters

Annotations for parameters take the form of optional expressions that
follow the parameter name:

    def foo(a: expression, b: expression = 5):
        ...

In pseudo-grammar, parameters now look like
`identifier [: expression] [= expression]`. That is, annotations always
precede a parameter\'s default value and both annotations and default
values are optional. Just like how equal signs are used to indicate a
default value, colons are used to mark annotations. All annotation
expressions are evaluated when the function definition is executed, just
like default values.

Annotations for excess parameters (i.e., `*args` and `**kwargs`) are
indicated similarly:

    def foo(*args: expression, **kwargs: expression):
        ...

Annotations for nested parameters always follow the name of the
parameter, not the last parenthesis. Annotating all parameters of a
nested parameter is not required:

    def foo((x1, y1: expression),
            (x2: expression, y2: expression)=(None, None)):
        ...

## Return Values

The examples thus far have omitted examples of how to annotate the type
of a function\'s return value. This is done like so:

    def sum() -> expression:
        ...

That is, the parameter list can now be followed by a literal `->` and a
Python expression. Like the annotations for parameters, this expression
will be evaluated when the function definition is executed.

The grammar for function definitions[^2] is now:

    decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    decorators: decorator+
    funcdef: [decorators] 'def' NAME parameters ['->' test] ':' suite
    parameters: '(' [typedargslist] ')'
    typedargslist: ((tfpdef ['=' test] ',')*
                    ('*' [tname] (',' tname ['=' test])* [',' '**' tname]
                     | '**' tname)
                    | tfpdef ['=' test] (',' tfpdef ['=' test])* [','])
    tname: NAME [':' test]
    tfpdef: tname | '(' tfplist ')'
    tfplist: tfpdef (',' tfpdef)* [',']

## Lambda

`lambda`\'s syntax does not support annotations. The syntax of `lambda`
could be changed to support annotations, by requiring parentheses around
the parameter list. However it was decided [^3] not to make this change
because:

1.  It would be an incompatible change.
2.  Lambdas are neutered anyway.
3.  The lambda can always be changed to a function.

# Accessing Function Annotations

Once compiled, a function\'s annotations are available via the
function\'s `__annotations__` attribute. This attribute is a mutable
dictionary, mapping parameter names to an object representing the
evaluated annotation expression

There is a special key in the `__annotations__` mapping, `"return"`.
This key is present only if an annotation was supplied for the
function\'s return value.

For example, the following annotation:

    def foo(a: 'x', b: 5 + 6, c: list) -> max(2, 9):
        ...

would result in an `__annotations__` mapping of :

    {'a': 'x',
     'b': 11,
     'c': list,
     'return': 9}

The `return` key was chosen because it cannot conflict with the name of
a parameter; any attempt to use `return` as a parameter name would
result in a `SyntaxError`.

`__annotations__` is an empty, mutable dictionary if there are no
annotations on the function or if the functions was created from a
`lambda` expression.

# Use Cases

In the course of discussing annotations, a number of use-cases have been
raised. Some of these are presented here, grouped by what kind of
information they convey. Also included are examples of existing products
and packages that could make use of annotations.

- Providing typing information
  - Type checking ([^4],[^5])
  - Let IDEs show what types a function expects and returns ([^6])
  - Function overloading / generic functions ([^7])
  - Foreign-language bridges ([^8],[^9])
  - Adaptation ([^10],[^11])
  - Predicate logic functions
  - Database query mapping
  - RPC parameter marshaling ([^12])
- Other information
  - Documentation for parameters and return values ([^13])

# Standard Library

## pydoc and inspect

The `pydoc` module should display the function annotations when
displaying help for a function. The `inspect` module should change to
support annotations.

# Relation to Other PEPs

## Function Signature Objects (PEP 362)

Function Signature Objects should expose the function\'s annotations.
The `Parameter` object may change or other changes may be warranted.

# Implementation

A reference implementation has been checked into the py3k (formerly
\"p3yk\") branch as revision 53170[^14].

# Rejected Proposals

- The BDFL rejected the author\'s idea for a special syntax for adding
  annotations to generators as being \"too ugly\"[^15].
- Though discussed early on ([^16],[^17]), including special objects in
  the stdlib for annotating generator functions and higher-order
  functions was ultimately rejected as being more appropriate for
  third-party libraries; including them in the standard library raised
  too many thorny issues.
- Despite considerable discussion about a standard type parameterisation
  syntax, it was decided that this should also be left to third-party
  libraries. ([^18], [^19],[^20]).
- Despite yet more discussion, it was decided not to standardize a
  mechanism for annotation interoperability. Standardizing
  interoperability conventions at this point would be premature. We
  would rather let these conventions develop organically, based on
  real-world usage and necessity, than try to force all users into some
  contrived scheme. ([^21],[^22], [^23]).

# References and Footnotes

# Copyright

This document has been placed in the public domain.

[^1]: Unless specifically stated, \"function\" is generally used as a
    synonym for \"callable\" throughout this document.

[^2]: <http://docs.python.org/reference/compound_stmts.html#function-definitions>

[^3]: <https://mail.python.org/pipermail/python-3000/2006-May/001613.html>

[^4]: <http://web.archive.org/web/20070730120117/http://oakwinter.com/code/typecheck/>

[^5]: <http://web.archive.org/web/20070603221429/http://maxrepo.info/>

[^6]: <http://www.python.org/idle/doc/idle2.html#Tips>

[^7]: <http://www-128.ibm.com/developerworks/library/l-cppeak2/>

[^8]: <http://www.jython.org/Project/index.html>

[^9]: <http://www.codeplex.com/Wiki/View.aspx?ProjectName=IronPython>

[^10]: <http://www.artima.com/weblogs/viewpost.jsp?thread=155123>

[^11]: <http://peak.telecommunity.com/PyProtocols.html>

[^12]: <http://rpyc.wikispaces.com/>

[^13]: <http://docs.python.org/library/pydoc.html>

[^14]: <http://svn.python.org/view?rev=53170&view=rev>

[^15]: <https://mail.python.org/pipermail/python-3000/2006-May/002103.html>

[^16]: <https://mail.python.org/pipermail/python-3000/2006-May/002091.html>

[^17]: <https://mail.python.org/pipermail/python-3000/2006-May/001972.html>

[^18]: <https://mail.python.org/pipermail/python-3000/2006-May/002105.html>

[^19]: <https://mail.python.org/pipermail/python-3000/2006-May/002209.html>

[^20]: <https://mail.python.org/pipermail/python-3000/2006-June/002438.html>

[^21]: <https://mail.python.org/pipermail/python-3000/2006-August/002895.html>

[^22]: <https://mail.python.org/pipermail/python-ideas/2007-January/000032.html>

[^23]: <https://mail.python.org/pipermail/python-list/2006-December/420645.html>
