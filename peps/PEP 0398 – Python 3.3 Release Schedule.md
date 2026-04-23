---
pep: 398
title: Python 3.3 Release Schedule
author:
- Georg Brandl <georg@python.org>
status: Final
type: Informational
topic: Release
created: 23-Mar-2011
python_version: '3.3'
python_status: Final
url: https://peps.python.org/pep-0398/
source_path: https://github.com/python/peps/blob/main/peps/pep-0398.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:30+00:00'
---

# Abstract

This document describes the development and release schedule for Python
3.3. The schedule primarily concerns itself with PEP-sized items.

# Release Manager and Crew

- 3.3 Release Managers: Georg Brandl, Ned Deily (3.3.7+)
- Windows installers: Martin v. Löwis
- Mac installers: Ronald Oussoren/Ned Deily
- Documentation: Georg Brandl

# 3.3 Lifespan

3.3 will receive bugfix updates approximately every 4-6 months for
approximately 18 months. After the release of 3.4.0 final, a final 3.3
bugfix update will be released. After that, security updates (source
only) will be released until 5 years after the release of 3.3 final,
which will be September 2017.

As of 2017-09-29, Python 3.3.x reached end-of-life status.

# Release Schedule

## 3.3.0 schedule

- 3.3.0 alpha 1: March 5, 2012
- 3.3.0 alpha 2: April 2, 2012
- 3.3.0 alpha 3: May 1, 2012
- 3.3.0 alpha 4: May 31, 2012
- 3.3.0 beta 1: June 27, 2012

(No new features beyond this point.)

- 3.3.0 beta 2: August 12, 2012
- 3.3.0 candidate 1: August 24, 2012
- 3.3.0 candidate 2: September 9, 2012
- 3.3.0 candidate 3: September 24, 2012
- 3.3.0 final: September 29, 2012

## 3.3.1 schedule

- 3.3.1 candidate 1: March 23, 2013
- 3.3.1 final: April 6, 2013

## 3.3.2 schedule

- 3.3.2 final: May 13, 2013

## 3.3.3 schedule

- 3.3.3 candidate 1: October 27, 2013
- 3.3.3 candidate 2: November 9, 2013
- 3.3.3 final: November 16, 2013

## 3.3.4 schedule

- 3.3.4 candidate 1: January 26, 2014
- 3.3.4 final: February 9, 2014

## 3.3.5 schedule

Python 3.3.5 was the last regular maintenance release before 3.3 entered
security-fix only mode.

- 3.3.5 candidate 1: February 22, 2014
- 3.3.5 candidate 2: March 1, 2014
- 3.3.5 final: March 8, 2014

## 3.3.6 schedule

Security fixes only

- 3.3.6 candidate 1 (source-only release): October 4, 2014
- 3.3.6 final (source-only release): October 11, 2014

## 3.3.7 schedule

Security fixes only

- 3.3.7 candidate 1 (source-only release): September 6, 2017
- 3.3.7 final (source-only release): September 19, 2017

## 3.3.x end-of-life

- September 29, 2017

# Features for 3.3

Implemented / Final PEPs:

- `362`{.interpreted-text role="pep"}: Function Signature Object
- `380`{.interpreted-text role="pep"}: Syntax for Delegating to a
  Subgenerator
- `393`{.interpreted-text role="pep"}: Flexible String Representation
- `397`{.interpreted-text role="pep"}: Python launcher for Windows
- `399`{.interpreted-text role="pep"}: Pure Python/C Accelerator Module
  Compatibility Requirements
- `405`{.interpreted-text role="pep"}: Python Virtual Environments
- `409`{.interpreted-text role="pep"}: Suppressing exception context
- `412`{.interpreted-text role="pep"}: Key-Sharing Dictionary
- `414`{.interpreted-text role="pep"}: Explicit Unicode Literal for
  Python 3.3
- `415`{.interpreted-text role="pep"}: Implement context suppression
  with exception attributes
- `417`{.interpreted-text role="pep"}: Including mock in the Standard
  Library
- `418`{.interpreted-text role="pep"}: Add monotonic time, performance
  counter, and process time functions
- `420`{.interpreted-text role="pep"}: Implicit Namespace Packages
- `421`{.interpreted-text role="pep"}: Adding sys.implementation
- `3118`{.interpreted-text role="pep"}: Revising the buffer protocol
  (protocol semantics finalised)
- `3144`{.interpreted-text role="pep"}: IP Address manipulation library
- `3151`{.interpreted-text role="pep"}: Reworking the OS and IO
  exception hierarchy
- `3155`{.interpreted-text role="pep"}: Qualified name for classes and
  functions

Other final large-scale changes:

- Addition of the \"faulthandler\" module
- Addition of the \"lzma\" module, and lzma/xz support in tarfile
- Implementing `__import__` using importlib
- Addition of the C decimal implementation
- Switch of Windows build toolchain to VS 2010

Candidate PEPs:

- None

Other planned large-scale changes:

- None

Deferred to post-3.3:

- `395`{.interpreted-text role="pep"}: Qualified Names for Modules
- `3143`{.interpreted-text role="pep"}: Standard daemon process library
- `3154`{.interpreted-text role="pep"}: Pickle protocol version 4
- Breaking out standard library and docs in separate repos
- Addition of the \"packaging\" module, deprecating \"distutils\"
- Addition of the \"regex\" module
- Email version 6
- A standard event-loop interface (PEP by Jim Fulton pending)

# Copyright

This document has been placed in the public domain.
