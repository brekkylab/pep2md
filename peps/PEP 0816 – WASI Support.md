---
pep: 816
title: WASI Support
author:
- Brett Cannon <brett@python.org>
discussions_to: https://discuss.python.org/t/pep-816-wasi-support/105237
status: Active
type: Informational
created: 05-Nov-2025
post_history:
- '`08-Dec-2025 <https://discuss.python.org/t/pep-816-wasi-support/105237>`__'
resolution: https://discuss.python.org/t/pep-816-wasi-support/105237/3
python_status: Active
url: https://peps.python.org/pep-0816/
source_path: https://github.com/python/peps/blob/main/peps/pep-0816.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:09+00:00'
---

# Abstract

This PEP outlines the expected support for [WASI](https://wasi.dev) by
CPython. It contains enough details to know what WASI and WASI SDK
version is expected to be supported for any release of CPython while
official WASI support is specified in `11`{.interpreted-text
role="pep"}.

# Motivation

CPython has supported WASI according to `11`{.interpreted-text
role="pep"} since Python 3.11. As part of this support, CPython needs to
target two different things: the [WASI](https://wasi.dev) version and
the [WASI SDK](https://github.com/WebAssembly/wasi-sdk) version (both of
whose development is driven by the [Bytecode
Alliance](https://bytecodealliance.org)). The former is the
specification of WASI itself while the latter is a version of
[clang](https://clang.llvm.org) with a specific version of
[wasi-libc](https://github.com/WebAssembly/wasi-libc) as the sysroot
that allows for compiling CPython to WASI. There is roughly an annual
release cadence for new WASI versions while there\'s no set release
cadence for WASI SDK.

Agreeing on which WASI and WASI SDK versions to support allows for clear
targeting of the CPython code base towards those versions. This also
lets the community set appropriate expectations as to what will (not) be
considered a bug if it only manifests itself under a certain WASI or
WASI SDK version. It also provides the community an overall target for
WASI and WASI SDK for any specific Python version when building other
software like libraries. This is important as WASI SDK is NOT forwards-
or backwards-compatible due to the ABI of wasi-libc not making any
compatibility guarantees, making broad coordination important so code
works together.

This coordination and recording around version targets can be important
in situations where the selected version is non-obvious. For example,
WASI SDK 26 and 27 have a
[bug](https://github.com/WebAssembly/wasi-libc/issues/617) which cause
CPython to hang in certain situations (including exiting the REPL).
Because the bug is in thread support code it wouldn\'t necessarily be
obvious to others in the community that CPython will not target those
versions and thus 3rd-party code should also avoid those versions.

# Rationale

While technically separate, CPython cannot support a version of WASI
until WASI SDK supports it. WASI versions are considered
backwards-compatible with each other, but WASI SDK is NOT compatible
forwards or backwards thanks to wasi-libc not having ABI compatibility
guarantees. As such, it\'s important to set support expectations for a
specific WASI SDK version in CPython. Historically, the support
difference between WASI SDK versions for CPython have involved settings
in the `config.site` file that is maintained for WASI. Support issues
have come up due to bugs in WASI SDK itself. Finally, new features being
supported by WASI SDK can also cause code that wasn\'t previously used
in a WASI build to suddenly be run which can require code updates to
pass tests.

As for WASI version support, that typically translates into what stdlib
modules are (potentially) usable with a WASI build. For example, WASI
0.2 added socket support and WASI 0.3.1 is scheduled to have some form
of threading support. Knowing what WASI version is supported sets
expectations for what stdlib modules should be supported.

Interpreter feature availability can be dependent on the WASI version.
For instance, until there is threading support there can\'t be
free-threading support in WASI. Once again, this helps set expectations
of what should be working based on the target WASI version.

# Specification

The WASI and WASI SDK version supported by a CPython version in CI or
its stable Buildbot builder when b1 is released MUST be the version to
be supported for the lifetime of that Python version after this PEP is
accepted. If there is a discrepancy between CI and the Buildbot builder
for some reason, the WASI maintainers as specified by
`11`{.interpreted-text role="pep"} will choose which sets of versions
will be designated as the versions to support.

The WASI version and WASI SDK version supported for a Python version
MUST be recorded in `11`{.interpreted-text role="pep"} as an official
record. This is to be recorded by the maintainers of WASI as listed in
`11`{.interpreted-text role="pep"} and done around the time of the b1
release.

If for some reason a supported WASI SDK version needs to change after
being recorded, a note will be made in `11`{.interpreted-text
role="pep"} as to when and why the change was made. Such a change is at
the discretion of the maintainers of WASI support as listed in
`11`{.interpreted-text role="pep"} and does not require steering council
approval. The expectation, though, is that such a change SHOULD NOT
occur.

Changing the WASI version after it has been recorded MUST NOT occur
UNLESS the steering council approves it. This is due to the increased
support burden for new WASI versions and the shift in expectations of
what CPython would support when support expectations have already been
set.

Any updates to `11`{.interpreted-text role="pep"} to reflect the
appropriate WASI version for the target triple for the main branch MUST
be made as needed, but it does NOT require steering council approval to
update. The steering council is spared needing to approve such an update
as it does not constitute a new platform and is more in line with a new
OS release which currently does not require steering council approval.

# Designated Support

Note that while WASI SDK in some places lists both a major and minor
version, in actuality the minor version has never been set to anything
other than `0` and there\'s an expectation that [any minor version will
be ABI compatible with the overall major
version](https://bytecodealliance.zulipchat.com/#narrow/channel/219900-wasi/topic/Platform.20tags.20for.20packages.20targeting.20WASI/near/516771862).
As well, the WASI community only refers to WASI SDK versions by their
major version due to there having never been a minor release.
Subsequently, this PEP only records the major version of WASI SDK until
such time that there\'s a need to record a minor version.

  Python   WASI   WASI SDK
  -------- ------ ----------
  3.14     0.1    24
  3.13     0.1    24
  3.12     0.1    21
  3.11     0.1    21

## Notes

All versions prior to Python 3.15 predate this PEP. The version support
for those versions is based on what was supported when this PEP was
written.

WASI was a tier 3 platform according to `11`{.interpreted-text
role="pep"} for Python 3.11 and 3.12. WASI became a tier 2 platform
starting with Python 3.13.

WASI 0.2 support has been skipped due to lack of time, to the point that
it was deemed better to go straight to WASI 0.3 instead. This is based
on a recommendation from the [Bytecode
Alliance](https://bytecodealliance.org).

WASI SDK 26 and 27 have a
[bug](https://github.com/WebAssembly/wasi-libc/issues/617) which causes
CPython to hang in certain situations, and so they have been skipped.

# Acknowledgements

Thanks to Joel Dice and Ben Brandt of the Python
[sub-group](https://github.com/bytecodealliance/SIG-Guest-Languages/blob/main/docs/subgroups.md)
of the [guest languages
SIG](https://github.com/bytecodealliance/SIG-Guest-Languages) of the
[Bytecode Alliance](https://bytecodealliance.org) for discussing the
specification of this PEP.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
