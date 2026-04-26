---
pep: 569
title: Python 3.8 Release Schedule
author:
- Łukasz Langa <lukasz@python.org>
status: Final
type: Informational
topic: Release
created: 27-Jan-2018
python_version: '3.8'
python_status: Final
url: https://peps.python.org/pep-0569/
source_path: https://github.com/python/peps/blob/main/peps/pep-0569.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:24+00:00'
---

# Abstract

This document describes the development and release schedule for Python
3.8. The schedule primarily concerns itself with PEP-sized items.

# Release Manager and Crew

- 3.8 Release Manager: Łukasz Langa
- Windows installers: Steve Dower
- Mac installers: Ned Deily
- Documentation: Julien Palard

# 3.8 Lifespan

3.8 will receive bugfix updates approximately every 2 months for
approximately 18 months. Some time after the release of 3.9.0 final, the
ninth and final 3.8 bugfix update was released. After that, security
updates (source only) were released for 5 years until the release of
Python 3.13.0 final.

As of 2024-10-07, 3.8 has reached the [end-of-life
phase](https://devguide.python.org/devcycle/#end-of-life-branches) of
its release cycle. 3.8.20 was the final security release. The codebase
for 3.8 is now frozen and no further updates will be provided nor issues
of any kind will be accepted on the bug tracker.

# Release Schedule

## 3.8.0 schedule

Actual:

- 3.8 development begins: Monday, 2018-01-29
- 3.8.0 alpha 1: Sunday, 2019-02-03
- 3.8.0 alpha 2: Monday, 2019-02-25
- 3.8.0 alpha 3: Monday, 2019-03-25
- 3.8.0 alpha 4: Monday, 2019-05-06
- 3.8.0 beta 1: Tuesday, 2019-06-04 (No new features beyond this point.)
- 3.8.0 beta 2: Thursday, 2019-07-04
- 3.8.0 beta 3: Monday, 2019-07-29
- 3.8.0 beta 4: Friday, 2019-08-30
- 3.8.0 candidate 1: Tuesday, 2019-10-01
- 3.8.0 final: Monday, 2019-10-14

## Bugfix releases

Actual:

- 3.8.1 candidate 1: Tuesday, 2019-12-10
- 3.8.1 final: Wednesday, 2019-12-18
- 3.8.2 candidate 1: Monday, 2020-02-10
- 3.8.2 candidate 2: Monday, 2020-02-17
- 3.8.2 final: Monday, 2020-02-24
- 3.8.3 candidate 1: Wednesday, 2020-04-29
- 3.8.3 final: Wednesday, 2020-05-13
- 3.8.4 candidate 1: Tuesday, 2020-06-30
- 3.8.4 final: Monday, 2020-07-13
- 3.8.5 final: Monday, 2020-07-20 (security hotfix)
- 3.8.6 candidate 1: Tuesday, 2020-09-08
- 3.8.6 final: Thursday, 2020-09-24
- 3.8.7 candidate 1: Monday, 2020-12-07
- 3.8.7 final: Monday, 2020-12-21
- 3.8.8 candidate 1: Tuesday, 2021-02-16
- 3.8.8 final: Friday, 2021-02-19
- 3.8.9 final: Friday, 2021-04-02 (security hotfix)
- 3.8.10 final: Monday, 2021-05-03 (Final regular bugfix release with
  binary installers)

## Source-only security fix releases

Provided irregularly on an \"as-needed\" basis until October 7th 2024.

- 3.8.11 final: Monday, 2021-06-28
- 3.8.12 final: Monday, 2021-08-30
- 3.8.13 final: Wednesday, 2022-03-16
- 3.8.14 final: Tuesday, 2022-09-06
- 3.8.15 final: Tuesday, 2022-10-11
- 3.8.16 final: Tuesday, 2022-12-06
- 3.8.17 final: Tuesday, 2023-06-06
- 3.8.18 final: Thursday, 2023-08-24
- 3.8.19 final: Tuesday, 2024-03-19
- 3.8.20 final: Friday, 2024-09-06 (final security release)

# Features for 3.8

Some of the notable features of Python 3.8 include:

- `570`{.interpreted-text role="pep"}, Positional-only arguments
- `572`{.interpreted-text role="pep"}, Assignment Expressions
- `574`{.interpreted-text role="pep"}, Pickle protocol 5 with
  out-of-band data
- `578`{.interpreted-text role="pep"}, Runtime audit hooks
- `587`{.interpreted-text role="pep"}, Python Initialization
  Configuration
- `590`{.interpreted-text role="pep"}, Vectorcall: a fast calling
  protocol for CPython
- Typing-related: `591`{.interpreted-text role="pep"} (Final qualifier),
  `586`{.interpreted-text role="pep"} (Literal types), and
  `589`{.interpreted-text role="pep"} (TypedDict)
- Parallel filesystem cache for compiled bytecode
- Debug builds share ABI as release builds
- f-strings support a handy `=` specifier for debugging
- `continue` is now legal in `finally:` blocks
- on Windows, the default `asyncio` event loop is now
  `ProactorEventLoop`
- on macOS, the *spawn* start method is now used by default in
  `multiprocessing`
- `multiprocessing` can now use shared memory segments to avoid pickling
  costs between processes
- `typed_ast` is merged back to CPython
- `LOAD_GLOBAL` is now 40% faster
- `pickle` now uses Protocol 4 by default, improving performance

There are many other interesting changes, please consult the \"What\'s
New\" page in the documentation for a full list.

# Copyright

This document has been placed in the public domain.
