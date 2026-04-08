#!/bin/bash

# Generates .env files from example templates, fetching secrets from Bitwarden.
#
# Usage: ./generate_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Generate the local env file
"$SCRIPT_DIR/expand_env.sh" infra/docker/local/.env.example infra/docker/local/.env

# Generate the deploy env file
"$SCRIPT_DIR/expand_env.sh" infra/docker/deploy/.env.example infra/docker/deploy/.env

# Generate the frontend env.js file (if it doesn't exist)
if [ ! -f frontend/public/env.js ]; then
    cp frontend/public/env.js.example frontend/public/env.js
    echo "Created frontend/public/env.js"
fi
