---
pep: 726
title: Module ``__setattr__`` and ``__delattr__``
author:
- Sergey B Kirpichev <skirpichev@gmail.com>
sponsor: Adam Turner <adam@python.org>
discussions_to: https://discuss.python.org/t/32640/
status: Rejected
type: Standards Track
created: 24-Aug-2023
python_version: '3.13'
post_history:
- '`06-Apr-2023 <https://discuss.python.org/t/25506/>`__'
- '`31-Aug-2023 <https://discuss.python.org/t/32640/>`__'
resolution: https://discuss.python.org/t/32640/32
python_status: Rejected
url: https://peps.python.org/pep-0726/
source_path: https://github.com/python/peps/blob/main/peps/pep-0726.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:05+00:00'
---

# Abstract

This PEP proposes supporting user-defined `__setattr__` and
`__delattr__` methods on modules to extend customization of module
attribute access beyond `562`{.interpreted-text role="pep"}.

# Motivation

There are several potential uses of a module `__setattr__`:

1.  To prevent setting an attribute at all (i.e. make it read-only)
2.  To validate the value to be assigned
3.  To intercept setting an attribute and update some other state

Proper support for read-only attributes would also require adding the
`__delattr__` function to prevent their deletion.

It would be convenient to directly support such customization, by
recognizing `__setattr__` and `__delattr__` methods defined in a module
that would act like normal `python:object.__setattr__`{.interpreted-text
role="py:meth"} and `python:object.__delattr__`{.interpreted-text
role="py:meth"} methods, except that they will be defined on module
*instances*. Together with existing `__getattr__` and `__dir__` methods
this will streamline all variants of customizing module attribute
access.

For example

``` python
# mplib.py

CONSTANT = 3.14
prec = 53
dps = 15

def dps_to_prec(n):
    """Return the number of bits required to represent n decimals accurately."""
    return max(1, int(round((int(n)+1)*3.3219280948873626)))

def prec_to_dps(n):
    """Return the number of accurate decimals that can be represented with n bits."""
    return max(1, int(round(int(n)/3.3219280948873626)-1))

def validate(n):
    n = int(n)
    if n <= 0:
        raise ValueError('Positive integer expected')
    return n

def __setattr__(name, value):
    if name == 'CONSTANT':
        raise AttributeError('Read-only attribute!')
    if name == 'dps':
        value = validate(value)
        globals()['dps'] = value
        globals()['prec'] = dps_to_prec(value)
        return
    if name == 'prec':
        value = validate(value)
        globals()['prec'] = value
        globals()['dps'] = prec_to_dps(value)
        return
    globals()[name] = value

def __delattr__(name):
    if name in ('CONSTANT', 'dps', 'prec'):
        raise AttributeError('Read-only attribute!')
    del globals()[name]
```

``` pycon
>>> import mplib
>>> mplib.foo = 'spam'
>>> mplib.CONSTANT = 42
Traceback (most recent call last):
  ...
AttributeError: Read-only attribute!
>>> del mplib.foo
>>> del mplib.CONSTANT
Traceback (most recent call last):
  ...
AttributeError: Read-only attribute!
>>> mplib.prec
53
>>> mplib.dps
15
>>> mplib.dps = 5
>>> mplib.prec
20
>>> mplib.dps = 0
Traceback (most recent call last):
  ...
ValueError: Positive integer expected
```

# Existing Options

The current workaround is assigning the `__class__` of a module object
to a custom subclass of `python:types.ModuleType`{.interpreted-text
role="py:class"} (see[^1]).

For example, to prevent modification or deletion of an attribute we
could use:

``` python
# mod.py

import sys
from types import ModuleType

CONSTANT = 3.14

class ImmutableModule(ModuleType):
    def __setattr__(name, value):
        raise AttributeError('Read-only attribute!')

    def __delattr__(name):
        raise AttributeError('Read-only attribute!')

sys.modules[__name__].__class__ = ImmutableModule
```

But this variant is slower (\~2x) than the proposed solution. More
importantly, it also brings a noticeable speed regression (\~2-3x) for
attribute *access*.

# Specification

The `__setattr__` function at the module level should accept two
arguments, the name of an attribute and the value to be assigned, and
return `None`{.interpreted-text role="py:obj"} or raise an
`AttributeError`{.interpreted-text role="exc"}.

``` python
def __setattr__(name: str, value: typing.Any, /) -> None: ...
```

The `__delattr__` function should accept one argument, the name of an
attribute, and return `None`{.interpreted-text role="py:obj"} or raise
an `AttributeError`{.interpreted-text role="py:exc"}:

