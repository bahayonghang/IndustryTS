"""Pytest configuration and fixtures for industryts tests."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import polars as pl
import pytest


@pytest.fixture
def sample_datetime_range() -> pl.Series:
    """Create a sample datetime range for testing."""
    return pl.datetime_range(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 10),
        interval="1d",
        eager=True,
    )


@pytest.fixture
def sample_dataframe(sample_datetime_range: pl.Series) -> pl.DataFrame:
    """Create a sample DataFrame with time series data."""
    return pl.DataFrame({
        "DateTime": sample_datetime_range,
        "temperature": [20.1, 21.5, 19.8, 22.3, 21.0, 20.5, 21.2, 20.8, 21.5, 22.0],
        "pressure": [1013, 1015, 1012, 1018, 1016, 1014, 1017, 1015, 1016, 1019],
    })


@pytest.fixture
def sample_dataframe_with_nulls(sample_datetime_range: pl.Series) -> pl.DataFrame:
    """Create a sample DataFrame with null values."""
    return pl.DataFrame({
        "DateTime": sample_datetime_range,
        "temperature": [20.1, None, 19.8, 22.3, None, 20.5, 21.2, 20.8, None, 22.0],
        "pressure": [1013, 1015, None, 1018, 1016, None, 1017, 1015, 1016, 1019],
    })


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for file I/O tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def basic_pipeline_config() -> str:
    """TOML configuration for a basic pipeline."""
    return """
[pipeline]
name = "test_pipeline"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "standardize"
"""


@pytest.fixture
def feature_engineering_config() -> str:
    """TOML configuration for feature engineering pipeline."""
    return """
[pipeline]
name = "feature_engineering"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "lag"
periods = [1, 2, 3]
columns = ["temperature", "pressure"]

[[operations]]
type = "standardize"
"""

