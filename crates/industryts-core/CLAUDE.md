# industryts-core - Rust Core Library

[Root Directory](../../CLAUDE.md) > [crates](../) > **industryts-core**

**Last Updated:** 2025-11-04 14:47:17 CST

---

## Change Log

### 2025-11-04 14:47:17 CST
- Initial module documentation created
- Documented core data structures and operation implementations
- Identified implemented operations: fill_null, lag, standardize
- Noted pending work: resample operation (Polars 0.51 API migration)

---

## Module Responsibilities

`industryts-core` is the pure Rust core library providing high-performance time series processing capabilities. It defines the fundamental data structures, operation trait, and implementations for all time series operations. This module has **no Python dependencies** and can be used standalone in Rust projects.

**Core Responsibilities:**
- Define `TimeSeriesData` struct wrapping Polars DataFrame
- Implement `Operation` trait for composable transformations
- Provide concrete operation implementations (cleaning, features, transforms)
- Parse and validate TOML pipeline configurations
- Orchestrate multi-step pipelines via `Pipeline` struct
- Handle errors with domain-specific error types

**Not Responsible For:**
- Python bindings (handled by `py-industryts/src/`)
- Python API design (handled by `py-industryts/industryts/`)
- I/O beyond basic TOML parsing (delegated to Polars)

---

## Entry and Startup

### Library Entry Point

**File:** `src/lib.rs`

The library exposes the following public modules:
```rust
pub mod error;          // Error types and Result alias
pub mod timeseries;     // TimeSeriesData struct
pub mod pipeline;       // Pipeline and Operation trait
pub mod config;         // TOML configuration structures
pub mod operations;     // Operation implementations
pub mod utils;          // Utility functions
```

**Primary Types Re-exported:**
- `IndustrytsError`, `Result` - Error handling
- `TimeSeriesData` - Core data structure
- `Pipeline`, `Operation` - Pipeline orchestration
- `PipelineConfig` - Configuration parsing

### Usage Example

```rust
use industryts_core::{TimeSeriesData, Pipeline};
use polars::prelude::*;

// Create time series data
let df = df! {
    "DateTime" => &[...],
    "temperature" => &[...],
}.unwrap();
let ts_data = TimeSeriesData::new(df, None)?;

// Load and execute pipeline
let pipeline = Pipeline::from_toml("config.toml")?;
let result = pipeline.process(ts_data)?;
```

---

## External Interfaces

### Public API Surface

#### Core Data Structure

**`TimeSeriesData` (src/timeseries.rs)**
- `new(df: DataFrame, time_column: Option<&str>) -> Result<Self>` - Create with auto-detection
- `dataframe() -> &DataFrame` - Immutable access to underlying data
- `dataframe_mut() -> &mut DataFrame` - Mutable access
- `time_column() -> &str` - Get time column name
- `feature_columns() -> &[String]` - Get feature column names
- `into_dataframe(self) -> DataFrame` - Consume and extract DataFrame
- `len() -> usize`, `is_empty() -> bool` - Size queries

**Auto-Detection Logic:**
- Time column detection tries: `DateTime`, `datetime`, `tagTime`, `tagtime`, `timestamp`, `Timestamp`, `time`, `Time`, `date`, `Date`
- Falls back to first column if no match
- Validates column is `DataType::Date` or `DataType::Datetime`

#### Pipeline System

**`Pipeline` (src/pipeline.rs)**
- `new() -> Self` - Create empty pipeline
- `from_toml<P: AsRef<Path>>(path: P) -> Result<Self>` - Load from TOML config
- `add_operation(&mut self, operation: Box<dyn Operation>)` - Add operation
- `process(&self, data: TimeSeriesData) -> Result<TimeSeriesData>` - Execute pipeline
- `to_toml<P: AsRef<Path>>(&self, path: P) -> Result<()>` - Save config
- `len() -> usize`, `is_empty() -> bool` - Pipeline size

**`Operation` Trait (src/pipeline.rs)**
```rust
pub trait Operation: Send + Sync {
    fn execute(&self, data: TimeSeriesData) -> Result<TimeSeriesData>;
    fn name(&self) -> &str;
}
```

All operations must be thread-safe (`Send + Sync`) for future parallel execution.

#### Configuration

**`PipelineConfig` (src/config.rs)**
- `from_toml_str(s: &str) -> Result<Self>` - Parse TOML string
- `from_toml_file(path: &Path) -> Result<Self>` - Load from file
- `to_toml_string(&self) -> Result<String>` - Serialize to TOML
- `to_toml_file(&self, path: &Path) -> Result<()>` - Save to file

**TOML Structure:**
```toml
[pipeline]
name = "pipeline_name"
time_column = "DateTime"  # optional

[[operations]]
type = "fill_null"
method = "forward"
columns = ["col1", "col2"]  # optional
```

---

## Key Dependencies and Configuration

### Cargo.toml Dependencies

