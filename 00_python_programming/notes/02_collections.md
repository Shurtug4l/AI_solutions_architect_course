# Collections

## TL;DR

Python ships four core container types that cover almost every data-structure need. **List** is the ordered, mutable workhorse — append at end is amortised O(1), insert/remove in the middle is O(n). **Tuple** is its immutable, hashable cousin: use it for fixed-shape records and as dict keys. **Dict** is the ordered (insertion-order since 3.7) key-value mapping with O(1) average lookup; keys must be hashable. **Set** is an unordered collection of unique, hashable elements with O(1) average membership tests — use it the moment you find yourself doing many `x in lst` checks. **Comprehensions** build any of these from an iterable in one expression; their lazy cousin, the **generator expression**, produces values on demand and uses O(1) memory. The `collections` module adds drop-in upgrades — `defaultdict` for missing-key handling, `Counter` for frequency tables, `deque` for fast operations on both ends.

## Cheatsheet

| Container | When to reach for it | Mutable | Hashable |
|---|---|---|---|
| `list` | Ordered, mutable sequence; default choice | Yes | No |
| `tuple` | Fixed-shape record, dict key, function return | No | Yes (if elements are) |
| `dict` | Key → value lookup, O(1) average | Yes | No |
| `set` | Unique elements, fast membership | Yes | No |
| `frozenset` | Set as dict key or set element | No | Yes |
| `defaultdict` | Group / accumulate without `if key in d` boilerplate | Yes | No |
| `Counter` | Frequency tables, top-k | Yes | No |
| `deque` | Stack / queue with O(1) on both ends | Yes | No |

| Operation | List | Dict / Set |
|---|---|---|
| Membership `x in c` | O(n) | O(1) average |
| Append / insert end | O(1) amortised | — |
| Insert / remove middle | O(n) | — |
| Lookup / insert by key | — | O(1) average |
| Slice | O(k) | — |

---

## List

Ordered, mutable sequence. The general-purpose workhorse — when in doubt, use a list.

```python
lst = [1, 2, 3, "four", True]   # heterogeneous works, but homogeneous is better practice

# Access
lst[0]          # 1
lst[-1]         # True
lst[1:3]        # [2, 3]      — slicing returns a new list
lst[::2]        # [1, 3, True] — every other element
lst[::-1]       # reversed copy

# Mutation
lst.append(5)               # add to end — O(1) amortised
lst.extend([6, 7])          # concatenate another iterable — O(k)
lst.insert(0, 0)            # insert at index — O(n)
lst.pop()                   # remove and return last — O(1)
lst.pop(0)                  # remove and return at index — O(n)
lst.remove(3)               # remove first occurrence of value — O(n)
lst.index(2)                # find index of first occurrence
lst.count(1)                # count occurrences of a value
lst.reverse()               # in-place reverse
lst.sort()                  # in-place sort
lst.sort(key=lambda x: x[1], reverse=True)  # custom sort key
sorted(lst)                 # new sorted list, leaves original untouched

# Copy
copy_lst = lst.copy()       # shallow — equivalent to lst[:]
import copy
deep_copy = copy.deepcopy(lst)   # deep — for nested mutable objects
```

Shallow copy duplicates the list container but not the inner objects: nested mutables are still shared. Use `copy.deepcopy` when nested mutables exist and you need full independence.

---

## Tuple

Ordered, immutable sequence. Use it for heterogeneous data with a fixed shape — coordinates, database records, function return values — where mutation would be a bug, not a feature.

```python
t = (1, 2, 3)
t = 1, 2, 3             # parentheses optional; the comma makes the tuple
single = (42,)          # trailing comma mandatory for a single-element tuple
empty  = ()

t[0]            # 1
t[-1]           # 3
len(t)          # 3

# Unpacking
x, y, z = t
x, *rest = t            # x = 1, rest = [2, 3]

# Named tuple — tuple with field access
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
p.x             # 1
p[0]            # 1 — still indexable

# Tuples are hashable if all elements are, so they can be dict keys
d = {(0, 0): 'origin', (1, 1): 'diagonal'}
```

Prefer tuples over lists when the structure is fixed. It signals intent ("this won't change"), gains hashability (so the tuple can be a dict key or set member), and avoids accidental mutation. For tuples you intend to type-annotate, consider `typing.NamedTuple` or `dataclass(frozen=True)` for richer self-documentation.

