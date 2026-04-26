---
pep: 663
title: Standardizing Enum str(), repr(), and format() behaviors
author:
- Ethan Furman <ethan@stoneleaf.us>
discussions_to: python-dev@python.org
status: Rejected
type: Informational
created: 30-Jun-2021
python_version: '3.11'
post_history:
- 20-Jul-2021
- 02-Nov-2021
resolution: https://mail.python.org/archives/list/python-dev@python.org/message/RN3WCRZSTQR55DOHJTZ2KIO6CZPJPCU7/
python_status: Rejected
url: https://peps.python.org/pep-0663/
source_path: https://github.com/python/peps/blob/main/peps/pep-0663.rst
source_commit: b4269b24f4308101504a87d3e3094a40af0ff4da
generated_at: '2026-04-26T03:34:27+00:00'
---

# Abstract

Update the `repr()`, `str()`, and `format()` of the various Enum types
to better match their intended purpose. For example, `IntEnum` will have
its `str()` change to match its `format()`, while a user-mixed int-enum
will have its `format()` match its `str()`. In all cases, an enum\'s
`str()` and `format()` will be the same (unless the user overrides
`format()`).

Add a global enum decorator which changes the `str()` and `repr()` (and
`format()`) of the decorated enum to be a valid global reference: i.e.
`re.IGNORECASE` instead of `<RegexFlag.IGNORECASE: 2>`.

# Motivation

Having the `str()` of `IntEnum` and `IntFlag` not be the value causes
bugs and extra work when replacing existing constants.

Having the `str()` and `format()` of an enum member be different can be
confusing.

The addition of `StrEnum` with its requirement to have its `str()` be
its `value` is inconsistent with other provided Enum\'s `str`.

The iteration of `Flag` members, which directly affects their `repr()`,
is inelegant at best, and buggy at worst.

# Rationale

Enums are becoming more common in the standard library; being able to
recognize enum members by their `repr()`, and having that `repr()` be
easy to parse, is useful and can save time and effort in understanding
and debugging code.

However, the enums with mixed-in data types (`IntEnum`, `IntFlag`, and
the new `StrEnum`) need to be more backwards compatible with the
constants they are replacing \-- specifically,
`str(replacement_enum_member) == str(original_constant)` should be true
(and the same for `format()`).

IntEnum, IntFlag, and StrEnum should be as close to a drop-in
replacement of existing integer and string constants as is possible.
Towards that goal, the `str()` output of each should be its inherent
value; e.g. if `Color` is an `IntEnum`:

    >>> Color.RED
    <Color.RED: 1>
    >>> str(Color.RED)
    '1'
    >>> format(Color.RED)
    '1'

Note that `format()` already produces the correct output, only `str()`
needs updating.

As much as possible, the `str()`, `repr()`, and `format()` of enum
members should be standardized across the standard library. However, up
to Python 3.10 several enums in the standard library have a custom
`str()` and/or `repr()`.

The `repr()` of Flag currently includes aliases, which it should not;
fixing that will, of course, already change its `repr()` in certain
cases.

# Specification

There are three broad categories of enum usage:

- simple: `Enum` or `Flag` a new enum class is created with no data type
  mixins
- drop-in replacement: `IntEnum`, `IntFlag`, `StrEnum` a new enum class
  is created which also subclasses `int` or `str` and uses `int.__str__`
  or `str.__str__`
- user-mixed enums and flags the user creates their own integer-,
  float-, str-, whatever-enums instead of using enum.IntEnum, etc.

There are also two styles:

- normal: the enumeration members remain in their classes and are
  accessed as `classname.membername`, and the class name shows in their
  `repr()` and `str()` (where appropriate)
- global: the enumeration members are copied into their module\'s global
  namespace, and their module name shows in their `repr()` and `str()`
  (where appropriate)

