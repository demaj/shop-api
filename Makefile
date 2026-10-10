.PHONY: start
start:
	@docker compose up -d --build

.PHONY: stop
stop:
	@docker compose down

.PHONY: migrate
migrate:
	@docker compose exec -w /code web alembic upgrade head

.PHONY: logs
logs:
	@docker logs -f shop-web

.PHONY: test
test:
	@docker compose exec -e TESTS_REQUIRE_DB=1 -e COVERAGE_FILE=/tmp/.coverage -w /code web python -m pytest --cov --cov-fail-under=80

.PHONY: lint
lint:
	@docker compose exec -w /code web bash -c "ruff check . && ruff format --check ."

.PHONY: format
format:
	@docker compose exec -w /code web bash -c "ruff check --fix . && ruff format ."

.PHONY: lock
lock:
	@uv lock

.PHONY: shell
shell:
	@docker compose exec -w /code web bash

.PHONY: prod-config
prod-config:
	@docker compose --project-directory . -f docker/production.yml config
