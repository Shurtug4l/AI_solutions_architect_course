# Types and Variables

## Variables and Assignment

Python variables are **references to objects**, not memory containers. Assignment binds a name to an object.

```python
x = 42          # x references an int object
y = x           # y references the same object
x = 100         # x now references a new object; y still references 42
```

Multiple assignment and unpacking:

```python
a, b, c = 1, 2, 3
a, *rest = [1, 2, 3, 4]    # a=1, rest=[2, 3, 4]
a, b = b, a                 # swap (no temp variable needed)
```

Variable names are case-sensitive. Convention: `snake_case` for variables and functions, `UPPER_CASE` for constants, `PascalCase` for classes.

---

## Built-in Types

### Numeric Types

```python
x = 42          # int (arbitrary precision, no overflow)
y = 3.14        # float (64-bit IEEE 754 double)
z = 2 + 3j      # complex

# Integer arithmetic
10 // 3         # 3  — floor division
10 % 3          # 1  — modulo
2 ** 10         # 1024 — exponentiation
abs(-7)         # 7

# Float gotcha
0.1 + 0.2       # 0.30000000000000004  — use decimal.Decimal for exact arithmetic
round(2.675, 2) # 2.67, not 2.68 — floating-point representation artifact
```

`int` has arbitrary precision in Python 3. `float` is always 64-bit; there is no `double` type.

### Booleans

```python
True + True     # 2 — bool is a subclass of int
bool(0)         # False
bool("")        # False
bool([])        # False
bool(None)      # False
bool(1)         # True (any non-zero, non-empty value)
```

Falsy values: `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False`. Everything else is truthy.

### None

The singleton representing the absence of a value. Test with `is None`, not `== None`.

```python
result = None
if result is None:
    ...
```

### Strings

Immutable sequences of Unicode characters.

```python
s = "hello"
s = 'hello'
s = """multi
line"""

# Common operations
len(s)              # 5
s.upper()           # 'HELLO'
s.strip()           # removes leading/trailing whitespace
s.split(',')        # list of parts
','.join(['a','b']) # 'a,b'
s.replace('l','r')  # 'herro'
s.startswith('he')  # True
s.find('ll')        # 2 (index); returns -1 if not found
'll' in s           # True

# Indexing and slicing (immutable, cannot assign)
s[0]        # 'h'
s[-1]       # 'o'
s[1:4]      # 'ell'
s[::-1]     # 'olleh' — reversed

# f-strings (Python 3.6+) — preferred interpolation method
name = "Alice"
age = 30
f"{name} is {age} years old"
f"{3.14159:.2f}"    # '3.14' — format spec after colon
f"{2**10 = }"       # '2**10 = 1024' — debug format (3.8+)
```

---

## Type Conversion

```python
int("42")       # 42
int(3.9)        # 3 — truncates, does not round
float("3.14")   # 3.14
str(42)         # '42'
bool(0)         # False
list("abc")     # ['a', 'b', 'c']

# Check type
type(x)             # <class 'int'>
isinstance(x, int)  # True — preferred over type() ==, handles inheritance
isinstance(x, (int, float))  # True if either
```

---

## Mutability

A key distinction in Python: **mutable** objects can be changed in place; **immutable** objects cannot.

| Immutable | Mutable |
|-----------|---------|
| `int`, `float`, `bool` | `list` |
| `str` | `dict` |
| `tuple` | `set` |
| `frozenset` | Most custom objects |
| `bytes` | `bytearray` |

Mutability matters when passing objects to functions and when using objects as dictionary keys (only hashable — immutable — objects can be dict keys).

```python
# Mutable default argument — classic bug
def append(x, lst=[]):    # lst is created once and shared across calls!
    lst.append(x)
    return lst

# Correct pattern
def append(x, lst=None):
    if lst is None:
        lst = []
    lst.append(x)
    return lst
```

---

## Identity vs Equality

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b      # True  — same value
a is b      # False — different objects in memory
a is c      # True  — same object

id(a)       # memory address of the object
```

`is` tests **object identity** (same memory address). `==` tests **value equality** (calls `__eq__`).

Use `is` only for `None`, `True`, `False` (singletons). Use `==` for value comparisons.

---

## Type Hints

Python is dynamically typed, but **type hints** (PEP 484) add optional annotations for static analysis tools (`mypy`, `pyright`, IDE checkers). They have no runtime effect.

```python
def add(x: int, y: int) -> int:
    return x + y

name: str = "Alice"
values: list[int] = [1, 2, 3]

# Optional (can be None)
from typing import Optional
def greet(name: Optional[str] = None) -> str:
    return f"Hello {name or 'stranger'}"

# Union (Python 3.10+ shorthand)
def parse(value: int | str) -> str:
    return str(value)

# Common types from typing
from typing import Any, Callable, Dict, List, Tuple, Union
```

Type hints improve readability and enable tooling-based refactoring — use them on function signatures at minimum.

---

## The Python Data Model

Everything in Python is an **object**: integers, functions, classes, modules. Each object has:
- **Identity**: `id(obj)` — memory address, never changes
- **Type**: `type(obj)` — determines available operations
- **Value**: the data it holds

Operators call **dunder methods** (double underscore) on the objects:
- `a + b` → `a.__add__(b)`
- `len(x)` → `x.__len__()`
- `a == b` → `a.__eq__(b)`
- `str(x)` → `x.__str__()`

Understanding this model is the foundation for understanding operator overloading, iteration protocols, and context managers.
