---
pep: 515
title: Underscores in Numeric Literals
author:
- Georg Brandl
- Serhiy Storchaka
status: Final
type: Standards Track
created: 10-Feb-2016
python_version: '3.6'
post_history:
- 10-Feb-2016
- 11-Feb-2016
python_status: Final
url: https://peps.python.org/pep-0515/
source_path: https://github.com/python/peps/blob/main/peps/pep-0515.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:34+00:00'
---

# Abstract and Rationale

This PEP proposes to extend Python\'s syntax and number-from-string
constructors so that underscores can be used as visual separators for
digit grouping purposes in integral, floating-point and complex number
literals.

This is a common feature of other modern languages, and can aid
readability of long literals, or literals whose value should clearly
separate into parts, such as bytes or words in hexadecimal notation.

Examples:

    # grouping decimal numbers by thousands
    amount = 10_000_000.0

    # grouping hexadecimal addresses by words
    addr = 0xCAFE_F00D

    # grouping bits into nibbles in a binary literal
    flags = 0b_0011_1111_0100_1110

    # same, for string conversions
    flags = int('0b_1111_0000', 2)

# Specification

The current proposal is to allow one underscore between digits, and
after base specifiers in numeric literals. The underscores have no
semantic meaning, and literals are parsed as if the underscores were
absent.

## Literal Grammar

The production list for integer literals would therefore look like this:

    integer: decinteger | bininteger | octinteger | hexinteger
    decinteger: nonzerodigit (["_"] digit)* | "0" (["_"] "0")*
    bininteger: "0" ("b" | "B") (["_"] bindigit)+
    octinteger: "0" ("o" | "O") (["_"] octdigit)+
    hexinteger: "0" ("x" | "X") (["_"] hexdigit)+
    nonzerodigit: "1"..."9"
    digit: "0"..."9"
    bindigit: "0" | "1"
    octdigit: "0"..."7"
    hexdigit: digit | "a"..."f" | "A"..."F"

For floating-point and complex literals:

    floatnumber: pointfloat | exponentfloat
    pointfloat: [digitpart] fraction | digitpart "."
    exponentfloat: (digitpart | pointfloat) exponent
    digitpart: digit (["_"] digit)*
    fraction: "." digitpart
    exponent: ("e" | "E") ["+" | "-"] digitpart
    imagnumber: (floatnumber | digitpart) ("j" | "J")

## Constructors

Following the same rules for placement, underscores will be allowed in
the following constructors:

- `int()` (with any base)
- `float()`
- `complex()`
- `Decimal()`

## Further changes

The new-style number-to-string formatting language will be extended to
allow `_` as a thousands separator, where currently only `,` is
supported. This can be used to easily generate code with more readable
literals.[^1]

The syntax would be the same as for the comma, e.g. `{:10_}` for a width
of 10 with `_` separator.

For the `b`, `x` and `o` format specifiers, `_` will be allowed and
group by 4 digits.

# Prior Art

Those languages that do allow underscore grouping implement a large
variety of rules for allowed placement of underscores. In cases where
the language spec contradicts the actual behavior, the actual behavior
is listed. (\"single\" or \"multiple\" refer to allowing runs of
consecutive underscores.)

- Ada: single, only between digits[^2]
- C# (open proposal for 7.0): multiple, only between digits[^3]
- C++14: single, between digits (different separator chosen)[^4]
- D: multiple, anywhere, including trailing[^5]
- Java: multiple, only between digits[^6]
- Julia: single, only between digits (but not in float exponent parts)
  [^7]
- Perl 5: multiple, basically anywhere, although docs say it\'s
  restricted to one underscore between digits[^8]
- Ruby: single, only between digits (although docs say \"anywhere\")
  [^9]
- Rust: multiple, anywhere, except for between exponent \"e\" and digits
  [^10]
- Swift: multiple, between digits and trailing (although textual
  description says only \"between digits\")[^11]

# Alternative Syntax

## Underscore Placement Rules

Instead of the relatively strict rule specified above, the use of
underscores could be less limited. As seen in other languages, common
rules include:

- Only one consecutive underscore allowed, and only between digits.
- Multiple consecutive underscores allowed, but only between digits.
- Multiple consecutive underscores allowed, in most positions except for
  the start of the literal, or special positions like after a decimal
  point.

The syntax in this PEP has ultimately been selected because it covers
the common use cases, and does not allow for syntax that would have to
be discouraged in style guides anyway.

A less common rule would be to allow underscores only every N digits
(where N could be 3 for decimal literals, or 4 for hexadecimal ones).
This is unnecessarily restrictive, especially considering the separator
placement is different in different cultures.

## Different Separators

A proposed alternate syntax was to use whitespace for grouping. Although
strings are a precedent for combining adjoining literals, the behavior
can lead to unexpected effects which are not possible with underscores.
Also, no other language is known to use this rule, except for languages
that generally disregard any whitespace.

C++14 introduces apostrophes for grouping (because underscores introduce
ambiguity with user-defined literals), which is not considered because
of the use in Python\'s string literals.[^12]

# Implementation

A preliminary patch that implements the specification given above has
been posted to the issue tracker.[^13]

# References

# Copyright

This document has been placed in the public domain.

[^1]: <https://mail.python.org/pipermail/python-dev/2016-February/143283.html>

[^2]: <http://archive.adaic.com/standards/83lrm/html/lrm-02-04.html#2.4>

[^3]: <https://github.com/dotnet/roslyn/issues/216>

[^4]: <http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3499.html>

[^5]: <https://dlang.org/spec/lex.html#integerliteral>

[^6]: <https://docs.oracle.com/javase/7/docs/technotes/guides/language/underscores-literals.html>

[^7]: <https://web.archive.org/web/20160223175334/http://docs.julialang.org/en/release-0.4/manual/integers-and-floating-point-numbers/>

[^8]: <https://perldoc.perl.org/perldata#Scalar-value-constructors>

[^9]: <https://ruby-doc.org/core-2.3.0/doc/syntax/literals_rdoc.html#label-Numbers>

[^10]: <https://web.archive.org/web/20160304121349/http://doc.rust-lang.org/reference.html#integer-literals>

[^11]: <https://docs.swift.org/swift-book/ReferenceManual/LexicalStructure.html>

[^12]: <http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3499.html>

[^13]: <http://bugs.python.org/issue26331>
