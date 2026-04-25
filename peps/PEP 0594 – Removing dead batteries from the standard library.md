---
pep: 594
title: Removing dead batteries from the standard library
author:
- Christian Heimes <christian@python.org>
- Brett Cannon <brett@python.org>
discussions_to: https://discuss.python.org/t/13508
status: Final
type: Standards Track
created: 20-May-2019
python_version: '3.11'
post_history:
- 21-May-2019
- 04-Feb-2022
resolution: https://discuss.python.org/t/13508/22
python_status: Final
url: https://peps.python.org/pep-0594/
source_path: https://github.com/python/peps/blob/main/peps/pep-0594.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:38+00:00'
---

# Abstract

This PEP proposed a list of standard library modules to be removed from
the standard library. The modules are mostly historic data formats (e.g.
Commodore and SUN file formats), APIs and operating systems that have
been superseded a long time ago (e.g. Mac OS 9), or modules that have
security implications and better alternatives (e.g. password and login).

The PEP follows in the footsteps of other PEPS like
`3108`{.interpreted-text role="pep"}. The *Standard Library
Reorganization* proposal removed a bunch of modules from Python 3.0. In
2007, the PEP referred to maintenance burden as:

> \"Over the years, certain modules have become a heavy burden upon
> python-dev to maintain. In situations like this, it is better for the
> module to be given to the community to maintain to free python-dev to
> focus more on language support and other modules in the standard
> library that do not take up an undue amount of time and effort.\"

The withdrawn `206`{.interpreted-text role="pep"} from 2000 expresses
issues with the Python standard library in an unvarnished and forthright
manner:

> \"\[\...\] the standard library modules aren\'t always the best
> choices for a job. Some library modules were quick hacks (e.g.
> `calendar`, `commands`), some were designed poorly and are now
> near-impossible to fix (`cgi`), and some have been rendered obsolete
> by other, more complete modules \[\...\].\"

# Rationale

Back in the early days of Python, the interpreter came with a large set
of useful modules. This was often referred to as \"batteries included\"
philosophy and was one of the cornerstones to Python\'s success story.
Users didn\'t have to figure out how to download and install separate
packages in order to write a simple web server or parse email.

Times have changed. With the introduction of PyPI (née Cheeseshop),
setuptools, and later pip, it became simple and straightforward to
download and install packages. Nowadays Python has a rich and vibrant
ecosystem of third-party packages. It\'s pretty much standard to either
install packages from PyPI or use one of the many Python or Linux
distributions.

On the other hand, Python\'s standard library is piling up with cruft,
unnecessary duplication of functionality, and dispensable features. This
is undesirable for several reasons.

- Any additional module increases the maintenance cost for the Python
  core development team. The team has limited resources, reduced
  maintenance cost frees development time for other improvements.
- Modules in the standard library are generally favored and seen as the
  de facto solution for a problem. A majority of users only pick
  third-party modules to replace a stdlib module, when they have a
  compelling reason, e.g. `lxml` instead of `xml`. The removal of an
  unmaintained stdlib module increases the chances of a
  community-contributed module to become widely used.
- A lean and mean standard library benefits platforms with limited
  resources like devices with just a few hundred kilobyte of storage
  (e.g. BBC Micro:bit). Python on mobile platforms like BeeWare or
  WebAssembly (e.g. pyodide) also benefit from reduced download size.

The modules in this PEP have been selected for deprecation because their
removal is either least controversial or most beneficial. For example,
least controversial are 30-year-old multimedia formats like the `sunau`
audio format, which was used on SPARC and NeXT workstations in the late
1980s. The `crypt` module has fundamental flaws that are better solved
outside the standard library.

This PEP also designates some modules as not scheduled for removal. Some
modules have been deprecated for several releases or seem unnecessary at
first glance. However it is beneficial to keep the modules in the
standard library, mostly for environments where installing a package
from PyPI is not an option. This can be corporate environments or
classrooms where external code is not permitted without legal approval.

- The usage of FTP is declining, but some files are still provided over
  the FTP protocol or hosters offer FTP to upload content. Therefore,
  `ftplib` is going to stay.
- The `optparse` and `getopt` modules are widely used. They are mature
  modules with very low maintenance overhead.
- According to David Beazley[^1] the `wave` module is easy to teach to
  kids and can make crazy sounds. Making a computer generate sounds is a
  powerful and highly motivating exercise for a nine-year-old aspiring
  developer. It\'s a fun battery to keep.

