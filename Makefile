# Telegram Multi-Agent AI Bot - Makefile
.PHONY: help venv activate install run clean clean-venv clean-all docker-build docker-run docker-stop docker-logs docker-logs-all docker-restart docker-clean docker-dev migrate-to-hf
.PHONY: dev dev-logs dev-stop build prod prod-logs prod-stop restart logs logs-atlas logs-all health status db-shell db-backup test test-logging security-scan setup setup-env up down ps

VENV_NAME=venv
PYTHON=python3
PIP=pip3

# Default target
help: ## Show this help message
	@echo "Telegram Multi-Agent AI Bot - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Virtual Environment Management
venv: ## Create virtual environment
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment '$(VENV_NAME)' created. Run 'source venv/bin/activate' to activate it."

activate: ## Show activation command
	@echo "To activate the virtual environment, run: source venv/bin/activate"

install: venv ## Install dependencies in virtual environment
	. ./$(VENV_NAME)/bin/activate && $(PIP) install -r requirements.txt

run-local: ## Run locally with virtual environment
	@if [ -d "$(VENV_NAME)" ]; then \
		. ./$(VENV_NAME)/bin/activate && python main.py; \
	else \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

# Migration to HuggingFace Embeddings
migrate-to-hf: ## Migrate to HuggingFace embeddings
	@echo "Migrating to HuggingFace Inference API embeddings..."
	@echo "1. Make sure HUGGINGFACE_API_KEY is set in your .env file"
	@echo "2. Get your free API key from: https://huggingface.co/settings/tokens"
	@echo "3. Update your .env file with: HUGGINGFACE_API_KEY=your_key_here"
	@echo "4. Set EMBEDDING_SERVICE=huggingface in your .env file"
	@echo "5. Run 'make docker-clean && make docker-build && make docker-run'"
	@echo "Migration setup complete!"

# Environment Setup
setup: ## Setup environment and directories
	@echo "🚀 Setting up DocExpert Bot environment..."
	@./setup.sh

setup-env: ## Setup environment file only
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.example .env 2>/dev/null || echo "TELEGRAM_BOT_TOKEN=\nXAI_API_KEY=\nHUGGINGFACE_API_KEY=\nLOG_LEVEL=INFO" > .env; \
		echo "✅ .env file created! Please edit it with your API keys."; \
	else \
		echo "✅ .env file already exists!"; \
	fi

# Basic Docker Commands
docker-build: ## Build docker images
	docker-compose build

docker-run: ## Run with docker-compose
	docker-compose up -d

docker-stop: ## Stop docker services
	docker-compose down

docker-logs: ## View bot logs
	docker-compose logs -f llm-telegram-bot

docker-logs-all: ## View all service logs
	docker-compose logs -f

docker-restart: ## Restart bot service
	docker-compose restart llm-telegram-bot

docker-dev: ## Run in development mode
	docker-compose up

docker-clean: ## Clean docker resources
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development Environment Commands
dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build -d
	@echo "✅ Development environment started!"
	@echo "📱 Bot API: http://localhost:8000"
	@echo "🗄️  MongoDB: Using MongoDB Atlas cloud database"

dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Development environment stopped!"

# Production commands
build: ## Build production images
	@echo "🔨 Building production images..."
	docker-compose -f docker-compose.production.yml build --no-cache
	@echo "✅ Production images built!"

prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.production.yml up -d
	@echo "✅ Production environment started!"
	@echo "🌐 Web: http://localhost"
	@echo "📱 Bot API: http://localhost:8000"

prod-logs: ## View production logs
	docker-compose -f docker-compose.production.yml logs -f

prod-stop: ## Stop production environment
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker-compose.production.yml down
	@echo "✅ Production environment stopped!"

# Standard Docker Compose Commands (uses docker-compose.yml)
run: ## Start standard environment (recommended)
	@echo "🚀 Starting application..."
	docker-compose up --build -d
	@echo "✅ Application started!"
	@echo "📱 Bot API: http://localhost:8000"
	@echo "🗄️  MongoDB: Using MongoDB Atlas cloud database"

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped!"

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

# Logging and monitoring
logs: ## View application logs
	docker-compose logs -f llm-telegram-bot

logs-db: ## View application logs (no local DB)
	@echo "⚠️  No local MongoDB container - using MongoDB Atlas cloud"
	@echo "📊 To monitor your MongoDB Atlas cluster:"
	@echo "   1. Visit https://cloud.mongodb.com"
	@echo "   2. Navigate to your cluster"
	@echo "   3. Use the Monitoring tab for metrics and logs"

logs-all: ## View all service logs
	docker-compose logs -f

# Health and status
health: ## Check service health
	@echo "🔍 Checking service health..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Bot API is healthy" || echo "❌ Bot API is unhealthy"
	@docker-compose ps

status: ## Show service status
	docker-compose ps

# Database operations (MongoDB Atlas)
db-shell: ## Access MongoDB Atlas via mongosh
	@echo "🗄️  Connecting to MongoDB Atlas..."
	@if [ -z "$$MONGODB_URI" ]; then \
		echo "❌ MONGODB_URI environment variable not set"; \
		echo "💡 Make sure to source your .env file or set MONGODB_URI"; \
		exit 1; \
	fi
	mongosh "$$MONGODB_URI"

db-backup: ## Backup MongoDB Atlas database
	@echo "💾 Creating MongoDB Atlas backup..."
	@if [ -z "$$MONGODB_URI" ]; then \
		echo "❌ MONGODB_URI environment variable not set"; \
		echo "💡 Make sure to source your .env file or set MONGODB_URI"; \
		exit 1; \
	fi
	@mkdir -p ./backups
	mongodump --uri="$$MONGODB_URI" --out=./backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "✅ Database backup created in ./backups/"

# Security and Testing
security-scan: ## Run security scan on images
	@echo "🔒 Running security scan..."
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
	-v $(HOME)/Library/Caches:/root/.cache/ \
	aquasec/trivy image llm-telegram-bot:latest

test: ## Run tests in container
	@echo "🧪 Running tests..."
	docker-compose exec llm-telegram-bot python -m pytest tests/ -v
	@echo "✅ Tests completed!"

test-logging: ## Test logging system
	@echo "📝 Testing logging system..."
	docker-compose exec llm-telegram-bot python -c "from app.utils.logging import setup_logging; setup_logging(); print('✅ Logging system working!')"

# Quick Aliases
up: run ## Alias for run
down: stop ## Alias for stop  
ps: status ## Alias for status

# Cleanup Commands
clean: ## Clean Python cache files
	@echo "🧹 Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Python cleanup completed!"

clean-venv: clean ## Clean virtual environment
	@echo "🧹 Removing virtual environment..."
	rm -rf $(VENV_NAME)
	@echo "✅ Virtual environment removed!"

clean-all: clean-venv docker-clean ## Clean everything
	@echo "🧹 Complete cleanup finished!"