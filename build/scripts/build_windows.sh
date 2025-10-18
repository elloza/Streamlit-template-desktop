#!/bin/bash
# Windows build script for Streamlit Desktop App
# Uses PyInstaller to create standalone Windows executable

set -e  # Exit on error

echo "======================================"
echo "Building Streamlit Desktop App (Windows)"
echo "======================================"

# Clean previous builds (but keep build/scripts)
echo "Cleaning previous builds..."
rm -rf dist/ *.spec
rm -rf build/StreamlitApp

# Build with PyInstaller
# IMPORTANT: --copy-metadata streamlit is required to include package metadata
# Without this, streamlit.version will fail with PackageNotFoundError
echo "Running PyInstaller..."
.conda/python.exe -m PyInstaller \
    --name="StreamlitApp" \
    --onedir \
    --windowed \
    --noconfirm \
    --clean \
    --icon="assets/icon_default.png" \
    --add-data="src;src" \
    --add-data="assets;assets" \
    --add-data="config;config" \
    --add-binary=".conda/Library/bin/libexpat.dll;." \
    --add-binary=".conda/Library/bin/ffi.dll;." \
    --copy-metadata streamlit \
    --copy-metadata altair \
    --hidden-import=streamlit \
    --hidden-import=streamlit.web.cli \
    --hidden-import=streamlit.web.bootstrap \
    --hidden-import=pywebview \
    --hidden-import=pywebview.platforms.winforms \
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
echo "Binary location: dist/StreamlitApp/"
echo "Executable: dist/StreamlitApp/StreamlitApp.exe"
echo ""

# Check build size
if [ -d "dist/StreamlitApp" ]; then
    size=$(du -sh dist/StreamlitApp | cut -f1)
    echo "Build size: $size"
fi
