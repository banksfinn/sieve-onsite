#!/bin/bash

# These are all of the directories that we want to delete
# when we reset the uv environment
dirs_to_delete=(".venv" "build" "__pycache__")

# Specify the root directory of your repository
root_directory="."

# Loop through each directory name to delete
for dir_name in "${dirs_to_delete[@]}"; do
    # Find and delete directories
    find "$root_directory" -name "$dir_name" -exec rm -rf {} +
done

# Delete all of the egg info directories
find . -name "*.egg-info" -type d -exec rm -rf {} +

# Clear the uv cache
uv cache clean >/dev/null 2>&1

# Install dependencies
uv sync >/dev/null 2>&1

echo "UV environment has been reset."
