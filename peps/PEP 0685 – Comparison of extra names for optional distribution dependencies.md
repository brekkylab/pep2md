---
pep: 685
title: Comparison of extra names for optional distribution dependencies
author:
- Brett Cannon <brett@python.org>
pep_delegate: Paul Moore <p.f.moore@gmail.com>
discussions_to: https://discuss.python.org/t/14141
status: Final
type: Standards Track
topic: Packaging
created: 08-Mar-2022
post_history:
- '`08-Mar-2022 <https://discuss.python.org/t/14141>`__'
resolution: https://discuss.python.org/t/pep-685-comparison-of-extra-names-for-optional-distribution-dependencies/14141/55
python_status: Final
url: https://peps.python.org/pep-0685/
source_path: https://github.com/python/peps/blob/main/peps/pep-0685.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:03+00:00'
---

::: canonical-pypa-spec
:::

# Abstract

This PEP specifies how to normalize [distribution
extra](https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use)
names when performing comparisons. This prevents tools from either
failing to find an extra name, or accidentally matching against an
unexpected name.

# Motivation

The
[Provides-Extra](https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use)
core metadata specification states that an extra\'s name \"must be a
valid Python identifier\". `508`{.interpreted-text role="pep"} specifies
that the value of an `extra` marker may contain a letter, digit, or any
one of `.`, `-`, or `_` after the initial character. There is no other
[PyPA
specification](https://packaging.python.org/en/latest/specifications/)
which outlines how extra names should be written or normalized for
comparison. Due to the amount of packaging-related code in existence, it
is important to evaluate current practices by the community and
standardize on one that doesn\'t break most existing code, while being
something tool authors can agree to following.

The issue of there being no consistent standard was brought forward by
an [initial discussion](https://discuss.python.org/t/7614) noting that
the extra `adhoc-ssl` was not considered equal to the name `adhoc_ssl`
by pip 22.

# Rationale

`503`{.interpreted-text role="pep"} specifies how to normalize
distribution names:

    re.sub(r"[-_.]+", "-", name).lower()

This collapses any run of the characters `-`, `_` and `.` down to a
single `-`. For example, `---` `.` and `__` all get converted to just
`-`. This does **not** produce a valid Python identifier, per the core
metadata 2.2 specification for extra names.

[Setuptools 60 performs
normalization](https://github.com/pypa/setuptools/blob/b2f7b8f92725c63b164d5776f85e67cc560def4e/pkg_resources/__init__.py#L1324-L1330)
via:

    re.sub(r'[^A-Za-z0-9-.]+', '_', name).lower()

The use of an underscore/`_` differs from PEP 503\'s use of a
hyphen/`-`, and it also normalizes characters outside of those allowed
by `508`{.interpreted-text role="pep"}. Runs of `.` and `-`, unlike PEP
503, do **not** get normalized to one `_`, e.g. `..` stays the same. To
note, this is inconsistent with this function\'s docstring, which *does*
specify that all non-alphanumeric characters (which would include `-`
and `.`) are normalized and collapsed.

For pip 22, its \"extra normalisation behaviour is quite convoluted and
erratic\" [\[pip-erratic\]](#pip-erratic){.citation} and so its use is
not considered.

# Specification

When comparing extra names, tools MUST normalize the names being
compared using the semantics outlined in
`PEP 503 <0503#normalized-names>`{.interpreted-text role="pep"} for
names:

    re.sub(r"[-_.]+", "-", name).lower()

The [core
metadata](https://packaging.python.org/en/latest/specifications/core-metadata/)
specification will be updated such that the allowed names for
[Provides-Extra](https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use)
matches what `508`{.interpreted-text role="pep"} specifies for names.
This will bring extra naming in line with that of the
[Name](https://packaging.python.org/en/latest/specifications/core-metadata/#name)
field. Because this changes what is considered valid, it will lead to a
core metadata version increase to `2.3`.

For tools writing [core
metadata](https://packaging.python.org/en/latest/specifications/core-metadata/),
they MUST write out extra names in their normalized form. This applies
to the
[Provides-Extra](https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use)
field and the `extra marker <0508#extras>`{.interpreted-text role="pep"}
when used in the
[Requires-Dist](https://packaging.python.org/en/latest/specifications/core-metadata/#requires-dist-multiple-use)
field.

Tools generating metadata MUST raise an error if a user specified two or
more extra names which would normalize to the same name. Tools
generating metadata MUST raise an error if an invalid extra name is
provided as appropriate for the specified core metadata version. If a
project\'s metadata specifies an older core metadata version and the
name would be invalid with newer core metadata versions, tools reading
that metadata SHOULD warn the user. Tools SHOULD warn users when an
invalid extra name is read and SHOULD ignore the name to avoid
ambiguity. Tools MAY raise an error instead of a warning when reading an
invalid name, if they so desire.

# Backwards Compatibility

Moving to `503`{.interpreted-text role="pep"} normalization and
`508`{.interpreted-text role="pep"} name acceptance allows for all
preexisting, valid names to continue to be valid.

Based on research looking at a collection of wheels on PyPI
[\[pypi-results\]](#pypi-results){.citation}, the risk of extra name
clashes is limited to 73 instances when considering all extras names on
PyPI, valid or not (not just those within a single package) while *only*
looking at valid names leads to only 3 clashes:

- `dev-test`: `dev_test`, `dev-test`, `dev.test`
- `dev-lint`: `dev-lint`, `dev.lint`, `dev_lint`
- `apache-beam`: `apache-beam`, `apache.beam`

By requiring tools writing core metadata to only record the normalized
name, the issue of preexisting, invalid extra names should diminish over
time.

# Security Implications

It is possible that for a distribution that has conflicting extra names,
a tool ends up installing dependencies that somehow weaken the security
of the system. This is only hypothetical and if it were to occur, it
would probably be more of a security concern for the distributions
specifying such extras names rather than the distribution that pulled
them in together.

# How to Teach This

This should be transparent to users on a day-to-day basis. It will be up
to tools to educate/stop users when they select extra names which
conflict.

# Reference Implementation

No reference implementation is provided aside from the code above, but
the expectation is the [packaging project](https://packaging.pypa.io)
will provide a function in its `packaging.utils` module that will
implement extra name normalization. It will also implement extra name
comparisons appropriately. Finally, if the project ever gains the
ability to write out metadata, it will also implement this PEP.

# Transition Plan

There is a risk that a build tool will produce core metadata conforming
to version 2.3 and thus this PEP but which is consumed by a tool that is
unaware of this PEP (if that tool chooses to attempt to read a core
metadata version it does not directly support). In such a case there is
a chance that a user may specify an extra using an non-normalized name
which worked previously but which fails now.

As such, consumers of this PEP should be prioritized more than producers
so that users can be notified that they are specifying extra names which
are not normalized (and thus may break in the future).

# Rejected Ideas

## Using setuptools 60\'s normalization

Initially, this PEP proposed using setuptools `safe_extra()` for
normalization to try to minimize backwards-compatibility issues.
However, after checking various wheels on PyPI, it became clear that
standardizing **all** naming on `508`{.interpreted-text role="pep"} and
`503`{.interpreted-text role="pep"} semantics was easier and better
long-term, while causing minimal backwards compatibility issues.

# Open Issues

N/A

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

::: {#citations}

[pip-erratic]{#pip-erratic .citation-label}

:   Tzu-ping Chung on Python Discourse
    \<https://discuss.python.org/t/7614/10

[pypi-results]{#pypi-results .citation-label}

:   Paul Moore on Python Discourse
    <https://discuss.python.org/t/14141/17>
:::