Some sample enums:

    # module: tools.py

    class Hue(Enum):  # or IntEnum
        LIGHT = -1
        NORMAL = 0
        DARK = +1

    class Color(Flag):  # or IntFlag
        RED = 1
        GREEN = 2
        BLUE = 4

    class Grey(int, Enum):  # or (int, Flag)
       BLACK = 0
       WHITE = 1

Using the above enumerations, the following two tables show the old and
new output (blank cells indicate no change):

+--------+----------+----------+---------------+------------+-----------------+
| style  | category            | enum repr()   | enum str() | enum format()   |
+--------+----------+----------+---------------+------------+-----------------+
| normal | simple   | 3.10     |               |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      |               |            |                 |
|        +----------+----------+---------------+------------+-----------------+
|        | user     | 3.10     |               |            | 1               |
|        | mixed    |          |               |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      |               |            | Grey.WHITE      |
|        +----------+----------+---------------+------------+-----------------+
|        | int      | 3.10     |               | Hue.LIGHT  |                 |
|        | drop-in  |          |               |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      |               | `-1`       |                 |
|        |          |          |               |            |                 |
|        |          |          |               | :          |                 |
+--------+----------+----------+---------------+------------+-----------------+
| global | simple   | 3.10     | \<Hue.LIGHT:  | Hue.LIGHT  | Hue.LIGHT       |
|        |          |          | -1\>          |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      | tools.LIGHT   | LIGHT      | LIGHT           |
|        +----------+----------+---------------+------------+-----------------+
|        | user     | 3.10     | \<Grey.WHITE: | Grey.WHITE | Grey.WHITE      |
|        | mixed    |          | 1             |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      | tools.WHITE   | WHITE      | WHITE           |
|        +----------+----------+---------------+------------+-----------------+
|        | int      | 3.10     | \<Hue.LIGHT:  | Hue.LIGHT  |                 |
|        | drop-in  |          | -1\>          |            |                 |
|        |          +----------+---------------+------------+-----------------+
|        |          | new      | tools.LIGHT   | `-1`       |                 |
|        |          |          |               |            |                 |
|        |          |          |               | :          |                 |
+--------+----------+----------+---------------+------------+-----------------+

+--------+---------+---------+------------------------+------------------------+------------------------+
| style  | category          | flag repr()            | flag str()             | flag format()          |
+--------+---------+---------+------------------------+------------------------+------------------------+
| normal | simple  | 3.10    | \<Color.RED\|GREEN:    | Color.RED\|GREEN       | Color.RED\|GREEN       |
|        |         |         | 3\>                    |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | \<Color(3):            | Color.RED\|Color.GREEN | Color.RED\|Color.GREEN |
|        |         |         | RED\|GREEN\>           |                        |                        |
|        +---------+---------+------------------------+------------------------+------------------------+
|        | user    | 3.10    | \<Grey.WHITE: 1\>      |                        | 1                      |
|        | mixed   |         |                        |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | \<Grey(1): WHITE\>     |                        | Grey.WHITE             |
|        +---------+---------+------------------------+------------------------+------------------------+
|        | int     | 3.10    | \<Color.RED\|GREEN:    | Color.RED\|GREEN       |                        |
|        | drop-in |         | 3\>                    |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | \<Color(3):            | 3                      |                        |
|        |         |         | RED\|GREEN\>           |                        |                        |
+--------+---------+---------+------------------------+------------------------+------------------------+
| global | simple  | 3.10    | \<Color.RED\|GREEN:    | Color.RED\|GREEN       | Color.RED\|GREEN       |
|        |         |         | 3\>                    |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | tools.RED\|tools.GREEN | RED\|GREEN             | RED\|GREEN             |
|        +---------+---------+------------------------+------------------------+------------------------+
|        | user    | 3.10    | \<Grey.WHITE: 1\>      | Grey.WHITE             | 1                      |
|        | mixed   |         |                        |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | tools.WHITE            | WHITE                  | WHITE                  |
|        +---------+---------+------------------------+------------------------+------------------------+
|        | int     | 3.10    | \<Color.RED\|GREEN:    | Color.RED\|GREEN       |                        |
|        | drop-in |         | 3\>                    |                        |                        |
|        |         +---------+------------------------+------------------------+------------------------+
|        |         | new     | tools.RED\|tools.GREEN | 3                      |                        |
+--------+---------+---------+------------------------+------------------------+------------------------+

