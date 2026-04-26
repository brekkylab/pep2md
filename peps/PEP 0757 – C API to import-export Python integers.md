---
pep: 757
title: C API to import-export Python integers
author:
- Sergey B Kirpichev <skirpichev@gmail.com>
- Victor Stinner <vstinner@python.org>
discussions_to: https://discuss.python.org/t/63895
status: Final
type: Standards Track
created: 13-Sep-2024
python_version: '3.14'
post_history:
- '`14-Sep-2024 <https://discuss.python.org/t/63895>`__'
resolution: '`08-Dec-2024 <https://discuss.python.org/t/63895/79>`__'
python_status: Final
url: https://peps.python.org/pep-0757/
source_path: https://github.com/python/peps/blob/main/peps/pep-0757.rst
source_commit: 8d6686b74fa57d5cb7caf051b025416e3f359f16
---

::: canonical-doc
the [Export API](https://docs.python.org/dev/c-api/long.html#export-api)
and the [PyLongWriter
API](https://docs.python.org/dev/c-api/long.html#pylongwriter-api)
:::

# Abstract

Add a new C API to import and export Python integers,
`int`{.interpreted-text role="class"} objects: especially
`PyLongWriter_Create()`{.interpreted-text role="c:func"} and
`PyLong_Export()`{.interpreted-text role="c:func"} functions.

# Rationale

Projects such as [gmpy2](https://github.com/aleaxit/gmpy),
[SAGE](https://www.sagemath.org/) and
[Python-FLINT](https://github.com/flintlib/python-flint) access directly
Python \"internals\" (the `PyLongObject`{.interpreted-text
role="c:type"} structure) or use an inefficient temporary format (hex
strings for Python-FLINT) to import and export Python
`int`{.interpreted-text role="class"} objects. The Python
`int`{.interpreted-text role="class"} implementation changed in Python
3.12 to add a tag and \"compact values\".

In the 3.13 alpha 1 release, the private undocumented
`!_PyLong_New()`{.interpreted-text role="c:func"} function had been
removed, but it is being used by these projects to import Python
integers. The private function has been restored in 3.13 alpha 2.

A public efficient abstraction is needed to interface Python with these
projects without exposing implementation details. It would allow Python
to change its internals without breaking these projects. For example,
implementation for gmpy2 was changed recently for CPython 3.9 and for
CPython 3.12.

# Specification

## Layout API

Data needed by [GMP](https://gmplib.org/)-like
[import](https://gmplib.org/manual/Integer-Import-and-Export#index-mpz_005fimport)-[export](https://gmplib.org/manual/Integer-Import-and-Export#index-mpz_005fexport)
functions.

> Layout of an array of \"digits\" (\"limbs\" in the GMP terminology),
> used to represent absolute value for arbitrary precision integers.
>
> Use `PyLong_GetNativeLayout`{.interpreted-text role="c:func"} to get
> the native layout of Python `int`{.interpreted-text role="class"}
> objects, used internally for integers with \"big enough\" absolute
> value.
>
> See also `sys.int_info`{.interpreted-text role="data"} which exposes
> similar information to Python.
>
> > Bits per digit. For example, a 15 bit digit means that bits 0-14
> > contain meaningful information.
>
> > Digit size in bytes. For example, a 15 bit digit will require at
> > least 2 bytes.
>
> > Digits order:
> >
> > - `1` for most significant digit first
> > - `-1` for least significant digit first
>
> > Digit endianness:
> >
> > - `1` for most significant byte first (big endian)
> > - `-1` for least significant byte first (little endian)

> Get the native layout of Python `int`{.interpreted-text role="class"}
> objects.
>
> See the `PyLongLayout`{.interpreted-text role="c:struct"} structure.
>
> The function must not be called before Python initialization nor after
> Python finalization. The returned layout is valid until Python is
> finalized. The layout is the same for all Python sub-interpreters and
> so it can be cached.

## Export API

> Export of a Python `int`{.interpreted-text role="class"} object.
>
> There are two cases:
>
> - If `digits`{.interpreted-text role="c:member"} is `NULL`, only use
>   the `value`{.interpreted-text role="c:member"} member.
> - If `digits`{.interpreted-text role="c:member"} is not `NULL`, use
>   `negative`{.interpreted-text role="c:member"},
>   `ndigits`{.interpreted-text role="c:member"} and
>   `digits`{.interpreted-text role="c:member"} members.
>
> > The native integer value of the exported `int`{.interpreted-text
> > role="class"} object. Only valid if `digits`{.interpreted-text
> > role="c:member"} is `NULL`.
>
> > 1 if the number is negative, 0 otherwise. Only valid if
> > `digits`{.interpreted-text role="c:member"} is not `NULL`.
>
> > Number of digits in `digits`{.interpreted-text role="c:member"}
> > array. Only valid if `digits`{.interpreted-text role="c:member"} is
> > not `NULL`.
>
> > Read-only array of unsigned digits. Can be `NULL`.

If `PyLongExport.digits`{.interpreted-text role="c:member"} is not
`NULL`, a private field of the `PyLongExport`{.interpreted-text
role="c:struct"} structure stores a strong reference to the Python
`int`{.interpreted-text role="class"} object to make sure that that
structure remains valid until `PyLong_FreeExport()`{.interpreted-text
role="c:func"} is called.

> Export a Python `int`{.interpreted-text role="class"} object.
>
> *export_long* must point to a `PyLongExport`{.interpreted-text
> role="c:struct"} structure allocated by the caller. It must not be
> `NULL`.
>
> On success, fill in *\*export_long* and return 0. On error, set an
> exception and return -1.
>
> `PyLong_FreeExport`{.interpreted-text role="c:func"} must be called
> when the export is no longer needed.
>
> **CPython implementation detail**: This function always succeeds if
> *obj* is a Python `int`{.interpreted-text role="class"} object or a
> subclass.

On CPython 3.14, no memory copy is needed in
`PyLong_Export`{.interpreted-text role="c:func"}, it\'s just a thin
wrapper to expose Python `int`{.interpreted-text role="class"} internal
digits array.

> Release the export *export_long* created by
> `PyLong_Export`{.interpreted-text role="c:func"}.
>
> **CPython implementation detail**: Calling
> `PyLong_FreeExport`{.interpreted-text role="c:func"} is optional if
> *export_long-\>digits* is `NULL`.

## Import API

The `PyLongWriter`{.interpreted-text role="c:type"} API can be used to
import an integer.

> A Python `int`{.interpreted-text role="class"} writer instance.
>
> The instance must be destroyed by
> `PyLongWriter_Finish`{.interpreted-text role="c:func"} or
> `PyLongWriter_Discard`{.interpreted-text role="c:func"}.

> Create a `PyLongWriter`{.interpreted-text role="c:type"}.
>
> On success, allocate *\*digits* and return a writer. On error, set an
> exception and return `NULL`.
>
> *negative* is `1` if the number is negative, or `0` otherwise.
>
> *ndigits* is the number of digits in the *digits* array. It must be
> greater than 0.
>
> *digits* must not be NULL.
>
> After a successful call to this function, the caller should fill in
> the array of digits *digits* and then call
> `PyLongWriter_Finish`{.interpreted-text role="c:func"} to get a Python
> `int`{.interpreted-text role="class"}. The layout of *digits* is
> described by `PyLong_GetNativeLayout`{.interpreted-text
> role="c:func"}.
>
> Digits must be in the range \[`0`; `(1 << bits_per_digit) - 1`\]
> (where the `~PyLongLayout.bits_per_digit`{.interpreted-text
> role="c:struct"} is the number of bits per digit). Any unused most
> significant digits must be set to `0`.
>
> Alternately, call `PyLongWriter_Discard`{.interpreted-text
> role="c:func"} to destroy the writer instance without creating an
> `~int`{.interpreted-text role="class"} object.

On CPython 3.14, the `PyLongWriter_Create`{.interpreted-text
role="c:func"} implementation is a thin wrapper to the private
`!_PyLong_New()`{.interpreted-text role="c:func"} function.

> Finish a `PyLongWriter`{.interpreted-text role="c:type"} created by
> `PyLongWriter_Create`{.interpreted-text role="c:func"}.
>
> On success, return a Python `int`{.interpreted-text role="class"}
> object. On error, set an exception and return `NULL`.
>
> The function takes care of normalizing the digits and converts the
> object to a compact integer if needed.
>
> The writer instance and the *digits* array are invalid after the call.

> Discard a `PyLongWriter`{.interpreted-text role="c:type"} created by
> `PyLongWriter_Create`{.interpreted-text role="c:func"}.
>
> *writer* must not be `NULL`.
>
> The writer instance and the *digits* array are invalid after the call.

# Optimize import for small integers

Proposed import API is efficient for large integers. Compared to
accessing directly Python internals, the proposed import API can have a
significant performance overhead on small integers.

For small integers of a few digits (for example, 1 or 2 digits),
existing APIs can be used:

- `PyLong_FromUInt64()`{.interpreted-text
  role="external+py3.14:c:func"};
- `PyLong_FromLong()`{.interpreted-text role="c:func"};
- `PyLong_FromNativeBytes()`{.interpreted-text role="c:func"}.

# Implementation

- CPython:
  - <https://github.com/python/cpython/pull/121339>
  - <https://github.com/vstinner/cpython/pull/5>
- gmpy:
  - <https://github.com/aleaxit/gmpy/pull/495>

# Benchmarks

Code:

``` c
/* Query parameters of Python’s internal representation of integers. */
const PyLongLayout *layout = PyLong_GetNativeLayout();

size_t int_digit_size = layout->digit_size;
int int_digits_order = layout->digits_order;
size_t int_bits_per_digit = layout->bits_per_digit;
size_t int_nails = int_digit_size*8 - int_bits_per_digit;
int int_endianness = layout->digit_endianness;
```

## Export: `PyLong_Export()`{.interpreted-text role="c:func"} with gmpy2

Code:

``` c
static int
mpz_set_PyLong(mpz_t z, PyObject *obj)
{
    static PyLongExport long_export;

    if (PyLong_Export(obj, &long_export) < 0) {
        return -1;
    }

    if (long_export.digits) {
        mpz_import(z, long_export.ndigits, int_digits_order, int_digit_size,
                   int_endianness, int_nails, long_export.digits);
        if (long_export.negative) {
            mpz_neg(z, z);
        }
        PyLong_FreeExport(&long_export);
    }
    else {
        const int64_t value = long_export.value;

        if (LONG_MIN <= value && value <= LONG_MAX) {
            mpz_set_si(z, value);
        }
        else {
            mpz_import(z, 1, -1, sizeof(int64_t), 0, 0, &value);
            if (value < 0) {
                mpz_t tmp;
                mpz_init(tmp);
                mpz_ui_pow_ui(tmp, 2, 64);
                mpz_sub(z, z, tmp);
                mpz_clear(tmp);
            }
        }
    }
    return 0;
}
```

Reference code: [mpz_set_PyLong() in the gmpy2 master for commit
9177648](https://github.com/aleaxit/gmpy/blob/9177648c23f5c507e46b81c1eb7d527c79c96f00/src/gmpy2_convert_gmp.c#L42-L69).

Benchmark:

``` py
import pyperf
from gmpy2 import mpz

runner = pyperf.Runner()
runner.bench_func('1<<7', mpz, 1 << 7)
runner.bench_func('1<<38', mpz, 1 << 38)
runner.bench_func('1<<300', mpz, 1 << 300)
runner.bench_func('1<<3000', mpz, 1 << 3000)
```

Results on Linux Fedora 40 with CPU isolation, Python built in release
mode:

  --------------------------------------------------
  Benchmark        ref       pep757
  ---------------- --------- -----------------------
  1\<\<7           91.3 ns   89.9 ns: 1.02x faster

  1\<\<38          120 ns    94.9 ns: 1.27x faster

  1\<\<300         196 ns    203 ns: 1.04x slower

  1\<\<3000        939 ns    945 ns: 1.01x slower

  Geometric mean   (ref)     1.05x faster
  --------------------------------------------------

## Import: `PyLongWriter_Create()`{.interpreted-text role="c:func"} with gmpy2

Code:

``` c
static PyObject *
GMPy_PyLong_From_MPZ(MPZ_Object *obj, CTXT_Object *context)
{
    if (mpz_fits_slong_p(obj->z)) {
        return PyLong_FromLong(mpz_get_si(obj->z));
    }

    size_t size = (mpz_sizeinbase(obj->z, 2) +
                   int_bits_per_digit - 1) / int_bits_per_digit;
    void *digits;
    PyLongWriter *writer = PyLongWriter_Create(mpz_sgn(obj->z) < 0, size,
                                               &digits);
    if (writer == NULL) {
        return NULL;
    }

    mpz_export(digits, NULL, int_digits_order, int_digit_size,
               int_endianness, int_nails, obj->z);

    return PyLongWriter_Finish(writer);
}
```

Reference code: [GMPy_PyLong_From_MPZ() in the gmpy2 master for commit
9177648](https://github.com/aleaxit/gmpy/blob/9177648c23f5c507e46b81c1eb7d527c79c96f00/src/gmpy2_convert_gmp.c#L128-L156).

Benchmark:

``` py
import pyperf
from gmpy2 import mpz

runner = pyperf.Runner()
runner.bench_func('1<<7', int, mpz(1 << 7))
runner.bench_func('1<<38', int, mpz(1 << 38))
runner.bench_func('1<<300', int, mpz(1 << 300))
runner.bench_func('1<<3000', int, mpz(1 << 3000))
```

Results on Linux Fedora 40 with CPU isolation, Python built in release
mode:

  --------------------------------------------------
  Benchmark        ref       pep757
  ---------------- --------- -----------------------
  1\<\<7           56.7 ns   56.2 ns: 1.01x faster

  1\<\<300         191 ns    213 ns: 1.12x slower

  Geometric mean   (ref)     1.03x slower
  --------------------------------------------------

Benchmark hidden because not significant (2): 1\<\<38, 1\<\<3000.

# Backwards Compatibility

There is no impact on the backward compatibility, only new APIs are
added.

# Rejected Ideas

## Support arbitrary layout

It would be convenient to support arbitrary layout to import-export
Python integers.

For example, it was proposed to add a *layout* parameter to
`PyLongWriter_Create()`{.interpreted-text role="c:func"} and a *layout*
member to the `PyLongExport`{.interpreted-text role="c:struct"}
structure.

The problem is that it\'s more complex to implement and not really
needed. What\'s strictly needed is only an API to import-export using
the Python \"native\" layout.

If later there are use cases for arbitrary layouts, new APIs can be
added.

## Don\'t add `PyLong_GetNativeLayout`{.interpreted-text role="c:func"} function

Currently, most required information for `int`{.interpreted-text
role="class"} import/export is already available via
`PyLong_GetInfo()`{.interpreted-text role="c:func"} (and
`sys.int_info`{.interpreted-text role="data"}). We also can add more
(like order of digits), this interface doesn\'t poses any constraints on
future evolution of the `PyLongObject`{.interpreted-text role="c:type"}.

The problem is that the `PyLong_GetInfo()`{.interpreted-text
role="c:func"} returns a Python object, `named tuple`{.interpreted-text
role="term"}, not a convenient C structure and that might distract
people from using it in favor e.g. of current semi-private macros like
`!PyLong_SHIFT`{.interpreted-text role="c:macro"} and
`!PyLong_BASE`{.interpreted-text role="c:macro"}.

## Provide mpz_import/export-like API instead

The other approach to import/export data from `int`{.interpreted-text
role="class"} objects might be following: expect, that C extensions
provide contiguous buffers that CPython then exports (or imports) the
*absolute* value of an integer.

API example:

``` c
struct PyLongLayout {
    uint8_t bits_per_digit;
    uint8_t digit_size;
    int8_t digits_order;
};

size_t PyLong_GetDigitsNeeded(PyLongObject *obj, PyLongLayout layout);
int PyLong_Export(PyLongObject *obj, PyLongLayout layout, void *buffer);
PyLongObject *PyLong_Import(PyLongLayout layout, void *buffer);
```

This might work for the GMP, as it has
`!mpz_limbs_read()`{.interpreted-text role="c:func"} and
`!mpz_limbs_write()`{.interpreted-text role="c:func"} functions, that
can provide required access to internals of `!mpz_t`{.interpreted-text
role="c:struct"}. Other libraries may require using temporary buffers
and then mpz_import/export-like functions on their side.

The major drawback of this approach is that it\'s much more complex on
the CPython side (i.e. actual conversion between different layouts). For
example, implementation of the
`PyLong_FromNativeBytes()`{.interpreted-text role="c:func"} and the
`PyLong_AsNativeBytes()`{.interpreted-text role="c:func"} (together
provided restricted version of the required API) in the CPython took
\~500 LOC (c.f. \~100 LOC in the current implementation).

## Drop `~PyLongExport.value`{.interpreted-text role="c:member"} field from the export API

With this suggestion, only one export type will exist (array of
\"digits\"). If such view is not available for a given integer, it will
be either emulated by export functions or the
`PyLong_Export`{.interpreted-text role="c:func"} will return an error.
In both cases, it\'s assumed that users will use other C-API functions
to get \"small enough\" integers (i.e., that fits to some machine
integer types), like the `PyLong_AsLongAndOverflow`{.interpreted-text
role="c:func"}. The `PyLong_Export`{.interpreted-text role="c:func"}
will be inefficient (or just fail) in this case.

An example:

``` c
static int
mpz_set_PyLong(mpz_t z, PyObject *obj)
{
    int overflow;
#if SIZEOF_LONG == 8
    long value = PyLong_AsLongAndOverflow(obj, &overflow);
#else
    /* Windows has 32-bit long, so use 64-bit long long instead */
    long long value = PyLong_AsLongLongAndOverflow(obj, &overflow);
#endif
    Py_BUILD_ASSERT(sizeof(value) == sizeof(int64_t));

    if (!overflow) {
        if (LONG_MIN <= value && value <= LONG_MAX) {
            mpz_set_si(z, (long)value);
        }
        else {
            mpz_import(z, 1, -1, sizeof(int64_t), 0, 0, &value);
            if (value < 0) {
                mpz_t tmp;
                mpz_init(tmp);
                mpz_ui_pow_ui(tmp, 2, 64);
                mpz_sub(z, z, tmp);
                mpz_clear(tmp);
            }
        }

    }
    else {
        static PyLongExport long_export;

        if (PyLong_Export(obj, &long_export) < 0) {
            return -1;
        }
        mpz_import(z, long_export.ndigits, int_digits_order, int_digit_size,
                   int_endianness, int_nails, long_export.digits);
        if (long_export.negative) {
            mpz_neg(z, z);
        }
        PyLong_FreeExport(&long_export);
    }
    return 0;
}
```

This might look as a simplification from the API designer point of view,
but will be less convenient for end users. They will have to follow
Python development, benchmark different variants for exporting small
integers (is that obvious why above case was chosen instead of
`PyLong_AsInt64`{.interpreted-text role="c:func"}?), maybe support
different code paths for various CPython versions or across different
Python implementations.

# Discussions

- Discourse: [PEP 757 -- C API to import-export Python
  integers](https://discuss.python.org/t/63895)
- [C API Working Group decision issue
  #35](https://github.com/capi-workgroup/decisions/issues/35)
- [Pull request #121339](https://github.com/python/cpython/pull/121339)
- [Issue #102471](https://github.com/python/cpython/issues/102471): The
  C-API for Python to C integer conversion is, to be frank, a mess.
- [Add public function
  PyLong_GetDigits()](https://github.com/capi-workgroup/decisions/issues/31)
- [Consider restoring \_PyLong_New() function as
  public](https://github.com/python/cpython/issues/111415)
- [Pull request
  gh-106320](https://github.com/python/cpython/pull/108604): Remove
  private [PyLong_New]{#pylong_new}() function.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
