//! Fill null operation for handling missing values

use crate::config::FillMethod;
use crate::core::{Operation, TimeSeriesData};
use crate::error::Result;
use polars::prelude::*;

/// Fill null operation
pub struct FillNullOperation {
    method: FillMethod,
    columns: Option<Vec<String>>,
}

impl FillNullOperation {
    pub fn new(method: FillMethod, columns: Option<Vec<String>>) -> Self {
        Self { method, columns }
    }
}

impl Operation for FillNullOperation {
    fn execute(&self, mut data: TimeSeriesData) -> Result<TimeSeriesData> {
        // Get columns to fill before mutable borrow
        let columns_to_fill = if let Some(cols) = &self.columns {
            cols.clone()
        } else {
            data.feature_columns().to_vec()
        };

        let df = data.dataframe_mut();
        for col_name in columns_to_fill {
            let column = df.column(&col_name)?;
            let series = column.as_materialized_series().clone();

            let filled = match self.method {
                FillMethod::Forward => series.fill_null(FillNullStrategy::Forward(None))?,
                FillMethod::Backward => series.fill_null(FillNullStrategy::Backward(None))?,
                FillMethod::Zero => series.fill_null(FillNullStrategy::Zero)?,
                FillMethod::Mean => series.fill_null(FillNullStrategy::Mean)?,
            };

            df.replace(&col_name, filled)?;
        }

        Ok(data)
    }

    fn name(&self) -> &str {
        "fill_null"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fill_null_forward() {
        use polars::prelude::*;

        // Create datetime series from milliseconds since epoch
        let dates_ms = vec![
            1704067200000i64, // 2024-01-01
            1704153600000,    // 2024-01-02
            1704240000000,    // 2024-01-03
            1704326400000,    // 2024-01-04
        ];
        let time_series = Series::new("time".into(), dates_ms)
            .cast(&DataType::Datetime(TimeUnit::Milliseconds, None))
            .unwrap();

        let df = DataFrame::new(vec![
            time_series.into(),
            Series::new("value".into(), &[Some(1.0), None, None, Some(4.0)]).into(),
        ])
        .unwrap();

        let ts = TimeSeriesData::new(df, Some("time")).unwrap();
        let op = FillNullOperation::new(FillMethod::Forward, None);
        let result = op.execute(ts).unwrap();

        let value_col = result.dataframe().column("value").unwrap();
        assert_eq!(value_col.len(), 4);
    }
}
