---
pep: 764
title: Inline typed dictionaries
author:
- Victorien Plot <contact@vctrn.dev>
sponsor: Eric Traut <erictr at microsoft.com>
discussions_to: https://discuss.python.org/t/78779
status: Draft
type: Standards Track
topic: Typing
created: 25-Oct-2024
python_version: '3.15'
post_history:
- '`29-Jan-2025 <https://discuss.python.org/t/78779>`__'
python_status: Draft
url: https://peps.python.org/pep-0764/
source_path: https://github.com/python/peps/blob/main/peps/pep-0764.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:31+00:00'
---

# Abstract

`589`{.interpreted-text role="pep"} defines a
`class-based <typing:typeddict-class-based-syntax>`{.interpreted-text
role="ref"} and a
`functional syntax <typing:typeddict-functional-syntax>`{.interpreted-text
role="ref"} to create typed dictionaries. In both scenarios, it requires
defining a class or assigning to a value. In some situations, this can
add unnecessary boilerplate, especially if the typed dictionary is only
used once.

This PEP proposes the addition of a new inline syntax, by subscripting
the `~typing.TypedDict`{.interpreted-text role="class"} type:

    from typing import TypedDict

    def get_movie() -> TypedDict[{'name': str, 'year': int}]:
        return {
            'name': 'Blade Runner',
            'year': 1982,
        }

# Motivation

Python dictionaries are an essential data structure of the language.
Many times, it is used to return or accept structured data in functions.
However, it can get tedious to define
`~typing.TypedDict`{.interpreted-text role="class"} classes:

- A typed dictionary requires a name, which might not be relevant.
- Nested dictionaries require more than one class definition.

Taking a simple function returning some nested structured data as an
example:

    from typing import TypedDict

    class ProductionCompany(TypedDict):
        name: str
        location: str

    class Movie(TypedDict):
        name: str
        year: int
        production: ProductionCompany


    def get_movie() -> Movie:
        return {
            'name': 'Blade Runner',
            'year': 1982,
            'production': {
                'name': 'Warner Bros.',
                'location': 'California',
            }
        }

# Rationale

The new inline syntax can be used to resolve these problems:

    def get_movie() -> TypedDict[{'name': str, 'year': int, 'production': TypedDict[{'name': str, 'location': str}]}]:
        ...

While less useful (as the functional or even the class-based syntax can
be used), inline typed dictionaries can be assigned to a variable, as an
alias:

    InlineTD = TypedDict[{'name': str}]

    def get_movie() -> InlineTD:
        ...

# Specification

The `~typing.TypedDict`{.interpreted-text role="class"} special form is
made subscriptable, and accepts a single type argument which must be a
`dict`{.interpreted-text role="class"}, following the same semantics as
the
`functional syntax <typing:typeddict-functional-syntax>`{.interpreted-text
role="ref"} (the dictionary keys are strings representing the field
names, and values are valid
`annotation expressions <typing:annotation-expression>`{.interpreted-text
role="ref"}). Only the comma-separated list of `key: value` pairs within
braces constructor (`{k: <type>}`) is allowed, and should be specified
directly as the type argument (i.e. it is not allowed to use a variable
which was previously assigned a `dict`{.interpreted-text role="class"}
instance).

Inline typed dictionaries can be referred to as *anonymous*, meaning
they don\'t have a specific name (see the [runtime
behavior](Runtime behavior) section).

It is possible to define a nested inline dictionary:

    Movie = TypedDict[{'name': str, 'production': TypedDict[{'location': str}]}]

    # Note that the following is invalid as per the updated `type_expression` grammar:
    Movie = TypedDict[{'name': str, 'production': {'location': str}}]

Although it is not possible to specify any class arguments such as
`total`, any `typing:type qualifier`{.interpreted-text role="term"} can
be used for individual fields:

    Movie = TypedDict[{'name': NotRequired[str], 'year': ReadOnly[int]}]

Inline typed dictionaries are implicitly *total*, meaning all keys must
be present. Using the `~typing.Required`{.interpreted-text role="data"}
type qualifier is thus redundant.

Type variables are allowed in inline typed dictionaries, provided that
they are bound to some outer scope:

    class C[T]:
        inline_td: TypedDict[{'name': T}]  # OK, `T` is scoped to the class `C`.

    reveal_type(C[int]().inline_td['name'])  # Revealed type is 'int'


    def fn[T](arg: T) -> TypedDict[{'name': T}]: ...  # OK: `T` is scoped to the function `fn`.

    reveal_type(fn('a')['name'])  # Revealed type is 'str'


    type InlineTD[T] = TypedDict[{'name': T}]  # OK, `T` is scoped to the type alias.


    T = TypeVar('T')

    InlineTD = TypedDict[{'name': T}]  # OK, same as the previous type alias, but using the old-style syntax.


    def func():
        InlineTD = TypedDict[{'name': T}]  # Not OK: `T` refers to a type variable that is not bound to the scope of `func`.

Inline typed dictionaries can be extended:

    InlineTD = TypedDict[{'a': int}]

    class SubTD(InlineTD):
        pass

## Typing specification changes

The inline typed dictionary adds a new kind of
`typing:type expression`{.interpreted-text role="term"}. As such, the
`~expression-grammar:type_expression`{.interpreted-text
role="external+typing:token"} production will be updated to include the
inline syntax:

