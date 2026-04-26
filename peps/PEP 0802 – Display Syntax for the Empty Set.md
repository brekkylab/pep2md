---
pep: 802
title: Display Syntax for the Empty Set
author:
- Adam Turner <adam@python.org>
discussions_to: https://discuss.python.org/t/101676
status: Draft
type: Standards Track
created: 08-Aug-2025
python_version: '3.15'
post_history:
- '`08-Aug-2025 <https://discuss.python.org/t/101676>`__'
python_status: Draft
url: https://peps.python.org/pep-0802/
source_path: https://github.com/python/peps/blob/main/peps/pep-0802.rst
source_commit: fc27d63782cbd1bb24b4f14e97040fb9983c87d8
---

# Abstract

We propose a new notation, `{/}`, to construct and represent the empty
set. This is modelled after the corresponding mathematical symbol
\'$\emptyset$\'.

This complements the existing notation for empty tuples, lists, and
dictionaries, which use `()`, `[]`, and `{}` respectively.

# Motivation

Sets are currently the only built-in collection type that have a
`display syntax <python:comprehensions>`{.interpreted-text role="ref"},
but no notation to express an empty collection. The
`Python Language Reference <python:set>`{.interpreted-text role="ref"}
notes this, stating:

> An empty set cannot be constructed with `{}`; this literal constructs
> an empty dictionary.

This can be confusing for beginners, especially those coming to the
language from a scientific or mathematical background, where sets may be
in more common use than dictionaries or maps.

A syntax notation for the empty set has the important benefit of not
requiring a name lookup (unlike `set()`). `{/}` will always have a
consistent meaning, improving teachability of core concepts to
beginners. For example, users must be careful not to use `set` as a
local variable name, as doing so prevents constructing new sets. This
can be frustrating as beginners may not know how to recover the
`set`{.interpreted-text role="py:class"} type if they have overriden the
name. Techniques to do so (e.g. `type({1})`) are not immediately
obvious, especially to those learning the language, who may not yet be
familiar with the `python:type`{.interpreted-text role="py:class"}
function.

Finally, this may be helpful for users who do not speak English, as it
provides a culture-free notation for a common data structure that is
built into the language.

# Rationale

Sets were introduced to Python 2.2 via `218`{.interpreted-text
role="pep"}, which did not include set notation, but discussed the idea
of `{-}` for the empty set:

> The PEP originally proposed `{1,2,3}` as the set notation and `{-}`
> for the empty set. Experience with Python 2.3\'s `sets.py` showed that
> the notation was not necessary. Also, there was some risk of making
> dictionaries less instantly recognizable.

