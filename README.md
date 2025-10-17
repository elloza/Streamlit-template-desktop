# Streamlit Desktop App Template

A boilerplate project for creating Streamlit desktop applications with binary generation for Win11/Unix (MacOS support aspirational).

## Features

- 🖥️ **Desktop Application**: Convert Streamlit web apps to native desktop applications using pywebview
- 📦 **Binary Distribution**: Generate standalone executables with PyInstaller
- 🎨 **Customizable**: Easy branding with logo and title configuration
- 🔧 **Extensible**: Add new pages by creating Python modules
- 🐍 **Python-Only**: No JavaScript, HTML, or CSS required
- 🌐 **Cross-Platform**: Works on Windows 11 and Unix/Linux

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Streamlit-template-desktop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

A desktop window will open displaying the Streamlit application with sidebar navigation.

## Project Structure

```
Streamlit-template-desktop/
├── app.py                  # Application entry point
├── src/
│   ├── ui/                 # UI components and pages
│   │   ├── sidebar.py      # Sidebar navigation
│   │   ├── pages/          # Application pages
│   │   └── components/     # Reusable UI components
│   └── logic/              # Business logic
│       └── config_loader.py
├── config/
│   └── app.yaml            # Application configuration
├── assets/
│   └── logo.png            # Application logo
├── build/                  # Build scripts and configuration
├── docs/                   # Documentation
└── tests/                  # Test files
```

## Customization

### Change App Title and Logo

1. Edit `config/app.yaml` to change the app title
2. Replace `assets/logo.png` with your own logo (recommended: 200x200 pixels)
3. Restart the application

### Add a New Page

1. Create a new Python file in `src/ui/pages/` (e.g., `my_page.py`)
2. Implement a `render()` function using Streamlit components
3. Add the page to `config/app.yaml` menu items
4. Restart the application

See `docs/extending.md` for detailed instructions.

## Building Binaries

### Windows

```bash
cd build/scripts
./build_windows.sh
```

### Unix/Linux

```bash
cd build/scripts
./build_unix.sh
```

Binaries will be created in the `dist/` directory.

## Documentation

- [Architecture](docs/architecture.md) - Technical architecture explanation
- [Extending](docs/extending.md) - Guide for adding new features
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Quickstart](specs/001-streamlit-app-scaffold/quickstart.md) - Detailed quickstart guide

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
