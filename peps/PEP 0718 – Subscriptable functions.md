---
pep: 718
title: Subscriptable functions
author:
- James Hilton-Balfe <gobot1234yt@gmail.com>
sponsor: Guido van Rossum <guido@python.org>
discussions_to: https://discuss.python.org/t/28457/
status: Draft
type: Standards Track
topic: Typing
created: 23-Jun-2023
python_version: '3.15'
post_history:
- '`24-Jun-2023 <https://discuss.python.org/t/28457/>`__'
python_status: Draft
url: https://peps.python.org/pep-0718/
source_path: https://github.com/python/peps/blob/main/peps/pep-0718.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:45+00:00'
---

# Abstract

This PEP proposes making function objects subscriptable for typing
purposes. Doing so gives developers explicit control over the types
produced by the type checker where bi-directional inference (which
allows for the types of parameters of anonymous functions to be
inferred) and other methods than specialisation are insufficient. It
also brings functions in line with regular classes in their ability to
be subscriptable.

# Motivation

## Unknown Types

Currently, it is not possible to infer the type parameters to generic
functions in certain situations:

``` python
def make_list[T](*args: T) -> list[T]: ...
reveal_type(make_list())  # type checker cannot infer a meaningful type for T
```

Making instances of `FunctionType` subscriptable would allow for this
constructor to be typed:

``` python
reveal_type(make_list[int]())  # type is list[int]
```

Currently you have to use an assignment to provide a precise type:

``` python
x: list[int] = make_list()
reveal_type(x)  # type is list[int]
```

but this code is unnecessarily verbose taking up multiple lines for a
simple function call.

Similarly, `T` in this example cannot currently be meaningfully
inferred, so `x` is untyped without an extra assignment:

``` python
def factory[T](func: Callable[[T], Any]) -> Foo[T]: ...

reveal_type(factory(lambda x: "Hello World" * x))
```

If function objects were subscriptable, however, a more specific type
could be given:

``` python
reveal_type(factory[int](lambda x: "Hello World" * x))  # type is Foo[int]
```

## Undecidable Inference

There are even cases where subclass relations make type inference
impossible. However, if you can specialise the function type checkers
can infer a meaningful type.

``` python
def foo[T](x: Sequence[T] | T) -> list[T]: ...

reveal_type(foo[bytes](b"hello"))
```

Currently, type checkers do not consistently synthesise a type here.

## Unsolvable Type Parameters

Currently, with unspecialised literals, it is not possible to determine
a type for situations similar to:

``` python
def foo[T](x: list[T]) -> T: ...
reveal_type(foo([]))  # type checker cannot infer T (yet again)
```

``` python
reveal_type(foo[int]([]))  # type is int
```

It is also useful to be able to specify in cases in which a certain type
must be passed to a function beforehand:

``` python
words = ["hello", "world"]
foo[int](words)  # Invalid: list[str] is incompatible with list[int]
```

Allowing subscription makes functions and methods consistent with
generic classes where they weren\'t already. Whilst all of the proposed
changes can be implemented using callable generic classes, syntactic
sugar would be highly welcome.

Due to this, specialising the function and using it as a new factory is
fine

``` python
make_int_list = make_list[int]
reveal_type(make_int_list())  # type is list[int]
```

## Monomorphisation and Reification

This proposal also opens the door to
[monomorphisation](https://en.wikipedia.org/wiki/Monomorphization) and
[reified
types](https://en.wikipedia.org/wiki/Reification_(computer_science)).

This would allow for a functionality which anecdotally has been
requested many times.

*Please note this feature is not being proposed by the PEP, but may be
implemented in the future.*

The syntax for such a feature may look something like:

``` python
def foo[T]():
   return T.__value__

assert foo[int]() is int
```

# Rationale

Function objects in this PEP is used to refer to `FunctionType`,
`MethodType`, `BuiltinFunctionType`, `BuiltinMethodType` and
`MethodWrapperType`.

For `MethodType` you should be able to write:

``` python
class Foo:
    def make_list[T](self, *args: T) -> list[T]: ...

Foo().make_list[int]()
```

and have it work similarly to a `FunctionType`.

For `BuiltinFunctionType`, so builtin generic functions (e.g. `max` and
`min`) work like ones defined in Python. Built-in functions should
behave as much like functions implemented in Python as possible.

`BuiltinMethodType` is the same type as `BuiltinFunctionType`.

`MethodWrapperType` (e.g. the type of `object().__str__`) is useful for
generic magic methods.

# Specification

Function objects should implement `__getitem__` to allow for
subscription at runtime and return an instance of `types.GenericAlias`
with `__origin__` set as the callable and `__args__` as the types
passed.

Type checkers should support subscripting functions and understand that
the parameters passed to the function subscription should follow the
same rules as a generic callable class.

## Setting `__orig_class__`

Currently, `__orig_class__` is an attribute set in
`GenericAlias.__call__` to the instance of the `GenericAlias` that
created the called class e.g.

``` python
class Foo[T]: ...

assert Foo[int]().__orig_class__ == Foo[int]
```

Currently, `__orig_class__` is unconditionally set; however, to avoid
potential erasure on any created instances, this attribute should not be
set if `__origin__` is an instance of any function object.

The following code snippet would fail at runtime without this change as
`__orig_class__` would be `bar[str]` and not `Foo[int]`.

``` python
def bar[U]():
    return Foo[int]()

assert bar[str]().__orig_class__  == Foo[int]
```

## Interactions with `@typing.overload`

Overloaded functions should work much the same as already, since they
have no effect on the runtime type. The only change is that more
situations will be decidable and the behaviour/overload can be specified
by the developer rather than leaving it to ordering of overloads/unions.

# Backwards Compatibility

Currently these classes are not subclassable and so there are no
backwards compatibility concerns with regards to classes already
implementing `__getitem__`.

# Reference Implementation

The runtime changes proposed can be found here
<https://github.com/Gobot1234/cpython/tree/function-subscript>

# Acknowledgements

Thank you to Alex Waygood and Jelle Zijlstra for their feedback on this
PEP and Guido for some motivating examples.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
