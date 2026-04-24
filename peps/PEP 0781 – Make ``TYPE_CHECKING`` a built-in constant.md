---
pep: 781
title: Make ``TYPE_CHECKING`` a built-in constant
author:
- Inada Naoki <songofacandy@gmail.com>
discussions_to: https://discuss.python.org/t/85728
status: Draft
type: Standards Track
topic: Typing
created: 24-Mar-2025
python_version: '3.15'
post_history:
- '`11-Jan-2025 <https://discuss.python.org/t/76766>`__'
- '`24-Mar-2025 <https://discuss.python.org/t/85728>`__'
python_status: Draft
url: https://peps.python.org/pep-0781/
source_path: https://github.com/python/peps/blob/main/peps/pep-0781.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:08+00:00'
---

# Abstract

This PEP proposes adding a new built-in variable,
`!TYPE_CHECKING`{.interpreted-text role="data"}, to improve the
experience of writing Python code with type annotations. It is evaluated
as `True` when the code is being analyzed by a static type checker, and
as `False` during normal runtime execution. Unlike
`typing.TYPE_CHECKING`{.interpreted-text role="data"}, which this
variable replaces, it does not require an import statement.

# Motivation

Type annotations were defined for Python by `484`{.interpreted-text
role="pep"}, and have enjoyed widespread adoption. A challenge with
fully-annotated code is that many more imports are required in order to
bring the relevant name into scope, potentially causing import cycles
without careful design. This has been recognized by
`563`{.interpreted-text role="pep"} and later `649`{.interpreted-text
role="pep"}, which introduce two different mechanisms for deferred
evaluation of type annotations. As PEP 563 notes, \"type hints are \...
not computationally free\". The `typing.TYPE_CHECKING`{.interpreted-text
role="data"} constant was thus
[introduced](https://github.com/python/typing/issues/230), initially to
aid in breaking cyclic imports.

In situations where startup time is critical, such as command-line
interfaces, applications, or core libraries, programmers may place all
import statements not required for runtime execution within a
\'TYPE_CHECKING block\', or even defer certain imports to within
functions. The `typing` module itself though can take as much as 10ms to
import, longer than Python takes to initialize. The time taken to import
the `typing` module clearly cannot be ignored.

To avoid importing `TYPE_CHECKING` from `typing`, developers currently
define a module-level variable such as `TYPE_CHECKING = False` or use
code like `if False:  # TYPE_CHECKING`. Providing a standard method will
allow many tools to implement the same behavior consistently. It will
also allow third-party tools in the ecosystem to standardize on a single
behavior with guaranteed semantics, as for example some static type
checkers currently do not permit local constants, only recognizing
`typing.TYPE_CHECKING`.

# Specification

`TYPE_CHECKING` is a built-in constant and its value is `False`. Unlike
`True`, `False`, `None`, and `__debug__`, `TYPE_CHECKING` is not a real
constant; assigning to it will not raise a `SyntaxError`.

Static type checkers must treat `TYPE_CHECKING` as `True`, similar to
`typing.TYPE_CHECKING`{.interpreted-text role="data"}.

If this PEP is accepted, the new `TYPE_CHECKING` constant will be the
preferred approach and importing `typing.TYPE_CHECKING` will be
deprecated. To minimize the runtime impact of typing, this deprecation
will generate `DeprecationWarning` no sooner than Python 3.13\'s end of
life, scheduled for October 2029.

Instead, type checkers may warn about such deprecated usage when the
target version of the checked program is signalled to be Python 3.14 or
newer.

# Backwards Compatibility

Since `TYPE_CHECKING` doesn\'t prohibit assignment, existing code using
`TYPE_CHECKING` will continue to work.

``` python
# This code will continue to work
TYPE_CHECKING = False
from typing import TYPE_CHECKING
```

User can remove the assignment to `TYPE_CHECKING` after they stop using
Python 3.13 or older versions.

# How to Teach This

- Use `if TYPE_CHECKING:` for skipping type-checking code at runtime.
- Use `from typing import TYPE_CHECKING` to support Python versions
  before 3.14.
- Workarounds like `TYPE_CHECKING = False` or
  `if False:  # TYPE_CHECKING` will continue to work, but are not
  recommended.

# Reference Implementation

- [python/cpython#131793](https://github.com/python/cpython/pull/131793)

# Rejected Ideas

## Eliminate type-checking-only code

It is considered to add real constant named `__type_checking__` to
eliminate type-checking-only code at compile time.

However, adding real constant to language increase complexity of the
language. Benefit from eliminating type-checking-only code is estimated
to be not enough to justify the complexity.

## Optimize `import typing`

Future optimizations may eliminate the need to avoid importing the
`typing` module for startup time.

Even with such optimizations, there will still be use cases where
minimizing imports is beneficial, such as running Python on embedded
systems or in browsers.

Therefore, defining a constant for skipping type-checking-only code
outside the `typing` module remains valuable.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
