---
pep: 775
title: Make zlib required to build CPython
author:
- Gregory P. Smith <greg@krypto.org>
- Stan Ulbrych <stan@python.org>
- Petr Viktorin <encukou@gmail.com>
discussions_to: https://discuss.python.org/t/82672
status: Withdrawn
type: Standards Track
created: 24-Feb-2025
python_version: '3.14'
post_history:
- '`23-Jan-2023 <https://discuss.python.org/t/23062>`__'
- '`01-Mar-2025 <https://discuss.python.org/t/82672>`__'
python_status: Withdrawn
url: https://peps.python.org/pep-0775/
source_path: https://github.com/python/peps/blob/main/peps/pep-0775.rst
source_commit: 6f5c20e3f2e7aa080b96474253d3c02b259d29ee
---

# Abstract

Building CPython without the [zlib](https://zlib.net) compression
library will no be longer supported, and the `zlib`{.interpreted-text
role="mod"} module will be required in the standard library. The only
exception is [WASI](https://wasi.dev), as zlib is not currently
supported in CPython on WASI. Building the interpreter without zlib may
still be possible, but formally unsupported.

# PEP Withdrawal

This PEP was withdrawn by the authors on 2025-05-07. After further
reflection, we realized it did not provide sufficient value and was met
with significant negative feedback, particularly regarding the proposed
exception for WASI.

# Motivation

The zlib library, which powers the `!zlib`{.interpreted-text role="mod"}
Python module, is available on all supported systems except WASI.

Many wheels on PyPI, including the `pip`{.interpreted-text role="pypi"}
installer, require zlib. Users of pip would consider CPython without
zlib to be broken, but mostly don\'t notice because all major builds of
CPython include zlib.

CPython developers don\'t really notice either. It turns out that at the
time of writing, at least one CPython test fails without zlib (the
\"skip\" decorator in `test_peg_generator.test_c_parser` is applied too
late), but our CI didn\'t catch this.

This PEP treats this as an issue in documentation and messaging. In
practice, we already don\'t support building CPython without zlib; we
should just say so.

# Rationale

There are possible use cases for zlib-less builds, such as embedding and
bootstrapping, as well as unforeseen ones. Therefore, we don\'t *remove*
support for zlib-less systems; we mark them unsupported and invite
affected users to do their own testing, or to share use cases that can
make us reconsider this decision.

zlib is not yet used by default on the WASI platform \-- mostly because
adding it hasn\'t yet been a priority there. (Note that
[Pyodide](https://pyodide.org), the main \"real-world\" CPython
distribution for WASI, does include zlib.) We take this as an
opportunity to continue testing a platform without zlib, so that we
don\'t unintentionally break unsupported builds yet.

# Specification

In standard library modules that use zlib for optional functionality,
that functionality will raise `ImportError` when used. Code to generate
more \"friendly\" error messages, or to pre-check whether zlib is
available, will be removed. All functionality unrelated to zlib will
still be usable if zlib is missing.

This affects the following modules, and more that depend on these
transitively:

- `shutil`{.interpreted-text role="mod"} (`gztar` and `zip` archive
  formats)
- `tarfile`{.interpreted-text role="mod"}, `zipfile`{.interpreted-text
  role="mod"}, `zipimport`{.interpreted-text role="mod"},
  `zipapp`{.interpreted-text role="mod"} (archive compression)
- `codecs`{.interpreted-text role="mod"} (`zlib_codec`)

`shutil.get_archive_formats()` will always include `zip` and `gztar` as
registered formats, even if they are unusable due to missing zlib.

The `configure` script will issue a warning when zlib is not found on
platforms other than WASI.

`test_zlib` will fail on platforms other than WASI. All other tests will
continue to be skipped \-- that is, uses of
`@test.support.requires_zlib` will be kept in place \-- for the benefit
of WASI, unsupported builds, and any possible reverts.

`11`{.interpreted-text role="pep"} will be adjusted to mark \"Systems
without zlib, except WASI\" as unsupported.

# Backwards Compatibility

In practice, nothing major changes, except in error cases \-- for
example, attempts to use tar compression without zlib available will
raise `ImportError` and not `CompressionError`.

# Security Implications

None known.

# How to Teach This

We don\'t expect that any instructions will need to change, as zlib is
already available in all relevant contexts.

# Reference Implementation

A reference implementation may be found in a pull request to the CPython
repository,
[python/cpython#130297](https://github.com/python/cpython/pull/130297)

# Future work

In the future, if no use cases for zlib-less builds are found, zlib may
be made fully required. The main changes needed for that would be making
the `configure` script raise a hard error, and removing
`@test.support.requires_zlib`.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
