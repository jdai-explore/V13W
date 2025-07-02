#!/usr/bin/env python3
"""
PyQt5 Diagnostic Script - Quick check for PyQt5 setup and compatibility
Save as: diagnose_pyqt5.py
"""

import sys
from pathlib import Path

def check_pyqt5_basic():
    """Check basic PyQt5 functionality"""
    print("🔍 Checking PyQt5 Basic Functionality...")
    print("-" * 40)
    
    try:
        # Basic imports
        from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
        from PyQt5.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
        from PyQt5.QtGui import QFont, QPainter, QColor
        
        print(f"✅ PyQt5 version: {PYQT_VERSION_STR}")
        print(f"✅ Qt version: {QT_VERSION_STR}")
        print("✅ Basic imports working")
        
        # Test application creation
        app = QApplication(sys.argv)
        print("✅ QApplication creation working")
        
        # Test widget creation
        widget = QLabel("Test")
        print("✅ Widget creation working")
        
        # Test rendering hints
        painter_hints = [
            hasattr(QPainter, 'Antialiasing'),
            hasattr(QPainter, 'TextAntialiasing'),
            hasattr(QPainter, 'SmoothPixmapTransform')
        ]
        
        if all(painter_hints):
            print("✅ QPainter rendering hints available")
        else:
            print("⚠️  Some QPainter rendering hints missing")
        
        return True
        
    except Exception as e:
        print(f"❌ PyQt5 basic check failed: {e}")
        return False

def check_graphics_imports():
    """Check graphics-related imports"""
    print("\n🎨 Checking Graphics Imports...")
    print("-" * 40)
    
    try:
        from PyQt5.QtWidgets import (
            QGraphicsScene, QGraphicsView, QGraphicsItem,
            QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
        )
        from PyQt5.QtCore import pyqtSignal, QRectF, QPointF
        from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
        
        print("✅ QGraphicsScene imports working")
        print("✅ Graphics items imports working")
        print("✅ Core graphics imports working")
        print("✅ Graphics utilities imports working")
        
        # Test scene creation
        scene = QGraphicsScene()
        print("✅ QGraphicsScene creation working")
        
        # Test item creation
        rect_item = QGraphicsRectItem(0, 0, 100, 50)
        scene.addItem(rect_item)
        print("✅ Graphics item creation and scene addition working")
        
        return True
        
    except Exception as e:
        print(f"❌ Graphics imports check failed: {e}")
        return False

