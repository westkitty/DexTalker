#!/bin/zsh

# DexTalker Clickable Launcher
# This script activates the virtual environment and runs DexTalker

# Navigate to the folder where this script is located
BASE_DIR=$(dirname "$0")
cd "$BASE_DIR"

echo "🚀 Launching DexTalker..."

# Activate virtual environment if present
if [ -f "./.venv/bin/activate" ]; then
    source "./.venv/bin/activate"
elif [ -f "./.venv311/bin/activate" ]; then
    source "./.venv311/bin/activate"
fi

# Uncomment for share mode
# export DEXTALKER_BIND_ALL=1

# Run DexTalker
if command -v python >/dev/null 2>&1; then
    python run.py
else
    python3 run.py
fi
