# Streamlit Desktop App Template

A production-ready template for creating **cross-platform desktop applications** using **Streamlit** and **pywebview**. Build beautiful desktop apps with Python only—no JavaScript, HTML, or CSS required.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🖥️ **Native Desktop Window**: Uses pywebview for true desktop experience (no browser chrome)
- 📦 **Standalone Binaries**: Distribute as .exe (Windows), executable (Linux/MacOS) with PyInstaller
- 🎨 **Fully Customizable**: Configurable branding (logo, icon, title) via YAML
- 🔧 **Easily Extensible**: Add new pages without touching navigation code
- 🐍 **100% Python**: No web development knowledge required
- 🌐 **Cross-Platform**: Windows 11, Linux, and MacOS supported
- 🚀 **Fast Startup**: <5 seconds from launch to window display
- 📝 **Complete Documentation**: Architecture, user guide, troubleshooting included
- 🤖 **CI/CD Ready**: GitHub Actions workflow for automated multi-platform builds

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

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Technical architecture, component breakdown, design decisions |
| [Extending Guide](docs/extending.md) | Step-by-step guide for adding new pages and features |
| [User Guide](docs/user-guide.md) | End-user documentation for apps built with this template |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |
| [Build Guide](build/README.md) | Comprehensive binary building instructions |
| [Quickstart](specs/001-streamlit-app-scaffold/quickstart.md) | Detailed setup and validation guide |

## 🎯 Use Cases

This template is perfect for:

- **Internal tools**: Build desktop apps for your team without web deployment
- **Data visualization**: Create interactive dashboards as desktop applications
- **Prototyping**: Quickly build desktop app prototypes with Python
- **Offline applications**: Apps that must run without internet connection
- **Desktop utilities**: File processors, converters, analysis tools

## 🔧 Technology Stack

- **UI Framework**: [Streamlit](https://streamlit.io/) (≥1.30.0)
- **Desktop Wrapper**: [pywebview](https://pywebview.flowrl.com/) (≥4.4.0)
- **Configuration**: PyYAML (≥6.0)
- **Binary Packaging**: PyInstaller (≥6.0)
- **Platform Support**: Windows 11, Ubuntu 20.04+, MacOS 10.15+

## 🚀 What's Next?

After setup, check out:

1. **Customize branding** - Replace logo, icon, and title in `config/app.yaml`
2. **Add your first page** - See [`docs/extending.md`](docs/extending.md)
3. **Build binary** - Create standalone executable with build scripts
4. **Deploy with CI/CD** - Use included GitHub Actions workflow

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: See [`docs/`](docs/) folder
- **Troubleshooting**: See [`docs/troubleshooting.md`](docs/troubleshooting.md)

---

**Built with ❤️ using Python, Streamlit, and pywebview**
