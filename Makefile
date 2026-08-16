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
	@docker compose exec -w /code web python -m pytest

.PHONY: lint
lint:
	@docker compose exec -w /code web bash -c "isort --check-only shop_api tests && black --check shop_api tests && flake8 shop_api tests"

.PHONY: shell
shell:
	@docker compose exec -w /code web bash

.PHONY: prod-config
prod-config:
	@docker compose --project-directory . -f docker/production.yml config
