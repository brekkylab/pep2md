---
pep: 3152
title: Cofunctions
author:
- Gregory Ewing <greg.ewing@canterbury.ac.nz>
status: Rejected
type: Standards Track
created: 13-Feb-2009
python_version: '3.3'
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-3152/
source_path: https://github.com/python/peps/blob/main/peps/pep-3152.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:52+00:00'
---

# Abstract

A syntax is proposed for defining and calling a special type of
generator called a \'cofunction\'. It is designed to provide a
streamlined way of writing generator-based coroutines, and allow the
early detection of certain kinds of error that are easily made when
writing such code, which otherwise tend to cause hard-to-diagnose
symptoms.

This proposal builds on the \'yield from\' mechanism described in PEP
380, and describes some of the semantics of cofunctions in terms of it.
However, it would be possible to define and implement cofunctions
independently of `380`{.interpreted-text role="pep"} if so desired.

## Rejection

See
<https://mail.python.org/pipermail/python-dev/2015-April/139503.html>

# Specification

## Cofunction definitions

A new keyword `codef` is introduced which is used in place of `def` to
define a cofunction. A cofunction is a special kind of generator having
the following characteristics:

1.  A cofunction is always a generator, even if it does not contain any
    `yield` or `yield from` expressions.
2.  A cofunction cannot be called the same way as an ordinary function.
    An exception is raised if an ordinary call to a cofunction is
    attempted.

## Cocalls

Calls from one cofunction to another are made by marking the call with a
new keyword `cocall`. The expression :

    cocall f(*args, **kwds)

is semantically equivalent to :

    yield from f.__cocall__(*args, **kwds)

except that the object returned by \_\_cocall\_\_ is expected to be an
iterator, so the step of calling iter() on it is skipped.

The full syntax of a cocall expression is described by the following
grammar lines:

    atom: cocall | <existing alternatives for atom>
    cocall: 'cocall' atom cotrailer* '(' [arglist] ')'
    cotrailer: '[' subscriptlist ']' | '.' NAME

The `cocall` keyword is syntactically valid only inside a cofunction. A
SyntaxError will result if it is used in any other context.

Objects which implement \_\_cocall\_\_ are expected to return an object
obeying the iterator protocol. Cofunctions respond to \_\_cocall\_\_ the
same way as ordinary generator functions respond to \_\_call\_\_, i.e.
by returning a generator-iterator.

Certain objects that wrap other callable objects, notably bound methods,
will be given \_\_cocall\_\_ implementations that delegate to the
underlying object.

## New builtins, attributes and C API functions

To facilitate interfacing cofunctions with non-coroutine code, there
will be a built-in function `costart` whose definition is equivalent to
:

    def costart(obj, *args, **kwds):
        return obj.__cocall__(*args, **kwds)

There will also be a corresponding C API function :

    PyObject *PyObject_CoCall(PyObject *obj, PyObject *args, PyObject *kwds)

It is left unspecified for now whether a cofunction is a distinct type
of object or, like a generator function, is simply a specially-marked
function instance. If the latter, a read-only boolean attribute
`__iscofunction__` should be provided to allow testing whether a given
function object is a cofunction.

# Motivation and Rationale

The `yield from` syntax is reasonably self-explanatory when used for the
purpose of delegating part of the work of a generator to another
function. It can also be used to good effect in the implementation of
generator-based coroutines, but it reads somewhat awkwardly when used
for that purpose, and tends to obscure the true intent of the code.

Furthermore, using generators as coroutines is somewhat error-prone. If
one forgets to use `yield from` when it should have been used, or uses
it when it shouldn\'t have, the symptoms that result can be obscure and
confusing.

Finally, sometimes there is a need for a function to be a coroutine even
though it does not yield anything, and in these cases it is necessary to
resort to kludges such as `if 0: yield` to force it to be a generator.

The `codef` and `cocall` constructs address the first issue by making
the syntax directly reflect the intent, that is, that the function forms
part of a coroutine.

The second issue is addressed by making it impossible to mix coroutine
and non-coroutine code in ways that don\'t make sense. If the rules are
violated, an exception is raised that points out exactly what and where
the problem is.

Lastly, the need for dummy yields is eliminated by making the form of
definition determine whether the function is a coroutine, rather than
what it contains.

# Prototype Implementation

An implementation in the form of patches to Python 3.1.2 can be found
here:

<http://www.cosc.canterbury.ac.nz/greg.ewing/python/generators/cofunctions.html>

# Copyright

This document has been placed in the public domain.
