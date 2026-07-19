---
pep: 837
title: Extensible JSON serialization
author:
- Serhiy Storchaka <storchaka@gmail.com>
discussions_to: https://discuss.python.org/t/pep-837-extensible-json-serialization/108124
status: Draft
type: Standards Track
created: 12-Jul-2026
python_version: '3.16'
post_history:
- '`12-Jul-2026 <https://discuss.python.org/t/pep-837-extensible-json-serialization/108124>`__'
python_status: Draft
url: https://peps.python.org/pep-0837/
source_path: https://github.com/python/peps/blob/main/peps/pep-0837.rst
source_commit: cdd55c6901fa74a264105ba4b3fc5631d08eae11
---

# Abstract

This PEP adds an extension mechanism to the `json`{.interpreted-text
role="mod"} encoder consisting of three complementary parts, one per
level of customization:

- **library level**: a serialization protocol --- the special methods
  `__json__()` and `__raw_json__()`;
- **application level**: a global registry ---
  `copyreg.json(cls, function)` filling `copyreg.json_dispatch_table`,
  following the precedent of `copyreg.pickle`{.interpreted-text
  role="func"};
- **call level**: a per-encoder dispatch table --- a `dispatch_table`
  attribute on a `json.JSONEncoder`{.interpreted-text role="class"},
  mirroring `pickle.Pickler.dispatch_table`{.interpreted-text
  role="attr"}.

The more specific level takes precedence.

A helper class `copyreg.RawJSON` wraps an already-encoded JSON string so
that it is emitted verbatim, enabling representations that are not
otherwise expressible (such as serializing
`decimal.Decimal`{.interpreted-text role="class"} as a JSON number with
full precision).

Several standard library container types whose JSON form is unambiguous
--- `collections.deque`{.interpreted-text role="class"},
`types.MappingProxyType`{.interpreted-text role="class"},
`collections.ChainMap`{.interpreted-text role="class"},
`collections.UserDict`{.interpreted-text role="class"},
`collections.UserList`{.interpreted-text role="class"} and
`collections.UserString`{.interpreted-text role="class"} --- gain a
`__json__` method and therefore serialize out of the box.

The `json`{.interpreted-text role="mod"} module itself gains no new
public names.

# Motivation

Serializing anything beyond the basic types (`dict`, `frozendict`,
`list`, `tuple`, `str`, `int`, `float`, `bool`, `None`) with
`json.dumps`{.interpreted-text role="func"} today requires either
passing a `default=` function to every call, or subclassing
`json.JSONEncoder`{.interpreted-text role="class"} and threading the
subclass through every call site. Both mechanisms attach the knowledge
to the *call* rather than to the *type*:

- **They do not compose.** Two libraries that each need a custom
  `default=` cannot both have it applied to one document without the
  application writing a merging wrapper by hand. A library that
  serializes internally (for logging, caching, IPC) cannot see the
  application\'s `default=` at all.
- **Third-party types cannot opt in.** A library defining a new type has
  no way to make it JSON-serializable for its users; every user must
  learn and repeat the incantation. Requests to fix this for NumPy
  scalars and arrays (`68501`{.interpreted-text role="cpython-issue"},
  `62503`{.interpreted-text role="cpython-issue"}) and for D-Bus integer
  types (`77978`{.interpreted-text role="cpython-issue"}) were closed as
  out of scope for the standard library --- correctly, but leaving the
  underlying need unmet.
- **Some representations are impossible.** `default=` must return one of
  the basic types, so there is no way to emit a non-integer JSON
  *number* that `float` cannot represent exactly.
  `json.loads`{.interpreted-text role="func"} can read decimal numbers
  losslessly via `parse_float=decimal.Decimal`, but the result cannot be
  written back (`67312`{.interpreted-text role="cpython-issue"}). The
  same limitation blocks control over float formatting
  (`81022`{.interpreted-text role="cpython-issue"}) and non-finite float
  representation (`98306`{.interpreted-text role="cpython-issue"},
  `134717`{.interpreted-text role="cpython-issue"}), and the general
  request for emitting pre-encoded JSON (`86957`{.interpreted-text
  role="cpython-issue"}).

