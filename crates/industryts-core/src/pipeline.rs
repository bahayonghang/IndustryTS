//! Pipeline for chaining time series operations

use crate::config::{OperationConfig, PipelineConfig};
use crate::error::{IndustrytsError, Result};
use crate::operations::*;
use crate::timeseries::TimeSeriesData;
use std::path::Path;

/// Trait for time series operations
pub trait Operation: Send + Sync {
    /// Execute the operation on time series data
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData>;

    /// Get the name of the operation
    fn name(&self) -> &str;
}

/// Pipeline that chains multiple operations
pub struct Pipeline {
    operations: Vec<Box<dyn Operation>>,
    config: Option<PipelineConfig>,
}

impl Pipeline {
    /// Create a new empty pipeline
    pub fn new() -> Self {
        Self {
            operations: Vec::new(),
            config: None,
        }
    }

    /// Load pipeline from TOML configuration file
    pub fn from_toml<P: AsRef<Path>>(path: P) -> Result<Self> {
        let config = PipelineConfig::from_toml_file(path.as_ref())?;
        let mut pipeline = Self::new();
        pipeline.config = Some(config.clone());

        // Convert OperationConfig to Operation instances
        for op_config in &config.operations {
            let operation = Self::create_operation(op_config)?;
            pipeline.add_operation(operation);
        }

        Ok(pipeline)
    }

    /// Create an operation from configuration
    fn create_operation(config: &OperationConfig) -> Result<Box<dyn Operation>> {
        match config {
            OperationConfig::FillNull { method, columns } => {
                Ok(Box::new(FillNullOperation::new(*method, columns.clone())))
            }
            OperationConfig::Resample {
                rule: _,
                aggregation: _,
                columns: _,
            } => {
                // TODO: Resample operation requires updating to Polars 0.51 API
                // The group_by_dynamic API has changed significantly
                Err(IndustrytsError::InvalidOperation(
                    "Resample operation is not yet implemented for Polars 0.51+".to_string(),
                ))
            }
            OperationConfig::Lag { periods, columns } => Ok(Box::new(LagOperation::new(
                periods.clone(),
                columns.clone(),
            ))),
            OperationConfig::Standardize { columns } => {
                Ok(Box::new(StandardizeOperation::new(columns.clone())))
            }
        }
    }

    /// Add an operation to the pipeline
    pub fn add_operation(&mut self, operation: Box<dyn Operation>) {
        self.operations.push(operation);
    }

    /// Execute the pipeline on time series data
    pub fn process(&self, mut data: TimeSeriesData) -> Result<TimeSeriesData> {
        for operation in &self.operations {
            data = operation.execute(data)?;
        }
        Ok(data)
    }

    /// Get number of operations in the pipeline
    pub fn len(&self) -> usize {
        self.operations.len()
    }

    /// Check if pipeline is empty
    pub fn is_empty(&self) -> bool {
        self.operations.is_empty()
    }

    /// Save pipeline configuration to TOML file
    pub fn to_toml<P: AsRef<Path>>(&self, path: P) -> Result<()> {
        if let Some(config) = &self.config {
            config.to_toml_file(path.as_ref())?;
            Ok(())
        } else {
            Err(IndustrytsError::ConfigError(
                "Pipeline has no configuration to save".to_string(),
            ))
        }
    }
}

impl Default for Pipeline {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_pipeline() {
        let pipeline = Pipeline::new();
        assert_eq!(pipeline.len(), 0);
        assert!(pipeline.is_empty());
    }
}
