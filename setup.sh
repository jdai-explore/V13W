#!/bin/bash

# ARXML Viewer Pro - Anaconda/Conda Compatible Setup Script
# This script works with Anaconda Python environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="arxml_viewer_pro"
CONDA_ENV_NAME="arxml-viewer-pro"
PYTHON_VERSION="3.9"

print_header() {
    echo -e "${PURPLE}🚀 ARXML Viewer Pro - Anaconda/Conda Setup${NC}"
    echo -e "${CYAN}=================================================================${NC}"
    echo -e "${BLUE}Professional AUTOSAR ARXML file viewer for automotive engineers${NC}"
    echo -e "${BLUE}Python + PyQt6 Implementation (Conda Compatible)${NC}"
    echo -e "${CYAN}=================================================================${NC}"
    echo
}

print_step() {
    echo -e "${YELLOW}📋 $1...${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_conda() {
    print_step "Checking Conda installation"
    
    if ! command -v conda &> /dev/null; then
        print_error "Conda is not installed or not in PATH"
        echo "Please install Anaconda or Miniconda from:"
        echo "  - Anaconda: https://www.anaconda.com/products/distribution"
        echo "  - Miniconda: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    CONDA_VERSION=$(conda --version | cut -d' ' -f2)
    print_success "Conda $CONDA_VERSION found"
    
    # Check Python in base environment
    PYTHON_VER=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VER in base environment"
}

create_project_structure() {
    print_step "Creating project directory structure"
    
    # Create main project directory
    mkdir -p $PROJECT_NAME
    cd $PROJECT_NAME
    
    # Create all directories
    mkdir -p {src/arxml_viewer/{core,models,parsers,gui/{widgets,dialogs,graphics},services,utils,resources/{icons,themes,sample_data}},tests/{unit,integration,fixtures,sample_arxml},docs/{api,user_guide,developer_guide},config,scripts,tools,packaging/{windows,macos,linux},build,dist,logs}
    
    print_success "Project structure created"
}

create_conda_environment() {
    print_step "Creating Conda environment"
    
    # Check if environment already exists
    if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
        print_info "Environment $CONDA_ENV_NAME already exists, removing it..."
        conda env remove -n $CONDA_ENV_NAME -y
    fi
    
    # Create new conda environment with Python 3.9
    conda create -n $CONDA_ENV_NAME python=3.9 -y
    
    print_success "Conda environment '$CONDA_ENV_NAME' created"
}

create_requirements_files() {
    print_step "Creating requirements files"
    
    # Create requirements.txt
    cat > requirements.txt << 'EOF'
# ARXML Viewer Pro - Core Dependencies

# GUI Framework
PyQt6>=6.5.0

# XML Processing
lxml>=4.9.3

# Data Processing & Models
pandas>=2.1.0
pydantic>=2.4.0

# Graphics and Visualization
matplotlib>=3.7.2
networkx>=3.1

# Utilities
click>=8.1.7
loguru>=0.7.2

# Performance
numba>=0.58.0
numpy>=1.24.0

# Optional: Advanced features
Pillow>=10.0.0
reportlab>=4.0.4
EOF

    # Create environment.yml for conda
    cat > environment.yml << EOF
name: $CONDA_ENV_NAME
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - pip
  - numpy>=1.24.0
  - pandas>=2.1.0
  - matplotlib>=3.7.2
  - networkx>=3.1
  - pillow>=10.0.0
  - lxml>=4.9.3
  - numba>=0.58.0
  - pip:
    - PyQt6>=6.5.0
    - pydantic>=2.4.0
    - click>=8.1.7
    - loguru>=0.7.2
    - reportlab>=4.0.4
    - pytest>=7.4.2
    - pytest-cov>=4.1.0
    - pytest-qt>=4.2.0
    - pytest-mock>=3.11.1
    - black>=23.7.0
    - mypy>=1.5.1
    - flake8>=6.0.0
    - isort>=5.12.0
    - pylint>=2.17.5
    - sphinx>=7.1.2
    - sphinx-rtd-theme>=1.3.0
    - PyInstaller>=5.13.2
    - wheel>=0.41.2
    - build>=0.10.0
    - pre-commit>=3.4.0
    - memory-profiler>=0.61.0
EOF

    # Create requirements-dev.txt
    cat > requirements-dev.txt << 'EOF'
# ARXML Viewer Pro - Development Dependencies
-r requirements.txt

# Testing Framework
pytest>=7.4.2
pytest-cov>=4.1.0
pytest-qt>=4.2.0
pytest-mock>=3.11.1

# Code Quality
black>=23.7.0
mypy>=1.5.1
flake8>=6.0.0
isort>=5.12.0
pylint>=2.17.5

# Documentation
sphinx>=7.1.2
sphinx-rtd-theme>=1.3.0

# Packaging
PyInstaller>=5.13.2
wheel>=0.41.2
build>=0.10.0

# Development Tools
pre-commit>=3.4.0
memory-profiler>=0.61.0
EOF

    print_success "Requirements files created"
}

