# Telegram Analytics Bot - Easy Commands
# Usage: make <command>

.PHONY: help install test test-unit test-connectivity test-all lint format clean setup

# Default target
help:
	@echo "🤖 Telegram Analytics Bot - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install      Install dependencies"
	@echo "  make setup        Full setup (install + copy .env.example)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run all internal tests (unit, lint, type)"
	@echo "  make test-unit    Run only unit tests"
	@echo "  make test-unit-v  Run unit tests with verbose output"
	@echo "  make test-cov     Run unit tests with coverage"
	@echo "  make test-conn    Run connectivity tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         Run linting checks"
	@echo "  make format       Format code (black + ruff fix)"
	@echo "  make type         Run type checking"
	@echo ""
	@echo "Authentication:"
	@echo "  make auth         Test Telegram authentication"
	@echo "  make auth-setup   Complete Telegram authentication"
	@echo ""
	@echo "Validation:"
	@echo "  make validate     Validate setup"
	@echo "  make clean        Clean cache and temp files"

# Installation
install:
	@echo "📦 Installing dependencies..."
	uv sync

setup: install
	@echo "🔧 Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env with your Telegram API credentials"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

# Testing
test:
	@echo "🧪 Running all internal tests..."
	uv run python run_tests.py

test-unit:
	@echo "🧪 Running unit tests..."
	uv run python run_tests.py --unit

test-unit-v:
	@echo "🧪 Running unit tests (verbose)..."
	uv run python run_tests.py --unit --verbose

test-cov:
	@echo "🧪 Running unit tests with coverage..."
	uv run python run_tests.py --unit --coverage

test-conn:
	@echo "🌐 Running connectivity tests..."
	uv run python test_connectivity.py

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	uv run python run_tests.py --lint

format:
	@echo "🎨 Formatting code..."
	uv run black src/ tests/ *.py
	uv run ruff check src/ tests/ *.py --fix

type:
	@echo "🔍 Running type checking..."
	uv run python run_tests.py --type

# Authentication
auth:
	@echo "🔐 Testing Telegram authentication..."
	uv run python test_login.py

auth-setup:
	@echo "🔐 Setting up Telegram authentication..."
	uv run python test_login.py --complete

# Validation
validate:
	@echo "✅ Validating setup..."
	uv run python validate_setup.py

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"