.PHONY: start
start:
	@docker compose up -d --build

.PHONY: stop
stop:
	@docker compose down

.PHONY: migrate
migrate:
	@docker compose exec web alembic upgrade head

.PHONY: logs
logs:
	@docker logs -f shop-web
