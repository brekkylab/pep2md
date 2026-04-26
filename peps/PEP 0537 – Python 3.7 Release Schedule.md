---
pep: 537
title: Python 3.7 Release Schedule
author:
- Ned Deily <nad@python.org>
status: Final
type: Informational
topic: Release
created: 23-Dec-2016
python_version: '3.7'
python_status: Final
url: https://peps.python.org/pep-0537/
source_path: https://github.com/python/peps/blob/main/peps/pep-0537.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:23+00:00'
---

# Abstract

This document describes the development and release schedule for Python
3.7. The schedule primarily concerns itself with PEP-sized items.

# Release Manager and Crew

- 3.7 Release Manager: Ned Deily
- Windows installers: Steve Dower
- Mac installers: Ned Deily
- Documentation: Julien Palard

# 3.7 Lifespan

3.7 will receive [bugfix
updates](https://devguide.python.org/devcycle/#maintenance-branches)
approximately every 3 months for about 24 months. Sometime after the
release of 3.8.0 final, a final 3.7 bugfix update will be released.
After that, it is expected that [security
updates](https://devguide.python.org/devcycle/#security-branches)
(source only) will be released as needed until 5 years after the release
of 3.7 final, so until approximately 2023-06.

As of 2023-06-27, 3.7 has reached the [end-of-life
phase](https://devguide.python.org/devcycle/#end-of-life-branches) of
its release cycle. 3.7.17 was the final security release. The code base
for 3.7 is now frozen and no further updates will be provided nor issues
of any kind will be accepted on the bug tracker.

# Release Schedule

## 3.7.0 schedule

- 3.7 development begins: 2016-09-12
- 3.7.0 alpha 1: 2017-09-19
- 3.7.0 alpha 2: 2017-10-17
- 3.7.0 alpha 3: 2017-12-05
- 3.7.0 alpha 4: 2018-01-09
- 3.7.0 beta 1: 2018-01-31 (No new features beyond this point.)
- 3.7.0 beta 2: 2018-02-27
- 3.7.0 beta 3: 2018-03-29
- 3.7.0 beta 4: 2018-05-02
- 3.7.0 beta 5: 2018-05-30
- 3.7.0 candidate 1: 2018-06-12
- 3.7.0 final: 2018-06-27

## 3.7.1 schedule (first bugfix release)

- 3.7.1 candidate 1: 2018-09-26
- 3.7.1 candidate 2: 2018-10-13
- 3.7.1 final: 2018-10-20

## 3.7.2 schedule

- 3.7.2 candidate 1: 2018-12-11
- 3.7.2 final: 2018-12-24

## 3.7.3 schedule

- 3.7.3 candidate 1: 2019-03-12
- 3.7.3 final: 2019-03-25

## 3.7.4 schedule

- 3.7.4 candidate 1: 2019-06-18
- 3.7.4 candidate 2: 2019-07-02
- 3.7.4 final: 2019-07-08

## 3.7.5 schedule

- 3.7.5 candidate 1: 2019-10-02
- 3.7.5 final: 2019-10-15

## 3.7.6 schedule

- 3.7.6 candidate 1: 2019-12-11
- 3.7.6 final: 2019-12-18

## 3.7.7 schedule

- 3.7.7 candidate 1: 2020-03-04
- 3.7.7 final: 2020-03-10

## 3.7.8 schedule (last bugfix release)

Last planned release of binaries

- 3.7.8 candidate 1: 2020-06-15
- 3.7.8 final: 2020-06-27

## 3.7.9 schedule (security/binary release)

Security fixes plus updated binary installers to address 3.7.8 issues;
no further binary releases are planned.

- 3.7.9 final: 2020-08-17

## 3.7.10 schedule

- 3.7.10 final: 2021-02-15

## 3.7.11 schedule

- 3.7.11 final: 2021-06-28

## 3.7.12 schedule

- 3.7.12 final: 2021-09-04

## 3.7.13 schedule

- 3.7.13 final: 2022-03-16

## 3.7.14 schedule

- 3.7.14 final: 2022-09-06

## 3.7.15 schedule

- 3.7.15 final: 2022-10-11

## 3.7.16 schedule

- 3.7.16 final: 2022-12-06

## 3.7.17 schedule (last security-only release)

- 3.7.17 final: 2023-06-06

# Features for 3.7

Implemented PEPs for 3.7 (as of 3.7.0 beta 1):

- `538`{.interpreted-text role="pep"}, Coercing the legacy C locale to a
  UTF-8 based locale
- `539`{.interpreted-text role="pep"}, A New C-API for Thread-Local
  Storage in CPython
- `540`{.interpreted-text role="pep"}, `UTF-8` mode
- `552`{.interpreted-text role="pep"}, Deterministic `pyc`
- `553`{.interpreted-text role="pep"}, Built-in breakpoint()
- `557`{.interpreted-text role="pep"}, Data Classes
- `560`{.interpreted-text role="pep"}, Core support for typing module
  and generic types
- `562`{.interpreted-text role="pep"}, Module `__getattr__` and
  `__dir__`
- `563`{.interpreted-text role="pep"}, Postponed Evaluation of
  Annotations
- `564`{.interpreted-text role="pep"}, Time functions with nanosecond
  resolution
- `565`{.interpreted-text role="pep"}, Show DeprecationWarning in
  \_\_main\_\_
- `567`{.interpreted-text role="pep"}, Context Variables

# Copyright

This document has been placed in the public domain.