install_dependencies() {
    print_step "Installing dependencies with Conda"
    
    # Activate conda environment and install packages
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate $CONDA_ENV_NAME
    
    # Install from environment.yml
    conda env update -f environment.yml
    
    print_success "Dependencies installed"
}

create_setup_py() {
    print_step "Creating setup.py"
    
    cat > setup.py << 'EOF'
#!/usr/bin/env python3
"""
ARXML Viewer Pro - Setup Configuration
Professional AUTOSAR ARXML file viewer for automotive engineers
"""

from setuptools import setup, find_packages
import os

def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "ARXML Viewer Pro - Professional AUTOSAR ARXML file viewer"

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="arxml-viewer-pro",
    version="1.0.0",
    author="Jayadev Meka",
    author_email="jd@miraiflow.tech",
    description="Professional AUTOSAR ARXML file viewer for automotive engineers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jdai-explore/V13W",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "black>=23.7.0",
            "mypy>=1.5.1",
            "flake8>=6.0.0",
            "PyInstaller>=5.13.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "arxml-viewer=arxml_viewer.main:main",
        ],
        "gui_scripts": [
            "arxml-viewer-gui=arxml_viewer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "arxml_viewer": [
            "resources/icons/*.png",
            "resources/icons/*.svg", 
            "resources/themes/*.qss",
            "resources/sample_data/*.arxml",
        ],
    },
    zip_safe=False,
)
EOF

    print_success "setup.py created"
}

create_config_files() {
    print_step "Creating configuration files"
    
    # .gitignore
    cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Application specific
logs/
*.arxml
config/local_*.json

# Conda
.conda/
EOF

    # pytest.ini
    cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src/arxml_viewer
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gui: GUI tests requiring display
EOF

    # mypy.ini
    cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-PyQt6.*]
ignore_missing_imports = True

[mypy-lxml.*]
ignore_missing_imports = True

[mypy-pandas.*]
ignore_missing_imports = True
EOF

    print_success "Configuration files created"
}

create_package_files() {
    print_step "Creating Python package files"
    
    # Create all __init__.py files
    find src -type d -exec touch {}/__init__.py \;
    find tests -type d -exec touch {}/__init__.py \;
    
    # Create main package __init__.py
    cat > src/arxml_viewer/__init__.py << 'EOF'
"""
ARXML Viewer Pro - Professional AUTOSAR ARXML Viewer
Copyright (c) 2025 ARXML Viewer Pro Team
"""

__version__ = "1.0.0"
__author__ = "ARXML Viewer Pro Team"
__email__ = "support@arxmlviewer.com"
__description__ = "Professional AUTOSAR ARXML file viewer for automotive engineers"
EOF

    print_success "Package files created"
}

create_development_scripts() {
    print_step "Creating development scripts"
    
    mkdir -p scripts
    
    # Run script for conda
    cat > scripts/run.sh << EOF
#!/bin/bash
# Quick run script for Conda environment
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME
cd ..
python -m arxml_viewer.main "\$@"
EOF
    chmod +x scripts/run.sh
    
    # Test script for conda
    cat > scripts/test.sh << EOF
#!/bin/bash
# Quick test script for Conda environment
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME
cd ..
pytest "\$@"
EOF
    chmod +x scripts/test.sh
    
    # Format script for conda
    cat > scripts/format.sh << EOF
#!/bin/bash
# Code formatting script for Conda environment
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME
cd ..
echo "Running black..."
black src/ tests/
echo "Running isort..."
isort src/ tests/
echo "Code formatted!"
EOF
    chmod +x scripts/format.sh
    
    # Activate environment script
    cat > activate.sh << EOF
#!/bin/bash
# Activate the conda environment
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME
echo "Conda environment '$CONDA_ENV_NAME' activated!"
echo "You can now run:"
echo "  python -m arxml_viewer.main"
echo "  pytest"
echo "  black src/ tests/"
EOF
    chmod +x activate.sh
    
    print_success "Development scripts created"
}

