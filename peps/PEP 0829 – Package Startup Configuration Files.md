---
pep: 829
title: Package Startup Configuration Files
author:
- Barry Warsaw <barry@python.org>
discussions_to: https://discuss.python.org/t/pep-829-structured-startup-configuration-via-site-toml-files/106789
status: Draft
type: Standards Track
created: 31-Mar-2026
python_version: '3.15'
post_history:
- '`01-Apr-2026 <https://discuss.python.org/t/pep-829-structured-startup-configuration-files/106789>`__'
- '`13-Apr-2026 <https://discuss.python.org/t/pep-829-structured-startup-configuration-files/106789/69>`__'
- '`15-Apr-2026 <https://discuss.python.org/t/pep-829-structured-startup-configuration-files/106789/99>`__'
python_status: Draft
url: https://peps.python.org/pep-0829/
source_path: https://github.com/python/peps/blob/main/peps/pep-0829.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:10+00:00'
---

# Abstract

This PEP changes the way packages influence Python\'s startup process.
Previously controlled through legacy `.pth` files parsed and executed by
the `site.py` file during interpreter startup, such files are used to
extend `sys.path` and execute package initialization code before control
is passed to the first line of user code.

`.pth` files in their historical form have a [long
history](https://github.com/python/cpython/issues/78125) of proposed
removal, primarily because of the obtuse nature of the arbitrary code
execution feature. Recent [supply chain
attacks](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/)
have used arbitrary code execution in `.pth` files as an attack vector.

This PEP doesn\'t completely close this vector, but it does propose an
important and useful improvement, by narrowing the attack surface and
enabling a future policy mechanism for controlling which packages are
allowed or prevented from extending the path and executing start up
code. See `security`{.interpreted-text role="ref"} for additional
discussion.

# Motivation

Python\'s `.pth` files (processed by `Lib/site.py` at startup) support
two functions:

- **Extending** `sys.path` \-- Lines in this file (excluding comments
  and lines that start with `import`) name directories to be appended to
  `sys.path`. Relative paths are implicitly anchored at the
  site-packages directory.
- **Executing arbitrary code** \-- lines starting with `import` (or
  `import\\t`) are executed immediately by passing the source string to
  `exec()`.

While there are valid use cases for both, the `import` line feature is
the most problematic because:

- Code execution is a side effect of the implementation. Lines that
  start with `import` can be extended by separating multiple statements
  with a semicolon. As long as all the code to be executed appears on
  the same line, it all gets executed when the `.pth` file is processed.
- `import` lines are executed using `exec()` during interpreter startup,
  which opens a broad attack surface.
- There is no explicit concept of an entry point, which is an
  established pattern in Python packaging. Packages that require code
  execution and initialization at startup abuse `import` lines rather
  than explicitly declaring entry points.

# Specification

This PEP proposes the following:

- Keep the `<name>.pth` file format, but deprecate `import` line
  processing for three years, after which such lines will be disallowed.

- Keep the current `sys.path` extension feature of `<name>.pth` files
  unchanged. Specifically, absolute paths are used verbatim while
  relative paths are anchored at the directory in which the `.pth` file
  is located.

- A new file format called `<name>.start` is added which names entry
  points conforming to the \"colon-form\" of
  `pkgutil.resolve_name`{.interpreted-text role="func"} arguments.

- During the deprecation period, the presence of a `<name>.start` file
  matching a `<name>.pth` file disables the execution of `import` lines
  in the `<name>.pth` file in favor of entry points from the
  `<name>.start` file. This provides a migration path straddling Python
  versions which support this PEP and earlier versions which do not. In
  this case, warnings about `import` lines are *not* printed.

  During the deprecation period, for any `<name>.pth` file without a
  matching `<name>.start` file, the processing of the former is
  unchanged, although a warning about `import` lines is issued when `-v`
  (verbose) flag is given to Python.

  After the deprecation period `import` lines in `<name>.pth` files are
  ignored and a warning is issued, regardless of whether there is a
  matching `<name>.start` file or not.

  See the `teach`{.interpreted-text role="ref"} section for specific
  migration guidelines.

Both `<name>.pth` and `<name>.start` files are processed by the
`site.py` module, just like current `.pth` files. This means that
[disabling site.py
processing](https://docs.python.org/3/using/cmdline.html#cmdoption-S)
with `-S` disables processing of both files.

`site.py` start up code is divided into these explicit phases:

1.  Find the `<name>.pth` files (see `discovery`{.interpreted-text
    role="ref"} for additional details) and sort them in alphabetical
    order by filename.

2.  Parse the `<name>.pth` files in sorted order, keeping a global list
    of all path extensions, preserving order file-by-file and then by
    entry appearance. Duplicates are ignored.

3.  During the deprecation period, collect `import` lines found from
    `<name>.pth` files. Processing of these lines is deferred until
    after `<name>.start` file scanning.

4.  *Future extension:* apply a
    `global policy filter <future>`{.interpreted-text role="ref"} on the
    list of path extensions.

5.  Append path extensions to `sys.path` in the global preserved order.

6.  List all `<name>.start` files (see `discovery`{.interpreted-text
    role="ref"} for additional details) and sort them in alphabetical
    order by filename.

    For any `<name>.start` that matches a previously scanned
    `<name>.pth` file, discard all `import` lines from those matched
    `<name>.pth` files. See the `teach`{.interpreted-text role="ref"}
    section for more details and rationale.

7.  Parse the `<name>.start` files in sorted order, keeping a global
    list of all entry points, preserving order file-by-file and then by
    entry appearance. Duplicates are
    `not ignored <duplicate-eps>`{.interpreted-text role="ref"}.

8.  *Future extension:* apply a
    `global policy filter <future>`{.interpreted-text role="ref"} on the
    list of entry points.

9.  For each entry point in preserved order, use
    `pkgutil.resolve_name`{.interpreted-text role="func"} to resolve the
    entry point into a callable. Call the entry point with no arguments
    and any return value is discarded. The resolved object is not tested
    for callability before it is called (and thus any `TypeError` that
    might result is reported).

In both `<name>.pth` files and `<name>.start` files, comment lines (i.e.
lines beginning with `#` as the first non-whitespace character) and
blank lines are ignored. Any other parsing error causes the line to be
ignored.

## Entry point syntax {#ep-syntax}

`pkgutil.resolve_name`{.interpreted-text role="func"} is used to resolve
an entry point specification into a callable object. However, in Python
3.14 and earlier, this function accepts two forms, described in the
documentation with pseudo-regular expressions:

- `W(.W)*` - no colon form
- `W(.W)*:(W(.W)*)?` - colon form with optional callable suffix

This PEP proposes to only allow `pkg.mod:callable` form of entry points,
and requires that the callable be specified. See the `open issues
<open-issues>`{.interpreted-text role="ref"} for further discussion.

## File Naming and Discovery {#discovery}

- Packages may optionally install zero or more files of the format
  `<name>.pth` and `<name>.start`. The `<name>` prefix is arbitrary and
  need not match the package name or each other, although all else being
  equal, it is recommended that they do match the package name for
  clarity. The interpreter does not enforce any constraints on the
  prefix.
- Files are processed in alphabetical order.
- `<name>.start` files live in the same site-packages directories where
  `<name>.pth` files are found today. The `<name>.pth` location stays
  the same.
- The discovery rules for `<name>.start` files are the same as with
  `<name>.pth` files today. File names that start with a single `.`
  (e.g. `.start`) and files with OS-level hidden attributes
  (`UF_HIDDEN`, `FILE_ATTRIBUTE_HIDDEN`) are excluded.

## Error Handling

During parsing, errors are generally skipped and only reported when `-v`
(verbose) flag is given to Python. Unlike with `.pth` files currently,
processing does *not* abort for the entire file when an error is
encountered.

1.  If a `<name>.pth` or `<name>.start` file cannot be opened or read,
    it is skipped and processing continues to the next file.
2.  Invalid entry point specifications are skipped.

During execution, errors are printed to `sys.stderr` and processing
continues.

1.  Any `sys.path` extension directory pointing to an invalid or
    nonexistent path is ignored and processing continues to the next
    path entry.
2.  Exceptions during execution of the entry point are printed and
    processing continues to the next entry point.

## Encoding

`<name>.start` files **MUST** be encoded with
[utf-8-sig](https://docs.python.org/3.14/library/codecs.html#module-encodings.utf_8_sig),
i.e. UTF-8 with optional byte-order mark.

`<name>.pth` files **SHOULD** also be `utf-8-sig` encoded as well.
Currently, decoding `<name>.pth` files falls back to the current locale
if not encoded with `utf-8-sig`, but this PEP deprecates that support
for 5 years, after which `<name>.pth` files **MUST** be encoded with
`utf-8-sig` as well.

## Future Improvements {#future}

The introduction of 2-phase processing of `.pth` and `.start` files
gives us the ability to implement future improvements, where some global
site policy can be applied, providing finer grained control over both
`sys.path` extension and entry point execution. One could imagine that
after parsing, a policy could be applied to either allow or deny path
extensions or entry points based on a number of different criteria, such
as the `<name>` prefix used to specify the extension, the path
locations, or the modules in which the entry points are defined.

This PEP deliberately leaves the design of such a policy mechanism to a
future specification.

# Rationale

A previous iteration of this PEP proposed the use of a unified
`<name>.site.toml` file with tables to specify metadata, a list of path
extensions, and a list of entry points. While the PEP author and several
discussion participants liked this structured approach, a number of
detractors expressed the opinion that TOML files were overkill for this
proposal. The PEP author believes that the processing overhead of TOML
files was negligible and that the structured approach was useful for
readability and future extensibility. Detractors countered with YAGNI.

The two-file approach is a simple evolutionary improvement over the
previous `.pth` file process. The first improvement is the deprecation
and removal of arbitrary code execution through `exec()` of `import`
lines. Such lines are a wide attack vector that even the
`exec`{.interpreted-text role="func"} standard library documentation
strongly warns against. Replacing these lines with the narrower
invocation of entry point function inside modules indirectly reduces the
attack vector because functions inside modules are easier to audit, both
by humans and automatic vulnerability scanners.

The second improvement is splitting `sys.path` extension from entry
point specification into two files, special purposed for the exact use
case they support. There\'s no co-mingling of purposes, no possible
interleaving of effects, more readable file formats, and clear
processing rules. `sys.path` extensions are processed first, setting up
the ability to import modules, and then entry points are processed.
It\'s unambiguously clear which file format supports which use case.

The third improvement is the 2-phase approach to processing these files.
Parsing errors can be reported early and need not terminate the further
processing of lines in each file. The transition from processing to
execution for both `sys.path` extension and entry point invocation gives
us a chance (`in the future <future>`{.interpreted-text role="ref"}) to
design and implement global policies for explicitly controlling which
path extensions and entry points are allowed (and by implication, deemed
safe), without resorting to the heavy hammer of [disabling site.py
processing](https://docs.python.org/3/using/cmdline.html#cmdoption-S)
completely.

All valid `sys.path` extensions in all `<name>.pth` files found are
processed *before* any entry points in `<name>.start` files are called.
This is to ensure that all `sys.path` modifications required to import
entry point modules are applied first.

::: {#duplicate-eps}
Entry points are *not* de-duplicated, regardless of whether they\'re
defined multiple times in the same `<name>.start` file or across more
than one `<name>.start` file. This means that if an entry point appears
more than once it will get called more than once. Unlike with the
de-duplication of `sys.path` entries (where the appearance of a
directory path later on `sys.path` than its duplicate has no effect),
users could \-- however unlikely \-- actually want multiple invocations
of their entry points. This also avoids the complexity of defining
de-duplicating entry point semantics across independently-authored
`<name>.start` files.
:::

# Backwards Compatibility

This PEP proposes a 3 year deprecation period for processing of `import`
lines inside `.pth` files. `sys.path` extensions in `.pth` files remain
unchanged.

There should always be a simple migration strategy for any packages
which utilize the `import` line arbitrary code execution feature of
current `.pth` files. They can simply move the code into a callable
inside an importable module inside the package, and then name this
callable in an entry point specification inside a `<name>.start` file.

# Security Implications {#security}

This PEP improves the security posture of interpreter startup.

- The removal of arbitrary code execution by `exec`{.interpreted-text
  role="func"} with entry point execution, which is more constrained and
  auditable.
- Splitting `sys.path` extensioni from code execution into two separate
  files means that you can tell by listing the files in the site-dir,
  exactly where arbitrary code execution occurs.
- Python\'s import system is used to access and run the entry points, so
  the standard audit hooks (`578`{.interpreted-text role="pep"}) can
  provide monitoring.
- The two-phase processing model creates a natural hook where a `future
  <future>`{.interpreted-text role="ref"} policy mechanism could inspect
  and restrict what gets executed.
- The `package.module:callable` syntax limits execution to callables
  within importable modules.

The overall attack surface is not eliminated \-- a malicious package can
still cause arbitrary code execution via entry points, but the mechanism
proposed in this PEP is more structured, auditable, and amenable to
future policy controls.

# How to Teach This {#teach}

The `site`{.interpreted-text role="mod"} module documentation will be
updated to describe the operation and best practices for `<name>.pth`
and `<name>.start` files. The following migration guidelines for package
authors will be included:

- If your package currently ships a `<name>.pth` file, analyze whether
  you are using it for `sys.path` extension or start up code execution.
  You can keep all the `sys.path` extension lines unchanged.

- If you are using the code execution of `import` lines feature, create
  a callable (taking zero arguments) within an importable module inside
  your package. Name these as `pkg.mod:callable` entry points in a
  matching `<name>.start` file.

- If your package has to straddle older Pythons that don\'t support this
  PEP and newer Pythons that do, change the `import` lines in your
  `<name>.pth` to use the following form:

  `import pkg.mod; pkg.mod.callable()`

  This way, older Pythons will execute these `import` lines, and newer
  Pythons will ignore them, using the `<name>.start` file instead. In
  both cases the same code is effectively used, so while there\'s *some*
  duplication, it is minimal.

- After your straddling period, remove all `import` lines from your
  `<name>.pth` file.

Non-normatively, build tools may want to emit a warning if a package
includes both a `<name>.pth` file and a `<name>.start` file where the
former includes `import` lines that don\'t match lines in the latter.

# Reference Implementation

The [reference
implementation](https://github.com/python/cpython/pull/147955) supports
the current version of this PEP.

# Rejected Ideas

Just add entry points to `.pth` files and leave the `import` lines alone

:   This is rejected on the basis of conflation of intent and the
    migration path `described above <teach>`{.interpreted-text
    role="ref"}. The principle of separation of concerns means that
    it\'s easy to understand which use case a package is utilizing.

`<name>.site.toml` files

:   This was the unified new file format proposed in a previous draft of
    this PEP. It was generally felt that the structured format of the
    TOML file was overkill, and the overhead of parsing a TOML file
    wasn\'t worth the future extensibility benefit.

Single configuration file instead of per-package files

:   A single site-wide configuration file was considered but rejected
    because it would require coordination between independently
    installed packages and would not mirror the `<package>.pth`
    convention that tools already understand.

Priority or weight field for processing order

:   Since packages are installed independently, there is no arbiter of
    priority. Alphabetical ordering matches current `<name>.pth`
    processing order. Priority could be addressed by a future site-wide
    policy configuration file, not per-package metadata.

Passing arguments to callables

:   Callables are invoked with no arguments for simplicity and because
    there are no obviously useful arguments to pass to the entry point.

# Open Issues

- As described in the `entry point syntax <ep-syntax>`{.interpreted-text
  role="ref"} section, this PEP proposes to use a narrow definition of
  the acceptable object reference syntax implemented by
  `pkgutil.resolve_name`{.interpreted-text role="func"}, i.e.
  specifically requiring the `pkg.mod:callable` syntax. This is because
  we don\'t want to encourage code execution by direct import
  side-effect (i.e. functionality at module scope level).

  Assuming this restriction is acceptable, how this is implemented is an
  open question. `site.py` could enforce it directly, but then that sort
  of defeats the purpose of using
  `pkgutil.resolve_name`{.interpreted-text role="func"}. The PEP
  author\'s preference would be to add an optional keyword-only argument
  to `pkgutil.resolve_name`{.interpreted-text role="func"}, i.e.
  `strict` defaulting to `False` for backward compatibility.
  `strict=True` would narrow the acceptable inputs to effectively
  `W(.W)*:(W(.W)*)`, namely, rejecting the older, non-colon form, and
  making the callable after the colon required.

- `site.addpackage()` is an undocumented function that processes a
  single `.pth` file. It is not listed in `site.__all__`, not covered in
  [Doc/library/site.rst](https://github.com/python/cpython/blob/main/Doc/library/site.rst),
  and has no stability guarantees. A GitHub code search found roughly
  half a dozen third-party projects calling it directly, mostly with the
  pattern `site.addpackage(dir, "apps.pth", set())` --- all of which can
  be replaced by `site.addsitedir(dir)`.

  During the work on the reference implementation, `addpackage()`
  becomes a thin wrapper around the new internal pipeline for processing
  `.pth` and `.start` files. Maintaining it as a separate functions adds
  complexity for no documented use case. This function should be
  deprecated, with the suggestion that users migrate to `addsitedir()`
  instead, a documented public API.

- The PEP currently recommends a three year deprecation period on the
  *processing* of `import` lines in `.pth` files. Packages can straddle
  without warnings because the presence of a matching `.start` file
  disables warnings for `import` lines in `.pth` files *during the
  deprecation period*. However, as currently written, warnings will be
  re-enabled at the end of the deprecation period, so at that point
  there isn\'t a way to straddle without warnings.

  The preferred solution is to simply hide all warnings for `import`
  lines in `.pth` files behind the `-v` (verbose) flag, either for a
  full 5 year period (keeping the 3 year *processing* deprecation
  timeline), or indefinitely.

- Should future `-X` options provide fine-grained control over error
  reporting or entry point execution?

- This PEP does not address the use of `._pth`
  [files](https://docs.python.org/3/library/sys_path_init.html#pth-files)
  because the purpose and behavior is completely different, despite the
  similar name.

# Change History

`19-Apr-2026`

- Added a description of the encoding requirements for `<name>.start`
  and `<name>.pth` files.
- Update the migration guidelines.

[15-Apr-2026](https://discuss.python.org/t/pep-829-structured-startup-configuration-files/106789/99)

- During the deprecation period, warnings about `import` lines in
  `<name>.pth` files with no matching `<name>.start` file are only
  issued when `-v` (verbose) is given.
- Clarify that `import` lines in `<name>.pth` files where there is a
  matching `<name>.start` file are ignored.
- Added some `open issues <open-issues>`{.interpreted-text role="ref"}
  around `site.addpackage()` deprecation, and extending the suppression
  of `import` line warnings in `.pth` files unless `-v` is given, for an
  additional two years.

[13-Apr-2026](https://discuss.python.org/t/pep-829-structured-startup-configuration-files/106789/69)

- Changed the PEP title.
- The PEP is no longer in the `Packaging` Topic.
- The PEP now proposes an evolution of the `<name>.pth` file format and
  the addition of the `<name>.start` file for entry point specification.
  The `<name>.site.toml` file from the previous version is removed.
- A three year deprecation of `import` lines in `.pth` files is
  proposed.

# Acknowledgments

The PEP author thanks Paul Moore for the constructive and pleasant
conversation leading to the compromise from the first draft of this
proposal to its current form. Thanks also go to Emma Smith and Brett
Cannon for their feedback and encouragement.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
