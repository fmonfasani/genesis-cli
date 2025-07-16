# Makefile for Genesis CLI
# DOCTRINA: Solo comandos para desarrollo de interfaz de usuario

.PHONY: help install dev clean test test-cov test-watch lint format type-check security-check docs docs-serve docs-check build publish

# Variables
PYTHON := python
PIP := pip
PACKAGE := genesis_cli
TESTS := tests
DOCS := docs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(BLUE)Genesis CLI - Makefile Commands$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(install|dev|clean)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(test)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(lint|format|type|security)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(docs)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Build & Release:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(build|publish)" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make install          # Install dependencies"
	@echo "  make test             # Run tests"
	@echo "  make lint             # Check code quality"
	@echo "  make format           # Format code"
	@echo "  make docs-serve       # Serve documentation"

# Development targets
install: ## Install dependencies for development
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✅ Installation complete!$(NC)"

dev: install ## Set up development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@echo "$(BLUE)Verifying installation...$(NC)"
	genesis --version
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .tox/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

# Testing targets
test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest $(TESTS) -v

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest $(TESTS) --cov=$(PACKAGE) --cov-report=html --cov-report=term-missing --cov-report=xml

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	pytest-watch $(TESTS) -- -v

test-all: ## Run all tests (unit, integration, CLI)
	@echo "$(GREEN)Running all tests...$(NC)"
	pytest $(TESTS) -v --cov=$(PACKAGE) --cov-report=html --cov-report=term-missing

test-unit: ## Run only unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest $(TESTS) -v -m unit

test-integration: ## Run only integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	pytest $(TESTS) -v -m integration

test-cli: ## Run only CLI tests
	@echo "$(GREEN)Running CLI tests...$(NC)"
	pytest $(TESTS) -v -m cli

# Code quality targets
lint: ## Run all linting checks
	@echo "$(GREEN)Running linting checks...$(NC)"
	@echo "$(BLUE)Checking with flake8...$(NC)"
	flake8 $(PACKAGE) $(TESTS)
	@echo "$(BLUE)Checking with black...$(NC)"
	black --check --diff $(PACKAGE) $(TESTS)
	@echo "$(BLUE)Checking with isort...$(NC)"
	isort --check-only --diff $(PACKAGE) $(TESTS)
	@echo "$(GREEN)✅ Linting passed!$(NC)"

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	@echo "$(BLUE)Formatting with black...$(NC)"
	black $(PACKAGE) $(TESTS)
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	isort $(PACKAGE) $(TESTS)
	@echo "$(GREEN)✅ Code formatted!$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(GREEN)Running type checking...$(NC)"
	mypy $(PACKAGE)
	@echo "$(GREEN)✅ Type checking passed!$(NC)"

security-check: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	@echo "$(BLUE)Checking with bandit...$(NC)"
	bandit -r $(PACKAGE)/
	@echo "$(BLUE)Checking dependencies with safety...$(NC)"
	safety check
	@echo "$(GREEN)✅ Security checks passed!$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks passed!$(NC)"

# Documentation targets
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	@if [ -d "docs" ]; then \
		cd docs && mkdocs build; \
	else \
		echo "$(YELLOW)⚠️  Documentation directory not found$(NC)"; \
	fi

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation locally...$(NC)"
	@if [ -d "docs" ]; then \
		cd docs && mkdocs serve; \
	else \
		echo "$(YELLOW)⚠️  Documentation directory not found$(NC)"; \
		echo "$(BLUE)Starting simple documentation server...$(NC)"; \
		$(PYTHON) -m http.server 8000 -d . & \
		echo "$(GREEN)Documentation served at http://localhost:8000$(NC)"; \
	fi

docs-check: ## Check documentation for issues
	@echo "$(GREEN)Checking documentation...$(NC)"
	@if [ -d "docs" ]; then \
		cd docs && mkdocs build --strict; \
	else \
		echo "$(YELLOW)⚠️  Documentation directory not found$(NC)"; \
	fi

# Build and release targets
build: clean ## Build package
	@echo "$(GREEN)Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Package built successfully!$(NC)"
	@echo "$(BLUE)Generated files:$(NC)"
	@ls -la dist/

publish-test: build ## Publish to TestPyPI
	@echo "$(GREEN)Publishing to TestPyPI...$(NC)"
	$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@echo "$(GREEN)✅ Published to TestPyPI!$(NC)"

