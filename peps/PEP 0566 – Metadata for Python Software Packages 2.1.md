---
pep: 566
title: Metadata for Python Software Packages 2.1
author:
- Dustin Ingram <di@python.org>
bdfl_delegate: Daniel Holth
discussions_to: distutils-sig@python.org
status: Final
type: Standards Track
topic: Packaging
created: 01-Dec-2017
python_version: 3.x
post_history: []
replaces: '345'
resolution: https://mail.python.org/pipermail/distutils-sig/2018-February/032014.html
python_status: Final
url: https://peps.python.org/pep-0566/
source_path: https://github.com/python/peps/blob/main/peps/pep-0566.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:27:58+00:00'
---

::: canonical-pypa-spec
`packaging:core-metadata`{.interpreted-text role="ref"}
:::

# Abstract

This PEP describes the changes between versions 1.2 and 2.1 of the core
metadata specification for Python packages. Version 1.2 is specified in
`345`{.interpreted-text role="pep"}.

It also changes to the canonical source for field specifications to the
[Core Metadata
Specification](https://packaging.python.org/specifications/core-metadata/)
reference document, which includes specifics of the field names, and
their semantics and usage.

# Fields

The canonical source for the names and semantics of each of the
supported metadata fields is the [Core Metadata
Specification](https://packaging.python.org/specifications/core-metadata/)
document.

Fields marked with \"(Multiple use)\" may be specified multiple times in
a single PKG-INFO file. Other fields may only occur once in a PKG-INFO
file. Fields marked with \"(optional)\" are not required to appear in a
valid PKG-INFO file; all other fields must be present.

## New in Version 2.1

### Description-Content-Type (optional)

A string stating the markup syntax (if any) used in the distribution\'s
description, so that tools can intelligently render the description.

Historically, tools like PyPI assume that a package\'s description is
formatted in [reStructuredText
(reST)](http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html),
and fall back on plain text if the description is not valid reST.

The introduction of this field allows PyPI to support additional types
of markup syntax, and not need to make this assumption.

The full specification for this field is defined in the [Core Metadata
Specification](https://packaging.python.org/specifications/core-metadata/).

### Provides-Extra (optional, multiple use)

A string containing the name of an optional feature. Must be a valid
Python identifier. May be used to make a dependency conditional on
whether the optional feature has been requested.

This introduction of this field allows package installation tools (such
as `pip`) to determine which extras are provided by a given package, and
so that package publication tools (such as `twine`) can check for issues
with environment markers which use extras.

The full specification for this field is defined in the [Core Metadata
Specification](https://packaging.python.org/specifications/core-metadata/).

## Changed in Version 2.1

### Name

The specification for the format of this field is now identical to the
distribution name specification defined in `508`{.interpreted-text
role="pep"}.

### Description

In addition to the `Description` header field, the distribution\'s
description may instead be provided in the message body (i.e., after a
completely blank line following the headers, with no indentation or
other special formatting necessary).

# Version Specifiers

Version numbering requirements and the semantics for specifying
comparisons between versions are defined in `440`{.interpreted-text
role="pep"}. Direct references as defined in `440`{.interpreted-text
role="pep"} are also permitted as an alternative to version specifiers.

Following `508`{.interpreted-text role="pep"}, version specifiers no
longer need to be surrounded by parentheses in the fields Requires-Dist,
Provides-Dist, Obsoletes-Dist or Requires-External, so e.g.
`requests >= 2.8.1` is now a valid value. The recommended format is
without parentheses, but tools parsing metadata should also be able to
handle version specifiers in parentheses. Further, public index servers
MAY prohibit strict version matching clauses or direct references in
these fields.

Usage of version specifiers is otherwise unchanged from
`345`{.interpreted-text role="pep"}.

# Environment markers

An **environment marker** is a marker that can be added at the end of a
field after a semi-colon (\";\"), to add a condition about the execution
environment.

The environment marker format used to declare such a condition is
defined in the environment markers section of `508`{.interpreted-text
role="pep"}.

Usage of environment markers is otherwise unchanged from
`345`{.interpreted-text role="pep"}.

# JSON-compatible Metadata

It may be necessary to store metadata in a data structure which does not
allow for multiple repeated keys, such as JSON.

The canonical method to transform metadata fields into such a data
structure is as follows:

1.  The original key-value format should be read with
    `email.parser.HeaderParser`;
2.  All transformed keys should be reduced to lower case. Hyphens should
    be replaced with underscores, but otherwise should retain all other
    characters;
3.  The transformed value for any field marked with \"(Multiple-use\")
    should be a single list containing all the original values for the
    given key;
4.  The `Keywords` field should be converted to a list by splitting the
    original value on commas;
5.  The message body, if present, should be set to the value of the
    `description` key.
6.  The result should be stored as a string-keyed dictionary.

# Summary of Differences From PEP 345

- Metadata-Version is now 2.1.
- Fields are now specified via the [Core Metadata
  Specification](https://packaging.python.org/specifications/core-metadata/).
- Added two new fields: `Description-Content-Type` and `Provides-Extra`
- Acceptable values for the `Name` field are now specified as per
  `508`{.interpreted-text role="pep"}.
- Added canonical method of transformation into JSON-compatible data
  structure.

# References

This document specifies version 2.1 of the metadata format. Version 1.0
is specified in `241`{.interpreted-text role="pep"}. Version 1.1 is
specified in `314`{.interpreted-text role="pep"}. Version 1.2 is
specified in `345`{.interpreted-text role="pep"}. Version 2.0, while not
formally accepted, was specified in `426`{.interpreted-text role="pep"}.

# Copyright

This document has been placed in the public domain.

# Acknowledgements

Thanks to Alyssa Coghlan and Thomas Kluyver for contributing to this
PEP.
