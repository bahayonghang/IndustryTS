# Industryts

[![CI](https://github.com/your-org/industryts/workflows/CI/badge.svg)](https://github.com/your-org/industryts/actions)
[![PyPI](https://img.shields.io/pypi/v/industryts.svg)](https://pypi.org/project/industryts/)
[![Python Version](https://img.shields.io/pypi/pyversions/industryts.svg)](https://pypi.org/project/industryts/)

High-performance time series processing library for industrial data, powered by Rust and Polars.

## Features

- ⚡ **10-100x faster** than pandas for typical time series operations
- 🦀 **Rust-powered** core for type safety and performance
- 🐍 **Python-friendly** API with full type hints
- 📊 **Comprehensive operations**: cleaning, resampling, feature engineering, transformations
- ⚙️ **Declarative pipelines** via TOML configuration
- 🔧 **Dual API**: programmatic (Python) and declarative (TOML)
- 🚀 **Polars-based** for columnar processing and lazy evaluation

## Installation

### Requirements

- **Python**: 3.8+
- **Operating System**: Linux (glibc 2.17+), macOS, Windows
- **Optional**: For large datasets (>4.2B rows), install with `polars[rt64]`

### Install from PyPI

```bash
pip install industryts
```

### Install from source (development)

```bash
# Clone repository
git clone https://github.com/your-org/industryts.git
cd industryts

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install in development mode
uv add maturin --dev
uv run maturin develop
```

## Quick Start

### Programmatic API

```python
import industryts as its

# Load time series data
data = its.TimeSeriesData.from_csv("sensor_data.csv")

# Create processing pipeline
pipeline = its.Pipeline()
pipeline.fill_null(method="forward")
pipeline.resample("1h", agg="mean")
pipeline.lag(columns=["temperature"], periods=[1, 2, 3])
pipeline.standardize(columns=["temperature", "pressure"])

# Process data
result = pipeline.process(data)
result.to_csv("processed_data.csv")
```

### Declarative API (TOML)

**pipeline.toml:**
```toml
[pipeline]
name = "sensor_processing"
time_column = "DateTime"

[[operations]]
type = "fill_null"
method = "forward"

[[operations]]
type = "resample"
rule = "1h"
aggregation = "mean"

[[operations]]
type = "lag"
columns = ["temperature"]
periods = [1, 2, 3]

[[operations]]
type = "standardize"
columns = ["temperature", "pressure"]
```

**Python:**
```python
import industryts as its

# Load pipeline from config
pipeline = its.Pipeline.from_toml("pipeline.toml")

# Process data
data = its.TimeSeriesData.from_csv("sensor_data.csv")
result = pipeline.process(data)
```

## Performance

Benchmarks on a dataset with 1M rows × 10 features:

| Operation | pandas | industryts | Speedup |
|-----------|--------|------------|---------|
| Resample (1h → 1min) | 2.3s | 0.05s | **46x** |
| Rolling mean (window=100) | 1.8s | 0.03s | **60x** |
| Lag features (3 lags) | 1.2s | 0.02s | **60x** |
| Full pipeline (10 ops) | 12.5s | 0.15s | **83x** |

## Operation Categories

### Data Cleaning
- Missing value handling (forward/backward fill, interpolation)
- Outlier detection (IQR, Z-score)
- Duplicate removal

### Time Operations
- Resampling (upsample/downsample)
- Rolling windows (mean, std, min, max, custom)
- Time alignment

### Feature Engineering
- Lag features
- Date/time component extraction
- Differencing
- Cyclical encoding (sin/cos)

### Aggregation
- Group by time bins
- Cumulative operations
- Expanding windows

### Transformations
- Standardization (z-score)
- Min-max scaling
- Log/Box-Cox transforms
- Robust scaling

## Documentation

📚 **[Full Documentation](./docs/)** - Comprehensive guides and API reference

- **[English Documentation](./docs/en/)** - Get started, user guides, API reference, examples
- **[中文文档](./docs/zh/)** - 入门指南、用户手册、API 参考、示例

Quick links:
- [Installation Guide](./docs/en/guide/installation.md) | [安装指南](./docs/zh/guide/installation.md)
- [Quick Start](./docs/en/guide/quick-start.md) | [快速开始](./docs/zh/guide/quick-start.md)
- [API Reference](./docs/en/api/timeseries.md) | [API 参考](./docs/zh/api/timeseries.md)
- [TOML Configuration](./docs/en/guide/toml/structure.md) | [TOML 配置](./docs/zh/guide/toml/structure.md)
- [Examples](./docs/en/examples/basic.md) | [示例](./docs/zh/examples/basic.md)

### Building Documentation

**Option 1: Using just (Recommended)**

```bash
cd docs
just dev      # Auto-install dependencies and start dev server
just build    # Build for production
just --list   # Show all commands
```

**Option 2: Using make**

```bash
# Install documentation dependencies
make docs-install

# Start development server (with live reload)
make docs-dev

# Build for production
make docs-build
```

**Option 3: Using npm directly**

```bash
cd docs
npm install
npm run docs:dev
```

See [docs/README.md](./docs/README.md) for detailed documentation development guide.

## Documentation (Old Links)

The following links point to online documentation (to be deployed):

- [User Guide](https://industryts.readthedocs.io/)
- [API Reference](https://industryts.readthedocs.io/api/)
- [Examples](./examples/)
- [TOML Configuration Reference](https://industryts.readthedocs.io/config/)

## Development

### Building

```bash
# Development build (fast compile)
make develop

# Release build
make build

# Run tests
make test

# Type checking
make typecheck
```

### Project Structure

Following the Polars architecture pattern:

```
industryts/
├── crates/              # Rust crates
│   └── industryts-core/ # Pure Rust core library
├── py-industryts/       # Python bindings (analogous to py-polars)
│   ├── src/             # Rust PyO3 binding code (_its module)
│   └── industryts/      # Python package
├── examples/            # Usage examples
└── docs/                # Documentation
```

## Platform Compatibility

| Platform | Architecture | Minimum glibc | Status |
|----------|--------------|---------------|--------|
| Linux | x86_64 | 2.17 (CentOS 7+) | ✅ Tested |
| Linux | aarch64 | 2.17 | ✅ Tested |
| macOS | x86_64 | N/A | ✅ Tested |
| macOS | arm64 (M1/M2) | N/A | ✅ Tested |
| Windows | x86_64 | N/A | ✅ Tested |

**Note**: Linux wheels are built with manylinux2014 for maximum compatibility.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [Polars](https://www.pola.rs/) for high-performance data processing
- Python bindings via [PyO3](https://pyo3.rs/)
- Build system powered by [Maturin](https://www.maturin.rs/)
