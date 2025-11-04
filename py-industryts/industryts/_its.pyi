"""Type stubs for the _its Rust extension module.

This file provides type information for the Rust-compiled extension module.
It should be kept in sync with the actual Rust implementation in py-industryts/src/lib.rs
"""

from __future__ import annotations

import polars as pl

class TimeSeriesData:
    """Rust-backed TimeSeriesData (internal).

    This is the low-level Rust implementation. Users should use the
    Python wrapper `industryts.TimeSeriesData` instead.
    """

    def __init__(self, data: pl.DataFrame, time_column: str | None = None) -> None:
        """Initialize TimeSeriesData from Polars DataFrame.

        Args:
            data: Polars DataFrame
            time_column: Name of time column (auto-detected if None)
        """
        ...

    def to_polars(self) -> pl.DataFrame:
        """Convert to Polars DataFrame.

        Returns:
            Polars DataFrame containing all data
        """
        ...

    @property
    def time_column(self) -> str:
        """Get the name of the time column.

        Returns:
            Name of the time column
        """
        ...

    @property
    def feature_columns(self) -> list[str]:
        """Get list of feature column names.

        Returns:
            List of feature column names (excludes time column)
        """
        ...

    def __len__(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows in the time series
        """
        ...

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation including shape and column info
        """
        ...

class Pipeline:
    """Rust-backed Pipeline (internal).

    This is the low-level Rust implementation. Users should use the
    Python wrapper `industryts.Pipeline` instead.
    """

    def __init__(self) -> None:
        """Initialize an empty pipeline."""
        ...

    @staticmethod
    def from_toml(path: str) -> Pipeline:
        """Load pipeline from TOML configuration file.

        Args:
            path: Path to TOML file

        Returns:
            Configured Pipeline instance
        """
        ...

    def process(self, data: TimeSeriesData) -> TimeSeriesData:
        """Execute pipeline on time series data.

        Args:
            data: Input TimeSeriesData

        Returns:
            Processed TimeSeriesData
        """
        ...

    def to_toml(self, path: str) -> None:
        """Save pipeline configuration to TOML file.

        Args:
            path: Output file path
        """
        ...

    def __len__(self) -> int:
        """Get the number of operations in the pipeline.

        Returns:
            Number of operations
        """
        ...

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation including operation count
        """
        ...
