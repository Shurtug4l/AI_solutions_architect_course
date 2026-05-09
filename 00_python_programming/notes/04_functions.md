# Functions

## TL;DR

Functions in Python are first-class objects: they can be passed around, returned, and assigned like any other value. Their signatures are flexible — `*args` collects extra positional arguments, `**kwargs` collects extra keyword arguments, and the markers `/` and `*` enforce positional-only and keyword-only calling conventions. Three traps recur in practice. **Mutable default arguments** (lists, dicts) are evaluated once at definition time and shared across all calls, leading to silent state leakage. **Closures created in loops** bind the loop variable by reference, so every callable ends up reading the final value at call time. **Assignment inside a function** creates a new local variable unless `global` or `nonlocal` is declared, silently shadowing outer names. **Decorators** are functions that wrap functions to extend their behavior; always pair them with `functools.wraps` to preserve `__name__`, `__doc__`, and the signature — otherwise debuggers, IDEs, and introspection tools all break.

## Cheatsheet

| Pattern | Syntax | Key note |
|---|---|---|
| Default arg | `def f(x=10)` | Evaluated once at def time — never `[]`, `{}`, or any mutable as default |
| Variable positional | `def f(*args)` | Collects extra positional args into a **tuple** |
| Variable keyword | `def f(**kwargs)` | Collects extra keyword args into a **dict** |
| Positional-only | `def f(x, /)` | Caller cannot pass `x=...`; useful for fast paths and stable APIs (3.8+) |
| Keyword-only | `def f(*, x)` | Caller must use `x=...`; prevents argument-order bugs |
| Unpack at call site | `f(*lst, **dct)` | Spread an iterable / mapping into the call |
| Closure with mutation | `def outer(): nonlocal x` | Inner function writes to the outer binding |
| Decorator | `@dec` above `def f` | Sugar for `f = dec(f)`, applied at definition time |
| Decorator with args | `@dec(n)` | Factory pattern: `dec(n)` returns the actual decorator |
| Type hints | `def f(x: int) -> str` | PEP 484, runtime no-op — checked by mypy / pyright |

---

## Defining functions

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")                          # "Hello, Alice!"
greet("Bob", "Hi")                      # "Hi, Bob!"
greet(greeting="Hey", name="Carol")     # all-keyword call
```

A function with no `return`, or a bare `return`, returns `None`. Functions are **first-class objects**: you can store them in variables, pass them as arguments, return them from other functions, and even assign attributes to them. This is the foundation of higher-order programming, factory patterns, and decorators.

---

## Argument types

### Positional and keyword

Positional arguments are matched by position; keyword arguments are matched by name. They can be mixed in a single call, but every positional must come before any keyword.

```python
def func(a, b, c): ...

func(1, 2, 3)               # all positional
func(a=1, b=2, c=3)         # all keyword
func(1, c=3, b=2)           # mixed; positional first
```

### Default arguments

Default values are evaluated **once at function definition time**, not on each call. This is fine for immutable defaults (numbers, strings, tuples) but a classic source of bugs with mutable ones:

```python
# Bug: every call shares the same list
def append(x, lst=[]):
    lst.append(x)
    return lst

append(1)   # [1]
append(2)   # [1, 2]   not the fresh list you expected

# Correct: use a None sentinel and create a new list inside the body
def append(x, lst=None):
    lst = lst if lst is not None else []
    lst.append(x)
    return lst
```

The same trap applies to dicts, sets, and any user-defined mutable object.

### `*args` and `**kwargs`

`*args` gathers leftover positional arguments into a tuple; `**kwargs` gathers leftover keyword arguments into a dict. The names `args` and `kwargs` are conventional, not required — what matters are the `*` and `**` markers.

```python
def add(*numbers):              # numbers is a tuple
    return sum(numbers)

def configure(**options):       # options is a dict
    for key, val in options.items():
        print(f"{key} = {val}")
```

### Full signature order

Python supports a precise ordering of parameter kinds:

```python
def full(pos_only, /, standard, *, kw_only, **kwargs):
    ...
```

- `/` — every parameter to its left is **positional-only**: it cannot be passed by name.
- `*` — every parameter to its right is **keyword-only**: it must be passed by name.

```python
def func(a, b, /, c, *, d, e): ...

