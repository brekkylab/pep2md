---
pep: 788
title: Protecting the C API from Interpreter Finalization
author:
- Peter Bierma <peter@python.org>
sponsor: Victor Stinner <vstinner@python.org>
discussions_to: https://discuss.python.org/t/104150
status: Draft
type: Standards Track
created: 23-Apr-2025
python_version: '3.15'
post_history:
- '`10-Mar-2025 <https://discuss.python.org/t/83959>`__'
- '`27-Apr-2025 <https://discuss.python.org/t/89863>`__'
- '`28-May-2025 <https://discuss.python.org/t/93653>`__'
- '`03-Oct-2025 <https://discuss.python.org/t/104150>`__'
python_status: Draft
url: https://peps.python.org/pep-0788/
source_path: https://github.com/python/peps/blob/main/peps/pep-0788.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:48+00:00'
---

# Abstract

This PEP introduces a suite of functions in the C API to safely attach
to an interpreter by preventing finalization. In particular:

1.  `PyInterpreterGuard`{.interpreted-text role="c:type"}, which
    prevents an interpreter from finalizing.
2.  `PyInterpreterView`{.interpreted-text role="c:type"}, which provides
    a thread-safe way to get an interpreter without holding an
    `attached thread state`{.interpreted-text role="term"}.
3.  `PyThreadState_Ensure`{.interpreted-text role="c:func"},
    `PyThreadState_EnsureFromView`{.interpreted-text role="c:func"}, and
    `PyThreadState_Release`{.interpreted-text role="c:func"}, which are
    high-level APIs for getting an attached thread state while in
    arbitrary native code (similar to
    `PyGILState_Ensure`{.interpreted-text role="c:func"} and
    `PyGILState_Release`{.interpreted-text role="c:func"}).

For example:

``` c
static int
thread_function(PyInterpreterView *view)
{
    // Similar to PyGILState_Ensure(), but we can be sure that the interpreter
    // is alive and well before attaching.
    PyThreadState *tstate = PyThreadState_EnsureFromView(view);
    if (tstate == NULL) {
        return -1;
    }

    // Now we can call Python code, without worrying about the thread
    // hanging due to finalization.
    if (PyRun_SimpleString("print('My hovercraft is full of eels')") < 0) {
        PyErr_Print();
    }

    // Destroy the thread state and allow the interpreter to finalize.
    PyThreadState_Release(tstate);
    return 0;
}
```

# Terminology

This PEP uses the term \"finalization\" to refer to the finalization of
a singular interpreter, not the entire Python runtime.

Additionally, this PEP uses the term \"foreign thread\" to refer to
threads that were not created by the `threading`{.interpreted-text
role="mod"} module. Threads that were created by the `threading` module
are sometimes referred to as \"Python threads\" in this proposal.

# Motivation

## Foreign threads hang during interpreter finalization

