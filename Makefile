.PHONY: help build up down logs shell migrate makemigrations test

help:
	@echo "Available commands:"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start development environment"
	@echo "  make down          - Stop development environment"
	@echo "  make logs          - View logs"
	@echo "  make shell         - Django shell"
	@echo "  make bash          - Bash into web container"
	@echo "  make migrate       - Run migrations"
	@echo "  make makemigrations - Make migrations"
	@echo "  make test          - Run tests"
	@echo "  make createsuperuser - Create admin user"

build:
	docker compose build

up:
	docker compose up

upd:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web bash

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

test:
	docker compose exec web python manage.py test

createsuperuser:
	docker compose exec web python manage.py createsuperuser

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput