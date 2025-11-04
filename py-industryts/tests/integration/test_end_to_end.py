"""End-to-end integration tests for industryts."""

from __future__ import annotations

from pathlib import Path

import industryts as its
import polars as pl
import pytest


class TestEndToEndWorkflows:
    """Test complete workflows from data loading to export."""

    def test_csv_to_pipeline_to_csv(
        self,
        sample_dataframe: pl.DataFrame,
        feature_engineering_config: str,
        temp_dir: Path
    ) -> None:
        """Test complete workflow: CSV -> Pipeline -> CSV."""
        # Save input data
        input_csv = temp_dir / "input.csv"
        sample_dataframe.write_csv(str(input_csv))

        # Save pipeline config
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(feature_engineering_config)

        # Load data
        ts_data = its.TimeSeriesData.from_csv(str(input_csv))

        # Load and apply pipeline
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        # Export results
        output_csv = temp_dir / "output.csv"
        result.to_csv(str(output_csv))

        # Verify output
        assert output_csv.exists()
        output_df = pl.read_csv(str(output_csv))
        assert len(output_df) > 0

    def test_parquet_to_pipeline_to_parquet(
        self,
        sample_dataframe: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test complete workflow: Parquet -> Pipeline -> Parquet."""
        # Save input data
        input_parquet = temp_dir / "input.parquet"
        sample_dataframe.write_parquet(str(input_parquet))

        # Save pipeline config
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        # Load data
        ts_data = its.TimeSeriesData.from_parquet(str(input_parquet))

        # Load and apply pipeline
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        # Export results
        output_parquet = temp_dir / "output.parquet"
        result.to_parquet(str(output_parquet))

        # Verify output
        assert output_parquet.exists()
        output_df = pl.read_parquet(str(output_parquet))
        assert len(output_df) > 0

    def test_data_cleaning_workflow(
        self,
        sample_dataframe_with_nulls: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test data cleaning workflow with null values."""
        config = """
[pipeline]
name = "cleaning"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "fill_null"
method = "backward"
"""
        config_path = temp_dir / "cleaning.toml"
        config_path.write_text(config)

        # Process
        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        # Verify
        assert result is not None
        assert len(result) == len(ts_data)

    def test_feature_engineering_workflow(
        self,
        sample_dataframe: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test feature engineering with lag and standardization."""
        config = """
[pipeline]
name = "feature_engineering"

[[operations]]
type = "lag"
periods = [1, 2, 3]
columns = ["temperature", "pressure"]

[[operations]]
type = "standardize"
"""
        config_path = temp_dir / "feat_eng.toml"
        config_path.write_text(config)

        # Process
        ts_data = its.TimeSeriesData(sample_dataframe)
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Verify lag features were created
        lag_cols = [col for col in result_df.columns if "lag" in col.lower()]
        assert len(lag_cols) > 0
        # Should have lag features for both columns and all periods
        # (2 columns * 3 periods = 6 lag columns)
        assert len(lag_cols) >= 6

    def test_multi_step_transformation(
        self,
        sample_dataframe_with_nulls: pl.DataFrame,
        temp_dir: Path
    ) -> None:
        """Test multi-step transformation pipeline."""
        config = """
[pipeline]
name = "multi_step"

# Step 1: Clean nulls
[[operations]]
type = "fill_null"
method = "forward"

# Step 2: Create features
[[operations]]
type = "lag"
periods = [1, 2]
columns = ["temperature"]

# Step 3: Normalize
[[operations]]
type = "standardize"
"""
        config_path = temp_dir / "multi_step.toml"
        config_path.write_text(config)

        # Process
        ts_data = its.TimeSeriesData(sample_dataframe_with_nulls)
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Verify all steps executed
        assert result_df is not None
        assert len(result_df) > 0
        assert "temperature_lag_1" in result_df.columns
        assert "temperature_lag_2" in result_df.columns


class TestRealWorldScenarios:
    """Tests simulating real-world use cases."""

    def test_sensor_data_processing(self, temp_dir: Path) -> None:
        """Test processing industrial sensor data."""
        from datetime import datetime

        # Create realistic sensor data
        dates = pl.datetime_range(
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 31),
            interval="1h",
            eager=True,
        )

        df = pl.DataFrame({
            "DateTime": dates,
            "sensor_temp": [20.0 + i * 0.1 for i in range(len(dates))],
            "sensor_pressure": [1013 + i * 0.5 for i in range(len(dates))],
            "sensor_flow": [50.0 + i * 0.2 for i in range(len(dates))],
        })

        # Add some null values to simulate sensor failures
        df = df.with_columns([
            pl.when(pl.col("sensor_temp") > 30)
            .then(None)
            .otherwise(pl.col("sensor_temp"))
            .alias("sensor_temp")
        ])

        # Process
        config = """
[pipeline]
name = "sensor_processing"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "lag"
periods = [1, 24]  # 1 hour and 1 day lag
columns = ["sensor_temp", "sensor_pressure"]

[[operations]]
type = "standardize"
"""
        config_path = temp_dir / "sensor.toml"
        config_path.write_text(config)

        ts_data = its.TimeSeriesData(df)
        pipeline = its.Pipeline.from_toml(str(config_path))
        result = pipeline.process(ts_data)

        result_df = result.to_polars()

        # Verify processing
        assert len(result_df) > 0
        assert "sensor_temp_lag_1" in result_df.columns
        assert "sensor_temp_lag_24" in result_df.columns

    def test_batch_processing_multiple_files(
        self,
        sample_dataframe: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test batch processing multiple data files."""
        # Create multiple input files
        input_files = []
        for i in range(3):
            file_path = temp_dir / f"input_{i}.csv"
            sample_dataframe.write_csv(str(file_path))
            input_files.append(file_path)

        # Save pipeline config
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)

        # Load pipeline once
        pipeline = its.Pipeline.from_toml(str(config_path))

        # Process all files
        results = []
        for input_file in input_files:
            ts_data = its.TimeSeriesData.from_csv(str(input_file))
            result = pipeline.process(ts_data)
            results.append(result)

        # Verify all processed
        assert len(results) == 3
        for result in results:
            assert len(result) > 0

    def test_pipeline_reusability(
        self,
        sample_dataframe: pl.DataFrame,
        basic_pipeline_config: str,
        temp_dir: Path
    ) -> None:
        """Test that same pipeline can be applied to different datasets."""
        # Create pipeline
        config_path = temp_dir / "pipeline.toml"
        config_path.write_text(basic_pipeline_config)
        pipeline = its.Pipeline.from_toml(str(config_path))

        # Create different datasets
        df1 = sample_dataframe
        df2 = sample_dataframe.with_columns([
            pl.col("temperature") * 2,
            pl.col("pressure") + 10,
        ])

        # Process both
        ts1 = its.TimeSeriesData(df1)
        ts2 = its.TimeSeriesData(df2)

        result1 = pipeline.process(ts1)
        result2 = pipeline.process(ts2)

        # Both should succeed
        assert len(result1) > 0
        assert len(result2) > 0


class TestErrorHandling:
    """Test error handling in real-world scenarios."""

    def test_corrupted_config_file(self, temp_dir: Path) -> None:
        """Test handling of corrupted configuration file."""
        config_path = temp_dir / "corrupted.toml"
        config_path.write_text("[[operations]\ntype = 'invalid")

        with pytest.raises(Exception):
            its.Pipeline.from_toml(str(config_path))

    def test_missing_required_columns(self, temp_dir: Path) -> None:
        """Test handling when specified columns don't exist."""
        from datetime import datetime

        df = pl.DataFrame({
            "DateTime": pl.datetime_range(
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 10),
                interval="1d",
                eager=True
            ),
            "temp": [20.0] * 10,
        })

        config = """
[pipeline]
name = "test"

[[operations]]
type = "lag"
periods = [1]
columns = ["nonexistent_column"]
"""
        config_path = temp_dir / "bad_cols.toml"
        config_path.write_text(config)

        ts_data = its.TimeSeriesData(df)
        pipeline = its.Pipeline.from_toml(str(config_path))

        # This should raise an error or handle gracefully
        with pytest.raises(Exception):
            pipeline.process(ts_data)

    def test_empty_dataframe_processing(
        self,
        temp_dir: Path
    ) -> None:
        """Test processing empty DataFrame."""
        df = pl.DataFrame({
            "DateTime": pl.Series([], dtype=pl.Datetime),
            "value": pl.Series([], dtype=pl.Float64),
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

        ts_data = its.TimeSeriesData(df)
        pipeline = its.Pipeline.from_toml(str(config_path))

        # Should handle empty data gracefully
        result = pipeline.process(ts_data)
        assert len(result) == 0

