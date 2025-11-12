//! Industryts Core Library
//!
//! High-performance time series processing library powered by Polars.

pub mod config;
pub mod core;
pub mod error;
pub mod operations;
pub mod pipeline;
pub mod timeseries;
pub mod utils;

// Re-export main types from core
pub use core::{ExecutionContext, Operation, TimeSeriesData};
pub use config::PipelineConfig;
pub use error::{IndustrytsError, Result};
pub use pipeline::Pipeline;

// Re-export for backward compatibility
pub use pipeline::PipelineBuilder;
