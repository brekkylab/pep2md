---
pep: 571
title: The manylinux2010 Platform Tag
author:
- Mark  Williams <mrw@enotuniq.org>
- Geoffrey Thomas <geofft@ldpreload.com>
- Thomas Kluyver <thomas@kluyver.me.uk>
bdfl_delegate: Alyssa Coghlan <ncoghlan@gmail.com>
discussions_to: distutils-sig@python.org
status: Superseded
type: Informational
topic: Packaging
created: 05-Feb-2018
post_history: []
superseded_by: '600'
resolution: https://mail.python.org/pipermail/distutils-sig/2018-April/032156.html
python_status: Superseded
url: https://peps.python.org/pep-0571/
source_path: https://github.com/python/peps/blob/main/peps/pep-0571.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:38+00:00'
---

# Abstract

This PEP proposes the creation of a `manylinux2010` platform tag to
succeed the `manylinux1` tag introduced by `513`{.interpreted-text
role="pep"}. It also proposes that PyPI and `pip` both be updated to
support uploading, downloading, and installing `manylinux2010`
distributions on compatible platforms.

# Rationale

True to its name, the `manylinux1` platform tag has made the
installation of binary extension modules a reality on many Linux
systems. Libraries like `cryptography`[^1] and `numpy`[^2] are more
accessible to Python developers now that their installation on common
architectures does not depend on fragile development environments and
build toolchains.

`manylinux1` wheels achieve their portability by allowing the extension
modules they contain to link against only a small set of system-level
shared libraries that export versioned symbols old enough to benefit
from backwards-compatibility policies. Extension modules in a
`manylinux1` wheel that rely on `glibc`, for example, must be built
against version 2.5 or earlier; they may then be run systems that
provide more recent `glibc` version that still export the required
symbols at version 2.5.

`513`{.interpreted-text role="pep"} drew its whitelisted shared
libraries and their symbol versions from CentOS 5.11, which was the
oldest supported CentOS release at the time of its writing.
Unfortunately, CentOS 5.11 reached its end-of-life on March 31st, 2017
with a clear warning against its continued use.[^3] No further updates,
such as security patches, will be made available. This means that its
packages will remain at obsolete versions that hamper the efforts of
Python software packagers who use the `manylinux1` Docker image.

CentOS 6 is now the oldest supported CentOS release, and will receive
maintenance updates through November 30th, 2020.[^4] We propose that a
new `425`{.interpreted-text role="pep"}-style platform tag called
`manylinux2010` be derived from CentOS 6 and that the `manylinux`
toolchain, PyPI, and `pip` be updated to support it.

This was originally proposed as `manylinux2`, but the versioning has
been changed to use calendar years (also known as CalVer[^5]). This
makes it easier to define future *manylinux* tags out of order: for
example, a hypothetical `manylinux2017` standard may be defined via a
new PEP before `manylinux2014`, or a `manylinux2007` standard might be
defined that targets systems older than this PEP but newer than
`manylinux1`.

Calendar versioning also gives a rough idea of which Linux distribution
versions support which tag: `manylinux2010` will work on most
distribution versions released since 2010. This is only an
approximation, however: the actual compatibility rules are defined
below, and some newer distributions may not meet them.

# The `manylinux2010` policy

The following criteria determine a `linux` wheel\'s eligibility for the
`manylinux2010` tag:

1.  The wheel may only contain binary executables and shared objects
    compiled for one of the two architectures supported by CentOS 6:
    x86_64 or i686.[^6]

