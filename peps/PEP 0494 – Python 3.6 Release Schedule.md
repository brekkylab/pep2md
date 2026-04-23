---
pep: 494
title: Python 3.6 Release Schedule
author:
- Ned Deily <nad@python.org>
status: Final
type: Informational
topic: Release
created: 30-May-2015
python_version: '3.6'
python_status: Final
url: https://peps.python.org/pep-0494/
source_path: https://github.com/python/peps/blob/main/peps/pep-0494.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:34+00:00'
---

# Abstract

This document describes the development and release schedule for Python
3.6. The schedule primarily concerns itself with PEP-sized items.

# Release Manager and Crew

- 3.6 Release Manager: Ned Deily
- Windows installers: Steve Dower
- Mac installers: Ned Deily
- Documentation: Julien Palard, Georg Brandl

# 3.6 Lifespan

3.6 will receive [bugfix
updates](https://devguide.python.org/devcycle/#maintenance-branches)
approximately every 3 months for about 24 months. Sometime after the
release of 3.7.0 final, a final 3.6 bugfix update will be released.
After that, it is expected that [security
updates](https://devguide.python.org/devcycle/#security-branches)
(source only) will be released as needed until 5 years after the release
of 3.6 final, so until approximately 2021-12.

As of 2021-12-23, 3.6 has reached the [end-of-life
phase](https://devguide.python.org/devcycle/#end-of-life-branches) of
its release cycle. 3.6.15 was the final security release. The code base
for 3.6 is now frozen and no further updates will be provided nor issues
of any kind will be accepted on the bug tracker.

# Release Schedule

## 3.6.0 schedule

- 3.6 development begins: 2015-05-24
- 3.6.0 alpha 1: 2016-05-17
- 3.6.0 alpha 2: 2016-06-13
- 3.6.0 alpha 3: 2016-07-11
- 3.6.0 alpha 4: 2016-08-15
- 3.6.0 beta 1: 2016-09-12 (No new features beyond this point.)
- 3.6.0 beta 2: 2016-10-10
- 3.6.0 beta 3: 2016-10-31
- 3.6.0 beta 4: 2016-11-21
- 3.6.0 candidate 1: 2016-12-06
- 3.6.0 candidate 2: 2016-12-16
- 3.6.0 final: 2016-12-23

## 3.6.1 schedule (first bugfix release)

- 3.6.1 candidate: 2017-03-05
- 3.6.1 final: 2017-03-21

## 3.6.2 schedule

- 3.6.2 candidate 1: 2017-06-17
- 3.6.2 candidate 2: 2017-07-07
- 3.6.2 final: 2017-07-17

## 3.6.3 schedule

- 3.6.3 candidate: 2017-09-19
- 3.6.3 final: 2017-10-03

## 3.6.4 schedule

- 3.6.4 candidate: 2017-12-05
- 3.6.4 final: 2017-12-19

## 3.6.5 schedule

- 3.6.5 candidate: 2018-03-13
- 3.6.5 final: 2018-03-28

## 3.6.6 schedule

- 3.6.6 candidate: 2018-06-12
- 3.6.6 final: 2018-06-27

## 3.6.7 schedule

- 3.6.7 candidate: 2018-09-26
- 3.6.7 candidate 2: 2018-10-13
- 3.6.7 final: 2018-10-20

## 3.6.8 schedule (last bugfix release)

Last binary releases

- 3.6.8 candidate: 2018-12-11
- 3.6.8 final: 2018-12-24

## 3.6.9 schedule (first security-only release)

Source only

- 3.6.9 candidate 1: 2019-06-18
- 3.6.9 final: 2019-07-02

## 3.6.10 schedule

- 3.6.10 candidate 1: 2019-12-11
- 3.6.10 final: 2019-12-18

## 3.6.11 schedule

- 3.6.11 candidate 1: 2020-06-15
- 3.6.11 final: 2020-06-27

## 3.6.12 schedule

- 3.6.12 final: 2020-08-17

## 3.6.13 schedule

- 3.6.13 final: 2021-02-15

## 3.6.14 schedule

- 3.6.14 final: 2021-06-28

## 3.6.15 schedule (last security-only release)

- 3.6.15 final: 2021-09-04

# Features for 3.6

Implemented changes for 3.6 (as of 3.6.0 beta 1):

- `468`{.interpreted-text role="pep"}, Preserving Keyword Argument Order
- `487`{.interpreted-text role="pep"}, Simpler customization of class
  creation
- `495`{.interpreted-text role="pep"}, Local Time Disambiguation
- `498`{.interpreted-text role="pep"}, Literal String Formatting
- `506`{.interpreted-text role="pep"}, Adding A Secrets Module To The
  Standard Library
- `509`{.interpreted-text role="pep"}, Add a private version to dict
- `515`{.interpreted-text role="pep"}, Underscores in Numeric Literals
- `519`{.interpreted-text role="pep"}, Adding a file system path
  protocol
- `520`{.interpreted-text role="pep"}, Preserving Class Attribute
  Definition Order
- `523`{.interpreted-text role="pep"}, Adding a frame evaluation API to
  CPython
- `524`{.interpreted-text role="pep"}, Make os.urandom() blocking on
  Linux (during system startup)
- `525`{.interpreted-text role="pep"}, Asynchronous Generators
  (provisional)
- `526`{.interpreted-text role="pep"}, Syntax for Variable Annotations
  (provisional)
- `528`{.interpreted-text role="pep"}, Change Windows console encoding
  to UTF-8 (provisional)
- `529`{.interpreted-text role="pep"}, Change Windows filesystem
  encoding to UTF-8 (provisional)
- `530`{.interpreted-text role="pep"}, Asynchronous Comprehensions

# Copyright

This document has been placed in the public domain.
