#!/bin/bash
# Build script for Windows 11 (Win11)
# Requires: PyInstaller installed (pip install pyinstaller)
# Platform: Windows with Git Bash, WSL, or similar Unix shell

set -e  # Exit on error

echo "========================================"
echo "Streamlit Desktop App - Windows Build"
echo "========================================"

# Configuration
APP_NAME="StreamlitApp"
VERSION="0.1.0"
ICON_PATH="assets/icon_default.png"
ENTRY_POINT="app.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Windows
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" && "$OSTYPE" != "cygwin" ]]; then
    echo -e "${YELLOW}Warning: This script is intended for Windows. Detected OS: $OSTYPE${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}Error: PyInstaller not found${NC}"
    echo "Install with: pip install pyinstaller"
    exit 1
fi

# Check if entry point exists
if [ ! -f "$ENTRY_POINT" ]; then
    echo -e "${RED}Error: Entry point '$ENTRY_POINT' not found${NC}"
    echo "Make sure you're running this script from the repository root"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.spec
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo

# Build with PyInstaller
echo "Building Windows executable..."
echo "This may take several minutes..."
echo

pyinstaller \
    --name="$APP_NAME" \
    --onedir \
    --windowed \
    --noconfirm \
    --clean \
    --icon="$ICON_PATH" \
    --add-data="src;src" \
    --add-data="assets;assets" \
    --add-data="config;config" \
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
    "$ENTRY_POINT"

echo
echo -e "${GREEN}✓ Build complete!${NC}"
echo

# Check if build succeeded
if [ -f "dist/$APP_NAME/$APP_NAME.exe" ]; then
    echo "========================================="
    echo "Build Information"
    echo "========================================="
    echo "App Name: $APP_NAME"
    echo "Version: $VERSION"
    echo "Platform: Windows 11"
    echo "Output: dist/$APP_NAME/"
    echo "Executable: dist/$APP_NAME/$APP_NAME.exe"

    # Get directory size
    BUILD_SIZE=$(du -sh "dist/$APP_NAME" | cut -f1)
    echo "Build Size: $BUILD_SIZE"
    echo

    echo -e "${GREEN}Build successful!${NC}"
    echo
    echo "Next steps:"
    echo "1. Test the executable: dist/$APP_NAME/$APP_NAME.exe"
    echo "2. Distribute the entire dist/$APP_NAME/ folder"
    echo "3. Users can run $APP_NAME.exe without Python installed"
    echo
    echo "Note: The entire dist/$APP_NAME/ directory must be distributed,"
    echo "      not just the .exe file (onedir mode includes dependencies)"
else
    echo -e "${RED}Error: Build failed - executable not found${NC}"
    echo "Check the build output above for errors"
    exit 1
fi

echo "========================================="
echo "Build process complete"
echo "========================================="