**Core Dependencies:**
- `polars = "0.51"` - DataFrame operations (features: `lazy`, `temporal`, `dtype-datetime`, `dtype-date`)
- `serde = "1.0"` (with `derive`) - Serialization for config
- `toml = "0.8"` - TOML parsing
- `thiserror = "2.0"` - Error derivation
- `anyhow = "1.0"` - Error context
- `rayon = "1.10"` - Parallel iterators (future use)

**Dev Dependencies:**
- `criterion = "0.5"` - Benchmarking framework

### Build Configuration

**Release Profile (workspace-level):**
```toml
[profile.release]
lto = "fat"              # Link-time optimization
codegen-units = 1        # Single codegen unit for max optimization
opt-level = 3            # Maximum optimization
strip = true             # Strip symbols
```

**Development Profile:**
```toml
[profile.dev]
opt-level = 0            # Fast compilation
debug = true             # Debug symbols
```

### Feature Flags

Currently no feature flags. Future considerations:
- Optional SIMD acceleration
- Parallel processing via `rayon`
- Optional operations (reduce binary size)

---

## Data Models

### Core Structures

#### TimeSeriesData

**File:** `src/timeseries.rs`

```rust
pub struct TimeSeriesData {
    df: DataFrame,                    // Polars DataFrame
    time_column: String,              // Name of time index column
    feature_columns: Vec<String>,     // Non-time columns
}
```

**Invariants:**
- `time_column` must exist in `df` and have `Date` or `Datetime` type
- `feature_columns` = all columns except `time_column`
- DataFrame can be empty, but structure is validated on construction

**Memory Layout:**
- Polars uses columnar storage (Arrow format)
- Time column typically `DateTime<TimeUnit, Tz>`
- Feature columns can be any Polars type (typically numeric)

#### Operation Implementations

**FillNullOperation (src/operations/cleaning.rs)**
```rust
pub struct FillNullOperation {
    method: FillMethod,               // Forward/Backward/Mean/Zero
    columns: Option<Vec<String>>,     // None = all features
}
```

**LagOperation (src/operations/features.rs)**
```rust
pub struct LagOperation {
    periods: Vec<i32>,                // Lag periods (positive = backward)
    columns: Option<Vec<String>>,     // None = all features
}
```

**StandardizeOperation (src/operations/transform.rs)**
```rust
pub struct StandardizeOperation {
    columns: Option<Vec<String>>,     // None = all features
}
```

### Configuration Enums

**File:** `src/config.rs`

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum OperationConfig {
    FillNull { method: FillMethod, columns: Option<Vec<String>> },
    Resample { rule: String, aggregation: AggMethod, columns: Option<Vec<String>> },
    Lag { periods: Vec<i32>, columns: Option<Vec<String>> },
    Standardize { columns: Option<Vec<String>> },
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum FillMethod {
    Forward, Backward, Mean, Zero,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AggMethod {
    Mean, Sum, Min, Max, First, Last, Count,
}
```

---

## Testing and Quality

### Current Test Status

**Inline Unit Tests:**
- `timeseries.rs`: Tests time column detection, feature column extraction
- `cleaning.rs`: Tests forward fill operation
- Total inline tests: ~3 test functions

**Coverage Gaps:**
- No integration tests in `tests/` directory
- Missing tests for:
  - LagOperation edge cases
  - StandardizeOperation with NaN/Inf values
  - Pipeline with multiple operations
  - Config parsing error cases
  - Error propagation scenarios

### Recommended Testing Strategy

**Unit Tests (inline with `#[cfg(test)]`):**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_edge_case() {
        // Test implementation
    }
}
```

**Integration Tests (`tests/*.rs`):**
- `tests/pipeline_integration.rs` - End-to-end pipeline tests
- `tests/config_parsing.rs` - TOML parsing and validation
- `tests/operations_chain.rs` - Multi-operation workflows

**Benchmarks (`benches/*.rs` with Criterion):**
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_lag_operation(c: &mut Criterion) {
    c.bench_function("lag_1M_rows", |b| {
        b.iter(|| /* benchmark code */);
    });
}

