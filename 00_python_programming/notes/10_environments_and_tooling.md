# Virtual Environments and Tooling

## TL;DR

Every Python project should have its own **virtual environment**. Different projects need different versions of the same dependency, and installing globally guarantees conflicts sooner or later. The standard-library tool is **`venv`** (`python -m venv .venv`); for new projects in 2024+ the faster, modern alternative is **`uv`** (Rust-based, drop-in for `pip` + `venv`). Dependencies are declared in **`pyproject.toml`** (PEP 621), which replaces the legacy `setup.py` / `setup.cfg` / `requirements.txt` triad with a single declarative file. The dependency convention has crystallised around three layers: **direct** dependencies in `pyproject.toml` (with version bounds, not pins), a **lock file** for reproducible installs (`uv.lock` or `poetry.lock`), and **dev/test extras** declared in `[project.optional-dependencies]`. For code quality, two tools cover most needs: **`ruff`** (lint + format + import sort, replacing flake8 + black + isort with a single fast tool) and **`mypy`** (static type checking). Environment-specific values (API keys, database URLs) belong in `.env` files loaded with `python-dotenv` — never committed to git.

## Cheatsheet

| Task | Command |
|---|---|
| Create venv (stdlib) | `python -m venv .venv` |
| Create venv (uv) | `uv venv` |
| Activate (mac/linux) | `source .venv/bin/activate` |
| Activate (windows) | `.venv\Scripts\activate` |
| Deactivate | `deactivate` |
| Install package | `pip install requests` / `uv pip install requests` |
| Install pinned | `pip install requests==2.31.0` |
| Install range | `pip install "requests>=2.28,<3.0"` |
| Install editable | `pip install -e .` |
| Install with extras | `pip install -e ".[dev]"` |
| Snapshot environment | `pip freeze > requirements.txt` |
| Sync from pyproject (uv) | `uv sync` / `uv sync --extra dev` |
| Lint + format | `ruff check . && ruff format .` |
| Type check | `mypy src/` |
| Run tests | `pytest` |
| Read env file | `from dotenv import load_dotenv; load_dotenv()` |

---

## Why virtual environments

Each Python project may need different versions of the same dependency: project A wants `numpy 1.26`, project B is stuck on `numpy 1.21` for compatibility. Installing everything into the system Python guarantees these versions collide. **Virtual environments** isolate per-project dependencies into a self-contained directory, leaving the system Python untouched and letting you have an arbitrary number of independent projects on one machine.

---

## `venv` (standard library)

```bash
# Create environment
python -m venv .venv

# Activate
source .venv/bin/activate            # macOS / Linux
.venv\Scripts\activate                # Windows

# Deactivate
deactivate

# After activation, 'python' and 'pip' point to the venv
which python                          # /path/to/project/.venv/bin/python
```

Once activated, `pip install` installs into the venv, not the system Python. The convention is to name the directory `.venv` (hidden, local) and add it to `.gitignore`.

---

## `pip`

```bash
pip install requests                  # latest version
pip install requests==2.31.0          # pin exact version
pip install "requests>=2.28,<3.0"     # version range
pip install -e .                      # install current project in editable mode
pip install -r requirements.txt       # install from file

pip uninstall requests
pip list                              # installed packages
pip show requests                     # metadata for one package
pip freeze                            # installed packages with exact versions
pip freeze > requirements.txt         # snapshot the entire environment

pip install --upgrade requests        # upgrade to latest
```

### `requirements.txt`

A flat list of pinned dependencies for reproducible installs:

```
requests==2.31.0
numpy==1.26.2
pandas==2.1.4
```

`pip freeze` captures the entire environment including transitive dependencies — perfect for reproducibility but verbose. For hand-written files, you can pin only your direct dependencies and let pip resolve the rest. Either way, `requirements.txt` is being supplanted by `pyproject.toml` for new projects.

---

## `pyproject.toml`

The modern, standardised way (PEP 517 / 518 / 621) to declare project metadata, dependencies, and build configuration. One file replaces the older trio of `setup.py`, `setup.cfg`, and `requirements.txt`.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mypackage"
version = "1.0.0"
description = "A short description"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "numpy>=1.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff",
    "mypy",
]

[project.scripts]
mycli = "mypackage.cli:main"          # creates a CLI command on install
```

Install with the dev extras:

```bash
pip install -e ".[dev]"
```

Use **version ranges**, not exact pins, for direct dependencies in `pyproject.toml` — pinning is the lock file's job, while `pyproject.toml` declares what your code is compatible with.

---

## `uv` — fast Python package manager

`uv` (from Astral) is a Rust-based drop-in replacement for `pip` + `venv`. It is dramatically faster for dependency resolution and installation — minutes-long resolves typically finish in seconds.

```bash
# Install uv
pip install uv                                    # or: curl -Ls https://astral.sh/uv/install.sh | sh

# Create and activate venv
uv venv                                           # creates .venv
source .venv/bin/activate

# Install packages
uv pip install requests
uv pip install -r requirements.txt
uv pip install -e ".[dev]"

# Sync from pyproject.toml (resolves and installs the declared dependencies)
uv sync
uv sync --extra dev

