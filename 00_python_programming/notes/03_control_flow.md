# Control Flow

## TL;DR

Python's control flow is structured around indentation, not braces, and around the **iterator protocol**, not C-style index counters. Conditionals are `if` / `elif` / `else`, with a one-line ternary (`a if cond else b`) for trivial cases and `match` / `case` (3.10+) for structural pattern matching that destructures sequences, mappings, and class instances. Every object can be evaluated in a boolean context: a fixed list of values is **falsy** (`None`, `0`, empty containers, `False`) and everything else is truthy, which enables `if lst:` instead of `if len(lst) > 0`. Loops iterate over **anything iterable**: lists, dicts, files, generators, ranges. `for` is the default; `while True` + `break` is the idiom for "loop at least once". `range`, `enumerate`, and `zip` cover most counter, index, and parallel-iteration needs without manual indexing. The lesser-known `else` clause on a loop runs only if the loop completed without `break`, which is the cleanest way to express "did I find anything?" without a flag variable.

## Cheatsheet

| Pattern | Syntax / Idiom | When |
|---|---|---|
| Conditional | `if a: ... elif b: ... else: ...` | Standard branching |
| Ternary | `a if cond else b` | Single-expression conditional |
| Pattern matching | `match x: case ...` | 3.10+, structural / sequence / mapping match |
| Falsy check | `if lst:` | Empty list / dict / set is falsy |
| Default via `or` | `name = input() or "default"` | Short-circuit on falsy |
| For loop | `for x in iterable:` | Default iteration |
| While true | `while True: ... if cond: break` | "Loop at least once" |
| Index + value | `for i, v in enumerate(seq):` | Counted iteration |
| Parallel | `for a, b in zip(A, B):` | Pair-wise iteration |
| Range | `range(start, stop, step)` | Lazy integer sequence |
| Loop else | `for ...: ... else: ...` | Runs if no `break` was hit |
| First match | `next((x for x in seq if cond(x)), None)` | Find or None |
| Flatten | `[v for sub in nested for v in sub]` | Flatten one level |
| Sliding window | `(seq[i:i+n] for i in range(len(seq)-n+1))` | n-grams |

---

## Conditionals

### `if` / `elif` / `else`

```python
x = 42

if x > 100:
    print("big")
elif x > 10:
    print("medium")
else:
    print("small")
```

No parentheses around the condition; indentation defines the block. Multiple `elif` branches are tried in order; the first match wins.

### Ternary expression

```python
label = "even" if x % 2 == 0 else "odd"
```

Readable for simple conditions. Avoid nesting more than one level deep — the result becomes hard to parse and obscures the logic.

### `match` / `case` (3.10+)

Structural pattern matching, more expressive than a chain of `elif`. It can destructure sequences, mappings, and class instances; it supports literals, names (which capture), wildcards (`_`), and guards (`if` clauses).

```python
match command:
    case "quit":
        quit()
    case "go" | "move":             # alternation
        move()
    case ("go", direction):         # sequence pattern, captures direction
        move(direction)
    case {"action": action}:        # mapping pattern, captures the value
        do(action)
    case Point(x=0, y=0):           # class pattern
        print("origin")
    case _:                         # wildcard / default
        print("unknown command")
```

Patterns can include `if` guards: `case Point(x, y) if x == y: ...`. Use `match` when you have many shape-based branches; for two or three simple value comparisons, plain `if` / `elif` is still cleaner.

---

## Truthiness in conditions

Python evaluates any object in a boolean context. The set of falsy values is fixed:

- `None`, `False`, `0`, `0.0`, `0j`
- `""`, `b""`, `()`
- `[]`, `{}`, `set()`
- Any object whose `__bool__()` returns `False`, or (failing that) whose `__len__()` returns `0`

Everything else is truthy. This enables idiomatic checks that read closer to natural English:

```python
if lst:                 # cleaner than: if len(lst) > 0
    ...

name = input() or "default"     # short-circuits: use "default" if input is empty
```

**Short-circuit evaluation**: `and` and `or` return one of their operands (not necessarily a bool) and stop evaluating as soon as the result is determined. This is both a performance feature and a defensive idiom for guarding against `None`:

```python
x = None
val = x or 42                   # 42 — x is falsy, returns the right operand
val = x and x.strip()           # None — short-circuits before calling .strip() on None
```

The `and x.strip()` pattern is a common safe-call idiom: if `x` is None or empty, evaluation stops at `x`; otherwise `.strip()` is called.

---

## `for` loop

Iterates over any **iterable**: lists, tuples, strings, dicts, files, generators, ranges. There is no C-style "loop with counter" in Python — use `range`, `enumerate`, or `zip` instead.

```python
for item in [1, 2, 3]:
    print(item)

for char in "hello":
    print(char)

for key in dictionary:                  # iterates over keys by default
    print(key, dictionary[key])

for key, value in dictionary.items():   # preferred when you need both
    print(key, value)
```

### `range`

Builds a lazy sequence of integers; does not allocate a list:

```python
range(5)            # 0, 1, 2, 3, 4
range(2, 8)         # 2, 3, 4, 5, 6, 7
range(0, 10, 2)     # 0, 2, 4, 6, 8
range(5, 0, -1)     # 5, 4, 3, 2, 1
```

### `enumerate`

Get index and value simultaneously, instead of `for i in range(len(seq))`:

```python
for i, val in enumerate(['a', 'b', 'c']):
    print(i, val)               # 0 a / 1 b / 2 c

for i, val in enumerate(['a', 'b'], start=1):
    print(i, val)               # 1 a / 2 b
```

### `zip`