# Deprecation schedule

## 3.11

Starting with Python 3.11, deprecated modules will start issuing
`DeprecationWarning`. The estimated EOL of Python 3.10, the last version
without the warning, is October 2026.

## 3.12

There should be no specific change compared to Python 3.11. This is the
last version of Python with the deprecated modules, with an estimated
EOL of October 2028.

## 3.13

All modules deprecated by this PEP are removed from the `main` branch of
the CPython repository and are no longer distributed as part of Python.

# Deprecated modules

The modules are grouped as data encoding, multimedia, network, OS
interface, and misc modules. The majority of modules are for old data
formats or old APIs. Some others are rarely useful and have better
replacements on PyPI, e.g. Pillow for image processing or NumPy-based
projects to deal with audio processing.

  ------------------------------------------------------------------------------------------------------
  Module            Deprecated   To be     Added in    Has            Replacement
                    in           removed               maintainer?    
  ----------------- ------------ --------- ----------- -------------- ----------------------------------
  aifc              3.11 (3.0\*) 3.13      1993        **yes          \-
                                                       (inactive)**   

  asynchat          **3.6**      3.12      1999        **yes**        `asyncio`{.interpreted-text
                    (3.0\*)                                           role="mod"}

  asyncore          **3.6**      3.12      1999        **yes**        `asyncio`{.interpreted-text
                    (3.0\*)                                           role="mod"}

  audioop           3.11 (3.0\*) 3.13      1992        **yes**        \-

  cgi               3.11         3.13      1995        no             \-
                    (2.0\*\*)                                         

  cgitb             3.11         3.13      1995        no             \-
                    (2.0\*\*)                                         

  chunk             3.11         3.13      1999        no             \-

  crypt             3.11         3.13      1994        **yes          `legacycrypt`{.interpreted-text
                                                       (inactive)**   role="pypi"},
                                                                      `bcrypt`{.interpreted-text
                                                                      role="pypi"},
                                                                      `argon2-cffi`{.interpreted-text
                                                                      role="pypi"},
                                                                      `hashlib`{.interpreted-text
                                                                      role="mod"},
                                                                      `passlib`{.interpreted-text
                                                                      role="pypi"}

  imghdr            3.11         3.13      1992        no             `filetype`{.interpreted-text
                                                                      role="pypi"},
                                                                      `puremagic`{.interpreted-text
                                                                      role="pypi"},
                                                                      `python-magic`{.interpreted-text
                                                                      role="pypi"}

  mailcap           3.11         3.13      1995        no             \-

  msilib            3.11         3.13      2006        no             \-

  nntplib           3.11         3.13      1992        no             \-

  nis               3.11 (3.0\*) 3.13      1992        no             \-

  ossaudiodev       3.11         3.13      2002        no             \-

  pipes             3.11         3.13      1992        no             `subprocess`{.interpreted-text
                                                                      role="mod"}

  smtpd             **3.4.7**,   3.12      2001        **yes**        `aiosmtpd`{.interpreted-text
                    **3.5.4**                                         role="pypi"}

  sndhdr            3.11         3.13      1994        no             `filetype`{.interpreted-text
                                                                      role="pypi"},
                                                                      `puremagic`{.interpreted-text
                                                                      role="pypi"},
                                                                      `python-magic`{.interpreted-text
                                                                      role="pypi"}

  spwd              3.11         3.13      2005        no             `python-pam`{.interpreted-text
                                                                      role="pypi"}

  sunau             3.11 (3.0\*) 3.13      1993        no             \-

  telnetlib         3.11 (3.0\*) 3.13      1997        no             `telnetlib3`{.interpreted-text
                                                                      role="pypi"},
                                                                      `Exscript`{.interpreted-text
                                                                      role="pypi"}

  uu                3.11         3.13      1994        no             \-

  xdrlib            3.11         3.13      1992/1996   no             \-
  ------------------------------------------------------------------------------------------------------

  : Table 1: Proposed modules deprecations

