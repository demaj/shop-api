.PHONY: build
build:
	@docker-compose -f docker-compose.yml build

.PHONY: run
run:
	@docker-compose -f docker-compose.yml up

.PHONY: down
down:
	@docker-compose -f docker-compose.yml down
