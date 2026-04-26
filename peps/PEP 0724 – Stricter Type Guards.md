---
pep: 724
title: Stricter Type Guards
author:
- Rich Chiodo <rchiodo at microsoft.com>
- Eric Traut <erictr at microsoft.com>
- Erik De Bonte <erikd at microsoft.com>
sponsor: Jelle Zijlstra <jelle.zijlstra@gmail.com>
discussions_to: https://discuss.python.org/t/pep-724-stricter-type-guards/34124
status: Withdrawn
type: Standards Track
topic: Typing
created: 28-Jul-2023
python_version: '3.13'
post_history:
- '`30-Dec-2021 <https://mail.python.org/archives/list/typing-sig@python.org/thread/EMUD2D424OI53DCWQ4H5L6SJD2IXBHUL/>`__'
- '`19-Sep-2023 <https://discuss.python.org/t/pep-724-stricter-type-guards/34124>`__'
python_status: Withdrawn
url: https://peps.python.org/pep-0724/
source_path: https://github.com/python/peps/blob/main/peps/pep-0724.rst
source_commit: 89e04d436614f1812c88f6b1ae5afe27c09c166b
---

# Status

This PEP is withdrawn. The Typing Council was unable to reach consensus
on this proposal, and the authors decided to withdraw it.

# Abstract

`647`{.interpreted-text role="pep"} introduced the concept of a
user-defined type guard function which returns `True` if the type of the
expression passed to its first parameter matches its return `TypeGuard`
type. For example, a function that has a return type of `TypeGuard[str]`
is assumed to return `True` if and only if the type of the expression
passed to its first input parameter is a `str`. This allows type
checkers to narrow types when a user-defined type guard function returns
`True`.

This PEP refines the `TypeGuard` mechanism introduced in
`647`{.interpreted-text role="pep"}. It allows type checkers to narrow
types when a user-defined type guard function returns `False`. It also
allows type checkers to apply additional (more precise) type narrowing
under certain circumstances when the type guard function returns `True`.

# Motivation

User-defined type guard functions enable a type checker to narrow the
type of an expression when it is passed as an argument to the type guard
function. The `TypeGuard` mechanism introduced in
`647`{.interpreted-text role="pep"} is flexible, but this flexibility
imposes some limitations that developers have found inconvenient for
some uses.