func(1, 2, 3, d=4, e=5)         # a, b positional-only; d, e keyword-only
func(a=1, b=2, c=3, d=4, e=5)   # SyntaxError: a, b cannot be keyword
```

Use positional-only for short, performance-sensitive APIs (e.g., math functions). Use keyword-only when argument order is non-obvious or when you want to add new parameters later without breaking callers.

### Unpacking at call site

The same `*` and `**` markers, used at the call site, **spread** an iterable or mapping into the call:

```python
args   = [1, 2, 3]
kwargs = {'sep': '-', 'end': '\n'}

func(*args)         # equivalent to func(1, 2, 3)
func(**kwargs)      # equivalent to func(sep='-', end='\n')
func(*args, **kwargs)
```

---

## Scope: LEGB rule

When you reference a name, Python searches scopes in this order:

1. **L**ocal — the current function.
2. **E**nclosing — any outer function (relevant for closures).
3. **G**lobal — module level.
4. **B**uilt-in — `len`, `print`, `range`, etc.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)        # "local"
    inner()
    print(x)            # "enclosing"

outer()
print(x)                # "global"
```

The lookup is for **reading** a name. Writing is different: assignment inside a function always creates a new local binding, unless you explicitly opt out.

### `global` and `nonlocal`

`global` declares that an assignment refers to a module-level name. `nonlocal` does the same for the nearest enclosing function scope.

```python
count = 0

def increment():
    global count        # without this, '+=' would create a local 'count'
    count += 1

def make_counter():
    n = 0
    def increment():
        nonlocal n      # writes to the enclosing 'n'
        n += 1
        return n
    return increment
```

Avoid `global` in production code: it creates implicit dependencies on module state, which makes functions hard to test and reason about. Prefer passing values explicitly or using a class to hold state.

---

## Closures

A closure is a function that retains references to variables from its enclosing scope, even after that scope has finished executing. It is the mechanism behind factory functions, partial application, and decorators.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor   # 'factor' is captured from the enclosing scope
    return multiply

triple = make_multiplier(3)
triple(10)                  # 30
```

The closure captures the **variable name**, not the value at capture time. This produces a famous gotcha in loops:

```python
# Bug: all functions share the same 'i', read at call time
funcs = [lambda: i for i in range(3)]
funcs[0]()      # 2, not 0!
funcs[1]()      # 2
funcs[2]()      # 2
```

When the lambda runs, it looks up `i` in the enclosing scope, which by then holds the loop's final value. The standard fix is to capture the current value of `i` as a default argument, since defaults are bound at definition time:

```python
funcs = [lambda i=i: i for i in range(3)]
funcs[0]()      # 0
funcs[1]()      # 1
funcs[2]()      # 2
```

---

## Lambda

Lambdas are anonymous one-expression functions. They cannot contain statements (no `if`, `for`, `return`), only expressions.

```python
square = lambda x: x ** 2
square(5)                       # 25

# The idiomatic use: as a 'key' callable
pairs = [(1, 'b'), (3, 'a'), (2, 'c')]
sorted(pairs, key=lambda pair: pair[1])     # [(3,'a'), (1,'b'), (2,'c')]
```

Use lambdas where the function is genuinely one-off and inline — typically as the `key=` argument of `sorted` / `min` / `max`, or inside `map` / `filter`. Once you find yourself wanting to break it across lines, switch to a named `def`. Assigning a lambda to a variable (`f = lambda x: ...`) provides no benefit over `def f(x): ...`, and it costs you the function name in tracebacks.

---

## Decorators

A decorator wraps another function to extend its behavior — logging, timing, caching, access control — without modifying the original. The `@` syntax is sugar for assigning the wrapped result back to the original name.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

# Equivalent to: say_hello = my_decorator(say_hello)
```

### `functools.wraps`

A decorator naively replaces the function with `wrapper`, so the original `__name__`, `__doc__`, and signature are lost. This breaks IDE help, debuggers, and any tool that introspects functions. `functools.wraps` copies the metadata from the wrapped function onto the wrapper — make it the default reflex inside any decorator you write.

```python
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Decorators with arguments

When a decorator takes arguments, you need an extra layer: the outer call returns the actual decorator, which then wraps the function.

```python
def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hi!")

greet()     # prints "Hi!" three times
```

### Stacking decorators

Multiple decorators apply bottom-up: the one closest to the `def` runs first.

```python
@decorator_a
@decorator_b
def func(): ...

