# Exceptions

## TL;DR

Exceptions are objects that signal something went wrong. When one is **raised**, Python unwinds the call stack until it finds a matching `except` clause; if none does, the program terminates with a traceback. The block structure has four parts: `try` (the protected code), `except` (handler, possibly multiple), `else` (runs only if no exception was raised), `finally` (always runs, before any return or propagation). Catch the **narrowest** exception type that covers your case — `except Exception` (and especially `except BaseException`) hides bugs. Pythonic style is **EAFP** (Easier to Ask Forgiveness than Permission): try the operation and handle failure, instead of pre-checking conditions. **Custom exceptions** subclass `Exception` and let callers handle application errors generically; keep the hierarchy shallow. **Context managers** (`with` statement) generalise the resource-acquire / cleanup pattern far beyond file handles — write them as classes with `__enter__` / `__exit__` or as `@contextlib.contextmanager` generators. Two operational rules: never silently swallow an exception (always log or re-raise), and prefer `logger.exception(...)` over `logger.error(...)` inside `except` blocks because it captures the full traceback.

## Cheatsheet

| Pattern | Syntax | When |
|---|---|---|
| Try / handle | `try: ... except E: ...` | Any failure-handling code |
| Multiple types | `except (E1, E2):` | Same handler for several types |
| Bind exception | `except E as e:` | Need access to the exception object |
| Else | `try: ... except: ... else: ...` | Code that should run only on success |
| Finally | `try: ... finally: ...` | Cleanup that must always run |
| Raise | `raise ValueError("msg")` | Signal an error |
| Re-raise | bare `raise` inside `except` | Preserve the original traceback |
| Chained raise | `raise NewError(...) from e` | Wrap a low-level error in a higher-level one |
| Suppress chain | `raise NewError(...) from None` | Hide the underlying cause |
| Custom exception | `class AppError(Exception):` | Application-specific errors |
| Context manager | `with cm:` | Resource cleanup, always runs |
| Suppress exception | `with contextlib.suppress(E):` | Best-effort cleanup |
| Log + traceback | `logger.exception("...")` inside `except` | Logs message + full stack |

---

## Exception basics

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    result = 0
```

When the `try` block raises a matching exception type, control jumps to the `except` block. If no exception is raised, the `except` block is skipped. If the raised exception doesn't match any `except` clause, it propagates up the call stack until something catches it or the program crashes with a traceback.

---

## `try` / `except` / `else` / `finally`

The full structure offers four distinct concerns:

```python
try:
    value = int(input("Enter a number: "))
    result = 100 / value
except ValueError:
    print("Not a valid integer")
except ZeroDivisionError:
    print("Cannot divide by zero")
