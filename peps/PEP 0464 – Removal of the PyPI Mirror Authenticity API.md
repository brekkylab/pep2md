---
pep: 464
title: Removal of the PyPI Mirror Authenticity API
author:
- Donald Stufft <donald@stufft.io>
bdfl_delegate: Richard Jones <richard@python.org>
discussions_to: distutils-sig@python.org
status: Final
type: Process
topic: Packaging
created: 02-Mar-2014
post_history:
- 04-Mar-2014
replaces: '381'
resolution: https://mail.python.org/pipermail/distutils-sig/2014-March/024027.html
python_status: Final
url: https://peps.python.org/pep-0464/
source_path: https://github.com/python/peps/blob/main/peps/pep-0464.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:27:53+00:00'
---

# Abstract

This PEP proposes the deprecation and removal of the PyPI Mirror
Authenticity API, this includes the /serverkey URL and all of the URLs
under /serversig.

# Rationale

The PyPI mirroring infrastructure (defined in `381`{.interpreted-text
role="pep"}) provides a means to mirror the content of PyPI used by the
automatic installers, and as a component of that, it provides a method
for verifying the authenticity of the mirrored content.

This PEP proposes the removal of this API due to:

- There are no known implementations that utilize this API, this
  includes [pip](http://www.pip-installer.org/en/latest/) and
  [setuptools](http://pythonhosted.org//setuptools/).
- Because this API uses DSA it is vulnerable to leaking the private key
  if there is *any* bias in the random nonce.
- This API solves one small corner of the trust problem, however the
  problem itself is much larger and it would be better to have a fully
  fledged system, such as `The Update Framework <458>`{.interpreted-text
  role="pep"}, instead.

Due to the issues it has and the lack of use it is the opinion of this
PEP that it does not provide any practical benefit to justify the
additional complexity.

# Plan for Deprecation & Removal

Immediately upon the acceptance of this PEP the Mirror Authenticity API
will be considered deprecated and mirroring agents and installation
tools should stop accessing it.

Instead of actually removing it from the current code base (PyPI 1.0)
the current work to replace PyPI 1.0 with a new code base (PyPI 2.0)
will simply not implement this API. This would cause the API to be
\"removed\" when the switch from 1.0 to 2.0 occurs.

If PyPI 2.0 has not been deployed in place of PyPI 1.0 by Sept 01 2014
then this PEP will be implemented in the PyPI 1.0 code base instead (by
removing the associated code).

No changes will be required in the installers, however
`381`{.interpreted-text role="pep"} compliant mirroring clients, such as
[bandersnatch](https://pypi.python.org/pypi/bandersnatch/) and
[pep381client](https://pypi.python.org/pypi/pep381client/) will need to
be updated to no longer attempt to mirror the /serversig URLs.

# Copyright

This document has been placed in the public domain.
