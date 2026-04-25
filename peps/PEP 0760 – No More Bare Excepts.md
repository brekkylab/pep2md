---
pep: 760
title: No More Bare Excepts
author:
- Pablo Galindo Salgado <pablogsal@python.org>
- Brett Cannon <brett@python.org>
status: Withdrawn
type: Standards Track
created: 02-Oct-2024
python_version: '3.14'
post_history:
- '`09-Oct-2024 <https://discuss.python.org/t/pep-760-no-more-bare-excepts/67182>`__'
python_status: Withdrawn
url: https://peps.python.org/pep-0760/
source_path: https://github.com/python/peps/blob/main/peps/pep-0760.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:46+00:00'
---

# Abstract

This PEP proposes disallowing bare `except:` clauses in Python\'s
exception-handling syntax. Currently, Python allows catching all
exceptions with a bare `except:` clause, which can lead to overly broad
exception handling and mask important errors. This PEP suggests
requiring explicit exception types in all except clauses, promoting more
precise and intentional error handling.

# Motivation

The current syntax allows for catching all exceptions with a bare
`except:` clause:

``` python
try:
    risky_operation()
except:
    handle_any_error()
```

While this syntax can be convenient for a \"catch all\" handler, it
often leads to poor coding practices:

1.  It can mask important errors that should be propagated.
2.  It makes debugging more difficult by catching and potentially hiding
    unexpected exceptions.
3.  It goes against the Python principle of explicit over implicit.

Various linters[^1][^2][^3] and style guides (including
`8`{.interpreted-text role="pep"})[^4][^5] [^6][^7] discourage bare
`except` clauses.

By requiring explicit exception types, we can encourage more thoughtful
and precise error handling:

``` python
try:
    risky_operation()
except Exception as e:
    handle_expected_error(e)
```

Another view of this problem is that bare except handlers are ambiguous
regarding the intended handling of terminating exceptions, as the
intention could have been either:

- Only catch non-terminating exceptions (`except Exception:`). If this
  was the intention, using a bare `except:` is an outright bug, since
  that isn\'t what it means.
- Catch all exceptions, including terminating ones
  (`except BaseException:`). using bare `except:` here it is at least
  correct, but readers need to check to be sure it isn\'t an instance of
  the first case.

Since both possible intentions have available unambiguous spellings, the
ambiguous form is redundant and that\'s why we propose to disallow it.

# Rationale

The decision to disallow bare except clauses is based on the following
considerations:

1.  Requiring specific exception types makes the programmer\'s
    intentions clear and encourages thinking about what exceptions might
    occur.
2.  Catching only specific exceptions makes identifying and debugging
    unexpected errors easier.
3.  Preventing overly broad exception handling reduces the risk of
    silently ignoring critical errors.
4.  Many style guides and linters already discourage the use of bare
    except clauses.

# Specification

The syntax for the except clause will be modified to require an
exception type. The grammar will be updated to remove the possibility of
adding an empty expression in except clauses.

This change disallows the bare `except:` syntax. All except clauses must
specify at least one exception type:

``` python
try:
    ...
except ValueError:
    ...
except (TypeError, RuntimeError):
    ...
except Exception:
    ...  # Still allowed, but catches all exceptions explicitly
```

The semantics of exception handling remain unchanged, except that it
will no longer be possible to catch all exceptions without explicitly
specifying `BaseException` or a similarly broad exception type.

# Backwards Compatibility

This change is not backwards compatible. Existing code that uses bare
`except:` clauses will need to be modified. To ease the transition:

1.  A deprecation warning will be issued for bare except clauses in
    Python 3.14.
2.  The syntax will be fully disallowed in Python 3.17.
3.  A `from __future__ import strict_excepts` will be provided to
    invalidate bare except handlers in earlier versions of Python.

A tool will be provided to automatically update code to replace bare
`except:` with `except BaseException:`.

# Security Implications

This change has no security implications.

# How to Teach This

For new Python users, exception handling should be taught with explicit
exception types from the start:

``` python
try:
    result = risky_operation()
except ValueError:
    handle_value_error()
except TypeError:
    handle_type_error()
except Exception as e:
    handle_unexpected_error(e)
```

For experienced users, the change can be introduced as a best practice
that is now enforced by the language. The following points should be
emphasized:

1.  Always catch specific exceptions when possible.
2.  Use `except Exception:` as a last resort for truly unexpected
    errors.
3.  Never silence exceptions without careful consideration.

Documentation should guide common exception hierarchies and how to
choose appropriate exception types to catch.

# Rejected ideas

- There are genuine cases where the use of bare `except:` handlers are
  correct. one of the examples that have been raised from Mailman[^8]
  involves handling transactions in the face of any exception:

  > ``` python
  > @contextmanager
  > def transaction():
  >     """Context manager for ensuring the transaction is complete."""
  >     try:
  >         yield
  >     except:
  >         config.db.abort()
  >         raise
  >     else:
  >         config.db.commit()
  > ```

  This code guarantees that no matter what exception occurs, any open
  transaction will be aborted, while in the successful condition, the
  transaction will be committed.

  We do believe that although there are cases such like this one where
  bare `except:` handlers are correct, it would be better to actually be
  explicit and use `except BaseException:` for the reasons indicated in
  the \"Motivation\" section.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.

[^1]: <https://pylint.pycqa.org/en/latest/user_guide/messages/warning/bare-except.html>

[^2]: <https://www.flake8rules.com/rules/E722.html>

[^3]: <https://docs.astral.sh/ruff/rules/bare-except/>

[^4]: <https://google.github.io/styleguide/pyguide.html#24-exceptions>

[^5]: <https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/CODING_STYLE.md#Avoid-bare_except>

[^6]: <https://4.docs.plone.org/develop/plone-coredev/style.html#concrete-rules>

[^7]: <https://docs.openedx.org/en/latest/developers/references/developer_guide/style_guides/python-guidelines.html>

[^8]: <https://gitlab.com/mailman/mailman/-/blob/master/src/mailman/database/transaction.py#L27>
