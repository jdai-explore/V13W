# ARXML Viewer Pro

Professional AUTOSAR ARXML file viewer for automotive engineers, built with Python and PyQt6.

## 🚀 Quick Start (Conda Environment)

### Activate Environment
```bash
# Activate the conda environment
./activate.sh

# Or manually:
conda activate arxml-viewer-pro
```

### Run Application
```bash
python -m arxml_viewer.main
```

### Development Commands
```bash
# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
```

### Using Scripts
```bash
# Quick run
./scripts/run.sh

# Quick test
./scripts/test.sh

# Format code
./scripts/format.sh
```

## 🛠️ Environment Info

- **Conda Environment**: arxml-viewer-pro
- **Python Version**: 3.9
- **GUI Framework**: PyQt6
- **Key Dependencies**: lxml, pydantic, pandas, matplotlib

## 📁 Project Structure

```
arxml_viewer_pro/
├── src/arxml_viewer/          # Main application package
├── tests/                     # Test suite
├── scripts/                   # Development scripts
├── environment.yml            # Conda environment
├── requirements.txt           # Pip requirements
└── activate.sh                # Environment activation
```

---

**Built with ❤️ for the automotive software community**