These two tables show the final result:

+--------+-----------+---------------+------------+--------------------+
| style  | category  | enum repr()   | enum str() | enum format()      |
+--------+-----------+---------------+------------+--------------------+
| normal | simple    | \<Hue.LIGHT:  | Hue.LIGHT  | Hue.LIGHT          |
|        |           | -1\>          |            |                    |
|        +-----------+---------------+------------+--------------------+
|        | user      | \<Grey.WHITE: | Grey.WHITE | Grey.WHITE         |
|        | mixed     | 1\>           |            |                    |
|        +-----------+---------------+------------+--------------------+
|        | int       | \<Hue.LIGHT:  | `-1`       | `-1`               |
|        | drop-in   | -1\>          |            |                    |
|        |           |               | :          | :                  |
+--------+-----------+---------------+------------+--------------------+
| global | simple    | tools.LIGHT   | LIGHT      | LIGHT              |
|        +-----------+---------------+------------+--------------------+
|        | user      | tools.WHITE   | WHITE      | WHITE              |
|        | mixed     |               |            |                    |
|        +-----------+---------------+------------+--------------------+
|        | int       | tools.LIGHT   | `-1`       | `-1`               |
|        | drop-in   |               |            |                    |
|        |           |               | :          | :                  |
+--------+-----------+---------------+------------+--------------------+

+--------+----------+------------------------+------------------------+------------------------+
| style  | category | flag repr()            | flag str()             | flag format()          |
+--------+----------+------------------------+------------------------+------------------------+
| normal | simple   | \<Color(3):            | Color.RED\|Color.GREEN | Color.RED\|Color.GREEN |
|        |          | RED\|GREEN\>           |                        |                        |
|        +----------+------------------------+------------------------+------------------------+
|        | user     | \<Grey(1): WHITE\>     | Grey.WHITE             | Grey.WHITE             |
|        | mixed    |                        |                        |                        |
|        +----------+------------------------+------------------------+------------------------+
|        | int      | \<Color(3):            | 3                      | 3                      |
|        | drop-in  | RED\|GREEN\>           |                        |                        |
+--------+----------+------------------------+------------------------+------------------------+
| global | simple   | tools.RED\|tools.GREEN | RED\|GREEN             | RED\|GREEN             |
|        +----------+------------------------+------------------------+------------------------+
|        | user     | tools.WHITE            | WHITE                  | WHITE                  |
|        | mixed    |                        |                        |                        |
|        +----------+------------------------+------------------------+------------------------+
|        | int      | tools.RED\|tools.GREEN | 3                      | 3                      |
|        | drop-in  |                        |                        |                        |
+--------+----------+------------------------+------------------------+------------------------+

As can be seen, `repr()` is primarily affected by whether the members
are global, while `str()` is affected by being global or by being a
drop-in replacement, with the drop-in replacement status having a higher
priority. Also, the basic `repr()` and `str()` have changed for flags as
the old style was flawed.

# Backwards Compatibility

Backwards compatibility of stringified objects is not guaranteed across
major Python versions, and there will be backwards compatibility breaks
where software uses the `repr()`, `str()`, and `format()` output of
enums in tests, documentation, data structures, and/or code generation.

Normal usage of enum members will not change: `re.ASCII` can still be
used as `re.ASCII` and will still compare equal to `256`.

If the previous output needs to be maintained, for example to ensure
compatibility between different Python versions, software projects will
need to create their own enum base class with the appropriate methods
overridden.

Note that by changing the `str()` of the drop-in category, we will
actually prevent future breakage when `IntEnum`, et al, are used to
replace existing constants.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