Some module deprecations proposed by `3108`{.interpreted-text
role="pep"} for 3.0 and `206`{.interpreted-text role="pep"} for 2.0. The
*added in* column illustrates, when a module was originally designed and
added to the standard library. The *has maintainer* column refers to the
[expert index](https://devguide.python.org/experts/), a list of domain
experts and maintainers in the DevGuide.

## Data encoding modules

### uu and the uu encoding

The `uu`{.interpreted-text role="external+py3.12:mod"} module provides
uuencode format, an old binary encoding format for email from 1980. The
uu format has been replaced by MIME. The uu codec is provided by the
`binascii` module. There\'s also `encodings/uu_codec.py` which is a
codec for the same encoding; it should also be deprecated.

### xdrlib

The `xdrlib`{.interpreted-text role="external+py3.12:mod"} module
supports the Sun External Data Representation Standard. XDR is an old
binary serialization format from 1987. These days it\'s rarely used
outside specialized domains like NFS.

## Multimedia modules

### aifc

The `aifc`{.interpreted-text role="external+py3.12:mod"} module provides
support for reading and writing AIFF and AIFF-C files. The Audio
Interchange File Format is an old audio format from 1988 based on Amiga
IFF. It was most commonly used on the Apple Macintosh. These days only
few specialized application use AIFF.

A user disclosed[^2] that the post production film industry makes heavy
use of the AIFC file format. The usage of the `aifc` module in closed
source and internal software was unknown prior to the first posting of
this PEP. This may be a compelling argument to keep the `aifc` module in
the standard library. The file format is stable and the module does not
require much maintenance. The strategic benefits for Python may outmatch
the burden.

### audioop

The `audioop`{.interpreted-text role="external+py3.12:mod"} module
contains helper functions to manipulate raw audio data and adaptive
differential pulse-code modulated audio data. The module is implemented
in C without any additional dependencies. The [aifc](#aifc),
[sunau](#sunau), and [wave](#wave) modules depend on [audioop](#audioop)
for some operations.

The byteswap operation in the `wave` module can be substituted with
little extra work. In case `aifc` is not deprecated as well, a reduced
version of the `audioop` module is converted into a private
implementation detail, e.g. `_audioop` with `byteswap`, `alaw2lin`,
`ulaw2lin`, `lin2alaw`, `lin2ulaw`, and `lin2adpcm`.

### chunk

The `chunk`{.interpreted-text role="external+py3.12:mod"} module
provides support for reading and writing Electronic Arts\' Interchange
File Format. IFF is an old audio file format originally introduced for
Commodore and Amiga. The format is no longer relevant.

### imghdr

The `imghdr`{.interpreted-text role="external+py3.12:mod"} module is a
simple tool to guess the image file format from the first 32 bytes of a
file or buffer. It supports only a limited number of formats and neither
returns resolution nor color depth.

### ossaudiodev

The `ossaudiodev`{.interpreted-text role="external+py3.12:mod"} module
provides support for Open Sound System, an interface to sound playback
and capture devices. OSS was initially free software, but later support
for newer sound devices and improvements were proprietary. Linux
community abandoned OSS in favor of ALSA[^3]. Some operating systems
like OpenBSD and NetBSD provide an incomplete[^4] emulation of OSS.

To best of my knowledge, FreeBSD is the only widespread operating system
that uses Open Sound System as of today. The `ossaudiodev` hasn\'t seen
any improvements or new features since 2003. All commits since 2003 are
project-wide code cleanups and a couple of bug fixes. It would be
beneficial for both FreeBSD community and core development, if the
module would be maintained and distributed by people that care for it
and use it.

The standard library used to have more audio-related modules. The other
audio device interfaces (`audiodev`, `linuxaudiodev`, `sunaudiodev`)
were removed in 2007 as part of the `3108`{.interpreted-text role="pep"}
stdlib re-organization.

### sndhdr

The `sndhdr`{.interpreted-text role="external+py3.12:mod"} module is
similar to the [imghdr](#imghdr) module but for audio formats. It
guesses file format, channels, frame rate, and sample widths from the
first 512 bytes of a file or buffer. The module only supports AU, AIFF,
HCOM, VOC, WAV, and other ancient formats.

### sunau

The `sunau`{.interpreted-text role="external+py3.12:mod"} module
provides support for Sun AU sound format. It\'s yet another old,
obsolete file format.

## Networking modules

### asynchat

The `asynchat`{.interpreted-text role="external+py3.11:mod"} module is
built on top of `asyncore`{.interpreted-text role="external+py3.11:mod"}
and has been deprecated since Python 3.6.

### asyncore

The `asyncore`{.interpreted-text role="external+py3.11:mod"} module was
the first module for asynchronous socket service clients and servers. It
has been replaced by asyncio and is deprecated since Python 3.6.

The `asyncore` module is also used in stdlib tests. The tests for
`ftplib`, `logging`, `smptd`, `smtplib`, and `ssl` are partly based on
`asyncore`. These tests must be updated to use asyncio or threading.

### cgi

The `cgi`{.interpreted-text role="external+py3.12:mod"} module is a
support module for Common Gateway Interface (CGI) scripts. CGI is deemed
as inefficient because every incoming request is handled in a new
process. `206`{.interpreted-text role="pep"} considers the module as:

> \"\[\...\] designed poorly and are now near-impossible to fix (`cgi`)
> \[\...\]\"

Replacements for the various parts of `cgi` which are not directly
related to executing code are:

- `parse` with `urllib.parse.parse_qs` (`parse` is just a wrapper)
- `parse_header` with `email.message.Message` (see example below)
- `parse_multipart` with `email.message.Message` (same MIME RFCs)
- `FieldStorage`/`MiniFieldStorage` has no direct replacement, but can
  typically be replaced by using `multipart`{.interpreted-text
  role="pypi"} (for `POST` and `PUT` requests) or
  `urllib.parse.parse_qsl` (for `GET` and `HEAD` requests)
- `valid_boundary` (undocumented) with
  `re.compile("^[ -~]{0,200}[!-~]$")`

As an explicit example of how close `parse_header` and
`email.message.Message` are:

``` pycon
>>> from cgi import parse_header
>>> from email.message import Message
>>> parse_header(h)
('application/json', {'charset': 'utf8'})
>>> m = Message()
>>> m['content-type'] = h
>>> m.get_params()
[('application/json', ''), ('charset', 'utf8')]
>>> m.get_param('charset')
'utf8'
```

### cgitb

The `cgitb`{.interpreted-text role="external+py3.12:mod"} module is a
helper for the `cgi` module for configurable tracebacks.

The `cgitb` module is not used by any major Python web framework
(Django, Pyramid, Plone, Flask, CherryPy, or Bottle). Only Paste uses it
in an optional debugging middleware.

### smtpd

The `smtpd`{.interpreted-text role="external+py3.11:mod"} module
provides a simple implementation of a SMTP mail server. The module
documentation marks the module as deprecated and recommends `aiosmtpd`
instead. The deprecation message was added in releases 3.4.7, 3.5.4, and
3.6.1.

### nntplib

The `nntplib`{.interpreted-text role="external+py3.12:mod"} module
implements the client side of the Network News Transfer Protocol (nntp).
News groups used to be a dominant platform for online discussions. Over
the last two decades, news has been slowly but steadily replaced with
mailing lists and web-based discussion platforms. Twisted is also
[planning](https://github.com/twisted/twisted/issues/9405) to deprecate
NNTP support and [pynntp](https://github.com/greenbender/pynntp) hasn\'t
seen any activity since 2014. This is a good indicator that the public
interest in NNTP support is declining.

The `nntplib` tests have been the cause of additional work in the recent
past. Python only contains the client side of NNTP, so the tests connect
to external news servers. The servers are sometimes unavailable, too
slow, or do not work correctly over IPv6. The situation causes flaky
test runs on buildbots.

### telnetlib

The `telnetlib`{.interpreted-text role="external+py3.12:mod"} module
provides a Telnet class that implements the Telnet protocol.

## Operating system interface

### crypt

The `crypt`{.interpreted-text role="external+py3.12:mod"} module
implements password hashing based on the `crypt(3)` function from
`libcrypt` or `libxcrypt` on Unix-like platforms. The algorithms are
mostly old, of poor quality and insecure. Users are discouraged from
using them.

- The module is not available on Windows. Cross-platform applications
  need an alternative implementation anyway.
- Only DES encryption is guaranteed to be available. DES has an
  extremely limited key space of 2\*\*56.
- MD5, salted SHA256, salted SHA512, and Blowfish are optional
  extensions. SSHA256 and SSHA512 are glibc extensions. Blowfish
  (bcrypt) is the only algorithm that is still secure. However it\'s in
  glibc and therefore not commonly available on Linux.
- Depending on the platform, the `crypt` module is not thread safe. Only
  implementations with `crypt_r(3)` are thread safe.
- The module was never useful to interact with system user and password
  databases. On BSD, macOS, and Linux, all user authentication and
  password modification operations must go through PAM (pluggable
  authentication module); see the [spwd](#spwd) deprecation.

### nis

The `nis`{.interpreted-text role="external+py3.12:mod"} module provides
NIS/YP support. Network Information Service / Yellow Pages is an old and
deprecated directory service protocol developed by Sun Microsystems. Its
designed successor NIS+ from 1992 never took off. For a long time,
libc\'s Name Service Switch, LDAP, and Kerberos/GSSAPI have been
considered a more powerful and more secure replacement for NIS.

### spwd

The `spwd`{.interpreted-text role="external+py3.12:mod"} module provides
direct access to Unix shadow password database using non-standard APIs.

In general, it\'s a bad idea to use `spwd`. It circumvents system
security policies, does not use the PAM stack, and is only compatible
with local user accounts, because it ignores NSS. The use of the `spwd`
module for access control must be considered a *security bug*, as it
bypasses PAM\'s access control.

Furthermore, the `spwd` module uses the
[shadow(3)](https://man7.org/linux/man-pages/man3/shadow.3.html) APIs.
Functions like `getspnam(3)` access the `/etc/shadow` file directly.
This is dangerous and even forbidden for confined services on systems
with a security engine like SELinux or AppArmor.

## Misc modules

### mailcap

The `mailcap`{.interpreted-text role="external+py3.12:mod"} package
reads *mail capability* files to assist in handling a file attachment in
an email. In most modern operating systems the email client itself
handles reacting to file attachments. Operating systems also have their
own way to register handling files by their file name extension.
Finally, the module has
[CVE-2015-20107](https://nvd.nist.gov/vuln/detail/CVE-2015-20107) filed
against it while having no maintainer to help fix it.

### msilib

The `msilib`{.interpreted-text role="external+py3.12:mod"} package is a
Windows-only package. It supports the creation of Microsoft Installers
(MSI). The package also exposes additional APIs to create cabinet files
(CAB). The module is used to facilitate distutils to create MSI
installers with the `bdist_msi` command. In the past it was used to
create CPython\'s official Windows installer, too.

Microsoft is slowly moving away from MSI in favor of Windows 10 Apps
(AppX) as a new deployment model[^5].

### pipes

The `pipes`{.interpreted-text role="external+py3.12:mod"} module
provides helpers to pipe the input of one command into the output of
another command. The module is built on top of `os.popen`. Users are
encouraged to use the `subprocess`{.interpreted-text role="mod"} module
instead.

# Modules to keep

Some modules were originally proposed for deprecation but are no longer
listed as such in this PEP.

  -----------------------------------------------------------------------
  Module            Deprecated in     Replacement
  ----------------- ----------------- -----------------------------------
  colorsys          \-                colormath, colour, colorspacious,
                                      Pillow

  fileinput         \-                argparse

  getopt            \-                argparse, optparse

  optparse          **3.2**           argparse

  wave              \-                
  -----------------------------------------------------------------------

  : Table 2: Withdrawn deprecations

## colorsys

The `colorsys`{.interpreted-text role="external+py3.12:mod"} module
defines color conversion functions between RGB, YIQ, HSL, and HSV
coordinate systems.

Walter Dörwald, Petr Viktorin, and others requested to keep `colorsys`.
The module is useful to convert CSS colors between coordinate systems.
The implementation is simple, mature, and does not impose maintenance
overhead on core development.

The PyPI packages `colormath`, `colour`, and `colorspacious` provide
more and advanced features. The Pillow library is better suited to
transform images between color systems.

## fileinput

The `fileinput`{.interpreted-text role="external+py3.12:mod"} module
implements helpers to iterate over a list of files from `sys.argv`. The
module predates the `optparse` and `argparse` modules. The same
functionality can be implemented with the `argparse` module.

Several core developers expressed their interest to keep the module in
the standard library, as it is handy for quick scripts.

## getopt

The `getopt`{.interpreted-text role="external+py3.12:mod"} module mimics
C\'s `getopt()` option parser.

Although users are encouraged to use `argparse` instead, the `getopt`
module is still widely used. The module is small, simple, and handy for
C developers to write simple Python scripts.

## optparse

The `optparse`{.interpreted-text role="external+py3.12:mod"} module is
the predecessor of the `argparse` module.

Although it has been deprecated for many years, it\'s still too widely
used to remove it.

## wave

The `wave`{.interpreted-text role="external+py3.12:mod"} module provides
support for the WAV sound format.

The module is not deprecated, because the WAV format is still relevant
these days. The `wave` module is also used in education, e.g. to show
kids how to make noise with a computer.

The module uses one simple function from the [audioop](#audioop) module
to perform byte swapping between little and big endian formats. Before
24 bit WAV support was added, byte swap used to be implemented with the
`array` module. To remove `wave`\'s dependency on `audioop`, the byte
swap function could be either be moved to another module (e.g.
`operator`) or the `array` module could gain support for 24-bit (3-byte)
arrays.

# Discussions

- Elana Hashman and Alyssa Coghlan suggested to keep the `getopt`
  module.
- Berker Peksag proposed to deprecate and remove `msilib`.
- Brett Cannon recommended to delay active deprecation warnings and
  removal of modules like `imp` until Python 3.10. Version 3.8 will be
  released shortly before Python 2 reaches end-of-life. A delay reduced
  churn for users that migrate from Python 2 to 3.8.
- At one point, distutils was mentioned in the same sentence as this
  PEP. To avoid lengthy discussion and delay of the PEP, I decided
  against dealing with distutils. Deprecation of the distutils package
  will be handled by another PEP.
- Multiple people (Gregory P. Smith, David Beazley, Alyssa Coghlan,
  \...) convinced me to keep the [wave](#wave) module.[^6]
- Gregory P. Smith proposed to deprecate [nntplib](#nntplib).[^7]
- Andrew Svetlov mentioned the `socketserver` module is questionable.
  However it\'s used to implement `http.server` and `xmlrpc.server`. The
  stdlib doesn\'t have a replacement for the servers, yet.

# Rejected ideas

## Creating/maintaining a separate repo for the deprecated modules

It was previously proposed to create a separate repository containing
the deprecated modules packaged for installation. One of the PEP authors
went so far as to create a [demo
repository](https://github.com/tiran/legacylib). In the end, though, it
was decided that the added workload to create and maintain such a repo
officially wasn\'t justified, as the source code will continue to be
available in the CPython repository for people to vendor as necessary.
Similar work has also not been done when previous modules were
deprecated and removed, and it seemingly wasn\'t an undue burden on the
community.

# Update history

## Update 1

- Deprecate `parser` module
- Keep [fileinput](#fileinput) module
- Elaborate why `crypt` and `spwd` are dangerous and bad
- Improve sections for [cgitb](#cgitb), [colorsys](#colorsys),
  [nntplib](#nntplib), and [smtpd](#smtpd) modules
- The [colorsys](#colorsys), `crypt`, [imghdr](#imghdr),
  [sndhdr](#sndhdr), and `spwd` sections now list suitable substitutions
- Mention that `socketserver` is going to stay for `http.server` and
  `xmlrpc.server`
- The future maintenance section now states that the deprecated modules
  may be adopted by Python community members

## Update 2

- Keep `colorsys` module
- Add experts
- Redirect discussions to discuss.python.org
- Deprecate [telnetlib](#telnetlib)
- Deprecate compat32 policy of `email` package
- Add creation year to overview table
- Mention `206`{.interpreted-text role="pep"} and
  `3108`{.interpreted-text role="pep"}
- Update sections for `aifc`, `audioop`, `cgi`, and `wave`.

## Update 3

- Keep the legacy email API modules. Internal deprecations will be
  handled separately.

## Update 4

- Add Brett as a co-author.
- Retarget the PEP for Python 3.11.
- Examples of how to replace the relevant parts of `cgi` (thanks Martijn
  Pieters).

# References

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: <https://web.archive.org/web/20220420154535/https://twitter.com/dabeaz/status/1130278844479545351>

[^2]: <https://mail.python.org/pipermail/python-dev/2019-May/157634.html>

[^3]: <https://en.wikipedia.org/wiki/Open_Sound_System#History>

[^4]: <https://man.openbsd.org/ossaudio>

[^5]: <https://web.archive.org/web/20221206204209/https://blogs.msmvps.com/installsite/blog/2015/05/03/the-future-of-windows-installer-msi-in-the-light-of-windows-10-and-the-universal-windows-platform/>

[^6]: <https://twitter.com/ChristianHeimes/status/1130257799475335169>

[^7]: <https://twitter.com/ChristianHeimes/status/1130257799475335169>
