# Phoenix Rise & Dojo Mental - Development Makefile
.PHONY: help dev build test clean seed migrate docker-up docker-down lint format

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Phoenix Rise & Dojo Mental - Development Commands"
	@echo "================================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }\' $(MAKEFILE_LIST)

# Development
dev: docker-up migrate seed ## Start development environment
	@echo "🚀 Phoenix Rise development environment is ready!"
	@echo "📊 Web App: http://localhost:3000"
	@echo "🔧 API: http://localhost:8000"
	@echo "📧 Mailhog: http://localhost:8025"
	@echo "📈 API Docs: http://localhost:8000/docs"

docker-up: ## Start all services
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 10

docker-down: ## Stop all services
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-clean: ## Stop and remove all containers, networks, and volumes
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Database
migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."
	docker-compose exec api alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Please provide MESSAGE: make migrate-create MESSAGE=\"your description\""; \
		exit 1; \
	fi
	@echo "📝 Creating new migration: $(MESSAGE)"
	docker-compose exec api alembic revision --autogenerate -m "$(MESSAGE)"

migrate-rollback: ## Rollback last migration
	@echo "↩️  Rolling back last migration..."
	docker-compose exec api alembic downgrade -1

seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	docker-compose exec api python scripts/seed_data.py

# Testing
test: test-api test-web ## Run all tests

test-api: ## Run API tests
	@echo "🧪 Running API tests..."
	docker-compose exec api pytest -v --cov=app --cov-report=html

test-web: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	cd apps/web && npm run test

test-e2e: ## Run end-to-end tests
	@echo "🎭 Running E2E tests..."
	cd apps/web && npx playwright test

# Code Quality
lint: lint-api lint-web ## Run all linters

lint-api: ## Lint API code
	@echo "🔍 Linting API code..."
	docker-compose exec api mypy .
	docker-compose exec api flake8 .

lint-web: ## Lint frontend code
	@echo "🔍 Linting frontend code..."
	cd apps/web && npm run lint

format: format-api format-web ## Format all code

format-api: ## Format API code
	@echo "✨ Formatting API code..."
	docker-compose exec api black .

format-web: ## Format frontend code
	@echo "✨ Formatting frontend code..."
	cd apps/web && npm run format

# Build
build: ## Build all services
	@echo "🏗️  Building services..."
	docker-compose build

build-api: ## Build API service
	@echo "🏗️  Building API..."
	docker-compose build api

build-web: ## Build web service
	@echo "🏗️  Building web app..."
	docker-compose build web

# Production
deploy-prepare: ## Prepare for deployment
	@echo "📦 Preparing for deployment..."
	@$(MAKE) test
	@$(MAKE) lint
	@echo "✅ Ready for deployment!"

# Monitoring & Debugging
logs: ## Show all service logs
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-web: ## Show web app logs
	docker-compose logs -f web

logs-db: ## Show database logs
	docker-compose logs -f postgres

shell-api: ## Open shell in API container
	docker-compose exec api bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U phoenix -d phoenix_rise

health: ## Check service health
	@echo "🏥 Checking service health..."
	@echo "API:" && curl -s http://localhost:8000/health | jq '.' || echo "❌ API not responding"
	@echo "Web:" && curl -s http://localhost:3000 > /dev/null && echo "✅ Web responding" || echo "❌ Web not responding"
	@echo "Database:" && docker-compose exec postgres pg_isready -U phoenix && echo "✅ DB responding" || echo "❌ DB not responding"

# Security
security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	docker-compose exec api safety check
	cd apps/web && npm audit

# Cleanup
clean: docker-clean ## Clean up everything
	@echo "🧹 Cleaning up..."
	cd apps/web && rm -rf .next node_modules
	cd apps/api && find . -name "*.pyc" -delete
	cd apps/api && find . -name "__pycache__" -type d -exec rm -rf {} +

# Development utilities
reset-db: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): \" confirm && [ $$confirm = "y" ]
	docker-compose down postgres
	docker volume rm phoenix-rise-monorepo_postgres_data
	@$(MAKE) docker-up migrate seed

install-deps: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	cd apps/web && npm install
	cd apps/api && pip install -r requirements.txt

update-deps: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	cd apps/web && npm update
	cd apps/api && pip install --upgrade -r requirements.txt

# Environment
env-check: ## Check environment variables
	@echo "🔍 Environment check..."
	@cd apps/web && node -e "console.log('Web env OK')\" 2>/dev/null && echo "✅ Web environment" || echo "❌ Web environment"
	@cd apps/api && python -c "from app.core.config import settings; print('✅ API environment')\" 2>/dev/null || echo "❌ API environment"

# Documentation
docs-api: ## Generate API documentation
	@echo "📚 Generating API docs..."
	docker-compose exec api python -c "import app; print('API docs available at http://localhost:8000/docs')"

# Quick commands for common workflows
quick-dev: docker-clean docker-up migrate seed ## Quick development setup (clean start)
	@echo "🏃 Quick dev setup complete!"

quick-test: ## Quick test run
	@$(MAKE) test-api
	@echo "✅ Quick tests passed!"

quick-lint: ## Quick lint check
	@$(MAKE) lint-api
	@echo "✅ Code looks good!"

# CI/CD helpers  
ci-test: ## Run tests for CI
	@echo "🤖 Running CI tests..."
	pytest apps/api/tests/ -v --cov=apps/api/app --cov-report=xml
	cd apps/web && npm run test:ci

ci-build: ## Build for CI
	@echo "🤖 Building for CI..."
	docker build -t phoenix-api ./apps/api
	docker build -t phoenix-web ./apps/web