create_vscode_config() {
    print_step "Creating VS Code configuration"
    
    mkdir -p .vscode
    
    # Get conda environment python path
    CONDA_BASE=$(conda info --base)
    PYTHON_PATH="$CONDA_BASE/envs/$CONDA_ENV_NAME/bin/python"
    
    # VS Code settings
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "$PYTHON_PATH",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/build": true,
        "**/dist": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF

    # Launch configuration
    cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ARXML Viewer Pro",
            "type": "python",
            "request": "launch",
            "module": "arxml_viewer.main",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "python": "$PYTHON_PATH",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/src"
            }
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "python": "$PYTHON_PATH"
        }
    ]
}
EOF

    print_success "VS Code configuration created"
}

create_readme() {
    print_step "Creating README.md"
    
    cat > README.md << EOF
# ARXML Viewer Pro

Professional AUTOSAR ARXML file viewer for automotive engineers, built with Python and PyQt6.

## 🚀 Quick Start (Conda Environment)

### Activate Environment
\`\`\`bash
# Activate the conda environment
./activate.sh

# Or manually:
conda activate $CONDA_ENV_NAME
\`\`\`

### Run Application
\`\`\`bash
python -m arxml_viewer.main
\`\`\`

### Development Commands
\`\`\`bash
# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
\`\`\`

### Using Scripts
\`\`\`bash
# Quick run
./scripts/run.sh

# Quick test
./scripts/test.sh

# Format code
./scripts/format.sh
\`\`\`

## 🛠️ Environment Info

- **Conda Environment**: $CONDA_ENV_NAME
- **Python Version**: 3.9
- **GUI Framework**: PyQt6
- **Key Dependencies**: lxml, pydantic, pandas, matplotlib

## 📁 Project Structure

\`\`\`
arxml_viewer_pro/
├── src/arxml_viewer/          # Main application package
├── tests/                     # Test suite
├── scripts/                   # Development scripts
├── environment.yml            # Conda environment
├── requirements.txt           # Pip requirements
└── activate.sh                # Environment activation
\`\`\`

---

**Built with ❤️ for the automotive software community**
EOF

    print_success "README.md created"
}

validate_setup() {
    print_step "Validating setup"
    
    # Activate environment
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate $CONDA_ENV_NAME
    
    # Check key packages
    python -c "import PyQt6; print('✅ PyQt6 OK')"
    python -c "import lxml; print('✅ lxml OK')"
    python -c "import pydantic; print('✅ pydantic OK')"
    python -c "import pandas; print('✅ pandas OK')"
    python -c "import pytest; print('✅ pytest OK')"
    
    print_success "All dependencies verified"
}

print_completion_info() {
    echo
    echo -e "${GREEN}🎉 Conda setup completed successfully!${NC}"
    echo -e "${CYAN}=================================================================${NC}"
    echo
    echo -e "${YELLOW}📂 Project Location:${NC} $(pwd)"
    echo -e "${YELLOW}🐍 Conda Environment:${NC} $CONDA_ENV_NAME"
    echo -e "${YELLOW}🖥️  IDE:${NC} VS Code configuration created"
    echo
    echo -e "${BLUE}🚀 Next Steps:${NC}"
    echo "1. Activate environment: ${CYAN}./activate.sh${NC}"
    echo "2. Open in VS Code: ${CYAN}code .${NC}"
    echo "3. Start Day 2 development: PyQt6 GUI Implementation"
    echo
    echo -e "${PURPLE}📋 Daily Commands:${NC}"
    echo "• Activate environment: ${CYAN}conda activate $CONDA_ENV_NAME${NC}"
    echo "• Run application: ${CYAN}python -m arxml_viewer.main${NC}"
    echo "• Run tests: ${CYAN}pytest${NC}"
    echo "• Format code: ${CYAN}./scripts/format.sh${NC}"
    echo "• Quick run: ${CYAN}./scripts/run.sh${NC}"
    echo
    echo -e "${CYAN}=================================================================${NC}"
    echo -e "${GREEN}Ready for ARXML Viewer Pro development! 🎨✨${NC}"
}

main() {
    print_header
    
    # Check system requirements
    check_conda
    
    # Setup project
    create_project_structure
    create_requirements_files
    create_conda_environment
    install_dependencies
    create_setup_py
    create_config_files
    create_package_files
    create_development_scripts
    create_vscode_config
    create_readme
    validate_setup
    
    # Show completion info
    print_completion_info
}

# Run main function
main