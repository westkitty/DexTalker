#!/bin/zsh

# DexTalker Clickable Launcher
# This script finds the environment and starts the launcher

# Navigate to the folder where this script is located
BASE_DIR=$(dirname "$0")
cd "$BASE_DIR"

echo "🚀 Launching DexTalker..."

# Find the python executable
if [ -f "./.venv/bin/python" ]; then
    PYTHON_EXE="./.venv/bin/python"
elif [ -f "./.venv311/bin/python" ]; then
    PYTHON_EXE="./.venv311/bin/python"
else
    PYTHON_EXE="python3"
fi

# Run the launcher
$PYTHON_EXE app/launcher_simple.py
