---
id: docker-infrastructure
title: Docker & Infrastructure
purpose: Docker services, compose configuration, and local development setup.
scope:
  paths:
  - infra/**/*
  - '**/Dockerfile'
  - '**/docker-compose*.yml'
  tags:
  - docker
  - infrastructure
  - devops
---

# Docker & Infrastructure

## Items

<!-- @item source:user status:active enforcement:recommended -->
Local development uses `infra/docker/local/docker-compose.yml`. Port allocation (1300-1310 range): Frontend (1300), Gateway API (1301), Redis (1302), PostgreSQL (1303). Services include: gateway, frontend, fullstack_db (PostgreSQL 16), redis, celery_worker, celery_beat, and migration.

<!-- @item source:user status:active enforcement:recommended -->
Use `make run` for full stack, `make run_no_frontend` for gateway + database only (faster frontend hot reload with `yarn start`).

<!-- @item source:llm status:proposed -->
Celery worker and beat run as non-root user (1000:1000) to avoid security warnings. Redis is used as the Celery broker/backend.
