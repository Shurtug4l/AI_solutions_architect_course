# Testing Strategy

## TL;DR

Testing for an ML system is testing on two layers at once: the **code** that runs the model (HTTP handlers, preprocessing, postprocessing, integrations) and the **model itself** as a stochastic object. The code layer uses the standard software testing pyramid — many fast **unit tests**, fewer **integration tests** that hit a real API or DB, a small set of **end-to-end** tests through the deployed service. The model layer adds tests that no software engineer trained on classical pyramids would think to write: **data validation** (schema, ranges, null rates), **invariance** tests (a small permutation of inputs that *should not* change the prediction), **directional** tests (a change that *should* move the prediction one way), **minimum performance** thresholds on a held-out set, and **degradation** tests against the previously deployed model.

**Pytest** is the de facto Python testing tool. Its core primitives are functions named `test_*`, **fixtures** for shared setup/teardown, **parametrize** for table-driven tests, **markers** for selecting subsets, and **plugins** for everything else (`pytest-cov`, `pytest-asyncio`, `pytest-mock`, `pytest-xdist` for parallel runs). The conventions worth enforcing from day one: tests live in a sibling `tests/` directory mirroring `src/`; one test file per module; `conftest.py` for shared fixtures; tests are independent and runnable in any order. Test discovery is automatic if names follow the convention; you do not register tests anywhere.

**Linting and formatting** keep the code in a state that is readable to anyone who picks it up. **Black** (formatter, opinionated, no config) handles style — quotes, line lengths, trailing commas — leaving zero room for bikeshedding. **Ruff** (linter + formatter, Rust-based, very fast) is replacing the older stack of `flake8` + `isort` + `pyupgrade` + `pylint` in 2024–2025; it covers ~700 rules across all of those tools and is fast enough to run on save. **mypy** (or **pyright**) is the type checker; with FastAPI/Pydantic codebases the type discipline is already there, so mypy in `--strict` mode catches real bugs at the cost of some boilerplate. The full quality gate is `ruff check --fix && ruff format && mypy && pytest` — usually wired into pre-commit hooks and the CI pipeline.

**API testing** uses FastAPI's `TestClient` (sync) or `httpx.AsyncClient` (async) against the app object — no live server needed. The pattern is to spin up the app with mocked external dependencies (model, DB, third-party APIs), send requests, and assert on the response. **ML-model testing** is more nuanced: a unit test on `model.predict(X)` checking equality is fragile (floating-point, library versions); instead, assert on **invariants** (output shape, range, monotonicity), **distributional properties** (mean prediction on a known dataset within a band), and **regression** (predictions on a frozen test set are within a tolerance of a baseline). The full picture is a **CI step that downloads a frozen evaluation set, runs the model, and fails the build if metrics drop below a threshold** — this is what gates a new model version from being promoted.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Unit test** | Tests one function in isolation | Fast (ms), no I/O |
| **Integration test** | Tests components together | DB, real HTTP, slower |
| **End-to-end test** | Tests the full deployed system | Slowest, fewest |
| **Test pyramid** | Many unit, fewer integration, fewest E2E | The right shape for the suite |
| **Pytest** | The Python testing framework | Default for any new project |
| **Fixture** | `@pytest.fixture` for shared setup | Parameter dependency injection |
| **`parametrize`** | Run a test with multiple input sets | The standard for table-driven tests |
| **Marker** | `@pytest.mark.slow` to tag tests | Run subsets with `-m` |
| **`conftest.py`** | Shared fixtures and config | Lives in `tests/` |
| **Coverage** | % of lines executed by tests | `pytest-cov`; a number, not a metric of quality |
| **Linter** | Static checker for code smells | Ruff |
| **Formatter** | Auto-fixes style | Black or Ruff format |
| **Type checker** | Verifies type hints | mypy / pyright |
| **Pre-commit** | Runs hooks before `git commit` | The hook framework |
| **FastAPI `TestClient`** | Sync client for testing FastAPI apps | The default for FastAPI tests |
| **Data validation test** | Schema/ranges/nulls on the dataset | Great Expectations, Pandera, custom asserts |
| **Invariance test** | Output should not change under irrelevant input change | "Capitalising a name should not change credit score" |
| **Directional test** | Output should move with a directional change | "Higher income should not decrease default risk" |
| **Regression test** (ML) | Predictions match the baseline within tolerance | Catch silent model changes in CI |

---

## The pyramid for ML systems

