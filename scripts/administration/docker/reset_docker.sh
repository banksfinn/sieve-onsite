#!/bin/bash

# This is a helper script to reset the docker environment. This can impact other docker
# environments, so be careful when using this.

# This should only impact local development
LOCAL_DOCKER_COMPOSE_FILE="./infra/docker/local/docker-compose.yml"

# Stop all Docker containers and remove orphans
echo "Stopping all Docker containers and removing orphans..."
docker compose -f "$LOCAL_DOCKER_COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f >/dev/null 2>&1

# Remove unused images
echo "Removing unused images..."
docker image prune -af >/dev/null 2>&1

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f >/dev/null 2>&1

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f >/dev/null 2>&1

# Clean up Docker system
echo "Cleaning up Docker system..."
docker system prune -af --volumes >/dev/null 2>&1

echo "Docker reset complete! You may now rebuild and start the environment."