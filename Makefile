# ==============================================================================
# == MastermindAI — Project task runner
# ==   Covers development tooling, testing, ML pipeline, and Docker web
# ==   deployment. Run `make <target>` to execute a specific task.
# ==============================================================================

.PHONY: install ci-local \
        lint format typecheck \
        test test-unit test-cov \
        train sweep evaluate serve docker-build \
        backend-serve backend-test \
        frontend-install frontend-dev frontend-build frontend-lint frontend-preview \
        web-build web-up web-down web-push web-publish web-run

NAMESPACE = yassermessahli
VERSION  ?= latest
APP_URL   = http://localhost:3000


# ==============================================================================
# == SETUP
# ==   Install all project dependency groups (core, dev, backend) via uv.
# ==============================================================================

install:
	uv sync --all-groups


# ==============================================================================
# == CODE QUALITY
# ==   Linting, formatting, and static type checking for the mastermind package.
# ==============================================================================

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy mastermind/


# ==============================================================================
# == TESTING
# ==   Unit tests, integration tests, and coverage reporting.
# ==============================================================================

test:
	uv run pytest tests/

test-unit:
	uv run pytest tests/unit/

test-cov:
	uv run pytest --cov=mastermind tests/


# ==============================================================================
# == ML PIPELINE
# ==   Train the RL agent, run hyperparameter sweeps, evaluate against
# ==   baselines, and start the FastAPI inference server.
# ==============================================================================

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


# ==============================================================================
# == CI
# ==   Reproduce the GitHub Actions pipeline locally using act (requires Docker).
# ==============================================================================

ci-local:
	act push


# ==============================================================================
# == BACKEND DEV
# ==   Run and test the Django server locally without Docker.
# ==============================================================================

backend-serve:
	cd web/server && DJANGO_SETTINGS_MODULE=config.settings uv run python manage.py runserver 8001

backend-test:
	cd web/server && uv run pytest game/


# ==============================================================================
# == FRONTEND DEV
# ==   Install npm deps, run the Vite dev server, build for production,
# ==   lint, and preview the production build locally.
# ==============================================================================

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


# ==============================================================================
# == WEB APP — DOCKER
# ==   Build, publish, and run the full-stack app (Django + React/Nginx)
# ==   via Docker Compose.
# ==
# --  Local build workflow:
# --    make web-build    build both images from source
# --    make web-up       start containers in the background, open browser
# --    make web-down     stop and remove containers
# --
# --  Registry workflow:
# --    make web-publish  build + push images to Docker Hub
# --    make web-run      pull from Docker Hub, start, open browser
# ==============================================================================

# Auto-create .env from the example template if it does not yet exist.
.env:
	cp .env.example .env
	@echo "Created .env from .env.example — update DJANGO_SECRET_KEY before use"

web-build:
	VERSION=$(VERSION) docker compose build

web-up: .env
	VERSION=$(VERSION) docker compose up -d
	@sleep 2 && (xdg-open $(APP_URL) 2>/dev/null || open $(APP_URL) 2>/dev/null || true)

web-down:
	docker compose down

web-push:
	VERSION=$(VERSION) docker compose push

web-publish: web-build web-push
	@if [ "$(VERSION)" != "latest" ]; then \
		docker tag $(NAMESPACE)/mastermind-backend:$(VERSION) $(NAMESPACE)/mastermind-backend:latest; \
		docker tag $(NAMESPACE)/mastermind-frontend:$(VERSION) $(NAMESPACE)/mastermind-frontend:latest; \
		docker push $(NAMESPACE)/mastermind-backend:latest; \
		docker push $(NAMESPACE)/mastermind-frontend:latest; \
	fi

web-run: .env
	VERSION=$(VERSION) docker compose pull
	VERSION=$(VERSION) docker compose up -d
	@sleep 2 && (xdg-open $(APP_URL) 2>/dev/null || open $(APP_URL) 2>/dev/null || true)
