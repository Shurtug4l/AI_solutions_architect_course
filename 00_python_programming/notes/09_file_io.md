# File I/O

## TL;DR

Always open files with the `with` statement — it guarantees the handle is closed even if the body raises. Always specify `encoding="utf-8"` for text files; the platform default is non-portable. Iterate line-by-line for large files, never `read()` or `readlines()` (the former loads the whole file into memory; the latter splits it into a list of strings just as wastefully). Use **`pathlib.Path`** for path manipulation in new code — it is cross-platform, composable with the `/` operator, and offers convenient methods (`read_text`, `write_text`, `glob`, `mkdir`). For structured formats, the standard library covers the common cases: **`csv`** for tabular text (always with `newline=""`), **`json`** for nested data (use `indent=2` for human-readable output and `ensure_ascii=False` to keep non-ASCII characters intact). For binary files use the `'b'` mode flag. **`tempfile`** handles scratch files and directories with auto-cleanup.

## Cheatsheet

| Pattern | Syntax | When |
|---|---|---|
| Open text | `with open(path, 'r', encoding='utf-8') as f:` | Reading text |
| Open write | `with open(path, 'w', encoding='utf-8') as f:` | Truncates if exists |
| Append | `with open(path, 'a', ...) as f:` | Adds to end |
| Exclusive create | `with open(path, 'x', ...) as f:` | Fails if exists |
| Binary | `with open(path, 'rb') as f:` | Bytes, not text |
| Iterate lines | `for line in f:` | Memory-efficient for large files |
| Path object | `Path('a') / 'b' / 'c.txt'` | Cross-platform path construction |
| Read whole text | `Path(p).read_text(encoding='utf-8')` | Small files, one-liner |
| Recursive glob | `Path(root).rglob('*.py')` | Find files by pattern |
| CSV read | `csv.DictReader(f)` | Header → dict per row |
| CSV write | `csv.DictWriter(f, fieldnames=...)` | Always pass `newline=""` |
| JSON read | `json.load(f)` | File → Python objects |
| JSON write | `json.dump(obj, f, indent=2, ensure_ascii=False)` | Human-readable, non-ASCII safe |
| Temp file | `with tempfile.NamedTemporaryFile() as f:` | Auto-deleted on close |
| Temp directory | `with tempfile.TemporaryDirectory() as d:` | Auto-deleted on exit |

---

## Opening files

```python
f = open("data.txt", "r")           # open for reading
data = f.read()
f.close()                           # must close manually — easy to forget on exception path
```

Always use the `with` statement — it guarantees `close()` runs even if the body raises:

```python
with open("data.txt", "r") as f:
    data = f.read()
# f is closed here automatically
```

The `with` form is mandatory in production code. The bare `open` form should appear only in throwaway scripts where the leak doesn't matter.

---

## File modes

| Mode | Meaning |
|---|---|
| `'r'` | Read (default). Raises `FileNotFoundError` if absent. |
| `'w'` | Write. Creates if absent, **truncates** to zero length if exists. |
| `'a'` | Append. Creates if absent, adds to end if exists. |
| `'x'` | Exclusive creation. Raises `FileExistsError` if file already exists. |
| `'r+'` | Read and write. File must exist. |
| `'b'` | Binary. Append to another mode: `'rb'`, `'wb'`, `'rb+'`. |
| `'t'` | Text mode. Default; rarely written explicitly. |

`'w'` is the most dangerous: it silently destroys existing content. Use `'x'` when you want creation to fail rather than overwrite.

---

## Reading files

```python
with open("data.txt", encoding="utf-8") as f:
    content = f.read()              # entire file as one string

with open("data.txt", encoding="utf-8") as f:
    lines = f.readlines()           # list of strings, each ending with '\n'

with open("data.txt", encoding="utf-8") as f:
    line = f.readline()             # one line at a time, returns '' at EOF

# Idiomatic: iterate line-by-line, memory proportional to one line
with open("data.txt", encoding="utf-8") as f:
    for line in f:
        process(line.rstrip('\n'))
```

For large files, **always** iterate line-by-line. `read()` and `readlines()` load the entire file into memory, which is fine for KB-sized configs but disastrous for GB-sized logs.

---

## Writing files

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, world!\n")
    f.writelines(["line1\n", "line2\n"])    # no newlines added automatically

