---
pep: 842
title: Module Exports
author:
- Peter Bierma <peter@python.org>
discussions_to: https://discuss.python.org/t/108460
status: Draft
type: Standards Track
created: 25-Jul-2026
python_version: '3.16'
post_history:
- '`24-Jul-2026 <https://discuss.python.org/t/108266/9>`__'
- '`31-Jul-2026 <https://discuss.python.org/t/108353>`__'
- '`07-Aug-2026 <https://discuss.python.org/t/108460>`__'
python_status: Draft
url: https://peps.python.org/pep-0842/
source_path: https://github.com/python/peps/blob/main/peps/pep-0842.rst
source_commit: 927b32a9b4ed161fbffe942482e9e8f24d669efe
---

# Abstract

This PEP proposes an `export` statement that modules can use to express
intent about the visibility of variables from outside the module.

For example:

``` python
# spam.py
from mypackage export name

export foo = "42"

export class Public:
   pass

class Private:
   pass
```

``` pycon
>>> import spam
>>> 'Public' in dir(spam)
True
>>> 'Private' in dir(spam)
False
>>> spam.Public
<class 'spam.Public'>
>>> spam.Private
<python-input-4>:1: ExportWarning: 'Private' is not exported by 'spam'
<class 'spam.Private'>
```

This is **not** intended to be an access modifier for Python; see
`the rationale <pep-842-not-an-access-modifier>`{.interpreted-text
role="ref"}.

# Motivation

## Module-level names need privacy

A developer is writing a Python module. The module is intended to have
one \"public\" class \-- a class that is intended for users of the
module \-- called `PublicAPI`. As part of implementing `PublicAPI`, the
developer wants to create another class, called `Helper`. However,
`Helper` is not meant to be public in the same way that `PublicAPI` is
public. `Helper` is supposed to only be used by the developer of the
module \-- a \"private\" API.

Nonetheless, the developer declares the two classes as such:

``` python
# spam.py
class Helper:
   ...

class PublicAPI:
   ...
```

The problem with this is that `Helper` comes with no indication that
it\'s not a public API. It shows up in autocomplete by language servers,
the `dir`{.interpreted-text role="func"} function, Python\'s interactive
`help`{.interpreted-text role="func"} function, and every other API
meant for introspection. How are users supposed to know that they
aren\'t supposed to use this?

## Prefixed names aren\'t necessarily a great solution {#pep-842-why-not-prefixed-names}

In Python, the convention for declaring private names is to prefix it
with `_`. So, the developer changes `Helper` into `_Helper`:

``` python
# spam.py
class _Helper:
   ...
```

This is generally the standard for Python libraries today, but it\'s not
clear that this is the best long term solution. This works (with some
caveats; see the sections below), but this is (subjectively) less
readable, and does require more keystrokes by the maintainer. Ideally,
users shouldn\'t be tempted to reach for private names from modules in
the first place.

However, it is acknowledged that this idea is going against 30 years of
convention; even if this PEP is accepted, it\'s expected that
\"underscored\" names (names prefixed with a leading `_`) will remain a
staple of Python for years to come. The purpose of this PEP is not to
eliminate the need for `_` in module-level names, but instead to clear
up corner cases where a private name is ambiguous or tempting. In other
words, this PEP is intended to improve expressiveness and clarity with
private APIs, *not* to add brand new functionality.

### It\'s not always clear where names need prefixing

Python defines names through many different constructs, some of which
are not always clear or intuitive to the developer. As a result, it can
be difficult to remember where names need to be prefixed. To put this
issue into perspective, imagine that a developer wants to import some
other modules in their code:

``` python
# spam.py
import argparse
import asyncio
import tabnanny
```

In the above example, the `spam` module will have `argparse`, `asyncio`,
and `tabnanny` as seemingly public attributes. In practice, this is not
good for a maintainer, because maintainers may want to remove and change
imports as they please, so these attributes should not be treated as
public APIs.

