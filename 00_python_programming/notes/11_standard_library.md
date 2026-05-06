# Standard Library Reference

Key modules from the Python standard library, organized by use case.

---

## os and sys

### os

```python
import os

os.getcwd()                         # current working directory
os.chdir("/tmp")                    # change directory
os.listdir(".")                     # list contents of a directory
os.makedirs("a/b/c", exist_ok=True) # create directory tree
os.remove("file.txt")               # delete file
os.rename("old.txt", "new.txt")     # rename / move file
os.path.exists("file.txt")          # check existence
os.path.join("dir", "sub", "file")  # cross-platform path join
os.path.basename("/a/b/file.txt")   # "file.txt"
os.path.dirname("/a/b/file.txt")    # "/a/b"
os.path.splitext("file.txt")        # ("file", ".txt")

os.environ                          # dict-like mapping of env variables
os.environ.get("HOME", "/tmp")
os.getenv("API_KEY")                # equivalent to os.environ.get

os.cpu_count()                      # number of logical CPUs
os.getpid()                         # current process ID
```

### sys

```python
import sys

sys.argv                     # ['script.py', 'arg1', 'arg2'] — command-line args
sys.path                     # list of module search paths
sys.version                  # Python version string
sys.platform                 # 'darwin', 'linux', 'win32'
sys.exit(0)                  # exit with status code (0 = success)
sys.stdin / sys.stdout / sys.stderr  # standard streams
sys.getsizeof(obj)           # memory size of object in bytes
sys.modules                  # dict of imported modules
```

---

## datetime

```python
from datetime import date, time, datetime, timedelta, timezone

# Current date/time
today = date.today()
now   = datetime.now()
now_utc = datetime.now(tz=timezone.utc)

# Construction
d = date(2024, 1, 15)
dt = datetime(2024, 1, 15, 10, 30, 0)

# Arithmetic
delta = timedelta(days=7, hours=3)
next_week = today + delta
diff = date(2025, 1, 1) - today   # timedelta object

# Formatting
dt.strftime("%Y-%m-%d %H:%M:%S")   # datetime → string
datetime.strptime("2024-01-15", "%Y-%m-%d")  # string → datetime

# ISO format (preferred for storage/serialization)
dt.isoformat()                     # "2024-01-15T10:30:00"
datetime.fromisoformat("2024-01-15T10:30:00")

# Components
dt.year, dt.month, dt.day
dt.hour, dt.minute, dt.second
dt.weekday()    # 0=Monday, 6=Sunday
dt.date()       # extract date part
dt.time()       # extract time part
```

Always work in UTC internally; convert to local time only for display. Use `datetime.now(tz=timezone.utc)` instead of `datetime.utcnow()` (the latter is naive and deprecated in 3.12).

---

## collections

```python
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict

# defaultdict
word_count = defaultdict(int)
for word in text.split():
    word_count[word] += 1      # no KeyError on first access

groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)

# Counter
c = Counter("abracadabra")     # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
c.most_common(3)               # [('a', 5), ('b', 2), ('r', 2)]
c['a']                         # 5
c['z']                         # 0 — no KeyError
c + Counter("abc")             # add counts
c - Counter("ab")              # subtract counts

# namedtuple — lightweight struct
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
p.x, p.y                       # 1, 2 — attribute access
p[0], p[1]                     # 1, 2 — index access still works
p._asdict()                    # OrderedDict — useful for serialization
p._replace(x=10)               # new namedtuple with updated field

# deque — double-ended queue, O(1) append/pop on both ends
dq = deque([1, 2, 3], maxlen=5)
dq.append(4)          # right
dq.appendleft(0)      # left
dq.pop()              # right
dq.popleft()          # left
dq.rotate(2)          # rotate elements right by 2
```

---

## itertools

See also [05_functional_programming.md](05_functional_programming.md) for usage patterns.

```python
import itertools as it

it.chain([1,2], [3,4])            # chained iteration
it.chain.from_iterable([[1,2],[3,4]])  # from nested
it.islice(iterable, n)            # take first n
it.islice(iterable, start, stop)
it.takewhile(pred, it)
it.dropwhile(pred, it)
it.filterfalse(pred, it)
it.compress(data, selectors)
it.starmap(func, pairs)           # map with argument unpacking
it.accumulate(it, func)           # running total/product
it.groupby(sorted_iter, key=f)    # group consecutive equal-key elements

it.product(A, B)                  # cartesian product
it.permutations(A, r)
it.combinations(A, r)
it.combinations_with_replacement(A, r)

it.count(start, step)             # infinite counter
it.cycle(iterable)                # infinite repeat
it.repeat(value, n)               # repeat n times
```

---

## functools

