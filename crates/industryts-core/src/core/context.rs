//! Execution context for tracking and metrics
//!
//! This module provides execution context that tracks operation execution,
//! performance metrics, and intermediate results.

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Execution metrics for an operation
#[derive(Debug, Clone)]
pub struct OperationMetrics {
    /// Name of the operation
    pub operation_name: String,
    /// Time taken to execute
    pub duration: Duration,
    /// Input row count
    pub input_rows: usize,
    /// Output row count
    pub output_rows: usize,
    /// Input column count
    pub input_columns: usize,
    /// Output column count
    pub output_columns: usize,
}

impl OperationMetrics {
    /// Create new metrics
    pub fn new(operation_name: String) -> Self {
        Self {
            operation_name,
            duration: Duration::ZERO,
            input_rows: 0,
            output_rows: 0,
            input_columns: 0,
            output_columns: 0,
        }
    }

    /// Calculate throughput (rows per second)
    pub fn throughput(&self) -> f64 {
        if self.duration.as_secs_f64() == 0.0 {
            0.0
        } else {
            self.input_rows as f64 / self.duration.as_secs_f64()
        }
    }
}

/// Execution context for tracking pipeline execution
pub struct ExecutionContext {
    /// Execution history (operation metrics)
    metrics: Vec<OperationMetrics>,
    /// Start time of execution
    start_time: Instant,
    /// Custom metadata
    metadata: HashMap<String, String>,
}

impl ExecutionContext {
    /// Create a new execution context
    pub fn new() -> Self {
        Self {
            metrics: Vec::new(),
            start_time: Instant::now(),
            metadata: HashMap::new(),
        }
    }

    /// Record metrics for an operation
    pub fn record_metrics(&mut self, metrics: OperationMetrics) {
        self.metrics.push(metrics);
    }

    /// Get all recorded metrics
    pub fn metrics(&self) -> &[OperationMetrics] {
        &self.metrics
    }

    /// Get total execution time
    pub fn total_duration(&self) -> Duration {
        self.start_time.elapsed()
    }

    /// Get total rows processed
    pub fn total_rows_processed(&self) -> usize {
        self.metrics.iter().map(|m| m.input_rows).next().unwrap_or(0)
    }

    /// Add custom metadata
    pub fn add_metadata(&mut self, key: String, value: String) {
        self.metadata.insert(key, value);
    }

    /// Get custom metadata
    pub fn get_metadata(&self, key: &str) -> Option<&str> {
        self.metadata.get(key).map(|s| s.as_str())
    }

    /// Get all metadata
    pub fn metadata(&self) -> &HashMap<String, String> {
        &self.metadata
    }

    /// Get summary of execution
    pub fn summary(&self) -> ExecutionSummary {
        ExecutionSummary {
            total_operations: self.metrics.len(),
            total_duration: self.total_duration(),
            total_rows_processed: self.total_rows_processed(),
            average_throughput: if self.metrics.is_empty() {
                0.0
            } else {
                self.metrics.iter().map(|m| m.throughput()).sum::<f64>()
                    / self.metrics.len() as f64
            },
        }
    }
}

impl Default for ExecutionContext {
    fn default() -> Self {
        Self::new()
    }
}

/// Summary of execution
#[derive(Debug, Clone)]
pub struct ExecutionSummary {
    /// Total number of operations executed
    pub total_operations: usize,
    /// Total execution time
    pub total_duration: Duration,
    /// Total rows processed
    pub total_rows_processed: usize,
    /// Average throughput (rows per second)
    pub average_throughput: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_operation_metrics_throughput() {
        let mut metrics = OperationMetrics::new("test".to_string());
        metrics.input_rows = 1000;
        metrics.duration = Duration::from_secs(1);

        assert_eq!(metrics.throughput(), 1000.0);
    }

    #[test]
    fn test_execution_context_creation() {
        let ctx = ExecutionContext::new();
        assert_eq!(ctx.metrics().len(), 0);
        // Verify that context was created (total_duration is always non-negative)
        let _ = ctx.total_duration();
    }

    #[test]
    fn test_execution_context_metadata() {
        let mut ctx = ExecutionContext::new();
        ctx.add_metadata("source".to_string(), "sensor".to_string());

        assert_eq!(ctx.get_metadata("source"), Some("sensor"));
    }

    #[test]
    fn test_execution_summary() {
        let mut ctx = ExecutionContext::new();
        let mut metrics = OperationMetrics::new("op1".to_string());
        metrics.input_rows = 1000;
        metrics.duration = Duration::from_secs(1);

        ctx.record_metrics(metrics);

        let summary = ctx.summary();
        assert_eq!(summary.total_operations, 1);
        assert_eq!(summary.total_rows_processed, 1000);
    }
}
