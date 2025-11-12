//! Operation registry for dynamic operation registration and discovery
//!
//! This module provides a registry for operations, allowing dynamic registration
//! and discovery of operations at runtime.

use crate::core::{Operation, OperationCategory};
use crate::error::Result;
use std::collections::HashMap;

/// Factory function for creating operations
pub type OperationFactory = fn() -> Box<dyn Operation>;

/// Information about a registered operation
#[derive(Clone)]
pub struct OperationInfo {
    /// Name of the operation
    pub name: String,
    /// Category of the operation
    pub category: OperationCategory,
    /// Description of the operation
    pub description: String,
    /// Factory function to create the operation
    pub factory: OperationFactory,
}

/// Registry for operations
pub struct OperationRegistry {
    operations: HashMap<String, OperationInfo>,
}

impl OperationRegistry {
    /// Create a new operation registry
    pub fn new() -> Self {
        Self {
            operations: HashMap::new(),
        }
    }

    /// Register an operation
    pub fn register(
        &mut self,
        name: String,
        category: OperationCategory,
        description: String,
        factory: OperationFactory,
    ) {
        let info = OperationInfo {
            name: name.clone(),
            category,
            description,
            factory,
        };
        self.operations.insert(name, info);
    }

    /// Get an operation by name
    pub fn get(&self, name: &str) -> Option<&OperationInfo> {
        self.operations.get(name)
    }

    /// Create an operation by name
    pub fn create(&self, name: &str) -> Result<Box<dyn Operation>> {
        self.get(name)
            .map(|info| (info.factory)())
            .ok_or_else(|| {
                crate::IndustrytsError::InvalidOperation(format!("Operation not found: {}", name))
            })
    }

    /// List all registered operations
    pub fn list_all(&self) -> Vec<&OperationInfo> {
        self.operations.values().collect()
    }

    /// List operations by category
    pub fn list_by_category(&self, category: OperationCategory) -> Vec<&OperationInfo> {
        self.operations
            .values()
            .filter(|info| info.category == category)
            .collect()
    }

    /// Check if an operation is registered
    pub fn contains(&self, name: &str) -> bool {
        self.operations.contains_key(name)
    }

    /// Get the number of registered operations
    pub fn len(&self) -> usize {
        self.operations.len()
    }

    /// Check if the registry is empty
    pub fn is_empty(&self) -> bool {
        self.operations.is_empty()
    }
}

impl Default for OperationRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_registry_creation() {
        let registry = OperationRegistry::new();
        assert_eq!(registry.len(), 0);
        assert!(registry.is_empty());
    }

    #[test]
    fn test_registry_register_and_get() {
        let mut registry = OperationRegistry::new();

        // Create a dummy operation factory
        fn dummy_factory() -> Box<dyn Operation> {
            struct DummyOp;
            impl Operation for DummyOp {
                fn execute(
                    &self,
                    data: crate::core::TimeSeriesData,
                ) -> Result<crate::core::TimeSeriesData> {
                    Ok(data)
                }
                fn name(&self) -> &str {
                    "dummy"
                }
            }
            Box::new(DummyOp)
        }

        registry.register(
            "dummy".to_string(),
            OperationCategory::Transform,
            "A dummy operation".to_string(),
            dummy_factory,
        );

        assert_eq!(registry.len(), 1);
        assert!(registry.contains("dummy"));

        let info = registry.get("dummy").unwrap();
        assert_eq!(info.name, "dummy");
        assert_eq!(info.category, OperationCategory::Transform);
    }

    #[test]
    fn test_registry_list_by_category() {
        let mut registry = OperationRegistry::new();

        fn dummy_factory() -> Box<dyn Operation> {
            struct DummyOp;
            impl Operation for DummyOp {
                fn execute(
                    &self,
                    data: crate::core::TimeSeriesData,
                ) -> Result<crate::core::TimeSeriesData> {
                    Ok(data)
                }
                fn name(&self) -> &str {
                    "dummy"
                }
            }
            Box::new(DummyOp)
        }

        registry.register(
            "op1".to_string(),
            OperationCategory::Transform,
            "Op 1".to_string(),
            dummy_factory,
        );

        registry.register(
            "op2".to_string(),
            OperationCategory::DataQuality,
            "Op 2".to_string(),
            dummy_factory,
        );

        let transform_ops = registry.list_by_category(OperationCategory::Transform);
        assert_eq!(transform_ops.len(), 1);

        let quality_ops = registry.list_by_category(OperationCategory::DataQuality);
        assert_eq!(quality_ops.len(), 1);
    }
}
