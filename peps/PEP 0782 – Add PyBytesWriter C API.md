---
pep: 782
title: Add PyBytesWriter C API
author:
- Victor Stinner <vstinner@python.org>
discussions_to: https://discuss.python.org/t/86617
status: Final
type: Standards Track
created: 27-Mar-2025
python_version: '3.15'
post_history:
- '`18-Feb-2025 <https://discuss.python.org/t/81182>`__'
resolution: '`11-Sep-2025 <https://discuss.python.org/t/86617/15>`__'
python_status: Final
url: https://peps.python.org/pep-0782/
source_path: https://github.com/python/peps/blob/main/peps/pep-0782.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:47+00:00'
---

::: canonical-doc
the `PyBytesWriter API <py3.15:pybyteswriter>`{.interpreted-text
role="ref"}
:::

# Abstract

Add a new `PyBytesWriter` C API to create `bytes` objects.

Soft deprecate `PyBytes_FromStringAndSize(NULL, size)` and
`_PyBytes_Resize()` APIs. These APIs treat an immutable `bytes` object
as a mutable object. They remain available and maintained, don\'t emit
deprecation warning, but are no longer recommended when writing new
code.

# Rationale

## Disallow creation of incomplete/inconsistent objects

Creating a Python `bytes`{.interpreted-text role="class"} object using
`PyBytes_FromStringAndSize(NULL, size)` and `_PyBytes_Resize()` treats
an immutable `bytes`{.interpreted-text role="class"} object as mutable.
It goes against the principle that `bytes`{.interpreted-text
role="class"} objects are immutable. It also creates an incomplete or
\"invalid\" object since bytes are not initialized. In Python, a
`bytes`{.interpreted-text role="class"} object should always have its
bytes fully initialized.

