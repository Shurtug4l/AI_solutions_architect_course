# Types and Variables

## TL;DR

Python variables are not memory containers; they are **names that reference objects**. Assignment binds a name to an object, never copies it, so `y = x` makes both names point to the same thing. Every value is an object with three immutable properties: identity (`id`), type (`type`), and a value. Numeric types include arbitrary-precision `int`, 64-bit `float`, and `complex`. Strings are immutable Unicode sequences. The single most important distinction is between **mutable** types (`list`, `dict`, `set`) and **immutable** ones (`int`, `str`, `tuple`): mutability determines whether a function can change an object passed to it, and only immutable types can be used as dict keys or set elements. Use `is` only for `None`, `True`, `False` (singletons); use `==` for value comparisons. Type hints (PEP 484) describe expected types but are erased at runtime — they exist for static analysers and IDEs.

## Cheatsheet

| Concept | Syntax / Example | Note |
|---|---|---|
| Multiple assignment | `a, b = 1, 2` | Tuple unpacking on the right |
| Star unpacking | `a, *rest = [1,2,3,4]` | `rest` is a list |
| Swap | `a, b = b, a` | No temp variable needed |
| `int` arithmetic | `10 // 3` (floor), `10 % 3` (mod), `2 ** 10` | `int` has no overflow |
| Float gotcha | `0.1 + 0.2 == 0.3` → `False` | IEEE 754; use `decimal.Decimal` for exact |
| Falsy values | `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False` | Everything else is truthy |
| None test | `if x is None` | Never `== None` |
| f-string | `f"{x:.2f}"`, `f"{x = }"` | Last form prints `"x = value"` (3.8+) |
| Type test | `isinstance(x, int)` | Preferred over `type(x) ==` |
| Mutable container | `list`, `dict`, `set`, `bytearray` | Cannot be dict keys |
| Immutable container | `tuple`, `frozenset`, `bytes` | Hashable, dict-key-friendly |
| Identity vs equality | `is` vs `==` | `is` checks address, `==` calls `__eq__` |
| Type hints | `def f(x: int) -> str` | No runtime effect |

---

## Variables and assignment

A Python variable is a **reference to an object**, not a slot that holds a value. Assignment binds a name to whatever object is on the right; it never copies the object. The same object can have multiple names pointing to it, and reassigning one name does not affect the others.

```python
x = 42          # x references an int object whose value is 42
y = x           # y references the same object as x
x = 100         # x is rebound to a new int 100; y still references 42
```

Multiple assignment and iterable unpacking work because the right-hand side is evaluated first as a tuple:

```python
a, b, c = 1, 2, 3
a, *rest = [1, 2, 3, 4]    # a = 1, rest = [2, 3, 4]
a, b = b, a                 # swap, no temporary variable needed
```

Variable names are case-sensitive. The community convention is `snake_case` for variables and functions, `UPPER_CASE` for module-level constants, and `PascalCase` for classes.

---

## Built-in types

### Numeric types

```python
x = 42          # int — arbitrary precision, no overflow
y = 3.14        # float — 64-bit IEEE 754 double
z = 2 + 3j      # complex

10 // 3         # 3   (floor division)
10 % 3          # 1   (modulo)
2 ** 10         # 1024 (exponentiation)
abs(-7)         # 7

0.1 + 0.2       # 0.30000000000000004 — IEEE 754 representation artifact
round(2.675, 2) # 2.67 — same artifact
```

`int` has unlimited precision in Python 3, so integer overflow does not exist. `float` is always a 64-bit double; there is no separate `double` type. For exact decimal arithmetic (money, scientific tolerances) use `decimal.Decimal`. For rationals use `fractions.Fraction`.

### Booleans

`bool` is a subclass of `int`, so `True == 1` and `False == 0`. Anything passed to `bool()` is reduced to true/false using a fixed set of falsy values:

```python
True + True     # 2 — bool inherits from int
bool(0)         # False
bool("")        # False
bool([])        # False
bool(None)      # False
bool(1)         # True (any non-zero, non-empty value)
```

Falsy values: `0`, `0.0`, `0j`, `""`, `[]`, `{}`, `set()`, `None`, `False`. Everything else is truthy. This enables idiomatic checks like `if lst:` instead of `if len(lst) > 0`.

### None

`None` is the singleton object representing the absence of a value. Always test with identity (`is None`), not equality, because `None.__eq__` could in theory be overridden and `is` is faster and more explicit.

```python
result = None
if result is None:
    ...
```

### Strings

Strings are **immutable** sequences of Unicode characters. You cannot modify them in place; every "modifying" method returns a new string.

```python
s = "hello"
s = 'hello'
s = """multi
line"""

len(s)              # 5
s.upper()           # 'HELLO'
s.strip()           # remove leading/trailing whitespace
s.split(',')        # list of parts split on the separator
','.join(['a','b']) # 'a,b'
s.replace('l','r')  # 'herro'
s.startswith('he')  # True
s.find('ll')        # 2 — index, or -1 if not found
'll' in s           # True

s[0]        # 'h'
s[-1]       # 'o'
s[1:4]      # 'ell'
s[::-1]     # 'olleh' — reversed copy
```

f-strings are the preferred way to interpolate values into strings. They support format specifiers and a debug form that prints the expression along with its value:

```python
name, age = "Alice", 30
f"{name} is {age} years old"
f"{3.14159:.2f}"        # '3.14' — format spec after the colon
f"{2**10 = }"           # '2**10 = 1024' — debug form (3.8+)
```

---

## Type conversion

