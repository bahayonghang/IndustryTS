//! Industryts Core Library
//!
//! High-performance time series processing library powered by Polars.

pub mod config;
pub mod error;
pub mod operations;
pub mod pipeline;
pub mod timeseries;
pub mod utils;

// Re-export main types
pub use config::PipelineConfig;
pub use error::{IndustrytsError, Result};
pub use pipeline::{Operation, Pipeline};
pub use timeseries::TimeSeriesData;