Limitation 1: Type checkers are not allowed to narrow a type in the case
where the type guard function returns `False`. This means the type is
not narrowed in the negative (\"else\") clause.

Limitation 2: Type checkers must use the `TypeGuard` return type if the
type guard function returns `True` regardless of whether additional
narrowing can be applied based on knowledge of the pre-narrowed type.

The following code sample demonstrates both of these limitations.

``` python
def is_iterable(val: object) -> TypeGuard[Iterable[Any]]:
    return isinstance(val, Iterable)

def func(val: int | list[int]):
    if is_iterable(val):
        # The type is narrowed to 'Iterable[Any]' as dictated by
        # the TypeGuard return type
        reveal_type(val)  # Iterable[Any]
    else:
        # The type is not narrowed in the "False" case
        reveal_type(val)  # int | list[int]

    # If "isinstance" is used in place of the user-defined type guard
    # function, the results differ because type checkers apply additional
    # logic for "isinstance"

    if isinstance(val, Iterable):
        # Type is narrowed to "list[int]" because this is
        # a narrower (more precise) type than "Iterable[Any]"
        reveal_type(val)  # list[int]
    else:
        # Type is narrowed to "int" because the logic eliminates
        # "list[int]" from the original union
        reveal_type(val)  # int
```

`647`{.interpreted-text role="pep"} imposed these limitations so it
could support use cases where the return `TypeGuard` type was not a
subtype of the input type. Refer to `647`{.interpreted-text role="pep"}
for examples.

# Rationale

There are a number of issues where a stricter `TypeGuard` would have
been a solution:

- [Python typing issue - TypeGuard doesn\'t intersect like
  isinstance](https://github.com/python/typing/issues/1351)
- [Pyright issue - TypeGuard not eliminating possibility on
  branch](https://github.com/microsoft/pyright/issues/3450)
- [Pyright issue - Type narrowing for Literal doesn\'t
  work](https://github.com/microsoft/pyright/issues/3466)
- [Mypy issue - TypeGuard is incompatible with exhaustive
  check](https://github.com/python/mypy/issues/15305)
- [Mypy issue - Incorrect type narrowing for
  inspect.isawaitable](https://github.com/python/mypy/issues/15520)
- [Typeshed issue - asyncio.iscoroutinefunction is not a
  TypeGuard](https://github.com/python/typeshed/issues/8009)

# Specification

The use of a user-defined type guard function involves five types:

- I = `TypeGuard` input type
- R = `TypeGuard` return type
- A = Type of argument passed to type guard function (pre-narrowed)
- NP = Narrowed type (positive)
- NN = Narrowed type (negative)

``` python
def guard(x: I) -> TypeGuard[R]: ...

def func1(val: A):
    if guard(val):
        reveal_type(val)  # NP
    else:
        reveal_type(val)  # NN
```

This PEP proposes some modifications to `647`{.interpreted-text
role="pep"} to address the limitations discussed above. These
limitations are safe to eliminate only when a specific condition is met.
In particular, when the output type `R` of a user-defined type guard
function is consistent[^1] with the type of its first input parameter
(`I`), type checkers should apply stricter type guard semantics.

> ``` python
> # Stricter type guard semantics are used in this case because
> # "Kangaroo | Koala" is consistent with "Animal"
> def is_marsupial(val: Animal) -> TypeGuard[Kangaroo | Koala]:
>     return isinstance(val, Kangaroo | Koala)
>
> # Stricter type guard semantics are not used in this case because
> # "list[T]"" is not consistent with "list[T | None]"
> def has_no_nones(val: list[T | None]) -> TypeGuard[list[T]]:
>     return None not in val
> ```

When stricter type guard semantics are applied, the application of a
user-defined type guard function changes in two ways.

- Type narrowing is applied in the negative (\"else\") case.

``` python
def is_str(val: str | int) -> TypeGuard[str]:
    return isinstance(val, str)

def func(val: str | int):
    if not is_str(val):
        reveal_type(val)  # int
```

- Additional type narrowing is applied in the positive \"if\" case if
  applicable.

``` python
def is_cardinal_direction(val: str) -> TypeGuard[Literal["N", "S", "E", "W"]]:
    return val in ("N", "S", "E", "W")

def func(direction: Literal["NW", "E"]):
    if is_cardinal_direction(direction):
        reveal_type(direction)  # "Literal[E]"
    else:
        reveal_type(direction)  # "Literal[NW]"
```

The type-theoretic rules for type narrowing are specified in the
following table.

  \\             Non-strict type guard     Strict type guard
  -------------- ------------------------- ---------------------
  Applies when   R not consistent with I   R consistent with I
  NP is ..       $R$                       $A \land R$
  NN is ..       $A$                       $A \land \neg{R}$

In practice, the theoretic types for strict type guards cannot be
expressed precisely in the Python type system. Type checkers should fall
back on practical approximations of these types. As a rule of thumb, a
type checker should use the same type narrowing logic \-- and get
results that are consistent with \-- its handling of \"isinstance\".
This guidance allows for changes and improvements if the type system is
extended in the future.

# Additional Examples

`Any` is consistent[^2] with any other type, which means stricter
semantics can be applied.

``` python
# Stricter type guard semantics are used in this case because
# "str" is consistent with "Any"
def is_str(x: Any) -> TypeGuard[str]:
   return isinstance(x, str)

def test(x: float | str):
   if is_str(x):
       reveal_type(x)  # str
   else:
       reveal_type(x)  # float
```

# Backwards Compatibility

This PEP proposes to change the existing behavior of `TypeGuard`. This
has no effect at runtime, but it does change the types evaluated by a
type checker.

``` python
def is_int(val: int | str) -> TypeGuard[int]:
    return isinstance(val, int)

def func(val: int | str):
    if is_int(val):
        reveal_type(val)  # "int"
    else:
        reveal_type(val)  # Previously "int | str", now "str"
```

This behavioral change results in different types evaluated by a type
checker. It could therefore produce new (or mask existing) type errors.

Type checkers often improve narrowing logic or fix existing bugs in such
logic, so users of static typing will be used to this type of behavioral
change.

We also hypothesize that it is unlikely that existing typed Python code
relies on the current behavior of `TypeGuard`. To validate our
hypothesis, we implemented the proposed change in pyright and ran this
modified version on roughly 25 typed code bases using [mypy
primer](https://github.com/hauntsaninja/mypy_primer) to see if there
were any differences in the output. As predicted, the behavioral change
had minimal impact. The only noteworthy change was that some
`# type: ignore` comments were no longer necessary, indicating that
these code bases were already working around the existing limitations of
`TypeGuard`.

## Breaking change

It is possible for a user-defined type guard function to rely on the old
behavior. Such type guard functions could break with the new behavior.

``` python
def is_positive_int(val: int | str) -> TypeGuard[int]:
    return isinstance(val, int) and val > 0

def func(val: int | str):
    if is_positive_int(val):
        reveal_type(val)  # "int"
    else:
        # With the older behavior, the type of "val" is evaluated as
        # "int | str"; with the new behavior, the type is narrowed to
        # "str", which is perhaps not what was intended.
        reveal_type(val)
```

We think it is unlikely that such user-defined type guards exist in
real-world code. The mypy primer results didn\'t uncover any such cases.

# How to Teach This

Users unfamiliar with `TypeGuard` are likely to expect the behavior
outlined in this PEP, therefore making `TypeGuard` easier to teach and
explain.

# Reference Implementation

A reference
[implementation](https://github.com/microsoft/pyright/commit/9a5af798d726bd0612cebee7223676c39cf0b9b0)
of this idea exists in pyright.

To enable the modified behavior, the configuration flag
`enableExperimentalFeatures` must be set to true. This can be done on a
per-file basis by adding a comment:

``` python
# pyright: enableExperimentalFeatures=true
```

# Rejected Ideas

## StrictTypeGuard

A new `StrictTypeGuard` construct was proposed. This alternative form
would be similar to a `TypeGuard` except it would apply stricter type
guard semantics. It would also enforce that the return type was
consistent [^3] with the input type. See this thread for details:
[StrictTypeGuard
proposal](https://github.com/python/typing/discussions/1013#discussioncomment-1966238)

This idea was rejected because it is unnecessary in most cases and added
unnecessary complexity. It would require the introduction of a new
special form, and developers would need to be educated about the subtle
difference between the two forms.

## TypeGuard with a second output type

Another idea was proposed where `TypeGuard` could support a second
optional type argument that indicates the type that should be used for
narrowing in the negative (\"else\") case.

``` python
def is_int(val: int | str) -> TypeGuard[int, str]:
    return isinstance(val, int)
```

This idea was proposed
[here](https://github.com/python/typing/issues/996).

It was rejected because it was considered too complicated and addressed
only one of the two main limitations of `TypeGuard`. Refer to this
[thread](https://mail.python.org/archives/list/typing-sig@python.org/thread/EMUD2D424OI53DCWQ4H5L6SJD2IXBHUL)
for the full discussion.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: `PEP 483's discussion of is-consistent <483#summary-of-gradual-typing>`{.interpreted-text
    role="pep"}

[^2]: `PEP 483's discussion of is-consistent <483#summary-of-gradual-typing>`{.interpreted-text
    role="pep"}

[^3]: `PEP 483's discussion of is-consistent <483#summary-of-gradual-typing>`{.interpreted-text
    role="pep"}