Many large libraries might need to call Python code in highly
asynchronous situations where the desired interpreter may be finalizing
or has already been finalized, but want to continue running code after
invoking the interpreter. This desire has been [brought up by
users](https://discuss.python.org/t/78850/). For example, a callback
that wants to call Python code might be invoked when:

1.  A kernel has finished running on a GPU.
2.  A network packet was received.
3.  A thread has quit, and a native library is executing static
    finalizers for thread-local storage.

Generally, this pattern would look something like this:

``` c
static void
some_callback(void *arg)
{
    /* Do some work */
    /* ... */

    PyGILState_STATE gstate = PyGILState_Ensure();
    /* Invoke the C API to do some computation */
    PyGILState_Release(gstate);

    /* ... */
}
```

This comes with a hidden problem. If the target interpreter is
finalizing, the current thread will hang! Or, if the target interpreter
has been completely deleted (such as with short-lived subinterpreters),
then attaching will likely result in a crash.

There are currently a few workarounds for this:

1.  Leak resources to prevent the need to invoke Python.
2.  Protect against finalization using an `atexit`{.interpreted-text
    role="mod"} callback.

These options generally work, but can be verbose, complex, or result in
other issues. Ideally, interpreter finalization should not be such a
footgun when working with Python\'s C API.

### Locks in native extensions can be unusable during finalization

When acquiring locks in a native API, it\'s common (and often necessary)
to release the GIL (or critical sections on the free-threaded build) to
allow other code to execute during aquisition of the lock. This can be
problematic during finalization, because threads holding locks might be
hung. For example:

1.  A thread goes to acquire a lock, first detaching its thread state to
    avoid deadlocks. This is generally done through
    `Py_BEGIN_ALLOW_THREADS`{.interpreted-text role="c:macro"}.
2.  The main thread begins finalization and tells all thread states to
    hang upon attachment.
3.  The thread acquires the lock it was waiting on, but then hangs while
    attempting to reattach its thread state via
    `Py_END_ALLOW_THREADS`{.interpreted-text role="c:macro"}.
4.  The main thread can no longer acquire the lock, because the thread
    holding it has hung.

[python/cpython#129536](https://github.com/python/cpython/issues/129536)
is an example of this problem. In that issue, Python issues a fatal
error during finalization, because a daemon thread was hung while
holding the lock for `sys.stderr`{.interpreted-text role="data"}, so the
main thread could no longer acquire it.

# Specification

:::: note
::: title
Note
:::

This PEP, as it is currently written, has **not** been approved by the C
API Working Group (see `731`{.interpreted-text role="pep"}). However,
the author of this proposal has discussed this PEP significantly with
them, and a prior iteration of this PEP was indeed approved. Following
discussion with Python\'s Steering Council, the author of this PEP
believed the right course of action was to deviate from some of the
working group\'s recommendations in order to produce the best possible
design while also avoiding invasive changes to Python\'s ecosystem.
::::

## Interpreter guards

> An opaque interpreter guard structure.
>
> By holding an interpreter guard, the caller can ensure that the
> interpreter will not finalize until the guard is closed (through
> `PyInterpreterGuard_Close`{.interpreted-text role="c:func"}).
>
> This is similar to a \"readers-writers\" lock; threads may
> concurrently guard an interpreter, and the interpreter will have to
> wait until all threads have closed their guards before it can enter
> finalization. After finalization has started, threads are forever
> unable to acquire guards for that interpreter.

> Create a finalization guard for the current interpreter.
>
> On success, this function returns a guard for the current interpreter
> (as determined by the `attached thread state`{.interpreted-text
> role="term"}); on failure, it returns `NULL` with an exception set.
> This function will fail only if the current interpreter has already
> started finalizing, or if the process is out of memory.
>
> The guard pointer returned by this function must be eventually closed
> with `PyInterpreterGuard_Close`{.interpreted-text role="c:func"};
> failing to do so will result in the Python process infinitely hanging.
>
> The caller must hold an attached thread state.

> Create a finalization guard for an interpreter through a view. *view*
> must not be `NULL`.
>
> On success, this function returns a guard to the interpreter
> represented by *view*. The view is still valid after calling this
> function. The guard must eventually be closed with
> `PyInterpreterGuard_Close`{.interpreted-text role="c:func"}.
>
> If the interpreter no longer exists, is already finalizing, or out of
> memory, then this function returns `NULL` without setting an
> exception.
>
> The caller does not need to hold an attached thread state.

> Close an interpreter guard, allowing the interpreter to enter
> finalization if no other guards remain. If an interpreter guard is
> never closed, the interpreter will infinitely wait when trying to
> enter finalization.
>
> After an interpreter guard is closed, it may not be used in
> `PyThreadState_Ensure`{.interpreted-text role="c:func"}. Doing so will
> result in undefined behavior.
>
> This function cannot fail, and the caller doesn\'t need to hold an
> attached thread state.

## Interpreter views

> An opaque view of an interpreter.
>
> This is a thread-safe way to access an interpreter that may have be
> finalizing or already destroyed.

> Create a view to the current interpreter.
>
> This function is generally meant to be used alongside
> `PyInterpreterGuard_FromView`{.interpreted-text role="c:func"} or
> `PyThreadState_EnsureFromView`{.interpreted-text role="c:func"}.
>
> On success, this function returns a view to the current interpreter;
> on failure, it returns `NULL` with an exception set.
>
> The caller must hold an attached thread state.

> Delete an interpreter view. If an interpreter view is never closed,
> the view\'s memory will never be freed, but there are no other
> consequences. (In contrast, forgetting to close a guard will
> infinitely hang the main thread during finalization.)
>
> This function cannot fail, and the caller doesn\'t need to hold an
> attached thread state.

> Create a view for the main interpreter (the first and default
> interpreter in a Python process).
>
> On success, this function returns a view to the main interpreter; on
> failure, it returns `NULL` without an exception set. Failure indicates
> that the process is out of memory.
>
> The caller does not need to hold an attached thread state.

## Attaching and detaching thread states

This proposal includes three new high-level threading APIs that intend
to replace `PyGILState_Ensure`{.interpreted-text role="c:func"} and
`PyGILState_Release`{.interpreted-text role="c:func"}.

> Ensure that the thread has an attached thread state for the
> interpreter protected by *guard*, and thus can safely invoke that
> interpreter.
>
> It is OK to call this function if the thread already has an attached
> thread state, as long as there is a subsequent call to
> `PyThreadState_Release`{.interpreted-text role="c:func"} that matches
> this one.
>
> Nested calls to this function will only sometimes create a new thread
> state.
>
> First, this function checks if an attached thread state is present. If
> there is, this function then checks if the interpreter of that thread
> state matches the interpreter guarded by *guard*. If that is the case,
> this function simply marks the thread state as being used by a
> `PyThreadState_Ensure` call and returns.
>
> If there is no attached thread state, then this function checks if any
> thread state has been used by the current OS thread. (This is returned
> by `PyGILState_GetThisThreadState`{.interpreted-text role="c:func"}.)
> If there was, then this function checks if that thread state\'s
> interpreter matches *guard*. If it does, it is re-attached and marked
> as used.
>
> Otherwise, if both of the above cases fail, a new thread state is
> created for *guard*. It is then attached and marked as owned by
> `PyThreadState_Ensure`.
>
> This function will return `NULL` to indicate a memory allocation
> failure, and otherwise return a pointer to the thread state that was
> previously attached (which might have been `NULL`, in which case an
> non-`NULL` sentinel value is returned instead to differentiate between
> failure \-- this means that this function will sometimes return an
> invalid `PyThreadState` pointer).
>
> To visualize, this function is roughly equivalent to the following:
>
> ``` c
> PyThreadState *
> PyThreadState_Ensure(PyInterpreterGuard *guard)
> {
>     assert(guard != NULL);
>     PyInterpreterState *interp = PyInterpreterGuard_GetInterpreter(guard);
>     assert(interp != NULL);
>
>     PyThreadState *current_tstate = PyThreadState_GetUnchecked();
>     if (current_tstate == NULL) {
>         PyThreadState *last_used = PyGILState_GetThisThreadState();
>         if (last_used != NULL) {
>             ++last_used->ensure_counter;
>             PyThreadState_Swap(last_used);
>             return NO_TSTATE_SENTINEL;
>         }
>     } else if (current_tstate->interp == interp) {
>         ++current_tstate->ensure_counter;
>         return current_tstate;
>     }
>
>     PyThreadState *new_tstate = PyThreadState_New(interp);
>     if (new_tstate == NULL) {
>         return NULL;
>     }
>
>     ++new_tstate->ensure_counter;
>     mark_tstate_owned_by_ensure(new_tstate);
>     PyThreadState_Swap(new_tstate);
>     return current_tstate == NULL ? NO_TSTATE_SENTINEL : current_tstate;
> }
> ```

> Get an attached thread state for the interpreter referenced by *view*.
>
> *view* must not be `NULL`. If the interpreter referenced by *view* has
> been finalized or is currently finalizing, then this function returns
> `NULL` without setting an exception. This function may also return
> `NULL` to indicate that the process is out of memory.
>
> The interpreter referenced by *view* will be implicitly guarded. The
> guard will be released upon the corresponding
> `PyThreadState_Release`{.interpreted-text role="c:func"} call.
>
> On success, this function will return the thread state that was
> previously attached. If no thread state was previously attached, this
> returns a non-`NULL` sentinel value. The behavior of whether this
> function creates a thread state is equivalent to that of
> `PyThreadState_Ensure`{.interpreted-text role="c:func"}.
>
> To visualize, function is roughly equivalent to the following:
>
> ``` c
> PyThreadState *
> PyThreadState_EnsureFromView(PyInterpreterView *view)
> {
>     assert(view != NULL);
>     PyInterpreterGuard *guard = PyInterpreterGuard_FromView(view);
>     if (guard == NULL) {
>         return NULL;
>     }
>
>     PyThreadState *tstate = PyThreadState_Ensure(guard);
>     if (tstate == NULL) {
>         PyInterpreterGuard_Close(guard);
>         return NULL;
>     }
>     close_guard_upon_tstate_release(tstate, guard);
>     return tstate;
> }
> ```

> Release a `PyThreadState_Ensure`{.interpreted-text role="c:func"}
> call. This must be called exactly once for each call to
> `PyThreadState_Ensure`.
>
> This function will decrement an internal counter on the attached
> thread state. If this counter ever reaches below zero, this function
> emits a fatal error (via `Py_FatalError`{.interpreted-text
> role="c:func"}).
>
> If the attached thread state is owned by `PyThreadState_Ensure`, then
> the attached thread state will be deallocated and deleted upon the
> internal counter reaching zero. Otherwise, nothing happens when the
> counter reaches zero.
>
> If *tstate* is non-`NULL`, it will be attached upon returning. If
> *tstate* indicates that no prior thread state was attached, there will
> be no attached thread state upon returning.
>
> To visualize, this function is roughly equivalent to the following:
>
> ``` c
> void
> PyThreadState_Release(PyThreadState *old_tstate)
> {
>     PyThreadState *current_tstate = PyThreadState_Get();
>     assert(old_tstate != NULL);
>     assert(current_tstate != NULL);
>     assert(current_tstate->ensure_counter > 0);
>     if (--current_tstate->ensure_counter > 0) {
>         // There are remaining PyThreadState_Ensure() calls
>         // for this thread state.
>         return;
>     }
>
>     assert(current_tstate->ensure_counter == 0);
>     if (old_tstate == NO_TSTATE_SENTINEL) {
>         // No thread state was attached prior the PyThreadState_Ensure()
>         // call. So, we can just destroy the current thread state and return.
>         assert(should_dealloc_tstate(current_tstate));
>         PyThreadState_Clear(current_tstate);
>         PyThreadState_DeleteCurrent();
>         return;
>     }
>
>     if (should_dealloc_tstate(current_tstate)) {
>         // The attached thread state was created by the initial PyThreadState_Ensure()
>         // call. It's our job to destroy it.
>         PyThreadState_Clear(current_tstate);
>         PyThreadState_DeleteCurrent();
>     }
>
>     PyThreadState_Swap(old_tstate);
> }
> ```

## Soft deprecation of `PyGILState` APIs

This proposal issues a
`soft deprecation <soft deprecated>`{.interpreted-text role="term"} on
all of the existing `PyGILState` APIs in favor of the existing and new
`PyThreadState` APIs. Soft deprecations only mean that these APIs will
not be developed further; there is **no** plan to remove `PyGILState`
from Python\'s C API.

Below is the full list of soft deprecated functions and their
replacements:

1.  `PyGILState_Ensure`{.interpreted-text role="c:func"}: use
    `PyThreadState_Ensure`{.interpreted-text role="c:func"} instead.
2.  `PyGILState_Release`{.interpreted-text role="c:func"}: use
    `PyThreadState_Release`{.interpreted-text role="c:func"} instead.
3.  `PyGILState_GetThisThreadState`{.interpreted-text role="c:func"}:
    use `PyThreadState_Get`{.interpreted-text role="c:func"} or
    `PyThreadState_GetUnchecked`{.interpreted-text role="c:func"}
    instead.
4.  `PyGILState_Check`{.interpreted-text role="c:func"}: use
    `PyThreadState_GetUnchecked() != NULL` instead.

## Additions to the Limited API

The following APIs from this PEP are to be added to the limited C API:

1.  `PyThreadState_Ensure`{.interpreted-text role="c:func"}
2.  `PyThreadState_EnsureFromView`{.interpreted-text role="c:func"}
3.  `PyThreadState_Release`{.interpreted-text role="c:func"}
4.  `PyInterpreterView`{.interpreted-text role="c:type"} (as an opaque
    structure)
5.  `PyInterpreterView_FromCurrent`{.interpreted-text role="c:func"}
6.  `PyInterpreterView_Close`{.interpreted-text role="c:func"}
7.  `PyInterpreterView_FromMain`{.interpreted-text role="c:func"}
8.  `PyInterpreterGuard`{.interpreted-text role="c:type"} (as an opaque
    structure)
9.  `PyInterpreterGuard_FromCurrent`{.interpreted-text role="c:func"}
10. `PyInterpreterGuard_Close`{.interpreted-text role="c:func"}

# Rationale

## Why a new API instead of fixing `PyGILState`?

### The term \"GIL\" in `PyGILState` is confusing for free-threading

This PEP uses the prefix `PyThreadState` instead of `PyGILState` is
because the term \"GIL\" in the C API is semantically misleading. In
modern Python versions, `PyGILState_Ensure`{.interpreted-text
role="c:func"} is about attaching a thread state, which only
incidentally acquires the GIL.

An attached thread state is still required to invoke the C API on the
free-threaded build, but with a name that contains \"GIL\", it is often
confusing to why calls to `PyGILState_Ensure` and `PyGILState_Release`
are still needed from foreign threads.

### Finalization behavior for `PyGILState_Ensure` cannot change

There will always have to be a point in a Python program where
`PyGILState_Ensure`{.interpreted-text role="c:func"} can no longer
attach a thread state. If the interpreter is long dead, then Python
obviously can\'t give a thread a way to invoke it. Unfortunately,
`PyGILState_Ensure`{.interpreted-text role="c:func"} doesn\'t have any
meaningful way to return a failure, so it has no choice but to terminate
(or hang) the thread or emit a fatal error. For example, this was
discussed in
[python/cpython#124622](https://github.com/python/cpython/issues/124622):

> I think a new GIL acquisition and release C API would be needed. The
> way the existing ones get used in existing C code is not amenible to
> suddenly bolting an error state onto; none of the existing C code is
> written that way. After the call they always just assume they have the
> GIL and can proceed. The API was designed as \"it\'ll block and only
> return once it has the GIL\" without any other option.

### `PyGILState_Ensure` can use the wrong (sub)interpreter

As of writing, the `PyGILState` functions are documented as being
unsupported in subinterpreters.

This is because `PyGILState_Ensure`{.interpreted-text role="c:func"}
doesn\'t have any way to know which interpreter created the thread, and
as such, it has to assume that it was the main interpreter. This can
lead to some spurious issues.

For example:

1.  The main thread enters a subinterpreter that creates a subthread.
2.  The subthread calls `PyGILState_Ensure`{.interpreted-text
    role="c:func"} with no knowledge of which interpreter created it.
    Thus, the subthread takes the GIL for the main interpreter.
3.  Now, the subthread might attempt to execute some resource for the
    subinterpreter. For example, the thread could have been passed a
    `PyObject *` reference to a `list`{.interpreted-text role="class"}
    object.
4.  The subthread calls `list.append`{.interpreted-text role="meth"},
    which attempts to call `PyMem_Realloc`{.interpreted-text
    role="c:func"} to resize the list\'s internal buffer.
5.  `PyMem_Realloc` uses the main interpreter\'s allocator rather than
    the subinterpreter\'s allocator, because the attached thread state
    (from `PyGILState_Ensure`) points to the main interpreter.
6.  `PyMem_Realloc` doesn\'t own the buffer in the list; crash!

The author of this PEP acknowledges that subinterpreters are not
currently a popular use-case, but believes that it would be difficult to
design a new API that does not also improve the situtation for
subinterpreters. Opting out of subinterpreter is support is available
through `PyInterpreterView_FromMain`{.interpreted-text role="c:func"}.

# Backwards Compatibility

This PEP specifies no breaking changes.

Existing code **does not** have to be rewritten to use the new APIs from
this PEP, and all `PyGILState` APIs will continue to work. Use of
`PyGILState` APIs will not emit any form of warning during compilation
or at runtime. There will merely not be any *new* `PyGILState` APIs in
future versions of Python.

# Security Implications

This PEP has no known security implications.

# How to Teach This

As with all C API functions, all the new APIs in this PEP will be
documented in the C API documentation.

## Examples

### Example: A library interface

Imagine that you\'re developing a C library for logging. You might want
to provide an API that allows users to log to a Python file object.

With this PEP, you would implement it like this:

``` c
/* Log to a Python file. No attached thread state is required by the caller. */
int
log_to_py_file_object(PyInterpreterView *view, PyObject *file,
                      PyObject *text)
{
    assert(view != NULL);
    PyThreadState *tstate = PyThreadState_EnsureFromView(view);
    if (tstate == NULL) {
        fputs("Cannot call Python.\n", stderr);
        return -1;
    }

    const char *to_write = PyUnicode_AsUTF8(text);
    if (to_write == NULL) {
        // Since the exception may be destroyed upon calling PyThreadState_Release(),
        // print out the exception ourselves.
        PyErr_Print();
        PyThreadState_Release(tstate);
        PyInterpreterGuard_Close(guard);
        return -1;
    }
    int res = PyFile_WriteString(to_write, file);
    if (res < 0) {
        PyErr_Print();
    }

    PyThreadState_Release(tstate);
    return res < 0;
}
```

### Example: Protecting locks

This example shows how to acquire a C lock in a Python method defined
from C.

If this were called from a daemon thread, the interpreter could hang the
thread while reattaching its thread state, leaving us with the lock
held, in which case any future finalizer that attempts to acquire the
lock would deadlock.

By guarding the interpreter while the lock is held, we can be sure that
the thread won\'t be clobbered or hung:

``` c
static PyObject *
critical_operation(PyObject *self, PyObject *Py_UNUSED(args))
{
    assert(PyThreadState_GetUnchecked() != NULL);
    PyInterpreterGuard *guard = PyInterpreterGuard_FromCurrent();
    if (guard == NULL) {
        /* Python is already finalizing or out of memory. */
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;
    PyMutex_Lock(&global_lock);

    /* Do something while holding the lock.
       The interpreter won't finalize during this period. */
    // ...

    PyMutex_Unlock(&global_lock);
    Py_END_ALLOW_THREADS;
    PyInterpreterGuard_Close(guard);

    Py_RETURN_NONE;
}
```

### Example: Migrating from `PyGILState` APIs

The following code uses the `PyGILState` APIs:

``` c
static int
thread_func(void *arg)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    /* It's not an issue in this example, but we just attached
       a thread state for the main interpreter. If my_method() was
       originally called in a subinterpreter, then we would be unable
       to safely interact with any objects from it. */

    // This can hang the thread during finalization, because print() will
    // detach the thread state while writing to stdout.
    if (PyRun_SimpleString("print(42)") < 0) {
        PyErr_Print();
    }
    PyGILState_Release(gstate);
    return 0;
}

static PyObject *
my_method(PyObject *self, PyObject *unused)
{
    PyThread_handle_t handle;
    PyThead_indent_t indent;

    if (PyThread_start_joinable_thread(thread_func, NULL, &ident, &handle) < 0) {
        return NULL;
    }

    // Join the thread, for example's sake.
    Py_BEGIN_ALLOW_THREADS;
    PyThread_join_thread(handle);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}
```

This is the same code, rewritten to use the new functions:

``` c
static int
thread_func(void *arg)
{
    PyInterpreterGuard *guard = (PyInterpreterGuard *)arg;
    PyThreadState *tstate = PyThreadState_Ensure(guard);
    if (tstate == NULL) {
        PyInterpreterGuard_Close(guard);
        return -1;
    }

    if (PyRun_SimpleString("print(42)") < 0) {
        PyErr_Print();
    }

    PyThreadState_Release(tstate);
    PyInterpreterGuard_Close(guard);
    return 0;
}

static PyObject *
my_method(PyObject *self, PyObject *unused)
{
    PyThread_handle_t handle;
    PyThead_indent_t indent;

    PyInterpreterGuard *guard = PyInterpreterGuard_FromCurrent();
    if (guard == NULL) {
        return NULL;
    }

    if (PyThread_start_joinable_thread(thread_func, guard, &ident, &handle) < 0) {
        PyInterpreterGuard_Close(guard);
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    PyThread_join_thread(handle);
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}
```

### Example: A daemon thread

With this PEP, \"daemon\" threads (that is, threads that hang upon
thread state attachment during interpreter finalization) are very
similar to how foreign threads work in the C API today. After calling
`PyThreadState_Ensure`{.interpreted-text role="c:func"}, simply close
the interpreter guard to allow the interpreter to shut down (and hang
the current thread forever). It is worth noting that this is not
possible when using `PyThreadState_EnsureFromView`{.interpreted-text
role="c:func"}, because the relevant interpreter guard is owned by the
thread state.

``` c
static int
thread_func(void *arg)
{
    PyInterpreterGuard *guard = (PyInterpreterGuard *)arg;
    PyThreadState *tstate = PyThreadState_Ensure(guard);
    if (tstate == NULL) {
        // Out of memory.
        PyInterpreterGuard_Close(guard);
        return -1;
    }

    // If no other guards are left, the interpreter may now finalize.
    PyInterpreterGuard_Close(guard);

    // This will detach the thread state while writing to stdout, which
    // will in turn allow for the thread to hang when attempting to reattach.
    if (PyRun_SimpleString("print(42)") < 0) {
        PyErr_Print();
    }

    PyThreadState_Release(tstate);
    return 0;
}

static PyObject *
my_method(PyObject *self, PyObject *unused)
{
    PyThread_handle_t handle;
    PyThead_indent_t indent;

    PyInterpreterGuard *guard = PyInterpreterGuard_FromCurrent();
    if (guard == NULL) {
        return NULL;
    }

    if (PyThread_start_joinable_thread(thread_func, guard, &ident, &handle) < 0) {
        PyInterpreterGuard_Close(guard);
        return NULL;
    }
    Py_RETURN_NONE;
}
```

### Example: An asynchronous callback

``` c
static int
async_callback(void *arg)
{
    PyInterpreterView *view = (PyInterpreterView *)arg;
    // Try to create and attach a thread state based on our view.
    PyThreadState *tstate = PyThreadState_EnsureFromView(view);
    if (tstate == NULL) {
        PyInterpreterView_Close(view);
        return -1;
    }

    // Execute our Python code, now that we have an attached thread state.
    if (PyRun_SimpleString("print(42)") < 0) {
        PyErr_Print();
    }

    PyThreadState_Release(tstate);

    // In this example, we'll close the view for completeness.
    // If we wanted to use this callback again, we'd have to keep it alive.
    PyInterpreterView_Close(view);

    return 0;
}

static PyObject *
setup_callback(PyObject *self, PyObject *unused)
{
    PyInterpreterView *view = PyInterpreterView_FromCurrent();
    if (view == NULL) {
        return NULL;
    }

    MyNativeLibrary_RegisterAsyncCallback(async_callback, view);
    Py_RETURN_NONE;
}
```

### Example: Implementing your own `PyGILState_Ensure`

Using `PyInterpreterView_FromMain`{.interpreted-text role="c:func"}, we
can replicate the behavior of `PyGILState_Ensure`/`PyGILState_Release`.
For example:

``` c
PyThreadState *
MyGILState_Ensure(void)
{
    PyInterpreterView *view = PyInterpreterView_FromMain();
    if (view == NULL) {
        // Out of memory.
        PyThread_hang_thread();
    }

    PyThreadState *tstate = PyThreadState_EnsureFromView(view);
    PyInterpreterView_Close(view);
    return tstate;
}

#define MyGILState_Release PyThreadState_Release
```

# Reference Implementation

A reference implementation of this PEP can be found at
[python/cpython#133110](https://github.com/python/cpython/pull/133110).

# Rejected Ideas

## Hard deprecating `PyGILState`

This PEP used to specify a \"hard\" deprecation of all APIs in the
`PyGILState` family, with a planned removal in Python 3.20 (five years)
or Python 3.25 (ten years).

This was eventually decided against, because while it is acknowledged
that `PyGILState_Ensure` does have some fundamental flaws, it has worked
for over twenty years, and migrating everything would simply be too
large of a change for Python\'s ecosystem.

Even with the finalization issues addressed by this PEP, a large
majority of existing code that uses `PyGILState_Ensure` currently works,
and will continue to work regardless of whether new APIs exist.

## Interpreter reference counting

There were two iterations of this proposal that both specified that an
interpreter maintain a reference count and would wait for that count to
reach zero before shutting down.

The first iteration of this idea did this by adding implicit reference
counting to `PyInterpreterState *` pointers. A function known as
`PyInterpreterState_Hold` would increment the reference count (making it
a \"strong reference\"), and `PyInterpreterState_Release` would
decrement it. An interpreter\'s ID (a standalone `int64_t`) was used as
a form of weak reference, which could be used to look up an interpreter
state and atomically increment its reference count.

These ideas were ultimately rejected because they seemed to make things
very confusing. All uses of `PyInterpreterState *` would be implicitly
borrowed or strong, making it difficult for developers to understand
which parts of their code require or use a strong reference. This issue
has already been acknowledged with `PyObject *` in Python\'s C API.

In response to that pushback, this PEP specified `PyInterpreterRef` APIs
that would also mimic reference counting, but in a more explicit manner
that made it easier for developers. `PyInterpreterRef` was analogous to
`PyInterpreterGuard`{.interpreted-text role="c:type"} in this PEP.
Similarly, the older revision included `PyInterpreterWeakRef`, which was
analogous to `PyInterpreterView`{.interpreted-text role="c:type"}.

Eventually, the notion of reference counting was completely abandoned
from this proposal for a few reasons:

1.  There was concern over overcomplication in the API design; the
    reference counting design looked very similar to HPy\'s, which had
    no precedent in CPython. There was fear that this proposal was going
    to be used as precedent to introduce HPy into CPython.
2.  Unlike traditional reference counting APIs, acquiring a strong
    reference to an interpreter could fail at any time, and an
    interpreter would not be deallocated immediately when its reference
    count reached zero.
3.  There was prior discussion about adding \"true\" reference counting
    to interpreters (which would deallocate upon reaching zero), which
    would have been very confusing if there was an existing API in
    CPython titled `PyInterpreterRef` that did something different.

## Non-daemon thread states

In earlier revisions of this PEP, interpreter guards were only ever a
property of a thread state rather than a property of an interpreter.
This meant that `PyThreadState_Ensure`{.interpreted-text role="c:func"}
kept an interpreter guard held, and it was closed upon calling
`PyThreadState_Release`{.interpreted-text role="c:func"}. A thread state
that had a guard to an interpreter was known as a \"non-daemon thread
state\".

Functionally, this proposal still has this behavior under
`PyThreadState_EnsureFromView`{.interpreted-text role="c:func"}, but
this is not the default behavior. Additionally, the term \"non-daemon\"
was confusing in contrast to `threading`{.interpreted-text role="mod"}
threads, because non-daemon `~threading.Thread`{.interpreted-text
role="class"} objects are explicitly joined, whereas a non-daemon
foreign thread would be only be waited on to release its guard.

## Using `PyStatus` for the return value of `PyThreadState_Ensure`

In prior iterations of this API,
`PyThreadState_Ensure`{.interpreted-text role="c:func"} returned a
`PyStatus`{.interpreted-text role="c:type"} to denote failure, which had
the benefit of providing an error message.

This was rejected because it\'s not clear that an error message would be
all that useful, and it would make the new API more cumbersome to use.

# Acknowledgements

This PEP is based on prior work, feedback, and discussions from many
people, including Victor Stinner, Antoine Pitrou, David Woods, Sam
Gross, Matt Page, Ronald Oussoren, Matt Wozniski, Eric Snow, Steve
Dower, Petr Viktorin, Gregory P. Smith, Alyssa Coghlan, and Python\'s
2026 Steering Council.

# Copyright

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
