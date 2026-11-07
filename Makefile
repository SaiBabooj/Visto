.PHONY: all dev test lint types clean

all: dev

dev:
	@echo "Starting Voicebridge Gateway and Web..."
	@trap 'kill 0' EXIT; \
	.venv/bin/uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload & \
	pnpm --prefix apps/web dev & \
	wait

test:
	@echo "Running backend test suite..."
	.venv/bin/pytest

lint:
	@echo "Running ruff check..."
	.venv/bin/ruff check .

types:
	@echo "Exporting JSON schemas from Pydantic v2 contracts..."
	.venv/bin/python packages/contracts/src/contracts/export_schema.py
	@echo "Compiling TypeScript interfaces for apps/web..."
	node apps/web/scripts/generate-types.js

clean:
	rm -rf .venv
	rm -rf apps/web/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
