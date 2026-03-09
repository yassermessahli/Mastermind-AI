.PHONY: install pre-push ci-local lint format typecheck test test-unit test-cov train evaluate serve docker-build

install:
	uv sync --all-groups

pre-push:
	uv run ruff check .
	@if find mastermind/ -name "*.py" | grep -q .; then uv run mypy mastermind/; else echo "mypy: no sources, skipping"; fi
	@uv run pytest tests/unit tests/integration; ec=$$?; [ $$ec -eq 0 ] || [ $$ec -eq 5 ]

ci-local:  ## lint only — typecheck/test jobs need 3 GB of ML deps, too heavy for act containers
	act push -j lint

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
