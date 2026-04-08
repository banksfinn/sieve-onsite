#!/bin/bash
set -o pipefail

# First, we need to generate the backend virtual environment
echo "Generating script virtual environment (python)"
cd backend
uv sync
cd ..

echo "Generating env file"
make env

echo "Installing pre-commit hooks"
cd backend && uv run pre-commit install -c ../.pre-commit-config.yaml
cd ..

echo "Setup complete"