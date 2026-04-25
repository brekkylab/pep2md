---
pep: 628
title: Add ``math.tau``
author:
- Alyssa Coghlan <ncoghlan@gmail.com>
status: Final
type: Standards Track
created: 28-Jun-2011
python_version: '3.6'
post_history:
- 28-Jun-2011
python_status: Final
url: https://peps.python.org/pep-0628/
source_path: https://github.com/python/peps/blob/main/peps/pep-0628.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:40+00:00'
---

# Abstract

In honour of Tau Day 2011, this PEP proposes the addition of the circle
constant `math.tau` to the Python standard library.

The concept of `tau` (`τ`) is based on the observation that the ratio of
a circle\'s circumference to its radius is far more fundamental and
interesting than the ratio between its circumference and diameter. It is
simply a matter of assigning a name to the value `2 * pi` (`2π`).

# PEP Acceptance

This PEP is now [accepted](https://bugs.python.org/issue12345#msg272287)
and `math.tau` will be a part of Python 3.6. Happy birthday Alyssa!

The idea in this PEP has been implemented in the auspiciously named
[issue 12345](https://bugs.python.org/issue12345).

# The Rationale for Tau

`pi` is defined as the ratio of a circle\'s circumference to its
diameter. However, a circle is defined by its centre point and its
*radius*. This is shown clearly when we note that the parameter of
integration to go from a circle\'s circumference to its area is the
radius, not the diameter. If we use the diameter instead we have to
divide by four to get rid of the extraneous multiplier.

When working with radians, it is trivial to convert any given fraction
of a circle to a value in radians in terms of `tau`. A quarter circle is
`tau/4`, a half circle is `tau/2`, seven 25ths is `7*tau/25`, etc. In
contrast with the equivalent expressions in terms of `pi` (`pi/2`, `pi`,
`14*pi/25`), the unnecessary and needlessly confusing multiplication by
two is gone.

# Other Resources

I\'ve barely skimmed the surface of the many examples put forward to
point out just how much *easier* and more *sensible* many aspects of
mathematics become when conceived in terms of `tau` rather than `pi`. If
you don\'t find my specific examples sufficiently persuasive, here are
some more resources that may be of interest:

- Michael Hartl is the primary instigator of Tau Day in his [Tau
  Manifesto](https://tauday.com/)
- Bob Palais, the author of the original mathematics journal article
  highlighting the problems with `pi` has [a page of
  resources](https://www.math.utah.edu/~palais/pi.html) on the topic
- For those that prefer videos to written text, [Pi is
  wrong!](https://www.youtube.com/watch?v=PIhNNnW1tUo) and [Pi is
  (still) wrong](https://vimeo.com/147792667) are available.

# Copyright

This document has been placed in the public domain.