# Lock dependencies to a specific resolution (commit uv.lock for reproducibility)
uv lock
```

`uv` is compatible with `requirements.txt` and `pyproject.toml`, so you can adopt it without changing your project layout. For new projects in 2024+ it is the recommended default.

---

## Dependency management: comparison

| Tool | File | Lock file | Notes |
|---|---|---|---|
| `pip` + `venv` | `requirements.txt` | None | Standard library, simple, no resolver guarantees |
| `pip` + `pyproject.toml` | `pyproject.toml` | None | Modern metadata, still no lock |
| `uv` | `pyproject.toml` | `uv.lock` | Fast, modern, recommended default |
| `poetry` | `pyproject.toml` | `poetry.lock` | Mature, opinionated, good for publishing |
| `pipenv` | `Pipfile` | `Pipfile.lock` | Older, less actively maintained |

For new projects: `uv` with `pyproject.toml`. For simple one-file scripts: `venv` + `pip` is enough. For libraries you publish to PyPI: either `uv` or `poetry`, both produce valid wheels.

---

## Python version management

Multiple Python versions on the same machine, useful when one project needs 3.10 and another 3.12:

```bash
# pyenv (macOS / Linux)
pyenv install 3.12.0
pyenv global 3.12.0                   # set machine-wide default
pyenv local 3.11.6                    # set for current directory (writes .python-version)
pyenv versions                        # list installed versions

# uv also manages Python versions
uv python install 3.12
uv python list
```

`pyenv` was the standard for years. `uv` now does the same job and integrates with venv / dependency management, which is one fewer tool to install.

---

## Code quality tools

| Tool | Purpose | Configuration |
|---|---|---|
| `ruff` | Linter + formatter (replaces flake8 / black / isort) | `pyproject.toml` `[tool.ruff]` |
| `black` | Code formatter (legacy alternative to `ruff format`) | `pyproject.toml` `[tool.black]` |
| `mypy` | Static type checker | `mypy.ini` or `[tool.mypy]` |
| `pytest` | Test runner | `[tool.pytest.ini_options]` |

```bash
ruff check .                          # lint
ruff check --fix .                    # lint + auto-fix
ruff format .                         # format

mypy src/                             # type-check the package

pytest                                # run all tests
pytest tests/test_core.py -v          # run one test file, verbose
pytest -k "test_login"                # run tests whose name matches the pattern
```

A minimal `pyproject.toml` ruff config that gets you 90% of the value:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]        # pycodestyle, pyflakes, isort, pyupgrade
```

`ruff` is fast enough to run on every save without noticeable lag, which is the right operational baseline.

---

## `.gitignore` essentials

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
.mypy_cache/
.ruff_cache/
.pytest_cache/
dist/
build/
*.egg-info/
.env
```

Two things you must never commit: the virtual environment directory (`.venv/`) and `.env` files containing secrets. Generated artefacts (`__pycache__`, `dist/`, `build/`, `.egg-info`) belong out of version control too — they're produced by tools, not authored.

---

## Environment variables and `.env` files

```python
import os

api_key = os.environ.get("API_KEY")           # returns None if not set
api_key = os.environ["API_KEY"]               # raises KeyError if not set

# Load from .env file (python-dotenv)
from dotenv import load_dotenv
load_dotenv()                                 # reads .env into os.environ
api_key = os.environ.get("API_KEY")
```

`.env` file format:

```
API_KEY=abc123
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
```

**Never commit `.env` to version control.** Document the required variables in a checked-in `.env.example` file (with no values) so collaborators know what to fill in.

For production deployments, prefer reading from the actual environment (set by your orchestrator, container, or CI system) over `.env` files. `.env` is a developer-experience tool, not a deployment mechanism.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Forgetting to activate the venv | `pip install` lands in system Python | Always check `which python` shows the venv path |
| `pip install` outside the venv | Pollutes the system or fails on permissions | Activate first; never `sudo pip install` |
| Committing the `.venv` directory | Repo bloat, Windows / macOS path mismatches | Add `.venv/` to `.gitignore` |
| Pinning everything in `pyproject.toml` | Conflicts with downstream consumers | Use ranges (`>=`); pin in the lock file |
| Loose ranges with no lock file | Different installs get different versions | Add `uv lock` and commit `uv.lock` |
| `pip install -r` after editing `pyproject.toml` | Old deps still installed | `uv sync`, or `pip install -e .` to refresh |
| Mismatched Python version | Code works locally, breaks elsewhere | Pin `requires-python` and use `pyenv` / `uv python` |
| `.env` committed to git | Secrets leaked into history | `git rm --cached .env`, rotate the secrets, add to `.gitignore` |
| Mixing `black` and `ruff format` | Format thrash on save | Pick one; ruff format is the modern default |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Per-project dependency isolation | `venv` or `uv venv` | Standard, mandatory for any non-trivial project |
| Fast installs and resolves | `uv` | Rust-based, dramatically faster than pip |
| Declare package metadata + deps | `pyproject.toml` | Modern PEP 621 standard |
| Reproducible installs | `uv.lock` (or `poetry.lock`) | Pin transitive deps for everyone |
| Snapshot legacy environment | `pip freeze > requirements.txt` | Quick reproducibility, no lock format |
| Multiple Python versions on one machine | `pyenv` or `uv python install` | Switch per project |
| Lint + format Python | `ruff` | Replaces flake8 + black + isort, fast |
| Static type checking | `mypy` | Catches type mismatches before runtime |
| Run unit tests | `pytest` | Standard, rich plugin ecosystem |
| Local secrets / config | `.env` + `python-dotenv` | Out of git, easy to vary per environment |
| Production secrets | Real environment variables | Set by orchestrator / CI / cloud platform |

---

## See also

- [08_modules_and_packages.md](08_modules_and_packages.md) — `pyproject.toml`, project layout
- [07_exceptions.md](07_exceptions.md) — logging configuration
- [11_standard_library.md](11_standard_library.md) — `os.environ`, `sys`, `argparse`
