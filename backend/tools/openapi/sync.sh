#!/bin/bash
set -eou pipefail

# Run from project root
cd "$(dirname "$0")/../../.."

# Download OpenAPI spec from gateway
cd backend
uv run python -m tools.openapi.update_api

# Generate TypeScript types
cd ../frontend


yarn install
yarn ts-codegen
