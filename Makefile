.PHONY: install ci-local lint format typecheck test test-unit test-cov train evaluate serve docker-build

install:
	uv sync --all-groups

ci-local:
	act push

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy mastermind/

test:
	uv run pytest tests/

test-unit:
	uv run pytest tests/unit/

test-cov:
	uv run pytest --cov=mastermind tests/

train:
	uv run python scripts/train.py

evaluate:
	uv run python scripts/evaluate.py

serve:
	uv run python scripts/serve.py

docker-build:
	docker build -f docker/Dockerfile.serve -t mastermind-rl:serve .
