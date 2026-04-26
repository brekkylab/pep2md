---
pep: 220
title: Coroutines, Generators, Continuations
author:
- Gordon McMillan <gmcm@hypernet.com>
status: Rejected
type: Informational
created: 14-Aug-2000
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0220/
source_path: https://github.com/python/peps/blob/main/peps/pep-0220.rst
source_commit: 7b1aca80ce7767ce3d75ec6718ded1854a940204
---

::: rejected
:::

# Abstract

Demonstrates why the changes described in the stackless PEP are
desirable. A low-level continuations module exists. With it, coroutines
and generators and \"green\" threads can be written. A higher level
module that makes coroutines and generators easy to create is desirable
(and being worked on). The focus of this PEP is on showing how
coroutines, generators, and green threads can simplify common
programming problems.
