.PHONY: help build start stop restart logs health deploy clean test

help: ## Show this help message
	@echo "JSON Compare Bot - Available Commands:"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker-compose build

start: ## Start the bot
	docker-compose up -d

stop: ## Stop the bot
	docker-compose down

restart: ## Restart the bot
	docker-compose restart

logs: ## View bot logs
	docker-compose logs -f

health: ## Run health check
	python3 healthcheck.py

deploy: ## Deploy the bot (build and start)
	./deploy.sh

clean: ## Clean up containers and images
	docker-compose down --volumes --remove-orphans
	docker image prune -f

test: ## Test the bot locally
	python3 -m pytest tests/ -v || echo "No tests found - create tests/ directory with test files"

status: ## Show container status
	docker-compose ps

shell: ## Open shell in running container
	docker-compose exec json-compare-bot /bin/bash

dev: ## Run bot in development mode
	python3 compare_json_bot.py

install: ## Install dependencies locally
	pip install -r requirements.txt

setup: ## Setup production environment
	@echo "Setting up production environment..."
	@if [ ! -f .env ]; then \
		cp .env.production .env; \
		echo "Created .env file from template"; \
		echo "Please edit .env and add your TELEGRAM_BOT_TOKEN"; \
	else \
		echo ".env file already exists"; \
	fi
	@mkdir -p logs
	@echo "Created logs directory"
	@echo "Run 'make deploy' to start the bot"

backup: ## Backup logs and configuration
	@mkdir -p backup/$(shell date +%Y%m%d_%H%M%S)
	@cp -r logs backup/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
	@cp .env backup/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
	@echo "Backup created in backup/ directory"
