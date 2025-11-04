# Industryts Test Suite

This directory contains comprehensive tests for the industryts library.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_timeseries.py  # TimeSeriesData class tests
│   └── test_pipeline.py    # Pipeline class tests
└── integration/             # End-to-end integration tests
    └── test_end_to_end.py  # Complete workflow tests
```

## Running Tests

### All Tests
```bash
# From project root
uv run pytest py-industryts/tests/

# With verbose output
uv run pytest py-industryts/tests/ -v

# Quick summary
uv run pytest py-industryts/tests/ -q
```

### Specific Test Categories
```bash
# Unit tests only
uv run pytest py-industryts/tests/unit/

# Integration tests only
uv run pytest py-industryts/tests/integration/

# Specific test file
uv run pytest py-industryts/tests/unit/test_timeseries.py

# Specific test class or method
uv run pytest py-industryts/tests/unit/test_timeseries.py::TestTimeSeriesDataCreation
uv run pytest py-industryts/tests/unit/test_timeseries.py::TestTimeSeriesDataCreation::test_create_from_dataframe
```

### With Coverage
```bash
# Install coverage tool
uv pip install pytest-cov

# Run with coverage report
uv run pytest py-industryts/tests/ --cov=industryts --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Coverage

### Unit Tests (35 tests)

**TimeSeriesData Tests** (`test_timeseries.py`):
- Creation and initialization (6 tests)
- Properties and methods (4 tests)
- Data conversion (2 tests)
- I/O operations (5 tests)
- Helper methods (5 tests)
- Edge cases (3 tests)

**Pipeline Tests** (`test_pipeline.py`):
- Creation and loading (5 tests)
- Properties (3 tests)
- Data processing (4 tests)
- Configuration I/O (2 tests)
- Operations (5 tests)
- Edge cases (2 tests)

### Integration Tests (11 tests)

**End-to-End Workflows** (`test_end_to_end.py`):
- Complete data pipelines (5 tests)
- Real-world scenarios (3 tests)
- Error handling (3 tests)

## Test Fixtures

Defined in `conftest.py`:

- `sample_datetime_range` - 10-day datetime series
- `sample_dataframe` - Sample time series DataFrame
- `sample_dataframe_with_nulls` - DataFrame with null values
- `temp_dir` - Temporary directory for file I/O tests
- `basic_pipeline_config` - Basic TOML pipeline configuration
- `feature_engineering_config` - Feature engineering pipeline configuration

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*` (PascalCase)
- Test methods: `test_*` (snake_case)

### Example Test

```python
from __future__ import annotations

import polars as pl
import pytest

import industryts as its


class TestMyFeature:
    """Tests for my new feature."""

    def test_basic_functionality(self, sample_dataframe: pl.DataFrame) -> None:
        """Test basic feature behavior."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        
        # Perform test
        result = ts_data.my_method()
        
        # Assertions
        assert result is not None
        assert len(result) > 0

    def test_edge_case(self) -> None:
        """Test edge case handling."""
        with pytest.raises(ValueError):
            its.TimeSeriesData(None)  # Should raise error
```

### Best Practices

1. **Use fixtures** - Leverage existing fixtures from `conftest.py`
2. **Test edge cases** - Empty data, single row, null values, etc.
3. **Clear assertions** - Make expected behavior explicit
4. **Descriptive names** - Test name should describe what's being tested
5. **One concept per test** - Keep tests focused and simple
6. **Use type hints** - Include type hints for all test parameters and returns

## CI/CD Integration

Tests are automatically run on:
- Every commit (via pre-commit hooks)
- Pull requests
- Main branch updates

Required: All tests must pass before merging.

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Rebuild the package
uv run maturin develop
```

**Datetime parsing errors:**
- CSV files: Use `try_parse_dates=True` in `from_csv()`
- Manual creation: Use `datetime` objects, not strings

**Standardization errors on small datasets:**
- Standardization requires at least 2 rows
- Use simpler operations for single-row tests

### Getting Help

- Check test output for error messages
- Run with `-vv` for more verbose output
- Use `--tb=short` for shorter tracebacks
- Add `pytest.set_trace()` for debugging

## Performance Testing

For performance benchmarks:

```bash
# Install benchmark plugin
uv pip install pytest-benchmark

# Run benchmarks (when added)
uv run pytest py-industryts/tests/ --benchmark-only
```

## Future Enhancements

- [ ] Property-based testing with Hypothesis
- [ ] Performance benchmarks vs pandas
- [ ] Memory usage tests
- [ ] Concurrent processing tests
- [ ] Extended error handling tests
- [ ] Documentation tests (doctest)

