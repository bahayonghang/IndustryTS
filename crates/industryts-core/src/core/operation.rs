//! Operation trait and base implementations
//!
//! This module defines the Operation trait that all time series operations must implement,
//! along with metadata and validation support.

use crate::error::Result;
use crate::core::data::TimeSeriesData;
use serde::{Deserialize, Serialize};

/// Metadata about an operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OperationMetadata {
    /// Name of the operation
    pub name: String,
    /// Description of what the operation does
    pub description: String,
    /// Version of the operation
    pub version: String,
    /// Category of the operation
    pub category: OperationCategory,
}

/// Categories for operations
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum OperationCategory {
    /// Data quality operations (cleaning, validation)
    DataQuality,
    /// Temporal operations (resampling, aggregation)
    Temporal,
    /// Feature engineering operations
    Features,
    /// Data transformation operations
    Transform,
}

impl std::fmt::Display for OperationCategory {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OperationCategory::DataQuality => write!(f, "data_quality"),
            OperationCategory::Temporal => write!(f, "temporal"),
            OperationCategory::Features => write!(f, "features"),
            OperationCategory::Transform => write!(f, "transform"),
        }
    }
}

/// Trait for time series operations
///
/// All operations that can be applied to time series data must implement this trait.
pub trait Operation: Send + Sync {
    /// Execute the operation on time series data
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData>;

    /// Get the name of the operation
    fn name(&self) -> &str;

    /// Validate that the operation can be applied to the given data
    ///
    /// This method should check preconditions like required columns, data types, etc.
    /// The default implementation does nothing.
    fn validate(&self, _data: &TimeSeriesData) -> Result<()> {
        Ok(())
    }

    /// Get metadata about the operation
    ///
    /// The default implementation provides basic metadata.
    fn metadata(&self) -> OperationMetadata {
        OperationMetadata {
            name: self.name().to_string(),
            description: String::new(),
            version: "1.0.0".to_string(),
            category: OperationCategory::Transform,
        }
    }
}

/// Base implementation for operations that operate on specific columns
pub trait ColumnOperation: Operation {
    /// Get the columns this operation applies to
    fn columns(&self) -> Option<&[String]>;

    /// Get the columns to apply the operation to
    /// If columns are specified, use those; otherwise use all feature columns
    fn get_target_columns(&self, data: &TimeSeriesData) -> Vec<String> {
        if let Some(cols) = self.columns() {
            cols.to_vec()
        } else {
            data.feature_columns().to_vec()
        }
    }

    /// Validate that all specified columns exist in the data
    fn validate_columns(&self, data: &TimeSeriesData) -> Result<()> {
        let df = data.dataframe();
        if let Some(cols) = self.columns() {
            for col in cols {
                if df.column(col).is_err() {
                    return Err(crate::IndustrytsError::ColumnNotFound(col.clone()));
                }
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_operation_category_display() {
        assert_eq!(OperationCategory::DataQuality.to_string(), "data_quality");
        assert_eq!(OperationCategory::Temporal.to_string(), "temporal");
        assert_eq!(OperationCategory::Features.to_string(), "features");
        assert_eq!(OperationCategory::Transform.to_string(), "transform");
    }

    #[test]
    fn test_operation_metadata_default() {
        struct DummyOp;

        impl Operation for DummyOp {
            fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData> {
                Ok(data)
            }

            fn name(&self) -> &str {
                "dummy"
            }
        }

        let op = DummyOp;
        let metadata = op.metadata();
        assert_eq!(metadata.name, "dummy");
        assert_eq!(metadata.version, "1.0.0");
    }
}