publish: build ## Publish to PyPI
	@echo "$(YELLOW)⚠️  Publishing to PyPI...$(NC)"
	@echo "$(RED)This will publish to production PyPI!$(NC)"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m twine upload dist/*; \
		echo "$(GREEN)✅ Published to PyPI!$(NC)"; \
	else \
		echo "$(YELLOW)Publishing cancelled$(NC)"; \
	fi

# Development utilities
check-deps: ## Check for outdated dependencies
	@echo "$(GREEN)Checking for outdated dependencies...$(NC)"
	$(PIP) list --outdated

upgrade-deps: ## Upgrade development dependencies
	@echo "$(GREEN)Upgrading development dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -e ".[dev]"

benchmark: ## Run performance benchmarks
	@echo "$(GREEN)Running performance benchmarks...$(NC)"
	@if [ -f "scripts/benchmark.py" ]; then \
		$(PYTHON) scripts/benchmark.py; \
	else \
		echo "$(YELLOW)⚠️  Benchmark script not found$(NC)"; \
	fi

profile: ## Profile application performance
	@echo "$(GREEN)Profiling application...$(NC)"
	$(PYTHON) -m cProfile -s cumulative -m $(PACKAGE).main init test-project --no-interactive 2>/dev/null

# CI/CD helpers
ci-test: ## Run tests in CI environment
	@echo "$(GREEN)Running CI tests...$(NC)"
	pytest $(TESTS) --cov=$(PACKAGE) --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml

ci-lint: ## Run linting in CI environment
	@echo "$(GREEN)Running CI linting...$(NC)"
	flake8 $(PACKAGE) $(TESTS) --output-file=flake8-report.txt
	black --check $(PACKAGE) $(TESTS)
	isort --check-only $(PACKAGE) $(TESTS)
	mypy $(PACKAGE)

# Database and logs cleanup
clean-logs: ## Clean application logs
	@echo "$(GREEN)Cleaning application logs...$(NC)"
	rm -rf ~/.genesis-cli/logs/*.log
	@echo "$(GREEN)✅ Logs cleaned!$(NC)"

clean-config: ## Clean application configuration
	@echo "$(YELLOW)⚠️  This will remove your Genesis CLI configuration!$(NC)"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ~/.genesis-cli/config.json; \
		echo "$(GREEN)✅ Configuration cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)Cleaning cancelled$(NC)"; \
	fi

# Docker helpers
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t genesis-cli:latest .

docker-run: ## Run in Docker container
	@echo "$(GREEN)Running in Docker container...$(NC)"
	docker run -it --rm genesis-cli:latest

docker-clean: ## Clean Docker images
	@echo "$(GREEN)Cleaning Docker images...$(NC)"
	docker rmi genesis-cli:latest 2>/dev/null || true

# Info and status
info: ## Show project information
	@echo "$(BLUE)Genesis CLI - Project Information$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo "Package: $(PACKAGE)"
	@echo "Tests: $(TESTS)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo ""
	@echo "$(GREEN)Installed packages:$(NC)"
	@$(PIP) list | grep -E "(genesis|typer|rich|pytest|black|isort|mypy|flake8)"
	@echo ""
	@echo "$(GREEN)Project structure:$(NC)"
	@find $(PACKAGE) -name "*.py" | head -10
	@echo ""
	@echo "$(GREEN)Recent commits:$(NC)"
	@git log --oneline -5 2>/dev/null || echo "Not a git repository"

status: ## Show development status
	@echo "$(BLUE)Genesis CLI - Development Status$(NC)"
	@echo "$(BLUE)===============================$(NC)"
	@echo ""
	@echo "$(GREEN)Git status:$(NC)"
	@git status --porcelain 2>/dev/null || echo "Not a git repository"
	@echo ""
	@echo "$(GREEN)Branch:$(NC)"
	@git branch --show-current 2>/dev/null || echo "Not a git repository"
	@echo ""
	@echo "$(GREEN)Last tests:$(NC)"
	@if [ -f ".coverage" ]; then \
		echo "Coverage file exists"; \
	else \
		echo "No coverage file found"; \
	fi
	@echo ""
	@echo "$(GREEN)Virtual environment:$(NC)"
	@echo "VIRTUAL_ENV: $$VIRTUAL_ENV"

# Shortcuts
t: test ## Shortcut for test
tc: test-cov ## Shortcut for test-cov
l: lint ## Shortcut for lint
f: format ## Shortcut for format
c: clean ## Shortcut for clean
i: install ## Shortcut for install
d: docs-serve ## Shortcut for docs-serve
b: build ## Shortcut for build

# Make sure intermediate files are not deleted
.SECONDARY:

# Ensure make doesn't get confused by files with these names
.PHONY: $(MAKECMDGOALS)