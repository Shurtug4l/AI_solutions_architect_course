# Virtual Environments and Tooling

## Why Virtual Environments

Each Python project may need different versions of the same dependency. Installing everything globally causes version conflicts. Virtual environments isolate per-project dependencies.

---

## venv (Standard Library)

```bash
# Create environment
python -m venv .venv

# Activate
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Deactivate
deactivate

# Verify: now 'python' and 'pip' point to the venv
which python    # /path/to/project/.venv/bin/python
```

Once activated, `pip install` installs into the venv, not the system Python.

Convention: name the directory `.venv` (hidden, local) and add it to `.gitignore`.

---

## pip

```bash
pip install requests                    # install latest
pip install requests==2.31.0           # pin exact version
pip install "requests>=2.28,<3.0"      # version range
pip install -e .                        # install current project in editable mode
pip install -r requirements.txt         # install from file

pip uninstall requests
pip list                                # installed packages
pip show requests                       # metadata for a package
pip freeze                              # installed packages with exact versions
pip freeze > requirements.txt           # snapshot current environment

pip install --upgrade requests          # upgrade to latest
```

### requirements.txt

Flat list of pinned dependencies for reproducible installs:

```
requests==2.31.0
numpy==1.26.2
pandas==2.1.4
```

`pip freeze` captures the entire environment including transitive dependencies. For hand-written files, you can pin only direct dependencies.

---

## pyproject.toml

The modern standard (PEP 517/518/621) for defining Python project metadata and build configuration. Replaces `setup.py` and `setup.cfg`.

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
mycli = "mypackage.cli:main"    # creates a CLI command on install
```

Install with dev extras:

```bash
pip install -e ".[dev]"
```

---

## uv — Fast Python Package Manager

`uv` (from Astral) is a Rust-based drop-in replacement for pip + venv. Significantly faster for dependency resolution and installation.

```bash
# Install uv
pip install uv   # or: curl -Ls https://astral.sh/uv/install.sh | sh

# Create and manage venv
uv venv                           # creates .venv
source .venv/bin/activate

# Install packages
uv pip install requests
uv pip install -r requirements.txt
uv pip install -e ".[dev]"

# Sync from pyproject.toml
uv sync
uv sync --extra dev

# Lock dependencies (like poetry.lock)
uv lock
```

`uv` is compatible with `requirements.txt` and `pyproject.toml`. Use it as a drop-in for `pip` in automated environments where speed matters.

---

## Dependency Management: Comparison

| Tool | File | Purpose |
|------|------|---------|
| `pip` + `venv` | `requirements.txt` | Simple, standard, no lock file |
| `pip` + `pyproject.toml` | `pyproject.toml` | Modern metadata, no lock |
| `uv` | `pyproject.toml` + `uv.lock` | Fast, lock file, modern |
| `poetry` | `pyproject.toml` + `poetry.lock` | Mature, lock file, publishing |
| `pipenv` | `Pipfile` + `Pipfile.lock` | Older alternative, less popular now |

For new projects: `uv` with `pyproject.toml` is the current best practice. For simple scripts: `venv` + `pip` is sufficient.

---

## Python Version Management

Multiple Python versions on the same machine:

```bash
# pyenv (macOS/Linux)
pyenv install 3.12.0
pyenv global 3.12.0        # set global default
pyenv local 3.11.6         # set for current directory (writes .python-version)
pyenv versions             # list installed versions

# uv also manages Python versions
uv python install 3.12
uv python list
```

---

## Code Quality Tools

| Tool | Purpose | Config |
|------|---------|--------|
| `ruff` | Linter + formatter (fast, replaces flake8/black/isort) | `pyproject.toml` `[tool.ruff]` |
| `black` | Code formatter | `pyproject.toml` `[tool.black]` |
| `mypy` | Static type checker | `mypy.ini` or `pyproject.toml` |
| `pytest` | Test runner | `pyproject.toml` `[tool.pytest.ini_options]` |

```bash
ruff check .              # lint
ruff check --fix .        # auto-fix
ruff format .             # format

mypy src/                 # type check

pytest                    # run all tests
pytest tests/test_core.py -v
pytest -k "test_login"    # run tests matching pattern
```

Minimal `pyproject.toml` ruff config:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]   # pycodestyle, pyflakes, isort, pyupgrade
```

---

## .gitignore Essentials

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

Never commit the virtual environment directory or `.env` files containing secrets.

---

## Environment Variables and .env Files

```python
import os
api_key = os.environ.get("API_KEY")   # returns None if not set
api_key = os.environ["API_KEY"]        # raises KeyError if not set

# Load from .env file (python-dotenv)
from dotenv import load_dotenv
load_dotenv()                          # reads .env into os.environ
api_key = os.environ.get("API_KEY")
```

`.env` file format:

```
API_KEY=abc123
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
```

Never commit `.env` to version control. Document required variables in `.env.example` (without values).
