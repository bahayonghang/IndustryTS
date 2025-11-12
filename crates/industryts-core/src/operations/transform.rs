//! Data transformation operations

use crate::core::{Operation, TimeSeriesData};
use crate::error::Result;

/// Standardize operation - z-score normalization
pub struct StandardizeOperation {
    columns: Option<Vec<String>>,
}

impl StandardizeOperation {
    pub fn new(columns: Option<Vec<String>>) -> Self {
        Self { columns }
    }
}

impl Operation for StandardizeOperation {
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData> {
        // Get columns to standardize
        let columns_to_std = if let Some(cols) = &self.columns {
            cols.clone()
        } else {
            data.feature_columns().to_vec()
        };

        let mut df = data.dataframe().clone();

        // Standardize each column: (x - mean) / std
        for col_name in &columns_to_std {
            let column = df.column(col_name)?;
            let series = column.as_materialized_series().clone();

            // Calculate mean and std
            let mean = series.mean().ok_or_else(|| {
                crate::IndustrytsError::OperationError(format!(
                    "Cannot calculate mean for column: {}",
                    col_name
                ))
            })?;

            let std = series.std(1).ok_or_else(|| {
                crate::IndustrytsError::OperationError(format!(
                    "Cannot calculate std for column: {}",
                    col_name
                ))
            })?;

            // Avoid division by zero
            if std == 0.0 {
                return Err(crate::IndustrytsError::OperationError(format!(
                    "Standard deviation is zero for column: {}",
                    col_name
                )));
            }

            // Standardize: (x - mean) / std
            let standardized = (&series - mean) / std;

            // Replace the column
            df.replace(col_name, standardized)?;
        }

        // Create new TimeSeriesData with standardized data
        TimeSeriesData::new(df, Some(data.time_column()))
    }

    fn name(&self) -> &str {
        "standardize"
    }
}

/// Normalize operation - min-max normalization to [0, 1]
pub struct NormalizeOperation {
    columns: Option<Vec<String>>,
}

impl NormalizeOperation {
    pub fn new(columns: Option<Vec<String>>) -> Self {
        Self { columns }
    }
}

impl Operation for NormalizeOperation {
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData> {
        // Get columns to normalize
        let columns_to_norm = if let Some(cols) = &self.columns {
            cols.clone()
        } else {
            data.feature_columns().to_vec()
        };

        let mut df = data.dataframe().clone();

        // Normalize each column: (x - min) / (max - min)
        for col_name in &columns_to_norm {
            let column = df.column(col_name)?;
            let series = column.as_materialized_series().clone();

            // Calculate min and max
            let min_val = series.min::<f64>()?.ok_or_else(|| {
                crate::IndustrytsError::OperationError(format!(
                    "Cannot calculate min for column: {}",
                    col_name
                ))
            })?;

            let max_val = series.max::<f64>()?.ok_or_else(|| {
                crate::IndustrytsError::OperationError(format!(
                    "Cannot calculate max for column: {}",
                    col_name
                ))
            })?;

            // Avoid division by zero
            let range = max_val - min_val;
            if range == 0.0 {
                return Err(crate::IndustrytsError::OperationError(format!(
                    "Range is zero for column: {}",
                    col_name
                )));
            }

            // Normalize: (x - min) / (max - min)
            let normalized = (&series - min_val) / range;

            // Replace the column
            df.replace(col_name, normalized)?;
        }

        // Create new TimeSeriesData with normalized data
        TimeSeriesData::new(df, Some(data.time_column()))
    }

    fn name(&self) -> &str {
        "normalize"
    }
}

/// Difference operation - calculate differences between consecutive values
pub struct DifferenceOperation {
    lag: usize,
    columns: Option<Vec<String>>,
}

impl DifferenceOperation {
    pub fn new(lag: usize, columns: Option<Vec<String>>) -> Self {
        Self { lag, columns }
    }
}

impl Operation for DifferenceOperation {
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData> {
        // Get columns to difference
        let columns_to_diff = if let Some(cols) = &self.columns {
            cols.clone()
        } else {
            data.feature_columns().to_vec()
        };

        let mut df = data.dataframe().clone();

        // Calculate differences for each column
        for col_name in &columns_to_diff {
            let column = df.column(col_name)?;
            let series = column.as_materialized_series().clone();

            // Calculate difference: x(t) - x(t-lag)
            let shifted = series.shift(self.lag as i64);
            let diff = (&series - &shifted)?;

            // Create new column name
            let diff_name = format!("{}_diff_{}", col_name, self.lag);

            // Add to dataframe
            df.with_column(diff.with_name(diff_name.as_str().into()))?;
        }

        // Create new TimeSeriesData with difference features
        TimeSeriesData::new(df, Some(data.time_column()))
    }

    fn name(&self) -> &str {
        "difference"
    }
}
