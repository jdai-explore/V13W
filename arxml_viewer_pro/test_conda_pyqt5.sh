#!/bin/bash
# test_conda_pyqt5.sh - Test PyQt5 with the correct conda Python

echo "🐍 Testing PyQt5 with Conda Python"
echo "=================================="

# Make sure we're using conda python
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Test PyQt5 installation
echo "🧪 Testing PyQt5 with conda Python..."
python -c "
import sys
print(f'Python executable: {sys.executable}')
print(f'Python version: {sys.version}')
print()

try:
    from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
    from PyQt5.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
    from PyQt5.QtGui import QPainter, QFont
    
    print(f'✅ PyQt5 version: {PYQT_VERSION_STR}')
    print(f'✅ Qt version: {QT_VERSION_STR}')
    print('✅ Basic imports successful')
    
    # Test application creation
    app = QApplication(sys.argv)
    print('✅ QApplication creation successful')
    
    # Test widget creation
    label = QLabel('Hello PyQt5!')
    label.setAlignment(Qt.AlignCenter)
    print('✅ Widget creation successful')
    
    # Test graphics components  
    from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
    from PyQt5.QtGui import QBrush, QColor
    
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)
    
    # Add a test item
    rect = QGraphicsRectItem(0, 0, 100, 50)
    rect.setBrush(QBrush(QColor(100, 150, 200)))
    scene.addItem(rect)
    
    print('✅ Graphics components working')
    print('✅ Scene and view creation successful')
    
    print()
    print('🎉 ALL TESTS PASSED!')
    print('PyQt5 is working correctly with conda Python!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! PyQt5 is working with conda Python!"
    echo ""
    echo "📋 Important: Always use 'python' (not 'python3') for this project"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Test minimal GUI: python minimal_pyqt5_test.py"
    echo "2. Test graphics scene: python test_pyqt5_graphics.py"
    echo "3. Run ARXML Viewer: python -m arxml_viewer.main"
    echo ""
    echo "💡 Remember: Use 'python' command, not 'python3'"
else
    echo ""
    echo "❌ Tests failed. Please check error messages above."
fi