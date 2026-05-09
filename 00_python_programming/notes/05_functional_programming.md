# Functional Programming

## TL;DR

Python is multi-paradigm: it gives you the functional toolkit (higher-order functions, closures, immutability, lazy evaluation) without enforcing it. The four cornerstones are **higher-order functions** (`map`, `filter`, `reduce`), **functools utilities** (`partial` for partial application, `lru_cache` for memoisation, `wraps` for decorator hygiene), **generators** (functions that `yield` lazily and produce values one at a time), and **itertools** (a deep standard-library set of lazy iterator combinators). For most everyday transformations a list/generator comprehension is more readable than `map`/`filter`; reach for the functional names when the function is already named, or when you need a lazy stream. Generators are the right tool for streaming pipelines on large data — chain them together and memory stays proportional to a single element. Don't force functional style: imperative loops are clearer when state is genuinely needed, and mutation in place beats functional purity for performance-sensitive code.

## Cheatsheet

| Tool | Use | Lazy? |
|---|---|---|
| `map(f, iter)` | Apply `f` to each element | Yes |
| `filter(pred, iter)` | Keep elements where `pred` is true | Yes |
| `functools.reduce(f, iter, init)` | Cumulative binary operation | Eager |
| List comp `[f(x) for x in iter]` | Build a list eagerly | No |
| Gen expr `(f(x) for x in iter)` | Build a generator lazily | Yes |
| `functools.partial(f, *args, **kw)` | Pre-bind arguments | — |
| `@functools.lru_cache(maxsize=N)` | Memoise pure function with hashable args | — |
| `@functools.wraps(func)` | Preserve metadata in decorators | — |
| `def f(): yield ...` | Generator function | Yes |
| `yield from iterable` | Delegate to a sub-iterable | Yes |
| `itertools.chain` | Concatenate iterables | Yes |
| `itertools.islice(iter, n)` | First n items | Yes |
| `itertools.groupby(iter, key)` | Group consecutive equal-key items | Yes |
| `itertools.product(a, b)` | Cartesian product | Yes |
| `itertools.combinations(seq, r)` | All r-element combinations | Yes |
| `itertools.accumulate(iter, op)` | Running totals / scan | Yes |

---

## Higher-order functions

### `map`

Applies a function to every element of an iterable. Returns a lazy iterator (no list is materialised until you ask for one).

```python
squares = list(map(lambda x: x**2, [1, 2, 3, 4]))
# [1, 4, 9, 16]

# Multiple iterables — function takes that many positional args
sums = list(map(lambda x, y: x + y, [1, 2, 3], [10, 20, 30]))
# [11, 22, 33]
```

In most everyday cases a list comprehension is more readable, because it reads top-to-bottom and doesn't need a lambda:

```python
squares = [x**2 for x in [1, 2, 3, 4]]
```

`map` shines when the function is already named — there's no lambda noise:

```python
strs = list(map(str, [1, 2, 3]))
```

### `filter`

Keeps only elements for which the predicate returns truthy. Lazy.

```python
evens = list(filter(lambda x: x % 2 == 0, range(10)))
# [0, 2, 4, 6, 8]

# Equivalent comprehension (usually preferred)
evens = [x for x in range(10) if x % 2 == 0]
```

### `functools.reduce`

Applies a binary function cumulatively, reducing an iterable to a single value. Less idiomatic in Python than in classical functional languages — Python prefers explicit loops or built-ins like `sum`, `max`, `min`, `any`, `all` for common reductions.

```python
from functools import reduce

product = reduce(lambda acc, x: acc * x, [1, 2, 3, 4, 5])
# 120 — equivalent to (((1*2)*3)*4)*5

# With initial value, the empty case is well-defined
reduce(lambda acc, x: acc + x, [], 0)   # 0
```

Use `reduce` only when the operation isn't covered by a built-in (`sum`, `max`, `min`, `any`, `all`, `math.prod`). For most "fold" patterns a `for` loop with an accumulator is just as concise and easier to debug.

---

## `functools` module

### `functools.partial`

Creates a new callable with some arguments pre-filled. Useful when adapting a function's signature to match a callback interface that expects fewer arguments.

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)