Iterate over multiple iterables in parallel, pair-wise:

```python
names  = ['Alice', 'Bob', 'Carol']
scores = [95, 87, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

`zip` stops at the **shortest** iterable. Use `itertools.zip_longest(..., fillvalue=...)` if you want to pad. Calling `zip(*matrix)` transposes a list of equal-length rows.

---

## `while` loop

```python
n = 10
while n > 0:
    print(n)
    n -= 1
```

`while True` combined with `break` is the standard idiom for loops that must run at least once before the exit condition can be evaluated:

```python
while True:
    data = read_data()
    if not data:
        break
    process(data)
```

Reach for `while` when the number of iterations isn't known up front; reach for `for` when you're iterating over a known sequence.

---

## Loop control

| Statement | Effect |
|---|---|
| `break` | Exit the innermost loop immediately |
| `continue` | Skip the rest of the current iteration, go to the next |
| `pass` | No-op placeholder; required where Python expects a block but you have nothing to put there |

### `else` on loops

The `else` block of a `for` or `while` runs **only if the loop completed without hitting `break`**. The most useful application is "did I find anything?" without introducing a flag variable:

```python
for item in collection:
    if condition(item):
        result = item
        break
else:
    result = None       # runs only if no item matched

# Equivalent to "if not found" but no flag
```

Read the `else` as "no break". This is one of those Python features that confuses newcomers and clarifies code once internalised.

---

## Nested loops and `break`

`break` only exits the **innermost** loop. To break out of multiple levels cleanly, the most readable option is to refactor into a function and `return`:

```python
def find_pair(matrix, target):
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == target:
                return i, j
    return None, None
```

Other options exist — flag variables, `itertools.product` to flatten the nest, raising and catching a custom exception — but extracting a function is almost always the cleanest.

---

## Iteration protocol

Any object that implements `__iter__()` and `__next__()` is an **iterator**. Objects that implement only `__iter__()` (returning a fresh iterator each time) are **iterables**. The `for` loop is sugar over this protocol:

```python
it = iter([1, 2, 3])
next(it)            # 1
next(it)            # 2
next(it)            # 3
next(it)            # raises StopIteration
```

A `for` loop calls `iter(obj)` once to obtain an iterator, then calls `next()` on it until `StopIteration` is raised. This is why you can iterate over a list multiple times (each call to `iter` creates a fresh iterator) but a generator only once (the generator is its own iterator).

Understanding this protocol is the foundation for writing custom iterators and generators, covered in [05_functional_programming.md](05_functional_programming.md).

---

## Common patterns

```python
# Accumulate results
total = sum(x**2 for x in range(100))

# Find first matching item, with a sentinel default
result = next((x for x in lst if condition(x)), None)

# Flatten one level of nesting
flat = [item for sublist in nested for item in sublist]

# Group consecutive elements (the input must be sorted by the key first)
from itertools import groupby
for key, group in groupby(sorted_data, key=lambda x: x['category']):
    items = list(group)

# Sliding window
def windows(seq, n):
    for i in range(len(seq) - n + 1):
        yield seq[i:i+n]
```

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Mutating a list while iterating over it | Items skipped or processed twice | Iterate over `list(lst)` (a copy), or build a new list |
| Late binding in loop closures | All callables read the final loop value | Capture as default arg: `lambda i=i:` |
| `for / else` confusion | `else` block runs after `break` | Read `else` as "no break"; ensure the loop has a `break` to be meaningful |
| `range(len(lst))` plus index | Reinventing `enumerate` | Use `for i, v in enumerate(lst):` |
| `zip` silently truncates | Shorter input ends iteration prematurely | Use `zip_longest` if you need the full length |
| Empty collection treated as truthy | None of the falsy values applies | Check explicitly with `if x is not None and len(x) > 0` if needed |
| Nested `break` only exits one level | Outer loops keep going | Refactor into a function with `return`, or use a flag |
| Walrus operator (`:=`) misuse in `if` | Harder-to-read code | Use it sparingly, only where it eliminates a clear duplication |
| Generator exhausted by an earlier consumer | `for x in gen:` runs zero times the second time | Call `iter(...)` again, or convert to a list if you need re-iteration |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Branch on simple condition | `if` / `elif` / `else` | Standard, no surprises |
| One-line conditional value | Ternary `a if cond else b` | Concise for simple cases |
| Many shape-based branches | `match` / `case` | Destructures, more declarative |
| Loop over a known sequence | `for` | Default; works on any iterable |
| Loop with unknown number of iterations | `while` | Condition checked each pass |
| Need both index and value | `enumerate(seq)` | Cleaner than `range(len(seq))` |
| Iterate two sequences in parallel | `zip(a, b)` | Reads pair-wise |
| Find first matching element | `next(genexpr, default)` | Lazy, short-circuits |
| Default value on falsy input | `value or default` | Short-circuit `or` |
| Test "any" / "all" of a condition | `any(...)`, `all(...)` | Lazy, short-circuit |
| Build collection from iterable | Comprehension | More readable than loop + append |
| Iterate over a huge sequence once | Generator expression | O(1) memory |
| Group consecutive equal-key elements | `itertools.groupby` | Streaming, no full-pass needed |
| Exit nested loops cleanly | Function with `return` | Most readable |

---

## See also

- [01_types_and_variables.md](01_types_and_variables.md) — falsy values, truthiness in detail
- [02_collections.md](02_collections.md) — comprehensions, generator expressions, slicing
- [04_functions.md](04_functions.md) — `*args`, `**kwargs`, default arguments
- [05_functional_programming.md](05_functional_programming.md) — generators, `itertools`, `map`/`filter`
