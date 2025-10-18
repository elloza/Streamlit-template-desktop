#!/bin/bash
# Build script for Unix/Linux platforms
# Requires: PyInstaller installed (pip install pyinstaller)
# Platform: Linux, MacOS, or Unix-like systems

set -e  # Exit on error

echo "========================================"
echo "Streamlit Desktop App - Unix/Linux Build"
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

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="MacOS"
else
    PLATFORM="Unix"
fi

echo "Detected platform: $PLATFORM"
echo

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

# Platform-specific checks
if [[ "$PLATFORM" == "Linux" ]]; then
    # Check for GTK dependencies (required for pywebview on Linux)
    if ! dpkg -l | grep -q libgtk-3-0; then
        echo -e "${YELLOW}Warning: GTK3 not detected${NC}"
        echo "Install with: sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37"
        echo "Required for pywebview to work on Linux"
        echo
    fi
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.spec
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo

# Build with PyInstaller
echo "Building $PLATFORM executable..."
echo "This may take several minutes..."
echo

pyinstaller \
    --name="$APP_NAME" \
    --onedir \
    --windowed \
    --noconfirm \
    --clean \
    --icon="$ICON_PATH" \
    --add-data="src:src" \
    --add-data="assets:assets" \
    --add-data="config:config" \
    --hidden-import=streamlit \
    --hidden-import=streamlit.web.cli \
    --hidden-import=streamlit.web.bootstrap \
    --hidden-import=pywebview \
    --hidden-import=pywebview.platforms.gtk \
    --hidden-import=pywebview.platforms.cocoa \
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
EXECUTABLE_NAME="$APP_NAME"
if [[ "$PLATFORM" == "MacOS" ]]; then
    EXECUTABLE_PATH="dist/$APP_NAME.app/Contents/MacOS/$APP_NAME"
else
    EXECUTABLE_PATH="dist/$APP_NAME/$APP_NAME"
fi

if [ -f "$EXECUTABLE_PATH" ]; then
    echo "========================================="
    echo "Build Information"
    echo "========================================="
    echo "App Name: $APP_NAME"
    echo "Version: $VERSION"
    echo "Platform: $PLATFORM"
    echo "Output: dist/$APP_NAME/"
    echo "Executable: $EXECUTABLE_PATH"

    # Get directory size
    BUILD_SIZE=$(du -sh "dist/$APP_NAME" 2>/dev/null | cut -f1 || echo "Unknown")
    echo "Build Size: $BUILD_SIZE"

    # Make executable if not already
    chmod +x "$EXECUTABLE_PATH"
    echo -e "${GREEN}✓ Executable permissions set${NC}"
    echo

    echo -e "${GREEN}Build successful!${NC}"
    echo
    echo "Next steps:"
    echo "1. Test the executable: $EXECUTABLE_PATH"
    echo "2. Distribute the entire dist/$APP_NAME/ folder"
    echo "3. Users can run $APP_NAME without Python installed"
    echo

    if [[ "$PLATFORM" == "Linux" ]]; then
        echo "Linux users will need GTK3 and WebKit2GTK installed:"
        echo "  sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37"
        echo
    fi

    echo "Note: The entire dist/$APP_NAME/ directory must be distributed,"
    echo "      not just the executable (onedir mode includes dependencies)"
else
    echo -e "${RED}Error: Build failed - executable not found at $EXECUTABLE_PATH${NC}"
    echo "Check the build output above for errors"
    exit 1
fi

echo "========================================="
echo "Build process complete"
echo "========================================="
