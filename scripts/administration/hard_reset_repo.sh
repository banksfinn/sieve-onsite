#!/bin/bash

# We want to delete all of the following directories:
dirs_to_delete=("node_modules" ".ruff_cache" ".pytest_cache")

# Specify the root directory of your repository
root_directory="."

echo "Resetting docker..."
make reset_docker >/dev/null 2>&1
echo "Docker reset."

echo "Deleting file caches..."
# Loop through each directory name to delete
for dir_name in "${dirs_to_delete[@]}"; do
    # Find and delete directories
    find "$root_directory" -name "$dir_name" -exec rm -rf {} +
done
echo "Deletion complete."

echo "Resetting DB..."
make db_reset >/dev/null 2>&1
echo "Reset complete."

echo "Running pdm reset."
make pdm_hard_reset

echo "Setting up env file."
make env
echo "Env file setup complete."

echo "Building images."
make build >/dev/null 2>&1
echo "Hard reset complete! 'make run' should work now"
