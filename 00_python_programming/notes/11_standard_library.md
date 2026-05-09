# Standard Library Reference

## TL;DR

A condensed tour of the modules you reach for most often. **`os` / `sys`** for OS-level operations and runtime introspection. **`datetime`** for dates, times, and durations — always work in UTC internally and convert only at display time, and prefer `datetime.now(tz=timezone.utc)` over the deprecated `datetime.utcnow()`. **`collections`** adds `defaultdict`, `Counter`, `deque`, and `namedtuple` — drop-in upgrades over rolling your own. **`itertools`** provides lazy iterator combinators for everything from chaining and slicing to combinatorics and grouping. **`functools`** offers higher-order helpers (`partial`, `reduce`, `lru_cache`, `wraps`, `total_ordering`). **`re`** is the regex engine — compile patterns once when reused, prefer named groups for readable matches. **`math`** and **`random`** for numerical work; **`secrets`** for cryptographically secure randomness (tokens, passwords). **`typing`** for type hints — modern Python lets you skip the `List`/`Dict`/`Optional`/`Union` imports in favour of `list`, `dict`, `int | None`, `int | str`. **`logging`** for production diagnostics — one logger per module via `logging.getLogger(__name__)`, and use `logger.exception(...)` inside `except` blocks to capture the traceback automatically.

## Cheatsheet

| Module | Use for | Tag |
|---|---|---|
| `os` | OS-level: paths, env, FS ops | System |
| `sys` | Runtime: argv, path, stdout, exit | System |
| `pathlib` | Modern path manipulation | FS (see file_io) |
| `datetime` | Dates, times, durations | Time |
| `time` | Sleep, timestamps, monotonic clock | Time |
| `collections` | `defaultdict`, `Counter`, `deque`, `namedtuple` | Data structures |
| `itertools` | Lazy iterator combinators | Iteration |
| `functools` | `partial`, `lru_cache`, `wraps`, `total_ordering` | Functional |
| `re` | Regular expressions | Text |
| `string` | String constants, `Template` | Text |
| `math` | Floating-point math, constants | Numeric |
| `random` | Pseudo-random numbers | Numeric |
| `secrets` | Cryptographically secure randomness | Security |
| `hashlib` | Cryptographic hashes (sha256, md5, ...) | Security |
| `typing` | Type hints, generics, protocols | Annotations |
| `logging` | Structured runtime diagnostics | Diagnostics |
| `argparse` | Command-line argument parsing | CLI |
| `subprocess` | Run external processes | Process |
| `concurrent.futures` | Thread / process pools | Concurrency |
| `dataclasses` | Auto-generated data containers | Classes |
| `enum` | Symbolic constant sets | Classes |

---

## `os` and `sys`

### `os`

```python
import os

os.getcwd()                                     # current working directory
os.chdir("/tmp")                                # change directory
os.listdir(".")                                 # list contents of a directory
os.makedirs("a/b/c", exist_ok=True)             # create directory tree
os.remove("file.txt")                           # delete file
os.rename("old.txt", "new.txt")                 # rename / move file
os.path.exists("file.txt")                      # check existence
os.path.join("dir", "sub", "file")              # cross-platform path join
os.path.basename("/a/b/file.txt")               # "file.txt"
os.path.dirname("/a/b/file.txt")                # "/a/b"
os.path.splitext("file.txt")                    # ("file", ".txt")

os.environ                                      # dict-like mapping of env variables
os.environ.get("HOME", "/tmp")
os.getenv("API_KEY")                            # equivalent to os.environ.get

os.cpu_count()                                  # number of logical CPUs
os.getpid()                                     # current process ID
```

For path manipulation, prefer `pathlib.Path` (covered in [09_file_io.md](09_file_io.md)). `os.path` remains useful when interfacing with libraries that expect path strings.

### `sys`

```python
import sys

sys.argv                                        # ['script.py', 'arg1', ...] — command-line args
sys.path                                        # list of module search paths
sys.version                                     # Python version string
sys.platform                                    # 'darwin', 'linux', 'win32'
sys.exit(0)                                     # exit with status code (0 = success)
sys.stdin / sys.stdout / sys.stderr             # standard streams
sys.getsizeof(obj)                              # memory size of an object in bytes
sys.modules                                     # dict of imported modules
```

`sys.exit(N)` raises `SystemExit(N)`, which can be caught — useful for deferred cleanup. `os._exit(N)` exits immediately without running cleanup; use it sparingly.

---

## `datetime`

