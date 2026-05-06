# Exceptions

## Exception Basics

Exceptions are objects that signal that something went wrong. When an exception is **raised**, Python unwinds the call stack until it finds a matching `except` clause. If none is found, the program terminates with a traceback.

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    result = 0
```

---

## try / except / else / finally

```python
try:
    value = int(input("Enter a number: "))
    result = 100 / value
except ValueError:
    print("Not a valid integer")
except ZeroDivisionError:
    print("Cannot divide by zero")
except (TypeError, AttributeError) as e:  # catch multiple, bind to e
    print(f"Type error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise                                  # re-raise without losing traceback
else:
    # runs only if NO exception was raised in the try block
    print(f"Result: {result}")
finally:
    # ALWAYS runs: exception or not, return or not
    print("Cleanup done")
```

### When to use each clause

- `except`: handle or log the error
- `else`: code that should run only on success (avoids accidentally catching exceptions from the success path)
- `finally`: resource cleanup that must happen regardless (close files, release locks, disconnect)

---

## Exception Hierarchy

```
BaseException
├── SystemExit               ← raised by sys.exit()
├── KeyboardInterrupt        ← Ctrl+C
├── GeneratorExit            ← generator .close()
└── Exception                ← base for all "normal" exceptions
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
    ├── OSError (IOError, FileNotFoundError, PermissionError, ...)
    ├── RuntimeError
    │   └── RecursionError
    ├── StopIteration
    └── NotImplementedError
```

**Never catch `BaseException` or `Exception` silently** (without re-raising or logging). It hides bugs.

Catching a parent class catches all its subclasses:

```python
except LookupError:   # catches both IndexError and KeyError
```

---

## Raising Exceptions

```python
raise ValueError("Value must be positive")
raise TypeError(f"Expected int, got {type(x).__name__}")

# Re-raise the current exception (preserves original traceback)
try:
    ...
except SomeError:
    log_error()
    raise

# Raise from another exception (exception chaining)
try:
    connect()
except ConnectionError as e:
    raise RuntimeError("Failed to initialize") from e
```

`raise ... from e` links exceptions explicitly. `raise ... from None` suppresses the original exception context.

---

## Custom Exceptions

Define application-specific exceptions by subclassing `Exception`:

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
    print(e.field)    # "email"
    print(str(e))     # "email: must contain @"
except AppError:
    # catch any app-specific error
    ...
```

Keep the exception hierarchy shallow. A deep tree of exception types adds complexity; prefer fewer, more informative types with structured data (like field names or error codes).

---

## Context Managers

A context manager is an object that defines `__enter__` and `__exit__` — it is used with the `with` statement.

```python
with open("file.txt", "r") as f:
    data = f.read()
# f is automatically closed here, even if an exception occurred
```

`__exit__` receives exception info. If it returns `True`, the exception is suppressed.

### Writing context managers

#### As a class

```python
class ManagedResource:
    def __enter__(self):
        self.resource = acquire()
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        release(self.resource)
        return False   # don't suppress exceptions
```

#### As a generator with contextlib

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield              # execution continues inside the with block
    finally:
        elapsed = time.time() - start
        print(f"Elapsed: {elapsed:.3f}s")

with timer():
    do_something()
```

`contextlib.contextmanager` converts a generator function into a context manager. The code before `yield` is `__enter__`, code after is `__exit__`.

### contextlib utilities

```python
from contextlib import suppress, nullcontext

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Conditional context manager
cm = lock if thread_safe else nullcontext()
with cm:
    shared_data.update(...)
```

---

## Exception Best Practices

**Be specific**: catch the narrowest exception that covers your case.

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

**Don't use exceptions for control flow** in performance-critical code. But the EAFP (Easier to Ask Forgiveness than Permission) style is idiomatic in Python for expected failures:

```python
# LBYL (Look Before You Leap) — checks first
if key in d:
    value = d[key]

# EAFP — try and handle failure
try:
    value = d[key]
except KeyError:
    value = default
```

EAFP is preferred in Python when the "happy path" is the common case.

**Always log or re-raise**: don't silently swallow exceptions.

```python
import logging

logger = logging.getLogger(__name__)

try:
    risky_operation()
except RiskyError as e:
    logger.exception("risky_operation failed")   # logs full traceback
    raise
```

`logger.exception()` logs the message plus the full current traceback — always prefer it over `logger.error()` inside an `except` block.
