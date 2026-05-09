# Modules and Packages

## TL;DR

A **module** is any `.py` file; its top-level functions, classes, and variables become attributes of the imported module object. A **package** is a directory containing an `__init__.py` file, possibly nested. Imports are cached in `sys.modules`: the first `import foo` finds the file on `sys.path`, executes it, and stores the result; subsequent imports return the cached object without re-executing. The `if __name__ == '__main__':` idiom lets a file be both importable as a module and runnable as a script. **`__init__.py`** runs once when its package is first imported and is the place to define the package's public API by re-exporting names from submodules. **Relative imports** (`from . import x`, `from ..sib import y`) work inside packages but not in top-level scripts. **Circular imports** are usually a design smell — fix them by extracting shared code to a third module, deferring imports inside function bodies, or using `from typing import TYPE_CHECKING` for annotation-only imports. The current best-practice project layout uses a `src/` directory to prevent accidental imports of the local package instead of the installed one during testing.

## Cheatsheet

| Pattern | Syntax | When |
|---|---|---|
| Import module | `import math` | Default; clearest namespace |
| Import name | `from math import sqrt` | Frequent use, prefix adds no clarity |
| Alias | `from math import sqrt as sq` | Conflicts or shorter local name |
| Wildcard import | `from math import *` | Avoid in production |
| Module entry point | `if __name__ == '__main__':` | Both library and script |
| Public API list | `__all__ = ['foo', 'bar']` | Controls `from module import *`, signals intent |
| Relative import | `from . import sibling` | Inside a package |
| Parent-package import | `from .. import other` | Across sibling subpackages |
| Type-check-only import | `if TYPE_CHECKING: from x import Y` | Avoid runtime circular imports |
| Inspect module | `dir(m)`, `help(m)`, `m.__file__` | Quick introspection |

---

## Modules

A module is any `.py` file. Importing it executes the file once and binds the resulting module object to a name in the current namespace.

```python
# math_utils.py
PI = 3.14159

def circle_area(r):
    return PI * r ** 2
```

```python
# main.py
import math_utils
math_utils.circle_area(5)
math_utils.PI
```

The module object is a regular Python object — you can assign attributes to it, list its contents with `dir(math_utils)`, and inspect its file path via `math_utils.__file__`.

---

## Import styles

```python
import math                             # imports the module object as 'math'
math.sqrt(16)

from math import sqrt, pi               # imports specific names into the local namespace
sqrt(16)

from math import sqrt as sq             # alias
sq(16)

from math import *                      # imports every public name — avoid in production
```

**Prefer `import module` over `from module import *`**. Explicit imports make it clear where each name comes from and prevent silent collisions when two modules export the same name. `from module import name` is appropriate when the name is used frequently and the module prefix adds no clarity (e.g., `from pathlib import Path`).

Wildcard imports (`from module import *`) are problematic for two reasons: they pollute the local namespace with names you didn't anticipate, and they make name lookup ambiguous (which module did `parse` come from?). They are sometimes used inside `__init__.py` to re-export everything from submodules.

---

## How import works

When Python encounters `import foo`:

1. It checks `sys.modules` — a dict mapping module names to module objects. If `foo` is already there, the cached object is returned.
2. If not cached, Python searches `sys.path` (a list of directories) for `foo.py` or a package directory `foo/`.
3. It compiles the file to bytecode (cached in `__pycache__/`) and executes it.
4. It stores the resulting module object in `sys.modules['foo']`.
5. It binds the name `foo` in the current namespace.

```python
import sys
sys.modules['math']             # the cached math module object
sys.path                        # list of directories searched for modules
```

Subsequent `import foo` calls return the cached object without re-executing the file. This is why **circular imports** can be tricky: if A imports B and B imports A, the first import partially builds the module before the second one tries to read it.

---

## `__name__` and entry point

When Python runs a file directly, the variable `__name__` is set to `'__main__'`. When the same file is imported, `__name__` is set to the module name (e.g., `'mypackage.utils'`). The `if __name__ == '__main__':` idiom exploits this difference to make a file behave as both a library and a script:

```python
# script.py
def main():
    print("Running script")

if __name__ == '__main__':
    main()
```

`python script.py` runs `main()`. `import script` does not. This pattern is mandatory for any file that should be importable but also has a CLI or test harness at the bottom.

---

## Packages

A **package** is a directory with an `__init__.py` file. Subdirectories with their own `__init__.py` become sub-packages.

```
mypackage/
├── __init__.py                 # makes the directory a package
├── utils.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── order.py
└── api/
    ├── __init__.py
    └── routes.py
```

```python
import mypackage.utils
from mypackage.models import user
from mypackage.models.order import Order
```

### `__init__.py`

Executed once when the package is first imported. It serves three purposes:

- **Define the public API** by re-exporting names from submodules.
- **Hide the internal layout** so callers don't need to know which submodule contains which symbol.
- **Run package-level initialisation** (logging setup, configuration loading) — sparingly, since it runs the first time anyone imports anything from the package.

```python
# mypackage/__init__.py
from .utils import helper_function          # expose at package level
from .models.user import User

__all__ = ['User', 'helper_function']       # controls 'from pkg import *', signals public API
```

After this, callers can write the shorter form:

```python
from mypackage import User                  # instead of mypackage.models.user.User
```

Re-exporting in `__init__.py` decouples the package's external API from its internal structure: you can refactor the location of `User` inside the package without breaking callers.

---

