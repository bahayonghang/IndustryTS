"""Time series data wrapper with Polars integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import polars as pl

from industryts import _its


class TimeSeriesData:
    """High-performance time series data container.

    This class wraps a Polars DataFrame with time series-specific functionality,
    powered by Rust for 10-100x performance improvements.

    Attributes:
        time_column: Name of the time index column
        feature_columns: List of feature column names

    Example:
        >>> import industryts as its
        >>> import polars as pl
        >>>
        >>> # Create from Polars DataFrame
        >>> df = pl.DataFrame({
        ...     "DateTime": pl.datetime_range(start="2024-01-01", end="2024-01-10", interval="1d"),
        ...     "temperature": [20.1, 21.5, 19.8, 22.3, 21.0, 20.5, 21.2, 20.8, 21.5, 22.0],
        ...     "pressure": [1013, 1015, 1012, 1018, 1016, 1014, 1017, 1015, 1016, 1019]
        ... })
        >>> ts_data = its.TimeSeriesData(df)
        >>> print(ts_data.time_column)
        'DateTime'
        >>> print(ts_data.feature_columns)
        ['temperature', 'pressure']
    """

    def __init__(
        self,
        data: pl.DataFrame,
        time_column: Optional[str] = None,
    ) -> None:
        """Create a new TimeSeriesData instance.

        Args:
            data: Polars DataFrame containing time series data
            time_column: Name of the time column. If None, will auto-detect from
                common names like 'DateTime', 'tagTime', 'timestamp', etc.
                If no match found, uses first column.

        Raises:
            ValueError: If data is empty or time column cannot be determined

        Example:
            >>> df = pl.DataFrame({"time": [...], "value": [...]})
            >>> ts = TimeSeriesData(df, time_column="time")
        """
        self._inner = _its.TimeSeriesData(data, time_column)

    @property
    def time_column(self) -> str:
        """Get the name of the time index column.

        Returns:
            Name of the time column
        """
        return self._inner.time_column

    @property
    def feature_columns(self) -> list[str]:
        """Get the names of all feature columns.

        Returns:
            List of feature column names (excludes time column)
        """
        return self._inner.feature_columns

    def to_polars(self) -> pl.DataFrame:
        """Convert to Polars DataFrame.

        Returns:
            Polars DataFrame containing all data

        Example:
            >>> df = ts_data.to_polars()
            >>> print(df.shape)
            (100, 3)
        """
        return self._inner.to_polars()

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        time_column: Optional[str] = None,
        **kwargs: Any,
    ) -> TimeSeriesData:
        """Load time series data from CSV file.

        Args:
            path: Path to CSV file
            time_column: Name of the time column (auto-detected if None)
            **kwargs: Additional arguments passed to polars.read_csv()

        Returns:
            TimeSeriesData instance

        Example:
            >>> ts_data = TimeSeriesData.from_csv("data.csv")
            >>> ts_data = TimeSeriesData.from_csv(
            ...     "data.csv",
            ...     time_column="timestamp",
            ...     parse_dates=True
            ... )
        """
        # Try to parse dates automatically if not specified
        if "try_parse_dates" not in kwargs:
            kwargs["try_parse_dates"] = True

        df = pl.read_csv(path, **kwargs)
        return cls(df, time_column)

    @classmethod
    def from_parquet(
        cls,
        path: str | Path,
        time_column: Optional[str] = None,
        **kwargs: Any,
    ) -> TimeSeriesData:
        """Load time series data from Parquet file.

        Args:
            path: Path to Parquet file
            time_column: Name of the time column (auto-detected if None)
            **kwargs: Additional arguments passed to polars.read_parquet()

        Returns:
            TimeSeriesData instance

        Example:
            >>> ts_data = TimeSeriesData.from_parquet("data.parquet")
        """
        df = pl.read_parquet(path, **kwargs)
        return cls(df, time_column)

    def to_csv(self, path: str | Path, **kwargs: Any) -> None:
        """Save time series data to CSV file.

        Args:
            path: Output file path
            **kwargs: Additional arguments passed to DataFrame.write_csv()

        Example:
            >>> ts_data.to_csv("output.csv")
        """
        df = self.to_polars()
        df.write_csv(path, **kwargs)

    def to_parquet(self, path: str | Path, **kwargs: Any) -> None:
        """Save time series data to Parquet file.

        Args:
            path: Output file path
            **kwargs: Additional arguments passed to DataFrame.write_parquet()

        Example:
            >>> ts_data.to_parquet("output.parquet")
        """
        df = self.to_polars()
        df.write_parquet(path, **kwargs)

    def __len__(self) -> int:
        """Get the number of rows in the time series.

        Returns:
            Number of rows
        """
        return self._inner.__len__()

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of TimeSeriesData
        """
        return self._inner.__repr__()

    def head(self, n: int = 5) -> pl.DataFrame:
        """Get the first n rows.

        Args:
            n: Number of rows to return

        Returns:
            Polars DataFrame with first n rows
        """
        return self.to_polars().head(n)

    def tail(self, n: int = 5) -> pl.DataFrame:
        """Get the last n rows.

        Args:
            n: Number of rows to return

        Returns:
            Polars DataFrame with last n rows
        """
        return self.to_polars().tail(n)

    def describe(self) -> pl.DataFrame:
        """Generate descriptive statistics.

        Returns:
            Polars DataFrame with statistics for each column
        """
        return self.to_polars().describe()
