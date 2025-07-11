# ARXML Viewer Pro

Professional AUTOSAR ARXML file viewer for automotive engineers.

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Windows, macOS, or Linux

### Installation

#### Option 1: Automatic Installation (Recommended)
```bash
# Clone or download the project
cd arxml_viewer_pro

# Run the automatic installer
python install_deps.py

# Run the application
python run_app.py
```

#### Option 2: Manual Installation
```bash
# Install required dependencies
pip install PyQt5>=5.15.0 pydantic>=2.4.0 lxml>=4.9.3

# Install optional dependencies (recommended)
pip install loguru pandas matplotlib networkx numpy Pillow

# Run the application
python run_app.py
```

#### Option 3: Using Conda Environment
```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate arxml-viewer-pro

# Run the application
python -m arxml_viewer.main
```

### Usage

1. **Launch the application:**
   ```bash
   python run_app.py
   ```

2. **Open an ARXML file:**
   - Use File → Open menu
   - Or provide file path as argument: `python run_app.py sample.arxml`

3. **Navigate the components:**
   - Browse packages and components in the left panel
   - View component diagrams in the center panel
   - Inspect component properties in the right panel

## Features

- ✅ **ARXML Parsing**: Parse AUTOSAR ARXML files
- ✅ **Component Visualization**: View software components and their relationships  
- ✅ **Port Management**: Display provided and required ports
- ✅ **Connection Analysis**: Visualize component connections
- ✅ **Package Navigation**: Browse hierarchical package structure
- ✅ **Search & Filter**: Find components and ports quickly
- ✅ **Multiple Views**: Tree view, diagram view, and properties panel

## Supported AUTOSAR Versions

- AUTOSAR 4.0.x
- AUTOSAR 4.1.x  
- AUTOSAR 4.2.x
- AUTOSAR 4.3.x

## Troubleshooting

### Common Issues

**1. "No module named 'loguru'" error:**
```bash
pip install loguru
# or run without loguru (uses fallback logging)
```

**2. "No module named 'PyQt5'" error:**
```bash
pip install PyQt5
# Make sure you have PyQt5, not PyQt6
```

**3. XML parsing errors:**
- Ensure your ARXML file is valid XML
- Check file encoding (should be UTF-8)
- Try with a smaller test file first

**4. Application won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Verify installations
python -c "import PyQt5; print('PyQt5 OK')"
python -c "import pydantic; print('Pydantic OK')"
python -c "import lxml; print('lxml OK')"

# Run with debug info
python run_app.py --debug
```

### Getting Help

1. **Check the logs**: The application logs information to the console
2. **Verify file format**: Ensure your ARXML file follows AUTOSAR standards
3. **Test with sample**: Try with a simple ARXML file first
4. **Check dependencies**: Run `python install_deps.py` to verify installations

## File Structure

```
arxml_viewer_pro/
├── src/arxml_viewer/           # Main application code
│   ├── models/                 # Data models (Component, Port, etc.)
│   ├── parsers/               # ARXML parsing logic
│   ├── gui/                   # User interface components
│   ├── services/              # Search, filter, and other services
│   └── utils/                 # Utilities and constants
├── run_app.py                 # Application launcher
├── install_deps.py           # Dependency installer
├── requirements.txt          # Python dependencies
└── environment.yml          # Conda environment
```

## Development

### Running Tests
```bash
# Validate the installation
python validate_project.py

# Run specific tests (if pytest is installed)
pytest tests/
```

### Code Style
```bash
# Format code (if black is installed)
black src/ tests/

# Check style (if flake8 is installed)  
flake8 src/
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a professional AUTOSAR ARXML viewer designed for automotive software engineers. It provides comprehensive analysis of AUTOSAR software component architectures.