## Relative imports

Inside a package, use relative imports to reference sibling modules. They are more refactor-safe than absolute imports because they don't break when the package is renamed:

```python
# mypackage/models/order.py
from . import user                  # same package (models/)
from .user import User              # same package, specific name
from .. import utils                # parent package (mypackage/)
from ..api import routes            # parent package, different subpackage
```

Relative imports only work inside packages, not in top-level scripts. If you try `from . import x` in a file you ran directly with `python file.py`, Python raises `ImportError: attempted relative import with no known parent package`.

---

## `__all__`

A list of strings defining the public API of a module. It serves two purposes: it controls what `from module import *` imports, and it signals intent to readers and tools.

```python
# utils.py
__all__ = ['public_func']           # only public_func is exported by '*'

def public_func():
    ...

def _internal():
    ...
```

Even without `__all__`, the convention is that names starting with `_` are private. Tools like `mypy` and `pyflakes` may use `__all__` to determine which names are intentionally exported.

---

## Namespace packages (Python 3.3+)

Packages without `__init__.py`. Useful for distributing parts of a single logical package across multiple directories or installation paths (a plugin system, for example). Not commonly needed in application code — when in doubt, write the `__init__.py`.

---

## Structuring a project

Current best practice for an installable Python project:

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── pyproject.toml
└── README.md
```

The `src/` layout prevents a subtle and infuriating class of bug: if your package directory is at the project root, then running tests from there causes Python to find the **local** package instead of the **installed** one. With `src/`, the local directory is not on `sys.path`, so the only way to import `mypackage` is to install it (`pip install -e .`), which forces tests to run against the same artefact you ship.

`pyproject.toml` is the modern (PEP 517 / 518) way to declare build configuration and dependencies. It replaces `setup.py` and `setup.cfg` for new projects.

---

## Circular imports

When module A imports B and B imports A, you have a circular dependency. Python doesn't infinitely recurse — it caches the partial module in `sys.modules` and returns whatever has been built so far — but it can produce `ImportError` or surprising `None` values for not-yet-defined names.

Three standard fixes:

1. **Restructure** — extract the shared code into a third module that both A and B import. This is almost always the cleanest solution and signals that the design has a missing layer.
2. **Defer the import** — move it inside the function body that needs it, so it runs at call time rather than module-load time. This breaks the cycle at the cost of a tiny per-call lookup.
3. **`TYPE_CHECKING` guard** for annotation-only imports — when the cycle exists only because of type hints:

```python
from __future__ import annotations         # defer evaluation of annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypackage.models import Order     # imported only by type checkers, not at runtime
```

`from __future__ import annotations` makes Python treat all annotations as strings (PEP 563), evaluated only by tools that need them. Combined with the `TYPE_CHECKING` guard, you can have rich type annotations across modules without runtime cycles.

---

## Useful introspection

```python
import math
dir(math)               # list all attributes of the module
help(math.sqrt)         # docstring and signature
math.__file__           # path to the source file
math.__doc__            # module-level docstring
vars(math)              # dict of all module attributes
math.__name__           # 'math'
math.__package__        # parent package name (or '' for top-level)
```

`dir()` is the fastest way to see what's in an unfamiliar module; `help()` gives you the docstring for any object.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Circular import | `ImportError`, or `None` where a class is expected | Restructure, defer the import, or use `TYPE_CHECKING` |
| Relative import in a script | `ImportError: attempted relative import with no known parent package` | Run as module: `python -m mypackage.script`, or convert to absolute import |
| Mutable module-level state | Tests interfere with each other | Avoid module-level mutable state; use functions or classes |
| `from module import *` collisions | Variables silently overwritten | Always import explicitly |
| `__init__.py` doing heavy work | Slow imports, surprising side effects | Keep it light; defer to function bodies if expensive |
| Same module imported twice from different paths | Two distinct module objects, equality fails | Standardise the import path; one canonical name |
| `sys.path` manipulation in code | Imports work in dev, fail in production | Use proper packaging instead of path hacks |
| Forgetting `__init__.py` in legacy code | Directory not recognised as a package (pre-3.3 behaviour) | Add `__init__.py` (an empty file is fine) |
| Reloading a module after change | Other modules still hold the old version | Restart the interpreter; `importlib.reload` is fragile |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Group related functions/classes | Module | Single file, single responsibility |
| Group related modules | Package | Hierarchy + namespace |
| Re-export submodule names | `__init__.py` with `from .sub import X` | Clean public API |
| Mark intended exports | `__all__ = [...]` | Controls `import *`, hints to tooling |
| File runnable as both library and script | `if __name__ == '__main__':` | Test harness or CLI alongside library code |
| Reference sibling inside package | Relative import | Refactor-safe |
| Reference top-level dependency | Absolute import | Clear, namespaced |
| Defer a heavy import | Inside function body | Avoid pay-on-load cost; break cycles |
| Annotation-only import to avoid cycle | `TYPE_CHECKING` block | No runtime cost |
| Standard project layout | `src/mypackage/` + `tests/` + `pyproject.toml` | Forces test-against-installed-package |

---

## See also

- [04_functions.md](04_functions.md) — `if __name__ == '__main__':` block as entry point
- [10_environments_and_tooling.md](10_environments_and_tooling.md) — virtual environments, `pip install -e .`, `pyproject.toml`
- [11_standard_library.md](11_standard_library.md) — `importlib`, `pkgutil`, `runpy`
