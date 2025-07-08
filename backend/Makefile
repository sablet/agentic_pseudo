# Agentic Pseudo Project Makefile

.PHONY: setup test lint format clean dev help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Install dependencies"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run code quality checks"
	@echo "  format    - Format code"
	@echo "  clean     - Clean generated files"
	@echo "  dev       - Full development workflow"

# Setup environment
setup:
	@echo "Setting up development environment..."
	uv sync

# Format code
format:
	uv run --frozen ruff format .

# Lint code
lint:
	uv run --frozen ruff check . --fix
	uv run --frozen ruff format --check .
	uv run --frozen pyright

# Run tests
test:
	uv run --frozen pytest tests/ -v

# Run unit tests
test-unit:
	uv run --frozen pytest tests/unit/ -v

# Run integration tests
test-integration:
	uv run --frozen pytest tests/integration/ -v

# Clean generated files
clean:
	@echo "Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# Development workflow
dev: format lint test
	@echo "Development checks completed"