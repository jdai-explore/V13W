#!/bin/bash
# cleanup_pyqt.sh - Clean up PyQt conflicts and reinstall PyQt5

echo "🧹 PyQt Cleanup and Reinstallation Script"
echo "=========================================="
echo ""

# Function to check what's currently installed
check_current_installation() {
    echo "🔍 Checking current PyQt installations..."
    echo ""
    
    echo "📦 Checking pip packages:"
    pip list | grep -i pyqt || echo "No PyQt packages found in pip"
    echo ""
    
    echo "📦 Checking conda packages:"
    conda list | grep -i pyqt || echo "No PyQt packages found in conda"
    echo ""
}

# Function to remove all PyQt packages
remove_pyqt_packages() {
    echo "🗑️  Removing all PyQt packages..."
    echo ""
    
    # Remove PyQt6 packages
    echo "Removing PyQt6 packages..."
    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip 2>/dev/null || true
    conda remove -y pyqt6 qt6 2>/dev/null || true
    
    # Remove PyQt5 packages
    echo "Removing PyQt5 packages..."
    pip uninstall -y PyQt5 PyQt5-Qt5 PyQt5-sip 2>/dev/null || true
    conda remove -y pyqt qt 2>/dev/null || true
    
    # Remove any PySide packages that might conflict
    echo "Removing PySide packages..."
    pip uninstall -y PySide2 PySide6 2>/dev/null || true
    conda remove -y pyside2 pyside6 2>/dev/null || true
    
    echo "✅ Cleanup completed"
    echo ""
}

# Function to clean conda cache
clean_conda_cache() {
    echo "🧽 Cleaning conda cache..."
    conda clean --all -y
    echo "✅ Conda cache cleaned"
    echo ""
}

# Function to install PyQt5 cleanly
install_pyqt5_clean() {
    echo "📦 Installing PyQt5 cleanly..."
    echo ""
    
    # Method 1: Try conda-forge first (usually more stable on macOS)
    echo "Attempting conda-forge installation..."
    if conda install -c conda-forge pyqt=5.15.7 qt=5.15.2 -y; then
        echo "✅ PyQt5 installed via conda-forge"
        return 0
    else
        echo "⚠️  Conda installation failed, trying pip..."
    fi
    
    # Method 2: Fallback to pip
    echo "Attempting pip installation..."
    if pip install PyQt5==5.15.7; then
        echo "✅ PyQt5 installed via pip"
        return 0
    else
        echo "❌ Both conda and pip installation failed"
        return 1
    fi
}

# Function to test the installation
test_installation() {
    echo "🧪 Testing PyQt5 installation..."
    echo ""
    
    python3 -c "
import sys
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    print(f'✅ PyQt5 version: {PYQT_VERSION_STR}')
    print(f'✅ Qt version: {QT_VERSION_STR}')
    
    # Test basic functionality
    app = QApplication(sys.argv)
    print('✅ QApplication creation successful')
    
    # Test graphics imports
    from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
    from PyQt5.QtGui import QPainter
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)
    print('✅ Graphics components working')
    
    print('🎉 PyQt5 installation test PASSED!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Installation test passed"
        return 0
    else
        echo "❌ Installation test failed"
        return 1
    fi
}

# Function to set environment variables to avoid conflicts
set_environment() {
    echo "🔧 Setting environment variables..."
    
    # Prevent Qt plugin conflicts
    export QT_PLUGIN_PATH=""
    export QT_QPA_PLATFORM_PLUGIN_PATH=""
    
    # Force PyQt5
    export QT_API="pyqt5"
    
    echo "✅ Environment configured for PyQt5"
    echo ""
}

# Main execution
main() {
    echo "This script will:"
    echo "1. Remove all existing PyQt installations"
    echo "2. Clean conda cache"
    echo "3. Install PyQt5 cleanly"
    echo "4. Test the installation"
    echo ""
    
    read -p "Do you want to continue? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        exit 0
    fi
    
    echo ""
    echo "🚀 Starting cleanup and reinstallation..."
    echo ""
    
    # Step 1: Check current state
    check_current_installation
    
    # Step 2: Remove everything
    remove_pyqt_packages
    
    # Step 3: Clean cache
    clean_conda_cache
    
    # Step 4: Set environment
    set_environment
    
    # Step 5: Install PyQt5
    if install_pyqt5_clean; then
        echo ""
        echo "📋 Installation summary:"
        pip list | grep -i pyqt
        echo ""
        
        # Step 6: Test installation
        if test_installation; then
            echo ""
            echo "🎉 SUCCESS! PyQt5 is now cleanly installed and working!"
            echo ""
            echo "📋 Next steps:"
            echo "1. Run: python minimal_pyqt5_test.py"
            echo "2. Then: python test_pyqt5_graphics.py"
            echo "3. Start developing with PyQt5!"
            echo ""
            echo "💡 If you encounter issues, restart your terminal to clear environment variables."
        else
            echo ""
            echo "❌ Installation completed but tests failed"
            echo "Please check the error messages above"
        fi
    else
        echo ""
        echo "❌ Installation failed"
        echo "Please try manual installation:"
        echo "  conda install -c conda-forge pyqt=5.15.7"
        echo "  or"
        echo "  pip install PyQt5==5.15.7"
    fi
}

# Run main function
main "$@"