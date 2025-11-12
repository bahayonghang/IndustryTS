//! Pipeline execution engine
//!
//! This module provides the main Pipeline struct that executes a sequence of operations.

use crate::config::PipelineConfig;
use crate::core::{ExecutionContext, Operation, TimeSeriesData};
use crate::error::Result;
use std::path::Path;

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
    fn create_operation(config: &crate::config::OperationConfig) -> Result<Box<dyn Operation>> {
        use crate::config::OperationConfig;
        use crate::operations::*;

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
                Err(crate::IndustrytsError::InvalidOperation(
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

    /// Execute the pipeline with execution context tracking
    pub fn process_with_context(
        &self,
        mut data: TimeSeriesData,
        mut context: ExecutionContext,
    ) -> Result<(TimeSeriesData, ExecutionContext)> {
        for operation in &self.operations {
            let input_rows = data.len();
            let input_columns = data.feature_columns().len();

            data = operation.execute(data)?;

            let output_rows = data.len();
            let output_columns = data.feature_columns().len();

            let mut metrics = crate::core::context::OperationMetrics::new(
                operation.name().to_string(),
            );
            metrics.input_rows = input_rows;
            metrics.output_rows = output_rows;
            metrics.input_columns = input_columns;
            metrics.output_columns = output_columns;

            context.record_metrics(metrics);
        }
        Ok((data, context))
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
            Err(crate::IndustrytsError::ConfigError(
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