The demand is long-standing and broad. Beyond the general proposals for
a serialization hook checked before raising
`TypeError`{.interpreted-text role="exc"} (`71549`{.interpreted-text
role="cpython-issue"} --- open since 2016, `79292`{.interpreted-text
role="cpython-issue"}, `114285`{.interpreted-text role="cpython-issue"},
`86931`{.interpreted-text role="cpython-issue"}), the tracker
accumulated requests for out-of-the-box support of concrete standard
library types: `decimal.Decimal`{.interpreted-text role="class"}
(`67312`{.interpreted-text role="cpython-issue"},
`118810`{.interpreted-text role="cpython-issue"},
`145115`{.interpreted-text role="cpython-issue"}),
`array.array`{.interpreted-text role="class"} (`70451`{.interpreted-text
role="cpython-issue"}), `collections.deque`{.interpreted-text
role="class"} (`64973`{.interpreted-text role="cpython-issue"},
`73849`{.interpreted-text role="cpython-issue"}),
`types.MappingProxyType`{.interpreted-text role="class"}
(`79039`{.interpreted-text role="cpython-issue"}),
`collections.namedtuple`{.interpreted-text role="func"} as an object
(`67661`{.interpreted-text role="cpython-issue"}), and
`datetime.datetime`{.interpreted-text role="class"}
(`65742`{.interpreted-text role="cpython-issue"}); and for whole
categories: sets, frozensets, bytearrays and iterators
(`75338`{.interpreted-text role="cpython-issue"}), generators
(`78031`{.interpreted-text role="cpython-issue"}), and dictionary views
(`83377`{.interpreted-text role="cpython-issue"}).

