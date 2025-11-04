//! Pipeline configuration structures

use serde::{Deserialize, Serialize};

/// Pipeline configuration loaded from TOML
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct PipelineConfig {
    pub pipeline: PipelineMetadata,
    pub operations: Vec<OperationConfig>,
}

/// Pipeline metadata
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct PipelineMetadata {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_column: Option<String>,
}

/// Configuration for a single operation
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum OperationConfig {
    FillNull {
        method: FillMethod,
        #[serde(skip_serializing_if = "Option::is_none")]
        columns: Option<Vec<String>>,
    },
    Resample {
        rule: String,
        aggregation: AggMethod,
        #[serde(skip_serializing_if = "Option::is_none")]
        columns: Option<Vec<String>>,
    },
    Lag {
        periods: Vec<i32>,
        #[serde(skip_serializing_if = "Option::is_none")]
        columns: Option<Vec<String>>,
    },
    Standardize {
        #[serde(skip_serializing_if = "Option::is_none")]
        columns: Option<Vec<String>>,
    },
    // Add more operation types as needed
}

/// Fill method for handling null values
#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum FillMethod {
    Forward,
    Backward,
    Mean,
    Zero,
}

/// Aggregation method
#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum AggMethod {
    Mean,
    Sum,
    Min,
    Max,
    First,
    Last,
    Count,
}

impl PipelineConfig {
    /// Load configuration from TOML string
    pub fn from_toml_str(s: &str) -> crate::Result<Self> {
        toml::from_str(s).map_err(Into::into)
    }

    /// Load configuration from TOML file
    pub fn from_toml_file(path: &std::path::Path) -> crate::Result<Self> {
        let contents = std::fs::read_to_string(path)?;
        Self::from_toml_str(&contents)
    }

    /// Serialize to TOML string
    pub fn to_toml_string(&self) -> crate::Result<String> {
        toml::to_string_pretty(self)
            .map_err(|e| crate::IndustrytsError::ConfigError(format!("Failed to serialize: {}", e)))
    }

    /// Save to TOML file
    pub fn to_toml_file(&self, path: &std::path::Path) -> crate::Result<()> {
        let content = self.to_toml_string()?;
        std::fs::write(path, content)?;
        Ok(())
    }
}