```python
from datetime import date, time, datetime, timedelta, timezone

# Current date/time
today = date.today()
now   = datetime.now()
now_utc = datetime.now(tz=timezone.utc)         # preferred for storage / logs

# Construction
d  = date(2024, 1, 15)
dt = datetime(2024, 1, 15, 10, 30, 0)

# Arithmetic with timedelta
delta = timedelta(days=7, hours=3)
next_week = today + delta
diff = date(2025, 1, 1) - today                 # timedelta object

# Formatting
dt.strftime("%Y-%m-%d %H:%M:%S")                # datetime → string
datetime.strptime("2024-01-15", "%Y-%m-%d")     # string → datetime

# ISO 8601 (preferred for storage and serialisation)
dt.isoformat()                                  # "2024-01-15T10:30:00"
datetime.fromisoformat("2024-01-15T10:30:00")

# Components
dt.year, dt.month, dt.day
dt.hour, dt.minute, dt.second
dt.weekday()                                    # 0 = Monday, 6 = Sunday
dt.date()
dt.time()
```

**Always work in UTC internally**; convert to local time only for display. Use `datetime.now(tz=timezone.utc)` instead of `datetime.utcnow()` — the latter returns a naive datetime that knows nothing about its timezone, and is deprecated in 3.12. For richer time-zone support (named zones, DST), use `zoneinfo.ZoneInfo("Europe/Rome")`.

---

## `collections`

```python
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict

# defaultdict — no KeyError on missing keys
word_count = defaultdict(int)
for word in text.split():
    word_count[word] += 1                       # no need for `if word in d`

groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)

# Counter — frequency tables for any hashable
c = Counter("abracadabra")                      # Counter({'a': 5, 'b': 2, 'r': 2, ...})
c.most_common(3)                                # [('a', 5), ('b', 2), ('r', 2)]
c['a']                                          # 5
c['z']                                          # 0 — missing keys read as zero
c + Counter("abc")                              # add counts
c - Counter("ab")                               # subtract (clamped at 0)

# namedtuple — lightweight, immutable struct
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
p.x, p.y                                        # attribute access
p[0], p[1]                                      # index access still works
p._asdict()                                     # OrderedDict of fields
p._replace(x=10)                                # new namedtuple with one field changed

# deque — double-ended queue, O(1) on both ends
dq = deque([1, 2, 3], maxlen=5)
dq.append(4)                                    # right
dq.appendleft(0)                                # left
dq.pop()                                        # right
dq.popleft()                                    # left
dq.rotate(2)                                    # rotate elements right by 2
```

`OrderedDict` is mostly obsolete since Python 3.7 (regular dicts preserve insertion order), but its `move_to_end` method still has its uses.

For richer record types with type hints, prefer `dataclasses.dataclass` or `typing.NamedTuple` over `collections.namedtuple`.

---

## `itertools`

See [05_functional_programming.md](05_functional_programming.md) for usage patterns. Quick reference:

```python
import itertools as it

# Combining
it.chain([1, 2], [3, 4])                        # 1, 2, 3, 4
it.chain.from_iterable([[1, 2], [3, 4]])        # flatten one level
it.zip_longest([1, 2, 3], ['a'], fillvalue=0)   # zip with padding

# Slicing
it.islice(iterable, n)                          # first n
it.islice(iterable, start, stop, step)
it.takewhile(pred, iter)
it.dropwhile(pred, iter)
it.filterfalse(pred, iter)
it.compress(data, selectors)
it.starmap(func, pairs)                         # map with argument unpacking
it.accumulate(iter, func)                       # running total / scan

# Grouping (input must be sorted by the key first!)
it.groupby(sorted_iter, key=f)

# Combinatorics
it.product(A, B)                                # cartesian product
it.permutations(A, r)
it.combinations(A, r)
it.combinations_with_replacement(A, r)

# Infinite iterators (always pair with islice or takewhile!)
it.count(start, step)
it.cycle(iterable)
it.repeat(value, n)
```

---

## `functools`

```python
from functools import partial, reduce, lru_cache, wraps, cache, total_ordering, cached_property

# partial — pre-fill arguments
add5 = partial(lambda x, y: x + y, y=5)
add5(10)                                        # 15

# lru_cache — memoise, bounded
@lru_cache(maxsize=128)
def expensive(n): ...

# cache — like lru_cache(maxsize=None) (3.9+)
@cache
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# reduce — fold
reduce(lambda a, b: a + b, [1, 2, 3, 4])        # 10

# total_ordering — define __eq__ and one comparison, get the rest free
@total_ordering
class Card:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
    # __le__, __gt__, __ge__ auto-generated

# wraps — preserve metadata in a decorator (see 04_functions.md)
def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kw): ...
    return wrapper
```

---

## `re` — regular expressions

