"""Industryts: High-performance time series processing library.

A Rust-powered Python library for industrial time series data processing,
providing 10-100x performance improvements over pandas while maintaining
a familiar API.

Example:
    >>> import industryts as its
    >>> import polars as pl
    >>>
    >>> # Create time series data
    >>> df = pl.DataFrame({
    ...     "DateTime": pl.datetime_range("2024-01-01", "2024-01-10", interval="1d"),
    ...     "temperature": [20.1, 21.5, 19.8, 22.3, 21.0, 20.5, 21.2, 20.8, 21.5, 22.0],
    ... })
    >>> data = its.TimeSeriesData(df)
    >>>
    >>> # Load and apply pipeline
    >>> pipeline = its.Pipeline.from_toml("config.toml")
    >>> result = pipeline.process(data)
    >>>
    >>> # Export results
    >>> result.to_csv("output.csv")
"""

from __future__ import annotations

__version__ = "0.1.0"

# Import Rust binding module (compiled by PyO3)
from industryts import _its  # type: ignore  # noqa: F401

# Import Python wrappers
from industryts.pipeline import Pipeline
from industryts.timeseries import TimeSeriesData

__all__ = [
    "__version__",
    "TimeSeriesData",
    "Pipeline",
]