```python
int("42")               # 42
int(3.9)                # 3 — truncates toward zero, does not round
float("3.14")           # 3.14
str(42)                 # '42'
bool(0)                 # False
list("abc")             # ['a', 'b', 'c']

type(x)                 # <class 'int'>
isinstance(x, int)      # True — preferred over `type(x) == int`, handles inheritance
isinstance(x, (int, float))  # True if x is either
```

`isinstance` is preferred over `type(x) == ...` because it correctly handles subclasses. For example, `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`, while `type(True) == int` is `False`.

---

## Mutability

Mutability is the single most important property to track when reading Python code. Mutable objects can change in place; immutable ones cannot. The distinction matters when passing objects to functions (a mutating function call alters the caller's state) and when using objects as dict keys or set elements (only hashable — practically, immutable — objects qualify).

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool`, `complex` | `list` |
| `str` | `dict` |
| `tuple` | `set` |
| `frozenset` | most user-defined classes |
| `bytes` | `bytearray` |
| `None` | |

The mutable-default-argument trap is a direct consequence:

```python
# Bug: lst is created once at definition time and shared across calls
def append(x, lst=[]):
    lst.append(x)
    return lst

append(1)       # [1]
append(2)       # [1, 2]    — not the fresh list you expected!

# Correct: use a None sentinel and create the container inside the body
def append(x, lst=None):
    if lst is None:
        lst = []
    lst.append(x)
    return lst
```

---

## Identity vs equality

Two distinct concepts that look superficially similar:

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b      # True  — same value
a is b      # False — different objects in memory
a is c      # True  — same object

id(a)       # memory address (CPython implementation detail)
```

`is` tests **object identity**: do both names point to the same object in memory? `==` tests **value equality**: it calls `__eq__`. Use `is` only for the singletons `None`, `True`, `False`. Use `==` everywhere else.

A subtle case: small integers and short strings are sometimes interned by CPython, so `a is b` may unexpectedly return `True` when both are equal. Never rely on this behavior — it is an implementation detail.

---

## Type hints

Python is dynamically typed, but **type hints** (PEP 484) add optional annotations consumed by static analysers (`mypy`, `pyright`) and IDEs. They have **no runtime effect**: a function annotated `x: int` will happily accept anything you pass.

```python
def add(x: int, y: int) -> int:
    return x + y

name: str = "Alice"
values: list[int] = [1, 2, 3]
```

Modern Python (3.10+) lets you write union types with `|` and skip the `typing` imports for collection types:

```python
def parse(value: int | str) -> str:               # was Union[int, str]
    return str(value)

def greet(name: str | None = None) -> str:        # was Optional[str]
    return f"Hello {name or 'stranger'}"

values: list[int] = [1, 2, 3]                     # was List[int]
```

Annotate function signatures at minimum: they document intent, enable refactoring tools, and give IDEs the information they need for accurate autocomplete.

---

## The Python data model

Everything in Python is an **object**: integers, functions, classes, modules, even types themselves. Each object has three properties:

- **Identity** — `id(obj)`, the memory address (in CPython); never changes during the object's lifetime.
- **Type** — `type(obj)`, determines which operations are valid.
- **Value** — the data the object holds.

Operators are sugar for **dunder methods** (double-underscore methods) on the underlying objects:

- `a + b` → `a.__add__(b)`
- `len(x)` → `x.__len__()`
- `a == b` → `a.__eq__(b)`
- `str(x)` → `x.__str__()`

Understanding this model is the entry point to operator overloading, the iteration protocol, and context managers — all covered in later notes.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| `0.1 + 0.2 != 0.3` | Float comparison fails unexpectedly | Use `math.isclose(a, b)` or `decimal.Decimal` for exact arithmetic |
| `is` instead of `==` | Equality checks fail for non-singletons | Use `is` only for `None`, `True`, `False` |
| Mutable default argument | List/dict accumulates state across calls | None sentinel, build the container inside the body |
| Shallow copy with nested mutables | Inner objects still shared | `copy.deepcopy()` for nested structures |
| `bool(x)` on a NumPy array | `ValueError: ambiguous truth value` | Use `x.any()` or `x.all()`, or check `len(x)` |
| `==` on objects without `__eq__` | Falls back to identity (`is`) | Define `__eq__` (or use `@dataclass`) |
| Integer division of negatives | `-7 // 2 == -4`, not `-3` | Floor division rounds toward minus infinity |
| `int("3.0")` raises | `ValueError` because `int()` only parses integer strings | Convert via `int(float("3.0"))` |
| `isinstance(True, int) == True` | Booleans count as integers in checks | Use `type(x) is bool` if you really need to distinguish |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Whole numbers, including very large ones | `int` | Arbitrary precision |
| Real numbers, fast | `float` | 64-bit hardware double |
| Exact decimal (money, accounting) | `decimal.Decimal` | No binary representation artifacts |
| Exact rationals | `fractions.Fraction` | Symbolic ratios |
| Text | `str` | Immutable Unicode |
| Raw bytes | `bytes` (immutable) or `bytearray` (mutable) | Binary protocols, file I/O |
| Ordered, mutable sequence | `list` | Default for "a bunch of things" |
| Ordered, immutable sequence with fixed shape | `tuple` | Records, function returns, dict keys |
| Key-value mapping | `dict` | O(1) average lookup |
| Membership checks at scale | `set` / `frozenset` | O(1) average lookup |
| Singleton sentinel | `None` | Universal convention for "no value" |
| Document types in a function signature | Type hints | IDE autocomplete + static checking |

---

## See also

- [02_collections.md](02_collections.md) — list, tuple, dict, set, comprehensions, slicing
- [03_control_flow.md](03_control_flow.md) — truthiness in conditions, falsy values
- [04_functions.md](04_functions.md) — function signatures, type hints in depth
- [06_oop.md](06_oop.md) — `__eq__`, `__hash__`, the data model in user classes
