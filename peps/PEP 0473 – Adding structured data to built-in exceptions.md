---
pep: 473
title: Adding structured data to built-in exceptions
author:
- Sebastian Kreft <skreft@deezer.com>
status: Rejected
type: Standards Track
created: 29-Mar-2014
post_history: []
resolution: https://mail.python.org/pipermail/python-dev/2019-March/156692.html
python_status: Rejected
url: https://peps.python.org/pep-0473/
source_path: https://github.com/python/peps/blob/main/peps/pep-0473.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:27:54+00:00'
---

# Abstract

Exceptions like `AttributeError`, `IndexError`, `KeyError`,
`LookupError`, `NameError`, `TypeError`, and `ValueError` do not provide
all information required by programmers to debug and better understand
what caused them. Furthermore, in some cases the messages even have
slightly different formats, which makes it really difficult for tools to
automatically provide additional information to diagnose the problem. To
tackle the former and to lay ground for the latter, it is proposed to
expand these exceptions so to hold both the offending and affected
entities.

# Rationale

The main issue this PEP aims to solve is the fact that currently error
messages are not that expressive and lack some key information to
resolve the exceptions. Additionally, the information present on the
error message is not always in the same format, which makes it very
difficult for third-party libraries to provide automated diagnosis of
the error.

These automated tools could, for example, detect typos or display or log
extra debug information. These could be particularly useful when running
tests or in a long running application.

Although it is in theory possible to have such libraries, they need to
resort to hacks in order to achieve the goal. One such example is
python-improved-exceptions[^1], which modifies the byte-code to keep
references to the possibly interesting objects and also parses the error
messages to extract information like types or names. Unfortunately, such
approach is extremely fragile and not portable.

A similar proposal[^2] has been implemented for `ImportError` and in the
same fashion this idea has received support[^3]. Additionally, almost 10
years ago Guido asked in[^4] to have a clean API to access the affected
objects in Exceptions like `KeyError`, `AttributeError`, `NameError`,
and `IndexError`. Similar issues and proposals ideas have been written
in the last year. Some other issues have been created, but despite
receiving support they finally get abandoned. References to the created
issues are listed below:

- `AttributeError`:[^5],[^6],[^7],[^8],[^9]
- `IndexError`:[^10],[^11],[^12]
- `KeyError`:[^13],[^14],[^15]
- `LookupError`:[^16]
- `NameError`:[^17],[^18],[^19]
- `TypeError`:[^20]
- `ValueError`:[^21]

To move forward with the development and to centralize the information
and discussion, this PEP aims to be a meta-issue summarizing all the
above discussions and ideas.

# Examples

## IndexError

The error message does not reference the list\'s length nor the index
used.

    a = [1, 2, 3, 4, 5]
    a[5]
    IndexError: list index out of range

## KeyError

By convention the key is the first element of the error\'s argument, but
there\'s no other information regarding the affected dictionary (keys
types, size, etc.)

    b = {'foo': 1}
    b['fo']
    KeyError: 'fo'

## AttributeError

The object\'s type and the offending attribute are part of the error
message. However, there are some different formats and the information
is not always available. Furthermore, although the object type is useful
in some cases, given the dynamic nature of Python, it would be much more
useful to have a reference to the object itself. Additionally the
reference to the type is not fully qualified and in some cases the type
is just too generic to provide useful information, for example in case
of accessing a module\'s attribute.

    c = object()
    c.foo
    AttributeError: 'object' object has no attribute 'foo'

    import string
    string.foo
    AttributeError: 'module' object has no attribute 'foo'

    a = string.Formatter()
    a.foo
    AttributeError: 'Formatter' object has no attribute 'foo'

## NameError

The error message provides typically the name.

    foo = 1
    fo
    NameError: global name 'fo' is not defined

## Other Cases

Issues are even harder to debug when the target object is the result of
another expression, for example:

    a[b[c[0]]]