```python
import re

# Compile once, reuse — meaningfully faster when used in a loop
pattern = re.compile(r'\d{3}-\d{4}')
pattern.match("123-4567")

# Match at start of string
m = re.match(r'\d+', '123abc')
m.group()                                       # '123'

# Search anywhere
m = re.search(r'\d+', 'abc123def')
m.group()                                       # '123'
m.start(), m.end()                              # 3, 6

# All non-overlapping matches
re.findall(r'\d+', 'a1 b22 c333')               # ['1', '22', '333']
re.finditer(r'\d+', 'a1 b22')                   # iterator of match objects

# Substitute
re.sub(r'\s+', ' ', 'hello  world')             # 'hello world'
re.sub(r'(\w+)', r'[\1]', 'foo bar')            # '[foo] [bar]' — backreference

# Split
re.split(r'[,;\s]+', 'a, b; c d')               # ['a', 'b', 'c', 'd']

# Groups
m = re.match(r'(\d{4})-(\d{2})-(\d{2})', '2024-01-15')
m.groups()                                      # ('2024', '01', '15')

# Named groups (preferred — self-documenting)
m = re.match(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-01')
m.group('year')                                 # '2024'
m.groupdict()                                   # {'year': '2024', 'month': '01'}

# Flags
re.match(r'hello', 'HELLO', re.IGNORECASE)
re.compile(r'^start', re.MULTILINE)             # ^ matches at start of each line
```

Common pattern syntax:

- `\d` digit, `\w` word char, `\s` whitespace
- `+` one or more, `*` zero or more, `?` zero or one
- `{n,m}` between n and m times
- `^` start, `$` end
- `[abc]` character class, `[^abc]` negated class
- `(?:...)` non-capturing group, `(?=...)` lookahead

For complex parsing, regular expressions become unmaintainable. Switch to a real parser (`pyparsing`, `lark`) or, for structured formats, the dedicated module (`json`, `csv`, `email.parser`).

---

## `math` and `random`

```python
import math

math.sqrt(16)                                   # 4.0
math.floor(3.7)                                 # 3
math.ceil(3.2)                                  # 4
math.log(100, 10)                               # 2.0 — log base 10
math.log2(8)                                    # 3.0
math.exp(1)                                     # e ≈ 2.718
math.pi                                         # 3.14159...
math.e                                          # 2.71828...
math.inf                                        # positive infinity
math.isnan(x)
math.isinf(x)
math.factorial(5)                               # 120
math.gcd(12, 8)                                 # 4
math.comb(10, 3)                                # 120 — combinations
math.perm(10, 3)                                # 720 — permutations
math.isclose(a, b, rel_tol=1e-9)                # safe float equality
```

```python
import random

random.random()                                 # float in [0, 1)
random.uniform(1.0, 10.0)                       # float in [a, b]
random.randint(1, 6)                            # int in [a, b] inclusive
random.choice([1, 2, 3, 4])                     # one random element
random.choices([1, 2, 3], k=5)                  # k elements with replacement
random.sample([1, 2, 3, 4, 5], k=3)             # k elements without replacement
random.shuffle(lst)                             # in-place shuffle
random.seed(42)                                 # reproducibility
```

For cryptographically secure random numbers (tokens, passwords, anything an attacker shouldn't predict), use `secrets`:

```python
import secrets

secrets.token_hex(16)                           # 32-char hex string
secrets.token_urlsafe(16)                       # URL-safe base64 token
secrets.randbelow(100)                          # uniform random int in [0, n)
secrets.choice(["a", "b", "c"])                 # uniform choice from a sequence
```

`random` is fine for simulations and games; `secrets` is mandatory for anything security-sensitive.

---

## `typing`

```python
from typing import (
    Any, Optional, Union,
    List, Dict, Tuple, Set,                     # deprecated in 3.9+: use list, dict, etc.
    Callable, Iterator, Generator,
    TypeVar, Generic,
    Protocol,
    Literal, Final,
    TYPE_CHECKING,
)

# TypeVar — generic functions
T = TypeVar('T')

def first(lst: list[T]) -> T:
    return lst[0]

# Protocol — structural subtyping (duck typing with type checking)
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:              # any object with .draw() qualifies
    obj.draw()

# Literal — constrain to specific values
def align(text: str, mode: Literal["left", "center", "right"]) -> str: ...

# Final — mark as constant (mypy enforced, no runtime effect)
MAX_SIZE: Final = 100
```

In modern Python (3.10+), prefer the built-in collection types and the `|` union syntax: `list[int]` instead of `List[int]`, `int | None` instead of `Optional[int]`, `int | str` instead of `Union[int, str]`. The `typing` imports are only needed for the more advanced constructs (`TypeVar`, `Protocol`, `Literal`, `Final`, `TYPE_CHECKING`).

---

## `logging`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)            # one logger per module, named by module

logger.debug("Detailed debug info")
logger.info("Normal operation")
logger.warning("Something unexpected but non-fatal")
logger.error("Error occurred")
logger.critical("Critical failure")
logger.exception("Error with traceback")        # use inside except blocks

# Lazy formatting — message string is built only if the level is enabled
logger.info("Processing %d items", len(items))
```

Log levels in order: `DEBUG < INFO < WARNING < ERROR < CRITICAL`.

Use `__name__` as the logger name. It creates a logger hierarchy that mirrors your module structure, and handlers/levels can be set at any level of the hierarchy (`logging.getLogger("mypkg.api").setLevel(logging.WARNING)`).

Inside `except` blocks, **always prefer `logger.exception(...)` over `logger.error(...)`**: it captures the full traceback automatically.

---

## Quick mention: other useful modules

```python
# argparse — command-line interfaces
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("--verbose", "-v", action="store_true")
args = parser.parse_args()

# subprocess — run external commands
import subprocess
result = subprocess.run(["ls", "-la"], capture_output=True, text=True, check=True)
print(result.stdout)

# concurrent.futures — thread / process pools
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(fetch, urls))

