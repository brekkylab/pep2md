---
pep: 3100
title: Miscellaneous Python 3.0 Plans
author:
- Brett Cannon <brett@python.org>
status: Final
type: Process
created: 20-Aug-2004
post_history: []
python_status: Final
url: https://peps.python.org/pep-3100/
source_path: https://github.com/python/peps/blob/main/peps/pep-3100.rst
source_commit: 694086c010df64f20e72df84fae0ba20bfe86bff
generated_at: '2026-04-24T03:28:11+00:00'
---

# Abstract

This PEP, previously known as `3000`{.interpreted-text role="pep"},
describes smaller scale changes and new features for which no separate
PEP is written yet, all targeted for Python 3000.

The list of features included in this document is subject to change and
isn\'t binding on the Python development community; features may be
added, removed, and modified at any time. The purpose of this list is to
focus our language development effort on changes that are steps to 3.0,
and to encourage people to invent ways to smooth the transition.

This document is not a wish-list that anyone can extend. While there are
two authors of this PEP, we\'re just supplying the text; the decisions
for which changes are listed in this document are made by Guido van
Rossum, who has chosen them as goals for Python 3.0.

Guido\'s pronouncements on things that will not change in Python 3.0 are
recorded in `3099`{.interpreted-text role="pep"}.

# General goals

A general goal is to reduce feature duplication by removing old ways of
doing things. A general principle of the design will be that one obvious
way of doing something is enough.[^1]

# Influencing PEPs

- `238`{.interpreted-text role="pep"} (Changing the Division Operator)
- `328`{.interpreted-text role="pep"} (Imports: Multi-Line and
  Absolute/Relative)