def check_project_imports():
    """Check project-specific imports"""
    print("\n📦 Checking Project Imports...")
    print("-" * 40)
    
    # Add src to path
    src_path = Path.cwd() / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    try:
        # Test model imports
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.port import Port, PortType
        from arxml_viewer.models.package import Package
        print("✅ ARXML Viewer models import working")
        
        # Test utils imports
        from arxml_viewer.utils.constants import AppConstants, UIConstants
        from arxml_viewer.utils.logger import get_logger
        print("✅ ARXML Viewer utilities import working")
        
        # Test graphics scene import
        from arxml_viewer.gui.graphics.graphics_scene import ComponentDiagramScene
        print("✅ Graphics scene import working")
        
        # Test scene creation with models
        scene = ComponentDiagramScene()
        print("✅ Custom graphics scene creation working")
        
        # Test component creation
        component = Component(
            short_name="TestComponent",
            component_type=ComponentType.APPLICATION
        )
        print("✅ Component model creation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Project imports check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_rendering_hints():
    """Check rendering hints compatibility"""
    print("\n🖼️  Checking Rendering Hints...")
    print("-" * 40)
    
    try:
        from PyQt5.QtWidgets import QGraphicsView, QApplication
        from PyQt5.QtGui import QPainter
        from PyQt5.QtCore import Qt
        
        # Create application if not exists
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Test graphics view creation
        view = QGraphicsView()
        
        # Test rendering hint setting (the key fix)
        view.setRenderHint(QPainter.Antialiasing)
        print("✅ QPainter.Antialiasing setting working")
        
        view.setRenderHint(QPainter.TextAntialiasing)
        print("✅ QPainter.TextAntialiasing setting working")
        
        view.setRenderHint(QPainter.SmoothPixmapTransform)
        print("✅ QPainter.SmoothPixmapTransform setting working")
        
        # Test drag mode setting
        view.setDragMode(QGraphicsView.RubberBandDrag)
        print("✅ QGraphicsView.RubberBandDrag setting working")
        
        return True
        
    except Exception as e:
        print(f"❌ Rendering hints check failed: {e}")
        return False

def check_signal_slots():
    """Check PyQt5 signal/slot mechanism"""
    print("\n📡 Checking Signals and Slots...")
    print("-" * 40)
    
    try:
        from PyQt5.QtCore import QObject, pyqtSignal
        
        class TestObject(QObject):
            test_signal = pyqtSignal(str)
            
            def __init__(self):
                super().__init__()
                self.received_message = None
                
            def slot_method(self, message):
                self.received_message = message
        
        # Test signal/slot connection
        obj = TestObject()
        obj.test_signal.connect(obj.slot_method)
        obj.test_signal.emit("test message")
        
        if obj.received_message == "test message":
            print("✅ Signal/slot mechanism working")
            return True
        else:
            print("❌ Signal/slot test failed")
            return False
            
    except Exception as e:
        print(f"❌ Signal/slot check failed: {e}")
        return False

def run_mini_gui_test():
    """Run a minimal GUI test"""
    print("\n🖥️  Running Mini GUI Test...")
    print("-" * 40)
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont
        
        # Create application
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # Create test window
        window = QMainWindow()
        window.setWindowTitle("PyQt5 Mini Test")
        window.setGeometry(200, 200, 300, 200)
        
        # Central widget
        central = QWidget()
        window.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Test label
        label = QLabel("✅ PyQt5 GUI Test Successful!")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setStyleSheet("color: green; padding: 20px;")
        layout.addWidget(label)
        
        # Status label
        status = QLabel("This window will close automatically in 3 seconds...")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(status)
        
        # Show window
        window.show()
        window.raise_()
        
        print("✅ Mini GUI window displayed")
        
        # Auto-close timer
        def close_window():
            window.close()
            print("✅ Mini GUI test completed successfully")
        
        timer = QTimer()
        timer.singleShot(3000, close_window)  # Close after 3 seconds
        
        # Process events briefly
        for _ in range(100):
            app.processEvents()
            
        return True
        
    except Exception as e:
        print(f"❌ Mini GUI test failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🔍 PyQt5 Diagnostic Tool - ARXML Viewer Pro")
    print("=" * 60)
    
    checks = [
        ("PyQt5 Basic Functionality", check_pyqt5_basic),
        ("Graphics System", check_graphics_imports),
        ("Project Components", check_project_imports),
        ("Rendering Hints", check_rendering_hints),
        ("Signals and Slots", check_signal_slots),
        ("Mini GUI Test", run_mini_gui_test)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            print(f"\n🧪 {check_name}")
            print("=" * 60)
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 EXCELLENT! PyQt5 environment is fully functional!")
        print("✅ Ready to run the graphics scene test")
        print("\nNext step: python test_pyqt5_graphics.py")
        
    elif passed >= total - 1:
        print("✅ GOOD! PyQt5 environment is mostly functional")
        print("⚠️  Minor issues detected, but should work for development")
        print("\nTry: python test_pyqt5_graphics.py")
        
    else:
        print("❌ ISSUES DETECTED! Please fix the failing checks")
        print("\nTroubleshooting steps:")
        print("1. Reinstall PyQt5: pip install --force-reinstall PyQt5")
        print("2. Check Python version: python --version")
        print("3. Check project structure: ls src/arxml_viewer/")
        
    return passed >= total - 1

if __name__ == "__main__":
    success = main()
    print(f"\nDiagnostic {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)