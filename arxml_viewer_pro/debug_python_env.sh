#!/bin/bash
# debug_python_env.sh - Debug Python environment issues

echo "🔍 Python Environment Debugger"
echo "=============================="

# Check which Python is being used
echo "📍 Python executable locations:"
echo "which python: $(which python)"
echo "which python3: $(which python3)"
echo "which pip: $(which pip)"
echo "which pip3: $(which pip3)"
echo ""

# Check Python versions
echo "🐍 Python versions:"
echo "python --version: $(python --version 2>&1)"
echo "python3 --version: $(python3 --version 2>&1)"
echo ""

# Check Python paths
echo "📂 Python paths:"
echo "python -c 'import sys; print(sys.executable)'"
python -c "import sys; print(sys.executable)"
echo "python3 -c 'import sys; print(sys.executable)'"
python3 -c "import sys; print(sys.executable)"
echo ""

# Check site-packages locations
echo "📦 Site-packages locations:"
echo "python site-packages:"
python -c "import site; print(site.getsitepackages())" 2>/dev/null || echo "Failed to get site-packages"
echo "python3 site-packages:"
python3 -c "import site; print(site.getsitepackages())" 2>/dev/null || echo "Failed to get site-packages"
echo ""

# Check conda environment
echo "🐍 Conda environment info:"
echo "CONDA_DEFAULT_ENV: ${CONDA_DEFAULT_ENV:-'Not set'}"
echo "CONDA_PREFIX: ${CONDA_PREFIX:-'Not set'}"
echo ""

# List PyQt packages in different locations
echo "🔍 Searching for PyQt5 installations:"

# Check with pip list
echo "pip list | grep -i pyqt:"
pip list | grep -i pyqt || echo "No PyQt packages found with pip"
echo ""

# Check with conda list
echo "conda list | grep -i pyqt:"
conda list | grep -i pyqt || echo "No PyQt packages found with conda"
echo ""

# Try to find PyQt5 in filesystem
echo "🔍 File system search for PyQt5:"
find /opt/anaconda3 -name "*PyQt5*" -type d 2>/dev/null | head -5 || echo "PyQt5 not found in /opt/anaconda3"
echo ""

# Test different Python commands
echo "🧪 Testing PyQt5 import with different Python commands:"

echo "Testing 'python':"
python -c "
try:
    import PyQt5
    from PyQt5.QtCore import PYQT_VERSION_STR
    print(f'  ✅ PyQt5 found: {PYQT_VERSION_STR}')
except ImportError as e:
    print(f'  ❌ PyQt5 not found: {e}')
"

echo "Testing 'python3':"
python3 -c "
try:
    import PyQt5
    from PyQt5.QtCore import PYQT_VERSION_STR
    print(f'  ✅ PyQt5 found: {PYQT_VERSION_STR}')
except ImportError as e:
    print(f'  ❌ PyQt5 not found: {e}')
"

# Check if we need to use a specific conda python
if [ -n "$CONDA_PREFIX" ]; then
    echo "Testing conda python directly:"
    $CONDA_PREFIX/bin/python -c "
try:
    import PyQt5
    from PyQt5.QtCore import PYQT_VERSION_STR
    print(f'  ✅ PyQt5 found: {PYQT_VERSION_STR}')
except ImportError as e:
    print(f'  ❌ PyQt5 not found: {e}')
" 2>/dev/null || echo "  ❌ Conda python not accessible"
fi

echo ""
echo "💡 Recommendations:"
echo "1. If PyQt5 is found with one Python but not another, use the working one"
echo "2. If not found anywhere, try: pip3 install PyQt5==5.15.7"
echo "3. Consider creating a fresh conda environment"