- [Avoid creating incomplete/invalid objects
  api-evolution#36](https://github.com/capi-workgroup/api-evolution/issues/36)
- [Disallow mutating immutable objects
  api-evolution#20](https://github.com/capi-workgroup/api-evolution/issues/20)
- [Disallow creation of incomplete/inconsistent objects
  problems#56](https://github.com/capi-workgroup/problems/issues/56)

## Inefficient allocation strategy

When creating a bytes string and the output size is unknown, one
strategy is to allocate a short buffer and extend it (to the exact size)
each time a larger write is needed.

This strategy is inefficient because it requires enlarging the buffer
multiple times. It\'s more efficient to overallocate the buffer the
first time that a larger write is needed. It reduces the number of
expensive `realloc()` operations which can imply a memory copy.

# Specification

## API

> A Python `bytes`{.interpreted-text role="class"} writer instance
> created by `PyBytesWriter_Create`{.interpreted-text role="c:func"}.
>
> The instance must be destroyed by
> `PyBytesWriter_Finish`{.interpreted-text role="c:func"} or
> `PyBytesWriter_Discard`{.interpreted-text role="c:func"}.

### Create, Finish, Discard

> Create a `PyBytesWriter`{.interpreted-text role="c:type"} to write
> *size* bytes.
>
> If *size* is greater than zero, allocate *size* bytes, and set the
> writer size to *size*. The caller is responsible to write *size* bytes
> using `PyBytesWriter_GetData`{.interpreted-text role="c:func"}.
>
> On error, set an exception and return NULL.
>
> *size* must be positive or zero.

> Finish a `PyBytesWriter`{.interpreted-text role="c:type"} created by
> `PyBytesWriter_Create`{.interpreted-text role="c:func"}.
>
> On success, return a Python `bytes`{.interpreted-text role="class"}
> object. On error, set an exception and return `NULL`.
>
> The writer instance is invalid after the call in any case.

> Similar to `PyBytesWriter_Finish`{.interpreted-text role="c:func"},
> but resize the writer to *size* bytes before creating the
> `bytes`{.interpreted-text role="class"} object.

> Similar to `PyBytesWriter_Finish`{.interpreted-text role="c:func"},
> but resize the writer using *buf* pointer before creating the
> `bytes`{.interpreted-text role="class"} object.
>
> Set an exception and return `NULL` if *buf* pointer is outside the
> internal buffer bounds.
>
> Function pseudo-code:
>
> ``` c
> Py_ssize_t size = (char*)buf - (char*)PyBytesWriter_GetData(writer);
> return PyBytesWriter_FinishWithSize(writer, size);
> ```

> Discard a `PyBytesWriter`{.interpreted-text role="c:type"} created by
> `PyBytesWriter_Create`{.interpreted-text role="c:func"}.
>
> Do nothing if *writer* is `NULL`.
>
> The writer instance is invalid after the call.

### High-level API

> Grow the *writer* internal buffer by *size* bytes, write *size* bytes
> of *bytes* at the *writer* end, and add *size* to the *writer* size.
>
> If *size* is equal to `-1`, call `strlen(bytes)` to get the string
> length.
>
> On success, return `0`. On error, set an exception and return `-1`.

> Similar to `PyBytes_FromFormat()`, but write the output directly at
> the writer end. Grow the writer internal buffer on demand. Then add
> the written size to the writer size.
>
> On success, return `0`. On error, set an exception and return `-1`.

### Getters

> Get the writer size.

> Get the writer data: start of the internal buffer.
>
> The pointer is valid until `PyBytesWriter_Finish`{.interpreted-text
> role="c:func"} or `PyBytesWriter_Discard`{.interpreted-text
> role="c:func"} is called on *writer*.

### Low-level API

> Resize the writer to *size* bytes. It can be used to enlarge or to
> shrink the writer.
>
> Newly allocated bytes are left uninitialized.
>
> On success, return `0`. On error, set an exception and return `-1`.
>
> *size* must be positive or zero.

> Resize the writer by adding *grow* bytes to the current writer size.
>
> Newly allocated bytes are left uninitialized.
>
> On success, return `0`. On error, set an exception and return `-1`.
>
> *size* can be negative to shrink the writer.

> Similar to `PyBytesWriter_Grow`{.interpreted-text role="c:func"}, but
> update also the *buf* pointer.
>
> The *buf* pointer is moved if the internal buffer is moved in memory.
> The *buf* relative position within the internal buffer is left
> unchanged.
>
> On error, set an exception and return `NULL`.
>
> *buf* must not be `NULL`.
>
> Function pseudo-code:
>
> ``` c
> Py_ssize_t pos = (char*)buf - (char*)PyBytesWriter_GetData(writer);
> if (PyBytesWriter_Grow(writer, size) < 0) {
>     return NULL;
> }
> return (char*)PyBytesWriter_GetData(writer) + pos;
> ```

## Overallocation

`PyBytesWriter_Resize`{.interpreted-text role="c:func"} and
`PyBytesWriter_Grow`{.interpreted-text role="c:func"} overallocate the
internal buffer to reduce the number of `realloc()` calls and so reduce
memory copies.

`PyBytesWriter_Finish`{.interpreted-text role="c:func"} trims
overallocations: it shrinks the internal buffer to the exact size when
creating the final `bytes`{.interpreted-text role="class"} object.

## Thread safety

The API is not thread safe: a writer should only be used by a single
thread at the same time.

## Soft deprecations

Soft deprecate `PyBytes_FromStringAndSize(NULL, size)` and
`_PyBytes_Resize()` APIs. These APIs treat an immutable `bytes` object
as a mutable object. They remain available and maintained, don\'t emit
deprecation warning, but are no longer recommended when writing new
code.

`PyBytes_FromStringAndSize(str, size)` is not soft deprecated. Only
calls with `NULL` *str* are soft deprecated.

# Examples

## High-level API

Create the bytes string `b"Hello World!"`:

``` c
PyObject* hello_world(void)
{
    PyBytesWriter *writer = PyBytesWriter_Create(0);
    if (writer == NULL) {
        goto error;
    }
    if (PyBytesWriter_WriteBytes(writer, "Hello", -1) < 0) {
        goto error;
    }
    if (PyBytesWriter_Format(writer, " %s!", "World") < 0) {
        goto error;
    }
    return PyBytesWriter_Finish(writer);

error:
    PyBytesWriter_Discard(writer);
    return NULL;
}
```

## Create the bytes string \"abc\"

Example creating the bytes string `b"abc"`, with a fixed size of 3
bytes:

``` c
PyObject* create_abc(void)
{
    PyBytesWriter *writer = PyBytesWriter_Create(3);
    if (writer == NULL) {
        return NULL;
    }

    char *str = PyBytesWriter_GetData(writer);
    memcpy(str, "abc", 3);
    return PyBytesWriter_Finish(writer);
}
```

## `GrowAndUpdatePointer()` example

Example using a pointer to write bytes and to track the written size.

Create the bytes string `b"Hello World"`:

``` c
PyObject* grow_example(void)
{
    // Allocate 10 bytes
    PyBytesWriter *writer = PyBytesWriter_Create(10);
    if (writer == NULL) {
        return NULL;
    }

    // Write some bytes
    char *buf = PyBytesWriter_GetData(writer);
    memcpy(buf, "Hello ", strlen("Hello "));
    buf += strlen("Hello ");

    // Allocate 10 more bytes
    buf = PyBytesWriter_GrowAndUpdatePointer(writer, 10, buf);
    if (buf == NULL) {
        PyBytesWriter_Discard(writer);
        return NULL;
    }

    // Write more bytes
    memcpy(buf, "World", strlen("World"));
    buf += strlen("World");

    // Truncate the string at 'buf' position
    // and create a bytes object
    return PyBytesWriter_FinishWithPointer(writer, buf);
}
```

## Update `PyBytes_FromStringAndSize()` code

Example of code using the soft deprecated
`PyBytes_FromStringAndSize(NULL, size)` API:

``` c
PyObject *result = PyBytes_FromStringAndSize(NULL, num_bytes);
if (result == NULL) {
    return NULL;
}
if (copy_bytes(PyBytes_AS_STRING(result), start, num_bytes) < 0) {
    Py_CLEAR(result);
}
return result;
```

It can now be updated to:

``` c
PyBytesWriter *writer = PyBytesWriter_Create(num_bytes);
if (writer == NULL) {
    return NULL;
}
if (copy_bytes(PyBytesWriter_GetData(writer), start, num_bytes) < 0) {
    PyBytesWriter_Discard(writer);
    return NULL;
}
return PyBytesWriter_Finish(writer);
```

## Update `_PyBytes_Resize()` code

Example of code using the soft deprecated `_PyBytes_Resize()` API:

``` c
PyObject *v = PyBytes_FromStringAndSize(NULL, size);
if (v == NULL) {
    return NULL;
}
char *p = PyBytes_AS_STRING(v);

// ... fill bytes into 'p' ...

if (_PyBytes_Resize(&v, (p - PyBytes_AS_STRING(v)))) {
    return NULL;
}
return v;
```

It can now be updated to:

``` c
PyBytesWriter *writer = PyBytesWriter_Create(size);
if (writer == NULL) {
    return NULL;
}
char *p = PyBytesWriter_GetData(writer);

// ... fill bytes into 'p' ...

return PyBytesWriter_FinishWithPointer(writer, p);
```

# Reference Implementation

[Pull request gh-131681](https://github.com/python/cpython/pull/131681).

Notes on the CPython reference implementation which are not part of the
Specification:

- The implementation allocates internally a `bytes`{.interpreted-text
  role="class"} object, so `PyBytesWriter_Finish`{.interpreted-text
  role="c:func"} just returns the object without having to copy memory.
- For strings up to 256 bytes, a small internal raw buffer of bytes is
  used. It avoids having to resize a `bytes`{.interpreted-text
  role="class"} object which is inefficient. At the end,
  `PyBytesWriter_Finish`{.interpreted-text role="c:func"} creates the
  `bytes`{.interpreted-text role="class"} object from this small buffer.
- A free list is used to reduce the cost of allocating a
  `PyBytesWriter`{.interpreted-text role="c:type"} on the heap memory.

# Backwards Compatibility

There is no impact on the backward compatibility, only new APIs are
added.

`PyBytes_FromStringAndSize(NULL, size)` and `_PyBytes_Resize()` APIs are
soft deprecated. No new warnings is emitted when these functions are
used and they are not planned for removal.

# Prior Discussions

- March 2025: Third public API attempt, using size rather than pointers:
  - [Discussion](https://discuss.python.org/t/81182/56)
  - [Pull request
    gh-131681](https://github.com/python/cpython/pull/131681)
- February 2025: Second public API attempt:
  - [Issue gh-129813](https://github.com/python/cpython/issues/129813)
    and [pull request
    gh-129814](https://github.com/python/cpython/pull/129814)
- July 2024: First public API attempt:
  - C API Working Group decision: [Add PyBytes_Writer()
    API](https://github.com/capi-workgroup/decisions/issues/39) (August
    2024)
  - [Pull request
    gh-121726](https://github.com/python/cpython/pull/121726): first
    public API attempt (July 2024)
- March 2016: [Fast \_PyAccu, \_PyUnicodeWriter and \_PyBytesWriter APIs
  to produce strings in
  CPython](https://vstinner.github.io/pybyteswriter.html): Article on
  the original private `_PyBytesWriter` C API.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
