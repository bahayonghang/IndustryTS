# Makefile for Industryts development

.PHONY: help develop build test typecheck clean lint format

help:  ## Show this help message
	@echo "Industryts Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

develop:  ## Install package in development mode (fast compile, debug symbols)
	@echo "Installing in development mode..."
	uv run maturin develop

build:  ## Build release wheel
	@echo "Building release wheel..."
	uv run maturin build --release

build-docker:  ## Build manylinux2014 wheel in Docker (for distribution)
	@echo "Building manylinux2014 wheel..."
	docker run --rm -v $(PWD):/io \
		quay.io/pypa/manylinux2014_x86_64 \
		sh -c "cd /io && maturin build --release --manylinux 2014"

test:  ## Run all tests (Rust + Python)
	@echo "Running Rust tests..."
	cargo test --workspace
	@echo "Running Python tests..."
	uv run pytest py-industryts/tests -v

test-rust:  ## Run only Rust tests
	cargo test --workspace

test-python:  ## Run only Python tests
	uv run pytest py-industryts/tests -v

typecheck:  ## Run type checkers (mypy + pyright)
	@echo "Running mypy..."
	uv run mypy py-industryts/industryts
	@echo "Running pyright..."
	uv run pyright py-industryts/industryts

lint:  ## Run linters (clippy for Rust, ruff for Python)
	@echo "Running clippy..."
	cargo clippy --workspace -- -D warnings
	@echo "Running ruff..."
	uv run ruff check py-industryts/industryts

format:  ## Format code (rustfmt + ruff)
	@echo "Formatting Rust code..."
	cargo fmt --all
	@echo "Formatting Python code..."
	uv run ruff format py-industryts/industryts

clean:  ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	cargo clean
	rm -rf target/
	rm -rf py-industryts/industryts/*.so
	rm -rf py-industryts/industryts/*.pyd
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

bench:  ## Run benchmarks
	@echo "Running Rust benchmarks..."
	cargo bench
	@echo "Running Python benchmarks..."
	uv run pytest py-industryts/tests --benchmark-only

docs-install:  ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	cd docs && npm install

docs-dev:  ## Start VitePress development server
	@echo "Starting VitePress development server..."
	cd docs && npm run docs:dev

docs-build:  ## Build VitePress documentation for production
	@echo "Building VitePress documentation..."
	cd docs && npm run docs:build

docs-preview:  ## Preview built documentation
	@echo "Previewing documentation..."
	cd docs && npm run docs:preview

doc: docs-build  ## Alias for docs-build (for backward compatibility)

.DEFAULT_GOAL := help