Python\'s standard library currently sidesteps this problem through a
note in the backwards compatibility policy (`387`{.interpreted-text
role="pep"}) that states that imported modules are not considered public
APIs and may change at any time, but unfortunately, users are unable to
determine this without directly reading the backwards compatibility
policy, which is not a common thing to do. The solution to this is to
also prefix every imported name with `_`:

``` python
# spam.py
import argparse as _argparse
import asyncio as _asyncio
import tabnanny as _tabnanny
```

But, again, this sprinkles the code with even more underscored names,
and doesn\'t necessarily send a crystal-clear message that the name is
private; see the next section.

### Prefixed names are not a universal rule {#pep-842-prefixed-public}

As modules evolve, some underscored names are made public, either
because users did not clearly understand that an underscore indicated
instability, or because users found useful functionality in a module\'s
private API, and nothing was discouraging them from using it.

In the standard library, a prime example of this is the
`ctypes`{.interpreted-text role="mod"} module. `ctypes` is full of
stable APIs that are subject to Python\'s backwards compatibility
policy, but contain a leading underscore. For example:

1.  `ctypes._CFuncPtr`{.interpreted-text role="class"}
2.  `ctypes._CData`{.interpreted-text role="class"}
3.  `ctypes._Pointer`{.interpreted-text role="class"}

This sends the wrong message to consumers of the API. When seeing things
like this in a codebase, it makes it seem like the code is opting out of
backwards compatibility, or that an underscored name does not mean
\"private\" in the module. In both cases, consumers are inclined to
reach for more private names (because there\'s no apparent consequence
for doing so), making this problem worse.

Modules aren\'t immune to this problem either. The standard
`_thread`{.interpreted-text role="mod"} module, for example, is prefixed
with `_` while being public.

### Some libraries have native counterparts

In some cases, prefixing an import with `_` makes it ambiguous, because
some complicated modules come with
`extension modules <extension module>`{.interpreted-text role="term"}
that provide access to native functionality or otherwise speed up the
module in some way. These native modules are often prefixed with a
leading underscore.

For example, in `CPython`{.interpreted-text role="term"}, the
`asyncio`{.interpreted-text role="mod"} module has a private `_asyncio`
accelerator module, so a reader seeing `_asyncio` may take it to mean
the C accelerator and not the normal module.

## Imports are suggested by language servers and linters

Circling back to the issue described earlier, imports defined at the
module-level are visible as \"public\" names to the API surface. In
fact, when developing a module, the autocomplete provided by language
servers will often suggest importing modules that were also imported by
that module. So, not only are users not prevented from accessing
seemingly-public imports, they may be *encouraged* to do so by their
language server! (This problem applies to any name that is meant to be
private; it\'s just that imports are a particularly common case for this
to occur.)

### Real-world cases

This is not a hypothetical problem. There are many real examples of this
causing issues in practice.

:::: note
::: title
Note
:::

