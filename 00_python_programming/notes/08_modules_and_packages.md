# Modules and Packages

## Modules

A **module** is any `.py` file. Its contents (functions, classes, variables) become attributes of the module object when imported.

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

---

## Import Styles

```python
import math                          # import the module object
math.sqrt(16)

from math import sqrt, pi           # import specific names into local namespace
sqrt(16)

from math import sqrt as sq         # alias
sq(16)

from math import *                   # import all public names — avoid in production
```

**Prefer `import module` over `from module import *`**. Explicit imports make it clear where names come from and avoid namespace collisions.

**`from module import name`** is appropriate when the name is used frequently and the module prefix adds no clarity.

---

## How Import Works

When you `import foo`:

1. Python checks `sys.modules` cache — if already imported, returns the cached module object
2. If not cached: finds `foo.py` (or `foo/`) in `sys.path`, compiles to bytecode, executes the file
3. Stores the module in `sys.modules['foo']`
4. Binds the name `foo` in the current namespace

```python
import sys
sys.modules['math']   # the cached math module object
sys.path              # list of directories searched for modules
```

Subsequent `import foo` calls return the cached object — the module file is not re-executed. This is why circular imports can be tricky.

---

## `__name__` and Entry Point

When Python runs a file directly, `__name__` is set to `'__main__'`. When imported, `__name__` is the module name.

```python
# script.py
def main():
    print("Running script")

if __name__ == '__main__':
    main()
```

This pattern allows a file to be both importable as a module and runnable as a script, without executing the script logic on import.

---

## Packages

A **package** is a directory with an `__init__.py` file. Nested packages create a hierarchy.

```
mypackage/
├── __init__.py          # makes the directory a package
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

Executed when the package is first imported. Used to:
- Define the package's public API
- Expose submodule names at the package level
- Run initialization code

```python
# mypackage/__init__.py
from .utils import helper_function     # expose at package level
from .models.user import User

__all__ = ['User', 'helper_function']  # controls what 'from pkg import *' exports
```

After this, users can write:

```python
from mypackage import User   # instead of mypackage.models.user.User
```

---

## Relative Imports

Inside a package, use relative imports to reference sibling modules:

```python
# mypackage/models/order.py
from . import user            # same package (models/)
from .user import User        # same package, specific name
from .. import utils          # parent package (mypackage/)
from ..api import routes      # parent package, different subpackage
```

Relative imports only work inside packages, not in top-level scripts.

---

## `__all__`

List of strings defining the public API of a module. Controls what `from module import *` imports, and signals intent to other developers.

```python
# utils.py
__all__ = ['public_func']   # only public_func is exported

def public_func():
    ...

def _internal():
    ...
```

Even without `__all__`, the convention is that names starting with `_` are private.

---

## Namespace Packages (Python 3.3+)

Packages without `__init__.py`. Useful for distributing parts of a package across multiple directories or installation paths. Not commonly needed in application code.

---

## Structuring a Project

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

The `src/` layout prevents accidental imports of the local package instead of the installed one during testing. It is the current best practice.

---

## Circular Imports

A imports B, and B imports A — a circular dependency. Python partially handles this (the import cache prevents infinite loops) but it can cause `ImportError` or unexpected `None` values.

Fixes:
- Restructure: move shared code to a third module that both can import
- Import inside the function body (deferred import) where the circular dependency is needed
- Use `TYPE_CHECKING` for type annotation-only imports

```python
from __future__ import annotations   # defer evaluation of annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypackage.models import Order  # only imported by type checkers, not at runtime
```

---

## Useful Introspection

```python
import math
dir(math)           # list all attributes of the module
help(math.sqrt)     # docstring for sqrt
math.__file__       # path to the module source file
math.__doc__        # module-level docstring
vars(math)          # dict of all module attributes
```
