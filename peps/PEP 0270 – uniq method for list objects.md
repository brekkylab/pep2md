---
pep: 270
title: uniq method for list objects
author:
- Jason Petrone <jp@demonseed.net>
status: Rejected
type: Standards Track
created: 21-Aug-2001
python_version: '2.2'
post_history: []
python_status: Rejected
url: https://peps.python.org/pep-0270/
source_path: https://github.com/python/peps/blob/main/peps/pep-0270.rst
source_commit: 528ab44afbc38daee4ae5c361f1bc79f600155b0
generated_at: '2026-04-23T06:17:26+00:00'
---

# Notice

This PEP is withdrawn by the author. He writes:

> Removing duplicate elements from a list is a common task, but there
> are only two reasons I can see for making it a built-in. The first is
> if it could be done much faster, which isn\'t the case. The second is
> if it makes it significantly easier to write code. The introduction of
> `sets.py` eliminates this situation since creating a sequence without
> duplicates is just a matter of choosing a different data structure: a
> set instead of a list.

As described in `218`{.interpreted-text role="pep"}, sets are being
added to the standard library for Python 2.3.

# Abstract

This PEP proposes adding a method for removing duplicate elements to the
list object.

# Rationale

Removing duplicates from a list is a common task. I think it is useful
and general enough to belong as a method in list objects. It also has
potential for faster execution when implemented in C, especially if
optimization using hashing or sorted cannot be used.

On comp.lang.python there are many, many, posts[^1] asking about the
best way to do this task. It\'s a little tricky to implement optimally
and it would be nice to save people the trouble of figuring it out
themselves.

# Considerations

Tim Peters suggests trying to use a hash table, then trying to sort, and
finally falling back on brute force[^2]. Should uniq maintain list order
at the expense of speed?

Is it spelled \'uniq\' or \'unique\'?

# Reference Implementation

I\'ve written the brute force version. It\'s about 20 lines of code in
`listobject.c`. Adding support for hash table and sorted duplicate
removal would only take another hour or so.

# References

# Copyright

This document has been placed in the public domain.

[^1]: <https://groups.google.com/forum/#!searchin/comp.lang.python/duplicates>

[^2]: Tim Peters unique() entry in the Python cookbook:
    <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52560/index_txt>