---

## Dictionary

Ordered (insertion order preserved since Python 3.7), mutable mapping of **key → value**. Keys must be hashable.

```python
d = {'a': 1, 'b': 2}
d = dict(a=1, b=2)              # keyword syntax
d = dict([('a', 1)])            # from iterable of pairs

# Access
d['a']                          # 1; raises KeyError if missing
d.get('a')                      # 1; returns None if missing (safe)
d.get('z', 0)                   # 0; default value if missing

# Mutation
d['c'] = 3                      # add or update
d.update({'d': 4, 'e': 5})      # merge another dict (or iterable of pairs)
del d['a']                      # delete a key, raises KeyError if absent
d.pop('b')                      # remove and return the value
d.setdefault('f', 0)            # if 'f' absent, insert with default; return value at 'f'

# Iteration
d.keys()                        # dict_keys view
d.values()                      # dict_values view
d.items()                       # dict_items view — pairs (key, value)

for key, value in d.items():
    print(key, value)

# Merge (Python 3.9+)
merged = d1 | d2                # new dict, d2 wins on conflicts
d1 |= d2                        # in-place

# Dict comprehension
squares = {x: x**2 for x in range(10)}
```

Dict views (`keys`, `values`, `items`) are **live**: they reflect changes to the underlying dict. Avoid mutating the dict while iterating over a view (typical fix: iterate over `list(d.items())`).

---

## Set

Unordered collection of **unique, hashable** elements. No indexing or slicing.

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])           # {1, 2, 3} — duplicates removed
empty = set()                    # not {}, which is an empty dict

s.add(4)
s.remove(2)                     # raises KeyError if absent
s.discard(99)                   # safe removal; no error if absent
s.pop()                         # remove and return an arbitrary element

# Set algebra
a = {1, 2, 3}
b = {2, 3, 4}

a | b           # {1, 2, 3, 4}  — union
a & b           # {2, 3}        — intersection
a - b           # {1}           — difference
a ^ b           # {1, 4}        — symmetric difference

a.issubset(b)   # a <= b
a.issuperset(b) # a >= b
a.isdisjoint(b) # no common elements

# Fast membership test — O(1) average vs O(n) for list
42 in s
```

`frozenset` is the immutable, hashable variant. Use it as a dict key or set element when you need a set of sets.

---

## Comprehensions

Concise syntax for building collections from an iterable in a single expression. Comprehensions are preferred over manual loops when the logic is simple — they read top-to-bottom and avoid the boilerplate of pre-allocating, looping, and appending.

### List comprehension

```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]

# Nested
matrix = [[1, 2, 3], [4, 5, 6]]
flat   = [val for row in matrix for val in row]   # [1, 2, 3, 4, 5, 6]
```

### Dict comprehension

```python
{k: v for k, v in zip(keys, values)}
{k: v for k, v in d.items() if v > 0}    # filter while building
```

### Set comprehension

```python
{x**2 for x in range(10)}
```

### Generator expression

Looks like a list comprehension but with parentheses; produces values **lazily**, one at a time, using O(1) memory. Use it whenever you only need to iterate once, especially over very large or infinite sequences.

```python
gen = (x**2 for x in range(10**9))      # no memory issue
next(gen)       # 0
next(gen)       # 1

sum(x**2 for x in range(100))           # no intermediate list created
any(x > 0 for x in big_iter)            # short-circuits as soon as a match is found
```

When a generator expression is the only positional argument to a function call, the outer parentheses can be elided: `sum(x**2 for x in range(10))`.

---

## Slicing

Applies to sequences (`list`, `tuple`, `str`, `bytes`). Syntax: `seq[start:stop:step]`. The half-open convention (`stop` not included) is the same one NumPy uses, so the muscle memory transfers.

| Expression | Result |
|---|---|
| `s[2:]` | from index 2 to end |
| `s[:5]` | first 5 elements |
| `s[1:8:2]` | indices 1, 3, 5, 7 |
| `s[::-1]` | reversed copy |
| `s[:]` | shallow copy |
| `s[-3:]` | last 3 elements |

Slicing **never raises** `IndexError` — out-of-range indices are silently clamped.

```python
lst = [0, 1, 2, 3, 4]
lst[1:3] = [10, 20, 30]         # replace a slice in-place (lists only)
del lst[::2]                    # delete every other element
```

---

## Useful sequence functions

```python
len(s)                          # length
max(s)                          # maximum
min(s)                          # minimum
sum(s)                          # sum (numeric iterables)
sorted(s, reverse=True)         # new sorted list
reversed(s)                     # reverse iterator (lazy)
enumerate(s)                    # (index, value) pairs
zip(a, b, c)                    # parallel iteration
zip(*matrix)                    # transpose a matrix-like nested list
any(x > 0 for x in s)           # True if at least one is truthy
all(x > 0 for x in s)           # True if all are truthy
```

---

## `collections` module

The standard-library `collections` module adds specialised container types that solve common patterns more cleanly than rolling your own.

```python
from collections import defaultdict, Counter, deque, OrderedDict

