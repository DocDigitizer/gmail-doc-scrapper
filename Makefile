# Makefile for Gmail Document Scraper

.PHONY: help install test lint format clean docker-build docker-run

# Default target
help:
	@echo "Gmail Document Scraper - Available commands:"
	@echo ""
	@echo "  make install       - Install dependencies and setup environment"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Clean temporary files and caches"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker"
	@echo "  make run           - Run the application (set args with ARGS=...)"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt
	python -m spacy download pt_core_news_lg
	@echo "✓ Installation complete"

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=term --cov-report=html
	@echo "✓ Tests complete. See htmlcov/index.html for coverage report"

# Lint code
lint:
	flake8 src/ tests/ --max-line-length=100
	@echo "✓ Linting complete"

# Format code
format:
	black src/ tests/ main.py
	@echo "✓ Code formatted"

# Clean temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	@echo "✓ Cleaned temporary files"

# Docker build
docker-build:
	docker-compose build
	@echo "✓ Docker image built"

# Docker run
docker-run:
	@echo "Running with Docker..."
	@echo "Example: make docker-run ARGS='--start-date 2024-01-01 --end-date 2024-12-31'"
	docker-compose run --rm gmail-scraper $(ARGS)

# Run application
run:
	python main.py $(ARGS)

# Setup development environment
dev-setup: install
	pip install pytest pytest-cov black flake8 pre-commit
	@echo "✓ Development environment ready"

# Run application with default date (last 30 days)
quick-run:
	python main.py --start-date $$(date -d "30 days ago" +%Y-%m-%d) --dry-run

# Check code quality
check: lint test
	@echo "✓ All checks passed"
