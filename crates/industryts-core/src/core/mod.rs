//! Core abstractions for time series processing
//!
//! This module provides the fundamental abstractions used throughout the library:
//! - `data`: TimeSeriesData structure and metadata
//! - `operation`: Operation trait and base implementations
//! - `context`: Execution context for tracking and metrics

pub mod context;
pub mod data;
pub mod operation;

pub use context::ExecutionContext;
pub use data::TimeSeriesData;
pub use operation::{Operation, OperationCategory, OperationMetadata};
