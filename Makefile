.PHONY: help install dev build test clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  dev         - Start development servers"
	@echo "  build       - Build the application"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up build artifacts"
	@echo "  docker-build - Build Docker containers"
	@echo "  docker-up   - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"

install:
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	docker-compose up --build

build:
	cd frontend && npm run build

test:
	python -m pytest backend/tests/
	cd frontend && npm test

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	cd frontend && rm -rf .next node_modules
	docker system prune -f

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

setup-env:
	cp .env.example .env
	@echo "Please edit .env file with your configuration"