```
                       ┌─────────────────────┐
                       │       E2E           │   <— very few
                       │ (deployed system)   │
                       └─────────────────────┘
                  ┌─────────────────────────────┐
                  │     Integration             │   <— some
                  │ (API + model + dependencies)│
                  └─────────────────────────────┘
            ┌─────────────────────────────────────────┐
            │            Unit                          │   <— many
            │ (functions, validators, transformers)    │
            └─────────────────────────────────────────┘
            ┌─────────────────────────────────────────┐
            │       Data + Model validation            │   <— a layer ML adds
            │ (schemas, ranges, invariances, drift)    │
            └─────────────────────────────────────────┘
```

The bottom layer is what makes ML testing different. The pyramid alone gives you "the code does what we said"; the model layer gives you "the model behaves how we said".

---

## Pytest in 10 minutes

> The conventions are simple. The plugins are the leverage.

### Layout

```
src/
  myapp/
    __init__.py
    api.py
    model.py
    preprocessing.py
tests/
  __init__.py
  conftest.py
  test_api.py
  test_model.py
  test_preprocessing.py
pyproject.toml
```

### A first test

```python
# tests/test_preprocessing.py
import numpy as np
from myapp.preprocessing import standardise

def test_standardise_zero_mean_unit_std():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = standardise(x)
    assert abs(out.mean()) < 1e-9
    assert abs(out.std() - 1.0) < 1e-9
```

Discovery: pytest scans `tests/` for `test_*.py`, finds functions named `test_*`, runs them. No registration.

### Fixtures

```python
# tests/conftest.py
import pytest
import joblib

@pytest.fixture(scope="session")
def model():
    return joblib.load("tests/fixtures/model.pkl")

@pytest.fixture
def sample_features():
    return [0.1, 0.5, -0.3, 1.2, 0.0, -1.5, 0.8, 0.2, -0.7, 1.1]
```

Tests request fixtures by name:

```python
def test_predict_shape(model, sample_features):
    out = model.predict([sample_features])
    assert out.shape == (1,)
```

`scope="session"` means the fixture is created once per test session (good for expensive things like loading a model); the default is `function` (recreated for every test).

### Parametrize

```python
import pytest

@pytest.mark.parametrize("x, expected", [
    (0.0, "negative"),
    (0.5, "positive"),
    (0.9, "positive"),
])
def test_label_from_proba(x, expected):
    assert label_from_proba(x) == expected
```

One test, three cases, each shown separately in the output. The standard for input/output tables.

### Markers

```python
import pytest

@pytest.mark.slow
def test_full_pipeline_on_real_data():
    ...
```

```bash
pytest -m "not slow"   # skip slow tests in the fast loop
pytest -m slow         # run only slow ones in nightly CI
```

Register markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: tests that take more than a second",
    "integration: tests that hit the real DB",
]
```

### Async tests

```python
# pip install pytest-asyncio
import pytest
from httpx import AsyncClient
from myapp.api import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
```

### Mocking

```python
# pip install pytest-mock
def test_api_handles_model_error(mocker):
    mocker.patch("myapp.model.predict", side_effect=RuntimeError("oh no"))
    # ... call the endpoint, assert 500 ...
```

Or with the stdlib `unittest.mock.patch` as a decorator/context manager.

### Coverage

```bash
pytest --cov=myapp --cov-report=term-missing
```

Coverage is a *floor*, not a target. 80% coverage with assertions that prove nothing is worse than 60% coverage with tests that catch real bugs. Use coverage to find untested *modules*, not to optimise a number.

---

## Linting and formatting

> Style is not a matter of taste in a team; it is a matter of agreement and automation.

### Black

```bash
pip install black
black src tests
```

No configuration to argue about: line length 88 by default, double quotes, trailing commas. Run as a pre-commit hook; nobody reviews formatting in PRs.

### Ruff

```bash
pip install ruff
ruff check src tests           # lint
ruff check --fix src tests     # auto-fix what it can
ruff format src tests          # format (Black-compatible)
```

`pyproject.toml` config:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E", "F", "W",      # pycodestyle, pyflakes
    "I",                # isort
    "B",                # flake8-bugbear
    "UP",               # pyupgrade
    "SIM",              # flake8-simplify
    "RUF",              # ruff-specific
]
ignore = ["E501"]        # line length handled by formatter
```

Ruff is one tool that replaces `flake8` + `isort` + `pyupgrade` + `pydocstyle` + parts of `pylint`. Faster, simpler config, equivalent rules.

### mypy

```bash
pip install mypy
mypy src
```

```toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true   # for libraries without stubs
```

`--strict` enforces typed function signatures, no implicit `Any`, no untyped decorators. For a FastAPI + Pydantic codebase, the types are already there; the cost is low and the bug-catching is real.

### Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

Install once (`pre-commit install`); subsequent commits run the hooks automatically. The local fast loop matches what CI will check, so CI never fails on style alone.

