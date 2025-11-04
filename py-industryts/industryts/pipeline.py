"""Processing pipeline for time series transformations."""

from __future__ import annotations

from pathlib import Path

from industryts import _its
from industryts.timeseries import TimeSeriesData


class Pipeline:
    """Composable pipeline for time series data processing.

    Build pipelines by chaining operations, then apply them to time series data
    for high-performance batch processing powered by Rust.

    Example:
        >>> import industryts as its
        >>> import polars as pl
        >>>
        >>> # Create pipeline from TOML config
        >>> pipeline = its.Pipeline.from_toml("config.toml")
        >>>
        >>> # Or create programmatically
        >>> pipeline = its.Pipeline()
        >>> # Operations would be added here
        >>>
        >>> # Process data
        >>> df = pl.DataFrame({"DateTime": [...], "value": [...]})
        >>> ts_data = its.TimeSeriesData(df)
        >>> result = pipeline.process(ts_data)
    """

    def __init__(self) -> None:
        """Create a new empty pipeline.

        Example:
            >>> pipeline = Pipeline()
        """
        self._inner = _its.Pipeline()

    @classmethod
    def from_toml(cls, path: str | Path) -> Pipeline:
        """Load pipeline from TOML configuration file.

        The TOML file should follow this structure:

        ```toml
        [pipeline]
        name = "my_pipeline"
        time_column = "DateTime"  # optional

        [[operations]]
        type = "fill_null"
        method = "forward"
        columns = ["temperature", "pressure"]  # optional

        [[operations]]
        type = "lag"
        periods = [1, 2, 3]
        columns = ["value"]  # optional

        [[operations]]
        type = "standardize"
        columns = ["temperature"]  # optional
        ```

        Supported operations:
        - fill_null: Fill missing values (methods: forward, backward, mean, zero)
        - lag: Create lagged features
        - standardize: Z-score normalization
        - resample: Time-based resampling (TODO: being updated for Polars 0.51)

        Args:
            path: Path to TOML configuration file

        Returns:
            Pipeline instance loaded from config

        Raises:
            IOError: If file cannot be read
            ValueError: If configuration is invalid

        Example:
            >>> pipeline = Pipeline.from_toml("examples/configs/basic_pipeline.toml")
            >>> print(len(pipeline))
            4
        """
        inner = _its.Pipeline.from_toml(str(path))
        instance = cls.__new__(cls)
        instance._inner = inner
        return instance

    def process(self, data: TimeSeriesData) -> TimeSeriesData:
        """Process time series data through the pipeline.

        All operations in the pipeline are applied sequentially to the input data.

        Args:
            data: Input time series data

        Returns:
            Processed time series data

        Raises:
            RuntimeError: If any operation fails

        Example:
            >>> result = pipeline.process(ts_data)
            >>> print(result.to_polars())
        """
        result_inner = self._inner.process(data._inner)

        # Wrap the result back in our Python class
        result = TimeSeriesData.__new__(TimeSeriesData)
        result._inner = result_inner
        return result

    def to_toml(self, path: str | Path) -> None:
        """Save pipeline configuration to TOML file.

        Args:
            path: Output file path

        Raises:
            IOError: If file cannot be written
            ValueError: If pipeline has no configuration to save

        Example:
            >>> pipeline.to_toml("saved_pipeline.toml")
        """
        self._inner.to_toml(str(path))

    def __len__(self) -> int:
        """Get the number of operations in the pipeline.

        Returns:
            Number of operations

        Example:
            >>> len(pipeline)
            3
        """
        return self._inner.__len__()

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of Pipeline
        """
        return self._inner.__repr__()


# Future: Add builder methods for programmatic pipeline construction
# This would allow:
# pipeline = Pipeline()
# pipeline.fill_null(method="forward")
# pipeline.lag(periods=[1, 2, 3])
# pipeline.standardize()
#
# For now, pipelines are created from TOML configs or
# operations can be added via the Rust API
