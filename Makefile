.PHONY: help install dev build test clean docker-build docker-up docker-down backend frontend

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
	pip3 install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development environment..."
	@echo "Note: Install Docker to use 'make docker-dev' for full containerized development"
	@echo "Starting backend and frontend separately..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo ""
	@echo "Run 'make backend' in one terminal and 'make frontend' in another"

docker-dev:
	docker-compose up --build

backend:
	cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

test:
	python3 -m pytest backend/tests/
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