# Justfile for IndustryTS Project
# ================================
# A Rust-Python hybrid project for high-performance industry data processing
#
# QUICK START:
#   just              - Show all available commands
#   just setup        - Initialize development environment
#   just dev          - Build in development mode
#   just test         - Run all tests
#   just ci           - Run full CI pipeline
#
# BUILD COMMANDS:
#   just build        - Build wheel package (release mode)
#   just dev          - Build in development mode (faster, unoptimized)
#   just release      - Build optimized release version
#   just manylinux    - Build manylinux2014 wheel for distribution
#   just sync         - Build and install wheel to .venv
#
# TESTING & QUALITY:
#   just test         - Run Rust tests
#   just test-rust    - Run Rust tests only
#   just test-python  - Run Python tests (requires installed package)
#   just check        - Check Rust code (cargo check + clippy)
#   just typecheck    - Type check Python code (mypy + pyright)
#   just lint         - Lint both Rust and Python code
#   just ci           - Full CI workflow (check + test + typecheck)
#
# DEVELOPMENT:
#   just fmt          - Format Rust and Python code
#   just example      - Run example script
#   just quick        - Quick rebuild and test cycle
#   just watch        - Watch mode (rebuild on file changes)
#   just info         - Show project info and structure
#
# MAINTENANCE:
#   just clean        - Clean all build artifacts
#   just setup        - Setup development environment
#
# For more details on each command, run: just --list

# Default recipe to display help
default:
    @just --list

# Build the wheel package (release mode)
# Outputs wheel files to target/wheels/
build:
    @echo "🔨 Building wheel package..."
    uv sync --all-extras
    @rm -rf target/wheels/*.whl 2>/dev/null || true
    uv run maturin build --release --skip-auditwheel
    @echo "✅ Build complete! Wheel files are in target/wheels/"

# Build and install wheel to .venv (one-step build+install)
# Useful for testing the packaged version locally
sync: build
    @echo "📦 Installing wheel to .venv..."
    uv pip install --force-reinstall target/wheels/*.whl
    @echo "✅ Package installed to .venv!"

# Quick development build (faster, unoptimized)
# Use this for rapid iteration during development
# Installs in editable mode via maturin develop
dev:
    @echo "🚀 Installing in development mode..."
    uv sync --all-extras
    uv run maturin develop
    @echo "✅ Development build complete!"

# Build optimized release version with stripping
# Use this for production builds with maximum optimization
release:
    @echo "🎯 Building optimized release..."
    uv sync --all-extras
    uv run maturin build --release --strip --skip-auditwheel
    @echo "✅ Release build complete!"

# Build manylinux2014 wheel for PyPI distribution
# Requires Docker. Creates wheels compatible with most Linux systems
manylinux:
    @echo "🐧 Building manylinux2014 wheel..."
    uv sync --all-extras
    docker run --rm -v $(pwd):/io \
        quay.io/pypa/manylinux2014_x86_64 \
        sh -c "cd /io && maturin build --release --manylinux 2014"
    @echo "✅ Manylinux wheel built!"

# Clean all build artifacts and cache files
# Removes: target/, __pycache__/, .pytest_cache/, .mypy_cache/, etc.
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf target/
    rm -rf py-industryts/target/
    rm -rf **/__pycache__/
    rm -rf **/*.pyc
    rm -rf **/*.so
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    @echo "✅ Cleaned!"

# Run Rust unit and integration tests
# Runs: cargo test for industryts-core only (excludes Python bindings)
test-rust:
    @echo "🧪 Running Rust tests..."
    cargo test --manifest-path crates/industryts-core/Cargo.toml --lib

# Run Python tests with pytest
# Requires: package to be installed (run 'just dev' or 'just sync' first)
test-python:
    @echo "🧪 Running Python tests..."
    uv run pytest tests/ -v

# Run all tests (Rust + Python)
# Runs Rust tests and displays completion message
test: test-rust
    @echo "✅ All tests passed!"

# Type check Python code with mypy and pyright
# Uses strict mode for comprehensive checking
typecheck:
    @echo "🔍 Type checking with mypy..."
    uv run mypy py-industryts/industryts --strict
    @echo "🔍 Type checking with pyright..."
    uv run pyright py-industryts/industryts
    @echo "✅ Type checking passed!"

# Check Rust code with cargo check and clippy
# Clippy warnings are treated as errors (-D warnings)
# Only checks industryts-core (excludes Python bindings)
check:
    @echo "🔍 Checking Rust code..."
    cargo check --manifest-path crates/industryts-core/Cargo.toml
    cargo clippy --manifest-path crates/industryts-core/Cargo.toml -- -D warnings
    @echo "✅ Rust checks passed!"

# Format Rust and Python code
# Rust: cargo fmt, Python: ruff format
fmt:
    @echo "✨ Formatting Rust code..."
    cargo fmt --all
    @echo "✨ Formatting Python code..."
    uv run ruff format py-industryts/
    @echo "✅ Code formatted!"

# Lint Rust and Python code
# Rust: cargo clippy, Python: ruff check
# Only lints industryts-core (excludes Python bindings)
lint:
    @echo "🔍 Linting Rust code..."
    cargo clippy --manifest-path crates/industryts-core/Cargo.toml
    @echo "🔍 Linting Python code..."
    uv run ruff check py-industryts/
    @echo "✅ Linting complete!"

# Run example script to demonstrate functionality
# Location: examples/basic_usage.py
example:
    @echo "📝 Running example script..."
    uv run python examples/basic_usage.py

# Full CI workflow: check → test → typecheck → lint
# Mirrors GitHub CI: rust-check + python-lint + python-test
# Run this before committing to ensure all checks pass
ci: check test lint typecheck
    @echo "✅ All CI checks passed!"

# Setup development environment (one-time setup)
# Installs uv (if needed), dependencies, and builds in dev mode
setup:
    @echo "🔧 Setting up development environment..."
    @echo "Installing uv if not already installed..."
    @command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
    @echo "Installing development dependencies..."
    uv sync
    @echo "Building package in development mode..."
    uv run maturin develop
    @echo "✅ Development environment ready!"

# Show project information and structure
# Displays versions of Rust, Cargo, Python, uv, and project tree
info:
    @echo "📊 Project Information"
    @echo "======================"
    @echo "Rust version: $(rustc --version)"
    @echo "Cargo version: $(cargo --version)"
    @echo "Python version: $(python --version)"
    @echo "uv version: $(uv --version)"
    @echo ""
    @echo "Project structure:"
    @tree -L 2 -I 'target|__pycache__|*.pyc|.git'

# Quick rebuild and test cycle (dev build + example)
# Useful for rapid testing during development
quick: dev example
    @echo "✅ Quick test cycle complete!"

# Watch mode - rebuild on file changes
# Requires: cargo-watch (install with: cargo install cargo-watch)
# Watches for changes and runs: cargo check + just dev
watch:
    @echo "👀 Watching for changes..."
    cargo watch -x "check --workspace" -s "just dev"
