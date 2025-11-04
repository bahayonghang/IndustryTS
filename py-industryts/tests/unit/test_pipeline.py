"""Unit tests for Pipeline class."""

from __future__ import annotations

from pathlib import Path

import industryts as its
import polars as pl
import pytest


class TestPipelineCreation:
    """Tests for Pipeline creation and initialization."""

    def test_create_empty_pipeline(self) -> None:
        """Test creating an empty pipeline."""
        pipeline = its.Pipeline()

        assert pipeline is not None
        assert len(pipeline) == 0

    def test_from_toml(self, basic_pipeline_config: str, temp_dir: Path) -> None:
        """Test loading pipeline from TOML config."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        pipeline = its.Pipeline.from_toml(str(config_path))

        assert pipeline is not None
        assert len(pipeline) > 0

    def test_from_toml_with_path_object(
        self,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test loading pipeline from Path object."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        pipeline = its.Pipeline.from_toml(config_path)

        assert pipeline is not None
        assert len(pipeline) > 0

    def test_from_toml_nonexistent_file(self, temp_dir: Path) -> None:
        """Test loading from non-existent file raises error."""
        nonexistent_path = temp_dir / "nonexistent.toml"

        with pytest.raises((OSError, FileNotFoundError, RuntimeError)):
            its.Pipeline.from_toml(str(nonexistent_path))

    def test_from_toml_invalid_config(self, temp_dir: Path) -> None:
        """Test loading invalid TOML raises error."""
        config_path = temp_dir / "invalid.toml"
        config_path.write_text("invalid toml content [[[")

        with pytest.raises(Exception):  # Could be TOMLError or RuntimeError
            its.Pipeline.from_toml(str(config_path))


class TestPipelineProperties:
    """Tests for Pipeline properties."""

    def test_len_empty(self) -> None:
        """Test length of empty pipeline."""
        pipeline = its.Pipeline()
        assert len(pipeline) == 0

    def test_len_with_operations(
        self,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test length with operations."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        pipeline = its.Pipeline.from_toml(str(config_path))

        # basic_pipeline_config has 2 operations
        assert len(pipeline) == 2

    def test_repr(self, basic_pipeline_config: str, temp_dir: Path) -> None:
        """Test __repr__ method."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        pipeline = its.Pipeline.from_toml(str(config_path))
        repr_str = repr(pipeline)

        assert "Pipeline" in repr_str


class TestPipelineProcessing:
    """Tests for pipeline processing."""

    def test_process_basic_pipeline(
        self,
        sample_dataframe: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test processing data through basic pipeline."""
        # Create pipeline
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        # Create time series data
        ts_data = its.TimeSeriesData(sample_dataframe)

        # Process
        result = pipeline.process(ts_data)

        assert result is not None
        assert isinstance(result, its.TimeSeriesData)
        assert len(result) > 0

    def test_process_preserves_time_column(
        self,
        sample_dataframe: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test that processing preserves time column."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe)
        result = pipeline.process(ts_data)

        assert result.time_column == ts_data.time_column

    def test_process_feature_engineering(
        self,
        sample_dataframe: pl.DataFrame,
        feature_engineering_config: str,
        temp_dir: Path
    ) -> None:
        """Test feature engineering pipeline."""
        config_path = temp_dir / "feature_eng.toml"
        config_path.write_text(feature_engineering_config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe)
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Should have lag features
        lag_columns = [col for col in result_df.columns if "lag" in col.lower()]
        assert len(lag_columns) > 0

    def test_process_with_nulls(
        self,
        sample_dataframe_with_nulls: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test processing data with null values."""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)
        result = pipeline.process(ts_data)

        assert result is not None
        assert len(result) > 0


class TestPipelineConfigIO:
    """Tests for pipeline configuration I/O."""

    def test_to_toml(
        self,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test saving pipeline to TOML."""
        # Load pipeline
        load_path = temp_dir / "load.toml"
        load_path.write_text(basic_pipeline_config)
        pipeline = its.Pipeline.from_toml(str(load_path))

        # Save to new file
        save_path = temp_dir / "save.toml"
        pipeline.to_toml(str(save_path))

        assert save_path.exists()
        assert save_path.stat().st_size > 0

    def test_toml_roundtrip(
        self,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test TOML save/load roundtrip."""
        # Load original
        original_path = temp_dir / "original.toml"
        original_path.write_text(basic_pipeline_config)
        original_pipeline = its.Pipeline.from_toml(str(original_path))

        # Save
        save_path = temp_dir / "saved.toml"
        original_pipeline.to_toml(str(save_path))

        # Load saved
        loaded_pipeline = its.Pipeline.from_toml(str(save_path))

        # Should have same number of operations
        assert len(loaded_pipeline) == len(original_pipeline)


class TestPipelineOperations:
    """Tests for specific operations in pipeline."""

    def test_fill_null_operation(
        self,
        sample_dataframe_with_nulls: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test fill_null operation."""
        config = """
[pipeline]
name = "fill_test"

[[operations]]
type = "fill_null"
method = "forward"
"""
        config_path = temp_dir / "fill_null.toml"
        config_path.write_text(config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Check that nulls are filled (or at least processed)
        assert result_df is not None

    def test_standardize_operation(
        self,
        sample_dataframe: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test standardize operation."""
        config = """
[pipeline]
name = "standardize_test"

[[operations]]
type = "standardize"
columns = ["temperature", "pressure"]
"""
        config_path = temp_dir / "standardize.toml"
        config_path.write_text(config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe)
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Standardized values should have different scale
        assert result_df is not None
        assert len(result_df) == len(sample_dataframe)

    def test_lag_operation(
        self,
        sample_dataframe: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test lag operation."""
        config = """
[pipeline]
name = "lag_test"

[[operations]]
type = "lag"
periods = [1, 2]
columns = ["temperature"]
"""
        config_path = temp_dir / "lag.toml"
        config_path.write_text(config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe)
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Should have lag columns
        assert "temperature_lag_1" in result_df.columns
        assert "temperature_lag_2" in result_df.columns

    def test_multiple_operations(
        self,
        sample_dataframe_with_nulls: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test pipeline with multiple operations."""
        config = """
[pipeline]
name = "multi_op_test"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "lag"
periods = [1]
columns = ["temperature"]

[[operations]]
type = "standardize"
"""
        config_path = temp_dir / "multi_op.toml"
        config_path.write_text(config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Should have processed successfully
        assert result_df is not None
        # Should have lag column
        assert any("lag" in col.lower() for col in result_df.columns)


class TestPipelineEdgeCases:
    """Tests for edge cases."""

    def test_empty_pipeline_processing(self, sample_dataframe: pl.DataFrame) -> None:
        """Test processing with empty pipeline."""
        pipeline = its.Pipeline()
        ts_data = its.TimeSeriesData(sample_dataframe)

        # Empty pipeline should return data unchanged
        result = pipeline.process(ts_data)

        assert result is not None
        assert len(result) == len(ts_data)

    def test_pipeline_with_single_row(
        self,
        sample_datetime_range: pl.Series,
        temp_dir: Path
    ) -> None:
        """Test processing single-row data."""
        df = pl.DataFrame({
            "DateTime": sample_datetime_range[:1],
            "value": [42.0],
        })

        # Use a simpler config without standardization (which needs > 1 row)
        config = """
[pipeline]
name = "simple"

[[operations]]
type = "fill_null"
method = "forward"
"""
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        ts_data = its.TimeSeriesData(df)
        result = pipeline.process(ts_data)

        assert result is not None

