---
pep: 752
title: Implicit namespaces for package repositories
author:
- Ofek Lev <ofekmeister@gmail.com>
- Jarek Potiuk <potiuk@apache.org>
sponsor: Barry Warsaw <barry@python.org>
pep_delegate: Dustin Ingram <di@python.org>
discussions_to: https://discuss.python.org/t/63192
status: Draft
type: Standards Track
topic: Packaging
created: 13-Aug-2024
post_history:
- '`18-Aug-2024 <https://discuss.python.org/t/61227>`__'
- '`07-Sep-2024 <https://discuss.python.org/t/63192>`__'
python_status: Draft
url: https://peps.python.org/pep-0752/
source_path: https://github.com/python/peps/blob/main/peps/pep-0752.rst
source_commit: 2f33c5438f046fa8d33eeb9ac9e06594e57518c9
---

# Abstract

This PEP specifies a way for organizations to reserve package name
prefixes for future uploads.

> \"Namespaces are one honking great idea \-- let\'s do more of
> those!\" - `20`{.interpreted-text role="pep"}

# Motivation

The current ecosystem lacks a way for projects with many packages to
signal a verified pattern of ownership. Such projects fall into two
categories.

The first category is projects[^1] that want complete control over their
namespace. A few examples:

- Major cloud providers like Amazon, Google and Microsoft have a common
  prefix for each feature\'s corresponding package[^2]. For example,
  most of Google\'s packages are prefixed by `google-cloud-` e.g.
  `google-cloud-compute` for [using virtual
  machines](https://cloud.google.com/products/compute).
- [OpenTelemetry](https://opentelemetry.io) is an open standard for
  observability with [official
  packages](https://github.com/open-telemetry/opentelemetry-python) for
  the core APIs and SDK with [contrib
  packages](https://github.com/open-telemetry/opentelemetry-python-contrib)
  to collect data from various sources. All packages are prefixed by
  `opentelemetry-` with child prefixes in the form
  `opentelemetry-<component>-<name>-`. The contrib packages live in a
  central repository and they are the only ones with the ability to
  publish.
- [Apache Airflow](https://airflow.apache.org) is a platform to
  programmatically author, schedule and monitor workflows. It has
  providers, where each provider package is prefixed by
  `apache-airflow-providers-`.

The second category is projects[^3] that want to share their namespace
such that some packages are officially maintained and third-party
developers are encouraged to participate by publishing their own. Some
examples:

- [Project Jupyter](https://jupyter.org) is devoted to the development
  of tooling for sharing interactive documents. They support
  [extensions](https://jupyterlab.readthedocs.io/en/stable/user/extensions.html)
  which in most cases (and in all cases for officially maintained
  extensions) are prefixed by `jupyter-`.
- [Django](https://www.djangoproject.com) is one of the most widely used
  web frameworks in existence. They have the concept of [reusable
  apps](https://docs.djangoproject.com/en/5.1/intro/reusable-apps/),
  which are commonly installed via [third-party
  packages](https://djangopackages.org) that implement a subset of
  functionality to extend Django-based websites. These packages are by
  convention prefixed by `django-` or `dj-`.

Such projects are uniquely vulnerable to name-squatting attacks which
can ultimately result in [dependency
confusion](https://www.activestate.com/resources/quick-reads/dependency-confusion/).

For example, say a new product is released for which monitoring would be
valuable. It would be reasonable to assume that
[Datadog](https://www.datadoghq.com) would eventually support it as an
official integration. It takes a nontrivial amount of time to deliver
such an integration due to roadmap prioritization and the time required
for implementation. It would be impossible to reserve the name of every
potential package so in the interim an attacker may create a package
that appears legitimate which would execute malicious code at runtime.
Not only are users more likely to install such packages but doing so
taints the perception of the entire project.

Although `708`{.interpreted-text role="pep"} attempts to address this
attack vector, it is specifically about the case of multiple
repositories being considered during dependency resolution and does not
offer any protection to the aforementioned use cases.

Namespacing also would drastically reduce the incidence of
[typosquatting](https://en.wikipedia.org/wiki/Typosquatting) because
typos would have to be in the prefix itself which is
[normalized](#naming) and likely to be a short, well-known identifier
like `aws-`. In recent years, typosquatting has become a popular attack
vector [^4].

The [current
protection](https://github.com/pypi/warehouse/blob/8615326918a180eb2652753743eac8e74f96a90b/warehouse/migrations/versions/d18d443f89f0_ultranormalize_name_function.py#L29-L42)
against typosquatting used by PyPI is to normalize similar characters
but that is insufficient for these use cases.

Another problem that namespacing would solve is the issue of choosing
new names for packages following the agreed patterns of naming. Often
(this is the case for Apache Airflow for example), there are public
discussions that precede the decision to create a new package. The
decision is based on the agreed name and follow the pattern of the
existing packages. If more package names are considered during the
discussion, all the names have to be reserved via a PyPI interface
before the discussion is public, otherwise the names can be taken by
other users. This has happened in the past as explained in the
associated
[discussion](https://discuss.python.org/t/pep-752-implicit-namespaces-for-package-repositories/63192/80).

# Rationale

Other package ecosystems have generally solved this problem by taking
one of two approaches: either minimizing or maximizing backwards
compatibility.

- [NPM](https://www.npmjs.com) has the concept of [scoped
  packages](https://docs.npmjs.com/about-scopes) which were
  [introduced](https://blog.npmjs.org/post/116936804365/solving-npms-hard-problem-naming-packages)
  primarily to combat there being a dearth of available good package
  names (whether a real or perceived phenomenon). When a user or
  organization signs up they are given a scope that matches their name.
  For example, the
  [package](https://www.npmjs.com/package/@google-cloud/storage) for
  using Google Cloud Storage is `@google-cloud/storage` where
  `@google-cloud/` is the scope. Regular user accounts
  (non-organization) may publish
  [unscoped](https://docs.npmjs.com/package-scope-access-level-and-visibility)
  packages for public use. This approach has the lowest amount of
  backwards compatibility because every installer and tool has to be
  modified to account for scopes.
- [NuGet](https://www.nuget.org) has the concept of [package ID prefix
  reservation](https://learn.microsoft.com/en-us/nuget/nuget-org/id-prefix-reservation)
  which was
  [introduced](https://devblogs.microsoft.com/nuget/Package-identity-and-trust/)
  primarily to satisfy users wishing to know where a package came from.
  A package name prefix may be reserved for use by one or more owners.
  Every reserved package has a special indication [on its
  page](https://www.nuget.org/packages/Google.Cloud.Storage.V1) to
  communicate this. After reservation, any upload with a reserved prefix
  will fail if the user is not an owner of the prefix. Existing packages
  that have a prefix that is owned may continue to release as usual.
  This approach has the highest amount of backwards compatibility
  because only modifications to indices like PyPI are required and
  installers do not need to change.

This PEP specifies the NuGet approach of authorized reservation across a
flat namespace. Any solution that requires new package syntax must be
built atop the existing flat namespace and therefore implicit namespaces
acquired via a reservation mechanism would be a prerequisite to such
explicit namespaces.

Although existing packages matching a reserved namespace would be
untouched, preventing future unauthorized uploads and strategically
applying `541`{.interpreted-text role="pep"} takedown requests for
malicious cases would reduce risks to users to a negligible level.

# Terminology

The key words \"MUST\", \"MUST NOT\", \"REQUIRED\", \"SHALL\", \"SHALL
NOT\", \"SHOULD\", \"SHOULD NOT\", \"RECOMMENDED\", \"MAY\", and
\"OPTIONAL\" in this document are to be interpreted as described in
`2119`{.interpreted-text role="rfc"}.

Organization

:   [Organizations](#orgs) are entities that own projects and have
    various users associated with them.

Grant

:   A grant is a reservation of a namespace for a package repository.

Open Namespace

:   An [open](#open-namespaces) namespace allows for uploads from any
    project owner.

Restricted Namespace

:   A restricted namespace only allows uploads from an owner of the
    namespace.

Parent Namespace

:   A namespace\'s parent refers to the namespace without the trailing
    hyphenated component e.g. the parent of `foo-bar` is `foo`.

Child Namespace

:   A namespace\'s child refers to the namespace with additional
    trailing hyphenated components e.g. `foo-bar` is a valid child of
    `foo` as is `foo-bar-baz`.

# Specification

## Organizations {#orgs}

Any package repository that allows for the creation of projects (e.g.
non-mirrors) MAY offer the concept of organizations[^5]. Organizations
are entities that own projects and have various users associated with
them.

Organizations MAY reserve one or more namespaces. Such reservations
neither confer ownership nor grant special privileges to existing
projects.

## Naming

A namespace MUST be a
[valid](https://packaging.python.org/en/latest/specifications/name-normalization/#name-format)
project name and
[normalized](https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization)
internally e.g. `foo.bar` would become `foo-bar`.

## Semantics

A namespace grant bestows ownership over the following:

1.  A project matching the namespace itself such as the placeholder
    package [microsoft](https://pypi.org/project/microsoft/).
2.  Projects that start with the namespace followed by a hyphen. For
    example, the namespace `foo` would match the normalized project name
    `foo-bar` but not the project name `foobar`.

Package name matching acts upon the [normalized](#naming) namespace.

Namespaces are per-package repository and SHALL NOT be shared between
repositories. For example, if PyPI has a namespace `microsoft` that is
owned by the company Microsoft, packages starting with `microsoft-` that
come from other non-PyPI mirror repositories do not confer the same
level of trust.

Grants MUST NOT overlap. For example, if there is an existing grant for
`foo-bar` then a new grant for `foo` would be forbidden. An overlap is
determined by comparing the [normalized](#naming) proposed namespace
with the normalized namespace of every existing root grant. Every
comparison must append a hyphen to the end of the proposed and existing
namespace. An overlap is detected when any existing namespace starts
with the proposed namespace.

## Uploads

If the name of a package being uploaded matches a reserved namespace and
either of the following criteria are true:

- The project does not yet exist.
- The project is not owned by an organization with an active grant for
  the namespace.

Then the upload MUST fail with a 403 HTTP status code.

## Open Namespaces

The owner of a grant may choose to allow others the ability to release
new projects with the associated namespace. Doing so MUST allow
[uploads](##REF##uploads) for new projects matching the namespace from
any user.

It is possible for the owner of a namespace to both make it open and
allow other organizations to use the grant. In this case, the authorized
organizations have no special permissions and are equivalent to an open
grant without ownership.

## Hidden Grants

Repositories MAY create hidden grants that are not visible to the public
which prevent their namespaces from being claimed by others. Such grants
MUST NOT be [open](#open-namespaces) and SHOULD NOT be exposed in the
[API](#repository-metadata).

Hidden grants are useful for repositories that wish to enforce upload
restrictions without the need to expose the namespace to the public.

## Repository Metadata

The `JSON API <691>`{.interpreted-text role="pep"} version will be
incremented from `1.2` to `1.3`. The following API changes MUST be
implemented by repositories that support this PEP. Repositories that do
not support this PEP MUST NOT implement these changes so that consumers
of the API are able to determine whether the repository supports this
PEP.

### Project Detail

The `project detail <691#project-detail>`{.interpreted-text role="pep"}
response will be modified as follows.

The `namespace` key MUST be `null` if the project does not match an
active namespace grant. If the project does match a namespace grant, the
value MUST be a mapping with the following keys:

- `prefix`: This is the associated [normalized](#naming) namespace e.g.
  `foo-bar`. If the owner of the project owns multiple matching grants
  then this MUST be the namespace with the most number of characters.
  For example, if the project name matched both `foo-bar` and
  `foo-bar-baz` then this key would be the latter.
- `authorized`: This is a boolean and will be true if the project owner
  is an organization and is one of the current owners of the grant. This
  is useful for tools that wish to make a distinction between official
  and community packages.
- `open`: This is a boolean indicating whether the namespace is
  [open](#open-namespaces).

### Namespace Detail

The format of this URL is `/namespace/<namespace>` where `<namespace>`
is the [normalized](#naming) namespace. For example, the URL for the
namespace `foo.bar` would be `/namespace/foo-bar`.

The response will be a mapping with the following keys:

- `prefix`: This is the [normalized](#naming) version of the namespace
  e.g. `foo-bar`.
- `owner`: This is the organization that is responsible for the
  namespace.
- `open`: This is a boolean indicating whether the namespace is
  [open](#open-namespaces).
- `parent`: This is the parent namespace if it exists. For example, if
  the namespace is `foo-bar` and there is an active grant for `foo`,
  then this would be `"foo"`. If there is no parent then this key will
  be `null`.
- `children`: This is an array of any child namespaces. For example, if
  the namespace is `foo` and there are active grants for `foo-bar` and
  `foo-bar-baz` then this would be `["foo-bar", "foo-bar-baz"]`.

## Grant Removal

When a reserved namespace becomes unclaimed, repositories MUST set the
`namespace` key to `null` in the [API](#project-detail).

Namespaces that were previously claimed but are now not SHOULD be
eligible for claiming again by any organization.

# Community Buy-in

Representatives from the following organizations have expressed support
for this PEP (with a link to the discussion):

- [Apache
  Airflow](https://github.com/apache/airflow/discussions/41657#discussioncomment-10412999)
  ([expanded](https://discuss.python.org/t/63191/75))
- [pytest](https://discuss.python.org/t/63192/68)
- [Typeshed](https://discuss.python.org/t/1609/37)
- [Project Jupyter](https://discuss.python.org/t/61227/16)
  ([expanded](https://discuss.python.org/t/61227/48))
- [Microsoft](https://discuss.python.org/t/63191/40)
- [Sentry](https://discuss.python.org/t/63192/67) (in favor of the NuGet
  approach over others but not negatively impacted by the current lack
  of capability)
- [DataDog](https://discuss.python.org/t/63191/53)

# Backwards Compatibility

There are no intrinsic concerns because there is still a flat namespace
and installers need no modification. Additionally, many projects have
already chosen to signal a shared purpose with a prefix like [typeshed
has
done](https://github.com/python/typeshed/issues/2491#issuecomment-578456045).

# Security Implications

- There is an opportunity to build on top of `740`{.interpreted-text
  role="pep"} and `480`{.interpreted-text role="pep"} so that one could
  prove cryptographically that a specific release came from an owner of
  the associated namespace. This PEP makes no effort to describe how
  this will happen other than that work is planned for the future.

# How to Teach This

For consumers of packages we will document how metadata is exposed in
the [API](#repository-metadata) and potentially in future note tooling
that supports utilizing namespaces to provide extra security guarantees
during installation.

# Reference Implementation

A complete reference implementation of this PEP is available in [PR
#17691](https://github.com/pypi/warehouse/pull/17691).

# Rejected Ideas

## Granting Reservations to Users

As package repositories have a flat namespace, allowing any user to
reserve a namespace would be untenable not just because there would be
[contention for a finite
resource](https://en.wikipedia.org/wiki/Tragedy_of_the_commons), but
also because no repository has enough human operators to manage the
vetting of an arbitrary number of users.

## Artifact-level Namespace Association {#artifact-level-association}

An earlier version of this PEP proposed that metadata be associated with
individual artifacts at the point of release. This was rejected because
it had the potential to cause confusion for users who would expect the
namespace authorization guarantee to be at the project level based on
current grants rather than the time at which a given release occurred.

## Organization Scoping

The primary motivation for this PEP is to reduce dependency confusion
attacks and NPM-style scoping with an allowance of the legacy flat
namespace would increase the risk. If documentation instructed a user to
install `bar` in the namespace `foo` then the user must be careful to
install `@foo/bar` and not `foo-bar`, or vice versa. The Python
packaging ecosystem has normalization rules for names in order to
maximize the ease of communication and this would be a regression.

The runtime environment of Python is also not conducive to scoping.
Whereas multiple versions of the same JavaScript package may coexist,
Python only allows a single global namespace. Barring major changes to
the language itself, this is nearly impossible to change. Additionally,
users have come to expect that the package name is usually the same as
what they would import and eliminating the flat namespace would do away
with that convention.

Scoping would be particularly affected by organization changes which are
bound to happen over time. An organization may change their name due to
internal shuffling, an acquisition, or any other reason. Whenever this
happens every project they own would in effect be renamed which would
cause unnecessary confusion for users, frequently.

Finally, the disruption to the community would be massive because it
would require an update from every package manager, security scanner,
IDE, etc. New packages released with the scoping would be incompatible
with older tools and would cause confusion for users along with
frustration from maintainers having to triage such complaints.

## Encourage Dedicated Package Repositories {#dedicated-repositories}

Critically, this imposes a burden on projects to maintain their own
infra. This is an unrealistic expectation for the vast majority of
companies and a complete non-starter for community projects.

This does not help in most cases because the default behavior of most
package managers is to use PyPI so users attempting to perform a simple
`pip install` would already be vulnerable to malicious packages.

In this theoretical future every project must document how to add their
repository to dependency resolution, which would be different for each
package manager. Few package managers are able to download specific
dependencies from specific repositories and would require users to use
verbose configuration in the common case.

The ones that do not support this would instead find a given package
using an ordered enumeration of repositories, leading to dependency
confusion. For example, say a user wants two packages from two custom
repositories `X` and `Y`. If each repository has both packages but one
is malicious on `X` and the other is malicious on `Y` then the user
would be unable to satisfy their requirements without encountering a
malicious package.

## Exclusive Reliance on Provenance Assertions {#provenance-assertions}

The idea here[^6] would be to design a general purpose way for clients
to make provenance assertions to verify certain properties of
dependencies, each with custom syntax. Some examples:

- The package was uploaded by a specific organization or user name e.g.
  `pip install "azure-loganalytics from microsoft"`
- The package was uploaded by an owner of a specific domain name e.g.
  `pip install "google-cloud-compute from cloud.google.com"`
- The package was uploaded by a user with a specific email address e.g.
  `pip install "aws-cdk-lib from contact@amazon.com"`
- The package matching a namespace was uploaded by an authorized party
  (this PEP)

A fundamental downside is that it doesn\'t play well with multiple
repositories. For example, say a user wants the `azure-loganalytics`
package and wants to ensure it comes from the organization named
`microsoft`. If Microsoft\'s organization name on PyPI is `microsoft`
then a package manager that defaults to PyPI could accept
`azure-loganalytics from microsoft`. However, if multiple repositories
are used for dependency resolution then the user would have to specify
the repository as part of the definition which is unrealistic for
reasons outlined in the dedicated section on [asserting package owner
names](#asserting-package-owner-names).

Another general weakness with this approach is that a user attempting to
perform a simple `pip install` without special syntax, which is the most
common scenario, would already be vulnerable to malicious packages. In
order to overcome this there would have to be some default trust
mechanism, which in all cases would impose certain UX or resolver logic
upon every tool.

For example, package managers could be changed such that the first time
a package is installed the user would receive a confirmation prompt
displaying the provenance details. This would be very confusing and
noisy, especially for new users, and would be a breaking UX change for
existing users. Many methods of installation wouldn\'t work for this
scenario such as running in CI or installing from a requirements file
where the user would potentially be getting hundreds of prompts.

One solution to make this less disruptive for users would be to manually
maintain a list of trustworthy details (organization/user names, domain
names, email addresses, etc.). This could be discoverable by packages
providing [entry
points](https://packaging.python.org/en/latest/specifications/entry-points/)
which package managers could learn to detect and which corporate
environments could install by default. This has the major downside of
not providing automatic guarantees which would limit the usefulness for
the average user who is more likely to be affected.

There are two ideas that could be used to provide automatic protection,
which could be based on `740`{.interpreted-text role="pep"} attestations
or a new mechanism for utilizing third-party APIs that host the
metadata.

First, each repository could offer a service that verifies the owner of
a package using whatever criteria they deem appropriate. After
verification, the repository would add the details to a dedicated
package that would be installed by default.

This would require dedicated maintenance which is unrealistic for most
repositories, even PyPI currently. It\'s unclear how community projects
without the resources for something like a domain name would be
supported. Critically, this solution would cause extra confusion for
users in the case of multiple repositories as each might have their own
verification processes, attestation criteria and default package
containing the verified details. It would be challenging to get
community buy-in of every package manager to be aware of each
repositories\' chosen verification package and install that by default
before dependency resolution.

Should digital attestations become the chosen mechanism, a downside is
that implementing this in custom package repositories would require a
significant amount of work. In the case of PyPI, the prerequisite work
on [Trusted
Publishing](https://blog.pypi.org/posts/2023-04-20-introducing-trusted-publishers/#acknowledgements)
and then the [PEP 740
implementation](https://blog.trailofbits.com/2024/10/01/securing-the-software-supply-chain-with-the-slsa-framework/)
itself took the equivalent of a full-time engineer one year whose time
was paid for by a corporate sponsor. Other organizations are unlikely to
implement similar work because simpler mechanisms make it possible to
implement reproducible builds. When everything is internally managed,
attestations are also not very useful. Community projects are unlikely
to undertake this effort because they would likely lack the resources to
maintain the necessary infrastructure themselves and moreover there are
significant downsides to [encouraging dedicated package
repositories](#dedicated-repositories).

The other idea would be to host provenance assertions externally and
push more logic client-side. A possible implementation might be to
specify a provenance API that could be hosted at a designated relative
path like `/provenance`. Projects on each repository could then be
configured to point to a particular domain and this information would be
passed on to clients during installation.

While this distributed approach does impose less of an infrastructure
burden on repositories, it has the potential to be a security risk. If
an external provenance API is compromised, it could lead to malicious
packages being installed. If an external API is down, it could lead to
package installation failing or package managers might only emit
warnings in which case there is no security benefit.

Additionally, this disadvantages community projects that do not have the
resources to maintain such an API. They could use free hosting solutions
such as what many do for documentation but they do not technically own
the infrastructure and they would be compromised should the generous
offerings be restricted.

Finally, while both of these theoretical approaches are not yet
prescriptive, they imply assertions at the artifact level which was
already a [rejected idea](#artifact-level-association).

## Asserting Package Owner Names

This is about asserting that the package came from a specific
organization or user name. It\'s quite similar to the [organization
scoping](#organization-scoping) idea except that a flat namespace is the
base assumption.

This would require modifications to the
`JSON API <691>`{.interpreted-text role="pep"} of each supported
repository and could be implemented by exposing extra metadata or as
proper [provenance assertions](#provenance-assertions).

As with the organization scoping idea, a new
[syntax](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
would be required like `microsoft::azure-loganalytics` where `microsoft`
is the organization and `azure-loganalytics` is the package. Although
this plays well with the existing flat namespace in comparison, it
retains the critical downside of being a disruption for the community
with the number of changes required.

A unique downside is that names are an implementation detail of
repositories. On PyPI, the names of organizations are separate from user
names so there is potential for conflicts. In the case of multiple
repositories, users might run into cases of dependency confusion similar
to the one at the end of the [Encourage Dedicated Package
Repositories](#dedicated-repositories) rejected idea.

To ameliorate this, it was suggested that the syntax be expanded to also
include the expected repository URL like
`microsoft@pypi.org::azure-loganalytics`. This syntax or something like
it is so verbose that it could lead to user confusion, and even worse,
frustration should it gain increased adoption among those able to
maintain dedicated infrastructure (community projects would not
benefit).

The expanded syntax is an attempt to standardize resolver behavior and
configuration within dependency specifiers. Not only would this be
mandating the UX of tools, it lacks precedent in package managers for
language ecosystems with or without the concept of package repositories.
In such cases, the resolver configuration is separate from the
dependency definition.

  Language   Tool       Resolution behavior
  ---------- ---------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Rust       Cargo      Dependency resolution can be [modified](https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html) within `Cargo.toml` using the the `[patch]` table.
  JS         Yarn       Although they have the concept of [protocols](https://yarnpkg.com/protocols) (which are similar to the URL schemes of our [direct references](https://packaging.python.org/en/latest/specifications/version-specifiers/#direct-references)), users configure the [resolutions](https://yarnpkg.com/configuration/manifest#resolutions) field in the `package.json` file.
  JS         npm        Users can configure the [overrides](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#overrides) field in the `package.json` file.
  Ruby       Bundler    The `Gemfile` allows for specifying an [explicit source](https://bundler.io/v2.5/man/gemfile.5.html#SOURCE-PRIORITY) for a gem.
  C#         NuGet      It\'s possible to [override package versions](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management#overriding-package-versions) by configuring the `Directory.Packages.props` file.
  PHP        Composer   The `composer.json` file allows for specifying [repository](https://getcomposer.org/doc/articles/repository-priorities.md#filtering-packages) sources for specific packages.
  Go         go         The `go.mod` file allows for specifying a [replace](https://go.dev/ref/mod#go-mod-file-replace) directive. Note that this is used for direct dependencies as well as transitive dependencies.

## Use Fixed Prefixes

The idea here would be to have one or more top-level fixed prefixes that
are used for namespace reservations:

- `com-`: Reserved for corporate organizations.
- `org-`: Reserved for community organizations.

Organizations would then apply for a namespace prefixed by the type of
their organization.

This would cause perpetual disruption because when projects begin it is
unknown whether a user base will be large enough to warrant a namespace
reservation. Whenever that happens the project would have to be renamed
which would put a high maintenance burden on the project maintainers and
would cause confusion for users who have to learn a new way to reference
the project\'s packages. The potential for this deterring projects from
reserving namespaces at all is high.

Another issue with this approach is that projects often have branding in
mind
([example](https://github.com/apache/airflow/discussions/41657#discussioncomment-10417439))
and would be reluctant to change their package names.

It\'s unrealistic to expect every company and project to voluntarily
change their existing and future package names.

## Use DNS

The [idea](https://discuss.python.org/t/63455) here is to add a new
metadata field to projects in the API called `domain-authority`.
Repositories would support a new endpoint for verifying the domain via
HTTPS. Clients would then support options to allow certain domains.

This does not solve the problem for the target audience who do not check
where their packages are coming from and is more about checking for the
integrity of uploads which is already supported in a more secure way by
`740`{.interpreted-text role="pep"}.

Most projects do not have a domain and could not benefit from this,
unfairly favoring organizations that have the financial means to acquire
one.

# Open Issues

None at this time.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: Additional examples of projects with restricted namespaces:

    - [Typeshed](https://github.com/python/typeshed) is a community
      effort to maintain type stubs for various packages. The stub
      packages they maintain mirror the package name they target and are
      prefixed by `types-`. For example, the package `requests` has a
      stub that users would depend on called `types-requests`.
      Unofficial stubs are not supposed to use the `types-` prefix and
      are expected to use a `-stubs` suffix instead.
    - [Sphinx](https://www.sphinx-doc.org) is a documentation framework
      popular for large technical projects such as
      [Swift](https://www.swift.org) and Python itself. They have the
      concept of [extensions](##REF##_) which are prefixed by
      `sphinxcontrib-`, many of which are maintained within a [dedicated
      organization](https://github.com/sphinx-contrib).
    - [Apache Airflow](https://airflow.apache.org) is a platform to
      programmatically orchestrate tasks as directed acyclic graphs
      (DAGs). They have the concept of [plugins](##REF##_), and also
      [providers](##REF##_) which are prefixed by
      `apache-airflow-providers-`.

[^2]: The following shows the package prefixes for the major cloud
    providers:

    - Amazon: [aws-cdk-](https://docs.aws.amazon.com/cdk/api/v2/python/)
    - Google:
      [google-cloud-](https://github.com/googleapis/google-cloud-python/tree/main/packages)
      and others based on `google-`
    - Microsoft:
      [azure-](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk)

[^3]: Additional examples of projects with open namespaces:

    - [pytest](https://docs.pytest.org) is Python\'s most popular
      testing framework. They have the concept of [plugins](##REF##_)
      which may be developed by anyone and by convention are prefixed by
      `pytest-`.
    - [MkDocs](https://www.mkdocs.org) is a documentation framework
      based on Markdown files. They also have the concept of
      [plugins](https://www.mkdocs.org/dev-guide/plugins/) which may be
      developed by anyone and are usually prefixed by `mkdocs-`.
    - [Datadog](https://www.datadoghq.com) offers observability as a
      service. The [Datadog Agent](https://docs.datadoghq.com/agent/)
      ships out-of-the-box with [official
      integrations](https://github.com/DataDog/integrations-core) for
      many products, like various databases and web servers, which are
      distributed as Python packages that are prefixed by `datadog-`.
      There is support for creating [third-party integrations](##REF##_)
      which customers may run.

[^4]: Examples of typosquatting attacks targeting Python users:

    - `django-` namespace was squatted, among other packages, leading to
      a
      [postmortem](https://mail.python.org/pipermail/security-announce/2017-September/000000.html)
      by PyPI.
    - `cupy-` namespace was
      [squatted](https://github.com/cupy/cupy/issues/4787) by a
      malicious actor thousands of times.
    - `scikit-` namespace was
      [squatted](https://blog.phylum.io/a-pypi-typosquatting-campaign-post-mortem/),
      among other packages. Notice how packages with a known prefix are
      much more prone to successful attacks.
    - `typing-` namespace was
      [squatted](https://zero.checkmarx.com/malicious-pypi-user-strikes-again-with-typosquatting-starjacking-and-unpacks-tailor-made-malware-b12669cefaa5)
      and this would be useful to prevent as a [hidden
      grant](##REF##hidden-grants).

[^5]: As an example, PyPI\'s concept of organizations is described
    [here](https://blog.pypi.org/posts/2023-04-23-introducing-pypi-organizations/).

[^6]: [Detailed write-up](https://discuss.python.org/t/64679) of the
    potential for provenance assertions.
