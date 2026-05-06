# Functions

## Defining Functions

```python
def greet(name, greeting="Hello"):
    """One-line summary if truly needed."""
    return f"{greeting}, {name}!"

result = greet("Alice")           # "Hello, Alice!"
result = greet("Bob", "Hi")       # "Hi, Bob!"
result = greet(greeting="Hey", name="Carol")  # keyword arguments
```

- `return` without a value returns `None`. A function with no `return` also returns `None`.
- Functions are **first-class objects**: they can be stored in variables, passed as arguments, and returned from other functions.

---

## Argument Types

### Positional and Keyword Arguments

```python
def func(a, b, c):
    ...

func(1, 2, 3)               # positional
func(a=1, b=2, c=3)         # keyword
func(1, c=3, b=2)           # mixed — positional must come first
```

### Default Arguments

Default values are evaluated **once at function definition time**, not on each call.

```python
# Bug: mutable default
def append(x, lst=[]):     # lst is shared across all calls
    lst.append(x)
    return lst

# Correct pattern
def append(x, lst=None):
    lst = lst if lst is not None else []
    lst.append(x)
    return lst
```

### *args — Variable Positional Arguments

Collects extra positional arguments into a tuple:

```python
def add(*numbers):
    return sum(numbers)

add(1, 2, 3, 4)   # 10
```

### **kwargs — Variable Keyword Arguments

Collects extra keyword arguments into a dict:

```python
def configure(**options):
    for key, val in options.items():
        print(f"{key} = {val}")

configure(debug=True, verbose=False)
```

### Full signature order

```python
def full(pos_only, /, standard, *, kw_only, **kwargs):
    ...
```

- `/`: parameters before it are positional-only (Python 3.8+)
- `*`: parameters after it are keyword-only

```python
def func(a, b, /, c, *, d, e):
    ...

func(1, 2, 3, d=4, e=5)   # a,b positional-only; d,e keyword-only
```

### Unpacking at call site

```python
args   = [1, 2, 3]
kwargs = {'sep': '-', 'end': '\n'}

func(*args)        # unpacks list as positional args
func(**kwargs)     # unpacks dict as keyword args
func(*args, **kwargs)
```

---

## Scope: LEGB Rule

Python resolves names in this order:

1. **L**ocal — inside the current function
2. **E**nclosing — in any enclosing function's scope (for closures)
3. **G**lobal — module-level names
4. **B**uilt-in — `len`, `print`, `range`, etc.

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)    # "local"

    inner()
    print(x)        # "enclosing"

outer()
print(x)            # "global"
```

### global and nonlocal

```python
count = 0

def increment():
    global count    # without this, assignment creates a local variable
    count += 1

def make_counter():
    n = 0
    def increment():
        nonlocal n  # modify enclosing scope variable
        n += 1
        return n
    return increment
```

Avoid `global` in production code — it creates tight coupling and makes functions unpredictable.

---

## Closures

A **closure** is a function that remembers the variables from its enclosing scope even after that scope has exited.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor   # factor is captured from enclosing scope
    return multiply

triple = make_multiplier(3)
triple(10)   # 30
```

The returned function `multiply` carries a reference to `factor`. This is the mechanism behind factory functions, partial application, and decorators.

**Common gotcha** with closures in loops:

```python
# Bug: all functions share the same 'i' (late binding)
funcs = [lambda: i for i in range(3)]
funcs[0]()   # 2, not 0!

# Fix: capture by default argument
funcs = [lambda i=i: i for i in range(3)]
funcs[0]()   # 0
```

---

## Lambda Functions

Anonymous one-expression functions. Limited to a single expression; cannot contain statements.

```python
square = lambda x: x ** 2
square(5)   # 25

# Typical use: as a key argument
pairs = [(1, 'b'), (3, 'a'), (2, 'c')]
sorted(pairs, key=lambda pair: pair[1])   # sort by second element
```

For anything more complex than a single expression, use a named `def`. Lambdas in assignment (`f = lambda x: ...`) offer no advantage over `def f(x): ...`.

---

## Decorators

A decorator is a function that **wraps another function** to extend its behavior without modifying it.

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
say_hello()
# Before
# Hello!
# After
```

### functools.wraps

Always use `@functools.wraps(func)` inside a decorator to preserve the original function's metadata (`__name__`, `__doc__`):

```python
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Decorators with Arguments

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
```

### Stacking Decorators

```python
@decorator_a
@decorator_b
def func():
    ...
# Equivalent to: func = decorator_a(decorator_b(func))
# decorator_b is applied first (innermost)
```

### Common Built-in Decorators

| Decorator | Effect |
|-----------|--------|
| `@staticmethod` | No `self`/`cls`; behaves like a plain function in a class namespace |
| `@classmethod` | Receives `cls` instead of `self`; used for alternate constructors |
| `@property` | Turns a method into a read-only attribute |
| `@functools.lru_cache` | Memoize function results (covered in [05_functional_programming.md](05_functional_programming.md)) |
| `@dataclasses.dataclass` | Auto-generate `__init__`, `__repr__`, `__eq__` for classes |

---

## Type Annotations on Functions

```python
def process(data: list[int], scale: float = 1.0) -> list[float]:
    return [x * scale for x in data]
```

For callables as parameters:

```python
from typing import Callable

def apply(func: Callable[[int], int], values: list[int]) -> list[int]:
    return [func(x) for x in values]
```
