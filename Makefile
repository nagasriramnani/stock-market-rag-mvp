.PHONY: help install api web test docker-build docker-up docker-down clean

help:
	@echo "Available targets:"
	@echo "  install    - Install Python dependencies"
	@echo "  api        - Run FastAPI server"
	@echo "  web        - Run Next.js dev server"
	@echo "  test       - Run tests"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up  - Start services with docker-compose"
	@echo "  docker-down - Stop services"
	@echo "  clean      - Clean cache files"

install:
	pip install -e .

api:
	PYTHONPATH=. uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

web:
	cd apps/web && npm run dev

test:
	pytest -v

docker-build:
	docker-compose -f infra/compose.yaml build

docker-up:
	docker-compose -f infra/compose.yaml up -d

docker-down:
	docker-compose -f infra/compose.yaml down

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +

