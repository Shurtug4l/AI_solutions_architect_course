# Collections

## List

Ordered, mutable sequence. The general-purpose workhorse collection.

```python
lst = [1, 2, 3, "four", True]   # heterogeneous, but homogeneous is better practice

# Access
lst[0]       # 1
lst[-1]      # True
lst[1:3]     # [2, 3]      — slicing returns a new list
lst[::2]     # [1, 3, True] — every other element
lst[::-1]    # reversed copy

# Mutation
lst.append(5)           # add to end — O(1) amortized
lst.extend([6, 7])      # concatenate another iterable — O(k)
lst.insert(0, 0)        # insert at index — O(n)
lst.pop()               # remove and return last — O(1)
lst.pop(0)              # remove and return at index — O(n)
lst.remove(3)           # remove first occurrence of value — O(n)
lst.index(2)            # find index of first occurrence
lst.count(1)            # count occurrences
lst.reverse()           # in-place reverse
lst.sort()              # in-place sort
lst.sort(key=lambda x: x[1], reverse=True)  # custom sort key
sorted(lst)             # returns a new sorted list (non-destructive)

# Copy (shallow)
copy_lst = lst.copy()   # or lst[:]
import copy
deep_copy = copy.deepcopy(lst)   # for nested mutable objects
```

**Shallow vs deep copy**: a shallow copy copies the list container but not nested objects — nested mutable objects are still shared.

---

## Tuple

Ordered, **immutable** sequence. Use for heterogeneous data that should not change (e.g., coordinates, database records, function return values).

```python
t = (1, 2, 3)
t = 1, 2, 3         # parentheses optional
single = (42,)      # trailing comma mandatory for single-element tuple
empty  = ()

# Same indexing/slicing as list
t[0]        # 1
t[-1]       # 3
len(t)      # 3

# Unpacking
x, y, z = t
x, *rest = t   # x=1, rest=[2, 3]

# Named tuple — tuple with field access
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
p.x     # 1
p[0]    # 1 — still indexable

# Tuple is hashable (if all elements are hashable) → can be dict key or set member
d = {(0, 0): 'origin'}
```

Prefer tuples over lists when the structure is fixed — it signals intent and gains hashability.

---

## Dictionary

Ordered (insertion order preserved since Python 3.7), mutable mapping of **key → value**. Keys must be hashable.

```python
d = {'a': 1, 'b': 2}
d = dict(a=1, b=2)         # keyword syntax
d = dict([('a', 1)])       # from iterable of pairs

# Access
d['a']                     # 1; raises KeyError if missing
d.get('a')                 # 1; returns None if missing (safe)
d.get('z', 0)              # 0; default value if missing

# Mutation
d['c'] = 3                 # add or update
d.update({'d': 4, 'e': 5}) # merge from another dict
del d['a']                 # delete key
d.pop('b')                 # remove and return value
d.setdefault('f', 0)       # insert key with default if absent, return value

# Iteration
d.keys()                   # dict_keys view
d.values()                 # dict_values view
d.items()                  # dict_items view — pairs (key, value)

for key, value in d.items():
    print(key, value)

# Merge (Python 3.9+)
merged = d1 | d2           # new dict
d1 |= d2                   # update in place

# Dict comprehension
squares = {x: x**2 for x in range(10)}
```

**Dict views** are live: they reflect changes to the dict. Don't mutate the dict while iterating over it.

---

## Set

Unordered collection of **unique, hashable** elements. No indexing or slicing.

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])    # {1, 2, 3} — duplicates removed
empty = set()             # not {}, which is an empty dict

# Mutation
s.add(4)
s.remove(2)     # raises KeyError if absent
s.discard(99)   # safe removal (no error if absent)
s.pop()         # remove and return an arbitrary element

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}

a | b           # {1, 2, 3, 4}  — union
a & b           # {2, 3}        — intersection
a - b           # {1}           — difference (in a, not in b)
a ^ b           # {1, 4}        — symmetric difference

a.issubset(b)   # a <= b
a.issuperset(b) # a >= b
a.isdisjoint(b) # no common elements

# Fast membership test — O(1) average vs O(n) for list
42 in s
```

`frozenset` is the immutable, hashable variant. Use as dict keys or set elements when you need a set of sets.

---

## Comprehensions

Concise syntax for building collections from iterables. Preferred over manual loops when the logic is simple.

### List Comprehension

```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]

# Nested
matrix = [[1, 2, 3], [4, 5, 6]]
flat   = [val for row in matrix for val in row]   # [1, 2, 3, 4, 5, 6]
```

### Dict Comprehension

```python
{k: v for k, v in zip(keys, values)}
{k: v for k, v in d.items() if v > 0}    # filter
```

### Set Comprehension

```python
{x**2 for x in range(10)}
```

### Generator Expression

Like a list comprehension but **lazy**: produces values one at a time, uses O(1) memory.

```python
gen = (x**2 for x in range(10**9))   # no memory issue
next(gen)     # 0
next(gen)     # 1
sum(x**2 for x in range(100))        # no list created
```

Use generator expressions in function calls when you only need to iterate once.

---

## Slicing

Applies to sequences (list, tuple, str, bytes). Syntax: `seq[start:stop:step]`

| Expression | Result |
|-----------|--------|
| `s[2:]` | from index 2 to end |
| `s[:5]` | first 5 elements |
| `s[1:8:2]` | indices 1, 3, 5, 7 |
| `s[::-1]` | reversed copy |
| `s[:]` | shallow copy |
| `s[-3:]` | last 3 elements |

Slicing never raises `IndexError` — out-of-range indices are silently clamped.

```python
lst = [0, 1, 2, 3, 4]
lst[1:3] = [10, 20, 30]   # replace slice in-place (list only)
del lst[::2]              # delete every other element
```

---

## Useful Sequence Functions

```python
len(s)                  # length
max(s)                  # maximum value
min(s)                  # minimum value
sum(s)                  # sum (numeric iterables)
sorted(s, reverse=True) # new sorted list
reversed(s)             # reverse iterator
enumerate(s)            # (index, value) pairs
zip(a, b, c)            # (a[i], b[i], c[i]) tuples
zip(*matrix)            # transpose
any(x > 0 for x in s)  # True if at least one condition is True
all(x > 0 for x in s)  # True if all conditions are True
```

---

## collections Module

```python
from collections import defaultdict, Counter, deque, OrderedDict

# defaultdict: no KeyError on missing keys
dd = defaultdict(list)
dd['a'].append(1)         # works even though 'a' was absent

# Counter: count hashable objects
c = Counter("aabbbc")     # Counter({'b': 3, 'a': 2, 'c': 1})
c.most_common(2)          # [('b', 3), ('a', 2)]
c['b']                    # 3
c['z']                    # 0 — no KeyError

# deque: efficient O(1) append/pop from both ends
dq = deque([1, 2, 3], maxlen=5)
dq.appendleft(0)
dq.popleft()
dq.rotate(2)              # rotate elements

# OrderedDict: remembers insertion order (mostly obsolete in Python 3.7+)
# but still useful for move_to_end()
od = OrderedDict()
od['a'] = 1
od.move_to_end('a')
```