2.  The wheel\'s binary executables or shared objects may not link
    against externally-provided libraries except those in the following
    whitelist: :

        libgcc_s.so.1
        libstdc++.so.6
        libm.so.6
        libdl.so.2
        librt.so.1
        libc.so.6
        libnsl.so.1
        libutil.so.1
        libpthread.so.0
        libresolv.so.2
        libX11.so.6
        libXext.so.6
        libXrender.so.1
        libICE.so.6
        libSM.so.6
        libGL.so.1
        libgobject-2.0.so.0
        libgthread-2.0.so.0
        libglib-2.0.so.0

    This list is identical to the externally-provided libraries
    whitelisted for `manylinux1`, minus `libncursesw.so.5` and
    `libpanelw.so.5`.[^7] `libpythonX.Y` remains ineligible for
    inclusion for the same reasons outlined in `513`{.interpreted-text
    role="pep"}.

    `libcrypt.so.1` was retrospectively removed from the whitelist after
    Fedora 30 was released with `libcrypt.so.2` instead.

    On Debian-based systems, these libraries are provided by the
    packages:

      Package        Libraries
      -------------- ----------------------------------------------------------------------------------------------------------
      libc6          libdl.so.2, libresolv.so.2, librt.so.1, libc.so.6, libpthread.so.0, libm.so.6, libutil.so.1, libnsl.so.1
      libgcc1        libgcc_s.so.1
      libgl1         libGL.so.1
      libglib2.0-0   libgobject-2.0.so.0, libgthread-2.0.so.0, libglib-2.0.so.0
      libice6        libICE.so.6
      libsm6         libSM.so.6
      libstdc++6     libstdc++.so.6
      libx11-6       libX11.so.6
      libxext6       libXext.so.6
      libxrender1    libXrender.so.1

    On RPM-based systems, they are provided by these packages:

      Package      Libraries
      ------------ ----------------------------------------------------------------------------------------------------------
      glib2        libglib-2.0.so.0, libgthread-2.0.so.0, libgobject-2.0.so.0
      glibc        libresolv.so.2, libutil.so.1, libnsl.so.1, librt.so.1, libpthread.so.0, libdl.so.2, libm.so.6, libc.so.6
      libICE       libICE.so.6
      libX11       libX11.so.6
      libXext:     libXext.so.6
      libXrender   libXrender.so.1
      libgcc:      libgcc_s.so.1
      libstdc++    libstdc++.so.6
      mesa         libGL.so.1

3.  If the wheel contains binary executables or shared objects linked
    against any whitelisted libraries that also export versioned
    symbols, they may only depend on the following maximum versions:

        GLIBC_2.12
        CXXABI_1.3.3
        GLIBCXX_3.4.13
        GCC_4.5.0

    As an example, `manylinux2010` wheels may include binary artifacts
    that require `glibc` symbols at version `GLIBC_2.4`, because this an
    earlier version than the maximum of `GLIBC_2.12`.

4.  If a wheel is built for any version of CPython 2 or CPython versions
    3.0 up to and including 3.2, it *must* include a CPython ABI tag
    indicating its Unicode ABI. A `manylinux2010` wheel built against
    Python 2, then, must include either the `cpy27mu` tag indicating it
    was built against an interpreter with the UCS-4 ABI or the `cpy27m`
    tag indicating an interpreter with the UCS-2 ABI.
    (`3149`{.interpreted-text role="pep"},[^8])

5.  A wheel *must not* require the `PyFPE_jbuf` symbol. This is achieved
    by building it against a Python compiled *without* the
    `--with-fpectl` `configure` flag.

# Compilation of Compliant Wheels

Like `manylinux1`, the `auditwheel` tool adds `manylinux2010` platform
tags to `linux` wheels built by `pip wheel` or `bdist_wheel` in a
`manylinux2010` Docker container.

## Docker Image

Two `manylinux2010` Docker images based on CentOS 6 are provided for
building binary `linux` wheels that can reliably be converted to
`manylinux2010` wheels.[^9] The x86_64 and i686 images comes with a new
compiler suite installed (`gcc`, `g++`, and `gfortran` from
`devtoolset-8`) as well as the latest releases of Python and `pip`.

### Compatibility with kernels that lack `vsyscall`

A Docker container assumes that its userland is compatible with its
host\'s kernel. Unfortunately, an increasingly common kernel
configuration breaks this assumption for x86_64 CentOS 6 Docker images.