# defaultdict: skip the "if key in d" boilerplate
dd = defaultdict(list)
dd['a'].append(1)               # works even though 'a' was absent
dd['b'].append(2)               # creates a new list automatically

# Counter: frequency tables for hashable objects
c = Counter("aabbbc")           # Counter({'b': 3, 'a': 2, 'c': 1})
c.most_common(2)                # [('b', 3), ('a', 2)]
c['b']                          # 3
c['z']                          # 0 — no KeyError, missing keys read as zero

# deque: O(1) operations on both ends, ideal for queues and bounded buffers
dq = deque([1, 2, 3], maxlen=5)
dq.appendleft(0)
dq.popleft()
dq.rotate(2)                    # rotate elements by n positions

# OrderedDict: mostly obsolete since Python 3.7 (regular dict preserves order),
# but still useful for move_to_end and explicit ordering signals
od = OrderedDict()
od['a'] = 1
od.move_to_end('a')
```

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| `s = {}` for an empty set | Creates an empty dict instead | Use `set()` |
| Mutating a dict while iterating | `RuntimeError: dictionary changed size during iteration` | Iterate over `list(d.items())` |
| Shallow copy of nested lists | Modifying inner lists changes both copies | `copy.deepcopy(lst)` |
| Using a list as dict key | `TypeError: unhashable type: 'list'` | Convert to tuple: `tuple(lst)` |
| `lst.sort()` returns `None` | Forgetting it sorts in place | Use `sorted(lst)` if you need a return value |
| Single-element tuple | `(42)` is just `42` | `(42,)` — trailing comma mandatory |
| `set` ordering | Iteration order is implementation-dependent | Don't rely on it; sort if order matters |
| `dict.fromkeys(keys, [])` | All keys share the same list | Use comprehension: `{k: [] for k in keys}` |
| `lst1 = lst2` then mutating `lst1` | Both names reference the same list | Use `lst1 = lst2.copy()` or `list(lst2)` |
| Comparing lists with `is` | Returns `False` even for equal lists | Use `==` |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Default "bunch of things" container | `list` | Familiar, mutable, all common operations |
| Fixed-shape record | `tuple` or `NamedTuple` | Immutable, hashable, signals intent |
| Key-value lookup | `dict` | O(1) average lookup, ordered iteration |
| Set of unique items, fast `in` checks | `set` | O(1) average membership |
| Group items by category | `defaultdict(list)` | No boilerplate for missing keys |
| Frequency table or top-k | `Counter` | `most_common`, zero-default lookup |
| FIFO queue or LIFO stack with both ends fast | `deque` | O(1) append/pop on either side |
| Dict key built from multiple values | `tuple` of those values | Hashable, no encoding tricks |
| Build a collection in one line from an iterable | Comprehension | Reads top-to-bottom |
| Iterate over a huge sequence once | Generator expression | O(1) memory, lazy |
| Need order, uniqueness, and hashability | `frozenset` (no order) or sorted `tuple` | Choose based on which property matters more |

---

## See also

- [01_types_and_variables.md](01_types_and_variables.md) — mutability, identity vs equality
- [03_control_flow.md](03_control_flow.md) — `for` loops, iteration protocol, comprehensions in context
- [05_functional_programming.md](05_functional_programming.md) — generators, `map`/`filter`, `itertools`
- [11_standard_library.md](11_standard_library.md) — more from `collections` and `itertools`
