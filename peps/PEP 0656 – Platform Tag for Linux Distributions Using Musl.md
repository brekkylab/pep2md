---
pep: 656
title: Platform Tag for Linux Distributions Using Musl
author:
- Tzu-ping Chung <uranusjr@gmail.com>
sponsor: Brett Cannon <brett@python.org>
pep_delegate: Paul Moore <p.f.moore@gmail.com>
discussions_to: https://discuss.python.org/t/7165
status: Final
type: Standards Track
topic: Packaging
created: 17-Mar-2021
post_history:
- 17-Mar-2021
- 18-Apr-2021
resolution: https://discuss.python.org/t/7165/32
python_status: Final
url: https://peps.python.org/pep-0656/
source_path: https://github.com/python/peps/blob/main/peps/pep-0656.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:27+00:00'
---

# Abstract

This PEP proposes a new platform tag series `musllinux` for binary
Python package distributions for a Python installation that depends on
musl on a Linux distribution. The tag works similarly to the \"perennial
manylinux\" platform tags specified in `600`{.interpreted-text
role="pep"}, but targeting platforms based on musl instead.

# Motivation

With the wide use of containers, distributions such as Alpine Linux
[\[alpine\]](#alpine){.citation}, have been gaining more popularity than
ever. Many of them based on musl [\[musl\]](#musl){.citation}, a
different libc implementation from glibc, and therefore cannot use the
existing `manylinux` platform tags. This means that Python package
projects cannot deploy binary distributions on PyPI for them. Users of
such projects demand build constraints from those projects, putting
unnecessary burden on project maintainers.

# Rationale

According to the documentation, musl has a stable ABI, and maintains
backwards compatibility
[\[musl-compatibility\]](#musl-compatibility){.citation}
[\[compare-libcs\]](#compare-libcs){.citation}, so a binary compiled
against an earlier version of musl is guaranteed to run against a newer
musl runtime [\[musl-compat-ml\]](#musl-compat-ml){.citation}.
Therefore, we use a scheme similar to the glibc-version-based manylinux
tags, but against musl versions instead of glibc.

Logic behind the new platform tag largely follows
`600`{.interpreted-text role="pep"} (\"perennial manylinux\"), and
requires wheels using this tag make similar promises. Please refer to
`600`{.interpreted-text role="pep"} for more details on rationale and
reasoning behind the design.

The `musllinux` platform tags only apply to Python interpreters
dynamically linked against the musl libc and executed on the runtime
shared library, on a Linux operating system. Statically linked
interpreters or mixed builds with other libc implementations (such as
glibc) are out of scope and not supported by platform tags defined in
this document. Such interpreters should not claim compatibility with
`musllinux` platform tags.

# Specification

Tags using the new scheme will take the form:

    musllinux_${MUSLMAJOR}_${MUSLMINOR}_${ARCH}

This tag promises the wheel works on any mainstream Linux distribution
that uses musl version `${MUSLMAJOR}.${MUSLMINOR}`, following the
perennial design. All other system-level dependency requirements rely on
the community\'s definition to the intentionally vague \"mainstream\"
description introduced in `600`{.interpreted-text role="pep"}. A wheel
may make use of newer system dependencies when all mainstream
distributions using the specified musl version provide the dependency by
default; once all mainstream distributions on the musl version ship a
certain dependency version by default, users relying on older versions
are automatically removed from the coverage of that `musllinux` tag.

## Reading the musl version

The musl version values can be obtained by executing the musl libc
shared library the Python interpreter is currently running on, and
parsing the output:

    import re
    import subprocess

    def get_musl_major_minor(so: str) -> tuple[int, int] | None:
        """Detect musl runtime version.

        Returns a two-tuple ``(major, minor)`` that indicates musl
        library's version, or ``None`` if the given libc .so does not
        output expected information.

        The libc library should output something like this to stderr::

            musl libc (x86_64)
            Version 1.2.2
            Dynamic Program Loader
        """
        proc = subprocess.run([so], stderr=subprocess.PIPE, text=True)
        lines = (line.strip() for line in proc.stderr.splitlines())
        lines = [line for line in lines if line]
        if len(lines) < 2 or lines[0][:4] != "musl":
            return None
        match = re.match(r"Version (\d+)\.(\d+)", lines[1])
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None

There are currently two possible ways to find the musl library\'s
location that a Python interpreter is running on, either with the system
`ldd` command [\[ldd\]](#ldd){.citation}, or by parsing the `PT_INTERP`
section\'s value from the executable\'s ELF header
[\[elf\]](#elf){.citation}.

## Formatting the tag

Distributions using the tag make similar promises to those described in
`600`{.interpreted-text role="pep"}, including:

1.  The distribution works on any mainstream Linux distributions with
    musl version `${MUSLMAJOR}.${MUSLMINOR}` or later.
2.  The distribution\'s `${ARCH}` matches the return value of
    `sysconfig.get_platform()` on the host system, replacing period
    (`.`) and hyphen (`-`) characters with underscores (`_`), as
    outlined in `425`{.interpreted-text role="pep"} and
    `427`{.interpreted-text role="pep"}.

Example values:

    musllinux_1_1_x86_64   # musl 1.1 running on x86-64.
    musllinux_1_2_aarch64  # musl 1.2 running on ARM 64-bit.

The value can be formatted with the following Python code:

    import sysconfig

    def format_musllinux(musl_version: tuple[int, int]) -> str:
        os_name, sep, arch = sysconfig.get_platform().partition("-")
        assert os_name == "linux" and sep, "Not a Linux"
        arch = arch.replace(".", "_").replace("-", "_")
        return f"musllinux_{musl_version[0]}_{musl_version[1]}_{arch}"

## Recommendations to package indexes

It is recommended for Python package repositories, including PyPI, to
accept platform tags matching the following regular expression:

    musllinux_([0-9]+)_([0-9]+)_([^.-]+)

Python package repositories may impose additional requirements to reject
Wheels with known issues, including but not limited to:

- A `musllinux_1_1` wheel containing symbols only available in musl 1.2
  or later.
- Wheel that depends on external libraries not considered generally
  available to the intended audience of the package index.
- A platform tag claiming compatibility to a non-existent musl version
  (like `musllinux_9000_0`).

Such policies are ultimately up to individual package repositories. It
is not the author\'s intention to impose restrictions to the
maintainers.

# Backwards Compatibility

There are no backwards compatibility concerns in this PEP.

# Rejected Ideas

## Create a platform tag based specifically for Alpine Linux

Past experience on the `manylinux` tag series shows this approach would
be too costly time-wise. The author feels the \"works well with others\"
rule both is more inclusive and works well enough in practice.

# References

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

::: {#citations}

[alpine]{#alpine .citation-label}

:   <https://alpinelinux.org/>

[compare-libcs]{#compare-libcs .citation-label}

:   <https://www.etalabs.net/compare_libcs.html>

[elf]{#elf .citation-label}

:   <https://refspecs.linuxfoundation.org/elf/elf.pdf>

[ldd]{#ldd .citation-label}

:   <https://www.unix.com/man-page/posix/1/ldd/>

[musl]{#musl .citation-label}

:   <https://musl.libc.org>

[musl-compat-ml]{#musl-compat-ml .citation-label}

:   <https://mail.python.org/archives/list/distutils-sig@python.org/message/VRXSTNXWHPAVUW253ZCWWMP7WDTBAQDL/>

[musl-compatibility]{#musl-compatibility .citation-label}

:   <https://wiki.musl-libc.org/compatibility.html>
:::