criterion_group!(benches, benchmark_lag_operation);
criterion_main!(benches);
```

### Quality Tools

**Linting:**
```bash
cargo clippy --workspace -- -D warnings
```

**Formatting:**
```bash
cargo fmt --all
```

**Tests:**
```bash
cargo test --workspace
```

**Documentation:**
```bash
cargo doc --no-deps --open
```

---

## Frequently Asked Questions

### Q: Why is resample operation not implemented?

A: The Polars `group_by_dynamic` API changed significantly in version 0.51. The operation needs to be migrated to the new API. See comments in `src/operations/time.rs` and `src/pipeline.rs`.

### Q: How do I add a new operation?

1. Create struct in `src/operations/<category>.rs` (or new file)
2. Implement `Operation` trait with `execute()` and `name()`
3. Add variant to `OperationConfig` enum in `src/config.rs`
4. Update `Pipeline::create_operation()` to construct your operation
5. Add tests
6. Update this CLAUDE.md

### Q: Can operations modify the time column?

A: Yes, but it's discouraged. Most operations should only modify feature columns. If you need to transform time, create a new column and use `TimeSeriesData::new()` with the new time column name.

### Q: How does error handling work?

A: All fallible operations return `Result<T, IndustrytsError>`. The `?` operator propagates errors up the call stack. External errors (Polars, IO, TOML) are automatically converted to `IndustrytsError` via `From` implementations in `src/error.rs`.

### Q: Why use Polars instead of ndarray or custom structures?

A: Polars provides:
- Efficient columnar storage (Arrow format)
- Lazy evaluation for optimization
- Rich API for time series operations
- Interoperability with Python ecosystem via PyArrow
- Better performance than ndarray for many operations

### Q: Are operations executed in parallel?

A: Not yet. Operations are executed sequentially. Future versions may use `rayon` for parallel execution when operations are independent. The `Operation` trait requires `Send + Sync` in preparation for this.

---

## Related File List

### Source Files (src/)
- `lib.rs` - Library entry point, module exports
- `error.rs` - Error types (`IndustrytsError` enum, `Result` alias)
- `timeseries.rs` - `TimeSeriesData` struct and methods
- `pipeline.rs` - `Pipeline` struct, `Operation` trait
- `config.rs` - TOML configuration structures
- `utils.rs` - Utility functions (currently minimal)

### Operations (src/operations/)
- `mod.rs` - Operations module exports
- `cleaning.rs` - `FillNullOperation` (forward/backward/mean/zero fill)
- `features.rs` - `LagOperation` (lag feature creation)
- `transform.rs` - `StandardizeOperation` (z-score normalization)
- `time.rs` - Time-based operations (resample TODO)

### Configuration
- `Cargo.toml` - Crate configuration and dependencies

### Future Additions
- `tests/` - Integration tests (recommended)
- `benches/` - Criterion benchmarks (recommended)

---

## Module-Specific Conventions

### Naming Conventions
- **Structs:** `PascalCase` ending in `Operation` for operations
- **Functions:** `snake_case` following Rust conventions
- **Constants:** `SCREAMING_SNAKE_CASE`
- **Modules:** `snake_case`

### Code Organization
- Group related operations in same file (e.g., all cleaning operations together)
- Keep operation implementations focused (single responsibility)
- Use builder pattern for complex operations (future)

### Performance Considerations
- Prefer `.clone()` of column references over full DataFrame clones when possible
- Use Polars' expression API for vectorized operations
- Avoid row-by-row iteration
- Consider lazy evaluation for chained operations (future)

### Documentation Standards
- All public items must have `///` doc comments
- Include "Examples" section for non-trivial functions
- Document panics with "# Panics" section
- Document errors with "# Errors" section
- Use code blocks with `rust` language tag

### Error Handling Patterns
```rust
// Good: Use ? for propagation
let column = df.column(name)?;

// Good: Provide context with custom errors
let col = df.column(name)
    .map_err(|_| IndustrytsError::ColumnNotFound(name.to_string()))?;

// Avoid: Unwrapping in library code
let column = df.column(name).unwrap();  // ❌ Don't do this
```

---

## Implementation Notes

### Current Operation Implementations

**Implemented:**
1. **FillNullOperation** - Uses Polars `fill_null()` with strategies
2. **LagOperation** - Uses Polars `shift()` for lag features
3. **StandardizeOperation** - Manual mean/std calculation and normalization

**Pending:**
1. **ResampleOperation** - Needs Polars 0.51 `group_by_dynamic` migration
2. **RollingOperation** - Planned for future release

### Polars API Usage Patterns

**Current Pattern (Polars 0.51):**
```rust
// Getting column
let column = df.column(name)?;
let series = column.as_materialized_series().clone();

// Modifying DataFrame
df.replace(name, new_series)?;

// Adding column
df.with_column(series.with_name(new_name.into()))?;
```

**Deprecated Patterns (avoid):**
- Direct `Series` indexing without materialization
- Old `group_by_dynamic` API (pre-0.51)

### Future Enhancements

**Planned Features:**
- Lazy evaluation support for pipelines
- Parallel operation execution
- Streaming data processing
- Custom operation registration
- Expression-based operation DSL

**Performance Optimizations:**
- SIMD acceleration for numeric operations
- Column pruning in pipelines
- Automatic query optimization
- Memory pooling for large datasets

---

## Next Steps for Development

1. **Implement ResampleOperation** - Migrate to Polars 0.51 API
2. **Add Integration Tests** - Create `tests/` directory with comprehensive tests
3. **Benchmark Suite** - Add `benches/` with performance benchmarks
4. **Documentation** - Generate and publish rustdoc documentation
5. **Error Messages** - Improve error messages with actionable suggestions
