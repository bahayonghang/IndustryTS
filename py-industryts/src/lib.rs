//! PyO3 bindings for industryts
//!
//! This module provides Python bindings for the Rust-based industryts library.

use industryts_core::{Pipeline as CorePipeline, TimeSeriesData as CoreTimeSeriesData};
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;

/// Python wrapper for TimeSeriesData
#[pyclass(name = "TimeSeriesData")]
pub struct PyTimeSeriesData {
    inner: CoreTimeSeriesData,
}

#[pymethods]
impl PyTimeSeriesData {
    /// Create a new TimeSeriesData from a Polars DataFrame
    #[new]
    #[pyo3(signature = (data, time_column=None))]
    pub fn new(data: PyDataFrame, time_column: Option<&str>) -> PyResult<Self> {
        let df = data.into();
        let ts = CoreTimeSeriesData::new(df, time_column)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

        Ok(Self { inner: ts })
    }

    /// Convert to Polars DataFrame
    pub fn to_polars(&self) -> PyDataFrame {
        let df = self.inner.dataframe().clone();
        PyDataFrame(df)
    }

    /// Get the time column name
    #[getter]
    pub fn time_column(&self) -> String {
        self.inner.time_column().to_string()
    }

    /// Get feature column names
    #[getter]
    pub fn feature_columns(&self) -> Vec<String> {
        self.inner.feature_columns().to_vec()
    }

    /// Get number of rows
    pub fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// String representation
    pub fn __repr__(&self) -> String {
        format!(
            "TimeSeriesData(rows={}, time_column='{}', features={})",
            self.inner.len(),
            self.inner.time_column(),
            self.inner.feature_columns().len()
        )
    }
}

/// Python wrapper for Pipeline
#[pyclass(name = "Pipeline")]
pub struct PyPipeline {
    inner: CorePipeline,
}

impl Default for PyPipeline {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl PyPipeline {
    /// Create a new empty pipeline
    #[new]
    pub fn new() -> Self {
        Self {
            inner: CorePipeline::new(),
        }
    }

    /// Load pipeline from TOML file
    #[staticmethod]
    pub fn from_toml(path: &str) -> PyResult<Self> {
        let pipeline = CorePipeline::from_toml(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        Ok(Self { inner: pipeline })
    }

    /// Process time series data through the pipeline
    pub fn process(&self, data: &PyTimeSeriesData) -> PyResult<PyTimeSeriesData> {
        let result = self
            .inner
            .process(data.inner.clone())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        Ok(PyTimeSeriesData { inner: result })
    }

    /// Save pipeline to TOML file
    pub fn to_toml(&self, path: &str) -> PyResult<()> {
        self.inner
            .to_toml(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
    }

    /// Get number of operations
    pub fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// String representation
    pub fn __repr__(&self) -> String {
        format!("Pipeline(operations={})", self.inner.len())
    }
}

/// The _its module - internal Rust bindings
///
/// This module is not meant to be used directly by users.
/// Instead, use the high-level industryts Python API.
#[pymodule]
fn _its(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTimeSeriesData>()?;
    m.add_class::<PyPipeline>()?;
    Ok(())
}
