#!/bin/bash
# Re-creating a single, clean DexTalker app
APP_NAME="DexTalker"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BASE_DIR="$PROJECT_DIR"
RUNTIME_DIR="$HOME/Library/Application Support/DexTalker/runtime"
DEST_DIR="$HOME/Desktop/Anti_grav"
APP_ENTRY="app/launcher.py"
ICON_PNG="$HOME/.gemini/antigravity/brain/b06ea523-0248-47c9-80da-e93b601f804a/dextalk_app_icon_1768083912642.png"
PYTHON_PATH="$BASE_DIR/.venv311/bin/python"
USE_PROJECT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --local)
            DEST_DIR="$BASE_DIR"
            ;;
        --desktop)
            APP_ENTRY="app/desktop_app.py"
            APP_NAME="DexTalker Desktop"
            ;;
        --use-project)
            USE_PROJECT=1
            ;;
        --dest)
            shift
            DEST_DIR="$1"
            ;;
        --name)
            shift
            APP_NAME="$1"
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

APP_PATH="$DEST_DIR/$APP_NAME.app"

if [ "$APP_ENTRY" = "app/desktop_app.py" ] && [ "$USE_PROJECT" -eq 0 ]; then
    if [ -x "$RUNTIME_DIR/.venv/bin/python" ]; then
        BASE_DIR="$RUNTIME_DIR"
        PYTHON_PATH="$BASE_DIR/.venv/bin/python"
    fi
fi
APP_BACKGROUND=1
if [ "$APP_ENTRY" = "app/desktop_app.py" ]; then
    APP_BACKGROUND=0
fi

if [ "$APP_BACKGROUND" -eq 1 ]; then
    APP_CMD="cd \"$BASE_DIR\" && \"$PYTHON_PATH\" \"$APP_ENTRY\" > /dev/null 2>&1 &"
else
    APP_LOG_DIR="$HOME/Library/Logs/DexTalker"
    APP_LOG="$APP_LOG_DIR/desktop_app_run.log"
    APP_CMD="mkdir -p \"$APP_LOG_DIR\"; cd \"$BASE_DIR\" && \"$PYTHON_PATH\" \"$APP_ENTRY\" > \"$APP_LOG\" 2>&1"
fi
APP_CMD_ESCAPED=${APP_CMD//\"/\\\"}

if [ ! -x "$PYTHON_PATH" ]; then
    echo "DexTalker venv not found at $PYTHON_PATH"
    exit 1
fi

mkdir -p "$DEST_DIR"

if [ "$APP_ENTRY" = "app/desktop_app.py" ] && [ "$BASE_DIR" = "$RUNTIME_DIR" ]; then
    rsync -a --delete \
      --exclude '.venv*' \
      --exclude '__pycache__' \
      --exclude 'data/outputs' \
      --exclude 'dextalker.log' \
      --exclude 'launcher.log' \
      --exclude 'desktop_window.log' \
      --exclude 'desktop_app_run.log' \
      --exclude 'desktop_app.log' \
      "$PROJECT_DIR/" "$RUNTIME_DIR/"
fi

# 1. Clean up old apps
rm -rf "$APP_PATH"
rm -rf DexTalker.iconset DexTalker.icns

# 2. Create high-quality ICNS
if [ -f "$ICON_PNG" ]; then
    mkdir -p DexTalker.iconset
    sips -s format png -z 16 16     "$ICON_PNG" --out DexTalker.iconset/icon_16x16.png > /dev/null 2>&1
    sips -s format png -z 32 32     "$ICON_PNG" --out DexTalker.iconset/icon_16x16@2x.png > /dev/null 2>&1
    sips -s format png -z 32 32     "$ICON_PNG" --out DexTalker.iconset/icon_32x32.png > /dev/null 2>&1
    sips -s format png -z 64 64     "$ICON_PNG" --out DexTalker.iconset/icon_32x32@2x.png > /dev/null 2>&1
    sips -s format png -z 128 128   "$ICON_PNG" --out DexTalker.iconset/icon_128x128.png > /dev/null 2>&1
    sips -s format png -z 256 256   "$ICON_PNG" --out DexTalker.iconset/icon_128x128@2x.png > /dev/null 2>&1
    sips -s format png -z 256 256   "$ICON_PNG" --out DexTalker.iconset/icon_256x256.png > /dev/null 2>&1
    sips -s format png -z 512 512   "$ICON_PNG" --out DexTalker.iconset/icon_256x256@2x.png > /dev/null 2>&1
    sips -s format png -z 512 512   "$ICON_PNG" --out DexTalker.iconset/icon_512x512.png > /dev/null 2>&1
    sips -s format png -z 1024 1024 "$ICON_PNG" --out DexTalker.iconset/icon_512x512@2x.png > /dev/null 2>&1
    iconutil -c icns DexTalker.iconset
else
    echo "Icon not found at $ICON_PNG, using default app icon."
fi

# 3. Create the App
if [ "$APP_ENTRY" = "app/desktop_app.py" ]; then
    mkdir -p "$APP_PATH/Contents/MacOS" "$APP_PATH/Contents/Resources"
    cat << EOF > "$APP_PATH/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.antigrav.dextalker.desktop</string>
    <key>CFBundleExecutable</key>
    <string>DexTalker</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>
EOF
    cat << EOF > "$APP_PATH/Contents/MacOS/DexTalker"
#!/bin/bash
LOG_DIR="\$HOME/Library/Logs/DexTalker"
mkdir -p "\$LOG_DIR"
cd "$BASE_DIR" || exit 1
exec env PYTHONUNBUFFERED=1 \\
  "$PYTHON_PATH" "$APP_ENTRY" >> "\$LOG_DIR/desktop_app_run.log" 2>&1
EOF
    chmod +x "$APP_PATH/Contents/MacOS/DexTalker"
else
    cat << EOF > controller.applescript
on run
    try
        do shell script "lsof -ti:7860 | xargs kill -9 || true"
        do shell script "$APP_CMD_ESCAPED"
    on error e
        display dialog "Error: " & e & "\nSee $APP_LOG for details." with title "DexTalker"
    end try
end run

on quit
    try
        do shell script "lsof -ti:7860 | xargs kill -9 || true"
    end try
    continue quit
end quit
EOF

    osacompile -o "$APP_PATH" controller.applescript
fi

# 4. Apply Properties and Icon
if [ -f DexTalker.icns ]; then
    cp DexTalker.icns "$APP_PATH/Contents/Resources/applet.icns"
fi

if [ "$APP_ENTRY" != "app/desktop_app.py" ]; then
    /usr/libexec/PlistBuddy -c "Add :WindowState dict" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :WindowState:StayOpen bool true" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
fi

touch "$APP_PATH"

# 5. Cleanup
rm -rf DexTalker.iconset DexTalker.icns controller.applescript
echo "DexTalker app created successfully."
