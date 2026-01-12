#!/bin/zsh

# DexTalker Clickable Launcher
# This script activates the virtual environment, starts the server,
# opens Brave when ready, and keeps the server running.

# Navigate to the folder where this script is located
BASE_DIR=$(dirname "$0")
cd "$BASE_DIR"

echo "🚀 Launching DexTalker..."

# Activate virtual environment if present
if [ -f "./.venv/bin/activate" ]; then
    source "./.venv/bin/activate"
elif [ -f "./.venv311/bin/activate" ]; then
    source "./.venv311/bin/activate"
else
    echo "⚠️ No virtual environment found (.venv or .venv311)."
fi

# Uncomment for share mode
# export DEXTALKER_BIND_ALL=1

# Choose Python
if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    PYTHON_BIN="python3"
fi

LOG_DIR="$HOME/Library/Logs/DexTalker"
LOG_FILE="$LOG_DIR/launcher_icon.log"
mkdir -p "$LOG_DIR"
: > "$LOG_FILE"

export PYTHONUNBUFFERED=1

echo "Starting server..."
$PYTHON_BIN run.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

PORT=""
HOST=""
for i in {1..60}; do
    if [ -f "$LOG_FILE" ]; then
        line=$(tail -n 50 "$LOG_FILE" | /usr/bin/grep -E "Launching DexTalker on" | tail -n 1)
        if [ -n "$line" ]; then
            HOST=$(echo "$line" | /usr/bin/sed -E 's/.*Launching DexTalker on ([^:]+):([0-9]+).*/\1/')
            PORT=$(echo "$line" | /usr/bin/sed -E 's/.*Launching DexTalker on ([^:]+):([0-9]+).*/\2/')
        fi
    fi
    if [ -n "$PORT" ]; then
        if /usr/bin/curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
            echo "Server ready at http://127.0.0.1:$PORT/"
            /usr/bin/open -na "Brave Browser" --args --new-window "http://127.0.0.1:$PORT/"
            break
        fi
    fi
    /bin/sleep 1
done

if [ -z "$PORT" ]; then
    echo "❌ Failed to detect server port. Check $LOG_FILE"
elif ! /usr/bin/curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
    echo "❌ Server not responding at http://127.0.0.1:$PORT/. Check $LOG_FILE"
fi

wait "$SERVER_PID"