The idea has also been proposed independently for sixteen years, each
time reinventing part of this design: a `__json__()` method on
python-ideas in [July
2010](https://mail.python.org/pipermail/python-ideas/2010-July/007811.html)
and [April
2020](https://mail.python.org/archives/list/python-ideas@python.org/thread/ISSUQVYI5OYYXKELUNCD5YCEDZ75LCEB/)
and on [discuss.python.org in
2022--2024](https://discuss.python.org/t/introduce-a-json-magic-method/21768);
raw output and a standardized encoder protocol on [python-ideas in
2019](https://mail.python.org/archives/list/python-ideas@python.org/thread/WT6Z6YJDEZXKQ6OQLGAPB3OZ4OHCTPDU/);
a registration function on [discuss.python.org in
2022](https://discuss.python.org/t/json-register/20289).

Meanwhile the ecosystem adopted the convention piecemeal.
[TurboGears](https://turbogears.readthedocs.io/en/latest/cookbook/jsonp.html)
serializes objects via a no-argument `__json__()` --- and its
`custom_encoders` configuration takes precedence over it, the same
ordering as this PEP. [Pyramid\'s JSON
renderer](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html)
calls `__json__(request)`. Applications and libraries such as conda,
Checkmk and TatSu define `__json__` today.
[simplejson](https://simplejson.readthedocs.io/) added an opt-in
`for_json()` method instead --- choosing that name precisely because
dunder names are reserved for the language ([simplejson issue
#52](https://github.com/simplejson/simplejson/issues/52)). In that
issue\'s discussion, a GitHub code search already found more `__json__`
definitions in the wild than `for_json` ones by 2016, and formalizing
the protocol in a PEP was requested so that third-party libraries can
rely on the same signature. Only the standard library can define
`__json__`; this PEP does, ending the fragmentation.

The type-support requests could not simply be granted one by one. For
most of the requested types the JSON representation is *ambiguous*:

- `Decimal` --- a JSON number (`1234567890.0987654321`) or a JSON string
  (`"1234567890.0987654321"`)? Both are common; each is wrong for some
  consumers.
- `namedtuple` --- a JSON Array (it is a tuple) or a JSON Object (it has
  named fields)?
- `array.array` --- a JSON Array of numbers, or a compact encoded
  string? The sensible answer even depends on its type code.
- `datetime` --- which of the many string representations (ISO 8601
  variants, epoch seconds, RFC formats)?

No standard library default can be correct, so the standard library
should provide the *mechanism* by which each application declares its
*policy*. That mechanism is this PEP.

# Rationale

## One system covering all of the collected needs

The feature is deliberately a small *system* rather than a single hook:
each part answers a different cluster of the requests above, and no part
alone covers them all.

- The `__json__` **protocol** answers the general extension proposals
  and the third-party-type reports: the type\'s author makes it
  serializable once, with no imports, inherited by subclasses.
- The **registry** answers the requests for types the requester does not
  control or whose representation is a policy choice (`Decimal`,
  `namedtuple`, `array.array`, `datetime`): the application declares its
  policy in one line.
- **Raw output** (`__raw_json__`/`RawJSON`) answers the requests for
  representations that no basic-type conversion can express: pre-encoded
  fragments, full-precision numbers, float formatting, non-finite
  floats.
- **Duck typing of hook results** answers the category requests
  (iterables, sets, generators, dictionary views, mappings):
  `copyreg.json(set, sorted)` is a complete solution for sets, and a
  hook may return any iterable or mapping-like object rather than
  materializing a list or dict.
- **Standard library** `__json__` **methods** answer the requests for
  unambiguous containers (`deque`, `mappingproxy`) directly.
- The **per-encoder** `dispatch_table` scopes any of the above to one
  encoder when a process needs different policies for different outputs.

## Three levels of customization

The three parts correspond to the three levels at which serialization is
decided, and deliberately have different shapes:

- **Library level** --- `__json__()` is for the author of a type. A
  method needs no imports and is inherited by subclasses: a library can
  make its types JSON-serializable without depending on
  `json`{.interpreted-text role="mod"} or `copyreg`{.interpreted-text
  role="mod"} at all.
- **Application level** --- `copyreg.json()` is for users of a type they
  do not control: the application chooses, process-wide, how third-party
  or ambiguous standard library types serialize. Registration is by
  exact type; subclasses that want the same treatment inherit `__json__`
  instead.
- **Call level** --- the `dispatch_table` attribute on a
  `json.JSONEncoder`{.interpreted-text role="class"} subclass or
  instance customizes a particular call, when one program needs
  different policies for different outputs (an external API versus an
  internal cache, say). The existing `default=` parameter remains the
  call-level catch-all for objects no other mechanism handled.

The more specific level takes precedence: a registry entry is consulted
before the type\'s `__json__` (the application overrides the library),
and a per-encoder table replaces the global registry (the call overrides
the application).

## Why the registry lives in copyreg

The registry could have been `json.register()`. It is placed in
`copyreg`{.interpreted-text role="mod"} instead, for three reasons.

**Import cost and layering.** A library that registers a serialization
function for a foreign type at import time should not pay for the
`json`{.interpreted-text role="mod"} module, whose import is dominated
by `re`{.interpreted-text role="mod"} (roughly fifty times the cost of
importing `copyreg`{.interpreted-text role="mod"}, which is imported by
`copy`{.interpreted-text role="mod"} and `pickle`{.interpreted-text
role="mod"} anyway). With the registry and `RawJSON` both in
`copyreg`{.interpreted-text role="mod"}, a registrant imports exactly
one small module. The `json`{.interpreted-text role="mod"} module
imports `copyreg`{.interpreted-text role="mod"} (as
`copy`{.interpreted-text role="mod"} already does), never the reverse.

**Precedent and symmetry.** This is the pickle model, mirrored in both
halves: a registration function filling a global table
(`copyreg.pickle`{.interpreted-text role="func"} / `copyreg.json()`) and
a per-instance `dispatch_table` attribute overriding it
(`pickle.Pickler`{.interpreted-text role="class"} /
`json.JSONEncoder`{.interpreted-text role="class"}). The function name
follows the `copyreg.pickle()` convention; thirty years of that
precedent show that a registration function named after its protocol
causes no confusion, because registration is a one-off, module-prefixed
call.

**Neutral ground.** Third-party JSON encoders can honor the same
registry and helper class without importing the standard
`json`{.interpreted-text role="mod"} module, so the ecosystem can
converge on a single registration point.

Placing the registry in `copyreg`{.interpreted-text role="mod"} also
generalizes the module\'s charter --- registering protocol
implementations for types you do not control. Registries for other
protocols (such as `__copy__`- and `__deepcopy__`-like hooks for the
`copy`{.interpreted-text role="mod"} module) fit the same pattern and
will be proposed separately.

## The raw-output mechanism

Emitting an already-encoded fragment verbatim is the only way to express
representations outside the basic types, most importantly full-precision
numbers. The chosen mechanism is a duck-typed special method,
`__raw_json__()`, with `copyreg.RawJSON` as a convenience wrapper:

- A hook (or `__json__`) that wants raw output returns
  `copyreg.RawJSON(fragment)` --- one import, which the registrant has
  already paid --- or an instance of its own wrapper class defining just
  `__raw_json__`, with no imports at all.
- `RawJSON` additionally defines `__json__` returning `self` to serve
  its second function: including a pre-serialized fragment *directly* in
  a document (as a value in a dict or list passed to
  `json.dumps`{.interpreted-text role="func"}), not only as a hook
  result.

The protocol, not the class, is the interface; the class is sugar.

## Performance: the encoding pipeline as an invariant

The `json`{.interpreted-text role="mod"} encoder is among the hottest
code in the standard library, and the design treats its branch order as
an invariant:

1.  Objects of the exact basic types are encoded with **no attribute
    lookups at all** --- the overwhelmingly common case pays nothing for
    this PEP.
2.  The dispatch table and `__json__` are consulted next --- one dict
    lookup plus one type-attribute lookup --- *before* the `isinstance`
    fallbacks, solely so that subclasses of the basic types can
    customize their serialization at all (an `int` subclass would
    otherwise be consumed by the `isinstance(o, int)` check, the very
    problem history records for `IntEnum`: `62464`{.interpreted-text
    role="cpython-issue"}).
3.  The `isinstance` fallbacks then catch non-customizing subclasses,
    preserving today\'s behavior for them exactly (`IntEnum` still
    serializes as a number).
4.  Duck typing of a hook result --- `__index__` as a number,
    `__float__` as a number, `__iter__` with `keys()` as an object,
    `__iter__` alone as an array, `__raw_json__` verbatim --- applies
    **only when a hook has fired**. In particular, `__raw_json__` is
    never looked up on an object that did not come from a hook, so
    objects bound for the subclass checks or `default()` pay no extra
    lookups.
5.  The `default` hook runs last, unchanged.

## Which stdlib types get a default \_\_json\_\_

The criterion: **a standard library type gets a default
\`\`\_\_json\_\_\`\` only when its JSON form is unambiguous.**
Transparent containers qualify --- `deque`, `mappingproxy`, `ChainMap`,
`UserDict`, `UserList`, `UserString` are semantically just arrays and
objects (resolving `64973`{.interpreted-text role="cpython-issue"},
`73849`{.interpreted-text role="cpython-issue"} and
`79039`{.interpreted-text role="cpython-issue"} directly). `Decimal`,
`namedtuple`, `array.array` and `datetime` do not qualify, for the
ambiguity reasons given in the Motivation; for them, this PEP\'s answer
is a one-line registration by the application (see [How to Teach
This](#how-to-teach-this)).

This criterion is also the ready-made answer to future \"just add
`__json__` to X\" requests.

# Specification

## The \_\_json\_\_ protocol

A class may define a method `__json__(self)`. When the
`json`{.interpreted-text role="mod"} encoder encounters an object that
is not of an exactly-supported basic type and has no dispatch-table
entry, it looks up `__json__` on the object\'s type (like all special
methods) and, if present, calls it. The result is then serialized in
place of the object:

- A result of a basic type, or an instance of their subclasses, is
  serialized as usual.
- Otherwise the result is interpreted by duck typing: an object with
  `__index__` is serialized as a JSON number via
  `operator.index`{.interpreted-text role="func"}; else one with
  `__float__` as a JSON number via `float`{.interpreted-text
  role="class"}; else an iterable with a `keys()` method (and
  `__getitem__`) as a JSON object; else an iterable as a JSON array;
  else an object whose type defines `__raw_json__` is serialized by
  calling it (see below). Otherwise `TypeError`{.interpreted-text
  role="exc"} is raised.

The result of `__json__` is not recursively re-submitted to the
protocol: a result that is itself of a hook-defining type is not
converted again.

## The \_\_raw_json\_\_ protocol

`__raw_json__(self)` must return a `str`{.interpreted-text
role="class"}, which the encoder emits verbatim, without validation of
its content. It is consulted only for objects produced by a
dispatch-table function or `__json__` (see the pipeline invariant
above), so a wrapper class used as a hook result needs only
`__raw_json__`. `RawJSON` also defines `__json__` returning `self`,
which lets its instances appear directly in the input document.

## The registry

The following are added to `copyreg`{.interpreted-text role="mod"}:

`copyreg.json(ob_type, json_function)`

:   The official registration interface. Registers `json_function` as
    the serialization function for `ob_type`. Raises
    `TypeError`{.interpreted-text role="exc"} if `json_function` is not
    callable. The function is called with the object as its only
    argument and its result is interpreted exactly like the result of
    `__json__`. Registration is by exact type: it does not apply to
    subclasses of `ob_type`.

`copyreg.json_dispatch_table`

:   The dict mapping types to registered functions, consulted by the
    `json`{.interpreted-text role="mod"} module (and available to other
    JSON encoders honoring the registry). Applications register via
    `copyreg.json()` rather than mutating the table directly.

`copyreg.RawJSON(encoded_json)`

:   A wrapper whose instances are serialized by emitting `encoded_json`
    verbatim. `str()` of the instance returns the fragment.

Registered functions take precedence over `__json__`. Entries for the
exactly-supported basic types themselves (`dict`, `list`, `str`, `int`,
\...) are never consulted, because the fast paths for those types run
first.

## The encoder

`json.JSONEncoder`{.interpreted-text role="class"} (and the C
accelerator) consult
`getattr(encoder, 'dispatch_table', copyreg.json_dispatch_table)`, so a
subclass may set a `dispatch_table` class or instance attribute to
replace the global registry for that encoder, mirroring
`pickle.Pickler`{.interpreted-text role="class"}.

Dict *keys* are not affected by any part of this PEP: key serialization
accepts exactly the types it accepts today, and neither the dispatch
table nor `__json__` is consulted for keys (see Open Issues).

The `check_circular` machinery is unchanged: containers and `default`
results are tracked as today. Hook results are not separately tracked; a
pathological hook that returns a fresh cycle on every call ends in
`RecursionError`{.interpreted-text role="exc"} like any runaway
recursion.

## Standard library \_\_json\_\_ methods

`__json__` returning a view of the obvious container is added to:
`collections.deque`{.interpreted-text role="class"} and
`types.MappingProxyType`{.interpreted-text role="class"} (in C,
returning `self`; the encoder consumes them via the array and object
paths), and `collections.ChainMap`{.interpreted-text role="class"},
`collections.UserDict`{.interpreted-text role="class"},
`collections.UserList`{.interpreted-text role="class"},
`collections.UserString`{.interpreted-text role="class"} (in Python,
returning `self` or the underlying `data`).

# Backwards Compatibility

The `json`{.interpreted-text role="mod"} module gains no new public
names and no existing behavior changes for objects that define none of
the new hooks:

- All exactly-supported basic types serialize byte-for-byte as before.
- Subclasses of basic types without hooks serialize as before (`IntEnum`
  as a number, str subclasses as strings, dict and list subclasses as
  objects and arrays).
- Objects previously rejected with `TypeError`{.interpreted-text
  role="exc"} that define `__json__` will now serialize. Classes
  following the TurboGears convention (a no-argument `__json__`) get
  exactly the behavior they intended. Classes written for Pyramid\'s
  renderer, whose `__json__(self, request)` takes an argument, keep
  raising `TypeError`{.interpreted-text role="exc"} --- now from the
  missing argument rather than from `default` --- so code catching the
  exception keeps working, though the message changes. A class using the
  name for something unrelated would change behavior, but dunder names
  are reserved by the language reference, and no plausible unrelated
  meaning is known.
- The signature of the private `_json.make_encoder` gains a
  `dispatch_table` argument.
- The six standard library classes gaining `__json__` previously raised
  `TypeError`{.interpreted-text role="exc"} under
  `json.dumps`{.interpreted-text role="func"} (unless handled by
  `default=`). Code using `default=` to serialize them keeps working,
  because those objects no longer reach `default` --- but the built-in
  representation (array/object) may differ from what a custom `default`
  produced. This is the usual risk of any new default behavior and is
  judged acceptable for unambiguous containers.
- `from copyreg import json` shadows the `json`{.interpreted-text
  role="mod"} module name in the importing namespace, as
  `from copyreg import pickle` always has. Documentation will show
  module-prefixed calls.

# Security Implications

`__raw_json__` and `RawJSON` emit strings without validation, so a hook
returning attacker-controlled fragments could produce invalid or
misleading JSON. This is no new capability: `default=` already executes
arbitrary code during encoding, and producing malformed output requires
the application to have installed the hook. The documentation will note
that raw fragments must come from trusted producers.

# How to Teach This

Four recipes, one per customization level:

1.  *Library level* --- your own class: define `__json__`:

        class Money:
            def __json__(self):
                return {"amount": str(self.amount),
                        "currency": self.currency}

2.  *Application level* --- someone else\'s class: register it:

        import copyreg, decimal
        copyreg.json(decimal.Decimal, str)

3.  *Application level* --- a representation JSON cannot otherwise
    express: return a raw fragment:

        copyreg.json(decimal.Decimal,
                     lambda d: copyreg.RawJSON(str(d)))

4.  *Call level* --- one encoder, different policy:

        class APIEncoder(json.JSONEncoder):
            dispatch_table = {decimal.Decimal: str}

The existing `default=` remains the call-level catch-all for objects no
other mechanism handled and is documented as running last.

# Reference Implementation

`153607`{.interpreted-text role="cpython-pr"} (branch
`json-customize4`), a rebase and rework of the author\'s 2017--2022
`json-customize` branches: the protocol and registry with C and Python
encoder support, standard library `__json__` methods, and tests for both
encoder implementations, including the encoding-pipeline invariant
recorded as code comments.

# Rejected Ideas

`json.register()` instead of copyreg

:   Registration in the `json`{.interpreted-text role="mod"} module
    forces registrants to import it (\~50× the import cost of
    `copyreg`{.interpreted-text role="mod"}, dominated by
    `re`{.interpreted-text role="mod"}), breaks the pickle symmetry, and
    gives third-party encoders no neutral registry. Discoverability is
    addressed by documentation in the `json`{.interpreted-text
    role="mod"} docs pointing to `copyreg`{.interpreted-text
    role="mod"}.

`copyreg.register_json()`-style names

:   Inconsistent with `copyreg.pickle`{.interpreted-text role="func"},
    the thirty-year precedent.

Default `__json__` for Decimal, namedtuple, array.array, datetime

:   Each has at least two legitimate JSON representations (number vs
    string; array vs object; array vs encoded string, depending on type
    code; many string formats). A default would be wrong for a large
    fraction of consumers; the ambiguity is the argument for a registry,
    not for a default.

Serializing all iterables and mappings without opt-in

:   Requested in `75338`{.interpreted-text role="cpython-issue"} and
    implied by `78031`{.interpreted-text role="cpython-issue"} and
    `83377`{.interpreted-text role="cpython-issue"}, but a silent
    behavior change: every object with `__iter__` (sets, generators,
    file objects) would begin serializing as an array instead of
    reaching `default=` or raising. Duck typing therefore applies only
    to hook results --- an explicit opt-in.

`isinstance(o, RawJSON)` instead of `__raw_json__`

:   Rejected because it taxes the wrong audience: a type that opts in
    via `__json__` with zero imports would need to import
    `copyreg`{.interpreted-text role="mod"} the moment it needs raw
    output. With the duck-typed protocol, the class *is* the
    convenience, not the mechanism.

Recognizing raw wrappers by class name

:   Dispatching on names has precedent in pickle, which recognizes the
    `__newobj__` and `__newobj_ex__` callables in reduce tuples by their
    `__name__`, but this PEP does not follow that example. Recognizing
    raw wrappers by `type(o).__name__ == "RawJSON"` would inspect an
    ordinary, plausible class name on arbitrary objects: any unrelated
    class that happens to use it would silently change encoding
    behavior. The duck-typed `__raw_json__` keeps the marker in the
    reserved dunder namespace.

Consulting `__raw_json__` directly on all objects

:   Would let a class self-serialize raw with a single method, but adds
    a type-attribute lookup for every object on the way to the subclass
    checks, to the duck-typed interpretations (`__index__`, `__iter__`,
    etc.) and to `default()` --- a real cost in one of the hottest paths
    in the standard library. The gated design makes the raw object pay
    one method call instead.

Reusing `__repr__`/`__str__` or a generic `__serialize__`

:   Proposed in `114285`{.interpreted-text role="cpython-issue"}. These
    methods cannot serve as the *marker* for raw output: nearly every
    type defines them (and their results are usually not valid JSON), so
    the encoder could not tell raw-capable objects apart; a
    format-agnostic `__serialize__` likewise cannot say *which* format
    it produces. `__str__` can, however, serve as the *payload* once a
    separate marker exists --- see Open Issues.

MRO-based (isinstance) dispatch for the registry

:   The registry uses exact-type matching like `copyreg.dispatch_table`.
    Subclass dispatch is the protocol\'s job: a base class defines
    `__json__` once and subclasses inherit it. Exact matching keeps
    lookup one dict access and avoids MRO scans on the hot path.

# Open Issues

- **Dict keys.** Neither the registry nor `__json__` applies to dict
  keys; requests exist (`63020`{.interpreted-text role="cpython-issue"},
  `117391`{.interpreted-text role="cpython-issue"},
  `85741`{.interpreted-text role="cpython-issue"},
  `117592`{.interpreted-text role="cpython-issue"}). A compatible future
  extension is to consult the hooks exactly where the
  `keys must be str...` `TypeError`{.interpreted-text role="exc"} is
  raised today (before the `skipkeys` skip), so conforming keys pay
  nothing; the hook result would re-enter key normalization, and
  container or raw results would be rejected. Deferred from this PEP.
- **Cycle detection through hooks.** A hook returning a fresh
  equal-but-not-identical cycle each call exhausts the recursion limit
  (`RecursionError`{.interpreted-text role="exc"}) rather than reporting
  `Circular reference detected`. Tracking hook results in the
  `check_circular` markers would close this at some cost to the hook
  path; deferred pending evidence it matters in practice.
- **\_\_raw_json\_\_ as a pure marker.** An open alternative keeps
  `__raw_json__` as the marker but takes the emitted fragment from
  `str(o)` instead of the method\'s return value --- `RawJSON` defines
  `__str__` returning the fragment for exactly this reason, and the same
  would hold if raw wrappers were recognized by identity or name.
  Calling the `__str__` slot is faster than a full method call, but the
  design would *require* every raw wrapper to define both `__raw_json__`
  and `__str__`.

# Appendix: Related issues

The CPython issues referenced in this PEP, in chronological order:

- enum.IntEnum is not compatible with JSON serialisation
  (`62464`{.interpreted-text role="cpython-issue"}, closed)
- json.dumps() claims numpy.ndarray and numpy.bool\_ are not
  serializable (`62503`{.interpreted-text role="cpython-issue"}, closed)
- json.dump() ignores its \'default\' option when serializing dictionary
  keys (`63020`{.interpreted-text role="cpython-issue"}, open)
- collections.deque should ship with a stdlib json serializer
  (`64973`{.interpreted-text role="cpython-issue"}, open)
- json library fails to serialize objects such as datetime
  (`65742`{.interpreted-text role="cpython-issue"}, closed)
- Only READ support for Decimal in json (`67312`{.interpreted-text
  role="cpython-issue"}, open)
- Allow namedtuple to be JSON encoded as dict (`67661`{.interpreted-text
  role="cpython-issue"}, closed)
- json fails to serialise numpy.int64 (`68501`{.interpreted-text
  role="cpython-issue"}, closed)
- Serialize array.array to JSON by default (`70451`{.interpreted-text
  role="cpython-issue"}, open)
- json.dumps to check for obj.\_\_json\_\_ before raising TypeError
  (`71549`{.interpreted-text role="cpython-issue"}, open)
- Make collections.deque json serializable (`73849`{.interpreted-text
  role="cpython-issue"}, closed)
- Encode set, frozenset, bytearray, and iterators as json arrays
  (`75338`{.interpreted-text role="cpython-issue"}, closed)
- json int encoding incorrect for dbus.Byte (`77978`{.interpreted-text
  role="cpython-issue"}, closed)
- Json.dump() bug when using generator (`78031`{.interpreted-text
  role="cpython-issue"}, closed)
- MappingProxy objects should JSON serialize just like a dictionary
  (`79039`{.interpreted-text role="cpython-issue"}, open)
- Make Custom Object Classes JSON Serializable
  (`79292`{.interpreted-text role="cpython-issue"}, open)
- Supporting customization of float encoding in JSON
  (`81022`{.interpreted-text role="cpython-issue"}, open)
- json fails to encode dictionary view types (`83377`{.interpreted-text
  role="cpython-issue"}, closed)
- json.JSONEncoder.default should be called for dict keys as well
  (`85741`{.interpreted-text role="cpython-issue"}, closed)
- Introduce new data model method \_\_iter_items\_\_
  (`86931`{.interpreted-text role="cpython-issue"}, closed)
- There is no way to json encode object to str.
  (`86957`{.interpreted-text role="cpython-issue"}, open)
- Proper or custom JSON serialization of non-finite float values
  (`98306`{.interpreted-text role="cpython-issue"}, open)
- Json encode from \_\_repr\_\_, \_\_str\_\_ or \_\_serialize\_\_ when
  available (`114285`{.interpreted-text role="cpython-issue"}, closed)
- Allow JSONEncoder to handle passing unsupported dict keys through
  .default() before throwing TypeError (`117391`{.interpreted-text
  role="cpython-issue"}, open)
- json\'s default callable/method ignores keys.
  (`117592`{.interpreted-text role="cpython-issue"}, closed)
- Allow the JSON encoder to optionally support decimal.Decimal objects
  (`118810`{.interpreted-text role="cpython-issue"}, closed)
- Allow customization of NaN and Infinity serialization in json module
  (`134717`{.interpreted-text role="cpython-issue"}, closed)
- Optional Decimal to JSON Number Conversion in json Module
  (`145115`{.interpreted-text role="cpython-issue"}, closed)

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
