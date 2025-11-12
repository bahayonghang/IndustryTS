//! Pipeline builder with fluent API
//!
//! This module provides a builder pattern for constructing pipelines with a fluent API.

use crate::core::Operation;
use crate::pipeline::executor::Pipeline;

/// Builder for constructing pipelines with a fluent API
pub struct PipelineBuilder {
    operations: Vec<Box<dyn Operation>>,
}

impl PipelineBuilder {
    /// Create a new pipeline builder
    pub fn new() -> Self {
        Self {
            operations: Vec::new(),
        }
    }

    /// Add an operation to the pipeline
    pub fn add_operation(mut self, operation: Box<dyn Operation>) -> Self {
        self.operations.push(operation);
        self
    }

    /// Add an operation to the pipeline (mutable reference)
    pub fn add_operation_mut(&mut self, operation: Box<dyn Operation>) -> &mut Self {
        self.operations.push(operation);
        self
    }

    /// Build the pipeline
    pub fn build(self) -> Pipeline {
        let mut pipeline = Pipeline::new();
        for operation in self.operations {
            pipeline.add_operation(operation);
        }
        pipeline
    }

    /// Get the number of operations in the builder
    pub fn len(&self) -> usize {
        self.operations.len()
    }

    /// Check if the builder is empty
    pub fn is_empty(&self) -> bool {
        self.operations.is_empty()
    }
}

impl Default for PipelineBuilder {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipeline_builder_creation() {
        let builder = PipelineBuilder::new();
        assert_eq!(builder.len(), 0);
        assert!(builder.is_empty());
    }

    #[test]
    fn test_pipeline_builder_build() {
        let builder = PipelineBuilder::new();
        let pipeline = builder.build();
        assert_eq!(pipeline.len(), 0);
    }
}
