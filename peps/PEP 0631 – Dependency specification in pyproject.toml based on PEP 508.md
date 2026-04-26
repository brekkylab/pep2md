---
pep: 631
title: Dependency specification in pyproject.toml based on PEP 508
author:
- Ofek Lev <ofekmeister@gmail.com>
sponsor: Paul Ganssle <paul@ganssle.io>
discussions_to: https://discuss.python.org/t/5018
status: Superseded
type: Standards Track
topic: Packaging
created: 20-Aug-2020
post_history:
- 20-Aug-2020
superseded_by: '621'
resolution: https://discuss.python.org/t/how-to-specify-dependencies-pep-508-strings-or-a-table-in-toml/5243/38
python_status: Superseded
url: https://peps.python.org/pep-0631/
source_path: https://github.com/python/peps/blob/main/peps/pep-0631.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:26+00:00'
---

# Abstract

This PEP specifies how to write a project\'s dependencies in a
`pyproject.toml` file for packaging-related tools to consume using the
`fields defined in PEP 621 <621#dependencies-optional-dependencies>`{.interpreted-text
role="pep"}.

:::: note
::: title
Note
:::

This PEP has been accepted and was merged into `621`{.interpreted-text
role="pep"}.
::::

# Entries

All dependency entries MUST be valid
`PEP 508 strings <508>`{.interpreted-text role="pep"}.

Build backends SHOULD abort at load time for any parsing errors.

    from packaging.requirements import InvalidRequirement, Requirement

    ...

    try:
        Requirement(entry)
    except InvalidRequirement:
        # exit

# Specification

## dependencies

- Format: array of strings
- Related core metadata:
  - [Requires-Dist](https://packaging.python.org/specifications/core-metadata/#requires-dist-multiple-use)

Every element MUST be an [entry](#entries).

    [project]
    dependencies = [
      'PyYAML ~= 5.0',
      'requests[security] < 3',
      'subprocess32; python_version < "3.2"',
    ]

## optional-dependencies

- Format: table
- Related core metadata:
  - [Provides-Extra](https://packaging.python.org/specifications/core-metadata/#provides-extra-multiple-use)
  - [Requires-Dist](https://packaging.python.org/specifications/core-metadata/#requires-dist-multiple-use)

Each key is the name of the provided option, with each value being the
same type as the [dependencies](#dependencies) field i.e. an array of
strings.

    [project.optional-dependencies]
    tests = [
      'coverage>=5.0.3',
      'pytest',
      'pytest-benchmark[histogram]>=3.2.1',
    ]

# Example

This is a real-world example port of what
[docker-compose](https://github.com/docker/compose/blob/789bfb0e8b2e61f15f423d371508b698c64b057f/setup.py#L28-L61)
defines.

    [project]
    dependencies = [
      'cached-property >= 1.2.0, < 2',
      'distro >= 1.5.0, < 2',
      'docker[ssh] >= 4.2.2, < 5',
      'dockerpty >= 0.4.1, < 1',
      'docopt >= 0.6.1, < 1',
      'jsonschema >= 2.5.1, < 4',
      'PyYAML >= 3.10, < 6',
      'python-dotenv >= 0.13.0, < 1',
      'requests >= 2.20.0, < 3',
      'texttable >= 0.9.0, < 2',
      'websocket-client >= 0.32.0, < 1',

      # Conditional
      'backports.shutil_get_terminal_size == 1.0.0; python_version < "3.3"',
      'backports.ssl_match_hostname >= 3.5, < 4; python_version < "3.5"',
      'colorama >= 0.4, < 1; sys_platform == "win32"',
      'enum34 >= 1.0.4, < 2; python_version < "3.4"',
      'ipaddress >= 1.0.16, < 2; python_version < "3.3"',
      'subprocess32 >= 3.5.4, < 4; python_version < "3.2"',
    ]

    [project.optional-dependencies]
    socks = [ 'PySocks >= 1.5.6, != 1.5.7, < 2' ]
    tests = [
      'ddt >= 1.2.2, < 2',
      'pytest < 6',
      'mock >= 1.0.1, < 4; python_version < "3.4"',
    ]

# Implementation

## Parsing

    from packaging.requirements import InvalidRequirement, Requirement

    def parse_dependencies(config):
        dependencies = config.get('dependencies', [])
        if not isinstance(dependencies, list):
            raise TypeError('Field `project.dependencies` must be an array')

        for i, entry in enumerate(dependencies, 1):
            if not isinstance(entry, str):
                raise TypeError(f'Dependency #{i} of field `project.dependencies` must be a string')

            try:
                Requirement(entry)
            except InvalidRequirement as e:
                raise ValueError(f'Dependency #{i} of field `project.dependencies` is invalid: {e}')

        return dependencies

    def parse_optional_dependencies(config):
        optional_dependencies = config.get('optional-dependencies', {})
        if not isinstance(optional_dependencies, dict):
            raise TypeError('Field `project.optional-dependencies` must be a table')

        optional_dependency_entries = {}

        for option, dependencies in optional_dependencies.items():
            if not isinstance(dependencies, list):
                raise TypeError(
                    f'Dependencies for option `{option}` of field '
                    '`project.optional-dependencies` must be an array'
                )

            entries = []

            for i, entry in enumerate(dependencies, 1):
                if not isinstance(entry, str):
                    raise TypeError(
                        f'Dependency #{i} of option `{option}` of field '
                        '`project.optional-dependencies` must be a string'
                    )

                try:
                    Requirement(entry)
                except InvalidRequirement as e:
                    raise ValueError(
                        f'Dependency #{i} of option `{option}` of field '
                        f'`project.optional-dependencies` is invalid: {e}'
                    )
                else:
                    entries.append(entry)

            optional_dependency_entries[option] = entries

        return optional_dependency_entries

## Metadata

    def construct_metadata_file(metadata_object):
        """
        https://packaging.python.org/specifications/core-metadata/
        """
        metadata_file = 'Metadata-Version: 2.1\n'

        ...

        if metadata_object.dependencies:
            # Sort dependencies to ensure reproducible builds
            for dependency in sorted(metadata_object.dependencies):
                metadata_file += f'Requires-Dist: {dependency}\n'

        if metadata_object.optional_dependencies:
            # Sort extras and dependencies to ensure reproducible builds
            for option, dependencies in sorted(metadata_object.optional_dependencies.items()):
                metadata_file += f'Provides-Extra: {option}\n'
                for dependency in sorted(dependencies):
                    if ';' in dependency:
                        metadata_file += f'Requires-Dist: {dependency} and extra == "{option}"\n'
                    else:
                        metadata_file += f'Requires-Dist: {dependency}; extra == "{option}"\n'

        ...

        return metadata_file

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