```python
from functools import partial, reduce, lru_cache, wraps, cache, total_ordering

# partial — pre-fill arguments
add5 = partial(lambda x, y: x + y, y=5)
add5(10)   # 15

# lru_cache — memoization
@lru_cache(maxsize=128)
def expensive(n): ...

# cache — lru_cache with no size limit (Python 3.9+)
@cache
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# reduce — fold
reduce(lambda a, b: a + b, [1, 2, 3, 4])  # 10

# total_ordering — define __eq__ and one comparison, get the rest free
from functools import total_ordering

@total_ordering
class Card:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
    # __le__, __gt__, __ge__ are auto-generated
```

---

## re — Regular Expressions

```python
import re

# Compile once, use many times (more efficient)
pattern = re.compile(r'\d{3}-\d{4}')

# Match at start of string
m = re.match(r'\d+', '123abc')
m.group()    # '123'

# Search anywhere in string
m = re.search(r'\d+', 'abc123def')
m.group()    # '123'
m.start()    # 3
m.end()      # 6

# Find all non-overlapping matches
re.findall(r'\d+', 'a1 b22 c333')    # ['1', '22', '333']
re.finditer(r'\d+', 'a1 b22')        # iterator of match objects

# Substitute
re.sub(r'\s+', ' ', 'hello  world')  # 'hello world'
re.sub(r'(\w+)', r'[\1]', 'foo bar') # '[foo] [bar]' — backreference

# Split
re.split(r'[,;\s]+', 'a, b; c d')    # ['a', 'b', 'c', 'd']

# Groups
m = re.match(r'(\d{4})-(\d{2})-(\d{2})', '2024-01-15')
m.groups()   # ('2024', '01', '15')

# Named groups
m = re.match(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-01')
m.group('year')   # '2024'
m.groupdict()     # {'year': '2024', 'month': '01'}

# Flags
re.match(r'hello', 'HELLO', re.IGNORECASE)
re.compile(r'^start', re.MULTILINE)    # ^ matches at start of each line
```

Common patterns:
- `\d` digit, `\w` word char, `\s` whitespace
- `+` one or more, `*` zero or more, `?` zero or one
- `{n,m}` between n and m times
- `^` start, `$` end
- `[abc]` character class, `[^abc]` negated class

---

## math and random

```python
import math

math.sqrt(16)           # 4.0
math.floor(3.7)         # 3
math.ceil(3.2)          # 4
math.log(100, 10)       # 2.0 — log base 10
math.log2(8)            # 3.0
math.exp(1)             # e ≈ 2.718
math.pi                 # 3.14159...
math.e                  # 2.71828...
math.inf                # positive infinity
math.isnan(x)
math.isinf(x)
math.factorial(5)       # 120
math.gcd(12, 8)         # 4
math.comb(10, 3)        # 120 — combinations
math.perm(10, 3)        # 720 — permutations
```

```python
import random

random.random()                     # float in [0, 1)
random.uniform(1.0, 10.0)           # float in [a, b]
random.randint(1, 6)                # int in [a, b] inclusive
random.choice([1, 2, 3, 4])         # random element
random.choices([1,2,3], k=5)        # k elements with replacement
random.sample([1,2,3,4,5], k=3)     # k elements without replacement
random.shuffle(lst)                  # in-place shuffle
random.seed(42)                      # reproducibility
```

For cryptographically secure random numbers, use `secrets`:

```python
import secrets
secrets.token_hex(16)   # 32-char hex string — for tokens, passwords
secrets.randbelow(100)  # random int in [0, 100)
```

---

## typing

```python
from typing import (
    Any, Union, Optional,
    List, Dict, Tuple, Set,   # deprecated in 3.9+ (use list, dict, etc. directly)
    Callable, Iterator, Generator,
    TypeVar, Generic,
    Protocol,
    Literal, Final,
    TYPE_CHECKING
)

# TypeVar — generic functions
T = TypeVar('T')

def first(lst: list[T]) -> T:
    return lst[0]

# Protocol — structural subtyping (duck typing with type checking)
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:   # any object with .draw() qualifies
    obj.draw()

# Literal — constrain to specific values
def align(text: str, mode: Literal["left", "center", "right"]) -> str: ...

# Final — mark as constant
MAX_SIZE: Final = 100
```

---

## logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)   # one logger per module, named by module

logger.debug("Detailed debug info")
logger.info("Normal operation")
logger.warning("Something unexpected but non-fatal")
logger.error("Error occurred")
logger.critical("Critical failure")
logger.exception("Error with traceback")   # use inside except blocks

# Log with context
logger.info("Processing %d items", len(items))   # use % formatting, not f-strings
                                                   # lazy evaluation — no work if level is disabled
```

Log levels in order: DEBUG < INFO < WARNING < ERROR < CRITICAL.

Use `__name__` as the logger name — it creates a logger hierarchy that mirrors your module structure, and handlers/levels can be set at any level of the hierarchy.
