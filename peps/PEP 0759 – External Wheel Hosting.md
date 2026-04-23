---
pep: 759
title: External Wheel Hosting
author:
- Barry Warsaw <barry@python.org>
- Emma Harper Smith <emma@python.org>
pep_delegate: Donald Stufft <donald@python.org>
discussions_to: https://discuss.python.org/t/pep-759-external-wheel-hosting/66458
status: Withdrawn
type: Standards Track
topic: Packaging
created: 01-Oct-2024
post_history:
- 10-Oct-2024
- 31-Jan-2025
resolution: '`31-Jan-2025 <https://discuss.python.org/t/pep-759-external-wheel-hosting/66458/48>`__'
python_status: Withdrawn
url: https://peps.python.org/pep-0759/
source_path: https://github.com/python/peps/blob/main/peps/pep-0759.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:47+00:00'
---

# Abstract

This PEP proposes a mechanism by which projects hosted on
[pypi.org](https://pypi.org) can safely host wheel artifacts on external
sites other than PyPI. This PEP explicitly does *not* propose external
hosting of projects, packages, or their metadata. That functionality is
already available by externally hosting independent package indexes.
Because this PEP only provides a mechanism for projects to customize the
download URL for specific released wheel artifacts, dependency
resolution as already implemented by common installer tools such as
[pip](https://pip.pypa.io/en/stable/) and
[uv](https://docs.astral.sh/uv/) does not need to change.

This PEP defines what it means to be \"safe\" in this context, along
with a new package upload file format called a `.rim` file. It defines
how `.rim` files affect the metadata returned for a package\'s
`Simple Repository API
<packaging:simple-repository-api>`{.interpreted-text role="ref"} in both
HTML and JSON formats, and how traditional wheels can easily be turned
into `.rim` files.

# PEP withdrawn

This PEP was withdrawn by the authors on 2025-01-31. Our reading of the
sentiment in the discussion thread is that, while the problems this PEP
attempts to solve are valid, most folks would prefer a different
approach. Specifically, our read is that most users would prefer more
control over the ability to specify multiple indexes, how those indexes
interoperate, and the priority and trust assertions for those indexes.
For example, solutions such as `766`{.interpreted-text role="pep"} may
provide a better way forward. Existing stop gap measures (e.g. PyPI
limit increase requests and the
[\"wheel-stub\"](https://pypi.org/project/wheel-stub/) approach) are
sufficient \-- if not ideal \-- in the meantime. The authors wish to
thank everyone who contributed to the constructive discussion, and
especially those who showed their support for this PEP, both in public
and private.

# Rationale

The Python Package Index, hosted at <https://pypi.org>, imposes [default
limits](https://pypi.org/help/) on upload artifact file size (100 MiB)
and total project size (10 GiB). Most projects can comfortably fit
within these limits during the lifetime of the project, through years of
uploads. A few projects have encountered these limits, and have been
granted both file size and project size exceptions, allowing them to
continue uploading new releases without having to take more drastic
measures, such as removing files which may potentially still be in use
by consumers (e.g. through version pins).

A related workaround is the [\"wheel
stub\"](https://github.com/wheel-next/wheel-stub) approach, which
provides an indirect link between PyPI and an external third party
package index, where such limitations can be avoided. Wheel stubs are
`source distributions
<packaging:source-distribution-format>`{.interpreted-text role="ref"}
(a.k.a. \"sdists\") which utilize a `517`{.interpreted-text role="pep"}
build backend that, instead of turning source code into a binary wheel,
performs some logic to calculate the URL for an existing, externally
hosted wheel to download and install. This approach works, but it
obscures the connection between PyPI, the sdist, and the externally
hosted wheel, since there is no way to present this information to `pip`
or other such tools.

## Historical context

In 2013, `438`{.interpreted-text role="pep"} proposed a
\"backward-compatible two-phase transition process\" to modify several
aspects of release file hosting on PyPI. As this PEP describes, PyPI
originally supported only project and release *registration* without
also allowing for artifact file hosting. As such, most projects hosted
release file artifacts elsewhere. Artifact hosting was later added, but
the mix of externally and PyPI-hosted files led to a wide range of
usability and potential security-related problems. PEP 438 was an
attempt to provide several facilities to allow external hosting while
promoting a PyPI-first hosting preference.

PEP 438 was complex, with three different \"hosting modes\", `rel`
metadata in the simple HTML index pages to signify hosting locations,
and a two-phase transition plan affecting PyPI and installer tools. PEP
438 was ultimately retracted in 2015 by `470`{.interpreted-text
role="pep"}, which acknowledges that PEP 438 did succeed in\...

> bringing about more people to utilize PyPI\'s repository features, an
> altogether good thing given the global CDN powering PyPI providing
> speed ups for a lot of people\[\...\]

Instead of external hosting, PEP 470 promoted the use of explicit
multiple repositories, providing full package indexing and artifact
hosting, and enabled through installer tool support, such as
`pip install --extra-index-url` allowing `pip` to essentially treat
multiple repositories as [one single global
repository](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-extra-index-url)
for package installation resolution. Because this has been the blessed
norm for so many years, all Python package installation tools support
querying multiple indexes for dependency resolution.

## The problem with multiple indexes

Why then does this PEP propose to allow a more limited form of external
hosting, and how does this proposal avoid the problems documented in PEP
470?

One well-known problem that consolidating multiple indexes enables is
[dependency confusion
attacks](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610),
to which Python *can* be particularly vulnerable, due to the algorithm
that `pip install` uses for resolving package dependencies and preferred
versions. The `uv` tool addresses this by supporting an additional
[index
strategy](https://docs.astral.sh/uv/reference/settings/#index-strategy)
option, whereby users can select between, e.g. a `pip`-compatible
strategy, and a more limited strategy that prevents such dependency
confusion attacks.

`708`{.interpreted-text role="pep"} provides additional background about
dependency confusion attacks, and takes a different approach to
preventing them. At its core, PEP 708 allows repository owners to
indicate that projects track across different repositories, which allows
installers to determine how to treat the global package namespace when
combined across multiple repositories. PEP 708 has been provisionally
accepted, pending several required conditions as outlined in PEP 708,
some of which may have an indeterminate future. As PEP 708 itself says,
this won\'t by itself solve dependency confusion attacks, but is one way
to provide enough information to installers to help minimize these
attacks.

While there can still be valid use cases for standing up a totally
independent package index (such as providing richer platform support for
GPUs until a fully formed [variant
proposal](https://discuss.python.org/t/selecting-variant-wheels-according-to-a-semi-static-specification/53446)
is accepted), this PEP takes a different, simpler approach and doesn\'t
replace any of the existing, proposed, or approved package index
cooperation specifications.

This PEP also preserves the core purpose of PyPI, and allows it to
remain the traditional, canonical, centralized index of all Python
packages.

## Addressing PyPI limits

This proposal also addresses the problem of size limits imposed by PyPI,
where there is a [default artifact size
limit](https://pypi.org/help/#file-size-limit) of 100 MiB and a default
overall [project size limit](https://pypi.org/help/#project-size-limit)
of 10 GiB. Most packages and artifacts can easily fit in these limits,
even for packages containing binary extension modules for a variety of
platforms. A small, but important class of packages routinely exceed
these limits, requiring them to submit PyPI [exception request support
tickets](https://github.com/pypi/support/issues?q=is%3Aissue+is%3Aclosed+file+limit+request).
It\'s not necessarily difficult to get resolution on such exceptions,
but it is a special process that can take some time to resolve, and the
criteria for granting such exceptions aren\'t well documented.

## Reducing operational complexity

Setting up and maintaining an entire package index can be a complex
operational solution, both time and resource intensive. This is
especially true if the main purpose of such an index is just to avoid
file size limitations. The external index approach also imposes a tricky
UX on consumers of projects on the external index, requiring them to
understand how CLI options such as `--external-index-url` work, along
with the security implications of such flags. It would be much easier
for both producers and consumers of large wheel packages to just set up
and maintain a simple web server, capable of serving individual files
with no more complex API than `HTTP GET`. Such an interface is also
easily cacheable or placed behind a
[CDN](https://en.wikipedia.org/wiki/Content_delivery_network). Simple
HTTP servers are also much easier to audit for security purposes, easier
to proxy, and usually take much less resources to run, support, and
maintain. Even something like [Amazon S3](https://aws.amazon.com/s3/)
could be used to host external wheels.

This PEP proposes an approach that favors such operational simplicity.

# Specification

A new type of uploadable file is defined, called a \"RIM\" (i.e.
`.rim`), or \"Remote Installable Metadata\" file. The name evokes the
image of a wheel with the tire removed, and emphasizes that `.rim` files
are easily derived from `.whl` files. The process of turning a `.whl`
into a `.rim` is `outlined below <dismounting>`{.interpreted-text
role="ref"}. The file name format exactly matches the
`wheel file naming format
<packaging:wheel-file-name-spec>`{.interpreted-text role="ref"}
specification, except that RIM files use the suffix `.rim`. This means
that all the tags used to discriminate `.whl` files also distinguish
between different `.rim` files, and thus can be used during dependency
resolution steps, exactly as `.whl` files are today. In this respect,
`.whl` and `.rim` files are interchangeable.

The content of a `.rim` file is *nearly* identical to `.whl` files,
however `.rim` files **MUST** contain only the `.dist-info` directory
from a wheel. No other top-level file or directory is allowed in the
`.rim` zip file. The `.dist-info` directory **MUST** contain a single
additional file in addition to those
[allowed](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#the-dist-info-directory)
in a `.whl` file\'s `.dist-info` directory: a file called
`EXTERNAL-HOSTING.json`.

::: {#file-format}
This is a JSON file contains containing the following keys:
:::

`version`

:   This is the file format version, which for this PEP **MUST** be
    `1.0`.

`owner`

:   This **MUST** name the PyPI organization owner of this externally
    hosted file, for reasons which will be described in
    `detail below <resiliency>`{.interpreted-text role="ref"}.

`uri`

:   This is a single URL naming the location of the physical `.whl` file
    hosted on an external site. This URL **MUST** use the `https`
    scheme.

`size`

:   This is an integer value describing the size in bytes of the
    physical `.whl` file on the remote host.

`hashes`

:   This is a dictionary of the format described in
    `694`{.interpreted-text role="pep"}, used to capture both the
    `694#upload-each-file`{.interpreted-text role="pep"} of the physical
    `.whl` file, with the same constraints as proposed in that PEP.
    Since these hashes are immutable once uploaded to PyPI, they serve
    as a critical validation that the externally hosted wheel hasn\'t
    been corrupted or compromised.

## Effects of the RIM file

The only effect of a `.rim` file is to change the download URL for the
wheel artifact in both the HTML and JSON interfaces in the [simple
repository
API](https://packaging.python.org/en/latest/specifications/simple-repository-api/#).
In the HTML page for a package release, the `href` attribute **MUST** be
the value of the `uri` key, including a `#<hashname>=<hashvalue>`
fragment. this hash fragment **MUST** be in exactly the same format as
described the `376`{.interpreted-text role="pep"} originated [signed
wheel file
format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#signed-wheel-files)
in the `.dist-info/RECORD` file. The exact same rules for selection of
hash algorithm and encoding is used here.

Similarly in the [JSON
response](https://packaging.python.org/en/latest/specifications/simple-repository-api/#json-based-simple-api-for-python-package-indexes)
the `url` key pointing to the download file must be the value of the
`uri <file-format>`{.interpreted-text role="ref"} key, and the `hashes`
dictionary **MUST** be included with values populated from the `hashes`
dictionary provided above.

In all other respects, a compliant package index should treat `.rim`
files the same as `.whl` files, with some other minor exceptions as
outlined below. For example, `.rim` files can be
[deleted](https://pypi.org/help/#deletion) and yanked
(`592`{.interpreted-text role="pep"}) just like any `.whl` file, with
the exact same semantics (i.e. deletions are permanent). When a `.rim`
is deleted, an index **MUST NOT** allow a matching `.whl` or `.rim` file
to be (re-)uploaded.

## Availability order

Externally hosted wheels **MUST** be available before the corresponding
`.rim` file is uploaded to PyPI, otherwise a publishing race condition
is introduced, although this requirement **MAY** be relaxed for `.rim`
files uploaded to a `694`{.interpreted-text role="pep"} staged release.

## Wheels can override RIMs

Indexes **MUST** reject `.rim` files if a matching `.whl` file already
exists with the exact same file name tags. However, indexes **MAY**
accept a `.whl` file if a matching `.rim` file exists, as long as that
`.rim` file hasn\'t been deleted or yanked. This allows uploaders to
replace an externally hosted wheel file with an index hosted wheel file,
but the converse is prohibited. Since the default is to host wheels on
the same package index that contains the package metadata, it is not
allowed to \"downgrade\" an existing wheel file once uploaded. When a
`.whl` replaces a `.rim`, the index **MUST** provide download URLs for
the package using its own hosted file service. When uploading the
overriding `.whl` file, the package index **MUST** validate the hash
from the existing `.rim` file, and these hashes must match or the
overriding upload **MUST** be rejected.

## PyPI API bump unnecessary

It\'s likely that the changes are backward compatible enough that a bump
in the [PyPI repository
version](https://packaging.python.org/en/latest/specifications/simple-repository-api/#versioning-pypi-s-simple-api)
is not necessary. Since `.rim` files are essentially changes only to the
upload API, package resolvers and package installers can continue to
function with the APIs they\'ve always supported.

# External hosting resiliency {#resiliency}

One of the key concerns leading to PEP 438\'s revocation in PEP 470 was
potential user confusion when an external index disappeared. From PEP
470:

> This confusion comes down to end users of projects not realizing if a
> project is hosted on PyPI or if it relies on an external service. This
> often manifests itself when the external service is down but PyPI is
> not. People will see that PyPI works, and other projects works, but
> this one specific one does not. They oftentimes do not realize who
> they need to contact in order to get this fixed or what their
> remediation steps are.

While the problem of external wheel hosting service going down is not
directly solved by this PEP, several safeguards are in place to greatly
reduce the potential burden on PyPI administrators.

This PEP thus proposes that:

- External wheel hosting is only allowed for packages which are owned by
  [organization accounts](https://docs.pypi.org/organization-accounts/).
  External hosting is an organization-wide setting.
- Organization accounts do not automatically gain the ability to
  externally host wheels; this feature MUST be explicitly enabled by
  PyPI admins at their discretion. Since this will not be a common
  request, we don\'t expect the overhead to be nearly as burdensome as
  `541`{.interpreted-text role="pep"} resolutions, account recovery
  requests, or even file/project size increase requests. External
  hosting requests would be handled in the same manner as those
  requests, i.e. via the [PyPI GitHub support
  tracker](https://github.com/pypi/support).
- Organization accounts requesting external wheel hosting **MUST**
  register their own support contact URI, be it a `mailto` URI for a
  contact email address, or the URL to the organization\'s support
  tracker. Such a contact URI is optional for organizations which do not
  avail themselves of external wheel file hosting.

Combined with the `EXTERNAL-HOSTING.json` file\'s `owner` key, this
allows for installer tools to unambiguously redirect any download errors
away from the PyPI support admins and squarely to the organization\'s
support admins.

While the exact mechanics of storing and retrieving this organization
support URL will be defined separately, for the sake of example, let\'s
say a package `foo` externally hosts wheel files on
`` `https://foo.example.com `` \<https://foo.example.com\>\`\_\_ and
that host becomes unreachable. When an installer tool tries to download
and install the package `foo` wheel, the download step will fail. The
installer would then be able to query PyPI to provide a useful error
message to the end user:

- The installer downloads the `.rim` file and reads the `owner` key from
  the `EXTERNAL-HOSTING.json` file inside the `.rim` zip file.

- The installer queries PyPI for the support URI for the organization
  owner of the externally hosted wheel.

- An informative error message would then be displayed, e.g.:

  > The externally hosted wheel file `foo-....whl` could not be
  > downloaded. Please contact <support@foo.example.com> for help. Do
  > not report this to the PyPI administrators.

# Dismounting wheels {#dismounting}

It is generally very easy to produce a `.rim` file from an existing
`.whl` file. This could be done efficiently by a `518`{.interpreted-text
role="pep"} build backend with an additional command line option, or a
separate tool which takes a `.whl` file as input and creates the
associated `.rim` file. To complete the analogy, the act of turning a
`.whl` into a `.rim` is called \"dismounting\". The steps such a tool
would take are:

- Accept as input the source `.whl` file, the organization owner of the
  package, and URL at which the `.whl` will be hosted, and the support
  URI to report download problems from. These could in fact be captured
  in the `pyproject.toml` file, but that specification is out of scope
  for this PEP.
- Unzip the `.whl` and create the `.rim` zip archive.
- Omit from the `.rim` file any path in the `.whl` that **isn\'t**
  rooted at the `.dist-info` directory.
- Calculate the hash of the source `.whl` file.
- Add the `EXTERNAL-HOSTING.json` file containing the JSON keys and
  values as described above, to the `.rim` archive.

# Changes to tools

Theoretically, installer tools shouldn\'t need any changes, since when
they have identified the wheel to download and install, they simply
consult the download URLs returned by PyPI\'s Simple API. In practice
though, tools such as `pip` and `uv` may have constrained lists of hosts
they will allow downloads from, such as PyPI\'s own `pythonhosted.org`
domain.

In this case, such tools will need to relax those constraints, but the
exact policy for this is left to the installer tools themselves. Any
number of approaches could be implemented, such as downloading the
`.rim` file and verifying the `EXTERNAL-HOSTING.json` metadata, or
simply trusting the external downloads for any wheel with a matching
checksum. They could also query PyPI for the project\'s organization
owner and support URI before trusting the download. They could warn the
user when externally hosted wheel files are encountered, and/or require
the use of a command line option to enable additional download hosts.
Any of these verification policies could be chosen in configuration
files.

Installer tools should also probably provide better error messages when
externally hosted wheels cannot be downloaded, e.g. because a host is
unreachable. As described above, such tools could query enough metadata
from PyPI to provide clear and distinct error messages pointing users to
the package\'s external hosting support email or issue tracker.

# Constraints for external hosting services

The following constraints lead to reliable and compatible external wheel
hosting services:

- External wheels **MUST** be served over HTTPS, with a certificate
  signed by [Mozilla\'s root certificate
  store](https://wiki.mozilla.org/CA). This ensures compatibility with
  [pip](https://pip.pypa.io/en/stable/topics/https-certificates/) and
  [uv](https://docs.astral.sh/uv/configuration/authentication/#custom-ca-certificates).
  At the time of this writing, `pip` 24.2 on Python 3.10 or newer uses
  the system certificate store in addition to the Mozilla store provided
  by the third party [certifi](https://pypi.org/project/certifi/) Python
  package. `uv` uses the Mozilla store provided by the
  [webpki-roots](https://github.com/rustls/webpki-roots) crate, but not
  the system store unless the `--native-tls` flag is given[^1]. *The
  PyPI administrators may modify this requirement in the future, but
  compatibility with popular installers will not be compromised.*
- External wheel hosts **SHOULD** use a content delivery network
  ([CDN](https://en.wikipedia.org/wiki/Content_delivery_network)), just
  as PyPI does.
- External wheel hosts **MUST** commit to a stable URL for all wheels
  they host.
- Externally hosted wheels **MUST NOT** be removed from an external
  wheel host unless the corresponding `.rim` file is deleted from PyPI
  first, and **MUST NOT** remove external wheels for yanked releases.
- External wheel hosts **MUST** support [HTTP range
  requests](https://http.dev/range-request).
- External wheel hosts **SHOULD** support the
  [HTTP/2](https://http.dev/2) protocol.

# Security

Several factors as described in this proposal should mitigate security
concerns with externally hosted wheels, such as:

- Wheel file checksums **MUST** be included in `.rim` files, and once
  uploaded cannot be changed. Since the checksum stored on PyPI is
  immutable and required, it is not possible to spoof an external wheel
  file, even if the owning organization lost control of their hosting
  domain.
- Externally hosted wheels **MUST** be served over HTTPS.
- In order to serve externally hosted wheels, organizations **MUST** be
  approved by the PyPI admins.

When users identify malware or vulnerabilities in PyPI-hosted projects,
they can now report this using the [malware reporting
facilities](https://pypi.org/security/) on PyPI, as also described in
this [blog
post](https://blog.pypi.org/posts/2024-03-06-malware-reporting-evolved/).
The same process can be used to report security issues in externally
hosted wheels, and the same remediation process should be used. In
addition, since organizations with external hosting enabled MUST provide
a support contact URI, that URI can be used in some cases to report the
security issue to the hosting organization. Such organization reporting
won\'t make sense for malware, but could indeed be a very useful way to
report security vulnerabilities in externally hosted wheels.

# Rejected ideas

Several ideas were considered and rejected.

- Requiring digital signatures on externally hosted wheel files, either
  in addition to or other than hashes. We deem this unnecessary since
  the checksum requirement should be enough to validate that the
  metadata on PyPI for a wheel exactly matches the downloaded wheel. The
  added complexity of key management outweighs any additional benefit
  such digital signatures might convey.
- Hash verification on `.rim` file uploads. PyPI *could* verify that the
  hash in the uploaded `.rim` file matches the externally hosted wheel
  before it accepts the upload, but this requires downloading the
  external wheel and performing the checksum, which also implies that
  the upload of the `.rim` file cannot be accepted until this external
  `.whl` file is downloaded and verified. This increases PyPI bandwidth
  and slows down the upload query, although `694`{.interpreted-text
  role="pep"} draft uploads could potentially mitigate these concerns.
  Still, the benefit is not likely worth the additional complexity.
- Periodic verification of the download URLs by the index. PyPI could
  try to periodically ensure that the external wheel host or the
  external `.whl` file itself is still available, e.g. via an
  `HTTP HEAD <9110#section-9.3.2>`{.interpreted-text role="rfc"}
  request. This is likely overkill and without also providing the
  file\'s checksum in the response[^2], may not provide much additional
  benefit.
- This PEP could allow for an organization to provide fallback download
  hosts, such that a secondary is available if the primary goes down. We
  believe that DNS-based replication is a much better, well-known
  technique, and probably much more resilient anyway.
- `.rim` file replacement. While it is allowed for `.whl` files to
  replace existing `.rim` files, as long as a) the `.rim` file hasn\'t
  been deleted or yanked, b) the checksums match, we do not allow
  replacing `.whl` files with `.rim` files, nor do we allow a `.rim`
  file to overwrite an existing `.rim` file. This latter could be a
  technique to change the hosting URL for an externally hosted `.whl`;
  however, we do not think this is a good idea. There are other ways to
  \"fix\" an external host URL as described above, and we do not want to
  encourage mass re-uploads of existing `.rim` files.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: The `uv --native-tls` flag
    [replaces](https://github.com/astral-sh/uv/blob/3ce34035c84804fdfb8b78cf11b9ba1b168d0f35/crates/uv-client/src/base_client.rs#L248)
    the `webpki-roots` store.

[^2]: There being no standard way to return the file\'s checksum in
    response to an `HTTP HEAD <9110#section-9.3.2>`{.interpreted-text
    role="rfc"} request.