# Append without overwriting
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("New entry\n")
```

`writelines` does **not** add line terminators — it just concatenates. The name is misleading; treat it as "write a list of strings".

---

## Encoding

Always specify encoding explicitly for text files. The default depends on `locale.getpreferredencoding()`, which differs across platforms (UTF-8 on macOS/Linux, often `cp1252` on Windows). Hard-coding `encoding="utf-8"` makes your code portable and prevents the inevitable mojibake when a script that worked locally fails on a colleague's machine.

```python
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

For files that may contain non-Latin characters, also pass `errors="strict"` (the default — fail loudly on invalid sequences) rather than the lenient alternatives like `"replace"` or `"ignore"` that hide encoding bugs.

---

## `pathlib` — modern path handling

`pathlib.Path` is the preferred way to manipulate filesystem paths in Python 3.4+. It is cross-platform, composable, and offers methods that string-based path manipulation lacks.

```python
from pathlib import Path

p = Path("data/input.csv")
p = Path.home() / "Documents" / "file.txt"      # / operator joins paths

# Properties
p.name              # "file.txt"
p.stem              # "file"
p.suffix            # ".txt"
p.parent            # Path("data")
p.parts             # ("data", "input.csv")

# Tests
p.exists()
p.is_file()
p.is_dir()

# Read / write (for small files)
text = p.read_text(encoding="utf-8")
p.write_text("content", encoding="utf-8")
binary = p.read_bytes()
p.write_bytes(b"\x00\x01")

# Create / delete
p.parent.mkdir(parents=True, exist_ok=True)
p.unlink(missing_ok=True)                       # delete file

# Directory operations
for child in Path(".").iterdir():
    print(child)

for py_file in Path("src").rglob("*.py"):       # recursive glob
    print(py_file)

# Resolve absolute path
p.resolve()                 # resolves symlinks, returns absolute Path
p.relative_to(base)         # path of self relative to `base`
```

Prefer `pathlib.Path` over `os.path` for new code. The `os.path` functions are still useful for the rare cases pathlib doesn't cover (and for backwards compatibility with old code), but they are string-based and clunky by comparison.

---

## CSV files

```python
import csv

# Reading as dicts (the common case — first row is the header)
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["column_name"])

# Reading as lists (no header consumption)
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:                          # row is a list of strings
        print(row)

# Writing
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "age", "score"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30, "score": 95.5})
    writer.writerows(list_of_dicts)
```

Always pass `newline=""` when opening CSV files. The `csv` module handles line endings internally; without `newline=""`, Python's universal newline translation can corrupt rows on Windows.

For pandas-style work on large CSVs (filtering, aggregation, joining), reach for pandas (`pd.read_csv`) instead. The `csv` module is the right tool for streaming row-by-row processing without dependencies.

---

## JSON files

```python
import json

# Read JSON file → Python object
with open("config.json", encoding="utf-8") as f:
    data = json.load(f)

# Write Python object → JSON file
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# String round-trip
s = json.dumps(data)                # Python → JSON string
data = json.loads(s)                # JSON string → Python
```

Type mappings:

| JSON | Python |
|---|---|
| `null` | `None` |
| array | `list` |
| object | `dict` |
| number | `int` or `float` |
| string | `str` |
| `true` / `false` | `True` / `False` |

`indent=2` makes the output human-readable; omit it for compact machine-to-machine output. `ensure_ascii=False` preserves non-ASCII characters (otherwise they get escaped to `\uXXXX`).

`json` only serialises the basic types. For custom objects (datetime, decimal, custom classes), provide a `default=` callback or subclass `json.JSONEncoder`:

```python
import json
from datetime import date

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

json.dumps({"date": date.today()}, cls=DateEncoder)
```

---

## Binary files

```python
# Reading binary data
with open("image.png", "rb") as f:
    header = f.read(8)              # read first 8 bytes

# Writing binary data
with open("output.bin", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")

# Seek and tell
with open("data.bin", "rb") as f:
    f.seek(10)                      # move to byte 10 from start
    f.seek(-4, 2)                   # 4 bytes before end (whence=2)
    pos = f.tell()                  # current byte offset
```

For structured binary data (network protocols, file formats), the `struct` module packs and unpacks values according to a format string. For larger binary protocols, consider `ctypes` or third-party libraries that match the format.

