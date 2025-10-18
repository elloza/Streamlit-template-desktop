#!/bin/bash
# Unix/Linux/MacOS build script for Streamlit Desktop App
# Uses PyInstaller to create standalone executable

set -e  # Exit on error

echo "======================================"
echo "Building Streamlit Desktop App (Unix/Linux/MacOS)"
echo "======================================"

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="MacOS"
    BUNDLE_TYPE="--onedir"  # MacOS uses .app bundles
else
    PLATFORM="Linux"
    BUNDLE_TYPE="--onedir"
fi

echo "Platform: $PLATFORM"

# Detect Python executable (local .conda or system python)
if [ -f ".conda/bin/python" ]; then
    PYTHON_CMD=".conda/bin/python"
    echo "Using local conda Python: $PYTHON_CMD"
else
    PYTHON_CMD="python"
    echo "Using system Python: $PYTHON_CMD"
fi

# Clean previous builds (but keep build/scripts)
echo "Cleaning previous builds..."
rm -rf dist/ *.spec
rm -rf build/StreamlitApp

# Build with PyInstaller
# IMPORTANT: --copy-metadata streamlit is required to include package metadata
# Without this, streamlit.version will fail with PackageNotFoundError
echo "Running PyInstaller..."
$PYTHON_CMD -m PyInstaller \
    --name="StreamlitApp" \
    $BUNDLE_TYPE \
    --noconfirm \
    --clean \
    --icon="assets/icon_default.png" \
    --add-data="src:src" \
    --add-data="assets:assets" \
    --add-data="config:config" \
    --copy-metadata streamlit \
    --copy-metadata altair \
    --hidden-import=streamlit \
    --hidden-import=streamlit.web.cli \
    --hidden-import=streamlit.web.bootstrap \
    --hidden-import=pywebview \
    --hidden-import=yaml \
    --hidden-import=watchdog \
    --hidden-import=click \
    --hidden-import=tornado \
    --hidden-import=altair \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=PIL \
    --exclude-module=matplotlib \
    --exclude-module=scipy \
    --exclude-module=sklearn \
    --exclude-module=tensorflow \
    --exclude-module=torch \
    app.py

echo ""
echo "======================================"
echo "Build completed successfully!"
echo "======================================"

if [[ "$PLATFORM" == "MacOS" ]]; then
    echo "Application bundle: dist/StreamlitApp.app/"
    echo "Executable: dist/StreamlitApp.app/Contents/MacOS/StreamlitApp"
else
    echo "Binary location: dist/StreamlitApp/"
    echo "Executable: dist/StreamlitApp/StreamlitApp"
fi
echo ""

# Check build size
if [[ "$PLATFORM" == "MacOS" ]] && [ -d "dist/StreamlitApp.app" ]; then
    size=$(du -sh dist/StreamlitApp.app | cut -f1)
    echo "Build size: $size"
elif [ -d "dist/StreamlitApp" ]; then
    size=$(du -sh dist/StreamlitApp | cut -f1)
    echo "Build size: $size"
fi
