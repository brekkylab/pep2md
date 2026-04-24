---
pep: 815
title: Deprecate ``RECORD.jws`` and ``RECORD.p7s``
author:
- Konstantin Schütze <konstin@mailbox.org>
- William Woodruff <william@yossarian.net>
sponsor: Emma Harper Smith <emma@python.org>
pep_delegate: Paul Moore <p.f.moore@gmail.com>
discussions_to: https://discuss.python.org/t/105232
status: Final
type: Standards Track
topic: Packaging
created: 04-Dec-2025
post_history:
- '`09-Jun-2025 <https://discuss.python.org/t/94968>`__'
- '`08-Dec-2025 <https://discuss.python.org/t/105232>`__'
resolution: '`28-Jan-2026 <https://discuss.python.org/t/105232/10>`__'
python_status: Final
url: https://peps.python.org/pep-0815/
source_path: https://github.com/python/peps/blob/main/peps/pep-0815.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:09+00:00'
---

::: canonical-pypa-spec
`packaging:binary-distribution-format`{.interpreted-text role="ref"}
:::

# Abstract

This PEP deprecates the `RECORD.jws` and `RECORD.p7s` wheel signature
files. Lack of support in tooling means that these virtually unused
files do not provide the security they purport. Users looking for wheel
signing should instead refer to `index hosted attestations
<packaging:index-hosted-attestations>`{.interpreted-text role="ref"}.

# Motivation

No major Python packaging tool supports generating or checking either
`RECORD.jws` or `RECORD.p7s`. Notably, neither pip nor uv validate the
hashes in `RECORD`, a requirement for using signature files. The
`binary distribution format <packaging:binary-distribution-format>`{.interpreted-text
role="ref"} presents them as security features, potentially resulting in
user confusion.

The state of the art for hashing and signing wheels has shifted from
in-archive information to out-of-archive information presented on the
index, such as hashes and
`attestations <packaging:index-hosted-attestations>`{.interpreted-text
role="ref"} in the
`simple repository API <packaging:simple-repository-api>`{.interpreted-text
role="ref"}. Unlike the hashes in `RECORD`, tools such as pip and uv
validate index provided hashes.

Both files are virtually unused. A GitHub search for
`path:**.dist-info/RECORD` yields 635k results,
`path:**.dist-info/RECORD.jws` has 8 distinct results and
`path:**.dist-info/RECORD.p7s` has zero results.

# Specification

The `RECORD.jws` and `RECORD.p7s` files are deprecated, and the
`binary distribution format specification
<packaging:binary-distribution-format>`{.interpreted-text role="ref"}
will be updated to reflect this. Build backends and other tools MUST NOT
add these files to wheels. Installers SHOULD NOT attempt to verify them,
while they remain excluded from `RECORD`.

# Backwards Compatibility

No build backends and installers that the authors are aware of require
any changes, as they do not support these files beyond skipping them
when processing the `RECORD` file. If any build backends do currently
write these files, they need to deprecate and eventually remove this
feature.

For verifying provenance, users should refer to
`index hosted attestations <packaging:index-hosted-attestations>`{.interpreted-text
role="ref"}.

# Security Implications

This PEP strengthens the security of the Python packaging ecosystem by
reducing the divergence between security features presented in the
specification and the security features supported by tools.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
