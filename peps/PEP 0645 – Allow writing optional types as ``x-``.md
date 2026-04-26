---
pep: 645
title: Allow writing optional types as ``x?``
author:
- Maggie Moss <maggiebmoss@gmail.com>
sponsor: Guido van Rossum <guido@python.org>
status: Withdrawn
type: Standards Track
created: 25-Aug-2020
resolution: https://mail.python.org/archives/list/typing-sig@python.org/message/E75SPV6DDHLEEFSA5MBN5HUOQWDMUQJ2/
python_status: Withdrawn
url: https://peps.python.org/pep-0645/
source_path: https://github.com/python/peps/blob/main/peps/pep-0645.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:27+00:00'
---

# Abstract

This PEP proposes adding a `?` operator for types to allow writing
`int?` in place of `Optional[int]`.

# PEP Withdrawal

The notation `T|None` introduced by `604`{.interpreted-text role="pep"}
to write `Optional[T]` is a fine alternative to `T?` and does not
require new syntax.

Using `T?` to mean `T|None` is also inconsistent with TypeScript where
it roughly means `NotRequired[T]`. Such inconsistency would likely
confuse folks coming from TypeScript to Python.

The above represents the consensus of
[typing-sig](https://mail.python.org/archives/list/typing-sig@python.org/)
and the sponsor of this PEP.

# Motivation

Types have become a valuable and powerful part of the Python language.
However, many type annotations are verbose and add considerable friction
to using type annotations. By improving the typing syntax, adding types
to Python code becomes simpler and improves the development experience
for Python users.

In a similar vein, a PEP to introduce short hand syntax for
`Union types <604>`{.interpreted-text role="pep"} has been approved and
implemented.

# Rationale

Types in Python can be quite verbose, this can be a hindrance when
working towards type adoption. Making types more ergonomic, as was done
with the Union type in `604`{.interpreted-text role="pep"} (e.g., int \|
str), would reduce the effort needed to add types to new and existing
Python code. The Optional annotation is used frequently in both
partially and fully typed Python code bases. In a small sampling of [5
well-typed open source projects, on average 7% of
annotations](https://gist.github.com/MaggieMoss/fd8dfe002b2702fae243dbf81a62624e)
included at least one optional type. This indicates that updating the
syntax has the potential to make types more concise, reduce code length
and improve readability.

Simplifying the syntax for optionals has been [discussed
previously](https://github.com/python/typing/issues/429) within the
typing community. The consensus during these conversations has been that
`?` is the preferred operator. There is no native support for unary `?`
in Python and this will need to be added to the runtime.

Adding the ? sigil to the Python grammar has been proposed previously in
`505`{.interpreted-text role="pep"}, which is currently in a deferred
state. `505`{.interpreted-text role="pep"} proposes a:

> - \"None coalescing\" binary operator `??`
> - \"None-aware attribute access\" operator `?.` (\"maybe dot\")
> - \"None-aware indexing\" operator `?[]` (\"maybe subscript\")

Should `505`{.interpreted-text role="pep"} be approved in the future, it
would not interfere with the typing specific `?` proposed in this PEP.
As well, since all uses of the `?` would be conceptually related, it
would not be confusing in terms of learning Python or a hindrance to
quick visual comprehension.

The proposed syntax, with the postfix operator, mimics the optional
syntax found in other typed languages, like C#, TypeScript and Swift.
The widespread adoption and popularity of these languages means that
Python developers are likely already familiar with this syntax.

``` text
// Optional in Swift
var example: String?

// Optional in C#
string? example;
```

Adding this syntax would also follow the often used pattern of using
builtin types as annotations. For example, `list`, `dict` and `None`.
This would allow more annotations to be added to Python code without
importing from `typing`.

# Specification

The new optional syntax should be accepted for function, variable,
attribute and parameter annotations.

``` text
# instead of
# def foo(x: Optional[int], y: Optional[str], z: Optional[list[int]): ...
def foo(x: int?, y: str?, x: list[int]?): ...

# def bar(x: list[typing.Optional[int]]): ...
def bar(x: list[int?]): ...
```

The new optional syntax should be equivalent to the existing
typing.Optional syntax

``` text
typing.Optional[int] == int?
```

The new optional syntax should have the same identity as the existing
typing.Optional syntax.

``` text
typing.Optional[int] is int?
```

It should also be equivalent to a Union with None.

``` text
# old syntax
int? == typing.Union[int, None]

# new syntax
int? == int | None
```

Since the new Union syntax specified in `604`{.interpreted-text
role="pep"} is supported in `isinstance` and `issubclass`, the new
optional syntax should be supported in both `isinstance` and
`issubclass`,

``` text
isinstance(1, int?) # true
issubclass(Child, Super?) # true
```

A new dunder method will need to be implemented to allow the `?`
operator to be overloaded for other functionality.

# Backwards Compatibility

`?` is currently unused in Python syntax, therefore this PEP is fully
backwards compatible.

# Reference Implementation

A reference implementation can be found
[here](https://github.com/python/cpython/compare/main...MaggieMoss:new-optional-syntax-postfix).

# Rejected Ideas

Discussed alternatives were

- The `~` operator was considered in place of `?`.
- A prefix operator (`?int`).

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