``` python
def __delattr__(name: str, /) -> None: ...
```

The `__setattr__` and `__delattr__` functions are looked up in the
module `__dict__`. If present, the appropriate function is called to
customize setting the attribute or its deletion, else the normal
mechanism (storing/deleting the value in the module dictionary) will
work.

Defining module `__setattr__` or `__delattr__` only affects lookups made
using the attribute access syntax \-\-- directly accessing the module
globals (whether by `globals()` within the module, or via a reference to
the module\'s globals dictionary) is unaffected. For example:

``` pycon
>>> import mod
>>> mod.__dict__['foo'] = 'spam'  # bypasses __setattr__, defined in mod.py
```

or

``` python
# mod.py

def __setattr__(name, value):
   ...

foo = 'spam'  # bypasses __setattr__
globals()['bar'] = 'spam'  # here too

def f():
    global x
    x = 123

f()  # and here
```

To use a module global and trigger `__setattr__` (or `__delattr__`), one
can access it via `sys.modules[__name__]` within the module\'s code:

``` python
# mod.py

sys.modules[__name__].foo = 'spam'  # bypasses __setattr__

def __setattr__(name, value):
    ...

sys.modules[__name__].bar = 'spam'  # triggers __setattr__
```

This limitation is intentional (just as for the `562`{.interpreted-text
role="pep"}), because the interpreter highly optimizes access to module
globals and disabling all that and going through special methods written
in Python would slow down the code unacceptably.

# How to Teach This

The \"Customizing module attribute access\"[^2] section of the
documentation will be expanded to include new functions.

# Reference Implementation

The reference implementation for this PEP can be found in [CPython PR
#108261](https://github.com/python/cpython/pull/108261).

# Backwards compatibility

This PEP may break code that uses module level (global) names
`__setattr__` and `__delattr__`, but the language reference explicitly
reserves *all* undocumented dunder names, and allows \"breakage without
warning\"[^3].

The performance implications of this PEP are small, since additional
dictionary lookup is much cheaper than storing/deleting the value in the
dictionary. Also it is hard to imagine a module that expects the user to
set (and/or delete) attributes enough times to be a performance concern.
On another hand, proposed mechanism allows to override setting/deleting
of attributes without affecting speed of attribute access, which is much
more likely scenario to get a performance penalty.

# Discussion

As pointed out by Victor Stinner, the proposed API could be useful
already in the stdlib, for example to ensure that
`sys.modules`{.interpreted-text role="py:obj"} type is always a
`dict`{.interpreted-text role="py:class"}:

``` pycon
>>> import sys
>>> sys.modules = 123
>>> import asyncio
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<frozen importlib._bootstrap>", line 1260, in _find_and_load
AttributeError: 'int' object has no attribute 'get'
```

or to prevent deletion of critical `sys`{.interpreted-text
role="py:mod"} attributes, which makes the code more complicated. For
example, code using `sys.stderr`{.interpreted-text role="py:obj"} has to
check if the attribute exists and if it\'s not `None`{.interpreted-text
role="py:obj"}. Currently, it\'s possible to remove any
`sys`{.interpreted-text role="py:mod"} attribute, including functions:

``` pycon
>>> import sys
>>> del sys.excepthook
>>> 1+  # notice the next line
sys.excepthook is missing
 File "<stdin>", line 1
   1+
    ^
SyntaxError: invalid syntax
```

See [related
issue](https://github.com/python/cpython/issues/106016#issue-1771174774)
for other details.

Other stdlib modules also come with attributes which can be overridden
(as a feature) and some input validation here could be helpful.
Examples: `threading.excepthook`{.interpreted-text role="py:obj"},
`warnings.showwarning`{.interpreted-text role="py:obj"},
`io.DEFAULT_BUFFER_SIZE`{.interpreted-text role="py:obj"} or
`os.SEEK_SET`{.interpreted-text role="py:obj"}.

Also a typical use case for customizing module attribute access is
managing deprecation warnings. But the `562`{.interpreted-text
role="pep"} accomplishes this scenario only partially: e.g. it\'s
impossible to issue a warning during an attempt to *change* a renamed
attribute.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: Customizing module attribute access
    (<https://docs.python.org/3.11/reference/datamodel.html#customizing-module-attribute-access>)

[^2]: Customizing module attribute access
    (<https://docs.python.org/3.11/reference/datamodel.html#customizing-module-attribute-access>)

[^3]: Reserved classes of identifiers
    (<https://docs.python.org/3.11/reference/lexical_analysis.html#reserved-classes-of-identifiers>)