Versions 2.14 and earlier of `glibc` require the kernel provide an
archaic system call optimization known as `vsyscall` on x86_64.[^10] To
effect the optimization, the kernel maps a read-only page of
frequently-called system calls \-- most notably `time(2)` \-- into each
process at a fixed memory location. `glibc` then invokes these system
calls by dereferencing a function pointer to the appropriate offset into
the `vsyscall` page and calling it. This avoids the overhead associated
with invoking the kernel that affects normal system call invocation.
`vsyscall` has long been deprecated in favor of an equivalent mechanism
known as vDSO, or \"virtual dynamic shared object\", in which the kernel
instead maps a relocatable virtual shared object containing the
optimized system calls into each process.[^11]

The `vsyscall` page has serious security implications because it does
not participate in address space layout randomization (ASLR). Its
predictable location and contents make it a useful source of gadgets
used in return-oriented programming attacks.[^12] At the same time, its
elimination breaks the x86_64 ABI, because `glibc` versions that depend
on `vsyscall` suffer from segmentation faults when attempting to
dereference a system call pointer into a non-existent page. As a
compromise, Linux 3.1 implemented an \"emulated\" `vsyscall` that
reduced the executable code, and thus the material for ROP gadgets,
mapped into the process.[^13] `vsyscall=emulated` has been the default
configuration in most distribution\'s kernels for many years.

Unfortunately, `vsyscall` emulation still exposes predictable code at a
reliable memory location, and continues to be useful for return-oriented
programming.[^14] Because most distributions have now upgraded to
`glibc` versions that do not depend on `vsyscall`, they are beginning to
ship kernels that do not support `vsyscall` at all.[^15]

CentOS 5.11 and 6 both include versions of `glibc` that depend on the
`vsyscall` page (2.5 and 2.12.2 respectively), so containers based on
either cannot run under kernels provided with many distribution\'s
upcoming releases.[^16] If Travis CI, for example, begins running jobs
under a kernel that does not provide the `vsyscall` interface, Python
packagers will not be able to use our Docker images there to build
`manylinux` wheels.[^17]

We have derived a patch from the `glibc` git repository that backports
the removal of all dependencies on `vsyscall` to the version of `glibc`
included with our `manylinux2010` image.[^18] Rebuilding `glibc`, and
thus building `manylinux2010` image itself, still requires a host kernel
that provides the `vsyscall` mechanism, but the resulting image can be
both run on hosts that provide it and those that do not. Because the
`vsyscall` interface is an optimization that is only applied to running
processes, the `manylinux2010` wheels built with this modified image
should be identical to those built on an unmodified CentOS 6 system.
Also, the `vsyscall` problem applies only to x86_64; it is not part of
the i686 ABI.

## Auditwheel

The `auditwheel` tool has also been updated to produce `manylinux2010`
wheels.[^19] Its behavior and purpose are otherwise unchanged from
`513`{.interpreted-text role="pep"}.

# Platform Detection for Installers

Platforms may define a `manylinux2010_compatible` boolean attribute on
the `_manylinux` module described in `513`{.interpreted-text
role="pep"}. A platform is considered incompatible with `manylinux2010`
if the attribute is `False`.

If the `_manylinux` module is not found, or it does not have the
attribute `manylinux2010_compatible`, tools may fall back to checking
for glibc. If the platform has glibc 2.12 or newer, it is assumed to be
compatible unless the `_manylinux` module says otherwise.

Specifically, the algorithm we propose is:

    def is_manylinux2010_compatible():
        # Only Linux, and only x86-64 / i686
        from distutils.util import get_platform
        if get_platform() not in ["linux-x86_64", "linux-i686"]:
            return False

        # Check for presence of _manylinux module
        try:
            import _manylinux
            return bool(_manylinux.manylinux2010_compatible)
        except (ImportError, AttributeError):
            # Fall through to heuristic check below
            pass

        # Check glibc version. CentOS 6 uses glibc 2.12.
        # PEP 513 contains an implementation of this function.
        return have_compatible_glibc(2, 12)

