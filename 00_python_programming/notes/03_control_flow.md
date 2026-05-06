# Control Flow

## Conditionals

### if / elif / else

```python
x = 42

if x > 100:
    print("big")
elif x > 10:
    print("medium")
else:
    print("small")
```

No parentheses needed around the condition. Indentation defines blocks.

### Ternary Expression

```python
label = "even" if x % 2 == 0 else "odd"
```

Readable for simple conditions. Avoid nesting ternaries.

### match / case (Python 3.10+)

Structural pattern matching — more expressive than a chain of `elif`:

```python
match command:
    case "quit":
        quit()
    case "go" | "move":
        move()
    case ("go", direction):       # sequence pattern
        move(direction)
    case {"action": action}:      # mapping pattern
        do(action)
    case _:                       # wildcard / default
        print("unknown command")
```

Pattern matching can destructure sequences, mappings, class instances, and apply guards (`if` clauses).

---

## Truthiness in Conditions

Python evaluates any object in a boolean context. The following are **falsy**:

- `None`, `False`, `0`, `0.0`, `0j`
- `""`, `b""`, `()`
- `[]`, `{}`, `set()`
- Any object where `__bool__()` returns `False` or `__len__()` returns `0`

Everything else is truthy. This enables idiomatic checks:

```python
if lst:           # instead of: if len(lst) > 0
    ...

name = input() or "default"    # short-circuit: use "default" if input is empty
```

**Short-circuit evaluation**: `and` and `or` return one of their operands (not always a bool) and stop as soon as the result is determined:

```python
x = None
val = x or 42          # 42 — because x is falsy
val = x and x.strip()  # None — short-circuits before calling .strip()
```

---

## for Loop

Iterates over any **iterable**: lists, tuples, strings, dicts, files, generators, etc.

```python
for item in [1, 2, 3]:
    print(item)

for char in "hello":
    print(char)

for key in dictionary:          # iterates over keys
    print(key, dictionary[key])

for key, value in dictionary.items():  # preferred
    print(key, value)
```

### range()

```python
range(5)          # 0, 1, 2, 3, 4
range(2, 8)       # 2, 3, 4, 5, 6, 7
range(0, 10, 2)   # 0, 2, 4, 6, 8
range(5, 0, -1)   # 5, 4, 3, 2, 1
```

`range` is lazy — it does not build a list in memory.

### enumerate()

Get index and value simultaneously:

```python
for i, val in enumerate(['a', 'b', 'c']):
    print(i, val)   # 0 a / 1 b / 2 c

for i, val in enumerate(['a', 'b'], start=1):
    print(i, val)   # 1 a / 2 b
```

### zip()

Iterate over multiple iterables in parallel:

```python
names  = ['Alice', 'Bob', 'Carol']
scores = [95, 87, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# zip stops at the shortest iterable
# use itertools.zip_longest to fill missing values
```

---

## while Loop

```python
n = 10
while n > 0:
    print(n)
    n -= 1
```

`while True` + `break` is idiomatic for loops that must execute once before the exit condition can be checked:

```python
while True:
    data = read_data()
    if not data:
        break
    process(data)
```

---

## Loop Control

| Statement | Effect |
|-----------|--------|
| `break` | Exit the innermost loop immediately |
| `continue` | Skip the rest of the current iteration, go to next |
| `pass` | No-op placeholder (syntactically required empty block) |

### else Clause on Loops

The `else` block of a `for` or `while` runs **only if the loop completed without hitting `break`**. Useful for search patterns:

```python
for item in collection:
    if condition(item):
        result = item
        break
else:
    result = None    # runs only if no item matched

# Equivalent to "if not found" but without a flag variable
```

---

## Nested Loops and break

`break` only exits the **innermost** loop. To exit multiple levels, use a flag, a function return, or `itertools.product`:

```python
# Using a function to exit nested loops cleanly
def find_pair(matrix, target):
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == target:
                return i, j
    return None, None
```

---

## Iteration Protocol

Any object that implements `__iter__()` and `__next__()` is an **iterator**. Objects that implement only `__iter__()` (returning an iterator) are **iterables**.

A `for` loop calls `iter(obj)` to get an iterator, then repeatedly calls `next()` until `StopIteration` is raised.

```python
it = iter([1, 2, 3])
next(it)   # 1
next(it)   # 2
next(it)   # 3
next(it)   # raises StopIteration
```

Understanding this protocol is the foundation for writing custom iterators and generators (covered in [05_functional_programming.md](05_functional_programming.md)).

---

## Common Patterns

```python
# Accumulate results
total = sum(x**2 for x in range(100))

# Find first matching item
result = next((x for x in lst if condition(x)), None)

# Flatten nested structure
flat = [item for sublist in nested for item in sublist]

# Group consecutive elements
from itertools import groupby
for key, group in groupby(sorted_data, key=lambda x: x['category']):
    items = list(group)

# Sliding window
def windows(seq, n):
    for i in range(len(seq) - n + 1):
        yield seq[i:i+n]
```
