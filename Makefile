build:
	@docker-compose -f docker-compose.yml build

run:
	@docker-compose -f docker-compose.yml up

down:
	@docker-compose -f docker-compose.yml down
