#!/usr/bin/env python3
"""Basic usage example for industryts library.

This example demonstrates:
1. Creating time series data from a Polars DataFrame
2. Loading a pipeline from TOML configuration
3. Processing data through the pipeline
4. Exporting results
"""

import polars as pl
from datetime import datetime, timedelta
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR / "configs"

# Create sample time series data
print("Creating sample time series data...")
dates = pl.datetime_range(
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 10),
    interval="1d",
    eager=True,
)

data = pl.DataFrame({
    "DateTime": dates,
    "temperature": [20.1, 21.5, 19.8, 22.3, 21.0, 20.5, 21.2, 20.8, 21.5, 22.0],
    "pressure": [1013, 1015, 1012, 1018, 1016, 1014, 1017, 1015, 1016, 1019],
})

print(f"Created DataFrame with {len(data)} rows")
print(data)
print()

# Import industryts (this will only work after building the package)
try:
    import industryts as its

    # Create TimeSeriesData
    print("Creating TimeSeriesData...")
    ts_data = its.TimeSeriesData(data)
    print(f"Time column: {ts_data.time_column}")
    print(f"Feature columns: {ts_data.feature_columns}")
    print(f"Number of rows: {len(ts_data)}")
    print()

    # Load pipeline from config
    print("Loading pipeline from config...")
    config_path = CONFIG_DIR / "feature_engineering.toml"
    pipeline = its.Pipeline.from_toml(str(config_path))
    print(f"Pipeline loaded with {len(pipeline)} operations")
    print()

    # Process data
    print("Processing data through pipeline...")
    result = pipeline.process(ts_data)
    print(f"Processed data has {len(result)} rows")
    print()

    # Show results
    print("Result DataFrame:")
    result_df = result.to_polars()
    print(result_df)
    print()

    # Export results
    print("Exporting results...")
    result.to_csv("output.csv")
    print("Results saved to output.csv")

except ImportError as e:
    print(f"Error: {e}")
    print()
    print("The industryts package needs to be built first.")
    print("Run: maturin develop")
    print("Or: uv run maturin develop")
