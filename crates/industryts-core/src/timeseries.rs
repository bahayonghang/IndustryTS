//! Time series data structure and operations
//!
//! This module re-exports TimeSeriesData from core for backward compatibility.
//! New code should import from `crate::core` instead.

#[deprecated(since = "0.2.0", note = "Use `crate::core::TimeSeriesData` instead")]
pub use crate::core::TimeSeriesData;