# enum — symbolic constants
from enum import Enum, auto
class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

# hashlib — cryptographic hashes
import hashlib
hashlib.sha256(b"hello").hexdigest()

# uuid — universally unique identifiers
import uuid
uuid.uuid4()                                    # random UUID
```

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| `datetime.utcnow()` | Naive datetime, no tz info; deprecated in 3.12 | `datetime.now(tz=timezone.utc)` |
| `random` for security | Predictable, not cryptographically secure | Use `secrets` |
| `re.match` when meaning `re.search` | Only matches at the start | `re.search` for anywhere |
| `groupby` without sorting | Only consecutive equal keys are grouped | `sorted` first |
| `lru_cache` on a method | Cache keyed on `self`, can leak references | `functools.cached_property` for per-instance |
| `subprocess.run` without `check=True` | Failures silently ignored | Always pass `check=True` unless you want to handle returncode manually |
| `subprocess.run` without `text=True` | Output is bytes, not str | Pass `text=True` for string output |
| `os.path` mixed with `Path` | Type mismatch errors | Convert with `str(path)` or `Path(s)` |
| `logger.error` inside `except` | Traceback lost | Use `logger.exception` |
| f-string in log message | Builds string even when level disabled | Use `%s` formatting |
| Importing `typing.List` in 3.9+ | Works but deprecated | Use `list[int]` directly |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Filesystem path manipulation | `pathlib.Path` | Cross-platform, composable (see file_io) |
| OS-level operations | `os` | System calls, env vars |
| Runtime args / streams | `sys` | argv, stdout, exit |
| Dates and times | `datetime` + `zoneinfo` | TZ-aware, ISO 8601 |
| Frequency table | `collections.Counter` | `most_common`, zero-default |
| Group-by-key | `collections.defaultdict` | Skip "if key not in d" boilerplate |
| Stack / queue with both ends | `collections.deque` | O(1) on both ends |
| Lightweight record | `collections.namedtuple` or `dataclass` | Tuple semantics + named fields |
| Lazy iterator combinators | `itertools` | Memory-bounded composition |
| Memoise pure function | `functools.lru_cache` | Hashable args, deterministic |
| Memoise expensive attribute | `functools.cached_property` | Per-instance, lazy |
| Pattern matching in text | `re` | Compile once if used in a loop |
| Numerical computing | `math` | Constants, transcendentals |
| Reproducible randomness | `random` + `seed` | Simulations, tests |
| Security-sensitive randomness | `secrets` | Tokens, passwords, IDs |
| Type hints | `typing` (only what you need) | Static checking, IDE support |
| Production diagnostics | `logging` | Levels, handlers, hierarchy |
| Command-line interface | `argparse` | Standard, no dependencies |
| Run external command | `subprocess.run(..., check=True, text=True)` | Reliable, captures output |
| Parallelism | `concurrent.futures` | Pool abstraction, no thread/process plumbing |

---

## See also

- [02_collections.md](02_collections.md) — list, tuple, dict, set
- [04_functions.md](04_functions.md) — `functools.wraps`, decorator patterns
- [05_functional_programming.md](05_functional_programming.md) — `itertools`, `functools` in depth
- [07_exceptions.md](07_exceptions.md) — `logger.exception`, error handling
- [09_file_io.md](09_file_io.md) — `pathlib`, `csv`, `json`, `tempfile`
- [10_environments_and_tooling.md](10_environments_and_tooling.md) — `os.environ`, `.env` files
