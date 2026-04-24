---
pep: 4
title: Deprecation of Standard Modules
author:
- Brett Cannon <brett@python.org>
- Martin von Löwis <martin@v.loewis.de>
status: Active
type: Process
created: 01-Oct-2000
post_history: []
python_status: Active
url: https://peps.python.org/pep-0004/
source_path: https://github.com/python/peps/blob/main/peps/pep-0004.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:27:43+00:00'
---

# Introduction

When new modules were added to the standard Python library in the past,
it was not possible to foresee whether they would still be useful in the
future. Even though Python \"Comes With Batteries Included\", batteries
may discharge over time. Carrying old modules around is a burden on the
maintainer, especially when there is no interest in the module anymore.

At the same time, removing a module from the distribution is difficult,
as it is not known in general whether anybody is still using it. This
PEP defines a procedure for removing modules from the standard Python
library. Usage of a module may be \'deprecated\', which means that it
may be removed from a future Python release.

# Procedure for declaring a module deprecated

To remove a top-level module/package from the standard library, a PEP is
required. The deprecation process is outlined in `387`{.interpreted-text
role="pep"}.

For removing a submodule of a package in the standard library,
`387`{.interpreted-text role="pep"} must be followed, but a PEP is not
required.

# Copyright

This document has been placed in the public domain.
