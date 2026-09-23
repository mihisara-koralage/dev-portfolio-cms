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

# ── Production ─────────────────────────────────────────────────

build-prod:
	docker compose -f docker-compose.prod.yml build

up-prod:
	docker compose -f docker-compose.prod.yml up -d

down-prod:
	docker compose -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

migrate-prod:
	docker compose -f docker-compose.prod.yml exec web python manage.py migrate

collectstatic-prod:
	docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

shell-prod:
	docker compose -f docker-compose.prod.yml exec web python manage.py shell

ps-prod:
	docker compose -f docker-compose.prod.yml ps

# ── Database backup ────────────────────────────────────────────

backup:
	docker compose -f docker-compose.prod.yml exec db \
		pg_dump -U $${DB_USER} $${DB_NAME} \
		> backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup saved to backups/"


# ── Terraform ──────────────────────────────────────────────────

tf-init:
	cd terraform/environments/production && terraform init

tf-plan:
	cd terraform/environments/production && terraform plan

tf-apply:
	cd terraform/environments/production && terraform apply

tf-destroy:
	cd terraform/environments/production && terraform destroy

tf-output:
	cd terraform/environments/production && terraform output