//! Feature engineering operations for time series data

use crate::error::Result;
use crate::pipeline::Operation;
use crate::timeseries::TimeSeriesData;

/// Lag operation - create lagged features
pub struct LagOperation {
    periods: Vec<i32>,
    columns: Option<Vec<String>>,
}

impl LagOperation {
    pub fn new(periods: Vec<i32>, columns: Option<Vec<String>>) -> Self {
        Self { periods, columns }
    }
}

impl Operation for LagOperation {
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData> {
        // Get columns to create lag features for
        let columns_to_lag = if let Some(cols) = &self.columns {
            cols.clone()
        } else {
            data.feature_columns().to_vec()
        };

        let mut df = data.dataframe().clone();

        // Create lag features for each column and period
        for col_name in &columns_to_lag {
            let column = df.column(col_name)?;
            let series = column.as_materialized_series().clone();

            for &period in &self.periods {
                // Create lag feature name
                let lag_name = format!("{}_lag_{}", col_name, period.abs());

                // Shift series by period (positive = backward, negative = forward)
                let lagged = series.shift(period as i64);

                // Add to dataframe
                df.with_column(lagged.with_name(lag_name.as_str().into()))?;
            }
        }

        // Create new TimeSeriesData with lagged features
        TimeSeriesData::new(df, Some(data.time_column()))
    }

    fn name(&self) -> &str {
        "lag"
    }
}

// TODO: Implement RollingOperation using LazyFrame API in future versions
// Rolling window operations need to be implemented using Polars LazyFrame API
// which has changed in version 0.51+