square(5)       # 25
cube(3)         # 27
```

Common use case: passing a configurable callable into something that expects a one-argument function (`map`, `filter`, sort `key=`, GUI event handlers).

### `functools.lru_cache`

Memoises a function: caches results so that repeated calls with the same arguments return immediately. The cache is bounded by `maxsize` (LRU eviction) or unbounded with `maxsize=None`.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)              # instant; without cache, exponential time
fibonacci.cache_info()      # CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
fibonacci.cache_clear()     # invalidate cache
```

Two requirements: arguments must be **hashable**, and the function must be **pure** (no side effects, deterministic given inputs). Mutable arguments (lists, dicts) cannot be cached. For methods, prefer `functools.cached_property` when caching per instance.

### `functools.wraps`

Preserves function metadata (`__name__`, `__doc__`, signature) when writing decorators. Always pair every wrapper with `@functools.wraps(func)` — see [04_functions.md](04_functions.md) for the full discussion.

---

## Generators

A generator is a function that uses `yield` instead of `return`. Calling it does not run the body; it returns a **generator object** — an iterator that produces values on demand by executing the function up to the next `yield`.

```python
def count_up(limit):
    n = 0
    while n < limit:
        yield n
        n += 1

gen = count_up(5)
next(gen)       # 0
next(gen)       # 1
list(gen)       # [2, 3, 4] — consumes whatever is left
```

### Why generators

- **Memory efficient**: values are produced one at a time, so the iterator's memory footprint is constant regardless of how many values it will ultimately produce.
- **Can represent infinite sequences**: there's no requirement that the generator ever terminates.
- **Composable**: chain generators into pipelines without materialising any intermediate list.

```python
def infinite_counter(start=0):
    n = start
    while True:
        yield n
        n += 1

gen = infinite_counter()
[next(gen) for _ in range(5)]   # [0, 1, 2, 3, 4]
```

### `yield from`

Delegates to a sub-generator or any iterable, forwarding values without an explicit re-`yield` loop:

```python
def chain(*iterables):
    for it in iterables:
        yield from it

list(chain([1, 2], [3, 4], [5]))    # [1, 2, 3, 4, 5]
```

`yield from` also forwards `send()`, `throw()`, and the return value of the sub-generator, which matters in advanced patterns (coroutines, generator-based async).

### Generator pipelines

Chaining generators lets you process huge or streaming data with memory proportional to a single element:

```python
def read_lines(path):
    with open(path) as f:
        yield from f

def strip_comments(lines):
    for line in lines:
        if not line.startswith('#'):
            yield line

def parse(lines):
    for line in lines:
        yield line.split(',')

# Three lazy generators stacked into a pipeline; one row in memory at a time
pipeline = parse(strip_comments(read_lines('data.csv')))
for row in pipeline:
    process(row)
```

This is the same conceptual pattern as Unix pipes — each stage transforms a stream produced by the previous one.

---

## `itertools` module

A standard-library set of iterator combinators, all lazy. Treat it as your reference for "I need to do X with an iterator without writing the loop myself".

```python
import itertools as it

# Infinite iterators (always combine with islice or a stop condition!)
it.count(start=0, step=1)               # 0, 1, 2, 3, ...
it.cycle([1, 2, 3])                     # 1, 2, 3, 1, 2, 3, ...
it.repeat(value, n)                     # value n times (or infinitely if n omitted)

# Stop on shortest input or specific condition
it.chain([1, 2], [3, 4], [5])           # 1, 2, 3, 4, 5
it.chain.from_iterable([[1, 2], [3, 4]]) # flatten one level
it.zip_longest([1, 2, 3], ['a', 'b'], fillvalue=0)  # zip with padding
it.compress([1, 2, 3, 4], [1, 0, 1, 0]) # [1, 3] — filter by mask
it.islice(gen, 5)                       # take first 5 from any iterable
it.islice(gen, 2, 10, 2)                # slice with step
it.takewhile(pred, iter)                # take while predicate is True
it.dropwhile(pred, iter)                # drop while predicate is True, then take rest
it.filterfalse(pred, iter)              # opposite of filter
it.starmap(func, [(a, b), (c, d)])      # like map but unpacks tuples

# Combinatorics
it.product([1, 2], [3, 4])              # (1,3),(1,4),(2,3),(2,4)
it.permutations('ABC', 2)               # AB, AC, BA, BC, CA, CB
it.combinations('ABC', 2)               # AB, AC, BC
it.combinations_with_replacement('AB', 2)   # AA, AB, BB

# Grouping (input must be sorted by the key first!)
it.groupby(sorted_data, key=lambda x: x['field'])

# Running totals / scan
it.accumulate([1, 2, 3, 4], func=operator.mul)  # 1, 2, 6, 24
```

