# py-industryts - Python Bindings and API

[Root Directory](../CLAUDE.md) > **py-industryts**

**Last Updated:** 2025-11-04 14:47:17 CST

---

## Change Log

### 2025-11-04 14:47:17 CST
- Initial module documentation created
- Documented PyO3 bindings layer (src/lib.rs)
- Documented Python API layer (industryts/*.py)
- Identified API surface: TimeSeriesData, Pipeline with full type hints
- Noted test infrastructure needs to be created

---

## Module Responsibilities

`py-industryts` provides the Python interface to the Rust-powered industryts library. It consists of two sub-layers:

1. **PyO3 Bindings (src/):** Rust code using PyO3 to expose Rust types to Python
2. **Python API (industryts/):** Pure Python wrapper providing ergonomic API, type hints, and I/O helpers

**Core Responsibilities:**
- Bridge Rust `industryts-core` types to Python via PyO3
- Provide zero-copy DataFrame sharing via `pyo3-polars`
- Expose high-level Python API with full type hints
- Handle I/O operations (CSV, Parquet) using Polars Python
- Provide comprehensive docstrings and examples
- Package as Python wheel via Maturin

**Not Responsible For:**
- Time series processing logic (handled by `industryts-core`)
- Pipeline orchestration (handled by `industryts-core`)
- TOML parsing (handled by `industryts-core`)

---

## Entry and Startup

### Module Structure

```
py-industryts/
├── src/                    # Rust PyO3 bindings
│   └── lib.rs             # Defines _its module (compiled extension)
├── industryts/            # Python package (source distribution)
│   ├── __init__.py        # Public API exports
│   ├── timeseries.py      # TimeSeriesData class
│   └── pipeline.py        # Pipeline class
├── Cargo.toml             # Rust crate config (cdylib)
└── (future) tests/        # Python tests
```

### Import Hierarchy

**User imports:**
```python
import industryts as its

# Available classes
its.TimeSeriesData
its.Pipeline
```

**Internal flow:**
```
industryts/__init__.py
  ↓ imports
industryts._its (compiled Rust module)
  ↓ wraps
industryts_core (Rust library)
```

### Build Process

**Maturin workflow:**
1. `maturin develop` - Compile Rust code to `_its.so` (Linux) or `_its.pyd` (Windows)
2. Install Python package pointing to compiled module
3. Python code imports `_its` and wraps Rust types

**Configuration:** See root `pyproject.toml`:
```toml
[tool.maturin]
manifest-path = "py-industryts/Cargo.toml"
python-source = "py-industryts"
module-name = "industryts._its"
```

---

## External Interfaces

### Python Public API

#### TimeSeriesData Class

**File:** `industryts/timeseries.py`

**Constructor:**
```python
def __init__(
    self,
    data: pl.DataFrame,
    time_column: Optional[str] = None,
) -> None
```

**Properties:**
- `time_column: str` - Name of time index column
- `feature_columns: list[str]` - List of feature column names

**Methods:**
- `to_polars() -> pl.DataFrame` - Export to Polars DataFrame
- `from_csv(path, time_column=None, **kwargs) -> TimeSeriesData` - Load from CSV
- `from_parquet(path, time_column=None, **kwargs) -> TimeSeriesData` - Load from Parquet
- `to_csv(path, **kwargs) -> None` - Save to CSV
- `to_parquet(path, **kwargs) -> None` - Save to Parquet
- `head(n=5) -> pl.DataFrame` - Get first n rows
- `tail(n=5) -> pl.DataFrame` - Get last n rows
- `describe() -> pl.DataFrame` - Descriptive statistics
- `__len__() -> int` - Number of rows
- `__repr__() -> str` - String representation

**Usage Example:**
```python
import industryts as its
import polars as pl

# Create from DataFrame
df = pl.DataFrame({
    "DateTime": pl.datetime_range("2024-01-01", "2024-01-10", interval="1d"),
    "temperature": [20.1, 21.5, 19.8, 22.3, 21.0, 20.5, 21.2, 20.8, 21.5, 22.0],
})
ts_data = its.TimeSeriesData(df)

# Load from file
ts_data = its.TimeSeriesData.from_csv("sensor_data.csv")

# Export
ts_data.to_parquet("output.parquet")
```

#### Pipeline Class

**File:** `industryts/pipeline.py`

**Constructor:**
```python
def __init__(self) -> None  # Creates empty pipeline
```

**Class Methods:**
```python
@classmethod
def from_toml(cls, path: str | Path) -> Pipeline
```

**Methods:**
- `process(data: TimeSeriesData) -> TimeSeriesData` - Execute pipeline
- `to_toml(path: str | Path) -> None` - Save configuration
- `__len__() -> int` - Number of operations
- `__repr__() -> str` - String representation

**TOML Configuration:**
```toml
[pipeline]
name = "my_pipeline"
time_column = "DateTime"

[[operations]]
type = "fill_null"
method = "forward"
columns = ["temperature", "pressure"]  # optional

[[operations]]
type = "lag"
periods = [1, 2, 3]
columns = ["temperature"]

[[operations]]
type = "standardize"
```

**Supported Operations:**
- `fill_null`: methods = `forward`, `backward`, `mean`, `zero`
- `lag`: Create lagged features
- `standardize`: Z-score normalization
- `resample`: Time-based resampling (TODO: Polars 0.51 update)

**Usage Example:**
```python
# Load and execute
pipeline = its.Pipeline.from_toml("config.toml")
result = pipeline.process(ts_data)

# Save results
result.to_csv("output.csv")
```

---

## Key Dependencies and Configuration

### Cargo.toml (Rust Bindings)

**File:** `py-industryts/Cargo.toml`

```toml
[package]
name = "industryts"
version = "0.1.0"
edition = "2021"

[lib]
name = "industryts"
crate-type = ["cdylib"]  # Compile as C dynamic library for Python

[dependencies]
industryts-core = { path = "../crates/industryts-core" }
pyo3 = { version = "0.25", features = ["extension-module", "abi3-py38"] }
polars = "0.51"
pyo3-polars = "0.24"

[build-dependencies]
pyo3-build-config = "0.25"
```

**Key Points:**
- `crate-type = ["cdylib"]` - Produces shared library for Python to import
- `abi3-py38` - Stable ABI for Python 3.8+ compatibility (single wheel for all Python versions)
- `pyo3-polars` - Zero-copy DataFrame conversion between Python and Rust

### pyproject.toml (Python Package)

**Relevant sections:**

```toml
[project]
name = "industryts"
requires-python = ">=3.9"
dependencies = [
    "polars[rtcompat]>=1.35.0",
    "pyarrow>=14.0.0",
]

[tool.maturin]
manifest-path = "py-industryts/Cargo.toml"
features = ["pyo3/extension-module", "pyo3/abi3-py09"]
compatibility = "manylinux2014"
python-source = "py-industryts"
module-name = "industryts._its"
```

**Type Checking:**
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
disallow_untyped_defs = true
files = ["py-industryts/industryts"]

[tool.pyright]
include = ["py-industryts/industryts"]
pythonVersion = "3.9"
typeCheckingMode = "basic"
```

---

## Data Models

### PyO3 Wrapper Types

**File:** `src/lib.rs`

#### PyTimeSeriesData

```rust
#[pyclass(name = "TimeSeriesData")]
pub struct PyTimeSeriesData {
    inner: CoreTimeSeriesData,  // Wraps Rust core type
}
```

**Exposed to Python:**
- `__new__(data: PyDataFrame, time_column: Option<&str>)` - Constructor
- `to_polars() -> PyDataFrame` - Export DataFrame (zero-copy via pyo3-polars)
- `time_column` (property) - Get time column name
- `feature_columns` (property) - Get feature columns
- `__len__()`, `__repr__()` - Python protocols

**Key Pattern:**
```rust
// Python receives Polars DataFrame
let df: polars::DataFrame = data.into();  // PyDataFrame -> DataFrame

// Rust processes
let ts = CoreTimeSeriesData::new(df, time_column)?;

// Python gets back Polars DataFrame
PyDataFrame(df)  // DataFrame -> PyDataFrame (zero-copy!)
```

#### PyPipeline

```rust
#[pyclass(name = "Pipeline")]
pub struct PyPipeline {
    inner: CorePipeline,  // Wraps Rust core type
}
```

**Exposed to Python:**
- `__new__()` - Create empty pipeline
- `from_toml(path: &str)` - Load from config file
- `process(data: &PyTimeSeriesData) -> PyTimeSeriesData` - Execute
- `to_toml(path: &str)` - Save config
- `__len__()`, `__repr__()` - Python protocols

### Python Wrapper Types

**Files:** `industryts/timeseries.py`, `industryts/pipeline.py`

These provide:
- Type hints for all methods
- I/O helpers (from_csv, from_parquet, to_csv, to_parquet)
- Convenience methods (head, tail, describe)
- Comprehensive docstrings with examples

**Pattern:**
```python
class TimeSeriesData:
    def __init__(self, data: pl.DataFrame, time_column: Optional[str] = None):
        self._inner = _its.TimeSeriesData(data, time_column)

    @property
    def time_column(self) -> str:
        return self._inner.time_column
```

---

## Testing and Quality

### Current Test Status

**Tests Found:** None

**Test Infrastructure Needed:**
```
py-industryts/
  tests/
    test_timeseries.py      # TimeSeriesData tests
    test_pipeline.py        # Pipeline tests
    test_operations.py      # Operation-specific tests
    test_io.py              # I/O operations tests
    test_integration.py     # End-to-end workflows
    conftest.py             # pytest fixtures
```

### Recommended Test Structure

**Unit Tests:**
```python
# test_timeseries.py
import pytest
import polars as pl
import industryts as its

def test_timeseries_creation():
    df = pl.DataFrame({"DateTime": [...], "value": [...]})
    ts = its.TimeSeriesData(df)
    assert ts.time_column == "DateTime"
    assert "value" in ts.feature_columns

def test_time_column_auto_detection():
    df = pl.DataFrame({"tagTime": [...], "sensor1": [...]})
    ts = its.TimeSeriesData(df)
    assert ts.time_column == "tagTime"

def test_csv_io(tmp_path):
    # Create, save, load, compare
    ...
```

**Integration Tests:**
```python
# test_integration.py
def test_full_pipeline():
    # Load data
    ts = its.TimeSeriesData.from_csv("test_data.csv")

    # Load pipeline
    pipeline = its.Pipeline.from_toml("test_pipeline.toml")

    # Process
    result = pipeline.process(ts)

    # Validate
    assert len(result) > 0
    assert "temperature_lag_1" in result.to_polars().columns
```

**Property-Based Tests (Hypothesis):**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(), min_size=10))
def test_fill_null_preserves_length(values):
    # Property: fill_null doesn't change row count
    ...
```

### Type Checking

**Run type checkers:**
```bash
# mypy
uv run mypy py-industryts/industryts

# pyright
uv run pyright py-industryts/industryts
```

**Common type issues:**
- Missing `from __future__ import annotations`
- Incorrect `Optional[T]` vs `T | None` (use `Optional` for Python 3.9 compat)
- Missing return type annotations
- Untyped kwargs (use `**kwargs: Any`)

### Linting and Formatting

**Ruff configuration (pyproject.toml):**
```toml
[tool.ruff]
target-version = "py39"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

**Run linting:**
```bash
# Check
uv run ruff check py-industryts/industryts

# Fix
uv run ruff check --fix py-industryts/industryts

# Format
uv run ruff format py-industryts/industryts
```

---

## Frequently Asked Questions

### Q: Why separate Python API layer from PyO3 bindings?

A: The PyO3 layer (`src/lib.rs`) provides minimal wrappers, while the Python layer (`industryts/*.py`) adds type hints, I/O helpers, and documentation. This separation allows:
- Type hints (PyO3 doesn't generate stubs automatically)
- Convenient I/O methods without Rust code
- Future pure-Python extensions
- Better IDE autocomplete

### Q: How does zero-copy DataFrame transfer work?

A: `pyo3-polars` uses Apache Arrow's memory format. When Python passes a Polars DataFrame to Rust (or vice versa), only pointers are transferred, not data. This is critical for performance with large datasets.

### Q: Can I use pandas DataFrames?

A: Not directly. Convert pandas to Polars first:
```python
import pandas as pd
import polars as pl

pandas_df = pd.read_csv("data.csv")
polars_df = pl.from_pandas(pandas_df)
ts = its.TimeSeriesData(polars_df)
```

### Q: How do I add a new Python method?

1. Add method to `industryts/timeseries.py` or `industryts/pipeline.py`
2. Add type hints for all parameters and return type
3. Write comprehensive docstring with Google style
4. Add tests in `tests/`
5. Run `make typecheck` to verify
6. Update this CLAUDE.md

### Q: Why abi3-py38 in Cargo but requires-python = ">=3.9" in pyproject.toml?

A: `abi3-py38` is the Rust side (stable ABI from Python 3.8+), but we target Python 3.9+ for the API (for features like `from __future__ import annotations`, `dict | None` syntax). One wheel works for 3.9, 3.10, 3.11, 3.12, 3.13.

### Q: How do I debug Rust errors in Python?

A: PyO3 converts Rust errors to Python exceptions. For debugging:
1. Check exception message (includes Rust error)
2. Build with debug symbols: `maturin develop` (not `--release`)
3. Use `RUST_BACKTRACE=1` environment variable
4. Add debug prints in Rust code

---

## Related File List

### Rust Bindings (src/)
- `lib.rs` - PyO3 module definition, `PyTimeSeriesData`, `PyPipeline` wrappers

### Python API (industryts/)
- `__init__.py` - Public API exports, version, docstring
- `timeseries.py` - `TimeSeriesData` class with I/O and convenience methods
- `pipeline.py` - `Pipeline` class with TOML loading
- `py.typed` - Marker file for PEP 561 type checking

### Configuration
- `Cargo.toml` - Rust crate configuration (cdylib, dependencies)

### Future Additions (Recommended)
- `tests/test_timeseries.py` - TimeSeriesData tests
- `tests/test_pipeline.py` - Pipeline tests
- `tests/test_io.py` - I/O operations tests
- `tests/conftest.py` - pytest fixtures
- `industryts/__init__.pyi` - Type stub file (optional, for better IDE support)

---

## Module-Specific Conventions

### Python Naming Conventions
- **Classes:** `PascalCase` (e.g., `TimeSeriesData`, `Pipeline`)
- **Functions/Methods:** `snake_case` (e.g., `to_polars`, `from_csv`)
- **Private attributes:** `_leading_underscore` (e.g., `self._inner`)
- **Type variables:** `PascalCase` with `T` prefix (e.g., `TDataFrame`)

### Type Hint Standards
```python
from __future__ import annotations  # Always first import

from typing import Optional, Any
from pathlib import Path
import polars as pl

# Good
def method(self, data: pl.DataFrame, col: Optional[str] = None) -> pl.DataFrame:
    ...

# Also good (Python 3.10+, but use Optional for 3.9 compat)
def method(self, data: pl.DataFrame, col: str | None = None) -> pl.DataFrame:
    ...
```

### Docstring Standards

**Google style (required for all public APIs):**
```python
def from_csv(
    cls,
    path: str | Path,
    time_column: Optional[str] = None,
    **kwargs: Any,
) -> TimeSeriesData:
    """Load time series data from CSV file.

    This method reads a CSV file using Polars and creates a TimeSeriesData
    instance. The time column can be auto-detected or specified explicitly.

    Args:
        path: Path to CSV file
        time_column: Name of the time column (auto-detected if None)
        **kwargs: Additional arguments passed to polars.read_csv()

    Returns:
        TimeSeriesData instance containing the loaded data

    Raises:
        IOError: If file cannot be read
        ValueError: If time column cannot be determined

    Example:
        >>> ts_data = TimeSeriesData.from_csv("sensor_data.csv")
        >>> ts_data = TimeSeriesData.from_csv(
        ...     "data.csv",
        ...     time_column="timestamp",
        ...     parse_dates=True
        ... )
    """
```

### Error Handling Patterns

**Python wrapping Rust errors:**
```python
def process(self, data: TimeSeriesData) -> TimeSeriesData:
    try:
        result_inner = self._inner.process(data._inner)
    except RuntimeError as e:
        # Rust errors come as RuntimeError
        raise RuntimeError(f"Pipeline processing failed: {e}") from e

    # Wrap result
    result = TimeSeriesData.__new__(TimeSeriesData)
    result._inner = result_inner
    return result
```

**Custom Python validation:**
```python
def __init__(self, data: pl.DataFrame, time_column: Optional[str] = None):
    if not isinstance(data, pl.DataFrame):
        raise TypeError(f"Expected pl.DataFrame, got {type(data)}")

    self._inner = _its.TimeSeriesData(data, time_column)
```

---

## Implementation Notes

### PyO3 Patterns Used

**Class wrapping:**
```rust
#[pyclass(name = "TimeSeriesData")]  // Name in Python
pub struct PyTimeSeriesData {
    inner: CoreTimeSeriesData,  // Wrap Rust type
}
```

**Property getters:**
```rust
#[pymethods]
impl PyTimeSeriesData {
    #[getter]
    pub fn time_column(&self) -> String {
        self.inner.time_column().to_string()
    }
}
```

**Static methods:**
```rust
#[staticmethod]
pub fn from_toml(path: &str) -> PyResult<Self> {
    ...
}
```

**Error conversion:**
```rust
.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?
```

### pyo3-polars Integration

**Key type:** `PyDataFrame` - wrapper for zero-copy Polars DataFrame

**Python to Rust:**
```rust
pub fn new(data: PyDataFrame, time_column: Option<&str>) -> PyResult<Self> {
    let df: polars::DataFrame = data.into();  // Zero-copy conversion
    ...
}
```

**Rust to Python:**
```rust
pub fn to_polars(&self) -> PyDataFrame {
    let df = self.inner.dataframe().clone();
    PyDataFrame(df)  // Zero-copy conversion
}
```

### Future Enhancements

**Planned Features:**
- Programmatic pipeline building (builder pattern in Python)
- Custom operation registration from Python
- Progress callbacks for long-running operations
- Streaming/chunked data processing
- Integration with other libraries (scikit-learn, dask)

**API Improvements:**
- Type stubs (`.pyi` files) for better IDE support
- Async I/O operations
- Context managers for resource cleanup
- Better error messages with suggestions

---

## Build and Distribution

### Development Build
```bash
# Fast build with debug symbols
maturin develop

# Or via Make
make develop
```

### Release Build
```bash
# Optimized build
maturin build --release

# Output: target/wheels/industryts-0.1.0-*.whl
```

### Multi-platform Wheels

**manylinux (Linux):**
```bash
docker run --rm -v $(PWD):/io \
    quay.io/pypa/manylinux2014_x86_64 \
    sh -c "cd /io && maturin build --release --manylinux 2014"
```

**macOS and Windows:**
- Use GitHub Actions or local builds
- Separate wheels for x86_64 and arm64 (macOS)

### Publishing to PyPI
```bash
# Test PyPI first
maturin publish --repository testpypi

# Production PyPI
maturin publish
```

---

## Next Steps for Development

1. **Create Test Suite** - Add comprehensive tests in `tests/` directory
2. **Type Stubs** - Generate `.pyi` files for better IDE autocomplete
3. **Documentation** - Build Sphinx docs with API reference
4. **Examples** - Add more usage examples in `examples/`
5. **CI/CD** - Set up GitHub Actions for testing and wheel building
6. **Benchmarks** - Add Python benchmarks comparing to pandas
