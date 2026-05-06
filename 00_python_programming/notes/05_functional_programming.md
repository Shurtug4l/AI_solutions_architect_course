# Functional Programming

## Core Concepts in Python

Python is a multi-paradigm language. Its functional features center on:
- Functions as first-class objects
- Higher-order functions (accept/return functions)
- Immutability preference
- Lazy evaluation via generators

Python is not a pure functional language (it has no tail-call optimization, no enforced immutability), but functional style is idiomatic in many contexts.

---

## Higher-Order Functions

### map()

Apply a function to every element of an iterable. Returns a lazy iterator.

```python
squares = list(map(lambda x: x**2, [1, 2, 3, 4]))
# [1, 4, 9, 16]

# With multiple iterables
sums = list(map(lambda x, y: x + y, [1, 2, 3], [10, 20, 30]))
# [11, 22, 33]
```

In most cases, a list comprehension is more readable:

```python
squares = [x**2 for x in [1, 2, 3, 4]]
```

Use `map` when the function is already named (no need for a lambda):

```python
strs = list(map(str, [1, 2, 3]))
```

### filter()

Keep only elements where the predicate returns True. Returns a lazy iterator.

```python
evens = list(filter(lambda x: x % 2 == 0, range(10)))
# [0, 2, 4, 6, 8]

# Equivalent comprehension (preferred)
evens = [x for x in range(10) if x % 2 == 0]
```

### functools.reduce()

Cumulatively apply a binary function to reduce an iterable to a single value.

```python
from functools import reduce

product = reduce(lambda acc, x: acc * x, [1, 2, 3, 4, 5])
# 120 — (((1*2)*3)*4)*5

# With initial value
reduce(lambda acc, x: acc + x, [], 0)  # 0 — empty iterable safe with initializer
```

For common reductions, prefer built-ins: `sum()`, `max()`, `min()`, `any()`, `all()`.

---

## functools Module

### functools.partial

Create a new callable with some arguments pre-filled (partial application):

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)

square(5)   # 25
cube(3)     # 27
```

Useful when you need to adapt a function's signature to match an interface (e.g., callback that takes one argument).

### functools.lru_cache

Memoize a function: cache results for previously seen inputs. Avoids redundant computation.

```python
from functools import lru_cache

@lru_cache(maxsize=None)   # None = unbounded cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)      # instant; without cache: exponential time
fibonacci.cache_info()    # hits, misses, maxsize, currsize
fibonacci.cache_clear()   # invalidate cache
```

Only works with **hashable** arguments. Not suitable for functions with mutable arguments (lists, dicts).

### functools.wraps

Preserves function metadata in decorators (see [04_functions.md](04_functions.md)).

---

## Generators

A **generator** is a function that yields values lazily using `yield`. It returns a generator object — an iterator that produces values on demand.

```python
def count_up(limit):
    n = 0
    while n < limit:
        yield n
        n += 1

gen = count_up(5)
next(gen)    # 0
next(gen)    # 1
list(gen)    # [2, 3, 4] — consumes remainder
```

### Why generators

- Memory efficient: values computed one at a time, not all at once
- Can represent infinite sequences
- Composable: generators can be chained without materializing intermediate lists

```python
def infinite_counter(start=0):
    n = start
    while True:
        yield n
        n += 1

gen = infinite_counter()
[next(gen) for _ in range(5)]   # [0, 1, 2, 3, 4]
```

### yield from

Delegates to a sub-generator or any iterable:

```python
def chain(*iterables):
    for it in iterables:
        yield from it

list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]
```

### Generator as pipeline

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

# No intermediate lists; memory proportional to one line
pipeline = parse(strip_comments(read_lines('data.csv')))
for row in pipeline:
    process(row)
```

---

## itertools Module

Standard library tools for working with iterables. All return lazy iterators.

```python
import itertools as it

# Infinite iterators
it.count(start=0, step=1)          # 0, 1, 2, 3, ...
it.cycle([1, 2, 3])                # 1, 2, 3, 1, 2, 3, ...
it.repeat(value, n)                # value repeated n times (or infinitely)

# Terminating on shortest input
it.chain([1,2], [3,4], [5])        # 1, 2, 3, 4, 5
it.chain.from_iterable([[1,2],[3,4]])  # flattens one level
it.zip_longest([1,2,3], [a,b], fillvalue=0)  # zip with padding
it.compress([1,2,3,4], [1,0,1,0])  # [1, 3] — filter by mask
it.islice(gen, 5)                  # take first 5 from any iterable
it.islice(gen, 2, 10, 2)           # slice with step
it.takewhile(pred, it)             # take while predicate is True
it.dropwhile(pred, it)             # drop while predicate is True
it.filterfalse(pred, it)           # opposite of filter
it.starmap(func, [(a,b), (c,d)])   # map with tuple unpacking

# Combinatoric
it.product([1,2], [3,4])           # (1,3),(1,4),(2,3),(2,4)
it.permutations('ABC', 2)          # AB, AC, BA, BC, CA, CB
it.combinations('ABC', 2)          # AB, AC, BC
it.combinations_with_replacement('AB', 2)  # AA, AB, BB

# Grouping
it.groupby(sorted_data, key=lambda x: x['field'])  # must be sorted by key first!

# Accumulate
it.accumulate([1,2,3,4], func=operator.mul)  # [1, 2, 6, 24]
```

### Practical patterns

```python
# Flatten nested lists
flat = list(it.chain.from_iterable(nested))

# Take n items from a generator
first_10 = list(it.islice(infinite_gen, 10))

# Batch/chunk iterable into groups of n
def batched(iterable, n):
    it_ = iter(iterable)
    while batch := list(it.islice(it_, n)):
        yield batch
# Python 3.12+: itertools.batched(iterable, n)
```

---

## Functional Style: When and Why

Functional style in Python tends to produce:
- More composable code (small, pure functions that can be chained)
- Easier-to-test functions (no side effects, output determined entirely by input)
- More predictable data flow

Apply functional patterns when:
- Transforming or filtering collections
- Building pipelines on large/streaming data
- Writing reusable utility logic

Avoid forcing functional style when:
- Imperative loops are clearer
- State is genuinely needed (stateful algorithms, simulations)
- Performance requires in-place mutation