- `343`{.interpreted-text role="pep"} (The \"with\" Statement)
- `352`{.interpreted-text role="pep"} (Required Superclass for
  Exceptions)

# Style changes

- The C style guide will be updated to use 4-space indents, never tabs.
  This style should be used for all new files; existing files can be
  updated only if there is no hope to ever merge a particular file from
  the Python 2 HEAD. Within a file, the indentation style should be
  consistent. No other style guide changes are planned ATM.

# Core language

- True division becomes default behavior `238`{.interpreted-text
  role="pep"} \[done\]

- `exec` as a statement is not worth it \-- make it a function \[done\]

- Add optional declarations for static typing `3107`{.interpreted-text
  role="pep"}[^2] \[done\]

- Support only new-style classes; classic classes will be gone[^3]
  \[done\]

- Replace `print` by a function[^4] `3105`{.interpreted-text role="pep"}
  \[done\]

- The `softspace` attribute of files goes away. \[done\]

- Use `except E1, E2, E3 as err:` if you want the error variable.[^5]
  \[done\]

- `None` becomes a keyword[^6]; also `True` and `False` \[done\]

- `...` to become a general expression element[^7] \[done\]

- `as` becomes a keyword[^8] (starting in 2.6 already) \[done\]

- Have list comprehensions be syntactic sugar for passing an equivalent
  generator expression to `list()`; as a consequence the loop variable
  will no longer be exposed `289`{.interpreted-text role="pep"} \[done\]

- Comparisons other than `==` and `!=` between disparate types will
  raise an exception unless explicitly supported by the type[^9]
  \[done\]

- floats will not be acceptable as arguments in place of ints for
  operations where floats are inadvertently accepted (PyArg_ParseTuple()
  i & l formats)

- Remove from \... import \* at function scope. \[done\] This means that
  functions can always be optimized and support for unoptimized
  functions can go away.

- 

  Imports `328`{.interpreted-text role="pep"}

  :   - Imports will be absolute by default. \[done\]
      - Relative imports must be explicitly specified. \[done\]
      - Indirection entries in `sys.modules` (i.e., a value of `None`
        for `A.string` means to use the top-level `string` module) will
        not be supported.

- \_\_init\_\_.py might become optional in sub-packages? \_\_init\_\_.py
  will still be required for top-level packages.

- Cleanup the Py_InitModule() variants {,3,4} (also import and parser
  APIs)

- Cleanup the APIs exported in pythonrun, etc.

- Some expressions will require parentheses that didn\'t in 2.x:
  - List comprehensions will require parentheses around the iterables.
    This will make list comprehensions more similar to generator
    comprehensions. \[x for x in 1, 2\] will need to be: \[x for x in
    (1, 2)\] \[done\]
  - Lambdas may have to be parenthesized `308`{.interpreted-text
    role="pep"} \[NO\]

- In order to get rid of the confusion between \_\_builtin\_\_ and
  \_\_builtins\_\_, it was decided to rename \_\_builtin\_\_ (the
  module) to builtins, and to leave \_\_builtins\_\_ (the sandbox hook)
  alone.[^10][^11] \[done\]

- Attributes on functions of the form `func_whatever` will be renamed
  `__whatever__`[^12] \[done\]

- Set literals and comprehensions[^13][^14] \[done\] {x} means
  set(\[x\]); {x, y} means set(\[x, y\]). {F(x) for x in S if P(x)}
  means set(F(x) for x in S if P(x)). NB. {range(x)} means
  set(\[range(x)\]), NOT set(range(x)). There\'s no literal for an empty
  set; use set() (or {1}&{2} :-). There\'s no frozenset literal; they
  are too rarely needed.

- The `__nonzero__` special method will be renamed to `__bool__` and
  have to return a bool. The typeobject slot will be called
  `tp_bool`[^15] \[done\]

- Dict comprehensions, as first proposed in `274`{.interpreted-text
  role="pep"} \[done\] {K(x): V(x) for x in S if P(x)} means dict((K(x),
  V(x)) for x in S if P(x)).

To be removed:

- String exceptions: use instances of an Exception class[^16] \[done\]

- `raise Exception, "message"`: use `raise Exception("message")`[^17]
  \[done\]

- `x`: use `repr(x)`[^18] \[done\]

- The `<>` operator: use `!=` instead[^19] \[done\]

- The \_\_mod\_\_ and \_\_divmod\_\_ special methods on float. \[they
  should stay\][^20]

- Drop unbound methods[^21][^22] \[done\]

- METH_OLDARGS \[done\]

- WITH_CYCLE_GC \[done\]

- \_\_getslice\_\_, \_\_setslice\_\_, \_\_delslice\_\_[^23]; remove
  slice opcodes and use slice objects. \[done\]

- `__oct__`, `__hex__`: use `__index__` in `oct()` and `hex()` instead.
  \[done\]

- `__methods__` and `__members__` \[done\]

- C APIs (see code): PyFloat_AsString, PyFloat_AsReprString,
  PyFloat_AsStringEx, PySequence_In, PyEval_EvalFrame,
  PyEval_CallObject, [PyObject_Del]{#pyobject_del},
  [PyObject_GC_Del]{#pyobject_gc_del},
  [PyObject_GC_Track]{#pyobject_gc_track},
  [PyObject_GC_UnTrack]{#pyobject_gc_untrack} PyString_AsEncodedString,
  PyString_AsDecodedString PyArg_NoArgs, PyArg_GetInt, intargfunc,
  intintargfunc

  PyImport_ReloadModule ?

# Atomic Types

- Remove distinction between int and long types; \'long\' built-in type
  and literals with \'L\' or \'l\' suffix disappear[^24] \[done\]
- Make all strings be Unicode, and have a separate bytes() type[^25] The
  new string type will be called \'str\'. See `3137`{.interpreted-text
  role="pep"}. \[done\]
- Return iterable views instead of lists where appropriate for atomic
  type methods (e.g. `dict.keys()`, `dict.values()`, `dict.items()`,
  etc.); iter\* methods will be removed. \[done\]
- Make `string.join()` stringify its arguments?[^26] \[NO\]
- Fix open() so it returns a ValueError if the mode is bad rather than
  IOError. \[done\]

To be removed:

- `basestring.find()` and `basestring.rfind()`; use `basestring.index()`
  or `basestring.[r]partition()` or `basestring.rindex()` in a
  try/except block???[^27] \[UNLIKELY\]
- `file.xreadlines()` method[^28] \[done\]
- `dict.setdefault()`?[^29] \[UNLIKELY\]
- `dict.has_key()` method; use `in` operator \[done\]
- `list.sort()` and `builtin.sorted()` methods: eliminate `cmp`
  parameter[^30] \[done\]

# Built-in Namespace

- Make built-ins return an iterator where appropriate (e.g. `range()`,
  `zip()`, `map()`, `filter()`, etc.) \[done\]
- Remove `input()` and rename `raw_input()` to `input()`. If you need
  the old input(), use eval(input()). \[done\]
- Introduce `trunc()`, which would call the `__trunc__()` method on its
  argument; suggested use is for objects like float where calling
  `__int__()` has data loss, but an integral representation is still
  desired?[^31] \[done\]
- Exception hierarchy changes `352`{.interpreted-text role="pep"}
  \[done\]
- Add a `bin()` function for a binary representation of integers
  \[done\]

To be removed:

- `apply()`: use `f(*args, **kw)` instead[^32] \[done\]

- `buffer()`: must die (use a bytes() type instead) (?)[^33] \[done\]

- `callable()`: just use isinstance(x, collections.Callable) (?)[^34]
  \[done\]

- `compile()`: put in `sys` (or perhaps in a module of its own)[^35]

- `coerce()`: no longer needed[^36] \[done\]

- `execfile()`, `reload()`: use `exec()`[^37] \[done\]

- `intern()`: put in `sys`[^38],[^39] \[done\]

- `reduce()`: put in `functools`, a loop is more readable most of the
  times[^40],[^41] \[done\]

- `xrange()`: use `range()` instead[^42] \[See range() above\] \[done\]

- 

  `StandardError`: this is a relic from the original exception hierarchy;

  :   subclass `Exception` instead. \[done\]

# Standard library

- Reorganize the standard library to not be as shallow?
- Move test code to where it belongs, there will be no more test()
  functions in the standard library
- Convert all tests to use either doctest or unittest.
- For the procedures of standard library improvement, see
  `3001`{.interpreted-text role="pep"}

To be removed:

- The sets module. \[done\]

- 

  stdlib modules to be removed

  :   - 

        see docstrings and comments in the source

        :   - `macfs` \[to do\]
            - `new`, `reconvert`, `stringold`, `xmllib`, `pcre`,
              `pypcre`, `strop` \[all done\]

      - 

        see `4`{.interpreted-text role="pep"}

        :   - `buildtools`, `mimetools`, `multifile`, `rfc822`, \[to
              do\]
            - `mpz`, `posixfile`, `regsub`, `rgbimage`, `sha`,
              `statcache`, `sv`, `TERMIOS`, `timing` \[done\]
            - `cfmfile`, `gopherlib`, `md5`, `MimeWriter`, `mimify`
              \[done\]
            - `cl`, `sets`, `xreadlines`, `rotor`, `whrandom` \[done\]

      - 

        Everything in lib-old `4`{.interpreted-text role="pep"} \[done\]

        :   - `Para`, `addpack`, `cmp`, `cmpcache`, `codehack`,
              `dircmp`, `dump`, `find`, `fmt`, `grep`, `lockfile`,
              `newdir`, `ni`, `packmail`, `poly`, `rand`, `statcache`,
              `tb`, `tzparse`, `util`, `whatsound`, `whrandom`, `zmod`

- `sys.exitfunc`: use atexit module instead[^43], [^44] \[done\]

- `sys.exc_type`, `sys.exc_values`, `sys.exc_traceback`: not
  thread-safe; use `sys.exc_info()` or an attribute of the
  exception[^45][^46][^47] \[done\]

- `sys.exc_clear`: Python 3\'s except statements provide the same
  functionality[^48] `3110`{.interpreted-text role="pep"}[^49] \[done\]

- `array.read`, `array.write`[^50]

- `operator.isCallable` : `callable()` built-in is being removed
  [^51][^52] \[done\]

- `operator.sequenceIncludes` : redundant thanks to
  `operator.contains`[^53][^54] \[done\]

- In the thread module, the acquire_lock() and release_lock() aliases
  for the acquire() and release() methods on lock objects. (Probably
  also just remove the thread module as a public API, in favor of always
  using threading.py.)

- UserXyz classes, in favour of XyzMixins.

- Remove the unreliable empty() and full() methods from Queue.py?[^55]

- Remove jumpahead() from the random API?[^56]

- Make the primitive for random be something generating random bytes
  rather than random floats?[^57]

- Get rid of Cookie.SerialCookie and Cookie.SmartCookie?[^58]

- Modify the heapq.heapreplace() API to compare the new value to the top
  of the heap?[^59]

# Outstanding Issues

- Require C99, so we can use // comments, named initializers, declare
  variables without introducing a new scope, among other benefits. (Also
  better support for IEEE floating point issues like NaN and
  infinities?)
- Remove support for old systems, including: BeOS, RISCOS, (SGI) Irix,
  Tru64

# References

# Copyright

This document has been placed in the public domain.

[^1]: PyCon 2003 State of the Union:
    <https://legacy.python.org/doc/essays/ppt/pycon2003/pycon2003.ppt>

[^2]: Guido\'s blog (\"Python Optional Typechecking Redux\")
    <https://www.artima.com/weblogs/viewpost.jsp?thread=89161>

[^3]: PyCon 2003 State of the Union:
    <https://legacy.python.org/doc/essays/ppt/pycon2003/pycon2003.ppt>

[^4]: python-dev email (Replacement for print in Python 3.0)
    <https://mail.python.org/pipermail/python-dev/2005-September/056154.html>

[^5]: Python Wiki: <https://wiki.python.org/moin/Python3.0>

[^6]: python-dev email (\"Constancy of None\")
    <https://mail.python.org/pipermail/python-dev/2004-July/046294.html>

[^7]: python-3000 email
    <https://mail.python.org/pipermail/python-3000/2006-April/000996.html>

[^8]: python-dev email (\' \"as\" to be a keyword?\')
    <https://mail.python.org/pipermail/python-dev/2004-July/046316.html>

[^9]: python-dev email (\"Comparing heterogeneous types\")
    <https://mail.python.org/pipermail/python-dev/2004-June/045111.html>

[^10]: Approach to resolving \_\_builtin\_\_ vs \_\_builtins\_\_
    <https://mail.python.org/pipermail/python-3000/2007-March/006161.html>

[^11]: New name for \_\_builtins\_\_
    <https://mail.python.org/pipermail/python-dev/2007-November/075388.html>

[^12]: python-3000 email (\"Pronouncement on parameter lists\")
    <https://mail.python.org/pipermail/python-3000/2006-April/001175.html>

[^13]: python-3000 email (\"sets in P3K?\")
    <https://mail.python.org/pipermail/python-3000/2006-April/001286.html>

[^14]: python-3000 email (\"sets in P3K?\")
    <https://mail.python.org/pipermail/python-3000/2006-May/001666.html>

[^15]: python-3000 email (\"\_\_nonzero\_\_ vs. \_\_bool\_\_\")
    <https://mail.python.org/pipermail/python-3000/2006-November/004524.html>

[^16]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^17]: python-dev email (\"PEP 8: exception style\")
    <https://mail.python.org/pipermail/python-dev/2005-August/055190.html>

[^18]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^19]: Python Wiki: <https://wiki.python.org/moin/Python3.0>

[^20]: python-3000 email (\"bug in modulus?\")
    <https://mail.python.org/pipermail/python-3000/2006-May/001735.html>

[^21]: python-dev email (\"Let\'s get rid of unbound methods\")
    <https://mail.python.org/pipermail/python-dev/2005-January/050625.html>

[^22]: python-dev email (\"Should we do away with unbound methods in
    Py3k?\")
    <https://mail.python.org/pipermail/python-dev/2007-November/075279.html>

[^23]: Python docs (Additional methods for emulation of sequence types)
    <https://docs.python.org/release/2.6/reference/datamodel.html#additional-methods-for-emulation-of-sequence-types>

[^24]: PyCon 2003 State of the Union:
    <https://legacy.python.org/doc/essays/ppt/pycon2003/pycon2003.ppt>

[^25]: PyCon 2003 State of the Union:
    <https://legacy.python.org/doc/essays/ppt/pycon2003/pycon2003.ppt>

[^26]: python-3000 email (\"More wishful thinking\")
    <https://mail.python.org/pipermail/python-3000/2006-April/000810.html>

[^27]: python-dev email (Remove str.find in 3.0?)
    <https://mail.python.org/pipermail/python-dev/2005-August/055705.html>

[^28]: Python docs (File objects)
    <https://docs.python.org/release/2.6/library/stdtypes.html>

[^29]: python-dev email (\"defaultdict\")
    <https://mail.python.org/pipermail/python-dev/2006-February/061261.html>

[^30]: python-dev email (\"Mutable sequence .sort() signature\")
    <https://mail.python.org/pipermail/python-dev/2008-February/076818.html>

[^31]: python-dev email (\"Fixing
    [PyEval_SliceIndex]{#pyeval_sliceindex} so that integer-like objects
    can be used\")
    <https://mail.python.org/pipermail/python-dev/2005-February/051674.html>

[^32]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^33]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^34]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^35]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^36]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^37]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^38]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^39]: SF patch \"sys.id() and sys.intern()\"
    <https://bugs.python.org/issue1601678>

[^40]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^41]: Guido\'s blog (\"The fate of reduce() in Python 3000\")
    <https://www.artima.com/weblogs/viewpost.jsp?thread=98196>

[^42]: PyCon 2003 State of the Union:
    <https://legacy.python.org/doc/essays/ppt/pycon2003/pycon2003.ppt>

[^43]: Python docs (sys \-- System-specific parameters and functions)
    <https://docs.python.org/release/2.6/library/sys.html>

[^44]: Patch to remove sys.exitfunc
    <https://github.com/python/cpython/issues/44715>

[^45]: Python Regrets:
    <https://legacy.python.org/doc/essays/ppt/regrets/PythonRegrets.pdf>

[^46]: python-dev email (\"anonymous blocks\")
    <https://mail.python.org/pipermail/python-dev/2005-April/053060.html>

[^47]: Python docs (sys \-- System-specific parameters and functions)
    <https://docs.python.org/release/2.6/library/sys.html>

[^48]: python-3000 email (\"Pre-peps on raise and except changes\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005672.html>

[^49]: Python docs (sys \-- System-specific parameters and functions)
    <https://docs.python.org/release/2.6/library/sys.html>

[^50]: Python docs (array \-- Efficient arrays of numeric values)
    <https://docs.python.org/release/2.6/library/array.html>

[^51]: Python docs (operator \-- Standard operators as functions)
    <https://docs.python.org/release/2.6/library/operator.html>

[^52]: Remove deprecated functions from operator
    <https://github.com/python/cpython/issues/43602>

[^53]: Python docs (operator \-- Standard operators as functions)
    <https://docs.python.org/release/2.6/library/operator.html>

[^54]: Remove deprecated functions from operator
    <https://github.com/python/cpython/issues/43602>

[^55]: python-3000 email (\"Py3.0 Library Ideas\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005726.html>

[^56]: python-3000 email (\"Py3.0 Library Ideas\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005726.html>

[^57]: python-3000 email (\"Py3.0 Library Ideas\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005726.html>

[^58]: python-3000 email (\"Py3.0 Library Ideas\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005726.html>

[^59]: python-3000 email (\"Py3.0 Library Ideas\")
    <https://mail.python.org/pipermail/python-3000/2007-February/005726.html>