### Practical patterns

```python
# Flatten one level of nesting
flat = list(it.chain.from_iterable(nested))

# Take n items from a generator (works on any iterable, not just lists)
first_10 = list(it.islice(infinite_gen, 10))

# Batch / chunk an iterable into groups of n (Python 3.12+ has it.batched)
def batched(iterable, n):
    it_ = iter(iterable)
    while batch := list(it.islice(it_, n)):
        yield batch
```

The walrus operator `:=` in the loop above lets the assignment and the truthiness check share one expression — a rare case where the syntax really earns its keep.

---

## Functional style: when and why

Functional patterns produce code that is more **composable** (small, pure functions chain into pipelines), **easier to test** (no side effects, output determined entirely by inputs), and easier to reason about as a sequence of transformations.

Reach for functional style when:

- Transforming or filtering collections (a comprehension or a generator chain reads better than a manual loop with state).
- Building pipelines on large or streaming data (generators keep memory bounded).
- Writing reusable utility logic (small pure functions are easy to combine and test).

Avoid forcing functional style when:

- Imperative loops are clearer (most stateful algorithms).
- State is genuinely needed (simulations, accumulators with non-trivial structure).
- Performance requires in-place mutation (NumPy operations, memory-bound code).

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Iterating over a generator twice | Second loop runs zero times | Convert to a list once, or call the generator factory again |
| `map`/`filter` returns "nothing" | Forgot they return iterators, not lists | Wrap in `list(...)` or use a comprehension |
| `lru_cache` on a method | Cache attached to the function, not per instance; arguments include `self` | Use `functools.cached_property` for per-instance caching |
| `lru_cache` with mutable arguments | `TypeError: unhashable type` | Convert to tuple/frozenset, or refactor to take hashable inputs |
| `groupby` without sorting | Only consecutive equal keys are grouped | Sort by the key first |
| Infinite iterator without `islice` | Hangs or runs out of memory | Always combine with `islice`, `takewhile`, or a `break` |
| Closure capturing loop variable | All callables read the final value | Capture via default arg: `lambda x=x: ...` (see 04_functions.md) |
| `reduce` with no initial on empty | `TypeError: reduce() of empty sequence` | Provide an initial value |
| Side effects inside `map` | Hard to debug, lazy execution surprises | Use a `for` loop with explicit state |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Build a list from a transformation | List comprehension | Eager, readable, no lambda |
| Build a lazy stream from a transformation | Generator expression | O(1) memory, composable |
| Reuse a transformation function with one arg pre-filled | `functools.partial` | Cleaner than a one-line lambda |
| Cache results of an expensive pure function | `@lru_cache` | Hashable args, deterministic |
| Cache an expensive per-instance attribute | `@functools.cached_property` | Per-instance, lazy |
| Process huge / streaming data | Generator pipeline | Bounded memory, composable |
| Combine multiple iterables | `itertools.chain` | Lazy concatenation |
| Cross-product of iterables | `itertools.product` | Avoids nested loops |
| Group records by a key | `sorted` + `itertools.groupby` | Standard streaming pattern |
| Window over a sequence | Generator + slicing, or `itertools` recipe | Reusable across data types |
| Fold a binary op over a sequence | `functools.reduce` (rare) | Use only when no built-in fits |

---

## See also

- [02_collections.md](02_collections.md) — comprehensions, generator expressions, `collections` module
- [03_control_flow.md](03_control_flow.md) — iteration protocol, common patterns
- [04_functions.md](04_functions.md) — closures, decorators, `functools.wraps` in depth
- [11_standard_library.md](11_standard_library.md) — wider tour of standard-library modules
