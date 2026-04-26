---
pep: 536
title: Final Grammar for Literal String Interpolation
author:
- Philipp Angerer <phil.angerer@gmail.com>
status: Withdrawn
type: Standards Track
created: 11-Dec-2016
python_version: '3.7'
post_history:
- '`18-Aug-2016 <https://mail.python.org/archives/list/python-ideas@python.org/thread/FOYKXOFWEINPVQSK2XGEHKXSTEVO5WWA/>`__'
- '`23-Dec-2016 <https://mail.python.org/archives/list/python-ideas@python.org/thread/YKKEA5NIMMKHZTMRE5UFHST4WQ4NN3XJ/>`__'
- '`15-Mar-2019 <https://mail.python.org/archives/list/python-dev@python.org/thread/N43O4KNLZW4U7YZC4NVPCETZIVRDUVU2/>`__'
resolution: https://discuss.python.org/t/pep-536-should-be-marked-as-rejected/35226/4
python_status: Withdrawn
url: https://peps.python.org/pep-0536/
source_path: https://github.com/python/peps/blob/main/peps/pep-0536.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:23+00:00'
---

# Abstract

`498`{.interpreted-text role="pep"} introduced Literal String
Interpolation (or "f-strings"). The expression portions of those
literals however are subject to certain restrictions. This PEP proposes
a formal grammar lifting those restrictions, promoting "f-strings" to "f
expressions" or f-literals.

This PEP expands upon the f-strings introduced by
`498`{.interpreted-text role="pep"}, so this text requires familiarity
with `498`{.interpreted-text role="pep"}.

# PEP Withdrawal

This PEP has been withdrawn in favour of `701`{.interpreted-text
role="pep"}. `701`{.interpreted-text role="pep"} addresses all important
points of this PEP.

# Terminology

This text will refer to the existing grammar as "f-strings", and the
proposed one as "f-literals".

Furthermore, it will refer to the `{}`-delimited expressions in
f-literals/f-strings as "expression portions" and the static string
content around them as "string portions".

# Motivation

The current implementation of f-strings in CPython relies on the
existing string parsing machinery and a post processing of its tokens.
This results in several restrictions to the possible expressions usable
within f-strings:

1.  It is impossible to use the quote character delimiting the f-string
    within the expression portion:

        >>> f'Magic wand: { bag['wand'] }'
                                     ^
        SyntaxError: invalid syntax

2.  A previously considered way around it would lead to escape sequences
    in executed code and is prohibited in f-strings:

        >>> f'Magic wand { bag[\'wand\'] } string'
        SyntaxError: f-string expression portion cannot include a backslash

3.  Comments are forbidden even in multi-line f-strings:

        >>> f'''A complex trick: {
        ... bag['bag']  # recursive bags!
        ... }'''
        SyntaxError: f-string expression part cannot include '#'

4.  Expression portions need to wrap `':'` and `'!'` in braces:

        >>> f'Useless use of lambdas: { lambda x: x*2 }'
        SyntaxError: unexpected EOF while parsing

These limitations serve no purpose from a language user perspective and
can be lifted by giving f-literals a regular grammar without exceptions
and implementing it using dedicated parse code.

# Rationale

The restrictions mentioned in [Motivation](#motivation) are non-obvious
and counter-intuitive unless the user is familiar with the f-literals'
implementation details.

As mentioned, a previous version of `498`{.interpreted-text role="pep"}
allowed escape sequences anywhere in f-strings, including as ways to
encode the braces delimiting the expression portions and in their code.
They would be expanded before the code is parsed, which would have had
several important ramifications:

#\. It would not be clear to human readers which portions are
Expressions and which are strings. Great material for an
"obfuscated/underhanded Python challenge" #. Syntax highlighters are
good in parsing nested grammar, but not in recognizing escape sequences.
ECMAScript 2016 (JavaScript) allows escape sequences in its
identifiers[^1] and the author knows of no syntax highlighter able to
correctly highlight code making use of this.

As a consequence, the expression portions would be harder to recognize
with and without the aid of syntax highlighting. With the new grammar,
it is easy to extend syntax highlighters to correctly parse and display
f-literals:

<pre><span style=color:#ff5500>f'Magic wand: </span><span style=color:#3daee9>{</span>bag[<span style=color:#bf0303>'wand'</span>]<span style=color:#3daee9>:^10}</span><span style=color:#ff5500>'</span></pre>

Highlighting expression portions with possible escape sequences would
mean to create a modified copy of all rules of the complete expression
grammar, accounting for the possibility of escape sequences in key
words, delimiters, and all other language syntax. One such duplication
would yield one level of escaping depth and have to be repeated for a
deeper escaping in a recursive f-literal. This is the case since no
highlighting engine known to the author supports expanding escape
sequences before applying rules to a certain context. Nesting contexts
however is a standard feature of all highlighting engines.

Familiarity also plays a role: Arbitrary nesting of expressions without
expansion of escape sequences is available in every single other
language employing a string interpolation method that uses expressions
instead of just variable names.[^2]

# Specification

`498`{.interpreted-text role="pep"} specified f-strings as the
following, but places restrictions on it:

    f ' <text> { <expression> <optional !s, !r, or !a> <optional : format specifier> } <text> ... '

All restrictions mentioned in the PEP are lifted from f-literals, as
explained below:

1.  Expression portions may now contain strings delimited with the same
    kind of quote that is used to delimit the f-literal.
2.  Backslashes may now appear within expressions just like anywhere
    else in Python code. In case of strings nested within f-literals,
    escape sequences are expanded when the innermost string is
    evaluated.
3.  Comments, using the `'#'` character, are possible only in multi-line
    f-literals, since comments are terminated by the end of the line
    (which makes closing a single-line f-literal impossible).
4.  Expression portions may contain `':'` or `'!'` wherever
    syntactically valid. The first `':'` or `'!'` that is not part of an
    expression has to be followed a valid coercion or format specifier.

A remaining restriction not explicitly mentioned by
`498`{.interpreted-text role="pep"} is line breaks in expression
portions. Since strings delimited by single `'` or `"` characters are
expected to be single line, line breaks remain illegal in expression
portions of single line strings.

:::: note
::: title
Note
:::

Is lifting of the restrictions sufficient, or should we specify a more
complete grammar?
::::

# Backwards Compatibility

f-literals are fully backwards compatible to f-strings, and expands the
syntax considered legal.

# Reference Implementation

TBD

# References

# Copyright

This document has been placed in the public domain.

[^1]: ECMAScript `IdentifierName` specification (
    <http://ecma-international.org/ecma-262/6.0/#sec-names-and-keywords>
    )

    Yes, `const cthulhu = { H̹̙̦̮͉̩̗̗ͧ̇̏̊̾Eͨ͆͒̆ͮ̃͏̷̮̣̫̤̣Cͯ̂͐͏̨̛͔̦̟͈̻O̜͎͍͙͚̬̝̣̽ͮ͐͗̀ͤ̍̀͢M̴̡̲̭͍͇̼̟̯̦̉̒͠Ḛ̛̙̞̪̗ͥͤͩ̾͑̔͐ͅṮ̴̷̷̗̼͍̿̿̓̽͐H̙̙̔̄͜\u0042: 42 }` is valid ECMAScript
    2016

[^2]: Wikipedia article on string interpolation (
    <https://en.wikipedia.org/wiki/String_interpolation> )
