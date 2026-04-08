DOCKER_COMPOSE_FILE := infra/docker/local/docker-compose.yml
DEPLOY_DOCKER_COMPOSE_FILE := infra/docker/deploy/docker-compose.yml


# ------------------------------------------------------------
# ----------------- Repo Management --------------------------
# ------------------------------------------------------------
.PHONY: setup

# Sets up the project for development
setup:
	./scripts/administration/setup.sh

hard_reset_repo:
	./scripts/administration/hard_reset_repo.sh

env:
	./scripts/administration/env/generate_env.sh

reset_docker:
	./scripts/administration/reset_docker.sh

update_locks:
	cd backend && uv lock

# ------------------------------------------------------------
# ----------------- Local Development ------------------------
# ------------------------------------------------------------
.PHONY: build, run, run_no_frontend, api, stop

# Build the docker images for local development
build:
	docker compose -f $(DOCKER_COMPOSE_FILE) build

# Run the docker images for local development
run:
	docker compose -f $(DOCKER_COMPOSE_FILE) up

# Run just the gateway and database for local development
# This allow for faster frontend development (hot reloading)
run_no_frontend:
	docker compose -f $(DOCKER_COMPOSE_FILE) up fullstack_db -d
	docker compose -f $(DOCKER_COMPOSE_FILE) up gateway celery_worker celery_beat


# Run just the gateway for local development
api:
	docker compose -f $(DOCKER_COMPOSE_FILE) up gateway

# Stop the docker images for local development
stop:
	docker compose -f $(DOCKER_COMPOSE_FILE) stop

# ------------------------------------------------------------
# ------------------- Dev Tools  -----------------------------
# ------------------------------------------------------------
.PHONY: sync_openapi, mcp_server

# Sync the OpenAPI spec across the frontend and backend
sync_openapi:
	docker compose -f $(DOCKER_COMPOSE_FILE) up gateway -d;
	@until docker compose -f $(DOCKER_COMPOSE_FILE) exec gateway sh -c "curl gateway:1301/health" | grep -q ok; do \
		echo "Waiting for API..."; \
		sleep 2; \
	done;
	./backend/tools/openapi/sync.sh

# Run the MCP dev server (available at http://localhost:8100/mcp)
mcp_server:
	cd backend/tools && uv run python -m mcp_server.server

# ------------------------------------------------------------
# -------------- Database Management -------------------------
# ------------------------------------------------------------
.PHONY: db_generate_migration, db_wipe, db_reset, db_apply_migration, db_shell

# Generate a new migration
db_generate_migration:
	./scripts/database/generate_migration.sh

# Wipe the database
db_wipe:
	docker compose -f $(DOCKER_COMPOSE_FILE) run migration psql "postgresql://fullstack_user:password@fullstack_db/postgres" -c "DROP DATABASE \"fullstack-db\" WITH (FORCE); " -c "CREATE DATABASE \"fullstack-db\";"

# Fully reset the database
db_reset:
	docker compose -f $(DOCKER_COMPOSE_FILE) up fullstack_db -d
	@until docker compose -f $(DOCKER_COMPOSE_FILE) exec fullstack_db pg_isready -U fullstack_user; do \
		echo "Waiting for database..."; \
		sleep 2; \
	done;
	make db_wipe;
	make db_apply_migration;


# Apply a migration
db_apply_migration:
	docker compose -f $(DOCKER_COMPOSE_FILE) up migration

# This allows you to connect to the database of the local environment
db_shell:
	docker compose -f $(DOCKER_COMPOSE_FILE) exec fullstack_db psql -U fullstack_user -d fullstack-db

# ------------------------------------------------------------
# ----------------- Redis Management -------------------------
# ------------------------------------------------------------
.PHONY: redis_reset

redis_reset:
	docker compose -f $(DOCKER_COMPOSE_FILE) exec redis redis-cli FLUSHALL;


# ------------------------------------------------------------
# ----------------- Release Management -----------------------
# ------------------------------------------------------------
.PHONY: release, release_stop, release_logs, release_db_shell

# Release the project. For now, this simply just uses the deploy docker file
# (which has its own set of env variables + network).
# Further deployment steps can be done on deployed environments.
release:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) down todo_gateway todo_frontend todo_celery_worker todo_celery_beat
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) build todo_migration todo_frontend
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) up todo_migration
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) up todo_gateway todo_frontend todo_celery_worker todo_celery_beat -d

# Stop the release environment
release_stop:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) down

# This allows you to watch the logs of the release environment
release_logs:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) logs -f

# This allows you to connect to the database of the release environment
release_db_shell:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) exec deploy_fullstack_db psql -U $${POSTGRES_USER:-deploy_fullstack_user} -d $${POSTGRES_DB:-deploy_fullstack-db}