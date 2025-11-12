//! Pipeline execution engine
//!
//! This module provides the pipeline infrastructure for chaining and executing operations:
//! - `builder`: Fluent API for building pipelines
//! - `executor`: Pipeline execution engine
//! - `registry`: Operation registration and discovery

pub mod builder;
pub mod executor;
pub mod registry;

pub use builder::PipelineBuilder;
pub use executor::Pipeline;
pub use registry::OperationRegistry;
