---
pep: 639
title: Improving License Clarity with Better Package Metadata
author:
- Philippe Ombredanne <pombredanne@nexb.com>
- C.A.M. Gerlach <CAM.Gerlach@Gerlach.CAM>
- Karolina Surma <karolina.surma@gazeta.pl>
pep_delegate: Brett Cannon <brett@python.org>
discussions_to: https://discuss.python.org/t/53020
status: Final
type: Standards Track
topic: Packaging
created: 15-Aug-2019
post_history:
- '`15-Aug-2019 <https://discuss.python.org/t/2154>`__'
- '`17-Dec-2021 <https://discuss.python.org/t/12622>`__'
- '`10-May-2024 <https://discuss.python.org/t/53020>`__'
resolution: https://discuss.python.org/t/53020/106
python_status: Final
url: https://peps.python.org/pep-0639/
source_path: https://github.com/python/peps/blob/main/peps/pep-0639.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:26+00:00'
---

::: canonical-pypa-spec
`core-metadata`{.interpreted-text role="ref"}
:::

# Abstract {#639-abstract}

This PEP defines a specification how licenses are documented in the
Python projects.

To achieve that, it:

- Adopts the [SPDX license expression syntax](#639-spdx) as a means of
  expressing the license for a Python project.
- Defines how to include license files within the projects, source and
  built distributions.
- Specifies the necessary changes to `Core Metadata`{.interpreted-text
  role="term"} and the corresponding
  `Pyproject Metadata key`{.interpreted-text role="term"}s
- Describes the necessary changes to the [source distribution
  (sdist)](https://packaging.python.org/specifications/source-distribution-format/),
  [built distribution
  (wheel)](https://packaging.python.org/specifications/binary-distribution-format/)
  and [installed
  project](https://packaging.python.org/specifications/recording-installed-packages/)
  standards.

This will make license declaration simpler and less ambiguous for
package authors to create, end users to understand, and tools to
programmatically process.

The changes will update the [Core Metadata
specification](https://packaging.python.org/specifications/core-metadata)
to version 2.4.

# Goals {#639-goals}

This PEP\'s scope is limited to covering new mechanisms for documenting
the license of a `distribution package`{.interpreted-text role="term"},
specifically defining:

- A means of specifying a SPDX `license expression`{.interpreted-text
  role="term"}.
- A method of including license texts in
  `distribution package`{.interpreted-text role="term"}s and installed
  `Project`{.interpreted-text role="term"}s.

The changes that this PEP requires have been designed to minimize impact
and maximize backward compatibility.

# Non-Goals {#639-non-goals}

This PEP doesn\'t recommend any particular license to be chosen by any
particular package author.

If projects decide not to use the new fields, no additional restrictions
are imposed by this PEP when uploading to PyPI.

This PEP also is not about license documentation for individual files,
though this is a
`surveyed topic <639-license-doc-source-files>`{.interpreted-text
role="ref"} in an appendix, nor does it intend to cover cases where the
`source distribution <Source Distribution (or "sdist")>`{.interpreted-text
role="term"} and `binary distribution`{.interpreted-text role="term"}
packages don\'t have
`the same licenses <639-rejected-ideas-difference-license-source-binary>`{.interpreted-text
role="ref"}.

# Motivation {#639-motivation}

Software must be licensed in order for anyone other than its creator to
download, use, share and modify it. Today, there are multiple fields
where licenses are documented in `Core Metadata`{.interpreted-text
role="term"}, and there are limitations to what can be expressed in each
of them. This often leads to confusion both for package authors and end
users, including distribution re-packagers.

This has triggered a number of license-related discussions and issues,
including on [outdated and ambiguous PyPI
classifiers](https://github.com/pypa/trove-classifiers/issues/17),
[license interoperability with other
ecosystems](https://github.com/pypa/interoperability-peps/issues/46),
[too many confusing license metadata
options](https://github.com/pypa/packaging-problems/issues/41), [limited
support for license files in the Wheel
project](https://github.com/pypa/wheel/issues/138), and [the lack of
precise license
metadata](https://github.com/pombredanne/spdx-pypi-pep/issues/1).

As a result, on average, Python packages tend to have more ambiguous and
missing license information than other common ecosystems. This is
supported by the [statistics page](https://clearlydefined.io/stats) of
the [ClearlyDefined project](https://clearlydefined.io), an [Open Source
Initiative](https://opensource.org) effort to help improve licensing
clarity of other FOSS projects, covering all packages from PyPI, Maven,
npm and Rubygems.

The current license classifiers could be extended to include the full
range of the SPDX identifiers while deprecating the ambiguous
classifiers (such as `License :: OSI Approved :: BSD License`).

However, there are multiple arguments against such an approach:

- It requires a great effort to duplicate the SPDX license list and keep
  it in sync.
- It is a hard break in backward compatibility, forcing package authors
  to update to new classifiers immediately when PyPI deprecates the old
  ones.
- It only covers packages under a single license; it doesn\'t address
  projects that vendor dependencies (e.g. Setuptools), offer a choice of
  licenses (e.g. Packaging) or were relicensed, adapt code from other
  projects or contain fonts, images, examples, binaries or other assets
  under other licenses.
- It requires both authors and tools understand and implement the
  PyPI-specific classifier system.
- It does not provide as clear an indicator that a package has adopted
  the new system, and should be treated accordingly.

# Rationale {#639-rationale}

A survey was conducted to map the existing license metadata definitions
in the `Python ecosystem <639-license-doc-python>`{.interpreted-text
role="ref"} and a
`variety of other packaging systems, Linux distributions,
language ecosystems and applications <639-license-doc-other-projects>`{.interpreted-text
role="ref"}.

The takeaways from the survey have guided the recommendations of this
PEP:

- SPDX and SPDX-like syntaxes are the most popular
  `license expression`{.interpreted-text role="term"}s in many modern
  package systems.
- Most Free and Open Source Software licenses require package authors to
  include their full text in a `Distribution Package`{.interpreted-text
  role="term"}.

Therefore, this PEP introduces two new Core Metadata fields:

- `License-Expression <639-spec-field-license-expression>`{.interpreted-text
  role="ref"} that provides an unambiguous way to express the license of
  a package using SPDX license expressions.
- `License-File <639-spec-field-license-file>`{.interpreted-text
  role="ref"} that offers a standardized way to include the full text of
  the license(s) with the package when distributed, and allows other
  tools consuming the `Core Metadata`{.interpreted-text role="term"} to
  locate a `distribution archive`{.interpreted-text role="term"}\'s
  license files.

Furthermore, this specification builds upon existing practice in the
[Setuptools](https://github.com/pypa/setuptools/issues/2739) and
[Wheel](https://github.com/pypa/wheel/issues/138) projects. An
up-to-date version of the current draft of this PEP is
[implemented](https://discuss.python.org/t/12622/22) in the
[Hatch](https://hatch.pypa.io/latest/) packaging tool, and an earlier
draft of the
`license files portion <639-spec-field-license-file>`{.interpreted-text
role="ref"} is [implemented in
Setuptools](https://github.com/pypa/setuptools/pull/2645).

# Terminology {#639-terminology}

The keywords \"MUST\", \"MUST NOT\", \"REQUIRED\", \"SHOULD\", \"SHOULD
NOT\", \"RECOMMENDED\", \"MAY\", and \"OPTIONAL\" in this document are
to be interpreted as described in `2119`{.interpreted-text role="rfc"}.

## License terms {#639-terminology-license}

The license-related terminology draws heavily from the [SPDX
Project](https://spdx.dev/), particularly
`license identifier`{.interpreted-text role="term"} and
`license expression`{.interpreted-text role="term"}.

::: glossary

license classifier

:   A [PyPI Trove classifier](https://pypi.org/classifiers) (as
    `described <packaging:core-metadata-classifier>`{.interpreted-text
    role="ref"} in the `Core Metadata`{.interpreted-text role="term"}
    specification) which begins with `License ::`.

license expression SPDX expression A string with valid [SPDX license
expression
syntax](https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/)
including one or more SPDX `license identifier`{.interpreted-text
role="term"}(s), which describes a `Project`{.interpreted-text
role="term"}\'s license(s) and how they inter-relate. Examples:
`GPL-3.0-or-later`, `MIT AND (Apache-2.0 OR BSD-2-clause)`

license identifier SPDX identifier A valid [SPDX short-form license
identifier](https://spdx.dev/ids/), as described in the
`639-spec-field-license-expression`{.interpreted-text role="ref"}
section of this PEP. This includes all valid SPDX identifiers and the
custom `LicenseRef-[idstring]` strings conforming to the [SPDX
specification, clause
10.1](https://spdx.github.io/spdx-spec/v2.2.2/other-licensing-information-detected/).
Examples: `MIT`, `GPL-3.0-only`, `LicenseRef-My-Custom-License`

root license directory license directory The directory under which
license files are stored in a `project source tree`{.interpreted-text
role="term"}, `distribution archive`{.interpreted-text role="term"} or
`installed project`{.interpreted-text role="term"}. Also, the root
directory that their paths recorded in the
`License-File <639-spec-field-license-file>`{.interpreted-text
role="ref"} `Core Metadata field`{.interpreted-text role="term"} are
relative to. Defined to be the
`project root directory`{.interpreted-text role="term"} for a
`project source tree`{.interpreted-text role="term"} or
`source distribution <Source Distribution (or "sdist")>`{.interpreted-text
role="term"}; and a subdirectory named `licenses` of the directory
containing the `built metadata`{.interpreted-text role="term"}--- i.e.,
the `.dist-info/licenses` directory--- for a
`Built Distribution`{.interpreted-text role="term"} or
`installed project`{.interpreted-text role="term"}.
:::

# Specification {#639-specification}

The changes necessary to implement this PEP include:

- additions to
  `Core Metadata <639-spec-core-metadata>`{.interpreted-text
  role="ref"}, as defined in the
  [specification](https://packaging.python.org/specifications/core-metadata).
- additions to the author-provided
  `project source metadata <639-spec-source-metadata>`{.interpreted-text
  role="ref"}, as defined in the
  [specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/).
- `additions <639-spec-project-formats>`{.interpreted-text role="ref"}
  to the source distribution (sdist), built distribution (wheel) and
  installed project specifications.
- `guide for tools <639-spec-converting-metadata>`{.interpreted-text
  role="ref"} handling and converting legacy license metadata to license
  expressions, to ensure the results are consistent and correct.

Note that the guidance on errors and warnings is for tools\' default
behavior; they MAY operate more strictly if users explicitly configure
them to do so, such as by a CLI flag or a configuration option.

## SPDX license expression syntax {#639-spdx}

This PEP adopts the SPDX license expression syntax as documented in the
[SPDX
specification](https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/),
either Version 2.2 or a later compatible version.

A license expression can use the following
`license identifier`{.interpreted-text role="term"}s:

- Any SPDX-listed license short-form identifiers that are published in
  the [SPDX License List](https://spdx.org/licenses/), version 3.17 or
  any later compatible version. Note that the SPDX working group never
  removes any license identifiers; instead, they may choose to mark an
  identifier as \"deprecated\".
- The custom `LicenseRef-[idstring]` string(s), where `[idstring]` is a
  unique string containing letters, numbers, `.` and/or `-`, to identify
  licenses that are not included in the SPDX license list. The custom
  identifiers must follow the SPDX specification, [clause
  10.1](https://spdx.github.io/spdx-spec/v2.2.2/other-licensing-information-detected/)
  of the given specification version.

Examples of valid SPDX expressions:

``` none
MIT
BSD-3-Clause
MIT AND (Apache-2.0 OR BSD-2-Clause)
MIT OR GPL-2.0-or-later OR (FSFUL AND BSD-2-Clause)
GPL-3.0-only WITH Classpath-Exception-2.0 OR BSD-3-Clause
LicenseRef-Special-License OR CC0-1.0 OR Unlicense
LicenseRef-Proprietary
```

Examples of invalid SPDX expressions:

``` none
Use-it-after-midnight
Apache-2.0 OR 2-BSD-Clause
LicenseRef-License with spaces
LicenseRef-License_with_underscores
```

## Core Metadata {#639-spec-core-metadata}

The error and warning guidance in this section applies to build and
publishing tools; end-user-facing install tools MAY be less strict than
mentioned here when encountering malformed metadata that does not
conform to this specification.

As it adds new fields, this PEP updates the Core Metadata version to
2.4.

### Add `License-Expression` field {#639-spec-field-license-expression}

The `License-Expression` optional
`Core Metadata field`{.interpreted-text role="term"} is specified to
contain a text string that is a valid SPDX
`license expression`{.interpreted-text role="term"}, as
`defined above <639-spdx>`{.interpreted-text role="ref"}.

Build and publishing tools SHOULD check that the `License-Expression`
field contains a valid SPDX expression, including the validity of the
particular license identifiers (as
`defined above <639-spdx>`{.interpreted-text role="ref"}). Tools MAY
halt execution and raise an error when an invalid expression is found.
If tools choose to validate the SPDX expression, they also SHOULD store
a case-normalized version of the `License-Expression` field using the
reference case for each SPDX license identifier and uppercase for the
`AND`, `OR` and `WITH` keywords. Tools SHOULD report a warning and
publishing tools MAY raise an error if one or more license identifiers
have been marked as deprecated in the [SPDX License
List](https://spdx.org/licenses/).

For all newly-uploaded `distribution archive`{.interpreted-text
role="term"}s that include a `License-Expression` field, the [Python
Package Index (PyPI)](https://pypi.org/) MUST validate that they contain
a valid, case-normalized license expression with valid identifiers (as
`defined above <639-spdx>`{.interpreted-text role="ref"}) and MUST
reject uploads that do not. Custom license identifiers which conform to
the SPDX specification are considered valid. PyPI MAY reject an upload
for using a deprecated license identifier, so long as it was deprecated
as of the above-mentioned SPDX License List version.

### Add `License-File` field {#639-spec-field-license-file}

`License-File` is an optional `Core Metadata field`{.interpreted-text
role="term"}. Each instance contains the string representation of the
path of a license-related file. The path is located within the
`project source tree`{.interpreted-text role="term"}, relative to the
`project root directory`{.interpreted-text role="term"}. It is a
multi-use field that may appear zero or more times and each instance
lists the path to one such file. Files specified under this field could
include license text, author/attribution information, or other legal
notices that need to be distributed with the package.

As `specified by this PEP <639-spec-project-formats>`{.interpreted-text
role="ref"}, its value is also that file\'s path relative to the
`root license directory`{.interpreted-text role="term"} in both
`installed project`{.interpreted-text role="term"}s and the standardized
`Distribution Package`{.interpreted-text role="term"} types.

If a `License-File` is listed in a
`Source Distribution <Source Distribution (or "sdist")>`{.interpreted-text
role="term"} or `Built Distribution`{.interpreted-text role="term"}\'s
Core Metadata:

- That file MUST be included in the
  `distribution archive`{.interpreted-text role="term"} at the specified
  path relative to the root license directory.
- That file MUST be installed with the `project`{.interpreted-text
  role="term"} at that same relative path.
- The specified relative path MUST be consistent between project source
  trees, source distributions (sdists), built distributions
  (`Wheel`{.interpreted-text role="term"}s) and installed projects.
- Inside the root license directory, packaging tools MUST reproduce the
  directory structure under which the source license files are located
  relative to the project root.
- Path delimiters MUST be the forward slash character (`/`), and parent
  directory indicators (`..`) MUST NOT be used.
- License file content MUST be UTF-8 encoded text.

Build tools MAY and publishing tools SHOULD produce an informative
warning if a built distribution\'s metadata contains no `License-File`
entries, and publishing tools MAY but build tools MUST NOT raise an
error.

For all newly-uploaded `distribution archive`{.interpreted-text
role="term"}s that include one or more `License-File` fields in their
Core Metadata and declare a `Metadata-Version` of `2.4` or higher, PyPI
SHOULD validate that all specified files are present in that
`distribution archive`{.interpreted-text role="term"}s, and MUST reject
uploads that do not validate.

### Deprecate `License` field {#639-spec-field-license}

The legacy unstructured-text `License`
`Core Metadata field`{.interpreted-text role="term"} is deprecated and
replaced by the new `License-Expression` field. The fields are mutually
exclusive. Tools which generate Core Metadata MUST NOT create both these
fields. Tools which read Core Metadata, when dealing with both these
fields present at the same time, MUST read the value of
`License-Expression` and MUST disregard the value of the `License`
field.

If only the `License` field is present, tools MAY issue a warning
informing users it is deprecated and recommending `License-Expression`
instead.

For all newly-uploaded `distribution archive`{.interpreted-text
role="term"}s that include a `License-Expression` field, the [Python
Package Index (PyPI)](https://pypi.org/) MUST reject any that specify
both `License` and `License-Expression` fields.

The `License` field may be removed from a new version of the
specification in a future PEP.

### Deprecate license classifiers {#639-spec-field-classifier}

Using `license classifier`{.interpreted-text role="term"}s in the
`Classifier` `Core Metadata field`{.interpreted-text role="term"}
([described in the Core Metadata
specification](https://packaging.python.org/en/latest/specifications/core-metadata/#classifier-multiple-use))
is deprecated and replaced by the more precise `License-Expression`
field.

If the `License-Expression` field is present, build tools MAY raise an
error if one or more license classifiers is included in a `Classifier`
field, and MUST NOT add such classifiers themselves.

Otherwise, if this field contains a license classifier, tools MAY issue
a warning informing users such classifiers are deprecated, and
recommending `License-Expression` instead. For compatibility with
existing publishing and installation processes, the presence of license
classifiers SHOULD NOT raise an error unless `License-Expression` is
also provided.

New license classifiers MUST NOT be [added to
PyPI](https://github.com/pypa/trove-classifiers); users needing them
SHOULD use the `License-Expression` field instead. License classifiers
may be removed from a new version of the specification in a future PEP.

## Project source metadata {#639-spec-source-metadata}

This PEP specifies changes to the project\'s source metadata under a
`[project]` table in the `pyproject.toml` file.

### Add string value to `license` key {#639-spec-key-license-text}

`license` key in the `[project]` table is defined to contain a top-level
string value. It is a valid SPDX license expression as
`defined in this PEP <639-spdx>`{.interpreted-text role="ref"}. Its
value maps to the `License-Expression` field in the core metadata.

Build tools SHOULD validate and perform case normalization of the
expression as described in the
`639-spec-field-license-expression`{.interpreted-text role="ref"}
section, outputting an error or warning as specified.

Examples:

``` toml
[project]
license = "MIT"

[project]
license = "MIT AND (Apache-2.0 OR BSD-2-clause)"

[project]
license = "MIT OR GPL-2.0-or-later OR (FSFUL AND BSD-2-Clause)"

[project]
license = "LicenseRef-Proprietary"
```

### Add `license-files` key {#639-spec-key-license-files}

A new `license-files` key is added to the `[project]` table for
specifying paths in the project source tree relative to `pyproject.toml`
to file(s) containing licenses and other legal notices to be distributed
with the package. It corresponds to the `License-File` fields in the
Core Metadata.

Its value is an array of strings which MUST contain valid glob patterns,
as specified below:

- Alphanumeric characters, underscores (`_`), hyphens (`-`) and dots
  (`.`) MUST be matched verbatim.
- Special glob characters: `*`, `?`, `**` and character ranges: `[]`
  containing only the verbatim matched characters MUST be supported.
  Within `[...]`, the hyphen indicates a locale-agnostic range (e.g.
  `a-z`, order based on Unicode code points). Hyphens at the start or
  end are matched literally.
- Path delimiters MUST be the forward slash character (`/`). Patterns
  are relative to the directory containing `pyproject.toml`, therefore
  the leading slash character MUST NOT be used.
- Parent directory indicators (`..`) MUST NOT be used.

Any characters or character sequences not covered by this specification
are invalid. Projects MUST NOT use such values. Tools consuming this
field SHOULD reject invalid values with an error.

Tools MUST assume that license file content is valid UTF-8 encoded text,
and SHOULD validate this and raise an error if it is not.

Literal paths (e.g. `LICENSE`) are treated as valid globs which means
they can also be defined.

Build tools:

- MUST treat each value as a glob pattern, and MUST raise an error if
  the pattern contains invalid glob syntax.
- MUST include all files matched by a listed pattern in all distribution
  archives.
- MUST list each matched file path under a `License-File` field in the
  Core Metadata.
- MUST raise an error if any individual user-specified pattern does not
  match at least one file.

If the `license-files` key is present and is set to a value of an empty
array, then tools MUST NOT include any license files and MUST NOT raise
an error.

Examples of valid license files declaration:

``` toml
[project]
license-files = ["LICEN[CS]E*", "AUTHORS*"]

[project]
license-files = ["licenses/LICENSE.MIT", "licenses/LICENSE.CC0"]

[project]
license-files = ["LICENSE.txt", "licenses/*"]

[project]
license-files = []
```

Examples of invalid license files declaration:

``` toml
[project]
license-files = ["..\LICENSE.MIT"]
```

Reason: `..` must not be used. `\` is an invalid path delimiter, `/`
must be used.

``` toml
[project]
license-files = ["LICEN{CSE*"]
```

Reason: \"LICEN{CSE\*\" is not a valid glob.

### Deprecate `license` key table subkeys {#639-spec-key-license-table}

Table values for the `license` key in the `[project]` table, including
the `text` and `file` table subkeys, are now deprecated. If the new
`license-files` key is present, build tools MUST raise an error if the
`license` key is defined and has a value other than a single top-level
string.

If the new `license-files` key is not present and the `text` subkey is
present in a `license` table, tools SHOULD issue a warning informing
users it is deprecated and recommending a license expression as a
top-level string key instead.

Likewise, if the new `license-files` key is not present and the `file`
subkey is present in the `license` table, tools SHOULD issue a warning
informing users it is deprecated and recommending the `license-files`
key instead.

If the specified license `file` is present in the source tree, build
tools SHOULD use it to fill the `License-File` field in the core
metadata, and MUST include the specified file as if it were specified in
a `license-file` field. If the file does not exist at the specified
path, tools MUST raise an informative error as previously specified.

Table values for the `license` key MAY be removed from a new version of
the specification in a future PEP.

## License files in project formats {#639-spec-project-formats}

A few additions will be made to the existing specifications.

`Project source tree`{.interpreted-text role="term"}s

:   Per `639-spec-source-metadata`{.interpreted-text role="ref"}
    section, the [Declaring Project Metadata
    specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
    will be updated to reflect that license file paths MUST be relative
    to the project root directory; i.e. the directory containing the
    `pyproject.toml` (or equivalently, other legacy project
    configuration, e.g. `setup.py`, `setup.cfg`, etc).

`Source distributions (sdists) <Source Distribution (or "sdist")>`{.interpreted-text role="term"}

:   The [sdist
    specification](https://packaging.python.org/specifications/source-distribution-format/)
    will be updated to reflect that if the `Metadata-Version` is `2.4`
    or greater, the sdist MUST contain any license files specified by
    the
    `License-File field <639-spec-field-license-file>`{.interpreted-text
    role="ref"} in the `PKG-INFO` at their respective paths relative to
    the of the sdist (containing the `pyproject.toml` and the `PKG-INFO`
    Core Metadata).

`Built distribution`{.interpreted-text role="term"}s (`wheel`{.interpreted-text role="term"}s)

:   The [Wheel
    specification](https://packaging.python.org/specifications/binary-distribution-format/)
    will be updated to reflect that if the `Metadata-Version` is `2.4`
    or greater and one or more `License-File` fields is specified, the
    `.dist-info` directory MUST contain a `licenses` subdirectory, which
    MUST contain the files listed in the `License-File` fields in the
    `METADATA` file at their respective paths relative to the `licenses`
    directory.

`Installed project`{.interpreted-text role="term"}s

:   The [Recording Installed Projects
    specification](https://packaging.python.org/specifications/recording-installed-packages/)
    will be updated to reflect that if the `Metadata-Version` is `2.4`
    or greater and one or more `License-File` fields is specified, the
    `.dist-info` directory MUST contain a `licenses` subdirectory which
    MUST contain the files listed in the `License-File` fields in the
    `METADATA` file at their respective paths relative to the `licenses`
    directory, and that any files in this directory MUST be copied from
    wheels by install tools.

## Converting legacy metadata {#639-spec-converting-metadata}

Tools MUST NOT use the contents of the `license.text` `[project]` key
(or equivalent tool-specific format), license classifiers or the value
of the Core Metadata `License` field to fill the top-level string value
of the `license` key or the Core Metadata `License-Expression` field
without informing the user and requiring unambiguous, affirmative user
action to select and confirm the desired license expression value before
proceeding.

Tool authors, who need to automatically convert license classifiers to
SPDX identifiers, can use the
`recommendation <639-spec-mapping-classifiers-identifiers>`{.interpreted-text
role="ref"} prepared by the PEP authors.

# Backwards Compatibility {#639-backwards-compatibility}

Adding a new `License-Expression` Core Metadata field and a top-level
string value for the `license` key in the `pyproject.toml` `[project]`
table unambiguously means support for the specification in this PEP.
This avoids the risk of new tooling misinterpreting a license expression
as a free-form license description or vice versa.

The legacy deprecated Core Metadata `License` field, `license` key table
subkeys (`text` and `file`) in the `pyproject.toml` `[project]` table
and license classifiers retain backwards compatibility. A removal is
left to a future PEP and a new version of the Core Metadata
specification.

Specification of the new `License-File` Core Metadata field and adding
the files in the distribution is designed to be largely
backwards-compatible with the existing use of that field in many
packaging tools. The new `license-files` key in the `[project]` table of
`pyproject.toml` will only have an effect once users and tools adopt it.

This PEP specifies that license files should be placed in a dedicated
`licenses` subdir of `.dist-info` directory. This is new and ensures
that wheels following this PEP will have differently-located licenses
relative to those produced via the previous installer-specific behavior.
This is further supported by a new metadata version.

This also resolves current issues where license files are accidentally
replaced if they have the same names in different places, making wheels
undistributable without noticing. It also prevents conflicts with other
metadata files in the same directory.

The additions will be made to the source distribution (sdist), built
distribution (wheel) and installed project specifications. They document
behaviors allowed under their current specifications, and gate them
behind the new metadata version.

This PEP proposes PyPI implement validation of the new
`License-Expression` and `License-File` fields, which has no effect on
new and existing packages uploaded unless they explicitly opt in to
using these new fields and fail to follow the specification correctly.
Therefore, this does not have a backward compatibility impact, and
guarantees forward compatibility by ensuring all distributions uploaded
to PyPI with the new fields conform to the specification.

# Security Implications {#639-security-implications}

This PEP has no foreseen security implications: the `License-Expression`
field is a plain string and the `License-File` fields are file paths.
Neither introduces any known new security concerns.

# How to Teach This {#639-how-to-teach-this}

A majority of packages use a single license which makes the case simple:
a single license identifier is a valid license expression.

Users of packaging tools will learn the valid license expression of
their package through the messages issued by the tools when they detect
invalid ones, or when the deprecated `License` field or license
classifiers are used.

If an invalid `License-Expression` is used, the users will not be able
to publish their package to PyPI and an error message will help them
understand they need to use SPDX identifiers. It will be possible to
generate a distribution with incorrect license metadata, but not to
publish one on PyPI or any other index server that enforces
`License-Expression` validity. For authors using the now-deprecated
`License` field or license classifiers, packaging tools may warn them
and inform them of the replacement, `License-Expression`.

Tools may also help with the conversion and suggest a license expression
in many common cases:

- The appendix
  `639-spec-mapping-classifiers-identifiers`{.interpreted-text
  role="ref"} provides tool authors with recommendation on how to
  suggest a license expression produced from legacy classifiers.
- Tools may be able to suggest how to update an existing `License` value
  in project source metadata and convert that to a license expression,
  as also
  `specified in this PEP <639-spec-converting-metadata>`{.interpreted-text
  role="ref"}.

# Reference Implementation {#639-reference-implementation}

Tools will need to support parsing and validating license expressions in
the `License-Expression` field if they decide to implement this part of
the specification. It\'s up to the tools whether they prefer to
implement the validation on their side (e.g. like
[hatch](https://github.com/pypa/hatch/blob/hatchling-v1.24.2/backend/src/hatchling/licenses/parse.py#L8-L18))
or use one of the available Python libraries (e.g.
[license-expression](https://github.com/nexB/license-expression/)). This
PEP does not mandate using any specific library and leaves it to the
tools authors to choose the best implementation for their projects.

# Rejected Ideas {#639-rejected-ideas}

Many alternative ideas were proposed and after a careful consideration,
rejected. The exhaustive list including the rationale for rejecting can
be found in a
`separate page <639-rejected-ideas-details>`{.interpreted-text
role="ref"}.

# Appendices

A list of auxiliary documents is provided:

- Detailed `Licensing Examples <639-examples>`{.interpreted-text
  role="ref"},
- `User Scenarios <639-user-scenarios>`{.interpreted-text role="ref"},
- `License Documentation in Python and Other Projects <639-license-doc-python>`{.interpreted-text
  role="ref"},
- `Mapping License Classifiers to SPDX Identifiers <639-spec-mapping-classifiers-identifiers>`{.interpreted-text
  role="ref"},
- `Rejected Ideas <639-rejected-ideas-details>`{.interpreted-text
  role="ref"} in detail.

# References

# Acknowledgments

- Alyssa Coghlan
- Kevin P. Fleming
- Pradyun Gedam
- Oleg Grenrus
- Dustin Ingram
- Chris Jerdonek
- Cyril Roelandt
- Luis Villa
- Seth M. Larson
- Ofek Lev

# Copyright

This document is placed in the public domain or under the
[CC0-1.0-Universal
license](https://creativecommons.org/publicdomain/zero/1.0/), whichever
is more permissive.