except (TypeError, AttributeError) as e:        # multiple types, bind to e
    print(f"Type error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise                                       # re-raise without losing the traceback
else:
    # runs only if NO exception was raised in the try block
    print(f"Result: {result}")
finally:
    # ALWAYS runs: exception or not, return or not
    print("Cleanup done")
```

### When to use each clause

- **`except`** — handle or log the error. Catch the most specific type that makes sense.
- **`else`** — code that should run only if the `try` succeeded. Putting it here (rather than at the end of the `try` block) keeps the success path out of the protected region, so its exceptions are not accidentally caught by the `except`.
- **`finally`** — resource cleanup that must happen regardless of outcome (close files, release locks, disconnect from databases). Runs before any `return`, exception propagation, or even `sys.exit`.

---

## Exception hierarchy

```
BaseException
├── SystemExit                  # raised by sys.exit()
├── KeyboardInterrupt           # Ctrl+C
├── GeneratorExit               # generator .close()
└── Exception                   # base for all "normal" exceptions
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── ValueError
    ├── TypeError
    ├── AttributeError
    ├── NameError
    ├── OSError (FileNotFoundError, PermissionError, ConnectionError, ...)
    ├── RuntimeError
    │   └── RecursionError
    ├── StopIteration
    └── NotImplementedError
```

**Never catch `BaseException` or `Exception` silently** (without re-raising or logging). It hides bugs, including programmer errors like typos that raise `NameError`, and it can also swallow `KeyboardInterrupt` if you go too high in the hierarchy.

Catching a parent class catches all its subclasses:

```python
except LookupError:                 # catches both IndexError and KeyError
    ...
```

This is useful for high-level groups (`except OSError` covers all file/network errors) but be deliberate — broader handlers risk hiding more.

---

## Raising exceptions

```python
raise ValueError("Value must be positive")
raise TypeError(f"Expected int, got {type(x).__name__}")

# Re-raise the current exception (preserves the original traceback)
try:
    ...
except SomeError:
    log_error()
    raise                                   # bare raise inside except

# Chain explicitly: wrap a low-level error in a higher-level one
try:
    connect()
except ConnectionError as e:
    raise RuntimeError("Failed to initialize") from e

# Suppress the chain (rare, but useful when wrapping public APIs)
raise NewError("...") from None
```

`raise ... from e` adds an explicit "during handling of X, Y occurred" link to the traceback, which makes debugging much easier than a bare `raise NewError(...)` that loses the cause. `from None` strips the chain — appropriate when the underlying error would only confuse callers.

---

## Custom exceptions

Define application-specific exceptions by subclassing `Exception`. The pattern is to declare a base class for your application and have every other exception inherit from it, so callers can catch all your errors generically with one `except`:

```python
class AppError(Exception):
    """Base class for all application errors."""

class ValidationError(AppError):
    def __init__(self, field, message):
        self.field = field
        super().__init__(f"{field}: {message}")

class NotFoundError(AppError):
    pass

# Usage
try:
    raise ValidationError("email", "must contain @")
except ValidationError as e:
    print(e.field)              # "email"
    print(str(e))               # "email: must contain @"
except AppError:
    # catch any application-specific error generically
    ...
```

Keep the hierarchy shallow. A deep tree of exception types adds complexity and rarely earns its keep; prefer a few well-named types that carry **structured data** (field names, error codes, IDs) over many narrow types that say nothing the message couldn't.

---

## Context managers

A context manager is an object that defines `__enter__` and `__exit__`. The `with` statement guarantees that `__exit__` runs no matter how the block ends — normal completion, exception, even `sys.exit` (it does not run on `os._exit`, which bypasses cleanup entirely).

```python
with open("file.txt", "r") as f:
    data = f.read()
# f is automatically closed here, even if an exception was raised inside the block
```

`__exit__` receives information about any exception that occurred (`exc_type`, `exc_val`, `exc_tb`). If it returns truthy, the exception is **suppressed**; if it returns falsy or `None`, the exception continues to propagate.

### Writing context managers

#### As a class

```python
class ManagedResource:
    def __enter__(self):
        self.resource = acquire()
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        release(self.resource)
        return False                # don't suppress exceptions
```

#### As a generator with `contextlib`

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield                       # execution continues inside the with block
    finally:
        elapsed = time.time() - start
        print(f"Elapsed: {elapsed:.3f}s")

with timer():
    do_something()
```

`@contextmanager` converts a single-`yield` generator function into a context manager. Code before `yield` is the entry; code after (typically inside `finally`) is the exit. The `try/finally` is essential — without it, exceptions in the `with` block would skip cleanup.

### `contextlib` utilities

```python
from contextlib import suppress, nullcontext, ExitStack

# Suppress specific exceptions inside a block
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Conditional context manager
cm = lock if thread_safe else nullcontext()
with cm:
    shared_data.update(...)

# Stack of context managers, useful for dynamic numbers
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
```

`ExitStack` is the right tool when the number of context managers is dynamic (e.g., opening N files at once where N is unknown).

---

## Exception best practices

**Be specific** — catch the narrowest exception that covers your case:

```python
# Too broad — hides bugs
try:
    result = compute(data)
except Exception:
    result = default

# Specific
try:
    result = compute(data)
except (KeyError, ValueError) as e:
    logger.warning("Bad input: %s", e)
    result = default
```

**EAFP over LBYL**: Pythonic style is "Easier to Ask Forgiveness than Permission" — try the operation and handle failure, rather than pre-checking conditions:

```python
# LBYL (Look Before You Leap)
if key in d:
    value = d[key]

# EAFP (Easier to Ask Forgiveness than Permission)
try:
    value = d[key]
except KeyError:
    value = default
```

EAFP is preferred when the "happy path" is the common case (saves a lookup) and when there's a race condition between the check and the action (LBYL is unsafe in concurrent code). LBYL still wins when the check is dramatically cheaper than the operation (e.g., `os.path.exists` before a network call).

**Always log or re-raise** — never silently swallow an exception:

```python
import logging

logger = logging.getLogger(__name__)

try:
    risky_operation()
except RiskyError:
    logger.exception("risky_operation failed")      # logs the message AND the full traceback
    raise
```

`logger.exception(...)` automatically includes the current traceback; always prefer it over `logger.error(...)` inside an `except` block.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Bare `except:` | Catches `KeyboardInterrupt`, `SystemExit`, hides bugs | Use `except Exception:` at minimum, narrower if possible |
| Catching `Exception` and discarding | Silent failures, debugging nightmare | Always log or re-raise |
| Re-raising with `raise e` | Loses the original traceback | Use bare `raise` to preserve it |
| `raise NewError("...")` without `from` | Original cause is hidden | `raise NewError("...") from e` |
| `finally` with `return` | Suppresses any exception that was propagating | Avoid `return` in `finally` unless intentional |
| Mutable class attribute as exception arg | Shared state across instances | Pass values, not mutables |
| `__init__` of custom exception not calling `super().__init__()` | `str(e)` is empty, repr is uninformative | Call `super().__init__(message)` |
| `except` clauses not in specificity order | Broader clause catches first, narrower never fires | List most specific first |
| Logger inside except using `error` not `exception` | Loses the stack trace | Use `logger.exception(...)` |
| Closing files manually instead of `with` | Easy to forget on exception path | Use `with open(...)` |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Standard error handling | `try` / `except` | Pythonic, structured |
| Cleanup that must always run | `finally` or context manager | Guaranteed execution |
| "Only on success" code | `else` | Keeps success out of the protected region |
| Resource acquire / release | Context manager | `with`-statement scoping |
| Multiple resources, dynamic count | `contextlib.ExitStack` | Stacks managers cleanly |
| Best-effort cleanup ignoring specific errors | `contextlib.suppress(E)` | More explicit than empty `except` |
| Wrap low-level error in high-level | `raise NewError(...) from e` | Preserves the cause chain |
| Hide low-level error from caller | `raise NewError(...) from None` | Truncates the chain |
| Application-wide error type | Custom subclass of `Exception` | Generic catch + structured data |
| Inline log with traceback | `logger.exception(...)` | Captures full stack |
| Pre-check is cheap, action is expensive | LBYL with `if` | Avoid the cost of failure |
| Action is the common case, failure is rare | EAFP with `try` | Faster and race-free |

---

## See also

- [04_functions.md](04_functions.md) — `try` / `finally` inside functions, decorators that handle errors
- [06_oop.md](06_oop.md) — `__enter__` / `__exit__` as part of the data model
- [09_file_io.md](09_file_io.md) — `with open(...)` and file-related exceptions
- [10_environments_and_tooling.md](10_environments_and_tooling.md) — logging configuration
