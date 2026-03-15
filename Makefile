.PHONY: install ci-local lint format typecheck test test-unit test-cov train evaluate serve docker-build backend-serve backend-test frontend-install frontend-dev frontend-build frontend-lint frontend-preview

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

sweep:
	uv run python scripts/sweep.py

evaluate:
	uv run python scripts/evaluate.py model_path=outputs/sweep/rosy-sweep-30/model.zip

serve:
	uv run python scripts/serve.py

docker-build:
	docker build -f docker/Dockerfile.serve -t mastermind-rl:serve .

backend-serve:
	cd web/server && DJANGO_SETTINGS_MODULE=config.settings uv run python manage.py runserver 8001

backend-test:
	cd web/server && uv run pytest game/

frontend-install:
	cd web/frontend && npm install

frontend-dev:
	cd web/frontend && npm run dev

frontend-build:
	cd web/frontend && npm run build

frontend-lint:
	cd web/frontend && npm run lint

frontend-preview:
	cd web/frontend && npm run preview