---

## Testing FastAPI applications

### The `TestClient`

```python
from fastapi.testclient import TestClient
from myapp.api import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_predict_valid():
    r = client.post("/predict", json={"features": [0.1] * 10})
    assert r.status_code == 200
    body = r.json()
    assert "prediction" in body
    assert 0.0 <= body["prediction"] <= 1.0

def test_predict_invalid_length():
    r = client.post("/predict", json={"features": [0.1] * 5})
    assert r.status_code == 422   # Pydantic validation error
```

The `TestClient` runs FastAPI's ASGI app in-process — no network, no port, very fast.

### Overriding dependencies (mocking the model)

```python
from myapp.api import app, get_model

class FakeModel:
    def predict_proba(self, X):
        return [[0.1, 0.9] for _ in X]

def test_with_fake_model():
    app.dependency_overrides[get_model] = lambda: FakeModel()
    client = TestClient(app)
    r = client.post("/predict", json={"features": [0.0] * 10})
    assert r.status_code == 200
    assert r.json()["prediction"] == 0.9
    app.dependency_overrides.clear()
```

The `dependency_overrides` hook is FastAPI's purpose-built way to swap real dependencies with test doubles. It is cleaner than monkey-patching imports.

### Testing the full app with the real model

```python
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:   # triggers lifespan, loads model
        yield c

def test_predict_real_model(client):
    r = client.post("/predict", json={"features": [0.5] * 10})
    assert r.status_code == 200
```

The `with` block triggers FastAPI's lifespan, so the model gets loaded for the test session. Slow but high signal.

---

## ML-specific tests

### Data validation tests

Run *before training* and *before serving*. Confirms the dataset has the shape and properties you expect.

```python
import pandas as pd

def test_training_data_schema():
    df = pd.read_parquet("data/processed/train.parquet")
    expected_cols = {"feature_a", "feature_b", "feature_c", "label"}
    assert set(df.columns) == expected_cols
    assert df["label"].isin([0, 1]).all()
    assert df["feature_a"].notna().all()
    assert df["feature_b"].between(0, 100).all()
    assert len(df) > 1000   # sanity check on size
```

Frameworks like **Great Expectations** and **Pandera** wrap this into declarative schemas with better error messages, used in larger projects.

### Invariance tests

> Output must *not* change when an irrelevant feature changes.

```python
def test_name_capitalisation_does_not_change_score(model):
    base = {"name": "alice smith", **other_features}
    upper = {"name": "ALICE SMITH", **other_features}
    assert abs(model.predict([base])[0] - model.predict([upper])[0]) < 1e-6
```

These come from the model's invariance contracts (a credit model should not depend on name capitalisation; a sentiment model should not flip for "good" vs "Good").

### Directional tests

> Output must move in the right direction when a relevant feature changes.

```python
def test_higher_income_does_not_increase_default_risk(model):
    low = {"income": 20_000, **other_features}
    high = {"income": 200_000, **other_features}
    assert model.predict([high])[0] <= model.predict([low])[0]
```

Sanity tests that the model has not learned a wrong direction.

### Minimum performance tests

> The model meets a documented quality bar on a frozen holdout.

```python
from sklearn.metrics import roc_auc_score

def test_holdout_auc_meets_minimum(model):
    X_holdout, y_holdout = load_holdout()
    proba = model.predict_proba(X_holdout)[:, 1]
    auc = roc_auc_score(y_holdout, proba)
    assert auc >= 0.85, f"AUC {auc:.3f} below 0.85 threshold"
```

This is the test that gates a new model version from being promoted. Wire it into CI: the build fails if the metric drops below the floor.

### Regression tests on predictions

> Predictions on a frozen test set match a baseline within tolerance.

```python
def test_predictions_match_baseline(model):
    X = load_regression_inputs()
    baseline = load_baseline_predictions()
    new = model.predict_proba(X)[:, 1]
    diffs = abs(new - baseline)
    assert (diffs < 0.05).mean() > 0.99   # 99% of predictions within 0.05 of baseline
```

Catches silent model changes (library upgrade subtly changes predictions, retraining drifts the model).

### Slice tests

> Performance on important subgroups is acceptable.

```python
def test_auc_per_demographic_slice(model):
    X, y, slices = load_test_with_slices()
    proba = model.predict_proba(X)[:, 1]
    for slice_name, mask in slices.items():
        auc = roc_auc_score(y[mask], proba[mask])
        assert auc >= 0.75, f"AUC on slice {slice_name} too low: {auc:.3f}"
```

This is where fairness concerns enter the test suite: the model must not be terrible on minority slices.

---

## A complete quality gate

The script the CI runs on every push:

