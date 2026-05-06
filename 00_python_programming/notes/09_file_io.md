# File I/O

## Opening Files

```python
f = open("data.txt", "r")   # open for reading
data = f.read()
f.close()                    # must close manually
```

Always use the `with` statement — it guarantees the file is closed even if an exception occurs:

```python
with open("data.txt", "r") as f:
    data = f.read()
# f is closed here automatically
```

---

## File Modes

| Mode | Meaning |
|------|---------|
| `'r'` | Read (default). Raises `FileNotFoundError` if absent. |
| `'w'` | Write. Creates file if absent; **truncates** if exists. |
| `'a'` | Append. Creates if absent; adds to end if exists. |
| `'x'` | Exclusive creation. Raises `FileExistsError` if file exists. |
| `'r+'` | Read and write (file must exist) |
| `'b'` | Binary mode — append to another mode: `'rb'`, `'wb'` |
| `'t'` | Text mode (default) |

---

## Reading Files

```python
with open("data.txt") as f:
    content = f.read()          # entire file as a string

with open("data.txt") as f:
    lines = f.readlines()       # list of strings, each ending with '\n'

with open("data.txt") as f:
    line = f.readline()         # one line at a time

# Iterate line-by-line (memory efficient — does not load entire file)
with open("data.txt") as f:
    for line in f:
        process(line.rstrip('\n'))
```

For large files, always iterate line-by-line rather than `read()` or `readlines()`.

---

## Writing Files

```python
with open("output.txt", "w") as f:
    f.write("Hello, world!\n")
    f.writelines(["line1\n", "line2\n"])   # no automatic newlines

# Append without overwriting
with open("log.txt", "a") as f:
    f.write("New entry\n")
```

---

## Encoding

Always specify encoding explicitly for text files to avoid platform-dependent behavior:

```python
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

Default encoding is platform-dependent (`locale.getpreferredencoding()`). Specifying `utf-8` everywhere makes code portable.

---

## pathlib — Modern Path Handling

`pathlib.Path` objects are the preferred way to work with filesystem paths (Python 3.4+). They are cross-platform and more readable than string manipulation.

```python
from pathlib import Path

p = Path("data/input.csv")
p = Path.home() / "Documents" / "file.txt"   # / operator joins paths

# Properties
p.name          # "file.txt"
p.stem          # "file"
p.suffix        # ".txt"
p.parent        # Path("data")
p.parts         # ("data", "input.csv")

# Tests
p.exists()
p.is_file()
p.is_dir()

# Read/write (for small files)
text = p.read_text(encoding="utf-8")
p.write_text("content", encoding="utf-8")
binary = p.read_bytes()
p.write_bytes(b"\x00\x01")

# Create / delete
p.parent.mkdir(parents=True, exist_ok=True)
p.unlink(missing_ok=True)       # delete file

# Directory operations
for child in Path(".").iterdir():
    print(child)

for py_file in Path("src").rglob("*.py"):   # recursive glob
    print(py_file)

# Resolve absolute path
p.resolve()         # resolves symlinks, returns absolute Path
p.relative_to(base) # relative path from base
```

**Prefer `pathlib.Path` over `os.path`** for new code. It is more readable and composable.

---

## CSV Files

```python
import csv

# Reading
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)        # each row as OrderedDict/dict
    for row in reader:
        print(row["column_name"])

# Reading as lists (no header consumption)
with open("data.csv", newline="") as f:
    reader = csv.reader(f)
    for row in reader:                # row is a list of strings
        print(row)

# Writing
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "age", "score"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30, "score": 95.5})
    writer.writerows(list_of_dicts)
```

Always pass `newline=""` when opening CSV files — the `csv` module handles line endings internally.

---

## JSON Files

```python
import json

# Read JSON file
with open("config.json", encoding="utf-8") as f:
    data = json.load(f)             # parses file → Python dict/list

# Write JSON file
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# String ↔ Python object
s = json.dumps(data)                # Python → JSON string
data = json.loads(s)                # JSON string → Python

# Type mappings
# JSON null   → None
# JSON array  → list
# JSON object → dict
# JSON number → int or float
# JSON string → str
# JSON bool   → True / False
```

`json` only serializes basic types. For custom objects, implement `default` callback or subclass `json.JSONEncoder`.

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

## Binary Files

```python
# Reading binary data
with open("image.png", "rb") as f:
    header = f.read(8)      # read first 8 bytes

# Writing binary data
with open("output.bin", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")

# Seek and tell
with open("data.bin", "rb") as f:
    f.seek(10)              # move to byte 10
    f.seek(-4, 2)           # 4 bytes before end
    pos = f.tell()          # current position
```

For structured binary data (network protocols, file formats), use the `struct` module or `ctypes`.

---

## Temporary Files

```python
import tempfile

# Temporary file (auto-deleted when closed)
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("data")
    path = f.name           # get path if needed after context

# Temporary directory (auto-deleted when context exits)
with tempfile.TemporaryDirectory() as tmpdir:
    work_path = Path(tmpdir) / "workfile.txt"
    work_path.write_text("temp data")
```

---

## os Module (path operations)

`pathlib` covers most use cases, but `os` is still useful for:

```python
import os

os.getcwd()                    # current working directory
os.listdir(".")                # list directory contents
os.makedirs("a/b/c", exist_ok=True)
os.remove("file.txt")
os.rename("old.txt", "new.txt")
os.path.join("dir", "file")   # cross-platform path join (prefer pathlib)
os.path.exists("file.txt")
os.environ["HOME"]             # access environment variables
os.environ.get("API_KEY", "")  # safe access with default
```
