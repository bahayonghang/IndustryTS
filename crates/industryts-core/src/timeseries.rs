//! Time series data structure and operations

use crate::error::{IndustrytsError, Result};
use polars::prelude::*;

/// Core time series data structure wrapping a Polars DataFrame
#[derive(Clone)]
pub struct TimeSeriesData {
    /// Underlying Polars DataFrame
    df: DataFrame,
    /// Name of the time column
    time_column: String,
    /// Names of feature columns
    feature_columns: Vec<String>,
}

impl TimeSeriesData {
    /// Create a new TimeSeriesData instance
    ///
    /// # Arguments
    ///
    /// * `df` - Polars DataFrame containing the data
    /// * `time_column` - Optional time column name (auto-detected if None)
    ///
    /// # Returns
    ///
    /// Result containing TimeSeriesData or error
    pub fn new(df: DataFrame, time_column: Option<&str>) -> Result<Self> {
        let time_col = if let Some(col) = time_column {
            col.to_string()
        } else {
            Self::detect_time_column(&df)?
        };

        // Validate time column exists and has appropriate type
        Self::validate_time_column(&df, &time_col)?;

        // Get feature columns (all columns except time column)
        let feature_columns: Vec<String> = df
            .get_column_names()
            .into_iter()
            .filter(|&name| name != time_col.as_str())
            .map(|s| s.to_string())
            .collect();

        Ok(Self {
            df,
            time_column: time_col,
            feature_columns,
        })
    }

    /// Auto-detect time column based on common naming patterns
    fn detect_time_column(df: &DataFrame) -> Result<String> {
        let common_names = [
            "DateTime",
            "datetime",
            "tagTime",
            "tagtime",
            "timestamp",
            "Timestamp",
            "time",
            "Time",
            "date",
            "Date",
        ];

        for name in &common_names {
            if df
                .get_column_names()
                .iter()
                .any(|col| col.as_str() == *name)
            {
                return Ok(name.to_string());
            }
        }

        // If no common name found, use first column
        df.get_column_names()
            .first()
            .map(|s| s.to_string())
            .ok_or_else(|| IndustrytsError::TimeColumnNotFound("DataFrame is empty".to_string()))
    }

    /// Validate that the time column exists and has datetime type
    fn validate_time_column(df: &DataFrame, col_name: &str) -> Result<()> {
        let col = df
            .column(col_name)
            .map_err(|_| IndustrytsError::TimeColumnNotFound(col_name.to_string()))?;

        match col.dtype() {
            DataType::Date | DataType::Datetime(_, _) => Ok(()),
            dtype => Err(IndustrytsError::InvalidTimeColumnType(format!(
                "{:?}",
                dtype
            ))),
        }
    }

    /// Get reference to the underlying DataFrame
    pub fn dataframe(&self) -> &DataFrame {
        &self.df
    }

    /// Get mutable reference to the underlying DataFrame
    pub fn dataframe_mut(&mut self) -> &mut DataFrame {
        &mut self.df
    }

    /// Get the time column name
    pub fn time_column(&self) -> &str {
        &self.time_column
    }

    /// Get feature column names
    pub fn feature_columns(&self) -> &[String] {
        &self.feature_columns
    }

    /// Convert to Polars DataFrame (consumes self)
    pub fn into_dataframe(self) -> DataFrame {
        self.df
    }

    /// Get number of rows
    pub fn len(&self) -> usize {
        self.df.height()
    }

    /// Check if empty
    pub fn is_empty(&self) -> bool {
        self.df.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_time_column_detection() {
        use polars::prelude::*;

        // Create datetime series from milliseconds since epoch
        let dates_ms = vec![1704067200000i64, 1704153600000, 1704240000000];
        let time_series = Series::new("DateTime".into(), dates_ms)
            .cast(&DataType::Datetime(TimeUnit::Milliseconds, None))
            .unwrap();

        let df = DataFrame::new(vec![
            time_series.into(),
            Series::new("value".into(), &[10.0, 20.0, 30.0]).into(),
        ])
        .unwrap();

        let detected = TimeSeriesData::detect_time_column(&df).unwrap();
        assert_eq!(detected, "DateTime");
    }

    #[test]
    fn test_feature_columns() {
        use polars::prelude::*;

        // Create datetime series from milliseconds since epoch
        let dates_ms = vec![1704067200000i64, 1704153600000, 1704240000000];
        let time_series = Series::new("DateTime".into(), dates_ms)
            .cast(&DataType::Datetime(TimeUnit::Milliseconds, None))
            .unwrap();

        let df = DataFrame::new(vec![
            time_series.into(),
            Series::new("temp".into(), &[10.0, 20.0, 30.0]).into(),
            Series::new("pressure".into(), &[100.0, 200.0, 300.0]).into(),
        ])
        .unwrap();

        let ts = TimeSeriesData::new(df, Some("DateTime")).unwrap();
        assert_eq!(ts.feature_columns(), &["temp", "pressure"]);
    }
}
