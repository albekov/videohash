.PHONY: all lint test

all: lint test

lint:
	uv run ruff format .
	uv run ruff check --fix .
	uv run mypy .

test:
	uv run pytest