This issue is also related to the fact that opcodes only have line
number information and not the offset. This proposal would help in this
case but not as much as having offsets.

# Proposal

Extend the exceptions `AttributeError`, `IndexError`, `KeyError`,
`LookupError`, `NameError`, `TypeError`, and `ValueError` with the
following:

- `AttributeError`: target ^w^, attribute
- `IndexError`: target ^w^, key ^w^, index (just an alias to key)
- `KeyError`: target ^w^, key ^w^
- `LookupError`: target ^w^, key ^w^
- `NameError`: name, scope?
- `TypeError`: unexpected_type
- `ValueError`: unexpected_value ^w^

Attributes with the superscript ^w^ may need to be weak references[^22]
to prevent any memory cycles. However, this may add an unnecessary extra
complexity as noted by R. David Murray[^23]. This is specially true
given that builtin types do not support being weak referenced.

TODO(skreft): expand this with examples of corner cases.

To remain backwards compatible these new attributes will be optional and
keyword only.

It is proposed to add this information, rather than just improve the
error, as the former would allow new debugging frameworks and tools and
also in the future to switch to a lazy generated message. Generated
messages are discussed in[^24], although they are not implemented at the
moment. They would not only save some resources, but also uniform the
messages.

The stdlib will be then gradually changed so to start using these new
attributes.

# Potential Uses

An automated tool could for example search for similar keys within the
object, allowing to display the following::

    a = {'foo': 1}
    a['fo']
    KeyError: 'fo'. Did you mean 'foo'?

    foo = 1
    fo
    NameError: global name 'fo' is not defined. Did you mean 'foo'?

See[^25] for the output a TestRunner could display.

# Performance

Filling these new attributes would only require two extra parameters
with data already available so the impact should be marginal. However,
it may need special care for `KeyError` as the following pattern is
already widespread.

    try:
      a[foo] = a[foo] + 1
    except:
      a[foo] = 0

Note as well that storing these objects into the error itself would
allow the lazy generation of the error message, as discussed in[^26].

# References

# Copyright

This document has been placed in the public domain.

[^1]: Python Exceptions Improved
    (<https://www.github.com/sk-/python-exceptions-improved>)

[^2]: ImportError needs attributes for module and file name
    (<http://bugs.python.org/issue1559549>)

[^3]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^4]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^5]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^6]: making builtin exceptions more informative
    (<http://bugs.python.org/issue1182143>)

[^7]: Add an \'attr\' attribute to AttributeError
    (<http://bugs.python.org/issue18156>)

[^8]: Specificity in AttributeError
    (<https://mail.python.org/pipermail/python-ideas/2013-April/020308.html>)

[^9]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^10]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^11]: Add index attribute to IndexError
    (<http://bugs.python.org/issue18162>)

[^12]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^13]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^14]: Add a \'key\' attribute to KeyError
    (<http://bugs.python.org/issue18163>)

[^15]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^16]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^17]: LookupError etc. need API to get the key
    (<http://bugs.python.org/issue614557>)

[^18]: making builtin exceptions more informative
    (<http://bugs.python.org/issue1182143>)

[^19]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^20]: Add \'unexpected_type\' to TypeError
    (<http://bugs.python.org/issue18165>)

[^21]: \'value\' attribute for ValueError
    (<http://bugs.python.org/issue18166>)

[^22]: weakref - Weak References
    (<https://docs.python.org/3/library/weakref.html>)

[^23]: Message by R. David Murray: Weak refs on exceptions?
    (<http://bugs.python.org/issue18163#msg190791>)

[^24]: ImportError needs attributes for module and file name
    (<http://bugs.python.org/issue1559549>)

[^25]: Enhance exceptions by attaching some more information to them
    (<https://mail.python.org/pipermail/python-ideas/2014-February/025601.html>)

[^26]: ImportError needs attributes for module and file name
    (<http://bugs.python.org/issue1559549>)