Special thanks to Hugo van Kemenade for [compiling this
list](https://discuss.python.org/t/108353/66).
::::

#### `os.errno`

In Python 3.7, an import to the `errno`{.interpreted-text role="mod"}
module was removed from `os`{.interpreted-text role="mod"}. This caused
a lot of breakage:

- [python/cpython#77847](https://github.com/python/cpython/issues/77847)
- [Qiskit/qiskit#1253](https://github.com/Qiskit/qiskit/issues/1253)
- [uxlfoundation/oneMath#68](https://github.com/uxlfoundation/oneMath/issues/68)
- [intel/bmap-tools#34](https://github.com/intel/bmap-tools/issues/34)
- [Red Hat Bug
  1583196](https://bugzilla.redhat.com/show_bug.cgi?id=1583196)

#### `botocore.vendored`

The [botocore](https://github.com/boto/botocore) package had vendored
dependencies under the `botocore.vendored` namespace, which ended up
being [relied upon by
users](https://github.com/search?q=%22botocore.vendored.requests.packages%22&type=code):

- [boto/botocore#1466](https://github.com/boto/botocore/pull/1466)
- [AWS Developer Tools
  Blog](https://aws.amazon.com/blogs/developer/removing-the-vendored-version-of-requests-from-botocore/)
- [aws/aws-cli#4082](https://github.com/aws/aws-cli/issues/4082)

#### SciPy and pandas

Both the [SciPy](https://scipy.org/) and
[pandas](https://pandas.pydata.org/) packages had other packages visible
at the module-level, which had to be deprecated and removed due to
third-party usage:

- [scipy/scipy#14889](https://github.com/scipy/scipy/issues/14889)
- [scipy/scipy#19067](https://github.com/scipy/scipy/pull/19067)
- [pandas-dev/pandas#30296](https://github.com/pandas-dev/pandas/issues/30296)
- [tdda/tdda#21](https://github.com/tdda/tdda/issues/21)

#### scikit-learn

The [scikit-learn](https://scikit-learn.org/stable/) package vendored
`six` and `joblib`, which downstream packages then used and were broken
in v0.23:

- [scikit-learn/scikit-learn#12916](https://github.com/scikit-learn/scikit-learn/pull/12916)
- [scikit-learn-contrib/skope-rules#41](https://github.com/scikit-learn-contrib/skope-rules/issues/41)
- [shubhomoydas/ad_examples#8](https://github.com/shubhomoydas/ad_examples/issues/8)
- [Kaggle Product
  Feedback](https://www.kaggle.com/discussions/product-feedback/158412)

### Linters cannot fight against imports

As a solution to the above problem, one might suggest that linters
should simply warn against importing modules from another module. The
primary issue with this is that this pattern is particularly common in
`__init__.py` files to move all packages into one namespace. For
example:

``` 
# __init__.py

from my_package import subpackage_1
from my_package import subpackage_2
# etc
```

Linters have no language-level way to distinguish this pattern from
\"standard\" imports. As a solution, many linters use
`import name as name` to identify intentional re-exports, but this
pattern is only a convention. For example, the above `__init__.py` would
be rewritten as this:

``` 
# __init__.py

from my_package import subpackage_1 as subpackage_1
from my_package import subpackage_2 as subpackage_2
# etc
```

Not only is this redundant (and a violation of the [DRY
principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)),
it\'s confusing! Python\'s official documentation does not document this
pattern for re-exports (because it\'s not defined by the language and is
only a convention enforced by linters), so the packages that do this are
primarily just \"in the know\".

But, because this is only a convention, linters can\'t enforce the
negative case; if an import is not given the `name as name` treatment, a
linter can\'t necessarily assume that an import is not a re-export.

## We want to be nice to users, not shrug them away

When a user decides to use a private API, accidentally or not, they will
inevitably be broken by the library author. In many cases, this results
in a bug report asking for the API to be fixed or restored to prevent
downstream breakage. In this case, the library maintainer has to make a
decision:

1.  Tell the user that they\'re in the wrong for using it, and allow the
    breakage to take place.
2.  Commit to maintaining the private API as public, increasing the
    burden on themselves and encountering some of the problems described
    in `the motivation <pep-842-prefixed-public>`{.interpreted-text
    role="ref"}.

This PEP is not intended to solve this problem entirely, but instead is
meant to mitigate it by making it much clearer that a user is accessing
a private name; in other words, this PEP wants to decrease (or
eliminate) the amount of accidental private API usage in practice. By
accessing a private API, the user must make a conscious decision to do
so.

### Library consumers use runtime introspection for documentation

A counterargument to the above section is that a library should clearly
document what is private and what is public. In theory, yes, but in
practice, users don\'t read the documentation in full.

A common practice when designing APIs is to design for intuition. If an
API is named and placed well, then a user often won\'t need to reach for
the documentation. Python is no exception to this.

When prototyping, it\'s typical for someone to use
`dir`{.interpreted-text role="func"} or `help`{.interpreted-text
role="func"} in Python\'s interactive `REPL`{.interpreted-text
role="term"} to look for attributes that are useful to them. In this
case, if something is intuitive enough for the user, they will simply
reach for it without checking the documentation first. In a language as
dynamic as Python, the way people consume APIs is also dynamic.

## `__all__` is only a convention

The fundamental issue here is that Python has no way to express which
names in a module are \"private\" or \"public\". Prefixing is an option,
but given the reasons above, it\'s not always a bulletproof solution for
library authors.

Currently, the other convention for expressing which names are public is
done through a module\'s `__all__` variable. This has two major
downsides:

1.  `__all__` often gets out of sync, because as developers add, change,
    or remove names from their module, there is often nothing pushing
    them towards changing `__all__`, because again, using it to list
    public names is only a convention and not enforced by anything.
2.  `__all__` is not always exhaustive. See the `rejected ideas
    <pep-842-all-for-exports>`{.interpreted-text role="ref"} for
    examples on where the items in `__all__` might only be a subset of
    the \"public\" names in a module. In short, it can be difficult to
    control namespace pollution and declare all public names in
    `__all__` simultaneously.

This PEP intends to solve both of these problems with a new `__export__`
variable and `export` statement.

# Specification

## The `ExportWarning` type

A new warning category, called `ExportWarning`, is added to the
`builtins`{.interpreted-text role="mod"} module. `ExportWarning`
inherits from `Warning`{.interpreted-text role="class"} and defines no
other attributes.

Though allowed, it is not intended to be emitted by user code; instead,
it is meant for emission by a
`module <types.ModuleType>`{.interpreted-text role="class"} object when
accessing a name that is not in `__export__`; see
`pep-842-attribute-access`{.interpreted-text role="ref"}.

### C API

:::: note
::: title
Note
:::

This section is specific to `CPython`{.interpreted-text role="term"}.
::::

The `ExportWarning` class will be added to the public C API headers
under the name `PyExc_ExportWarning`. As with all other global warning
categories, it will be in the
`Stable ABI <stable-abi>`{.interpreted-text role="ref"} and will be
`immortal`{.interpreted-text role="term"} at runtime.

## `__export__` variables

### Requirements {#pep-842-export-requirements}

When defined in a module\'s global scope, `__export__` must be assigned
to an object that implements `~object.__contains__`{.interpreted-text
role="meth"} or `~object.__iter__`{.interpreted-text role="meth"} such
that `str`{.interpreted-text role="class"} objects can be checked for
containment on it. In other words, the expression
`str_instance in __export__` should not raise an exception. In practice,
this means that `__export__` will typically be a
`tuple`{.interpreted-text role="class"} or a `list`{.interpreted-text
role="class"} object:

``` python
__export__ = ["name1", "name2", "name3"]
__export__ = ("name1", "name2", "name3")
__export__ = {"name1", "name2", "name3"}
```

Again, however, the only requirement for `__export__` is that the
`in`{.interpreted-text role="keyword"} operator is valid on it for
instances of `str`. For example, some more exotic types are also valid
assignments for `__export__`:

``` python
__export__ = {"name": 0}
# '"name" in __export__' is valid, so this is okay
```

:::: note
::: title
Note
:::

When using one of the `export` syntax constructs as described later,
`__export__` must always be a `list`, or otherwise be an object with an
`append` method that is always valid for `str` objects.
::::

#### Item requirements

It is not required that the strings inside `__export__` are actually
names defined in the module (because it is not required for `__export__`
to be a `~collections.abc.Sequence`{.interpreted-text role="class"} or
similar, so there is no way to validate all values in `__export__`),
though there is no practical reason to do so. For example, the following
is valid (as in, it will not generate an exception at runtime), with one
caveat:

``` python
__export__ = ["does not exist"]
```

The caveat is that this will raise an exception when used with a
wildcard import (`from module import *`), because `__all__` is
implicitly set by `__export__`; see
`pep-842-implicit-all`{.interpreted-text role="ref"}.

### Module attribute access {#pep-842-attribute-access}

When `__export__` is present in a module\'s globals, all access to
attributes present on the module object will also check if the attribute
name is present in `__export__` (via `__contains__` or through
iteration, as specified previously). If the attribute name is not
present in `__export__`, then an `ExportWarning` is emitted. For
example:

``` python
# spam.py
a = 42
b = 24

__export__ = ["a"]
```

``` pycon
>>> import spam
>>> spam.a
42
>>> spam.b
<python-input-2>:1: ExportWarning: 'b' is not exported by 'spam'
24
```

:::: note
::: title
Note
:::

This also affects `from` imports, because those use the same attribute
access mechanism.
::::

#### Dunder names

This does not apply to `dunder`{.interpreted-text role="term"} names;
attributes such as `~object.__dict__`{.interpreted-text role="attr"} and
`~module.__file__`{.interpreted-text role="attr"} will always be
accessible on the module through attribute access, even if they are not
included in the module\'s `__export__`. For example:

``` python
# spam.py
__export__ = []
```

``` pycon
>>> import spam
>>> spam.__name__
'spam'
```

### Module `__getattr__` functions

The behavior of `__export__` cannot be overridden by a module\'s
`~module.__getattr__`{.interpreted-text role="meth"} function, as
`__getattr__` functions are only invoked for undefined names on modules.
However, in cases where a module `__getattr__` is invoked, `__export__`
has no effect. For example:

``` python
# spam.py
__export__ = ["exported"]

exported = 42

def __getattr__(name):
   if name == "exported":
      # This is never triggered!
      raise ImportError()

   if name == "hello":
      # "hello" is never put through the __export__ filter
      return 42

   raise AttributeError(f"{__name__!r} has no attribute {name!r}")
```

``` pycon
>>> import spam
>>> spam.__export__
["exported"]
>>> spam.exported
42
>>> spam.hello
42
```

### `__dir__` behavior

On a module with `__export__`, the module\'s
`~module.__dir__`{.interpreted-text role="meth"} function will be
modified to exclude names that are not in the module\'s `__export__`. As
with attributes, this behavior does not apply to dunder names; those
will always be included in the output of `dir()`, regardless of whether
the names are included in `__export__`. For example:

``` python
# spam.py
class Public:
   ...

class Private:
   ...

__export__ = ["Public"]
```

``` pycon
>>> import spam
>>> dir(spam)
['Public', '__builtins__', '__doc__', '__export__', '__file__', '__loader__', '__name__', '__package__', '__spec__']
```

#### User-defined module `__dir__` functions

If a module defines its own `__dir__` method, it takes precedence over
this behavior. It is up to the implementer of `__dir__` to exclude names
that are not present in `__export__`. For example:

``` python
# spam.py
a = 42
b = 24

__export__ = ['a']

def __dir__():
   return list(globals().keys())
```

``` pycon
>>> import spam
>>> dir(spam)
[..., 'a', 'b']
```

### Implicit `__all__` definitions {#pep-842-implicit-all}

If a module defines `__export__` but does not define
`~module.__all__`{.interpreted-text role="attr"}, then `__all__` will be
assigned to `__export__`. To visualize:

``` python
# spam.py
a = 42
b = 24
c = 'c'

__export__ = ['a', 'b']
# __all__ is implicitly set to ['a', 'b'], so 'c' will not be included in
# wildcard imports.
```

``` pycon
>>> from spam import *
>>> a
42
>>> b
24
>>> c
Traceback (most recent call last):
  File "<python-input-3>", line 1, in <module>
    c
NameError: name 'c' is not defined
```

This means that the
`previously specified requirements <pep-842-export-requirements>`{.interpreted-text
role="ref"} for `__export__` are not exhaustive, as `__export__` in this
case must also be a valid `__all__`. For example, including a name that
does not exist in `__export__` will break wildcard imports:

``` python
# spam.py
a = 42
__export__ = ['a', 'noexist']
```

``` pycon
>>> from spam import *
Traceback (most recent call last):
  File "<python-input-0>", line 1, in <module>
    from spam import *
AttributeError: module 'spam' has no attribute 'noexist'
```

### Semantic implementation

For a module, defining `__export__` is roughly equivalent to adding the
following code:

``` python
if "__all__" not in globals():
   __all__ = __export__

def _is_dunder_name(name):
    return (len(name) > 4) and name.startswith("__") and name.endswith("__")

# Attributes not in the __dict__ fall back to the normal lookup
def __getattribute__(name):
    try:
        value = globals()[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    if _is_dunder_name(name):
        return value

    if name not in __export__:
        __import__("warnings").warn(f"{name!r} is not exported by {__name__!r}", ExportWarning, stacklevel=1)

    return value

_module = sys.modules[__name__]
# This is a spooky magic function -- pretend it exists for example's sake
patch(_module, '__getattribute__', __getattribute__)

def __dir__():
   names = []
   for name in globals().keys():
      if (name in __export__) or _is_dunder_name(name):
         names.append(name)
   return names
```

## Exporting names

### Grammar

The grammar is changed to allow for the standalone `export` statement
and `export` assignments:

``` peg
export_stmt[stmt_ty]:
   | "export" ','.NAME+
   | "export" assignment

simple_stmt[stmt_ty] (memo):
   | assignment
   | &"export" export_stmt
```

Note that augmented assignments (`x += y`) are disallowed through a PEG
action at compile time.

### Standalone exports

A standalone `export` statement is a shorthand for appending one or more
names to a global `__export__` list.

When the `export` statement is used, the interpreter first checks if
each name exists in the global scope. If any do not exist, a
`NameError`{.interpreted-text role="class"} is raised. The interpreter
then checks if an `__export__` variable exists in the global namespace.
If not, it is assigned to an empty `list`{.interpreted-text
role="class"} object. Then, for each name used in the `export`
statement, a `str`{.interpreted-text role="class"} containing the name
of the variable is passed as the first positional argument to the
`__export__.append <list.append>`{.interpreted-text role="meth"} method.

To visualize, the following code:

``` python
export NAME1, NAME2
```

is semantically equivalent to:

``` python
if "NAME1" not in globals():
   raise NameError(...)

if "NAME2" not in globals():
   raise NameError(...)

try:
   __export__
except NameError:
   __export__ = []

__export__.append("NAME1")
__export__.append("NAME2")
```

The `export` statement is only allowed in the global namespace; using it
elsewhere (such as inside of a function body) raises a
`SyntaxError`{.interpreted-text role="class"} during compilation.

### Export assignments

When an assignment statement is prefixed with `export`, the name is
defined and then `export`ed.

As an example, the following code:

``` python
export NAME1, NAME2 = VALUE1, VALUE2
```

is semantically equivalent to:

``` python
NAME1 = VALUE1
NAME2 = VALUE2
export NAME1, NAME2
```

\"Export assignment\" statements are valid when used with standard
assignment statements (`a = b`, `a, b = c, d`, etc), and individual
assignments that contain a type annotation (`a: type = b`; in contrast,
a standalone `export a: type` is not valid). For example, each of the
following are valid:

``` python
export hello = "world"
export my, hovercraft = "full of", "eels"
export types_work_too: int = 42
```

The following are NOT valid:

``` python
export hello: str
export my: str, hovercraft: str = "full of", "eels"
export name := "walrus"
export hello += "world"
```

## Exporting functions and classes

### Grammar

``` peg
export_compound_stmt[stmt_ty]:
   | "export" (function_def | class_def)

compound_stmt[stmt_ty]:
   | &"export" export_compound_stmt
```

### Behavior

A function definition or class definition statement can be prefixed with
`export` to automatically export the name.

To visualize, the following code:

``` python
export def NAME1():
   ...

export class NAME2:
   ...
```

is semantically equivalent to:

``` python
def NAME1():
   ...
export NAME1

class NAME2:
   ...
export NAME2
```

As with assignments and standalone exports, using `export def` or
`export class` outside of the global scope will raise a
`SyntaxError`{.interpreted-text role="class"} at compile time.

There are no other caveats; all other syntax features of classes and
functions work when prefixed with `export`.

## The module re-export statement

### Grammar

A new rule is added and the existing `import_from` rule is modified:

``` peg
import_or_export[expr_ty]:
   | 'import'
   | "export"

import_from[stmt_ty]:
   | "lazy"? 'from' ('.' | '...')* dotted_name import_or_export import_from_targets
   | "lazy"? 'from' ('.' | '...')+ import_or_export import_from_targets
```

### Behavior

The \"module re-export statement\" is an extension to the behavior of
the `from` imports; it does the exact same thing, but also `export`s
each of the imported names.

For example, the following code:

``` python
from MODULE export NAME1, NAME2
```

is semantically equivalent to:

``` python
from MODULE import NAME1, NAME2
export NAME1, NAME2
```

Similar to the other `export` constructs, this must occur at the
module-level; using it elsewhere is a `SyntaxError`{.interpreted-text
role="class"}.

Lazy imports, as described by `810`{.interpreted-text role="pep"}, are
also allowed to be used with `from` exports. For example:

``` python
lazy from foo export bar
```

The existing rules for lazy imports apply here as well.

# Rationale

## This is not an access modifier {#pep-842-not-an-access-modifier}

This PEP does not aim to be a mechanism for preventing access to private
attributes in modules. The `ExportWarning` can be filtered away,
disabled, or bypassed (such as by accessing attributes through the
module\'s `__dict__`).

This is by design. Python does not include access modifiers as a
language feature for a reason. To
[quote](https://discuss.python.org/t/104994/2) Eric Smith: \"Access to
internals of other classes is a feature when you need it\". This PEP
does not intend to change this convention, nor should it be interpreted
as an indication that Python is tending toward the direction of true
access modifiers.

Instead, the intention of this PEP is to improve clarity when inspecting
modules at runtime, which should, in turn, improve the maintainer
experience of Python modules in the long term.

# Backwards Compatibility

## This does not require changes to existing code

The functionality described in this PEP is only activated when a module
defines `__export__` in the global scope (or by using the `export`
statement, which implicitly defines `__export__`). Modules that do not
do this will experience the current behavior, where every name is
exported by default.

## `__export__` overloads

This PEP has the potential to break users who were already defining
global variables called `__export__`. That said, the Python language
reference `explicitly forbids <id-classes>`{.interpreted-text
role="ref"} users from doing this in the first place.

## `export` (soft) keyword

`export`, as proposed by this PEP, is a
`soft keyword <soft-keywords>`{.interpreted-text role="ref"}. It does
*not* break backwards compatibility, meaning that existing code using
\"`export`\" as a variable name will continue to work.

## Relation to `-W error`

While this PEP does not break any existing applications, it may break
tests for downstream users of packages who choose to adopt this PEP, as
many popular testing frameworks, such as
[pytest](https://docs.pytest.org/en/stable/), run with
warnings-as-errors enabled by default.

# Security Implications

This PEP has no known security implications.

# How to Teach This

Both the `export` statement and the `__export__` variable will be
documented as part of the language standard.

## Maintaining backwards compatible codebases

To help adoption, it will be recommended that users define both
`__all__` and `__export__` in their modules. This allows code on Python
3.16+ to get the proper export behavior, while older versions still keep
their `__all__` attribute. In practice, this should look something like
this:

``` python
__all__ = ["hovercraft"]
__export__ = __all__ + ["eels"]
```

Or, if the package\'s `__all__` is equivalent to `__export__`:

``` python
__export__ = __all__
```

# Reference Implementation

A reference implementation of this PEP can be found
[here](https://github.com/python/cpython/compare/main...ZeroIntensity:cpython:pep-842/reference-impl).

## Performance

The reference implementation does not currently implement any
optimizations to reduce the overhead of the `__export__` lookup or
iteration, meaning that there is likely some overhead. However, if this
PEP is accepted, optimizations will be implemented before the feature
lands in `CPython`{.interpreted-text role="term"}.

# Rejected Ideas

## Reuse `__all__` for exports {#pep-842-all-for-exports}

Instead of adding a new `__export__` variable, an alternative was to
reuse `__all__` for names.

This was ultimately decided against because it seemed clear that there
were cases where a name could be in `__export__`, but not in `__all__`.
The primary example for this case was with static typing. For example, a
module may define several type aliases that would pollute a namespace if
used with a wildcard import, so the developer chooses to not include
them in `__all__`, but users of static typing will still want access to
these type aliases for annotating their own code.

In addition, it\'s not clear that there\'s any good spelling for this
behavior that covers all cases. The \"obvious\" solution is to add a new
`future statement <python:future>`{.interpreted-text role="ref"} that
makes `__all__` more strict, but that isn\'t backwards compatible;
codebases wanting to opt-in to the behavior described by this PEP must
use a spelling that works on all supported Python versions in order to
keep their code working on older versions, so any solutions that add
special functionality to `__all__` generally will not work.

## Raising an exception upon accessing unexported attributes

This PEP initially proposed raising an `ImportError`{.interpreted-text
role="exc"} upon accessing module attributes that were not listed in
`__export__`. For example:

``` pycon
>>> import module
>>> module.unexported
Traceback (most recent call last):
  File "<python-input-1>", line 1, in <module>
    module.unexported
ImportError: 'unexported' is not exported by 'module'
```

This caused a lot of concern, as many were fundamentally uncomfortable
with the idea of introducing any notion of \"private attributes\" in
Python. The purpose of this proposal is to improve *expression* of
private variables, not *security*. As such, this proposal switched to
emitting warnings when accessing unexported names.

## Introduce `__export__` on its own

The original revision of this proposal included `__export__` as a
standalone variable and did not provide any new syntax. The appeal of
this was that it was backwards compatible; projects could simply write
`__export__ = __all__`, and then when users upgraded to a version that
supported `__export__`, they would get the documentation and enforcement
benefits described by this PEP.

It was eventually decided that this was too conservative, because while
`__export__` was compatible with `__all__`, it shared many of the same
problems with it, such as forgetting to add or remove items from the
list.

To [quote](https://discuss.python.org/t/108353/46) Guido van Rossum:

> But the ergonomics are similar to those of `__all__`, and those are
> bad. It's too easy to forget to add (or remove!) something to the
> list, and it\'s distracting to have to update the export info in a
> totally different part of a file than the definition of the exported
> thing.

## Add a `private` keyword for class bodies

During discussion of this proposal, it was suggested to add a `private`
keyword for use in classes. For example:

``` python
class Something:
   private def hello(self):
      print("Hello, world!")
```

This was rejected primarily because it does not have a clear benefit
over the existing
`name mangling behavior <private-name-mangling>`{.interpreted-text
role="ref"} (using the `__` prefix), which also solves many of the
problems described in the motivation of this PEP.

Additionally, this is much more difficult to implement. The author\'s
reference implementation involved new access protocols, disabling
optimizations, and overall much more complexity when compared to the
simple modification to the default `module.__getattr__` behavior
required by `__export__`.

## Add `public` and `private` decorators as builtins

Instead of adding a new `export` keyword, it was suggested to add
`private` and `public` decorators, based on Barry Warsaw\'s
[atpublic](https://public.readthedocs.io/en/stable/) package, to the
`builtins`{.interpreted-text role="mod"} module.

The decorators would have provided the same documentation aspect of this
PEP, and potentially the same enforcement aspect, without the need for
new syntax. For example:

``` python
@public
class MyPublicClass:
   ...

# Or
@private
class MyPrivateClass:
   ...
```

This is the author\'s next preferred solution after `export` syntax, but
it does come with some caveats. In particular, there\'s no easy way to
export simple variables without duplicating the name, which many dislike
due to the violation of the DRY principle.

# Open Issues

TBD.

# Acknowledgements

Thanks to Hugo van Kemenade and Savannah Ostrowski for
[inspiring](https://github.com/python/cpython/pull/154639#discussion_r3647508463)
the idea behind this PEP.

In addition, the design behind this PEP was largely influenced by
discussion and ideas from many people, including, but not limited to,
Guido van Rossum, Paul Moore, Steve Dower, and Barry Warsaw.

# Change History

- 05-Aug-2026
  - Added an `export` statement.
  - Added the `ExportWarning` builtin type, which is now emitted instead
    of a `RuntimeWarning`{.interpreted-text role="exc"} when accessing
    unexported attributes.
- 01-Aug-2026
  - Accessing an unexported attribute now emits a
    `RuntimeWarning`{.interpreted-text role="exc"} instead of raising an
    `ImportError`{.interpreted-text role="exc"}.
  - Significantly overhauled the motivation section.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