# Backwards compatibility with `manylinux1` wheels

As explained in `513`{.interpreted-text role="pep"}, the specified
symbol versions for `manylinux1` whitelisted libraries constitute an
*upper bound*. The same is true for the symbol versions defined for
`manylinux2010` in this PEP. As a result, `manylinux1` wheels are
considered `manylinux2010` wheels. A `pip` that recognizes the
`manylinux2010` platform tag will thus install `manylinux1` wheels for
`manylinux2010` platforms \-- even when explicitly set \-- when no
`manylinux2010` wheels are available.[^20]

# PyPI Support

PyPI should permit wheels containing the `manylinux2010` platform tag to
be uploaded in the same way that it permits `manylinux1`. It should not
attempt to verify the compatibility of `manylinux2010` wheels.

# Summary of changes to PEP 571

The following changes were made to this PEP based on feedback received
after it was approved:

- The maximum version symbol of `libgcc_s` was updated from `GCC_4.3.0`
  to `GCC_4.5.0` to address 32-bit Cent OS 6. This doesn\'t affect
  x86_64 because `libgcc_s` for x86_64 has no additional symbol from
  `GCC_4.3.0` to `GCC_4.5.0`.

# References

# Copyright

This document has been placed into the public domain.

[^1]: pyca/cryptography (<https://cryptography.io/>)

[^2]: numpy (<https://numpy.org>)

[^3]: CentOS 5.11 EOL announcement
    (<https://lists.centos.org/pipermail/centos-announce/2017-April/022350.html>)

[^4]: CentOS Product Specifications
    (<https://web.archive.org/web/20180108090257/https://wiki.centos.org/About/Product>)

[^5]: Calendar Versioning <http://calver.org/>

[^6]: CentOS Product Specifications
    (<https://web.archive.org/web/20180108090257/https://wiki.centos.org/About/Product>)

[^7]: ncurses 5 -\> 6 transition means we probably need to drop some
    libraries from the manylinux whitelist
    (<https://github.com/pypa/manylinux/issues/94>)

[^8]: SOABI support for Python 2.X and PyPy
    <https://github.com/pypa/pip/pull/3075>

[^9]: manylinux2010 Docker image
    (<https://quay.io/repository/pypa/manylinux2010_x86_64>)

[^10]: On vsyscalls and the vDSO (<https://lwn.net/Articles/446528/>)

[^11]: vdso(7) (<http://man7.org/linux/man-pages/man7/vdso.7.html>)

[^12]: Framing Signals \-- A Return to Portable Shellcode
    (<http://www.cs.vu.nl/~herbertb/papers/srop_sp14.pdf>)

[^13]: ChangeLog-3.1
    (<https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.1>)

[^14]: Project Zero: Three bypasses and a fix for one of Flash\'s
    Vector.\<\*\> mitigations
    (<https://googleprojectzero.blogspot.com/2015/08/three-bypasses-and-fix-for-one-of.html>)

[^15]: linux: activate CONFIG_LEGACY_VSYSCALL_NONE ?
    (<https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=852620>)

[^16]: \[Wheel-builders\] Heads-up re: new kernel configurations
    breaking the manylinux docker image
    (<https://mail.python.org/pipermail/wheel-builders/2016-December/000239.html>)

[^17]: Travis CI (<https://travis-ci.org/>)

[^18]: remove-vsyscall.patch
    <https://github.com/markrwilliams/manylinux/commit/e9493d55471d153089df3aafca8cfbcb50fa8093#diff-3eda4130bdba562657f3ec7c1b3f5720>

[^19]: auditwheel manylinux2 branch
    (<https://github.com/markrwilliams/auditwheel/tree/manylinux2>)

[^20]: pip manylinux2 branch
    <https://github.com/markrwilliams/pip/commits/manylinux2>
