#!/usr/bin/env python3
"""
PyQt5 Graphics Scene Test - Test the updated graphics scene
Save as: test_pyqt5_graphics.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_pyqt5_graphics_scene():
    """Test PyQt5 graphics scene functionality"""
    
    print("🚀 Testing PyQt5 Graphics Scene...")
    print("=" * 50)
    
    try:
        # Test PyQt5 imports
        import sys
        print(f"Using Python: {sys.executable}")
        
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView
        from PyQt5.QtCore import Qt, PYQT_VERSION_STR
        from PyQt5.QtGui import QFont
        
        print(f"✅ PyQt5 {PYQT_VERSION_STR} imports successful")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("PyQt5 Graphics Test")
        
        # Test custom graphics scene import
        from arxml_viewer.gui.graphics.graphics_scene import ComponentDiagramScene, ComponentGraphicsItem
        print("✅ Graphics scene imports successful")
        
        # Test model imports
        from arxml_viewer.models.component import Component, ComponentType
        from arxml_viewer.models.port import Port, PortType
        from arxml_viewer.models.package import Package
        print("✅ Model imports successful")
        
        # Create test data
        print("📊 Creating test data...")
        
        # Create test components
        sensor_comp = Component(
            short_name="SensorComponent",
            component_type=ComponentType.APPLICATION,
            desc="Temperature sensor component for PyQt5 test"
        )
        
        # Add port to sensor
        sensor_port = Port(
            short_name="TempDataOut",
            port_type=PortType.PROVIDED,
            component_uuid=sensor_comp.uuid
        )
        sensor_comp.add_port(sensor_port)
        
        # Create controller
        controller_comp = Component(
            short_name="ControllerComponent",
            component_type=ComponentType.COMPOSITION,
            desc="Main controller for PyQt5 test"
        )
        
        # Add ports to controller
        controller_in = Port(
            short_name="SensorDataIn",
            port_type=PortType.REQUIRED,
            component_uuid=controller_comp.uuid
        )
        controller_out = Port(
            short_name="ControlOut",
            port_type=PortType.PROVIDED,
            component_uuid=controller_comp.uuid
        )
        controller_comp.add_port(controller_in)
        controller_comp.add_port(controller_out)
        
        # Create actuator
        actuator_comp = Component(
            short_name="ActuatorComponent",
            component_type=ComponentType.SERVICE,
            desc="Motor actuator for PyQt5 test"
        )
        
        actuator_port = Port(
            short_name="ControlIn",
            port_type=PortType.REQUIRED,
            component_uuid=actuator_comp.uuid
        )
        actuator_comp.add_port(actuator_port)
        
        # Create package
        test_package = Package(
            short_name="PyQt5TestPackage",
            full_path="/PyQt5/Test"
        )
        
        test_package.add_component(sensor_comp)
        test_package.add_component(controller_comp)
        test_package.add_component(actuator_comp)
        
        print(f"✅ Created test package with {len(test_package.components)} components")
        
        # Create graphics scene
        print("🎨 Creating graphics scene...")
        scene = ComponentDiagramScene()
        
        # Load test data into scene
        scene.load_packages([test_package])
        print("✅ Test data loaded into scene")
        
        # Create main window for testing
        main_window = QMainWindow()
        main_window.setWindowTitle("PyQt5 Graphics Scene Test - ARXML Viewer Pro")
        main_window.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add title
        from PyQt5.QtWidgets import QLabel
        title = QLabel("🎉 PyQt5 Graphics Scene Test")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E86C1; padding: 10px; font-weight: bold;")
        layout.addWidget(title)
        
        # Add graphics view
        graphics_view = QGraphicsView(scene)
        # Fix PyQt5 rendering hint access
        from PyQt5.QtGui import QPainter
        graphics_view.setRenderHint(QPainter.Antialiasing)
        graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        layout.addWidget(graphics_view)
        
        # Fit scene in view
        scene.fit_components_in_view()
        graphics_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        
        # Connect scene signals for testing
        def on_component_selected(component):
            if component:
                print(f"🔍 Component selected: {component.short_name}")
                main_window.statusBar().showMessage(f"Selected: {component.short_name}")
            else:
                print("🔍 Selection cleared")
                main_window.statusBar().showMessage("No selection")
        
        def on_component_double_clicked(component):
            print(f"🖱️  Component double-clicked: {component.short_name}")
            main_window.statusBar().showMessage(f"Double-clicked: {component.short_name}", 2000)
        
        scene.component_selected.connect(on_component_selected)
        scene.component_double_clicked.connect(on_component_double_clicked)
        
        # Show window
        main_window.show()
        main_window.raise_()
        
        print("✅ PyQt5 graphics window displayed")
        print("")
        print("🎉 PyQt5 Graphics Scene Test Ready!")
        print("=" * 50)
        print("You should see:")
        print("• Three colored component blocks")
        print("• Sensor (blue), Controller (purple), Actuator (orange)")
        print("• Small colored circles representing ports")
        print("• Dark background theme")
        print("• Interactive selection and tooltips")
        print("")
        print("💡 Try these interactions:")
        print("• Click components to select them")
        print("• Double-click components for actions")
        print("• Hover over components for tooltips")
        print("• Use mouse wheel to zoom")
        print("• Drag to pan the view")
        print("=" * 50)
        
        # Run the application
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PyQt5 is installed: pip install PyQt5")
        print("2. Check that all model files exist in src/arxml_viewer/models/")
        print("3. Verify graphics scene file exists: src/arxml_viewer/gui/graphics/graphics_scene.py")
        return 1
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def check_pyqt5_availability():
    """Check if PyQt5 is available and working"""
    print("🔍 Checking PyQt5 availability...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QT_VERSION_STR
        from PyQt5.QtGui import QFont
        
        print(f"✅ PyQt5 version: {QT_VERSION_STR}")
        return True
        
    except ImportError as e:
        print(f"❌ PyQt5 not available: {e}")
        print("\nTo install PyQt5:")
        print("pip install PyQt5")
        print("or")
        print("conda install pyqt=5")
        return False

def main():
    """Main test function"""
    print("🔍 PyQt5 Graphics Scene Test - ARXML Viewer Pro")
    print("=" * 60)
    
    # Check PyQt5 first
    if not check_pyqt5_availability():
        return 1
    
    # Run graphics test
    exit_code = test_pyqt5_graphics_scene()
    
    if exit_code == 0:
        print("\n🎉 PyQt5 Graphics Scene Test PASSED!")
        print("Your PyQt5 environment is ready for ARXML Viewer Pro development!")
    else:
        print("\n❌ PyQt5 Graphics Scene Test FAILED!")
        
    return exit_code

if __name__ == "__main__":
    sys.exit(main())