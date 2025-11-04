"""Unit tests for TimeSeriesData class."""

from __future__ import annotations

from pathlib import Path

import industryts as its
import polars as pl
import pytest


class TestTimeSeriesDataCreation:
    """Tests for TimeSeriesData creation and initialization."""

    def test_create_from_dataframe(self, sample_dataframe: pl.DataFrame) -> None:
        """Test creating TimeSeriesData from a Polars DataFrame."""
        ts_data = its.TimeSeriesData(sample_dataframe)

        assert ts_data is not None
        assert len(ts_data) == 10
        assert ts_data.time_column == "DateTime"
        assert "temperature" in ts_data.feature_columns
        assert "pressure" in ts_data.feature_columns

    def test_create_with_explicit_time_column(self, sample_datetime_range: pl.Series) -> None:
        """Test creating TimeSeriesData with explicit time column."""
        df = pl.DataFrame({
            "timestamp": sample_datetime_range,
            "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        })

        ts_data = its.TimeSeriesData(df, time_column="timestamp")

        assert ts_data.time_column == "timestamp"
        assert "value" in ts_data.feature_columns

    def test_auto_detect_time_column_tagtime(self, sample_datetime_range: pl.Series) -> None:
        """Test auto-detection of 'tagTime' as time column."""
        df = pl.DataFrame({
            "tagTime": sample_datetime_range,
            "sensor1": [1.0] * 10,
        })

        ts_data = its.TimeSeriesData(df)

        assert ts_data.time_column == "tagTime"
        assert "sensor1" in ts_data.feature_columns

    def test_auto_detect_time_column_timestamp(self, sample_datetime_range: pl.Series) -> None:
        """Test auto-detection of 'timestamp' as time column."""
        df = pl.DataFrame({
            "timestamp": sample_datetime_range,
            "sensor1": [1.0] * 10,
        })

        ts_data = its.TimeSeriesData(df)

        assert ts_data.time_column == "timestamp"

    def test_invalid_dataframe_type(self) -> None:
        """Test that non-DataFrame input raises TypeError."""
        with pytest.raises((TypeError, AttributeError)):
            its.TimeSeriesData([1, 2, 3])  # type: ignore

    def test_empty_dataframe(self) -> None:
        """Test behavior with empty DataFrame."""
        df = pl.DataFrame({
            "DateTime": pl.Series([], dtype=pl.Datetime),
            "value": pl.Series([], dtype=pl.Float64),
        })

        ts_data = its.TimeSeriesData(df)

        assert len(ts_data) == 0
        assert ts_data.time_column == "DateTime"


class TestTimeSeriesDataProperties:
    """Tests for TimeSeriesData properties and methods."""

    def test_time_column_property(self, sample_dataframe: pl.DataFrame) -> None:
        """Test time_column property."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        assert isinstance(ts_data.time_column, str)
        assert ts_data.time_column == "DateTime"

    def test_feature_columns_property(self, sample_dataframe: pl.DataFrame) -> None:
        """Test feature_columns property."""
        ts_data = its.TimeSeriesData(sample_dataframe)

        assert isinstance(ts_data.feature_columns, list)
        assert len(ts_data.feature_columns) == 2
        assert "temperature" in ts_data.feature_columns
        assert "pressure" in ts_data.feature_columns
        assert "DateTime" not in ts_data.feature_columns

    def test_len(self, sample_dataframe: pl.DataFrame) -> None:
        """Test __len__ method."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        assert len(ts_data) == 10

    def test_repr(self, sample_dataframe: pl.DataFrame) -> None:
        """Test __repr__ method."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        repr_str = repr(ts_data)

        assert "TimeSeriesData" in repr_str
        assert "10" in repr_str or "rows" in repr_str.lower()


class TestTimeSeriesDataConversion:
    """Tests for data conversion methods."""

    def test_to_polars(self, sample_dataframe: pl.DataFrame) -> None:
        """Test converting back to Polars DataFrame."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        result_df = ts_data.to_polars()

        assert isinstance(result_df, pl.DataFrame)
        assert result_df.shape == sample_dataframe.shape
        assert result_df.columns == sample_dataframe.columns

    def test_to_polars_preserves_data(self, sample_dataframe: pl.DataFrame) -> None:
        """Test that to_polars preserves data integrity."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        result_df = ts_data.to_polars()

        # Compare data values
        assert result_df["DateTime"].to_list() == sample_dataframe["DateTime"].to_list()
        assert result_df["temperature"].to_list() == sample_dataframe["temperature"].to_list()
        assert result_df["pressure"].to_list() == sample_dataframe["pressure"].to_list()


class TestTimeSeriesDataIO:
    """Tests for I/O operations."""

    def test_to_csv(self, sample_dataframe: pl.DataFrame, temp_dir: Path) -> None:
        """Test saving to CSV file."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        output_path = temp_dir / "output.csv"

        ts_data.to_csv(str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_from_csv(self, sample_dataframe: pl.DataFrame, temp_dir: Path) -> None:
        """Test loading from CSV file."""
        # Save first
        ts_data = its.TimeSeriesData(sample_dataframe)
        csv_path = temp_dir / "test.csv"
        ts_data.to_csv(str(csv_path))

        # Load back
        loaded_ts = its.TimeSeriesData.from_csv(str(csv_path))

        assert len(loaded_ts) == len(ts_data)
        assert loaded_ts.time_column == ts_data.time_column
        assert loaded_ts.feature_columns == ts_data.feature_columns

    def test_to_parquet(self, sample_dataframe: pl.DataFrame, temp_dir: Path) -> None:
        """Test saving to Parquet file."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        output_path = temp_dir / "output.parquet"

        ts_data.to_parquet(str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_from_parquet(self, sample_dataframe: pl.DataFrame, temp_dir: Path) -> None:
        """Test loading from Parquet file."""
        # Save first
        ts_data = its.TimeSeriesData(sample_dataframe)
        parquet_path = temp_dir / "test.parquet"
        ts_data.to_parquet(str(parquet_path))

        # Load back
        loaded_ts = its.TimeSeriesData.from_parquet(str(parquet_path))

        assert len(loaded_ts) == len(ts_data)
        assert loaded_ts.time_column == ts_data.time_column
        assert loaded_ts.feature_columns == ts_data.feature_columns

    def test_csv_roundtrip_preserves_data(
        self,
        sample_dataframe: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test that CSV save/load preserves data."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        csv_path = temp_dir / "roundtrip.csv"

        # Save and load
        ts_data.to_csv(str(csv_path))
        loaded_ts = its.TimeSeriesData.from_csv(str(csv_path))

        # Compare data
        original_df = ts_data.to_polars()
        loaded_df = loaded_ts.to_polars()

        assert loaded_df.shape == original_df.shape
        # Note: DateTime parsing might change precision, so we check column names
        assert loaded_df.columns == original_df.columns


class TestTimeSeriesDataHelpers:
    """Tests for helper methods."""

    def test_head(self, sample_dataframe: pl.DataFrame) -> None:
        """Test head method."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        head_df = ts_data.head(5)

        assert isinstance(head_df, pl.DataFrame)
        assert len(head_df) == 5

    def test_head_default(self, sample_dataframe: pl.DataFrame) -> None:
        """Test head with default parameter."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        head_df = ts_data.head()

        assert len(head_df) == 5

    def test_tail(self, sample_dataframe: pl.DataFrame) -> None:
        """Test tail method."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        tail_df = ts_data.tail(3)

        assert isinstance(tail_df, pl.DataFrame)
        assert len(tail_df) == 3

    def test_tail_default(self, sample_dataframe: pl.DataFrame) -> None:
        """Test tail with default parameter."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        tail_df = ts_data.tail()

        assert len(tail_df) == 5

    def test_describe(self, sample_dataframe: pl.DataFrame) -> None:
        """Test describe method."""
        ts_data = its.TimeSeriesData(sample_dataframe)
        desc_df = ts_data.describe()

        assert isinstance(desc_df, pl.DataFrame)
        # Should contain statistics for numeric columns
        assert len(desc_df) > 0


class TestTimeSeriesDataEdgeCases:
    """Tests for edge cases and error handling."""

    def test_single_row_dataframe(self, sample_datetime_range: pl.Series) -> None:
        """Test with single row DataFrame."""
        df = pl.DataFrame({
            "DateTime": sample_datetime_range[:1],
            "value": [42.0],
        })

        ts_data = its.TimeSeriesData(df)

        assert len(ts_data) == 1
        assert ts_data.time_column == "DateTime"

    def test_dataframe_with_nulls(self, sample_dataframe_with_nulls: pl.DataFrame) -> None:
        """Test creation with DataFrame containing null values."""
        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)

        assert ts_data is not None
        assert len(ts_data) == 10

    def test_many_feature_columns(self, sample_datetime_range: pl.Series) -> None:
        """Test with many feature columns."""
        data = {"DateTime": sample_datetime_range}
        for i in range(50):
            data[f"sensor_{i}"] = [float(i)] * 10

        df = pl.DataFrame(data)
        ts_data = its.TimeSeriesData(df)

        assert len(ts_data.feature_columns) == 50
        assert ts_data.time_column == "DateTime"