Python 3.0 introduced set literals (`3100`{.interpreted-text
role="pep"}), but again chose not to introduce notation for the empty
set, which was omitted out of pragmatism ([python-3000, April
2006](https://mail.python.org/pipermail/python-3000/2006-April/001286.html),
[python-3000, May
2006](https://mail.python.org/pipermail/python-3000/2006-May/001666.html)).

Since then, the topic has been discussed several times, with various
proposals, including:

1.  Changing `{}` to mean an empty set and using `{:}` for an empty
    dictionary ([python-ideas, January
    2008](https://mail.python.org/archives/list/python-ideas@python.org/thread/IBMTTESRSF5755LNMVTUMHHABKOBSPUZ/#IBMTTESRSF5755LNMVTUMHHABKOBSPUZ),
    [Discourse, March 2023](https://discuss.python.org/t/25213))
2.  A Unicode character (e.g. `∅` or `ϕ`) ([python-ideas, April
    2021](https://mail.python.org/archives/list/python-ideas@python.org/message/X4TX2HDNKDJ7PVZL3DVI5QD2MIMRHKO4/))
3.  `<>` ([python-ideas, November
    2010](https://mail.python.org/archives/list/python-ideas@python.org/thread/N7CHDYXW2FYHDJ5BTP7CCC5HLAIINOVH/#N7CHDYXW2FYHDJ5BTP7CCC5HLAIINOVH),
    [Discourse, December 2024](https://discuss.python.org/t/73235))
4.  `s{}` ([python-ideas, June
    2009](https://mail.python.org/archives/list/python-ideas@python.org/thread/AMWKPS54ZK6X2FI7NICDM6DG7LERIJFV/#AMWKPS54ZK6X2FI7NICDM6DG7LERIJFV))
5.  `{*()}`, perhaps optimising to compile this to the `BUILD_SET`
    opcode ([Discourse, August 2025
    (#37)](https://discuss.python.org/t/101197/37))
6.  `{-}` ([python-ideas, August
    2020](https://mail.python.org/archives/list/python-ideas@python.org/message/QOBONXUPUMC3ULCGJU6FVHOCIZQDT45W/))
7.  `(/)` ([Discourse, March 2023
    (#20)](https://discuss.python.org/t/25213/20))
8.  `{,}` ([Discourse, August
    2025](https://discuss.python.org/t/101197))
9.  `{/}` ([python-ideas, January
    2008](https://mail.python.org/archives/list/python-ideas@python.org/thread/IBMTTESRSF5755LNMVTUMHHABKOBSPUZ/#IBMTTESRSF5755LNMVTUMHHABKOBSPUZ))
10. `set()` (i.e. doing nothing)

The authors propose `{/}` as the notation, being in their opinion the
best of these options. It is simple and concise, with the benefit of
resembling the mathematical notation for the empty set, $\emptyset$.
This makes it an easier mnemonic to explain than several in the
language, such as `**` for exponentiation or `@` for matrix
multiplication.

The `{/}` notation was also the most popular in a [recent Discourse
poll](https://discuss.python.org/t/101197/15), selected by 41% of
respondents overall and 60% of those voting for a new syntax.

Brief summaries for the other proposals may be found in [Rejected
Ideas](#rejected-ideas).

# Specification

The grammar for set displays will become:

::: productionlist
python-grammar set_display: \"{\" (\"/\" \| flexible_expression_list \|
comprehension) \"}\"
:::

The parser will emit a specialised error message for `(/)` and `[/]`,
indicating that these are invalid syntax, and suggesting the correct
forms of the empty tuple and list respectively.

`{/}` will become the default syntax for the empty set.

``` python
>>> type({/})
<class 'set'>
>>> {/} == set()
True
```

The representation and string forms of the empty set will change to
`'{/}'`.

``` python
>>> repr({/})
'{/}'
>>> repr(set())
'{/}'
>>> str({/})
'{/}'
>>> str(set())
'{/}'
```

There will be no behavioural changes to `set`{.interpreted-text
role="py:class"} objects.

# Backwards Compatibility

Code that relies on the `repr()` or `str()` of the empty set will no
longer work, because the representation will change.

There will be no other backwards incompatibile changes, all current
constructors for the empty set will continue to work, and the behaviour
of the `set`{.interpreted-text role="py:class"} type will remain
unchanged.

Due to this, current code that uses `set()` will continue to work, and
can remain unchanged. Developers of automated tools such as linters and
formatters should avoid encouraging \'churn\' in existing projects by
suggesting changes en-masse from `set()` to `{/}`, unless explicitly
requested by the user of such tools.

# Security Implications

None.

# How to Teach This

All users can be taught that `{/}` is the new spelling for `set()`, and
that it is equivalent in all other ways. To help reinforce this, we will
update the documentation to use `{/}` instead of `set()`, including the
tutorial, standard libary modules, and the Python Language Reference.

For new users, sets can be introduced through syntax, noting that the
four built-in collection types with syntax all have empty forms: `()`,
`[]`, `{/}`, and `{}`.

The empty set uses a forwards slash to differentiate it from an empty
dictionary. It uses this syntax because it looks like the mathematical
symbol for the empty set (\'$\emptyset$\'). This can be used as a
helpful mnemonic when teaching beginners, especially those that have a
maths or science background.

# Reference Implementation

A reference implementation of this PEP exists as a pull request in the
CPython repository on Github:
[python/cpython#137565](https://github.com/python/cpython/pull/137565).

# Rejected Ideas

## Change `{}` to mean an empty set and use `{:}` for an empty dictionary

This would be an entirely backwards incompatible change, all current
empty `dict`{.interpreted-text role="py:class"} objects would become
sets.

## Use a Unicode character (e.g. `∅` or `ϕ`)

The Unicode character \'U+2205 ∅ EMPTY SET\' is not currently a valid
identifier. Introducing a Unicode character as syntax would be hard to
use, as it does not appear on standard keyboards.

Using other characters that look like ∅, such as \'U+03C6 ϕ GREEK SMALL
LETTER PHI\' or \'U+00D8 Ø LATIN CAPITAL LETTER O WITH STROKE\', would
be more confusing with the same drawbacks of using a Unicode character.

## Use the `<>` syntax

It does not have a resemblance to the syntax for non-empty sets. This
would be harder to explain than this PEP\'s proposal.

This syntax further has historic use as the inequality operator, which
can still be accessed via `from __future__ import barry_as_FLUFL`. Using
both the `barry_as_FLUFL` future import and `<>` for the empty set would
lead to parser ambiguity: what would `<> <> <>` mean?

## Use the `s{}` syntax

This syntax may cause confusion with `s` as a local variable. The only
current use of prefixes of this kind is for string literals. This would
be harder to explain than this PEP\'s proposal.

## Use the `{*()}` syntax

This relies on unpacking the empty tuple into a set, creating an empty
set. This has the benefit of support since Python 3.5
(`448`{.interpreted-text role="pep"}).

Explaining this notation requires understanding sequence unpacking, the
empty tuple, set literal syntax, and the concept of unpacking an empty
sequence, producing no values to unpack.

This is an unwieldy syntax; not one that can be easily taught to
beginners. We should avoid introducing complex notation with the proviso
that users will understand it later, or that it can be looked up online.
This removes agency from the learner. Especially when using a
programming language that can execute arbitrary code, it is important
that users understand what the code they are writing does.

In the authors\' opinion, it would be a misttep to promote `{*()}` as
the syntax for an empty set. It resulted as a side-effect of
`448`{.interpreted-text role="pep"}, rather than an intentional attempt
to design a syntax that is easy to teach, understand, and explain.

## Use the `{-}` syntax

This syntax was originally proposed in `218`{.interpreted-text
role="pep"}, but removed from the PEP before it was accepted. The
authors prefer `{/}` due to the resemblance to $\emptyset$.

## Use the `(/)` syntax

This notation has been suggested as a better visual resemlence of the
empty set symbol (e.g. U+2205 ∅ EMPTY SET). However, it is a complete
departure from the regular set syntax. To the authors, any of the
proposed notations with curly brackets are better than this proposal, as
they are more consistent with the current (since Python 3.0) set
notation.

The authors prefer `{/}` because it combines the benefits of visual
resemblance to the mathematical symbol and to the existing set syntax,
unlike `(/)`.

## Use the `{,}` syntax

This is the authors\' next preferred option. However, if a single comma
were to be used to represent an empty collection, it may be confusing
why this could not be used for empty tuples or lists. In time, there
might be proposals to add support for `[,]` and `(,)`. This conflicts
with the general principle that \'\*there should be one\-- and
preferably only one \--obvious way to do it\*\'. Having a visibly
different form, in `{/}`, helps to reinforce the idea that the syntax
for the empty set is a special case, rather than a general rule for all
empty collections.

## Create and use a new token for `'{/}'`

There have been [previous
proposals](https://discuss.python.org/t/73235/66) to create a new token
for this construct. This would require `'{/}'` to be written literally,
with no whitespace between the characters.

We insted chose to allow whitespace between the brackets and the slash,
treating `{`, `/`, and `}` as three distinct tokens, as we cannot see
any reason to prevent it. However, we expect that the vast majority of
uses will not include whitespace.

# Open Issues

None.

# Acknowledgements

- Chris Angelico, Dominykas Grigonis, Ben Hsing, James Webber, and other
  contributors to recent Discourse topics.
- Hugo van Kemenade, for helpful feedback on a draft of the PEP.

# Footnotes

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