```bash
#!/usr/bin/env bash
set -euo pipefail

ruff check src tests
ruff format --check src tests
mypy src

pytest --cov=src --cov-report=xml -m "not slow"

# ML-specific
pytest tests/ml -m "data_validation"
pytest tests/ml -m "invariance"
pytest tests/ml -m "performance"
```

The pre-commit hooks run a subset locally so the fast loop is tight. The nightly CI job runs `-m slow` too: anything that hits a real cloud resource, downloads large datasets, or runs a full training cycle.

---

## Common patterns

| Pattern | When |
|---|---|
| **One test file per source file** | The default; easy navigation |
| **`conftest.py` per test directory** | Shared fixtures localised to a subdirectory |
| **Test data in `tests/fixtures/`** | Small frozen datasets, baseline predictions, sample requests |
| **`pytest-xdist` for parallel** | Test suite > a few minutes |
| **Markers for tiers** (`unit`, `integration`, `slow`, `requires_gpu`) | Run subsets in different CI jobs |
| **`hypothesis` for property tests** | When inputs are complex (e.g., random tabular features) |
| **Snapshot testing** for output shapes | Save the expected shape, fail on changes |
| **Contract tests between services** | When two services share a JSON schema |
| **Smoke test against deployed staging** | Post-deploy verification that the system answered at all |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Tests depend on each other / ordering | Flaky failures when run in different order | Make every test independent; use fixtures for setup |
| Real network/HTTP in unit tests | Slow, flaky, fails offline | Mock external HTTP; reserve real calls for integration tier |
| Floating-point equality on predictions | Fails on different machine | Use tolerances or distribution-based assertions |
| Coverage chased as a target | Tests that pass without proving anything | Test behaviour, not line coverage |
| Test discovery missing files | `test_x.py` named `tests_x.py` or wrong location | Stick to `test_*.py` and `tests/` directory |
| Fixtures loading the model in `function` scope | Slow suite | `scope="session"` for expensive fixtures |
| Loading real model from cloud in CI | Slow, requires creds | Cache the model artefact in CI or use a tiny test model |
| `TestClient` without `with` block | Lifespan not triggered, model not loaded | Use `with TestClient(app) as c:` |
| Pre-commit hooks not installed | "Why is CI failing on formatting again?" | `pre-commit install` once per clone |
| Lint config in multiple files | Drift between Black/Ruff/mypy | Centralise in `pyproject.toml` |
| Type-checking with `--strict` on a legacy codebase | Hundreds of errors | Start without `--strict`, ratchet up |
| Skipping ML-specific tests | "It passed all the tests but the model is wrong" | Add data validation + invariance + performance tests |
| Baseline predictions never refreshed | Regression test becomes meaningless | Re-baseline whenever the model is intentionally retrained |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Default test framework | **pytest** | Standard; better than `unittest` in every dimension |
| Format code | **Black** or **Ruff format** | Zero-config, consistent |
| Lint | **Ruff** | Replaces flake8, isort, pyupgrade, parts of pylint; fast |
| Type-check | **mypy** (or **pyright**) | Real bugs at low cost in a typed codebase |
| FastAPI tests | **`TestClient`** + **`dependency_overrides`** | Built-in, fast, idiomatic |
| Async tests | **`pytest-asyncio`** + `httpx.AsyncClient` | The standard combo |
| Data validation | **Pandera** or **Great Expectations** | Declarative schemas with good errors |
| Property tests | **Hypothesis** | When inputs are large/random |
| Coverage | **`pytest-cov`** | Built-in, integrates with most CI |
| Pre-commit | **`pre-commit`** | Local hooks matching CI |
| Parallel tests | **`pytest-xdist`** | Cut suite time on multi-core |
| Mutation testing | **`mutmut`** | For libraries where coverage isn't enough |

---

## See also

### Other notes
- [02_environments_and_version_control.md](02_environments_and_version_control.md) — pinning the test environment so tests are reproducible
- [04_model_serving_with_fastapi.md](04_model_serving_with_fastapi.md) — the serving code being tested
- [08_ci_cd_pipelines.md](08_ci_cd_pipelines.md) — where the quality gate runs on every push

### Cross-module
- Module 01 [09_model_selection.md](../../01_machine_learning/notes/09_model_selection.md) — the evaluation metrics the performance test gates on
- Module 02 [06_rag_evaluation.md](../../02_large_language_models/notes/06_rag_evaluation.md) — RAG-specific evaluation that translates into automated tests
- Module 04 [02_kpis_lifecycle_drift.md](../../04_business_case_AIPM/notes/02_kpis_lifecycle_drift.md) — the business metrics that the performance tests reflect
