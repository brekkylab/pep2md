---
pep: 676
title: PEP Infrastructure Process
author:
- Adam Turner <adam@python.org>
sponsor: Mariatta <mariatta@python.org>
pep_delegate: Barry Warsaw <barry@python.org>
discussions_to: https://discuss.python.org/t/10774
status: Active
type: Process
created: 01-Nov-2021
post_history:
- 23-Sep-2021
- 30-Nov-2021
resolution: https://discuss.python.org/t/10774/99
python_status: Active
url: https://peps.python.org/pep-0676/
source_path: https://github.com/python/peps/blob/main/peps/pep-0676.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:43+00:00'
---

# Abstract

This PEP addresses the infrastructure around rendering PEP files from
[reStructuredText](https://docutils.sourceforge.io/rst.html) files to
HTML webpages. We aim to specify a self-contained and maintainable
solution for PEP readers, authors, and editors.

# Motivation

As of November 2021, Python Enhancement Proposals (PEPs) are rendered in
a multi-system, multi-stage process. A continuous integration (CI) task
runs a [docutils](https://docutils.sourceforge.io) script to render all
PEP files individually. The CI task then uploads a tar archive to a
server, where it is retrieved and rendered into the
[python.org](https://www.python.org) website periodically.

This places a constraint on the [python.org](https://www.python.org)
website to handle raw HTML uploads and handle PEP rendering, and makes
the appropriate place to raise issues unclear in some cases[^1].

This PEP provides a specification for self-contained rendering of PEPs.
This would:

- reduce the amount of distributed configuration for supporting PEPs
- enable quality-of-life improvements for those who read, write, and
  review PEPs
- solve a number of outstanding issues, and lay the path for
  improvements
- save volunteer maintainers\' time

We propose that PEPs are accessed through
[peps.python.org](https://peps.python.org/) at the top-level (for
example [peps.python.org/pep-0008](PEP 0008 – Style Guide for Python Code.md)),
and that all custom tooling to support rendering PEPs is hosted in the
[python/peps](https://github.com/python/peps) repository.

# Rationale

## Simplifying and Centralising Infrastructure

As of November 2021, to locally render a PEP file, a PEP author or
editor needs to create a full local instance of the
[python.org](https://www.python.org) website and run a number of
disparate scripts, following
[documentation](https://pythondotorg.readthedocs.io/pep_generation.html)
that lives outside of the [python/peps](https://github.com/python/peps)
repository.

By contrast, the proposed implementation provides a single
[Makefile](https://www.gnu.org/software/make/manual/make.html#Introduction)
and a Python script to render all PEP files, with options to target a
web-server or the local filesystem.

Using a single repository to host all tooling will clarify where to
raise issues, reducing volunteer time spent in triage.

Simplified and centralised tooling may also reduce the barrier to entry
to further improvements, as the scope of the PEP rendering
infrastructure is well defined.

## Quality-of-Life Improvements and Resolving Issues

There are several requests for additional features in reading PEPs, such
as:

- syntax highlighting[^2]
- use of `.. code-block::` directives[^3]
- support for SVG images[^4]
- typographic quotation marks[^5]
- additional footer information[^6]
- intersphinx functionality[^7]
- dark mode theme[^8]

These are \"easy wins\" from this proposal, and would serve to improve
the quality-of-life for consumers of PEPs (including reviewers and
writers).

For example, the current (as of November 2021) system runs periodically
on a schedule. This means that updates to PEPs cannot be circulated
immediately, reducing productivity. The reference implementation renders
and publishes all PEPs on every commit to the repository, solving the
issue by design.

The reference implementation fixes several issues[^9]. For example:

- list styles are currently not respected by
  [python.org](https://www.python.org)\'s stylesheets
- support for updating images in PEPs is challenging in
  [python.org](https://www.python.org)

Third-party providers such as [Read the Docs](https://readthedocs.org)
or [Netlify](https://www.netlify.com/) can enhance this experience with
features such as automatic rendering of pull requests.

# Specification

The proposed specification for rendering the PEP files to HTML is as per
the [reference implementation](#reference-implementation).

The rendered PEPs MUST be available at
[peps.python.org](https://peps.python.org/). These SHOULD be hosted as
static files, and MAY be behind a content delivery network (CDN).

A service to render previews of pull requests SHOULD be provided. This
service MAY be integrated with the hosting and deployment solution.

The following redirect rules MUST be created for the
[python.org](https://www.python.org) domain:

- `/peps/` -\> <https://peps.python.org/>
- `/dev/peps/` -\> <https://peps.python.org/>
- `/peps/(.*)\.html` -\> <https://peps.python.org/$1>
- `/dev/peps/(.*)` -\> <https://peps.python.org/$1>

The following nginx configuration would achieve this:

``` nginx
location ~ ^/dev/peps/?(.*)$ {
    return 308 https://peps.python.org/$1/;
}

location ~ ^/peps/(.*)\.html$ {
    return 308 https://peps.python.org/$1/;
}

location ^/(dev/)?peps(/.*)?$ {
    return 308 https://peps.python.org/;
}
```

Redirects MUST be implemented to preserve [URL
fragments](https://url.spec.whatwg.org/#concept-url-fragment) for
backward compatibility purposes.

# Backwards Compatibility

Due to server-side redirects to the new canonical URLs, links in
previously published materials referring to the old URL schemes will be
guaranteed to work. All PEPs will continue to render correctly, and a
custom stylesheet in the reference implementation improves presentation
for some elements (most notably code blocks and block quotes).
Therefore, this PEP presents no backwards compatibility issues.

# Security Implications

The main [python.org](https://www.python.org) website will no longer
process raw HTML uploads, closing a potential threat vector. PEP
rendering and deployment processes will use modern, well-maintained code
and secure automated platforms, further reducing the potential attack
surface. Therefore, we see no negative security impact.

# How to Teach This

The new canonical URLs will be publicised in the documentation. However,
this is mainly a backend infrastructure change, and there should be
minimal end-user impact. PEP 1 and PEP 12 will be updated as needed.

# Reference Implementation

The proposed implementation has been merged into the
[python/peps](https://github.com/python/peps) repository in a series of
pull requests[^10]. It uses the
[Sphinx](https://www.sphinx-doc.org/en/master/) documentation system
with a custom theme (supporting light and dark colour schemes) and
extensions.

This already automatically renders all PEPs on every commit, and
publishes them to
[python.github.io/peps](https://python.github.io/peps). The high level
documentation for the system covers [how to render PEPs
locally](https://python.github.io/peps/docs/build) and [the
implementation of the
system](https://python.github.io/peps/docs/rendering_system).

# Rejected Ideas

It would likely be possible to amend the current (as of November 2021)
rendering process to include a subset of the quality-of-life
improvements and issue mitigations mentioned above. However, we do not
believe that this would solve the distributed tooling issue.

It would be possible to use the output from the proposed rendering
system and import it into [python.org](https://www.python.org). We would
argue that this would be the worst of both worlds, as a great deal of
complexity is added whilst none is removed.

# Acknowledgements

- Hugo van Kemenade
- Pablo Galindo Salgado
- Éric Araujo
- Mariatta
- C.A.M. Gerlach

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: For example,
    [pythondotorg#1024](https://github.com/python/pythondotorg/issues/1204),
    [pythondotorg#1038](https://github.com/python/pythondotorg/issues/1038),
    [pythondotorg#1387](https://github.com/python/pythondotorg/issues/1387),
    [pythondotorg#1388](https://github.com/python/pythondotorg/issues/1388),
    [pythondotorg#1393](https://github.com/python/pythondotorg/issues/1393),
    [pythondotorg#1564](https://github.com/python/pythondotorg/issues/1564),
    [pythondotorg#1913](https://github.com/python/pythondotorg/issues/1913),

[^2]: Requested:
    [pythondotorg#1063](https://github.com/python/pythondotorg/pull/1063),
    [pythondotorg#1206](https://github.com/python/pythondotorg/issues/1206),
    [pythondotorg#1638](https://github.com/python/pythondotorg/pull/1638),
    [peps#159](https://github.com/python/peps/issues/159), [comment in
    peps#1571](https://github.com/python/peps/pull/1571#discussion_r478701944),
    [peps#1577](https://github.com/python/peps/pull/1577),

[^3]: Requested:
    [pythondotorg#1063](https://github.com/python/pythondotorg/pull/1063),
    [pythondotorg#1206](https://github.com/python/pythondotorg/issues/1206),
    [pythondotorg#1638](https://github.com/python/pythondotorg/pull/1638),
    [peps#159](https://github.com/python/peps/issues/159), [comment in
    peps#1571](https://github.com/python/peps/pull/1571#discussion_r478701944),
    [peps#1577](https://github.com/python/peps/pull/1577),

[^4]: Requested: [peps#701](https://github.com/python/peps/issues/701)

[^5]: Requested: [peps#165](https://github.com/python/peps/issues/165)

[^6]: Requested:
    [pythondotorg#1564](https://github.com/python/pythondotorg/issues/1564)

[^7]: Requested: [comment in
    peps#2](https://github.com/python/peps/issues/2#issuecomment-339195595)

[^8]: Requested: [in
    python-dev](https://mail.python.org/archives/list/python-dev@python.org/message/E7PK6TLVDJIYXVGFA6ZYPB24KLJASPUI/)

[^9]: As of November 2021, see
    [peps#1387](https://github.com/python/peps/issues/1387),
    [pythondotorg#824](https://github.com/python/pythondotorg/issues/824),
    [pythondotorg#1556](https://github.com/python/pythondotorg/pull/1556),

[^10]: Implementation PRs:
    [peps#1930](https://github.com/python/peps/pull/1930),
    [peps#1931](https://github.com/python/peps/pull/1931),
    [peps#1932](https://github.com/python/peps/pull/1932),
    [peps#1933](https://github.com/python/peps/pull/1933),
    [peps#1934](https://github.com/python/peps/pull/1934)
