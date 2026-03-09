.PHONY: install lint format typecheck test test-unit test-cov train evaluate serve docker-build

install:
	uv sync --all-groups

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy mastermind/

test:
	pytest tests/

test-unit:
	pytest tests/unit/

test-cov:
	pytest --cov=mastermind tests/

train:
	python scripts/train.py

evaluate:
	python scripts/evaluate.py

serve:
	python scripts/serve.py

docker-build:
	docker build -f docker/Dockerfile.serve -t mastermind-rl:serve .
