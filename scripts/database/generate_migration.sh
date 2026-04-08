#!/bin/bash

# Prompt for the migration subject
read -p "Enter migration subject: " msg

# Echo the migration subject for confirmation
echo "Running migration with subject: $msg"

# Define the Docker Compose file
DOCKER_COMPOSE_FILE="./infra/docker/local/docker-compose.yml"

# Build the migration service
docker compose -f "$DOCKER_COMPOSE_FILE" build migration

# Run the migration command with the provided subject
docker compose -f "$DOCKER_COMPOSE_FILE" run migration alembic -c /app/alembic.ini revision --autogenerate -m "$msg"
