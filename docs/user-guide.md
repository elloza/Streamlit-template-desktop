# User Guide: Streamlit Desktop Application

**For**: End-users of applications built with this template

---

## Getting Started

### First Launch

1. **Download** the application for your platform
2. **Extract** the archive to a folder
3. **Run** the executable:
   - Windows: Double-click `StreamlitApp.exe`
   - Linux: Run `./StreamlitApp`
   - MacOS: Open `StreamlitApp.app`

### System Requirements

- **Windows**: Windows 10/11 (64-bit)
- **Linux**: Ubuntu 20.04+ or equivalent with GTK3
- **MacOS**: MacOS 10.15 (Catalina) or newer
- **RAM**: Minimum 4GB recommended
- **Disk**: ~200MB for application

---

## Using the Application

### Navigation

Use the **sidebar menu** on the left to navigate between pages:
- Click any menu item to switch pages
- The active page is highlighted
- Your position is remembered during the session

### Pages

- **Home**: Overview and welcome message
- **Feature Pages**: Application-specific functionality
- **About**: Information about the application

### Customization

If you're running from source (not binary), you can customize:

**Logo** (`assets/logo.png`):
- Replace with your own image (PNG, JPG, SVG)
- Recommended size: 200x200 pixels
- Appears in sidebar

**Window Icon** (`assets/icon.png`):
- Replace with your icon (PNG or ICO)
- Recommended size: 256x256 pixels
- Appears in title bar and taskbar

**Configuration** (`config/app.yaml`):
```yaml
app_title: "Your App Name"
logo_path: "assets/logo.png"
icon_path: "assets/icon.png"
```

---

## Troubleshooting

### Application Won't Start

**Windows**:
- Check antivirus isn't blocking it
- Right-click → Properties → Unblock

**MacOS**:
- Right-click → Open (first time)
- System Preferences → Security → Allow

**Linux**:
- Install dependencies: `sudo apt-get install libgtk-3-0 libwebkit2gtk-4.0-37`
- Make executable: `chmod +x StreamlitApp`

### Application Crashes

Check the log file:
- Location: `logs/app.log` (same folder as executable)
- Contains error details and stack traces

### Slow Performance

- Close other applications to free RAM
- Check if antivirus is scanning the application
- Restart the application

---

## Keyboard Shortcuts

- **Ctrl/Cmd + R**: Refresh page (Streamlit feature)
- **F11**: Toggle fullscreen (may not work in all versions)

---

## Data and Privacy

- **No internet required**: Application runs completely offline
- **No data collection**: No analytics or tracking
- **Local storage**: All data stays on your computer
- **Logs**: Only local logs in `logs/` folder

---

## Support

For issues or questions:
1. Check `logs/app.log` for error messages
2. See [troubleshooting.md](./troubleshooting.md) for common issues
3. Contact the application developer/distributor

---

**Version**: 1.0.0
