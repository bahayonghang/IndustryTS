//! Time series operations module
//!
//! This module provides various operations for time series data processing organized by category:
//! - data_quality: data cleaning and validation
//! - temporal: time-based operations
//! - features: feature engineering operations
//! - transform: data transformation operations

pub mod data_quality;
pub mod features;
pub mod temporal;
pub mod transform;

// Re-export all operations for backward compatibility
pub use data_quality::FillNullOperation;
pub use features::LagOperation;
pub use transform::*;
