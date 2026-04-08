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
	docker compose -f $(DOCKER_COMPOSE_FILE) up sieve_db -d
	docker compose -f $(DOCKER_COMPOSE_FILE) up gateway


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
# --------------- GCS Bucket Tools ---------------------------
# ------------------------------------------------------------
.PHONY: gcs_list, gcs_download, gcs_view, gcs_generate_metadata

# List bucket contents. Usage: make gcs_list [prefix=videos/]
gcs_list:
	cd backend && GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json uv run python tools/gcs/list_bucket.py $(prefix)

# Download a file. Usage: make gcs_download path=videos/clip.mp4
gcs_download:
	cd backend && GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json uv run python tools/gcs/download_file.py $(path)

# View videos in browser. Usage: make gcs_view [prefix=videos/]
gcs_view:
	cd backend && GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json uv run python tools/gcs/view_videos.py $(prefix)

# Generate sample clip metadata from bucket videos.
# Usage: make gcs_generate_metadata [prefix=videos/] [samples=20] [output=sample.json]
gcs_generate_metadata:
	cd backend && GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json uv run python tools/gcs/generate_sample_metadata.py \
		$(if $(prefix),--prefix $(prefix)) \
		$(if $(samples),--samples $(samples)) \
		$(if $(output),--output $(output))

# ------------------------------------------------------------
# -------------- Database Management -------------------------
# ------------------------------------------------------------
.PHONY: db_generate_migration, db_wipe, db_reset, db_apply_migration, db_shell

# Generate a new migration
db_generate_migration:
	./scripts/database/generate_migration.sh

# Wipe the database
db_wipe:
	docker compose -f $(DOCKER_COMPOSE_FILE) run migration psql "postgresql://sieve_user:password@sieve_db/postgres" -c "DROP DATABASE \"sieve-db\" WITH (FORCE); " -c "CREATE DATABASE \"sieve-db\";"

# Fully reset the database
db_reset:
	docker compose -f $(DOCKER_COMPOSE_FILE) up sieve_db -d
	@until docker compose -f $(DOCKER_COMPOSE_FILE) exec sieve_db pg_isready -U sieve_user; do \
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
	docker compose -f $(DOCKER_COMPOSE_FILE) exec sieve_db psql -U sieve_user -d sieve-db

# ------------------------------------------------------------
# ----------------- Release Management -----------------------
# ------------------------------------------------------------
.PHONY: release, release_stop, release_logs, release_db_shell

# Release the project. For now, this simply just uses the deploy docker file
# (which has its own set of env variables + network).
# Further deployment steps can be done on deployed environments.
release:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) down todo_gateway todo_frontend
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) build todo_migration todo_frontend
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) up todo_migration
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) up todo_gateway todo_frontend -d

# Stop the release environment
release_stop:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) down

# This allows you to watch the logs of the release environment
release_logs:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) logs -f

# This allows you to connect to the database of the release environment
release_db_shell:
	docker compose -f $(DEPLOY_DOCKER_COMPOSE_FILE) exec deploy_sieve_db psql -U $${POSTGRES_USER:-deploy_sieve_user} -d $${POSTGRES_DB:-deploy_sieve-db}