---

## Temporary files

The `tempfile` module creates files and directories that clean themselves up. Use it for scratch space, test fixtures, and intermediate processing.

```python
import tempfile

# Temporary file (auto-deleted when closed, unless delete=False)
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("data")
    path = f.name                   # get path if you need it after the context

# Temporary directory (auto-deleted when context exits)
with tempfile.TemporaryDirectory() as tmpdir:
    work_path = Path(tmpdir) / "workfile.txt"
    work_path.write_text("temp data")
```

`NamedTemporaryFile` with `delete=False` is a common pattern when you need to pass the file path to a subprocess or another library — the file persists until you explicitly remove it.

---

## `os` module (path operations)

`pathlib` covers most use cases, but `os` is still useful for system-level operations and path strings:

```python
import os

os.getcwd()                                 # current working directory
os.listdir(".")                             # list directory contents (strings, not Path objects)
os.makedirs("a/b/c", exist_ok=True)         # create nested directories
os.remove("file.txt")
os.rename("old.txt", "new.txt")
os.path.join("dir", "file")                 # cross-platform path join (prefer pathlib's /)
os.path.exists("file.txt")
os.environ["HOME"]                          # access environment variable
os.environ.get("API_KEY", "")               # safe access with default
```

When working with both `os.path` strings and `Path` objects, `Path(os_path_string)` and `str(path_object)` convert between them.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Forgetting `encoding="utf-8"` | Mojibake on different platforms | Always specify encoding explicitly |
| `open(path, 'w')` on existing file | Silent truncation, content lost | Use `'x'` to fail, or `'a'` to append |
| Loading a huge file with `read()` | Memory blows up | Iterate line-by-line: `for line in f:` |
| CSV without `newline=""` | Garbled rows on Windows | Always pass `newline=""` to `open` for CSV |
| `writelines` not adding newlines | All output on one line | Append `'\n'` to each string yourself |
| JSON with non-serialisable types | `TypeError: Object of type ... is not JSON serializable` | Provide `default=` callback or custom encoder |
| `json.dumps` escaping accents | `"café"` instead of `"café"` | `ensure_ascii=False` |
| `Path / str` order | `"a" / Path("b")` raises | Path must come first: `Path("a") / "b"` |
| Reading a binary file in text mode | `UnicodeDecodeError` | Use `'rb'` mode |
| Forgetting `with` | File handle leaks on exception | Always use `with open(...)` |
| `temp.NamedTemporaryFile` deleted before reading | File gone before subprocess uses it | `delete=False`, manual `os.remove` later |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Open a file safely | `with open(...) as f:` | Auto-close on any exit |
| Read a small text file | `Path(p).read_text(encoding="utf-8")` | One-liner, modern |
| Stream a large text file | `for line in open(...)` | O(1) memory |
| Build paths cross-platform | `pathlib.Path` and `/` operator | Cross-platform, composable |
| List files matching a pattern | `Path.glob('*.py')` / `rglob` | No need for `fnmatch` or `os.walk` |
| Tabular text I/O | `csv.DictReader` / `csv.DictWriter` | Header-as-keys, streaming |
| Heavy CSV manipulation | `pandas.read_csv` | Vectorised filtering / joining |
| Nested data I/O | `json.load` / `json.dump` | Standard interchange format |
| Custom types in JSON | Custom `JSONEncoder` or `default=` | Bridge non-trivial Python objects |
| Binary format | `'rb'` / `'wb'`, plus `struct` for layout | Bytes precision |
| Scratch file with auto-cleanup | `tempfile.NamedTemporaryFile` | No manual deletion |
| Scratch directory with auto-cleanup | `tempfile.TemporaryDirectory` | Whole tree is wiped on exit |
| Environment variable | `os.environ.get("X", default)` | Safe lookup with fallback |

---

## See also

- [02_collections.md](02_collections.md) — iterating over file lines as a sequence
- [07_exceptions.md](07_exceptions.md) — `with` statement, context managers in detail, `FileNotFoundError`
- [10_environments_and_tooling.md](10_environments_and_tooling.md) — `.env` files, environment variables
- [11_standard_library.md](11_standard_library.md) — `os`, `sys`, `tempfile`, `shutil` for higher-level file ops