# Equivalent to: func = decorator_a(decorator_b(func))
# decorator_b wraps func first, decorator_a wraps the result.
```

### Built-in decorators worth knowing

| Decorator | When to reach for it |
|---|---|
| `@staticmethod` | Utility logic that lives in a class namespace but doesn't need `self` or `cls` |
| `@classmethod` | Alternate constructors (`from_dict`, `from_string`) and methods that operate on the class itself |
| `@property` | Expose a computed value as a read-only attribute, e.g. `circle.area` |
| `@functools.lru_cache(maxsize=N)` | Memoize a pure function whose arguments are hashable |
| `@functools.cached_property` | Compute an expensive attribute once per instance, cache the result |
| `@dataclasses.dataclass` | Auto-generate `__init__`, `__repr__`, `__eq__` for plain data containers |

---

## Type annotations

Type hints describe expected types but are **not enforced at runtime**: a function annotated `x: int` will still accept whatever you pass. Their purpose is to feed static analysers (`mypy`, `pyright`) and IDEs, which catch mismatches before the code runs and enable richer autocomplete.

```python
def process(data: list[int], scale: float = 1.0) -> list[float]:
    return [x * scale for x in data]

from typing import Callable
def apply(func: Callable[[int], int], values: list[int]) -> list[int]:
    return [func(x) for x in values]
```

In Python 3.10+ the syntax is lighter:

- `int | str` instead of `Union[int, str]`
- `int | None` instead of `Optional[int]`
- `list[int]`, `dict[str, float]` directly (no `List`, `Dict` imports)

For more complex shapes (protocols, generics, type variables), `typing.Protocol`, `TypeVar`, and `Generic` cover most needs.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Mutable default argument | A list/dict accumulates state across calls when it should be fresh | Use a `None` sentinel and create the container inside the body |
| Closure late binding in loop | All callables produced in the loop read the final loop value | Capture the value with a default argument: `lambda i=i: ...` |
| Missing `global` / `nonlocal` | Assignment creates a new local; the outer name remains unchanged | Add `global x` (module level) or `nonlocal x` (enclosing function) |
| Decorator without `functools.wraps` | `__name__` and `__doc__` are lost; introspection and debuggers break | Always wrap your wrapper with `@functools.wraps(func)` |
| Positional after keyword in a call | `SyntaxError: positional argument follows keyword argument` | Reorder, or unpack a tuple/list with `*` |
| `*args` vs `**kwargs` confusion | Wrong type passed downstream (tuple where dict expected, or vice versa) | Remember: `*args` is a tuple, `**kwargs` is a dict |
| Returning the inner closure but forgetting to call it | You receive a `function` object instead of the value | If the factory returns a callable, you need to call it: `factory()()` |
| Lambda assigned to a name | Tracebacks show `<lambda>` instead of a useful name | Use `def` for anything reused or worth naming |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Reusable function, more than one line | `def` | Named, debuggable, can carry a docstring |
| Inline callback (`key=`, `filter`, `map`) | `lambda` | Self-contained, no namespace pollution |
| Alternate constructor for a class | `@classmethod` | Receives `cls`, builds new instances |
| Utility that doesn't use `self` / `cls` | `@staticmethod` | Logically grouped under the class but doesn't depend on state |
| Computed read-only attribute | `@property` | Looks like an attribute to callers, no parentheses |
| Memoize a pure function | `@functools.lru_cache` | Saves repeated work for the same arguments |
| Cache an attribute on first access | `@functools.cached_property` | Per-instance lazy computation |
| Boilerplate-free data container | `@dataclasses.dataclass` | Auto `__init__`, `__repr__`, `__eq__` |
| Add cross-cutting concern (logging, timing, retry) | Custom decorator | Keeps the original function focused on its job |
| Forward arbitrary args to a wrapped callable | `*args, **kwargs` + unpacking | Future-proof against signature changes |

---

## See also

- [05_functional_programming.md](05_functional_programming.md) — `partial`, `reduce`, `map` / `filter`, generators, comprehensions
- [06_oop.md](06_oop.md) — `@property`, `@classmethod`, `@staticmethod` in class context
- [07_exceptions.md](07_exceptions.md) — `try` / `finally`, error handling patterns inside functions
- [10_environments_and_tooling.md](10_environments_and_tooling.md) — type checking with `mypy`, formatting tools