::: {.productionlist  | <TypedDict> '[' '{' (string="':' `~expression-grammar:annotation_expression` ',')* '}' ']'"}
inline-typed-dictionaries-grammar new-type_expression:
[\~expression-grammar:type_expression]{.title-ref}
:::

> : (where string is any string literal)

## Runtime behavior

Creating an inline typed dictionary results in a new class, so `T1` and
`T2` are of the same type:

    from typing import TypedDict

    T1 = TypedDict('T1', {'a': int})
    T2 = TypedDict[{'a': int}]

As inline typed dictionaries are meant to be *anonymous*, their
`~type.__name__`{.interpreted-text role="attr"} attribute will be set to
the `<inline TypedDict>` string literal. In the future, an explicit
class attribute could be added to make them distinguishable from named
classes.

Although `~typing.TypedDict`{.interpreted-text role="class"} is
documented as a class, the way it is defined is an implementation
detail. The implementation will have to be tweaked so that
`~typing.TypedDict`{.interpreted-text role="class"} can be made
subscriptable.

# Backwards Compatibility

This PEP does not bring any backwards incompatible changes.

# Security Implications

There are no known security consequences arising from this PEP.

# How to Teach This

The new inline syntax will be documented both in the
`typing`{.interpreted-text role="mod"} module documentation and the
`typing specification <typing:typed-dictionaries>`{.interpreted-text
role="ref"}.

When complex dictionary structures are used, having everything defined
on a single line can hurt readability. Code formatters can help by
formatting the inline type dictionary across multiple lines:

    def edit_movie(
        movie: TypedDict[{
            'name': str,
            'year': int,
            'production': TypedDict[{
                'location': str,
            }],
        }],
    ) -> None:
        ...

# Reference Implementation

Mypy supports a similar syntax as an
`experimental feature <mypy:mypy.--enable-incomplete-feature>`{.interpreted-text
role="option"}:

    def test_values() -> {"int": int, "str": str}:
        return {"int": 42, "str": "test"}

Support for this PEP is added in [this pull
request](https://github.com/python/mypy/pull/18889).

Pyright added support for the new syntax in version
[1.1.387](https://github.com/microsoft/pyright/releases/tag/1.1.387).

## Runtime implementation

The necessary changes were first implemented in
[typing_extensions](https://typing-extensions.readthedocs.io/en/latest/)
in [this pull
request](https://github.com/python/typing_extensions/pull/580).

# Rejected Ideas

## Using the functional syntax in annotations

The alternative functional syntax could be used as an annotation
directly:

    def get_movie() -> TypedDict('Movie', {'title': str}): ...

However, call expressions are currently unsupported in such a context
for various reasons (expensive to process, evaluating them is not
standardized).

This would also require a name which is sometimes not relevant.

## Using `dict` or `typing.Dict` with a single type argument

We could reuse `dict`{.interpreted-text role="class"} or
`typing.Dict`{.interpreted-text role="class"} with a single type
argument to express the same concept:

    def get_movie() -> dict[{'title': str}]: ...

While this would avoid having to import
`~typing.TypedDict`{.interpreted-text role="class"} from
`typing`{.interpreted-text role="mod"}, this solution has several
downsides:

- For type checkers, `dict`{.interpreted-text role="class"} is a regular
  class with two type variables. Allowing `dict`{.interpreted-text
  role="class"} to be parametrized with a single type argument would
  require special casing from type checkers, as there is no way to
  express parametrization overloads. On the other hand,
  `~typing.TypedDict`{.interpreted-text role="class"} is already a
  `special form <typing:special form>`{.interpreted-text role="term"}.
- If future work extends what inline typed dictionaries can do, we
  don\'t have to worry about impact of sharing the symbol with
  `dict`{.interpreted-text role="class"}.
- `typing.Dict`{.interpreted-text role="class"} has been deprecated
  (although not planned for removal) by `585`{.interpreted-text
  role="pep"}. Having it used for a new typing feature would be
  confusing for users (and would require changes in code linters).

## Using a simple dictionary

Instead of subscripting the `~typing.TypedDict`{.interpreted-text
role="class"} class, a plain dictionary could be used as an annotation:

    def get_movie() -> {'title': str}: ...

However, `584`{.interpreted-text role="pep"} added union operators on
dictionaries and `604`{.interpreted-text role="pep"} introduced
`union types <python:types-union>`{.interpreted-text role="ref"}. Both
features make use of the
`bitwise or (|) <python:bitwise>`{.interpreted-text role="ref"}
operator, making the following use cases incompatible, especially for
runtime introspection:

    # Dictionaries are merged:
    def fn() -> {'a': int} | {'b': str}: ...

    # Raises a type error at runtime:
    def fn() -> {'a': int} | int: ...

## Extending other typed dictionaries

Several syntaxes could be used to have the ability to extend other typed
dictionaries:

    InlineBase = TypedDict[{'a': int}]

    Inline = TypedDict[InlineBase, {'b': int}]
    # or, by providing a slice:
    Inline = TypedDict[{'b': int} : (InlineBase,)]

As inline typed dictionaries are meant to only support a subset of the
existing syntax, adding this extension mechanism isn\'t compelling
enough to be supported, considering the added complexity.

If intersections were to be added into the type system, it could cover
this use case.

# Open Issues

## Inline typed dictionaries and extra items

`728`{.interpreted-text role="pep"} introduces the concept of
`closed <typed-dict-closed>`{.interpreted-text role="ref"} type
dictionaries. If this PEP were to be accepted, inline typed dictionaries
will be *closed* by default. This means `728`{.interpreted-text
role="pep"} needs to be addressed first, so that this PEP can be updated
accordingly.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
